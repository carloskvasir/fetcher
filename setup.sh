#!/bin/bash
# Fetcher MCP Server Setup Script

echo "🚀 Setting up Fetcher MCP Server..."
echo "======================================"

# Check Python version
echo "📋 Checking Python version..."
if ! python3 --version | grep -q "Python 3"; then
    echo "❌ Python 3 is required but not found."
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Install dependencies
echo "📦 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip3 install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies installed successfully"
    else
        echo "❌ Failed to install dependencies"
        exit 1
    fi
else
    echo "❌ requirements.txt not found"
    exit 1
fi

# Setup environment file
echo "⚙️  Setting up environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo "📝 Please edit .env file with your API credentials"
    else
        echo "❌ .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x mcp_server.py
chmod +x mcp_client.py
chmod +x test_mcp.py
chmod +x setup.sh
echo "✅ Scripts are now executable"

# Test plugin loading
echo "🧪 Testing plugin loading..."
python3 -c "
from plugins.plugin_manager import PluginManager
manager = PluginManager()
manager.load_plugins()
print(f'✅ Loaded {len(manager.plugins)} plugins: {list(manager.plugins.keys())}')
"

if [ $? -eq 0 ]; then
    echo "✅ Plugin loading test successful"
else
    echo "❌ Plugin loading test failed"
    exit 1
fi

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials:"
echo "   nano .env"
echo ""
echo "2. Test the MCP server:"
echo "   python3 test_mcp.py"
echo ""
echo "3. Start the MCP server:"
echo "   python3 mcp_server.py"
echo ""
echo "4. Or test individual plugins:"
echo "   python3 fetcher.py github test"
echo "   python3 fetcher.py spotify test"
echo "   python3 fetcher.py trello test"
echo ""
echo "📖 See README.md for detailed usage instructions."
