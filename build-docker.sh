#!/bin/bash

# Docker Build Script for Harness Pipeline Agent
# Builds Docker image with automatic MCP server inclusion from official Harness image

set -e

echo "=========================================="
echo "Harness Pipeline Agent - Docker Build"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}ℹ️  This build uses multi-stage Docker build${NC}"
echo "   - MCP server is automatically pulled from harness/mcp-server image"
echo "   - No manual MCP server download required"
echo "   - .env file is generated at runtime from environment variables"
echo ""

# Build arguments
IMAGE_NAME=${1:-harness-pipeline-agent}
IMAGE_TAG=${2:-latest}
MCP_VERSION=${MCP_SERVER_VERSION:-latest}
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Build Configuration:"
echo "  Image Name: ${FULL_IMAGE_NAME}"
echo "  MCP Server Version: ${MCP_VERSION}"
echo ""

# Optional: Check if .env exists for docker-compose usage
if [ -f .env ]; then
    echo -e "${GREEN}✓ Found .env file (will be used by docker-compose)${NC}"
else
    echo -e "${YELLOW}ℹ️  No .env file found (not required for build)${NC}"
    echo "   You can create one for docker-compose or pass env vars at runtime"
fi

echo ""
echo "Building Docker image..."
echo ""

# Build the Docker image with MCP server version argument
docker build \
    --build-arg MCP_SERVER_VERSION="${MCP_VERSION}" \
    -t "${FULL_IMAGE_NAME}" \
    .

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=========================================="
    echo "Docker image built successfully!"
    echo "==========================================${NC}"
    echo ""
    echo "Image: ${FULL_IMAGE_NAME}"
    echo ""
    echo "To run the container, pass environment variables directly:"
    echo ""
    echo -e "${BLUE}Option 1: Using docker run with environment variables${NC}"
    echo "  docker run -d -p 8000:8000 \\"
    echo "    -e OPENAI_API_KEY=your_key \\"
    echo "    -e HARNESS_ACCOUNT_ID=your_account \\"
    echo "    -e HARNESS_API_KEY=your_key \\"
    echo "    -e HARNESS_DEFAULT_ORG_ID=your_org \\"
    echo "    -e HARNESS_DEFAULT_PROJECT_ID=your_project \\"
    echo "    ${FULL_IMAGE_NAME}"
    echo ""
    echo -e "${BLUE}Option 2: Using docker run with .env file${NC}"
    echo "  docker run -d -p 8000:8000 --env-file .env ${FULL_IMAGE_NAME}"
    echo ""
    echo -e "${BLUE}Option 3: Using docker-compose (recommended)${NC}"
    echo "  docker-compose up -d"
    echo ""
    echo "To view logs:"
    echo "  docker logs -f harness-pipeline-agent"
    echo ""
    echo -e "${YELLOW}Note:${NC} The container automatically generates .env from environment variables"
    echo ""
else
    echo -e "${RED}Docker build failed!${NC}"
    exit 1
fi
