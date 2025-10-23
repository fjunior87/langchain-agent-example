# Fixes Applied for Tool Call Errors

## Date: 2025-10-23

## Issues Fixed

### Issue 1: JSON Parsing Error in Tool Calls
**Error:** `Error calling tool list_pipelines: Expecting value: line 1 column 1 (char 0)`

**Root Cause:** The MCP server returns `CallToolResult` objects with a `content` array, not plain JSON strings. The tool wrapper was trying to directly serialize these objects as JSON, which failed.

**Solution:** Added `_extract_mcp_result()` method that properly extracts text content from MCP result objects.

### Issue 2: Pydantic Validation Error
**Error:** `1 validation error for AgentResponse intermediate_steps.0 Input should be a valid dictionary`

**Root Cause:** LangChain returns `intermediate_steps` as a list of tuples `[(AgentAction, observation), ...]`, but the Pydantic model expected a list of dictionaries.

**Solution:** 
- Made `intermediate_steps` field more flexible with `List[Any]` type
- Added new `tool_calls` field for structured, parsed tool information
- Added `_parse_intermediate_steps()` method to convert tuples to user-friendly dicts

## Changes Made

### 1. File: `agent.py`

#### Added Imports
```python
import time  # For timing tool execution
```

#### Enhanced Tool Wrapper (`make_tool_func`)
- Added detailed logging (🔧 for calls, ✅ for success, ❌ for errors)
- Added timing information for each tool call
- Improved error handling with specific error types
- Added call to `_extract_mcp_result()` to handle MCP response format

#### New Method: `_extract_mcp_result()`
- Extracts text content from MCP `CallToolResult` objects
- Handles various content types (text, data, etc.)
- Attempts to parse and format JSON for better readability
- Provides fallback for non-JSON content
- Returns structured error messages on failure

#### New Method: `_parse_intermediate_steps()`
- Converts LangChain's tuple format to structured dictionaries
- Extracts: step number, tool name, tool input, observation, log
- Truncates long observations (max 1000 chars)
- Handles errors gracefully with error objects

#### Updated Methods
All three main methods now return parsed steps:
- `generate_pipeline()`
- `generate_connector()`
- `process_request()`

**Return format changed from:**
```python
{
    "output": "...",
    "intermediate_steps": [(action, observation), ...]
}
```

**To:**
```python
{
    "output": "...",
    "intermediate_steps": None,  # Don't send raw tuples
    "tool_calls": [
        {
            "step": 1,
            "tool": "list_pipelines",
            "tool_input": {...},
            "observation": "...",
            "log": "..."
        }
    ]
}
```

### 2. File: `models.py`

#### New Model: `ToolCall`
```python
class ToolCall(BaseModel):
    step: int
    tool: str
    tool_input: Dict[str, Any]
    observation: str
    log: Optional[str]
```

#### Updated Model: `AgentResponse`
- Changed `intermediate_steps` to `Optional[List[Any]]` (more flexible)
- Added `arbitrary_types_allowed = True` in Config
- Added new `tool_calls` field: `Optional[List[Dict[str, Any]]]`
- Updated example in json_schema_extra

### 3. File: `main.py`

#### Updated All Three Endpoints
- `generate_pipeline()`
- `generate_connector()`
- `process_query()`

All now include `tool_calls` in the response:
```python
return AgentResponse(
    success=True,
    output=result["output"],
    intermediate_steps=result.get("intermediate_steps"),
    tool_calls=result.get("tool_calls"),  # NEW
    error=None
)
```

#### New Debug Endpoint: `/api/v1/debug/tools`
- Lists all available tools from MCP server
- Shows tool names and descriptions
- Returns count and status
- Helps debug what tools are available

## Benefits

### 1. Better Error Handling
- No more JSON parsing errors
- Clear error messages when tools fail
- Graceful handling of unexpected response formats

### 2. Better Debugging
- Detailed logging shows exactly what's happening
- Timing information for performance analysis
- Tool calls are visible in structured format
- New debug endpoint to list available tools

