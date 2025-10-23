import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import settings

logger = logging.getLogger(__name__)


class HarnessMCPClient:
    """Client for interacting with Harness.io MCP server."""

    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.tools: Dict[str, Any] = {}
        self._stdio_context = None
        self._session_context = None

    async def connect(self):
        """Connect to the Harness MCP server."""
        logger.info("Starting MCP client connection...")
        
        if not settings.mcp_server_path:
            raise ValueError("MCP_SERVER_PATH not configured")
        
        logger.info(f"MCP server path: {settings.mcp_server_path}")

        # Prepare environment variables for MCP server
        mcp_env = {
            "HARNESS_ACCOUNT_ID": settings.harness_account_id,
            "HARNESS_API_KEY": settings.harness_api_key,
            "HARNESS_API_URL": settings.harness_api_url,
            "HARNESS_DEFAULT_ORG_ID": settings.harness_default_org_id,
            "HARNESS_DEFAULT_PROJECT_ID": settings.harness_default_project_id,
        }
        logger.info(f"MCP environment: HARNESS_ACCOUNT_ID={settings.harness_account_id}, HARNESS_API_URL={settings.harness_api_url}")

        # The Harness MCP server requires the 'stdio' subcommand
        server_params = StdioServerParameters(
            command=settings.mcp_server_path,
            args=["stdio"],  # Add stdio subcommand
            env=mcp_env
        )

        logger.info("Creating stdio client...")
        # Initialize the stdio client connection using context manager properly
        self._stdio_context = stdio_client(server_params)
        
        logger.info("Entering stdio context...")
        stdio, write = await self._stdio_context.__aenter__()
        
        logger.info("Creating client session...")
        # Create and initialize session
        self.session = ClientSession(stdio, write)
        self._session_context = self.session
        
        logger.info("Entering session context...")
        await self._session_context.__aenter__()

        logger.info("Initializing session...")
        # Initialize the connection with timeout
        try:
            await asyncio.wait_for(self.session.initialize(), timeout=30.0)
        except asyncio.TimeoutError:
            logger.error("Session initialization timed out after 30 seconds")
            raise RuntimeError("MCP server session initialization timed out. The server may not be responding correctly.")

        logger.info("Listing available tools...")
        # List available tools
        try:
            response = await asyncio.wait_for(self.session.list_tools(), timeout=10.0)
            self.tools = {tool.name: tool for tool in response.tools}
        except asyncio.TimeoutError:
            logger.error("Listing tools timed out after 10 seconds")
            raise RuntimeError("MCP server list_tools timed out. The server may not be responding correctly.")
        
        logger.info(f"Connected to MCP server. Available tools: {list(self.tools.keys())}")

        return self

    async def disconnect(self):
        """Disconnect from the MCP server."""
        logger.info("Disconnecting from MCP server...")
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)
                self._session_context = None
                logger.info("Session closed")
        except Exception as e:
            logger.error(f"Error closing session: {e}")
        
        try:
            if self._stdio_context:
                await self._stdio_context.__aexit__(None, None, None)
                self._stdio_context = None
                logger.info("Stdio closed")
        except Exception as e:
            logger.error(f"Error closing stdio: {e}")
        
        self.session = None
        logger.info("MCP client disconnected")

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        if not self.session:
            raise RuntimeError("Not connected to MCP server")

        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}")

        result = await self.session.call_tool(tool_name, arguments)
        return result

    def get_available_tools(self) -> List[str]:
        """Get list of available tools."""
        return list(self.tools.keys())

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get schema for a specific tool."""
        tool = self.tools.get(tool_name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
        return None


# Global MCP client instance
mcp_client = HarnessMCPClient()
