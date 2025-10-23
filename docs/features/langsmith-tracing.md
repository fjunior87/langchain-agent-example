# LangSmith Integration Guide

## Overview

LangSmith is now integrated into the Harness Pipeline Agent, providing comprehensive observability and debugging capabilities for your AI agent. The integration is **completely optional** and requires **zero code changes** - just configuration.

## What is LangSmith?

LangSmith is LangChain's observability platform that provides:
- 🔍 **Tracing** - See every step of agent execution
- 📊 **Monitoring** - Track performance and costs
- 🐛 **Debugging** - Identify and fix issues quickly
- 📈 **Analytics** - Understand usage patterns
- 💰 **Cost Tracking** - Monitor token usage and expenses

## Quick Setup (5 Minutes)

### Step 1: Get LangSmith API Key

1. Go to [smith.langchain.com](https://smith.langchain.com/)
2. Sign up or log in (free tier available)
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the API key

### Step 2: Update Configuration

Add these three lines to your `.env` file:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_api_key_here
LANGCHAIN_PROJECT=harness-agent
```

### Step 3: Restart Application

```bash
# Stop the application (Ctrl+C if running)

# Restart
make run
```

### Step 4: Test It

Make a request to your API:

```bash
curl -X POST "http://localhost:8000/api/v1/generate/pipeline" \
  -H "Content-Type: application/json" \
  -d '{"request": "Create a simple CI pipeline"}'
```

Then check your LangSmith dashboard - you should see the trace!

## What Gets Traced

### Automatic Tracing Includes:

#### 1. Agent Execution
- Complete execution flow
- Decision-making process
- Tool selection logic
- Final response generation

#### 2. LLM Calls
- **Prompts** - Exact prompts sent to OpenAI
- **Responses** - Complete LLM responses
- **Model** - Which model was used (gpt-4)
- **Temperature** - Model parameters
- **Tokens** - Input/output token counts
- **Cost** - Estimated cost per call

#### 3. Tool Calls
- **Tool Name** - Which Harness tool was called
- **Arguments** - Input parameters
- **Results** - Tool output
- **Duration** - How long the tool took
- **Success/Failure** - Status of the call

#### 4. Metadata
- Request timestamp
- Total execution time
- User request text
- Error messages (if any)

## Example Trace

Here's what a typical trace looks like in LangSmith:

```
📊 Pipeline Generation Request
├── ⏱️ Duration: 12.3s
├── ✅ Status: Success
├── 💰 Cost: $0.0234
└── 📝 Steps:
    ├── [LLM] OpenAI GPT-4
    │   ├── Duration: 2.1s
    │   ├── Tokens: 450 (input: 320, output: 130)
    │   ├── Cost: $0.0087
    │   └── Decision: Call list_pipelines tool
    │
    ├── [Tool] list_pipelines
    │   ├── Duration: 0.3s
    │   ├── Input: {"org": "default", "project": "default"}
    │   └── Output: Found 3 existing pipelines
    │
    ├── [LLM] OpenAI GPT-4
    │   ├── Duration: 1.8s
    │   ├── Tokens: 380
    │   ├── Cost: $0.0073
    │   └── Decision: Call get_pipeline tool
    │
    ├── [Tool] get_pipeline
    │   ├── Duration: 0.2s
    │   ├── Input: {"name": "existing-pipeline"}
    │   └── Output: Retrieved pipeline YAML
    │
    └── [LLM] OpenAI GPT-4
        ├── Duration: 8.1s
        ├── Tokens: 1200
        ├── Cost: $0.0234
        └── Output: Generated new pipeline YAML
```

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LANGCHAIN_TRACING_V2` | Enable/disable tracing | `false` | No |
| `LANGCHAIN_API_KEY` | Your LangSmith API key | - | Yes (if tracing enabled) |
| `LANGCHAIN_PROJECT` | Project name in LangSmith | `harness-agent` | No |

### Project Names

You can organize traces by project:

```env
# Development
LANGCHAIN_PROJECT=harness-agent-dev

# Production
LANGCHAIN_PROJECT=harness-agent-prod

# Testing
LANGCHAIN_PROJECT=harness-agent-test
```

## Using LangSmith Dashboard

### Viewing Traces

1. Go to your LangSmith dashboard
2. Select your project (e.g., "harness-agent")
3. Click on any trace to see details

### Filtering Traces

Filter by:
- **Status** - Success/Error
- **Duration** - Slow requests
- **Cost** - Expensive calls
- **Date Range** - Time period
- **Tags** - Custom tags

### Comparing Runs

1. Select multiple traces
2. Click "Compare"
3. See side-by-side differences
4. Identify what changed

### Monitoring

View aggregated metrics:
- **Success Rate** - % of successful requests
- **Average Latency** - Response time trends
- **Token Usage** - Daily/weekly consumption
- **Cost** - Total spending
- **Error Rate** - Failure patterns

## Debugging with LangSmith

### Common Use Cases

#### 1. Agent Not Calling Tools
**Problem:** Agent generates response without using Harness tools

**Debug:**
1. Check trace in LangSmith
2. Look at LLM prompts
3. See if tools are in the prompt
4. Check tool descriptions

#### 2. Slow Responses
**Problem:** API takes too long to respond

**Debug:**
1. View trace timeline
2. Identify slow steps
3. Check if specific tools are slow
4. Optimize prompts to reduce LLM calls

#### 3. Wrong Tool Called
**Problem:** Agent calls incorrect tool

**Debug:**
1. Check LLM reasoning in trace
2. Review tool descriptions
3. Improve tool descriptions
4. Adjust system prompt

#### 4. Token Usage Too High
**Problem:** Requests are expensive

**Debug:**
1. View token breakdown
2. Identify which calls use most tokens
3. Optimize prompts
4. Reduce context size

## Best Practices

### 1. Use Different Projects for Environments

```env
# .env.dev
LANGCHAIN_PROJECT=harness-agent-dev

# .env.prod
LANGCHAIN_PROJECT=harness-agent-prod
```

### 2. Monitor Key Metrics

Set up alerts for:
- High error rates
- Slow response times
- Unusual token usage
- Cost spikes

### 3. Review Traces Regularly

- Check failed requests daily
- Review slow requests weekly
- Analyze token usage monthly
- Compare performance trends

### 4. Use Traces for Optimization

- Identify unnecessary tool calls
- Optimize prompts based on actual usage
- Reduce token consumption
- Improve error handling

## Disabling Tracing

To disable tracing:

### Option 1: Set to false
```env
LANGCHAIN_TRACING_V2=false
```

### Option 2: Remove from .env
```bash
# Comment out or remove these lines:
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=...
# LANGCHAIN_PROJECT=...
```

### Option 3: Unset environment variable
```bash
unset LANGCHAIN_TRACING_V2
```

## Performance Impact

### With Tracing Enabled:
- **Latency:** +50-100ms per request (network overhead)
- **Memory:** Negligible
- **CPU:** Negligible

### With Tracing Disabled:
- **Zero overhead** - No performance impact

## Privacy & Security

### What Gets Sent to LangSmith:
- ✅ Agent execution traces
- ✅ LLM prompts and responses
- ✅ Tool calls and results
- ✅ User requests

### What Doesn't Get Sent:
- ❌ Environment variables
- ❌ API keys (yours or Harness)
- ❌ Server logs
- ❌ Application code

### Security Considerations:
1. LangSmith API key should be kept secret
2. Traces may contain sensitive user data
3. Use separate projects for dev/prod
4. Review LangSmith's privacy policy
5. Consider disabling in production if handling sensitive data

## Troubleshooting

### Traces Not Appearing

**Check:**
1. `LANGCHAIN_TRACING_V2=true` (not "True" or "1")
2. API key is correct
3. Application was restarted after config change
4. Check application logs for errors

### Authentication Errors

**Error:** `Invalid API key`

**Solution:**
1. Verify API key in LangSmith dashboard
2. Check for extra spaces in `.env`
3. Regenerate API key if needed

### Network Errors

**Error:** `Failed to send trace`

**Solution:**
1. Check internet connection
2. Verify LangSmith is accessible
3. Check firewall settings
4. Try disabling and re-enabling

## Cost Considerations

### LangSmith Pricing:
- **Free Tier:** 5,000 traces/month
- **Developer:** $39/month for 50,000 traces
- **Team:** $199/month for 500,000 traces

### Recommendations:
- Use free tier for development
- Disable in production if high volume
- Enable only for debugging when needed
- Sample traces (trace 10% of requests)

## Advanced: Sampling Traces

If you want to trace only a percentage of requests (to reduce costs):

This would require code changes - let me know if you need this!

## Support

### LangSmith Documentation:
- [LangSmith Docs](https://docs.smith.langchain.com/)
- [Tracing Guide](https://docs.smith.langchain.com/tracing)
- [Python SDK](https://docs.smith.langchain.com/tracing/faq)

### Getting Help:
- LangSmith Discord
- LangChain GitHub Issues
- This project's GitHub Issues

## Summary

✅ **Zero code changes required**  
✅ **Automatic tracing of everything**  
✅ **Easy to enable/disable**  
✅ **Comprehensive debugging info**  
✅ **Cost and performance tracking**  
✅ **Free tier available**  

LangSmith integration provides powerful observability with minimal effort. Just add three environment variables and you're done!

