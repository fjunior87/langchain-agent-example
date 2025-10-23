# Harness Pipeline Agent Documentation

Complete documentation for the Harness Pipeline Agent project.

## Quick Links

- 📚 [Main README](../README.md) - Project overview and quick start
- 🚀 [Quick Start Guide](../QUICK_START.md) - Get up and running in 5 minutes

## Documentation Structure

### 📖 User Guide

Documentation for users of the Harness Pipeline Agent.

- **[Troubleshooting](user-guide/troubleshooting.md)** - Common issues and solutions
- **[Examples](user-guide/examples.md)** - Usage examples and patterns
- **[Docker Deployment](user-guide/docker-deployment.md)** - Running with Docker

### ✨ Features

Detailed guides for specific features and integrations.

- **[LangSmith Tracing](features/langsmith-tracing.md)** - Observability and debugging with LangSmith

### 🔧 Development

Documentation for developers working on the project.

- **[Debugging Guide](development/debugging-guide.md)** - How to debug the agent and troubleshoot issues

### 📜 History

Implementation notes, fixes, and change history.

- **[Change History Index](history/README.md)** - Overview of all changes
- **[Startup Fix](history/startup-fix.md)** - MCP server startup issues
- **[MCP Stdio Fix](history/mcp-stdio-fix.md)** - MCP stdio configuration
- **[Tool Call Fixes](history/tool-call-fixes.md)** - JSON parsing and Pydantic errors
- **[LangSmith Integration](history/langsmith-integration.md)** - Tracing implementation

## Getting Help

### For Users

1. Start with the [Quick Start Guide](../QUICK_START.md)
2. Check [Troubleshooting](user-guide/troubleshooting.md) for common issues
3. Review [Examples](user-guide/examples.md) for usage patterns
4. See [Docker Deployment](user-guide/docker-deployment.md) for container setup

### For Developers

1. Review [Debugging Guide](development/debugging-guide.md)
2. Check [Change History](history/README.md) for implementation details
3. Look at existing code patterns
4. Read feature-specific documentation

### For Issues

1. Check [Troubleshooting](user-guide/troubleshooting.md)
2. Review [Change History](history/README.md) for similar issues
3. Check application logs
4. Run debug scripts (`debug_config.py`, `test_mcp_connection.py`)

## Documentation Standards

### File Organization

```
docs/
├── README.md                    # This file
├── user-guide/                  # End-user documentation
│   ├── troubleshooting.md
│   ├── examples.md
│   └── docker-deployment.md
├── features/                    # Feature-specific guides
│   └── langsmith-tracing.md
├── development/                 # Developer documentation
│   └── debugging-guide.md
└── history/                     # Change history and fixes
    ├── README.md
    ├── startup-fix.md
    ├── mcp-stdio-fix.md
    ├── tool-call-fixes.md
    └── langsmith-integration.md
```

### Document Types

- **User Guides** - How to use features
- **Feature Docs** - Detailed feature documentation
- **Development Docs** - Technical implementation details
- **History Docs** - Changes, fixes, and lessons learned

### Writing Guidelines

- Use clear, concise language
- Include code examples
- Add troubleshooting sections
- Link to related documentation
- Keep documents focused and organized

## Contributing

When adding new documentation:

1. Choose the appropriate directory
2. Follow existing document structure
3. Update this README with links
4. Use descriptive filenames
5. Include examples and code snippets

## Quick Reference

### Common Tasks

| Task | Documentation |
|------|---------------|
| Install and setup | [Quick Start](../QUICK_START.md) |
| Troubleshoot issues | [Troubleshooting](user-guide/troubleshooting.md) |
| Deploy with Docker | [Docker Guide](user-guide/docker-deployment.md) |
| Enable tracing | [LangSmith](features/langsmith-tracing.md) |
| Debug problems | [Debugging](development/debugging-guide.md) |
| Understand changes | [History](history/README.md) |

### API Documentation

Interactive API documentation is available when the application is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## External Resources

- [Harness.io Documentation](https://docs.harness.io)
- [LangChain Documentation](https://python.langchain.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [LangSmith Documentation](https://docs.smith.langchain.com)

## Feedback

Documentation improvements are always welcome! If you find:
- Unclear instructions
- Missing information
- Errors or typos
- Opportunities for better examples

Please contribute improvements or report issues.

---

**Last Updated:** October 2024  
**Version:** 1.0.0

