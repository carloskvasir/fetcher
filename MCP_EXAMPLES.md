# Fetcher MCP Examples for AI Assistants

This document provides examples of how AI assistants can interact with the Fetcher MCP server.

## Setup

First, ensure the MCP server is configured and running:

```bash
# Start the MCP server
python3 mcp_server.py
```

## Example Interactions

### GitHub Integration

**"Show me my GitHub profile"**
- Tool: `github_me`
- Result: User profile information, repositories count, followers, etc.

**"Search for Python CLI projects on GitHub"**
- Tool: `github_search`
- Args: `["python cli"]`
- Result: List of matching repositories with descriptions

**"List repositories for user 'carloskvasir'"**
- Tool: `github_list` 
- Args: `["carloskvasir"]`
- Result: User's public repositories

### Spotify Integration

**"Show my Spotify profile"**
- Tool: `spotify_me`
- Result: User profile, subscription type, country, etc.

**"What are my top artists?"**
- Tool: `spotify_top`
- Args: `["artists"]`
- Result: User's most listened artists

**"Search for 'The Beatles' songs"**
- Tool: `spotify_search`
- Args: `["track", "The Beatles"]`
- Result: Beatles tracks with Spotify links

**"Show me Brazil's top music charts"**
- Tool: `spotify_charts`
- Args: `["brazil"]`
- Result: Current top tracks in Brazil

**"What did I listen to recently?"**
- Tool: `spotify_recent`
- Result: Recently played tracks with timestamps

### Trello Integration

**"Show all my Trello boards"**
- Tool: `trello_boards`
- Result: List of user's boards with IDs and descriptions

**"Get details for board ID xyz123"**
- Tool: `trello_board`
- Args: `["xyz123"]`
- Result: Board details, lists, and cards

### LinkedIn Integration

**"Show my LinkedIn profile"**
- Tool: `linkedin_me`
- Result: Profile information, connections count, etc.

**"Get my LinkedIn connections"**
- Tool: `linkedin_connections`
- Result: List of connections (if authenticated)

## Complex Workflows

### Music Discovery Workflow
1. `spotify_recommendations` - Get personalized recommendations
2. `spotify_search` - Search for similar artists
3. `spotify_create_playlist` - Create playlist with found tracks

### Project Research Workflow  
1. `github_search` - Find repositories matching criteria
2. `github_list` - Explore specific user's projects
3. `trello_boards` - Document findings in project board

### Social Media Analysis
1. `linkedin_me` - Get profile analytics
2. `spotify_top` - Analyze music preferences
3. `github_me` - Review coding activity

## Error Handling

The MCP server gracefully handles various error conditions:

- **Authentication failures** - Clear error messages about missing credentials
- **API rate limits** - Informative messages about service limitations  
- **Invalid parameters** - Helpful guidance on correct usage
- **Network issues** - Timeout and connectivity error reporting

## Best Practices for AI Assistants

1. **Always test connection first** - Use `*_test` tools before other operations
2. **Handle authentication errors** - Guide users to set up credentials
3. **Respect rate limits** - Don't make too many rapid requests
4. **Provide context** - Explain what tools are being used and why
5. **Format results nicely** - Present data in user-friendly format

## Security Notes

- All API credentials are stored locally in `.env` file
- No credentials are transmitted through MCP protocol
- Tools perform read-only operations by default
- Write operations (like creating playlists) require explicit confirmation

## Integration Examples

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "fetcher": {
      "command": "python3",
      "args": ["/absolute/path/to/fetcher/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fetcher"
      }
    }
  }
}
```

### Custom MCP Client

```python
import json
import subprocess

def call_fetcher_tool(tool_name, args=[]):
    request = {
        "id": "1",
        "method": "call_tool", 
        "params": {
            "name": tool_name,
            "arguments": {"args": args}
        }
    }
    
    # Send to MCP server via stdin/stdout
    process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        text=True
    )
    
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    
    response = json.loads(process.stdout.readline())
    return response

# Example usage
result = call_fetcher_tool("github_me")
print(result)
```