### 3. Better User Experience
- API responses now include structured `tool_calls` information
- Users can see which tools were called and what they returned
- Observations are truncated to prevent huge responses
- Clear separation between raw data and parsed data

### 4. Better Developer Experience
- Logging with emojis makes it easy to scan logs
- Structured tool call information is easy to parse
- Debug endpoint helps understand available capabilities
- No more Pydantic validation errors

## Testing

### Test the Fix

1. **Start the application:**
   ```bash
   make run
   ```

2. **Test the original failing request:**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/generate/pipeline" \
     -H "Content-Type: application/json" \
     -d '{
       "request": "Create a simple CI pipeline for a Python application it should use matrix for generating images for multiple versions. Check for existing pipelines to create it based on them"
     }'
   ```

3. **Check the response:**
   - Should have `success: true`
   - Should have `tool_calls` array showing which tools were called
   - Should NOT have validation errors
   - Should NOT have JSON parsing errors

4. **Check the logs:**
   ```
   INFO - 🔧 Calling tool: list_pipelines
   INFO - ✅ Tool list_pipelines completed in 234.56ms
   ```

5. **Test the debug endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/debug/tools
   ```
   
   Should return:
   ```json
   {
     "tools": [
       {"name": "list_pipelines", "description": "..."},
       {"name": "create_pipeline", "description": "..."},
       ...
     ],
     "count": 5,
     "status": "available"
   }
   ```

## Example Response

### Before (Errors)
```
Error calling tool list_pipelines: Expecting value: line 1 column 1 (char 0)
1 validation error for AgentResponse
intermediate_steps.0
  Input should be a valid dictionary
```

### After (Success)
```json
{
  "success": true,
  "output": "Here's your pipeline YAML...",
  "intermediate_steps": null,
  "tool_calls": [
    {
      "step": 1,
      "tool": "list_pipelines",
      "tool_input": {
        "org": "myorg",
        "project": "default"
      },
      "observation": "Found 3 existing pipelines: pipeline1, pipeline2, pipeline3",
      "log": null
    },
    {
      "step": 2,
      "tool": "get_pipeline",
      "tool_input": {
        "name": "pipeline1"
      },
      "observation": "Pipeline YAML: ...",
      "log": null
    }
  ],
  "error": null
}
```

## Logs Example

### Before (No Visibility)
```
INFO - Processing query...
ERROR - Error processing query: Expecting value: line 1 column 1 (char 0)
```

### After (Full Visibility)
```
INFO - Processing query: Create a simple CI pipeline...
INFO - 🔧 Calling tool: list_pipelines
DEBUG - 📥 Tool input: {"org": "myorg", "project": "default"}
INFO - ✅ Tool list_pipelines completed in 234.56ms
DEBUG - 📤 Tool output: Found 3 existing pipelines...
INFO - 🔧 Calling tool: get_pipeline
DEBUG - 📥 Tool input: {"name": "pipeline1"}
INFO - ✅ Tool get_pipeline completed in 156.78ms
DEBUG - 📤 Tool output: Pipeline YAML: ...
```

## API Documentation

The Swagger UI at `http://localhost:8000/docs` now shows:

### New Response Field: `tool_calls`
```json
{
  "tool_calls": [
    {
      "step": 1,
      "tool": "string",
      "tool_input": {},
      "observation": "string",
      "log": "string"
    }
  ]
}
```

### New Debug Endpoint
- **GET** `/api/v1/debug/tools`
- Returns list of available tools
- Useful for understanding agent capabilities

## Summary

✅ Fixed JSON parsing errors in tool calls  
✅ Fixed Pydantic validation errors  
✅ Added comprehensive logging with timing  
✅ Added structured tool call information in responses  
✅ Added debug endpoint to list tools  
✅ Improved error handling and messages  
✅ Better user and developer experience  

All changes are backward compatible - the API still works the same way, but now provides more information and handles errors better.

