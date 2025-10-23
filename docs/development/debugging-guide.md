# Quick Debug Steps for Startup Issues

## Your Application is Hanging? Follow These Steps:

### Step 1: Check Configuration (30 seconds)

```bash
cd /Users/franciscojunior/Workspace/personal/autogen_test/harness_agent
./venv/bin/python debug_config.py
```

This will tell you if:
- ✓ .env file exists
- ✓ All required variables are set
- ✓ MCP server binary exists and is executable

### Step 2: Test MCP Connection (1 minute)

```bash
./venv/bin/python test_mcp_connection.py
```

This will:
- Connect to the MCP server independently
- Show exactly where the connection fails
- List available tools if successful

### Step 3: Based on Results

#### If Step 1 Fails (Configuration Issues)

**Missing .env file:**
```bash
# Create .env file with these variables:
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
HARNESS_ACCOUNT_ID=your_account_id
HARNESS_API_KEY=your_harness_key
HARNESS_API_URL=https://app.harness.io
HARNESS_DEFAULT_ORG_ID=default
HARNESS_DEFAULT_PROJECT_ID=default
MCP_SERVER_PATH=./mcp_server/harness-mcp
API_HOST=0.0.0.0
API_PORT=8000
EOF
```

**MCP server binary missing:**
```bash
# Check if it exists
ls -la mcp_server/harness-mcp

# If not, you need to obtain it from Harness.io
# Place it in mcp_server/ directory
# Make it executable:
chmod +x mcp_server/harness-mcp
```

#### If Step 2 Fails (MCP Connection Issues)

**Timeout or no response:**
- Check if MCP server binary is correct version
- Verify Harness credentials are valid
- Try running MCP server manually:
  ```bash
  export HARNESS_ACCOUNT_ID=your_account_id
  export HARNESS_API_KEY=your_key
  export HARNESS_API_URL=https://app.harness.io
  ./mcp_server/harness-mcp
  ```

**Connection refused:**
- Check network connectivity
- Verify firewall settings
- Ensure Harness.io is accessible

#### If Both Pass (Application Still Hangs)

Check the application logs carefully:
```bash
make run
```

Look for the last message before hanging. The new detailed logging will show:
- "Initializing OpenAI LLM..." 
- "Connecting to MCP server..."
- "Creating stdio client..."
- "Entering stdio context..." ← Often hangs here
- "Initializing session..."
- "Listing available tools..."

### Step 4: Common Quick Fixes

**Fix 1: Make MCP server executable**
```bash
chmod +x ./mcp_server/harness-mcp
```

**Fix 2: Verify environment variables**
```bash
# Check if .env is being loaded
./venv/bin/python -c "from config import settings; print(f'MCP Path: {settings.mcp_server_path}')"
```

**Fix 3: Test MCP server manually**
```bash
./mcp_server/harness-mcp --help
# or just
./mcp_server/harness-mcp
# (Press Ctrl+C to exit if it waits for input)
```

**Fix 4: Check Python version**
```bash
./venv/bin/python --version
# Should be Python 3.9 or higher
```

### Step 5: Still Stuck?

Run all diagnostics and save output:
```bash
# Save diagnostic output
./venv/bin/python debug_config.py > debug_output.txt 2>&1
./venv/bin/python test_mcp_connection.py >> debug_output.txt 2>&1

# View the output
cat debug_output.txt
```

Then check:
1. `TROUBLESHOOTING.md` for detailed solutions
2. `STARTUP_FIX.md` for technical details
3. `mcp_server/README.md` for MCP server specific info

## Most Common Issues (90% of cases)

1. **MCP_SERVER_PATH not set or incorrect** (40%)
   - Solution: Set correct path in .env

2. **MCP server binary doesn't exist** (30%)
   - Solution: Download/build and place in mcp_server/

3. **MCP server not executable** (10%)
   - Solution: `chmod +x mcp_server/harness-mcp`

4. **Missing Harness credentials** (10%)
   - Solution: Set HARNESS_ACCOUNT_ID, HARNESS_API_KEY, HARNESS_DEFAULT_ORG_ID, and HARNESS_DEFAULT_PROJECT_ID in .env

## Quick Test Without MCP (For Testing API Only)

If you want to test the FastAPI part without MCP:

1. Comment out MCP connection in `agent.py` line 39:
   ```python
   # await mcp_client.connect()  # Temporarily disabled
   ```

2. Set empty tools list:
   ```python
   self.tools = []  # No MCP tools
   ```

3. Start the API:
   ```bash
   make run
   ```

The API will start but won't have Harness functionality.

## Summary

1. Run `debug_config.py` - checks configuration
2. Run `test_mcp_connection.py` - tests MCP connection
3. Fix issues based on output
4. Start application with `make run`
5. Check logs for detailed progress

Most issues are configuration-related and can be fixed in under 5 minutes!

