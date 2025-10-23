# Fix Applied: MCP Server Hanging at Session Initialization

## Problem Identified

The application was hanging at:
```
INFO - Initializing session...
```

This meant the MCP server was starting but not responding to the initialization handshake.

## Root Cause

The Harness MCP server requires the `stdio` subcommand to be passed as an argument. Without it, the server starts but doesn't enter stdio mode, causing it to hang when the client tries to initialize the session.

## Solution Applied

### 1. Added `stdio` Subcommand

**File: `mcp_client.py`**

Changed from:
```python
server_params = StdioServerParameters(
    command=settings.mcp_server_path,
    args=[],  # Empty args - WRONG!
    env=mcp_env
)
```

To:
```python
server_params = StdioServerParameters(
    command=settings.mcp_server_path,
    args=["stdio"],  # Add stdio subcommand - CORRECT!
    env=mcp_env
)
```

### 2. Added Timeouts

Added timeouts to prevent indefinite hanging:

```python
# Initialize with 30-second timeout
await asyncio.wait_for(self.session.initialize(), timeout=30.0)

# List tools with 10-second timeout
response = await asyncio.wait_for(self.session.list_tools(), timeout=10.0)
```

Now if the MCP server doesn't respond within these timeouts, you'll get a clear error message instead of hanging forever.

### 3. Updated Test Script

**File: `test_mcp_connection.py`**

Applied the same fix to the test script so it can properly test the connection.

## How to Test

### Option 1: Quick Test with Test Script

```bash
cd /Users/franciscojunior/Workspace/personal/autogen_test/harness_agent
./venv/bin/python test_mcp_connection.py
```

This should now:
- ✓ Connect to MCP server
- ✓ Initialize session successfully
- ✓ List available tools
- ✓ Show success message

### Option 2: Start the Full Application

```bash
make run
```

You should now see:
```
INFO - Starting Harness Pipeline Agent API...
INFO - Initializing Harness Pipeline Agent...
INFO - Initializing OpenAI LLM...
INFO - OpenAI LLM initialized
INFO - Connecting to MCP server...
INFO - Starting MCP client connection...
INFO - MCP server path: ./mcp_server/harness-mcp
INFO - Creating stdio client...
INFO - Entering stdio context...
INFO - Creating client session...
INFO - Entering session context...
INFO - Initializing session...
INFO - Listing available tools...
INFO - Connected to MCP server. Available tools: [...]
INFO - Creating LangChain tools...
INFO - Created X LangChain tools
INFO - Creating agent executor...
INFO - Agent executor created successfully
INFO - Harness Pipeline Agent initialization complete
INFO - Agent initialized successfully
INFO - Application startup complete.
INFO - Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## What Changed

### Files Modified:
1. **`mcp_client.py`**
   - Added `"stdio"` to args
   - Added timeouts to prevent hanging
   - Better error messages

2. **`test_mcp_connection.py`**
   - Added `"stdio"` to args
   - Consistent with main client

### Why This Works

The Harness MCP server has multiple modes:
- `harness-mcp stdio` - Stdio mode for MCP protocol
- `harness-mcp http-server` - HTTP server mode
- Default (no args) - Does nothing, just exits or hangs

By adding the `stdio` subcommand, we tell the server to enter stdio mode and listen for MCP protocol messages, which is what the client expects.

## Verification

To verify the fix worked, check that:

1. ✓ Test script completes successfully
2. ✓ Application starts without hanging
3. ✓ You see "Connected to MCP server. Available tools: [...]" in logs
4. ✓ API is accessible at http://localhost:8000
5. ✓ API docs are accessible at http://localhost:8000/docs

## If It Still Hangs

If it still hangs even with the `stdio` subcommand:

1. **Check credentials**: Verify HARNESS_ACCOUNT_ID and HARNESS_API_KEY are correct
2. **Check network**: Ensure you can reach Harness.io API
3. **Check MCP server logs**: Add `--debug` flag to see what's happening:
   ```python
   args=["stdio", "--debug"]
   ```
4. **Test manually**:
   ```bash
   export HARNESS_ACCOUNT_ID=your_account_id
   export HARNESS_API_KEY=your_key
   export HARNESS_API_URL=https://app.harness.io
   ./mcp_server/harness-mcp stdio
   ```
   Then type some JSON-RPC message to see if it responds.

## Summary

**Problem**: MCP server hanging at session initialization
**Cause**: Missing `stdio` subcommand
**Fix**: Added `args=["stdio"]` to server parameters
**Result**: Server now properly enters stdio mode and responds to client

The application should now start successfully! 🎉

