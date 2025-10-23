# Docker Deployment Guide

This guide explains how to build and run the Harness Pipeline Agent using Docker.

## Prerequisites

- Docker 20.10 or higher
- Docker Compose (optional, for easier deployment)
- Harness MCP server binary (see below for options)

## Bundling the Harness MCP Server

The Docker image bundles the Harness MCP server binary. You have several options:

### Option 1: Manual Copy (Recommended)

If you already have the Harness MCP server installed locally:

```bash
# Create the mcp_server directory
mkdir -p mcp_server

# Copy your MCP server binary
cp /path/to/your/harness-mcp mcp_server/harness-mcp

# Make it executable
chmod +x mcp_server/harness-mcp
```

### Option 2: Download from Harness

If the MCP server is available for download:

```bash
# Create the mcp_server directory
mkdir -p mcp_server

# Download the binary (replace URL with actual MCP server download link)
curl -L -o mcp_server/harness-mcp https://example.com/harness-mcp

# Make it executable
chmod +x mcp_server/harness-mcp
```

### Option 3: Install via npm (if available)

If the Harness MCP server is distributed via npm:

```bash
# The Dockerfile can be modified to install via npm
# Uncomment the npm install lines in the Dockerfile
```

## Building the Docker Image

### Method 1: Using the Build Script (Recommended)

```bash
# Make the script executable (if not already)
chmod +x build-docker.sh

# Build with default name (harness-pipeline-agent:latest)
./build-docker.sh

# Or specify custom image name and tag
./build-docker.sh my-harness-agent v1.0.0
```

### Method 2: Manual Docker Build

```bash
# Build the image
docker build -t harness-pipeline-agent:latest .

# Build with custom tag
docker build -t harness-pipeline-agent:v1.0.0 .
```

## Running the Container

### Method 1: Using Docker Compose (Recommended)

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down
```

### Method 2: Using Docker Run

```bash
# Run with environment file
docker run -d \
  --name harness-pipeline-agent \
  -p 8000:8000 \
  --env-file .env \
  harness-pipeline-agent:latest

# Run with explicit environment variables
docker run -d \
  --name harness-pipeline-agent \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e HARNESS_ACCOUNT_ID=your_account_id \
  -e HARNESS_API_KEY=your_api_key \
  -e HARNESS_API_URL=https://app.harness.io \
  harness-pipeline-agent:latest
```

## Viewing Logs

```bash
# Using Docker
docker logs -f harness-pipeline-agent

# Using Docker Compose
docker-compose logs -f
```

## Health Check

The container includes a health check that runs every 30 seconds:

```bash
# Check container health status
docker inspect --format='{{.State.Health.Status}}' harness-pipeline-agent

# Or with docker-compose
docker-compose ps
```

## Accessing the API

Once the container is running, access the API at:

- API endpoint: `http://localhost:8000`
- Interactive docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`

Test with curl:
```bash
curl http://localhost:8000/health
```

## Environment Variables

The following environment variables must be configured:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `HARNESS_ACCOUNT_ID` | Yes | Harness account identifier |
| `HARNESS_API_KEY` | Yes | Harness API key |
| `HARNESS_API_URL` | No | Harness API URL (default: https://app.harness.io) |
| `MCP_SERVER_PATH` | No | Path to MCP server (default: /app/mcp_server/harness-mcp) |
| `API_HOST` | No | API host (default: 0.0.0.0) |
| `API_PORT` | No | API port (default: 8000) |

## Volume Mounts

### Logs (Optional)

Mount a logs directory to persist logs:

```bash
docker run -d \
  --name harness-pipeline-agent \
  -p 8000:8000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  harness-pipeline-agent:latest
```

### Custom MCP Server (Alternative)

If you want to use a different MCP server binary without rebuilding:

```bash
docker run -d \
  --name harness-pipeline-agent \
  -p 8000:8000 \
  --env-file .env \
  -v /path/to/your/harness-mcp:/app/mcp_server/harness-mcp:ro \
  harness-pipeline-agent:latest
```

## Troubleshooting

### Container won't start

1. Check logs:
```bash
docker logs harness-pipeline-agent
```

2. Verify environment variables:
```bash
docker exec harness-pipeline-agent env | grep -E "OPENAI|HARNESS"
```

3. Check if MCP server is present:
```bash
docker exec harness-pipeline-agent ls -la /app/mcp_server/
```

### MCP server not found

If you get errors about the MCP server not being found:

1. Ensure the binary is in `mcp_server/harness-mcp` before building
2. Rebuild the image: `./build-docker.sh`
3. Or mount the binary at runtime (see Volume Mounts section)

### Connection refused

1. Verify the container is running:
```bash
docker ps | grep harness-pipeline-agent
```

2. Check port mapping:
```bash
docker port harness-pipeline-agent
```

3. Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' harness-pipeline-agent
```

### API Key errors

Verify your environment variables are set correctly:
```bash
docker exec harness-pipeline-agent env | grep OPENAI_API_KEY
```

## Updating the Application

```bash
# Pull latest code
git pull

# Rebuild the image
./build-docker.sh

# Restart with docker-compose
docker-compose down
docker-compose up -d

# Or with docker run
docker stop harness-pipeline-agent
docker rm harness-pipeline-agent
docker run -d --name harness-pipeline-agent -p 8000:8000 --env-file .env harness-pipeline-agent:latest
```

## Production Deployment

For production deployments, consider:

1. **Use specific image tags** instead of `latest`
2. **Set resource limits**:
```yaml
services:
  harness-agent:
    # ... other config
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

3. **Use secrets management** instead of environment files
4. **Enable HTTPS** with a reverse proxy (nginx, traefik)
5. **Set up monitoring** and log aggregation
6. **Configure restart policies**:
```yaml
restart: unless-stopped
```

## Security Considerations

- Never commit `.env` file with real credentials
- Use Docker secrets for sensitive data in production
- Run container as non-root user (can be added to Dockerfile)
- Regularly update base images for security patches
- Scan images for vulnerabilities: `docker scan harness-pipeline-agent`

## Multi-Architecture Builds

To build for multiple architectures (e.g., AMD64 and ARM64):

```bash
# Set up buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t harness-pipeline-agent:latest \
  --push \
  .
```

## Container Registry

Push to a container registry:

```bash
# Tag the image
docker tag harness-pipeline-agent:latest your-registry/harness-pipeline-agent:latest

# Login to registry
docker login your-registry

# Push the image
docker push your-registry/harness-pipeline-agent:latest
```

## Support

For issues with:
- Docker build: Check build logs and ensure MCP binary is present
- Container runtime: Check container logs with `docker logs`
- Application errors: See main README.md for application-specific troubleshooting
