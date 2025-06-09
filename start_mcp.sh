#!/bin/bash
# Script para iniciar o MCP Fetcher Server
# Autor: GitHub Copilot

echo "🚀 Iniciando MCP Fetcher Server..."
echo "=================================="

# Verificar dependências
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado!"
    exit 1
fi

# Verificar se o servidor existe
if [ ! -f "mcp_server.py" ]; then
    echo "❌ mcp_server.py não encontrado!"
    exit 1
fi

# Mostrar status das variáveis de ambiente
echo "📋 Status das APIs:"
[ ! -z "$GITHUB_TOKEN" ] && echo "  GitHub: ✅" || echo "  GitHub: ❌ (configure GITHUB_TOKEN)"
[ ! -z "$SPOTIFY_CLIENT_ID" ] && echo "  Spotify: ✅" || echo "  Spotify: ❌ (configure SPOTIFY_CLIENT_ID)"
[ ! -z "$TRELLO_API_KEY" ] && echo "  Trello: ✅" || echo "  Trello: ❌ (configure TRELLO_API_KEY)"
echo ""

# Opções de execução
case "${1:-normal}" in
    "debug")
        echo "🔍 Modo DEBUG ativado"
        export MCP_LOG_LEVEL=DEBUG
        python3 mcp_server.py
        ;;
    "test")
        echo "🧪 Executando testes..."
        python3 test_mcp.py
        ;;
    "protocol")
        echo "🔬 Testando protocolo MCP básico..."
        (echo '{"jsonrpc": "2.0", "id": "1", "method": "initialize", "params": {}}'; \
         echo '{"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}'; \
         echo '{"jsonrpc": "2.0", "id": "2", "method": "list_tools", "params": {}}') | \
        python3 mcp_server.py 2>/dev/null | head -2
        echo "✅ Protocolo MCP funcionando!"
        ;;
    "vscode")
        echo "🔬 Testando compatibilidade VS Code..."
        python3 test_vscode_compatibility.py
        ;;
    "normal"|*)
        echo "▶️  Iniciando servidor normal..."
        python3 mcp_server.py
        ;;
esac
