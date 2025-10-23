# Troubleshooting Guide

## Application Hangs on Startup

If the application freezes during startup with the message "Starting Harness Pipeline Agent API..." and doesn't proceed, follow these debugging steps:

### Step 1: Check Configuration

Run the debug script to verify your configuration:

```bash
./venv/bin/python debug_config.py
```

This will check:
- ✓ .env file exists
- ✓ All required environment variables are set
- ✓ MCP server binary exists and is executable
- ✓ API configuration

### Step 2: Common Issues

#### Issue: .env file not found

**Solution:** Create a .env file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here

# Harness.io Configuration
HARNESS_ACCOUNT_ID=your_harness_account_id
HARNESS_API_KEY=your_harness_api_key
HARNESS_API_URL=https://app.harness.io
HARNESS_DEFAULT_ORG_ID=default
HARNESS_DEFAULT_PROJECT_ID=default

# MCP Server Configuration
MCP_SERVER_PATH=./mcp_server/harness-mcp

# API Server Configuration (Optional)
API_HOST=0.0.0.0
API_PORT=8000
```

#### Issue: MCP server binary not found

**Error:** `MCP_SERVER_PATH not configured` or file doesn't exist

**Solution:**
1. Download or build the Harness MCP server binary
2. Place it in `mcp_server/harness-mcp`
3. Make it executable: `chmod +x mcp_server/harness-mcp`
4. Update MCP_SERVER_PATH in .env to point to the binary

#### Issue: MCP server not executable

**Error:** Permission denied when trying to run MCP server

**Solution:**
```bash
chmod +x ./mcp_server/harness-mcp
```

#### Issue: MCP server hangs on connection

**Symptoms:** Application freezes after "Connecting to MCP server..."

**Possible causes:**
1. MCP server binary is not responding
2. MCP server requires environment variables that aren't set
3. Network/firewall issues preventing connection to Harness.io

**Solution:**
1. Test the MCP server manually:
   ```bash
   ./mcp_server/harness-mcp
   ```
   
2. Check if it requires additional environment variables:
   ```bash
   export HARNESS_ACCOUNT_ID=your_account_id
   export HARNESS_API_KEY=your_api_key
   export HARNESS_API_URL=https://app.harness.io
   ./mcp_server/harness-mcp
   ```

3. Check the MCP server documentation in `mcp_server/README.md`

### Step 3: Enable Detailed Logging

The application now has detailed logging. When you run it, you should see:

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
```

**If it hangs at a specific step**, that tells you where the problem is:

- **Hangs at "Entering stdio context"**: MCP server binary issue
- **Hangs at "Initializing session"**: MCP server not responding
- **Hangs at "Listing available tools"**: MCP server connection issue

### Step 4: Test MCP Server Independently

Create a simple test script to verify the MCP server works:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_mcp():
    server_params = StdioServerParameters(
        command="./mcp_server/harness-mcp",
        args=[],
        env={
            "HARNESS_ACCOUNT_ID": "your_account_id",
            "HARNESS_API_KEY": "your_api_key",
            "HARNESS_API_URL": "https://app.harness.io"
        }
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            print(f"Available tools: {[t.name for t in tools.tools]}")

asyncio.run(test_mcp())
```

Save this as `test_mcp.py` and run:
```bash
./venv/bin/python test_mcp.py
```

### Step 5: Alternative - Skip MCP Server for Testing

If you want to test the API without the MCP server temporarily, you can modify the code to skip MCP initialization. However, the agent won't have access to Harness tools.

### Step 6: Check System Resources

Ensure you have:
- Sufficient memory (at least 2GB free)
- Network connectivity
- No firewall blocking the MCP server

### Step 7: Get Help

If none of these steps work, gather the following information:

1. Output from `./venv/bin/python debug_config.py`
2. Last log message before hanging
3. Output from testing MCP server manually
4. Your operating system and Python version
5. Contents of `mcp_server/README.md` if available

## Other Common Issues

### Issue: Import Errors

**Error:** `ModuleNotFoundError: No module named 'X'`

**Solution:**
```bash
./venv/bin/pip install -r requirements.txt
```

### Issue: OpenAI API Errors

**Error:** `AuthenticationError` or `Invalid API key`

**Solution:**
1. Verify your OpenAI API key is correct
2. Check you have credits available in your OpenAI account
3. Ensure the key starts with `sk-`

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
export API_PORT=8001
```

## Quick Fixes Checklist

- [ ] .env file exists and is properly configured
- [ ] All required environment variables are set
- [ ] MCP server binary exists at specified path
- [ ] MCP server binary is executable (chmod +x)
- [ ] OpenAI API key is valid
- [ ] Harness.io credentials are correct
- [ ] Port 8000 is available
- [ ] Virtual environment is activated
- [ ] All dependencies are installed

## Getting More Help

For more information:
- Check the main README.md
- Review the examples in examples.md
- Check Harness.io MCP server documentation
- Review application logs with increased verbosity

