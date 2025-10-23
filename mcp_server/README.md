# Harness MCP Server Binary

This directory should contain the Harness MCP server binary for Docker builds.

## Setup Instructions

### Option 1: Copy Existing Binary

If you have the Harness MCP server installed locally:

```bash
cp /path/to/your/harness-mcp ./harness-mcp
chmod +x ./harness-mcp
```

### Option 2: Download Binary

If the MCP server is available for download:

```bash
# Download from Harness (replace URL with actual download link)
curl -L -o harness-mcp https://example.com/harness-mcp
chmod +x harness-mcp
```

### Option 3: Install via Package Manager

If distributed via npm or other package managers:

```bash
# Example with npm (if available)
npm install -g @harness-io/mcp-server
cp $(which harness-mcp) ./harness-mcp
```

## Verification

After placing the binary, verify it works:

```bash
./harness-mcp --version
# or
./harness-mcp --help
```

## Docker Build

Once the binary is in place, you can build the Docker image:

```bash
cd ..
./build-docker.sh
```

## Important Notes

- The binary file is gitignored and won't be committed to version control
- Make sure the binary is executable: `chmod +x harness-mcp`
- The Docker build process will copy this binary into the container image
- For local development, set `MCP_SERVER_PATH` in your `.env` file to point to your local installation

## Required File

```
mcp_server/
└── harness-mcp    <- Place the Harness MCP server binary here
```
