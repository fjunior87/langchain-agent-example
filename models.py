from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PipelineRequest(BaseModel):
    """Request model for pipeline generation."""
    request: str = Field(..., description="User request describing the pipeline to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "request": "Create a CI pipeline for a Python application with build, test, and deploy stages"
            }
        }


class ConnectorRequest(BaseModel):
    """Request model for connector generation."""
    request: str = Field(..., description="User request describing the connector to generate")

    class Config:
        json_schema_extra = {
            "example": {
                "request": "Create a GitHub connector for my repository https://github.com/myorg/myrepo"
            }
        }


class GeneralRequest(BaseModel):
    """Request model for general agent queries."""
    request: str = Field(..., description="User request or question")

    class Config:
        json_schema_extra = {
            "example": {
                "request": "List all available pipelines in my Harness account"
            }
        }


class ToolCall(BaseModel):
    """Model for a single tool call in the agent execution."""
    step: int = Field(..., description="Step number in the execution")
    tool: str = Field(..., description="Name of the tool that was called")
    tool_input: Dict[str, Any] = Field(..., description="Input arguments passed to the tool")
    observation: str = Field(..., description="Result returned by the tool")
    log: Optional[str] = Field(default=None, description="Additional log information")


class AgentResponse(BaseModel):
    """Response model for agent operations."""
    success: bool = Field(..., description="Whether the request was successful")
    output: str = Field(..., description="The agent's response or generated YAML")
    intermediate_steps: Optional[List[Any]] = Field(
        default=None,
        description="Raw intermediate steps from agent (deprecated, use tool_calls instead)"
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Structured information about tools called during execution"
    )
    error: Optional[str] = Field(default=None, description="Error message if request failed")

    class Config:
        # Allow arbitrary types for intermediate_steps (to handle tuples from LangChain)
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "success": True,
                "output": "pipeline:\n  name: my-pipeline\n  stages:\n    - stage:\n        name: Build",
                "intermediate_steps": None,
                "tool_calls": [
                    {
                        "step": 1,
                        "tool": "list_pipelines",
                        "tool_input": {"org": "myorg"},
                        "observation": "Found 3 pipelines",
                        "log": None
                    }
                ],
                "error": None
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    agent_initialized: bool = Field(..., description="Whether the agent is initialized")
    mcp_connected: bool = Field(..., description="Whether MCP server is connected")
