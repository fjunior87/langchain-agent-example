# Harness Pipeline Agent

An AI-powered agent that generates Harness.io pipeline and connector YAML configurations using LangChain, OpenAI, and the Harness.io MCP server. The agent exposes its functionality through a REST API built with FastAPI.

## Features

- Generate Harness.io pipeline YAML from natural language descriptions
- Generate Harness.io connector YAML configurations
- Query existing pipelines and connectors
- Interact with Harness.io through MCP server integration
- RESTful API with interactive documentation
- Powered by OpenAI GPT-4 and LangChain

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│   FastAPI   │─────>│  LangChain   │─────>│  Harness MCP    │
│   REST API  │      │    Agent     │      │     Server      │
└─────────────┘      └──────────────┘      └─────────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  OpenAI      │
                     │  GPT-4       │
                     └──────────────┘
```

## Prerequisites

- Python 3.9 or higher
- OpenAI API key
- Harness.io account with API access
- Harness.io MCP server installed and configured

## Quick Start

### Docker (Recommended)

The easiest way to run the application is with Docker:

```bash
# 1. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 2. Place Harness MCP server binary
cp /path/to/harness-mcp mcp_server/harness-mcp

# 3. Build and run
./build-docker.sh
docker-compose up -d
```

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

## Installation (Local Development)

1. Clone or navigate to the project directory:
```bash
cd harness_agent
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
```

Edit `.env` with your credentials:
```env
OPENAI_API_KEY=your_openai_api_key_here
HARNESS_ACCOUNT_ID=your_harness_account_id
HARNESS_API_KEY=your_harness_api_key
HARNESS_API_URL=https://app.harness.io
HARNESS_DEFAULT_ORG_ID=default
HARNESS_DEFAULT_PROJECT_ID=default
MCP_SERVER_PATH=path_to_harness_mcp_server

# Optional: LangSmith Tracing
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=harness-agent
```

## Running the Application

### Option 1: Using the startup script (Unix/Mac)
```bash
./run.sh
```

### Option 2: Manual start
```bash
source venv/bin/activate
python main.py
```

### Option 3: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

## Documentation

### 📚 Complete Documentation

- **[Documentation Hub](docs/README.md)** - Complete documentation index
- **[Quick Start Guide](QUICK_START.md)** - Get started in 5 minutes

### 📖 User Guides

- **[Troubleshooting](docs/user-guide/troubleshooting.md)** - Common issues and solutions
- **[Examples](docs/user-guide/examples.md)** - Usage examples and patterns
- **[Docker Deployment](docs/user-guide/docker-deployment.md)** - Container deployment guide

### ✨ Features

- **[LangSmith Tracing](docs/features/langsmith-tracing.md)** - Observability and debugging

### 🔧 Development

- **[Debugging Guide](docs/development/debugging-guide.md)** - Debug and troubleshoot
- **[Change History](docs/history/README.md)** - Implementation notes and fixes

## API Documentation

Once the application is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### Health Check
```bash
GET /health
```

Returns the health status of the agent and MCP connection.

### Generate Pipeline
```bash
POST /api/v1/generate/pipeline
Content-Type: application/json

{
  "request": "Create a CI pipeline for a Python application with build, test, and deploy stages"
}
```

### Generate Connector
```bash
POST /api/v1/generate/connector
Content-Type: application/json

{
  "request": "Create a GitHub connector for my repository https://github.com/myorg/myrepo"
}
```

### General Query
```bash
POST /api/v1/query
Content-Type: application/json

{
  "request": "List all available pipelines in my Harness account"
}
```

## Usage Examples

### Example 1: Generate a CI/CD Pipeline
```bash
curl -X POST "http://localhost:8000/api/v1/generate/pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a CI/CD pipeline for a Node.js application with these stages: 1) Build and run tests, 2) Build Docker image, 3) Deploy to Kubernetes"
  }'
```

### Example 2: Generate a GitHub Connector
```bash
curl -X POST "http://localhost:8000/api/v1/generate/connector" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Create a GitHub connector named my-github with OAuth authentication"
  }'
```

### Example 3: Query Existing Resources
```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show me all pipelines in the production project"
  }'
