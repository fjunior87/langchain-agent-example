#!/bin/bash
# Test script to verify the fixes for tool call errors

echo "=========================================="
echo "Testing Tool Call Fixes"
echo "=========================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Please start the server with: make run"
    exit 1
fi

echo "✓ Server is running"
echo ""

# Test 1: Check debug endpoint
echo "Test 1: Checking available tools..."
echo "GET /api/v1/debug/tools"
echo ""

tools_response=$(curl -s http://localhost:8000/api/v1/debug/tools)
tool_count=$(echo "$tools_response" | grep -o '"count":[0-9]*' | grep -o '[0-9]*')

if [ -n "$tool_count" ] && [ "$tool_count" -gt 0 ]; then
    echo "✅ Found $tool_count tools available"
    echo "$tools_response" | python3 -m json.tool 2>/dev/null || echo "$tools_response"
else
    echo "❌ No tools found or error occurred"
    echo "$tools_response"
fi

echo ""
echo "=========================================="
echo ""

# Test 2: Test the original failing request
echo "Test 2: Testing pipeline generation (original failing request)..."
echo "POST /api/v1/generate/pipeline"
echo ""

request_payload='{
  "request": "Create a simple CI pipeline for a Python application it should use matrix for generating images for multiple versions. Check for existing pipelines to create it based on them"
}'

echo "Request:"
echo "$request_payload" | python3 -m json.tool 2>/dev/null || echo "$request_payload"
echo ""
echo "Sending request... (this may take 10-30 seconds)"
echo ""

response=$(curl -s -X POST "http://localhost:8000/api/v1/generate/pipeline" \
  -H "Content-Type: application/json" \
  -d "$request_payload")

# Check if response contains success
if echo "$response" | grep -q '"success":true' || echo "$response" | grep -q '"success": true'; then
    echo "✅ Request succeeded!"
    echo ""
    
    # Check if tool_calls are present
    if echo "$response" | grep -q '"tool_calls"'; then
        echo "✅ Response includes tool_calls information"
        
        # Extract and display tool calls
        echo ""
        echo "Tool Calls:"
        echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    if 'tool_calls' in data and data['tool_calls']:
        for call in data['tool_calls']:
            print(f\"  Step {call.get('step', '?')}: {call.get('tool', 'unknown')} - {call.get('observation', '')[:80]}...\")
    else:
        print('  No tool calls in response')
except:
    print('  Could not parse tool calls')
" 2>/dev/null || echo "  (Could not parse tool calls)"
    else
        echo "⚠️  Response does not include tool_calls (this is OK if no tools were needed)"
    fi
    
    echo ""
    echo "Full Response (truncated):"
    echo "$response" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    # Truncate output for display
    if 'output' in data and len(data['output']) > 200:
        data['output'] = data['output'][:200] + '... (truncated)'
    if 'tool_calls' in data and data['tool_calls']:
        for call in data['tool_calls']:
            if 'observation' in call and len(call['observation']) > 100:
                call['observation'] = call['observation'][:100] + '... (truncated)'
    print(json.dumps(data, indent=2))
except:
    print(sys.stdin.read()[:500])
" 2>/dev/null || echo "$response" | head -c 500
    
else
    echo "❌ Request failed or returned unexpected response"
    echo ""
    echo "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
fi

echo ""
echo "=========================================="
echo ""

# Test 3: Simple query test
echo "Test 3: Testing simple query..."
echo "POST /api/v1/query"
echo ""

simple_request='{"request": "What tools are available?"}'

response=$(curl -s -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d "$simple_request")

if echo "$response" | grep -q '"success":true' || echo "$response" | grep -q '"success": true'; then
    echo "✅ Simple query succeeded"
else
    echo "❌ Simple query failed"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
fi

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
echo "All tests completed. Check the results above."
echo ""
echo "Expected results:"
echo "  ✅ Tools endpoint should list available tools"
echo "  ✅ Pipeline generation should succeed without JSON errors"
echo "  ✅ Response should include tool_calls array"
echo "  ✅ No Pydantic validation errors"
echo ""
echo "If all tests passed, the fixes are working correctly!"
echo ""

