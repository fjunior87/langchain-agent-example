#!/usr/bin/env python3
"""
Simple test script to verify MCP server connection.
This helps isolate MCP connection issues from the rest of the application.
"""

import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_mcp_connection():
    """Test MCP server connection independently."""
    logger.info("=" * 60)
    logger.info("Testing MCP Server Connection")
    logger.info("=" * 60)
    
    try:
        # Import after logging is configured
        from config import settings
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        # Check configuration
        logger.info(f"MCP Server Path: {settings.mcp_server_path}")
        logger.info(f"Harness Account ID: {settings.harness_account_id}")
        logger.info(f"Harness API URL: {settings.harness_api_url}")
        
        # Check if file exists
        mcp_path = Path(settings.mcp_server_path)
        if not mcp_path.exists():
            logger.error(f"❌ MCP server binary not found: {settings.mcp_server_path}")
            logger.error("Please ensure the Harness MCP server is installed at this path")
            return False
        
        logger.info(f"✓ MCP server binary exists")
        
        # Prepare environment
        mcp_env = {
            "HARNESS_ACCOUNT_ID": settings.harness_account_id,
            "HARNESS_API_KEY": settings.harness_api_key,
            "HARNESS_API_URL": settings.harness_api_url,
        }
        
        # The Harness MCP server requires the 'stdio' subcommand
        server_params = StdioServerParameters(
            command=settings.mcp_server_path,
            args=["stdio"],  # Add stdio subcommand
            env=mcp_env
        )
        
        logger.info("Attempting to connect to MCP server...")
        logger.info("(This may take a few seconds...)")
        
        # Try to connect with a timeout
        try:
            async with asyncio.timeout(30):  # 30 second timeout
                async with stdio_client(server_params) as (read_stream, write_stream):
                    logger.info("✓ Stdio connection established")
                    
                    async with ClientSession(read_stream, write_stream) as session:
                        logger.info("✓ Client session created")
                        
                        logger.info("Initializing session...")
                        await session.initialize()
                        logger.info("✓ Session initialized")
                        
                        logger.info("Listing available tools...")
                        response = await session.list_tools()
                        
                        logger.info(f"✓ Successfully connected to MCP server!")
                        logger.info(f"Available tools: {len(response.tools)}")
                        
                        for tool in response.tools:
                            logger.info(f"  - {tool.name}: {tool.description}")
                        
                        return True
                        
        except asyncio.TimeoutError:
            logger.error("❌ Connection timed out after 30 seconds")
            logger.error("The MCP server is not responding.")
            logger.error("Possible causes:")
            logger.error("  1. MCP server binary is not working correctly")
            logger.error("  2. Missing or incorrect Harness credentials")
            logger.error("  3. Network issues connecting to Harness.io")
            logger.error("  4. MCP server requires additional configuration")
            return False
            
    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e}")
        logger.error("Ensure the MCP server binary exists at the specified path")
        return False
        
    except ValueError as e:
        logger.error(f"❌ Configuration error: {e}")
        logger.error("Check your .env file and ensure all required variables are set")
        return False
        
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.exception("Full traceback:")
        return False


async def main():
    """Main function."""
    print("\n🔍 MCP Server Connection Test\n")
    
    success = await test_mcp_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✓ MCP server connection test PASSED")
        print("The MCP server is working correctly.")
        print("You can now start the main application.")
    else:
        print("❌ MCP server connection test FAILED")
        print("Please fix the issues above before starting the application.")
        print("\nFor more help, see TROUBLESHOOTING.md")
        sys.exit(1)
    print("=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)

