#!/bin/bash
set -e

echo "🚀 Starting Harness Pipeline Agent..."
echo "📝 Generating .env file from environment variables..."

# Generate .env file from environment variables
cat > /app/.env << EOF
# OpenAI Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}

# Harness.io Configuration
HARNESS_ACCOUNT_ID=${HARNESS_ACCOUNT_ID}
HARNESS_API_KEY=${HARNESS_API_KEY}
HARNESS_API_URL=${HARNESS_API_URL:-https://app.harness.io}
HARNESS_DEFAULT_ORG_ID=${HARNESS_DEFAULT_ORG_ID:-default}
HARNESS_DEFAULT_PROJECT_ID=${HARNESS_DEFAULT_PROJECT_ID:-default}

# MCP Server Configuration
MCP_SERVER_PATH=${MCP_SERVER_PATH:-/app/mcp_server/harness-mcp}

# API Server Configuration
API_HOST=${API_HOST:-0.0.0.0}
API_PORT=${API_PORT:-8000}

# LangSmith Tracing (Optional)
LANGCHAIN_TRACING_V2=${LANGCHAIN_TRACING_V2:-false}
LANGCHAIN_API_KEY=${LANGCHAIN_API_KEY:-}
LANGCHAIN_PROJECT=${LANGCHAIN_PROJECT:-harness-agent}
EOF

echo "✅ .env file generated successfully"

# Validate required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ ERROR: OPENAI_API_KEY is required but not set"
    exit 1
fi

if [ -z "$HARNESS_ACCOUNT_ID" ]; then
    echo "❌ ERROR: HARNESS_ACCOUNT_ID is required but not set"
    exit 1
fi

if [ -z "$HARNESS_API_KEY" ]; then
    echo "❌ ERROR: HARNESS_API_KEY is required but not set"
    exit 1
fi

if [ -z "$HARNESS_DEFAULT_ORG_ID" ]; then
    echo "⚠️  WARNING: HARNESS_DEFAULT_ORG_ID not set, using 'default'"
fi

if [ -z "$HARNESS_DEFAULT_PROJECT_ID" ]; then
    echo "⚠️  WARNING: HARNESS_DEFAULT_PROJECT_ID not set, using 'default'"
fi

# Check if MCP server exists
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo "⚠️  WARNING: MCP server not found at $MCP_SERVER_PATH"
    echo "   The application may fail to start."
fi

echo "🔧 Configuration:"
echo "   API Host: $API_HOST"
echo "   API Port: $API_PORT"
echo "   MCP Server: $MCP_SERVER_PATH"
echo "   Harness URL: $HARNESS_API_URL"
echo "   Harness Org: ${HARNESS_DEFAULT_ORG_ID:-default}"
echo "   Harness Project: ${HARNESS_DEFAULT_PROJECT_ID:-default}"
echo "   LangSmith Tracing: ${LANGCHAIN_TRACING_V2:-false}"

echo ""
echo "🎯 Starting application..."
echo ""

# Execute the main command
exec "$@"

