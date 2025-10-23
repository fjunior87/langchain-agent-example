from dotenv import load_dotenv

# Load environment variables from .env file before anything else
# This ensures LangChain can detect LANGCHAIN_TRACING_V2 and related vars
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from agent import harness_agent
from models import (
    PipelineRequest,
    ConnectorRequest,
    GeneralRequest,
    AgentResponse,
    HealthResponse
)
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Harness Pipeline Agent API...")
    try:
        await harness_agent.initialize()
        logger.info("Agent initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Harness Pipeline Agent API...")
    try:
        await harness_agent.cleanup()
        logger.info("Agent cleanup completed")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="Harness Pipeline Agent API",
    description="AI Agent for generating Harness.io pipeline and connector YAML using LangChain and OpenAI",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint."""
    return {
        "message": "Harness Pipeline Agent API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    agent_initialized = harness_agent.agent_executor is not None
    mcp_connected = harness_agent.llm is not None

    return HealthResponse(
        status="healthy" if agent_initialized and mcp_connected else "degraded",
        agent_initialized=agent_initialized,
        mcp_connected=mcp_connected
    )


@app.post("/api/v1/generate/pipeline", response_model=AgentResponse, tags=["Pipeline"])
async def generate_pipeline(request: PipelineRequest):
    """
    Generate a Harness.io pipeline YAML based on the user request.

    Args:
        request: PipelineRequest containing the user's pipeline requirements

    Returns:
        AgentResponse with the generated pipeline YAML
    """
    try:
        logger.info(f"Generating pipeline for request: {request.request[:100]}...")
        result = await harness_agent.generate_pipeline(request.request)

        return AgentResponse(
            success=True,
            output=result["output"],
            intermediate_steps=result.get("intermediate_steps"),
            tool_calls=result.get("tool_calls"),
            error=None
        )
    except Exception as e:
        logger.error(f"Error generating pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/connector", response_model=AgentResponse, tags=["Connector"])
async def generate_connector(request: ConnectorRequest):
    """
    Generate a Harness.io connector YAML based on the user request.

    Args:
        request: ConnectorRequest containing the user's connector requirements

    Returns:
        AgentResponse with the generated connector YAML
    """
    try:
        logger.info(f"Generating connector for request: {request.request[:100]}...")
        result = await harness_agent.generate_connector(request.request)

        return AgentResponse(
            success=True,
            output=result["output"],
            intermediate_steps=result.get("intermediate_steps"),
            tool_calls=result.get("tool_calls"),
            error=None
        )
    except Exception as e:
        logger.error(f"Error generating connector: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query", response_model=AgentResponse, tags=["General"])
async def process_query(request: GeneralRequest):
    """
    Process a general query or request using the Harness agent.

    This endpoint can be used for:
    - Listing existing pipelines/connectors
    - Getting details about specific resources
    - Asking questions about Harness.io
    - Any other Harness-related queries

    Args:
        request: GeneralRequest containing the user's query

    Returns:
        AgentResponse with the agent's response
    """
    try:
        logger.info(f"Processing query: {request.request[:100]}...")
        result = await harness_agent.process_request(request.request)

        return AgentResponse(
            success=True,
            output=result["output"],
            intermediate_steps=result.get("intermediate_steps"),
            tool_calls=result.get("tool_calls"),
            error=None
        )
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/debug/tools", tags=["Debug"])
async def list_available_tools():
    """
    List all available tools from the MCP server.
    
    This endpoint helps debug which tools are available to the agent
    and can be used to understand what operations are possible.
    
    Returns:
        Dictionary with list of tools and their descriptions
    """
    try:
        if not harness_agent.tools:
            raise HTTPException(
                status_code=503, 
                detail="Agent not initialized. Tools not available yet."
            )
        
        tools_info = []
        for tool in harness_agent.tools:
            tools_info.append({
                "name": tool.name,
                "description": tool.description,
            })
        
        return {
            "tools": tools_info,
            "count": len(tools_info),
            "status": "available"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
