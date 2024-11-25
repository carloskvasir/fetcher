"""
Fetcher - A plugin-based CLI tool for fetching and managing information from multiple services.

Usage:
    python fetcher.py [plugin_name] [command] [args...]

"""

import sys
from plugins.plugin_manager import manager

def main():
    if len(sys.argv) < 2:
        print("Usage: python fetcher.py [plugin_name] [command] [args...]")
        print("\nAvailable plugins:")
        for name in manager.plugins:
            print(f"  - {name}")
        sys.exit(1)

    plugin_name = sys.argv[1]
    command = sys.argv[2] if len(sys.argv) > 2 else None
    args = sys.argv[3:] if len(sys.argv) > 3 else []
    
    manager.run_plugin(plugin_name, command, *args)

if __name__ == "__main__":
    main()
