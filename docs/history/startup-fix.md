# Startup Issue Fix and Debugging Guide

## What Was Fixed

### 1. Async Context Manager Issue (Original Error)

**Problem:** The MCP client was improperly managing async context managers, causing `RuntimeError: Attempted to exit cancel scope in a different task`.

**Solution:** Modified `mcp_client.py` to properly store and manage context managers:
- Added `_stdio_context` and `_session_context` attributes
- Properly enter and exit context managers in the same task context
- Improved error handling in disconnect method

### 2. Added Comprehensive Logging

**Problem:** When the application hangs, it's hard to know where the issue is.

**Solution:** Added detailed logging throughout the initialization process:
- `mcp_client.py`: Logs each step of MCP connection
- `agent.py`: Logs agent initialization steps
- Shows exactly where the process hangs

### 3. Created Debug Tools

**New files:**
- `debug_config.py`: Configuration checker and MCP server tester
- `TROUBLESHOOTING.md`: Comprehensive troubleshooting guide
- `.env.example`: Example environment configuration (if not already present)

## Current Issue: Application Hangs on Startup

Your application is now hanging during startup. This is likely because:

1. **MCP server path is not configured** or incorrect
2. **MCP server binary doesn't exist** at the specified path
3. **MCP server is not responding** to connection attempts
4. **Missing environment variables** required by MCP server

## How to Debug

### Step 1: Run the Debug Script

```bash
cd /Users/franciscojunior/Workspace/personal/autogen_test/harness_agent
./venv/bin/python debug_config.py
```

This will:
- ✓ Check if .env file exists
- ✓ Verify all required environment variables
- ✓ Check if MCP server binary exists and is executable
- ✓ Optionally test the MCP server

### Step 2: Check Your .env File

Create or verify your `.env` file in the project root:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-actual-key-here

# Harness.io Configuration
HARNESS_ACCOUNT_ID=your_account_id
HARNESS_API_KEY=your_harness_api_key
HARNESS_API_URL=https://app.harness.io
HARNESS_DEFAULT_ORG_ID=default
HARNESS_DEFAULT_PROJECT_ID=default

# MCP Server Configuration
# This is the most critical setting - must point to actual binary
MCP_SERVER_PATH=./mcp_server/harness-mcp

# API Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Step 3: Verify MCP Server Binary

Check if the MCP server binary exists:

```bash
ls -la ./mcp_server/harness-mcp
```

If it doesn't exist:
1. Download or build the Harness MCP server
2. Place it in `mcp_server/harness-mcp`
3. Make it executable: `chmod +x mcp_server/harness-mcp`

### Step 4: Run with Detailed Logging

When you start the application now, you'll see detailed logs:

```bash
make run
```

Look for where it hangs:

```
INFO - Starting Harness Pipeline Agent API...
INFO - Initializing Harness Pipeline Agent...
INFO - Initializing OpenAI LLM...
INFO - OpenAI LLM initialized
INFO - Connecting to MCP server...
INFO - Starting MCP client connection...
INFO - MCP server path: ./mcp_server/harness-mcp
INFO - Creating stdio client...
INFO - Entering stdio context...        <-- If it hangs here, MCP server issue
INFO - Creating client session...
INFO - Entering session context...
INFO - Initializing session...          <-- If it hangs here, connection issue
INFO - Listing available tools...
INFO - Connected to MCP server. Available tools: [...]
```

## Common Solutions

### Solution 1: MCP Server Not Found

If you don't have the Harness MCP server:

```bash
# Check if it exists
ls -la mcp_server/

# If not, you need to obtain it from Harness.io
# Check mcp_server/README.md for instructions
```

### Solution 2: MCP Server Needs Environment Variables

The MCP server might need environment variables. Update `mcp_client.py` to pass them:

```python
server_params = StdioServerParameters(
    command=settings.mcp_server_path,
    args=[],
    env={
        "HARNESS_ACCOUNT_ID": settings.harness_account_id,
        "HARNESS_API_KEY": settings.harness_api_key,
        "HARNESS_API_URL": settings.harness_api_url,
    }
)
```

### Solution 3: Test MCP Server Manually

Test if the MCP server works independently:

```bash
# Set environment variables
export HARNESS_ACCOUNT_ID=your_account_id
export HARNESS_API_KEY=your_api_key
export HARNESS_API_URL=https://app.harness.io

# Try to run the MCP server
./mcp_server/harness-mcp

# It should start and wait for input (that's normal)
# Press Ctrl+C to exit
```

### Solution 4: Add Timeout to Connection

If the MCP server is slow to respond, add a timeout. Modify `agent.py`:

```python
async def initialize(self):
    """Initialize the agent with OpenAI and MCP tools."""
    logger.info("Initializing Harness Pipeline Agent...")
    
    # ... OpenAI initialization ...
    
    # Connect to MCP server with timeout
    logger.info("Connecting to MCP server...")
    try:
        await asyncio.wait_for(mcp_client.connect(), timeout=30.0)
        logger.info("MCP server connected")
    except asyncio.TimeoutError:
        logger.error("MCP server connection timed out after 30 seconds")
        raise RuntimeError("Failed to connect to MCP server: timeout")
```

## What to Check Next

1. **Run debug script**: `./venv/bin/python debug_config.py`
2. **Check logs**: Look for the last log message before hanging
3. **Verify MCP server**: Ensure it exists and is executable
4. **Test manually**: Try running the MCP server directly
5. **Check environment**: Ensure all variables are set correctly

## Quick Test Without MCP Server

If you want to test the API without MCP server (for debugging), you can temporarily modify `agent.py`:

```python
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

    # TEMPORARY: Skip MCP connection for testing
    logger.warning("Skipping MCP connection (debug mode)")
    self.tools = []  # Empty tools list
    
    # Create simple agent without MCP tools
    # ... rest of agent creation ...
```

This will let you verify the API works, but won't have Harness functionality.

## Next Steps

1. Run the debug script to identify the issue
2. Follow the appropriate solution based on the output
3. Check the TROUBLESHOOTING.md for more detailed help
4. If still stuck, provide the output from the debug script

## Files Modified

- `mcp_client.py`: Fixed async context managers, added logging
- `agent.py`: Added detailed logging
- `debug_config.py`: New debug utility (NEW)
- `TROUBLESHOOTING.md`: Comprehensive troubleshooting guide (NEW)
- `STARTUP_FIX.md`: This file (NEW)

## Summary

The original async error is fixed. The current hang is likely due to MCP server configuration. Run the debug script to identify the exact issue, then follow the appropriate solution above.

