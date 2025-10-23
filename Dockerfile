# Multi-stage build for Harness Pipeline Agent

# Stage 1: Extract MCP server from official Harness image
ARG MCP_SERVER_VERSION=latest
FROM harness/mcp-server:${MCP_SERVER_VERSION} AS mcp-server

# Stage 2: Build application image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy and make entrypoint script executable
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# Create directory for MCP server binaries
RUN mkdir -p /app/mcp_server

# Copy MCP server binary from the official Harness image
COPY --from=mcp-server /app/harness-mcp-server /app/mcp_server/harness-mcp

# Make MCP server executable
RUN chmod +x /app/mcp_server/harness-mcp && \
    echo "✅ MCP server copied from harness/mcp-server:${MCP_SERVER_VERSION:-latest}"

# Set default MCP server path
ENV MCP_SERVER_PATH=/app/mcp_server/harness-mcp

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set entrypoint to generate .env from environment variables
ENTRYPOINT ["/app/docker-entrypoint.sh"]

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
