# Quick Start Guide

Get the Harness Pipeline Agent up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Docker and Docker Compose installed (recommended)
- [ ] OR Python 3.9+ installed (for local development)
- [ ] OpenAI API key
- [ ] Harness.io account with API access
- [ ] Harness MCP server binary

## Docker Deployment (Recommended)

### Step 1: Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

Required values in `.env`:
```env
OPENAI_API_KEY=sk-...
HARNESS_ACCOUNT_ID=your_account_id
HARNESS_API_KEY=your_api_key
HARNESS_API_URL=https://app.harness.io
HARNESS_DEFAULT_ORG_ID=default
HARNESS_DEFAULT_PROJECT_ID=default
```

### Step 2: Add MCP Server Binary

```bash
# Copy your Harness MCP server binary
cp /path/to/harness-mcp mcp_server/harness-mcp

# Make it executable
chmod +x mcp_server/harness-mcp
```

### Step 3: Build and Run

```bash
# Build the Docker image
./build-docker.sh

# Start the service
docker-compose up -d

# Check if it's running
curl http://localhost:8000/health
```

### Step 4: Test the API

```bash
# Generate a pipeline
curl -X POST "http://localhost:8000/api/v1/generate/pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a simple CI pipeline for a Python application"
  }'
```

### Step 5: Access Documentation

Open your browser to:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## Local Development

### Step 1: Setup Environment

```bash
# Use Makefile (recommended)
make install

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
```

### Step 2: Configure MCP Server Path

Edit `.env` and set the path to your local MCP server:
```env
MCP_SERVER_PATH=/path/to/your/harness-mcp
```

### Step 3: Run the Application

```bash
# Using Makefile
make run

# Or using the run script
./run.sh

# Or directly
python main.py
```

## Verify Installation

Run the test client:

```bash
# Make sure the API is running, then:
python test_client.py
```

You should see all tests pass!

## Common Commands

### Docker

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# View logs
docker-compose logs -f

# Restart
docker-compose restart
```

### Makefile

```bash
make help           # Show all commands
make install        # Install dependencies
make run            # Run locally
make docker-build   # Build Docker image
make docker-run     # Run with Docker
make docker-stop    # Stop Docker containers
make test           # Run test client
```

## Troubleshooting

### Issue: "MCP server not found"

**Solution**: Ensure the binary is in `mcp_server/harness-mcp` or set `MCP_SERVER_PATH` correctly in `.env`

### Issue: "Agent fails to initialize"

**Solution**: 
1. Check `.env` has all required variables
2. Verify OpenAI API key is valid
3. Check Harness API credentials

### Issue: "Connection refused"

**Solution**:
1. Ensure the service is running: `docker-compose ps` or check local process
2. Verify port 8000 is not in use: `lsof -i :8000`
3. Check firewall settings

### Issue: Docker build fails

**Solution**:
1. Ensure MCP binary exists: `ls -la mcp_server/harness-mcp`
2. Check Docker has enough resources
3. Review build logs for specific errors

## Next Steps

1. **Explore Examples**: Check `examples.md` for more request examples
2. **Read Documentation**: See `README.md` for comprehensive docs
3. **Docker Details**: See `DOCKER.md` for advanced Docker configurations
4. **Customize**: Modify the agent prompt in `agent.py` for your use case

## Getting Help

- Check the full documentation in `README.md`
- Review Docker-specific guides in `DOCKER.md`
- See example requests in `examples.md`
- Test the API using the interactive docs at `/docs`

## Success Criteria

You're all set if you can:
- ✓ Access http://localhost:8000/health and get a healthy status
- ✓ View the API documentation at http://localhost:8000/docs
- ✓ Successfully generate a pipeline using the test client
- ✓ See logs showing the agent processing requests

Happy building! 🚀
