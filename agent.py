from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain.schema import SystemMessage, HumanMessage
from mcp_client import mcp_client
from config import settings
import yaml
import json
import logging
import time
import os

logger = logging.getLogger(__name__)


class HarnessPipelineAgent:
    """LangChain agent for generating Harness.io pipeline and connector YAML."""

    def __init__(self):
        self.llm = None
        self.agent_executor = None
        self.tools = []

    async def initialize(self):
        """Initialize the agent with OpenAI and MCP tools."""
        logger.info("Initializing Harness Pipeline Agent...")
        
        # Initialize OpenAI LLM
        logger.info("Initializing OpenAI LLM...")
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        logger.info("OpenAI LLM initialized")

        # Connect to MCP server and get tools
        logger.info("Connecting to MCP server...")
        await mcp_client.connect()
        logger.info("MCP server connected")

        # Convert MCP tools to LangChain tools
        logger.info("Creating LangChain tools...")
        self.tools = await self._create_langchain_tools()
        logger.info(f"Created {len(self.tools)} LangChain tools")

        # Create the agent
        logger.info("Creating agent executor...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Harness.io pipeline and connector expert. Your role is to help users create
pipeline with Harness V0 format and connector YAML configurations for Harness.io based on their requirements.

You have access to Harness.io MCP server tools that can help you:
- Create pipelines with Harness V0 format
- Create connectors
- List existing pipelines and connectors
- Get pipeline/connector details
- Validate configurations

When a user asks you to generate a pipeline or connector:
1. Understand their requirements clearly
2. Use the appropriate MCP tools to interact with Harness.io
3. Generate or retrieve the YAML configuration in V0 format. Take the schema provided here: https://raw.githubusercontent.com/harness/harness-schema/refs/heads/main/v0/pipeline.json
4. Return the YAML in a clean, well-formatted manner

Basic pipeline structure:

pipeline:
    name: YAML Example ## A name for the pipeline.
    identifier: YAML_Example ## A unique Id for the pipeline.
    projectIdentifier: default ## Specify the project this pipeline belongs to.
    orgIdentifier: default ## Specify the organization this pipeline belongs to.
    description:
    stages: ## Contains the stage definitions.
        - stage:
            ...
        - stage:
            ...
    notificationRules:
    flowControl:
    properties:
    timeout:
    variables: ## Contains pipeline variables. Stage and step variables are defined within their own sections.
        -

Send as the response the YAML configuration only, no other text or explanation.
Provide only the YAML configuration, no other text or explanation."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True
        )
        
        logger.info("Agent executor created successfully")
        logger.info("Harness Pipeline Agent initialization complete")

        return self

    async def _create_langchain_tools(self) -> List[Tool]:
        """Convert MCP tools to LangChain tools."""
        langchain_tools = []

        for tool_name in mcp_client.get_available_tools():
            tool_schema = mcp_client.get_tool_schema(tool_name)

            if tool_schema:
                # Create a closure to capture tool_name
                def make_tool_func(name: str):
                    async def tool_func(arguments: str) -> str:
                        logger.info(f"🔧 Calling tool: {name}")
                        logger.debug(f"📥 Tool input: {str(arguments)[:200]}...")
                        
                        start_time = time.time()
                        try:
                            # Parse arguments if they're a string
                            if isinstance(arguments, str):
                                try:
                                    args = json.loads(arguments)
                                except json.JSONDecodeError as e:
                                    logger.warning(f"Failed to parse arguments as JSON: {e}. Using as plain string.")
                                    args = {"input": arguments}
                            else:
                                args = arguments

                            # Call MCP tool
                            result = await mcp_client.call_tool(name, args)
                            
                            # MCP returns a CallToolResult object with content array
                            # Extract text content from the result
                            result_text = self._extract_mcp_result(result)
                            
                            duration = (time.time() - start_time) * 1000
                            logger.info(f"✅ Tool {name} completed in {duration:.2f}ms")
                            logger.debug(f"📤 Tool output: {result_text[:200]}...")
                            
                            return result_text
                            
                        except json.JSONDecodeError as e:
                            duration = (time.time() - start_time) * 1000
                            error_msg = f"JSON parsing error in tool {name}: {str(e)}"
                            logger.error(f"❌ {error_msg} (after {duration:.2f}ms)")
                            return json.dumps({"error": error_msg, "tool": name, "status": "failed"})
                        except Exception as e:
                            duration = (time.time() - start_time) * 1000
                            error_msg = f"Error calling tool {name}: {str(e)}"
                            logger.error(f"❌ {error_msg} (after {duration:.2f}ms)", exc_info=True)
                            return json.dumps({"error": str(e), "tool": name, "status": "failed"})

                    return tool_func

                tool = Tool(
                    name=tool_name,
                    func=make_tool_func(tool_name),
                    description=tool_schema.get("description", f"Tool: {tool_name}"),
                    coroutine=make_tool_func(tool_name)
                )
                langchain_tools.append(tool)

        # Add custom YAML generation tool
        yaml_tool = Tool(
            name="generate_yaml",
            func=self._generate_yaml,
            description="Generate YAML from a dictionary or JSON object",
            coroutine=self._generate_yaml_async
        )
        langchain_tools.append(yaml_tool)

        return langchain_tools

    def _generate_yaml(self, data: str) -> str:
        """Synchronous YAML generation."""
        try:
            data_dict = json.loads(data) if isinstance(data, str) else data
            return yaml.dump(data_dict, default_flow_style=False, sort_keys=False)
        except Exception as e:
            return f"Error generating YAML: {str(e)}"

    async def _generate_yaml_async(self, data: str) -> str:
        """Asynchronous YAML generation."""
        return self._generate_yaml(data)

    def _extract_mcp_result(self, result: Any) -> str:
        """
        Extract text content from MCP CallToolResult object.
        
        MCP returns results in a specific format with a content array.
        Each content item can have text, image, or other data.
        """
        try:
            # Handle None result
            if result is None:
                return json.dumps({"status": "success", "data": None})
            
            # Check if result has content attribute (MCP CallToolResult)
            if hasattr(result, 'content') and result.content:
                content_parts = []
                for item in result.content:
                    if hasattr(item, 'text'):
                        content_parts.append(item.text)
                    elif hasattr(item, 'data'):
                        # Handle binary data or other content types
                        content_parts.append(str(item.data))
                    else:
                        # Fallback to string representation
                        content_parts.append(str(item))
                
                if content_parts:
                    combined = '\n'.join(content_parts)
                    # Try to parse as JSON for better formatting
                    try:
                        parsed = json.loads(combined)
                        return json.dumps(parsed, indent=2)
                    except json.JSONDecodeError:
                        # Return as-is if not JSON
                        return combined
                else:
                    return json.dumps({"status": "success", "message": "No content returned"})
            
            # If result is already a string
            if isinstance(result, str):
                return result
            
            # Try to serialize as JSON
            try:
                return json.dumps(result, indent=2)
            except (TypeError, ValueError):
                # If not JSON-serializable, convert to string
                return str(result)
                
        except Exception as e:
            logger.error(f"Error extracting MCP result: {e}", exc_info=True)
            return json.dumps({"error": f"Failed to extract result: {str(e)}"})

    def _parse_intermediate_steps(self, intermediate_steps: List[Any]) -> List[Dict[str, Any]]:
        """
        Convert LangChain intermediate_steps (list of tuples) to structured format.
        
        LangChain returns intermediate_steps as: [(AgentAction, observation), ...]
        We convert this to a more user-friendly format.
        """
        parsed = []
        
        for i, step in enumerate(intermediate_steps):
            try:
                if isinstance(step, tuple) and len(step) >= 2:
                    action, observation = step[0], step[1]
                    
                    # Extract action details
                    tool_name = getattr(action, 'tool', 'unknown')
                    tool_input = getattr(action, 'tool_input', {})
                    log = getattr(action, 'log', '') if hasattr(action, 'log') else ''
                    
                    # Truncate long observations
                    observation_str = str(observation)
                    if len(observation_str) > 1000:
                        observation_str = observation_str[:1000] + "... (truncated)"
                    
                    parsed.append({
                        "step": i + 1,
                        "tool": tool_name,
                        "tool_input": tool_input,
                        "observation": observation_str,
                        "log": log[:500] if log else None
                    })
                else:
                    # Handle unexpected format
                    parsed.append({
                        "step": i + 1,
                        "raw": str(step)[:500]
                    })
            except Exception as e:
                logger.error(f"Error parsing step {i}: {e}")
                parsed.append({
                    "step": i + 1,
                    "error": str(e)
                })
        
        return parsed

    async def generate_pipeline(self, user_request: str) -> Dict[str, Any]:
        """Generate a Harness pipeline based on user request."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        prompt = f"""Generate a Harness.io pipeline YAML based on the following request:

