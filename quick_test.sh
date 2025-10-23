#!/bin/bash
# Quick test script to verify the MCP connection fix

echo "=========================================="
echo "Quick MCP Connection Test"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with your credentials."
    exit 1
fi

if [ ! -f ./venv/bin/python ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: make install"
    exit 1
fi

echo "Testing MCP connection..."
echo ""

./venv/bin/python test_mcp_connection.py

exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "=========================================="
    echo "✓ Test PASSED! You can now run: make run"
    echo "=========================================="
else
    echo "=========================================="
    echo "❌ Test FAILED. Check the errors above."
    echo "See TROUBLESHOOTING.md for help."
    echo "=========================================="
fi

exit $exit_code

