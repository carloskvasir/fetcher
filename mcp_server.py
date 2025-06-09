#!/usr/bin/env python3
"""
MCP Server for Fetcher - Allows LLMs to interact with Fetcher plugins through MCP protocol.
"""

import asyncio
import contextlib
import io
import json
import logging
import os
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from plugins.plugin_manager import PluginManager

# Configure logging based on environment variable
log_level = os.getenv('MCP_LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_startup_info():
    """Print comprehensive startup information."""
    print("=" * 80, file=sys.stderr)
    print("🚀 FETCHER MCP SERVER STARTING", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("", file=sys.stderr)
    
    print("📋 CONFIGURAÇÃO / CONFIGURATION:", file=sys.stderr)
    print("", file=sys.stderr)
    
    print("🔧 Claude Desktop (recomendado/recommended):", file=sys.stderr)
    current_dir = os.path.abspath(os.path.dirname(__file__))
    print(f'   Adicione ao ~/.config/claude_desktop/config.json:', file=sys.stderr)
    print(f'   {{', file=sys.stderr)
    print(f'     "mcpServers": {{', file=sys.stderr)
    print(f'       "fetcher": {{', file=sys.stderr)
    print(f'         "command": "python3",', file=sys.stderr)
    print(f'         "args": ["{current_dir}/mcp_server.py"],', file=sys.stderr)
    print(f'         "env": {{', file=sys.stderr)
    print(f'           "PYTHONPATH": "{current_dir}"', file=sys.stderr)
    print(f'         }}', file=sys.stderr)
    print(f'       }}', file=sys.stderr)
    print(f'     }}', file=sys.stderr)
    print(f'   }}', file=sys.stderr)
    print("", file=sys.stderr)
    
    print("🌐 URL/HTTP Integration:", file=sys.stderr)
    print("   Este servidor usa stdin/stdout (não HTTP)", file=sys.stderr)
    print("   This server uses stdin/stdout (not HTTP)", file=sys.stderr)
    print("   Para integração HTTP, use um wrapper MCP-HTTP", file=sys.stderr)
    print("   For HTTP integration, use an MCP-HTTP wrapper", file=sys.stderr)
    print("", file=sys.stderr)
    
    print("🧪 Teste manual / Manual testing:", file=sys.stderr)
    print(f"   python3 {current_dir}/test_mcp.py", file=sys.stderr)
    print(f"   python3 {current_dir}/mcp_client.py", file=sys.stderr)
    print("", file=sys.stderr)
    
    print("🔍 Debug mode:", file=sys.stderr)
    print("   MCP_LOG_LEVEL=DEBUG python3 mcp_server.py", file=sys.stderr)
    print("", file=sys.stderr)
    
    print("⚙️  Variáveis de ambiente / Environment variables:", file=sys.stderr)
    env_vars = ['GITHUB_TOKEN', 'SPOTIFY_CLIENT_ID', 'TRELLO_API_KEY', 'TRELLO_TOKEN']
    for var in env_vars:
        value = os.getenv(var)
        status = "✅ Configurado" if value else "❌ Não configurado"
        print(f"   {var}: {status}", file=sys.stderr)
    print("", file=sys.stderr)
    
    print("=" * 80, file=sys.stderr)
    print("", file=sys.stderr)

@dataclass
class MCPRequest:
    """Represents an MCP request."""
    id: Union[str, int]
    method: str
    params: Optional[Dict[str, Any]] = None

@dataclass
class MCPResponse:
    """Represents an MCP response."""
    id: Union[str, int]
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None

class MCPServer:
    """MCP Server implementation for Fetcher."""
    
    def __init__(self):
        self.plugin_manager = PluginManager()
        logger.info("🔌 Carregando plugins / Loading plugins...")
        self.plugin_manager.load_plugins()
        
        # Log loaded plugins with details
        if self.plugin_manager.plugins:
            logger.info(f"✅ Plugins carregados / Loaded plugins: {list(self.plugin_manager.plugins.keys())}")
            
            # Show available tools for each plugin
            for plugin_name, plugin in self.plugin_manager.plugins.items():
                if hasattr(plugin, '_commands'):
                    commands = list(plugin._commands.keys())
                    logger.info(f"   📦 {plugin_name}: {commands}")
                else:
                    logger.info(f"   📦 {plugin_name}: [test]")
        else:
            logger.warning("⚠️  Nenhum plugin carregado / No plugins loaded")
            
        logger.info("🎯 Servidor MCP pronto para receber requisições / MCP Server ready for requests")
        
    async def handle_request(self, request_data: str) -> str:
        """Handle incoming MCP request."""
        try:
            logger.debug(f"📨 Requisição recebida / Received request: {request_data}")
            
            request_json = json.loads(request_data)
            request = MCPRequest(
                id=request_json.get("id"),
                method=request_json.get("method"),
                params=request_json.get("params", {})
            )
            
            logger.info(f"🔄 Processando método / Processing method: {request.method}")
            
            # Route request to appropriate handler
            if request.method == "initialize":
                result = await self._initialize(request.params)
            elif request.method == "notifications/initialized":
                # Notification - no response needed, but acknowledge it
                logger.info("✅ Cliente inicializado / Client initialized")
                return ""  # Return empty string for notifications
            elif request.method.startswith("notifications/"):
                # Handle other notifications
                logger.info(f"📢 Notificação recebida / Notification received: {request.method}")
                return ""  # Return empty string for notifications
            elif request.method == "tools/list":
                result = await self._tools_list(request.params)
            elif request.method == "tools/call":
                tool_name = request.params.get("name", "unknown")
                logger.info(f"🛠️  Executando ferramenta / Executing tool: {tool_name}")
                result = await self._tools_call(request.params)
            elif request.method == "list_plugins":
                result = await self._list_plugins()
            elif request.method == "get_plugin_info":
                result = await self._get_plugin_info(request.params)
            else:
                raise ValueError(f"Método desconhecido / Unknown method: {request.method}")
                
            response = MCPResponse(id=request.id, result=result)
            logger.debug(f"✅ Resposta / Response: {response}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao processar requisição / Error handling request: {e}")
            response = MCPResponse(
                id=request_json.get("id") if 'request_json' in locals() else None,
                error={"code": -1, "message": str(e)}
            )
            
        response_str = json.dumps({
            "jsonrpc": "2.0",
            "id": response.id,
            "result": response.result,
            "error": response.error
        })
        
        logger.debug(f"📤 Enviando resposta / Sending response: {response_str}")
        return response_str
    
    async def _initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize the MCP server - required by MCP protocol."""
        logger.info("🤝 Inicializando servidor MCP / Initializing MCP server")
        
        # Return server capabilities
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": False
                },
                "logging": {}
            },
            "serverInfo": {
                "name": "fetcher-mcp-server",
                "version": "1.0.0"
            }
        }
    
    def _get_input_schema(self, plugin_name: str, command: str) -> Dict[str, Any]:
        """Get specific input schema for a command."""
        if plugin_name == "github":
            if command == "issue":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "issue_number": {
                            "type": ["string", "number"],
                            "description": "Issue number to retrieve"
                        }
                    },
                    "required": ["owner_repo", "issue_number"]
                }
            elif command == "issues":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "state": {
                            "type": "string",
                            "description": "Issue state: open, closed, or all",
                            "default": "open"
                        }
                    },
                    "required": ["owner_repo"]
                }
            elif command == "repo":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        }
                    },
                    "required": ["owner_repo"]
                }
            elif command == "list":
                return {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username to list repositories for"
                        }
                    },
                    "required": ["username"]
                }
            elif command == "search":
                return {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for repositories"
                        }
                    },
                    "required": ["query"]
                }
            elif command == "create_issue":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body/description",
                            "default": ""
                        }
                    },
                    "required": ["owner_repo", "title"]
                }
        
        # Default schema for other commands
        return {
            "type": "object",
            "properties": {
                "arguments": {
                    "type": "object",
                    "description": "Command arguments"
                }
            }
        }
    
    async def _tools_list(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """List all available tools (MCP standard method)."""
        tools = []
        
        logger.info("🔍 Listando ferramentas disponíveis / Listing available tools")
        
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            # Get plugin commands
            if hasattr(plugin, '_commands'):
                for command, description in plugin._commands.items():
                    tool_name = f"{plugin_name}_{command}"
                    
                    # Create specific input schemas for different commands
                    input_schema = self._get_input_schema(plugin_name, command)
                    
                    tools.append({
                        "name": tool_name,
                        "description": f"{plugin_name}: {description}",
                        "inputSchema": input_schema
                    })
                    logger.debug(f"   🔧 {tool_name}: {description}")
            else:
                # Default commands for plugins without _commands attribute
                tool_name = f"{plugin_name}_test"
                tools.append({
                    "name": tool_name,
                    "description": f"{plugin_name}: Run plugin tests",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "arguments": {
                                "type": "object",
                                "description": "Command arguments"
                            }
                        }
                    }
                })
                logger.debug(f"   🔧 {tool_name}: Run plugin tests")
        
        logger.info(f"📊 Total de ferramentas / Total tools: {len(tools)}")
        
        # Return in MCP-compliant format
        return {
            "tools": tools
        }
    
    def _get_input_schema(self, plugin_name: str, command: str) -> Dict[str, Any]:
        """Get specific input schema for a command."""
        if plugin_name == "github":
            if command == "issue":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "issue_number": {
                            "type": ["string", "number"],
                            "description": "Issue number to retrieve"
                        }
                    },
                    "required": ["owner_repo", "issue_number"]
                }
            elif command == "issues":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "state": {
                            "type": "string",
                            "description": "Issue state: open, closed, or all",
                            "default": "open"
                        }
                    },
                    "required": ["owner_repo"]
                }
            elif command == "repo":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        }
                    },
                    "required": ["owner_repo"]
                }
            elif command == "list":
                return {
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub username to list repositories for"
                        }
                    },
                    "required": ["username"]
                }
            elif command == "search":
                return {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query for repositories"
                        }
                    },
                    "required": ["query"]
                }
            elif command == "create_issue":
                return {
                    "type": "object",
                    "properties": {
                        "owner_repo": {
                            "type": "string",
                            "description": "Repository in format owner/repo (e.g., microsoft/vscode)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body/description",
                            "default": ""
                        }
                    },
                    "required": ["owner_repo", "title"]
                }
        
        # Default schema for other commands
        return {
            "type": "object",
            "properties": {
                "arguments": {
                    "type": "object",
                    "description": "Command arguments"
                }
            }
        }

    async def _call_tool(self, params: Dict[str, Any]) -> Any:
        """Call a specific tool (plugin command)."""
        tool_name = params.get("name")
        # Support both 'args' and 'arguments' for compatibility
        args = params.get("args", params.get("arguments", []))
        
        # Convert arguments dict to list if needed (VS Code might send arguments as dict)
        if isinstance(args, dict):
            # Handle different argument formats based on the tool
            if tool_name.endswith('_issue') and 'owner_repo' in args and 'issue_number' in args:
                args = [args['owner_repo'], str(args['issue_number'])]
            elif tool_name.endswith('_issues') and 'owner_repo' in args:
                state = args.get('state', 'open')
                args = [args['owner_repo'], state]
            elif tool_name.endswith('_repo') and 'owner_repo' in args:
                args = [args['owner_repo']]
            elif tool_name.endswith('_list') and 'username' in args:
                args = [args['username']]
            elif tool_name.endswith('_search') and 'query' in args:
                args = [args['query']]
            elif tool_name.endswith('_create_issue') and 'owner_repo' in args and 'title' in args:
                title = args['title']
                body = args.get('body', '')
                args = [args['owner_repo'], title, body]
            else:
                # Extract values from dict in order they appear
                args = list(args.values())
        elif not isinstance(args, list):
            args = []
        
        if not tool_name:
            raise ValueError("Nome da ferramenta não fornecido / Tool name not provided")
        
        logger.info(f"🎯 Executando / Executing: {tool_name} com args: {args}")
        
        # Parse plugin name and command from tool name
        if "_" not in tool_name:
            raise ValueError(f"Nome de ferramenta inválido / Invalid tool name: {tool_name}")
        
        plugin_name, command = tool_name.split("_", 1)
        
        if plugin_name not in self.plugin_manager.plugins:
            raise ValueError(f"Plugin não encontrado / Plugin not found: {plugin_name}")
        
        plugin = self.plugin_manager.plugins[plugin_name]
        
        try:
            # Capture stdout to prevent plugin output from interfering with JSON response
            captured_output = io.StringIO()
            
            with contextlib.redirect_stdout(captured_output):
                # Execute the command
                if command == "test":
                    result = plugin.test()
                else:
                    result = plugin.run(command, *args)
            
            # Get the captured output
            plugin_output = captured_output.getvalue()
            
            logger.info(f"✅ Comando executado com sucesso / Command executed successfully: {tool_name}")
            
            # Combine plugin output with result
            if plugin_output.strip():
                final_result = plugin_output.strip()
                if result and str(result).strip() and str(result).strip() != "None":
                    final_result += f"\n\nResult: {result}"
            else:
                final_result = result if result is not None else "Command completed successfully"
            
            # Return the result in MCP-compliant format
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(final_result)
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na execução / Execution error: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing command: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    async def _tools_call(self, params: Dict[str, Any]) -> Any:
        """Call a specific tool (MCP standard method)."""
        tool_name = params.get("name")
        # Support both 'arguments' (MCP standard) and 'args' (compatibility)
        arguments = params.get("arguments", {})
        args = params.get("args", [])
        
        if not tool_name:
            raise ValueError("Nome da ferramenta não fornecido / Tool name not provided")
        
        logger.info(f"🎯 Executando / Executing: {tool_name} com arguments: {arguments}")
        
        # Parse plugin name and command from tool name
        if "_" not in tool_name:
            raise ValueError(f"Nome de ferramenta inválido / Invalid tool name: {tool_name}")
        
        plugin_name, command = tool_name.split("_", 1)
        
        if plugin_name not in self.plugin_manager.plugins:
            raise ValueError(f"Plugin não encontrado / Plugin not found: {plugin_name}")
        
        plugin = self.plugin_manager.plugins[plugin_name]
        
        try:
            # Capture stdout to prevent plugin output from interfering with JSON response
            captured_output = io.StringIO()
            
            with contextlib.redirect_stdout(captured_output):
                # Execute the command
                if command == "test":
                    result = plugin.test()
                else:
                    # Convert arguments dict to args list if needed
                    if arguments and not args:
                        # Try to extract arguments in some logical order
                        if isinstance(arguments, dict):
                            args = list(arguments.values())
                        else:
                            args = [arguments]
                    
                    result = plugin.run(command, *args)
            
            # Get the captured output
            plugin_output = captured_output.getvalue()
            
            logger.info(f"✅ Comando executado com sucesso / Command executed successfully: {tool_name}")
            
            # Combine plugin output with result
            if plugin_output.strip():
                final_result = plugin_output.strip()
                if result and str(result).strip() and str(result).strip() != "None":
                    final_result += f"\n\nResult: {result}"
            else:
                final_result = result if result is not None else "Command completed successfully"
            
            # Return the result in MCP-compliant format
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(final_result)
                    }
                ],
                "isError": False
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na execução / Execution error: {e}")
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing command: {str(e)}"
                    }
                ],
                "isError": True
            }

    async def _list_plugins(self) -> List[Dict[str, Any]]:
        """List all loaded plugins."""
        plugins = []
        
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            plugin_info = {
                "name": plugin_name,
                "class": plugin.__class__.__name__,
                "commands": []
            }
            
            if hasattr(plugin, '_commands'):
                plugin_info["commands"] = list(plugin._commands.keys())
            else:
                plugin_info["commands"] = ["test"]
            
            plugins.append(plugin_info)
        
        return plugins
    
    async def _get_plugin_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed information about a specific plugin."""
        # Accept both 'name' and 'plugin_name' for compatibility
        plugin_name = params.get("name") or params.get("plugin_name")
        
        if not plugin_name:
            raise ValueError("Nome do plugin não fornecido / Plugin name not provided")
        
        if plugin_name not in self.plugin_manager.plugins:
            raise ValueError(f"Plugin não encontrado / Plugin not found: {plugin_name}")
        
        plugin = self.plugin_manager.plugins[plugin_name]
        
        info = {
            "name": plugin_name,
            "class": plugin.__class__.__name__,
            "commands": {},
            "description": getattr(plugin, '__doc__', 'No description available')
        }
        
        if hasattr(plugin, '_commands'):
            info["commands"] = plugin._commands
        else:
            info["commands"] = {"test": "Run plugin tests"}
        
        return info

async def main():
    """Main server loop."""
    # Print startup information
    print_startup_info()
    
    server = MCPServer()
    
    logger.info("🌟 MCP Server para Fetcher iniciado / MCP Server for Fetcher started")
    logger.info(f"📦 Plugins carregados / Loaded plugins: {list(server.plugin_manager.plugins.keys())}")
    
    try:
        logger.info("⏳ Aguardando requisições via stdin / Waiting for requests via stdin...")
        
        while True:
            # Read from stdin
            line = sys.stdin.readline()
            if not line:
                logger.info("📛 EOF recebido, encerrando servidor / EOF received, shutting down server")
                break
                
            line = line.strip()
            if not line:
                continue
                
            # Process request
            response = await server.handle_request(line)
            
            # Write response to stdout (only if not empty)
            if response:
                print(response)
                sys.stdout.flush()
            
    except KeyboardInterrupt:
        logger.info("🛑 Servidor sendo encerrado por interrupção / Server shutting down due to interrupt...")
    except Exception as e:
        logger.error(f"❌ Erro no servidor / Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