```

## Project Structure

```
harness_agent/
├── main.py              # FastAPI application
├── agent.py             # LangChain agent implementation
├── mcp_client.py        # Harness MCP client
├── models.py            # Pydantic models for API
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── build-docker.sh      # Docker build script
├── .env.example         # Example environment variables
├── .dockerignore        # Docker build exclusions
├── .gitignore           # Git ignore rules
├── run.sh               # Local startup script
├── test_client.py       # API test client
├── mcp_server/          # Harness MCP server binary location
│   └── README.md        # MCP setup instructions
├── README.md            # This file
├── DOCKER.md            # Docker deployment guide
└── examples.md          # Usage examples
```

## How It Works

1. **User Request**: A user sends a request through the REST API
2. **LangChain Agent**: The request is processed by a LangChain agent powered by OpenAI GPT-4
3. **MCP Integration**: The agent uses tools from the Harness MCP server to interact with Harness.io
4. **YAML Generation**: The agent generates or retrieves the appropriate YAML configuration
5. **Response**: The YAML and any additional information is returned to the user

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests
```bash
pytest tests/
```

## Configuration Options

The following environment variables can be configured in `.env`:

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes | - |
| `HARNESS_ACCOUNT_ID` | Harness account identifier | Yes | - |
| `HARNESS_API_KEY` | Harness API key | Yes | - |
| `HARNESS_API_URL` | Harness API URL | No | https://app.harness.io |
| `HARNESS_DEFAULT_ORG_ID` | Default organization ID for pipelines | Yes | - |
| `HARNESS_DEFAULT_PROJECT_ID` | Default project ID for pipelines | Yes | - |
| `MCP_SERVER_PATH` | Path to Harness MCP server executable | Yes | - |
| `API_HOST` | API server host | No | 0.0.0.0 |
| `API_PORT` | API server port | No | 8000 |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | No | false |
| `LANGCHAIN_API_KEY` | LangSmith API key | No | - |
| `LANGCHAIN_PROJECT` | LangSmith project name | No | harness-agent |

## LangSmith Tracing (Optional)

LangSmith provides observability and debugging for your AI agent. When enabled, it automatically traces:
- All agent executions
- LLM calls and responses
- Tool calls and results
- Token usage and costs
- Execution timing

### Enabling LangSmith

1. Sign up at [smith.langchain.com](https://smith.langchain.com/)
2. Get your API key from Settings → API Keys
3. Add to your `.env` file:
   ```env
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_api_key
   LANGCHAIN_PROJECT=harness-agent
   ```
4. Restart the application

That's it! All traces will automatically appear in your LangSmith dashboard.

### What You'll See

- **Complete execution traces** with timing for each step
- **LLM prompts and responses** for debugging
- **Tool calls** showing which Harness tools were used
- **Token usage** for cost tracking
- **Error traces** for debugging failures

### Disabling Tracing

Set `LANGCHAIN_TRACING_V2=false` or remove the variable from `.env`.

## Troubleshooting

### Agent fails to initialize
- Verify all environment variables are set correctly
- Check that the Harness MCP server path is correct
- Ensure your OpenAI API key is valid

### MCP connection errors
- Verify the MCP server is accessible
- Check Harness API credentials
- Review MCP server logs

### Pipeline generation fails
- Ensure your request is clear and specific
- Check the agent logs for detailed error messages
- Verify Harness account permissions

## Security Considerations

- Never commit `.env` file to version control
- Rotate API keys regularly
- Use HTTPS in production
- Implement authentication/authorization for the API in production environments

## Contributing

Contributions are welcome! Please ensure your code follows the existing style and includes appropriate tests.

## License

MIT License - feel free to use this project as you see fit.

## Support

For issues related to:
- **Harness.io**: Visit [Harness Documentation](https://docs.harness.io)
- **OpenAI API**: Visit [OpenAI Documentation](https://platform.openai.com/docs)
- **LangChain**: Visit [LangChain Documentation](https://python.langchain.com)

## Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- Powered by [LangChain](https://www.langchain.com/)
- Uses [OpenAI GPT-4](https://openai.com/)
- Integrates with [Harness.io](https://harness.io/)