{user_request}

Please create the appropriate pipeline configuration and return it as YAML."""

        result = await self.agent_executor.ainvoke({"input": prompt})
        
        # Parse intermediate steps for better readability
        parsed_steps = self._parse_intermediate_steps(result.get("intermediate_steps", []))
        
        return {
            "output": result["output"],
            "intermediate_steps": None,  # Don't send raw tuples (causes Pydantic errors)
            "tool_calls": parsed_steps
        }

    async def generate_connector(self, user_request: str) -> Dict[str, Any]:
        """Generate a Harness connector based on user request."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        prompt = f"""Generate a Harness.io connector YAML based on the following request:

{user_request}

Please create the appropriate connector configuration and return it as YAML."""

        result = await self.agent_executor.ainvoke({"input": prompt})
        
        # Parse intermediate steps for better readability
        parsed_steps = self._parse_intermediate_steps(result.get("intermediate_steps", []))
        
        return {
            "output": result["output"],
            "intermediate_steps": None,  # Don't send raw tuples (causes Pydantic errors)
            "tool_calls": parsed_steps
        }

    async def process_request(self, user_request: str) -> Dict[str, Any]:
        """Process a general user request."""
        if not self.agent_executor:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        result = await self.agent_executor.ainvoke({"input": user_request})
        
        # Parse intermediate steps for better readability
        parsed_steps = self._parse_intermediate_steps(result.get("intermediate_steps", []))
        
        return {
            "output": result["output"],
            "intermediate_steps": None,  # Don't send raw tuples (causes Pydantic errors)
            "tool_calls": parsed_steps
        }

    async def cleanup(self):
        """Cleanup resources."""
        await mcp_client.disconnect()


# Global agent instance
harness_agent = HarnessPipelineAgent()
