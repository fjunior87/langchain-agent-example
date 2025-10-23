# Multi-stage build for Harness Pipeline Agent
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

# Create directory for MCP server binaries
RUN mkdir -p /app/mcp_server

# Download and install Harness MCP server
# Note: Replace this URL with the actual Harness MCP server download URL
# This is a placeholder that should be updated based on the actual MCP server distribution
RUN if [ ! -f /app/mcp_server/harness-mcp ]; then \
    echo "Downloading Harness MCP server..."; \
    # Option 1: If MCP server is available via npm
    # npm install -g @harness-io/mcp-server && \
    # ln -s $(which harness-mcp) /app/mcp_server/harness-mcp || \
    # Option 2: If MCP server needs to be downloaded from a specific URL
    # curl -L -o /app/mcp_server/harness-mcp <HARNESS_MCP_URL> && \
    # chmod +x /app/mcp_server/harness-mcp || \
    # Option 3: If copying from build context
    echo "MCP server should be placed in mcp_server directory before build"; \
    fi

# Make MCP server executable (if it exists)
RUN if [ -f /app/mcp_server/harness-mcp ]; then \
    chmod +x /app/mcp_server/harness-mcp; \
    fi

# Set default MCP server path
ENV MCP_SERVER_PATH=/app/mcp_server/harness-mcp

# Expose the API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
