# Fetcher MCP Server Guide

This guide provides detailed information about using Fetcher with the Model Context Protocol (MCP).

## What is MCP?

MCP (Model Context Protocol) is a protocol developed by Anthropic that allows AI assistants to securely connect to external tools and data sources. It enables seamless integration between Large Language Models (LLMs) and external services.

## Architecture

```
AI Assistant (Claude, ChatGPT, etc.)
        ↓ MCP Protocol
    MCP Server (fetcher)
        ↓ Plugin System
    External APIs (GitHub, Spotify, Trello)
```

## Server Implementation

The Fetcher MCP Server (`mcp_server.py`) implements the following MCP methods:

- `list_tools` - Lists all available plugin commands as tools
- `call_tool` - Executes plugin commands and returns results
- `list_plugins` - Lists available plugins (custom method)
- `get_plugin_info` - Gets detailed plugin information (custom method)

## Tool Naming Convention

Tools are named using the pattern: `{plugin_name}_{command}`

Examples:
- `github_test` - GitHub plugin test command
- `spotify_search` - Spotify plugin search command
- `trello_boards` - Trello plugin boards command

## Request/Response Format

### Tool Execution Request
```json
{
  "id": "request_id",
  "method": "call_tool",
  "params": {
    "name": "github_search",
    "arguments": {
      "args": ["python cli"]
    }
  }
}
```

### Tool Execution Response
```json
{
  "id": "request_id",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Search results..."
      }
    ]
  }
}
```

## Error Handling

The MCP server handles various error conditions:

- **Invalid Methods** - Returns error for unknown MCP methods
- **Missing Parameters** - Validates required parameters
- **Plugin Errors** - Captures and reports plugin execution errors
- **Authentication Issues** - Reports credential problems

## Integration with AI Assistants

### Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "fetcher": {
      "command": "python3",
      "args": ["/path/to/fetcher/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/fetcher"
      }
    }
  }
}
```

### Custom Integration

For custom integrations, communicate with the server via stdin/stdout:

```python
import subprocess
import json

# Start server
process = subprocess.Popen(
    ["python3", "mcp_server.py"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send request
request = {
    "id": "1",
    "method": "list_tools",
    "params": {}
}
process.stdin.write(json.dumps(request) + "\n")
process.stdin.flush()

# Read response
response = json.loads(process.stdout.readline())
```

## Security Considerations

- **Credential Management** - Store API credentials in `.env` file
- **Input Validation** - All inputs are validated before plugin execution
- **Error Isolation** - Plugin errors don't crash the server
- **Read-only Operations** - Most tools are read-only by default

## Debugging

Enable debug logging:

```bash
export MCP_LOG_LEVEL=DEBUG
python3 mcp_server.py
```

Test individual components:

```bash
# Test plugin loading
python3 -c "from plugins.plugin_manager import PluginManager; m = PluginManager(); m.load_plugins(); print(list(m.plugins.keys()))"

# Test MCP server
python3 test_mcp.py

# Test specific plugin
python3 fetcher.py github test
```

## Performance

- **Async Operations** - Server uses asyncio for concurrent handling
- **Plugin Caching** - Plugins are loaded once at startup
- **Memory Efficient** - Minimal memory footprint
- **Fast Response** - Sub-second response times for most operations

## Extending the Server

To add new MCP methods:

1. Add method handler in `MCPServer` class:
```python
async def _my_custom_method(self, params: Dict[str, Any]) -> Any:
    # Implementation
    pass
```

2. Add routing in `handle_request`:
```python
elif request.method == "my_custom_method":
    result = await self._my_custom_method(request.params)
```

3. Update `mcp_config.json` with new capabilities
