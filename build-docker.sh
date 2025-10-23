#!/bin/bash

# Docker Build Script for Harness Pipeline Agent
# This script helps build the Docker image with the Harness MCP server bundled

set -e

echo "=========================================="
echo "Harness Pipeline Agent - Docker Build"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure your settings."
    exit 1
fi

# Create mcp_server directory if it doesn't exist
mkdir -p mcp_server

# Check if MCP server binary exists
if [ ! -f mcp_server/harness-mcp ]; then
    echo -e "${YELLOW}Warning: Harness MCP server binary not found in mcp_server/harness-mcp${NC}"
    echo ""
    echo "Please do ONE of the following:"
    echo "1. Download the Harness MCP server binary and place it in mcp_server/harness-mcp"
    echo "2. If using npm package, the Dockerfile will handle installation"
    echo "3. Copy the binary from your local installation:"
    echo "   cp /path/to/harness-mcp mcp_server/harness-mcp"
    echo ""
    read -p "Do you want to continue building anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Found MCP server binary${NC}"
    chmod +x mcp_server/harness-mcp
fi

# Build arguments
IMAGE_NAME=${1:-harness-pipeline-agent}
IMAGE_TAG=${2:-latest}
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "Building Docker image: ${FULL_IMAGE_NAME}"
echo ""

# Build the Docker image
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "Docker image built successfully!"
    echo "==========================================${NC}"
    echo ""
    echo "Image: ${FULL_IMAGE_NAME}"
    echo ""
    echo "To run the container:"
    echo "  docker run -p 8000:8000 --env-file .env ${FULL_IMAGE_NAME}"
    echo ""
    echo "Or use docker-compose:"
    echo "  docker-compose up -d"
    echo ""
    echo "To view logs:"
    echo "  docker logs -f harness-pipeline-agent"
    echo ""
else
    echo -e "${RED}Docker build failed!${NC}"
    exit 1
fi
