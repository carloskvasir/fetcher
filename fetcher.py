#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2024 Carlos Kvasir
# https://github.com/carloskvasir
#

import os
import sys
import importlib.util

def load_plugin(plugin_name, command, item_id):
    """Load and execute the plugin"""
    try:
        # Import the plugin module
        plugin_path = os.path.join(os.path.dirname(__file__), f"plugins/{plugin_name}.py")
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)

        if command == 'check':
            plugin.check_connection()
        elif command == 'update':
            if ' ' not in item_id:
                print("Usage: ./fetcher.py github update <field> <value>")
                print("Supported fields: name, bio, location, company, blog")
                return
            field, value = item_id.split(' ', 1)  # Split only on first space
            if field == 'repo':
                if ' ' not in value:
                    print("Usage: ./fetcher.py github update repo <owner/repo> <description>")
                    return
                repo_name, description = value.split(' ', 1)
                plugin.update_repo(repo_name, description)
            else:
                plugin.update_profile(field, value)
        else:
            plugin.fetch_info(command, item_id)  # command is the type here
    except FileNotFoundError:
        print(f"Plugin '{plugin_name}' not found.")
    except AttributeError:
        print(f"Plugin '{plugin_name}' doesn't support this operation.")
    except Exception as e:
        print(f"Error: {str(e)}")

def show_usage():
    """Show usage information"""
    print("Usage: fetcher <plugin> [type] <ID|command>")
    print("Commands:")
    print("  check    - Check the connection to the service")
    print("\nExamples:")
    print("  fetcher trello 12345        # Fetch card (default)")
    print("  fetcher trello card 12345   # Fetch card explicitly")
    print("  fetcher trello board 67890  # Fetch board")
    print("  fetcher trello list 11111   # Fetch list")
    print("  fetcher trello check        # Check connection")
    print("  fetcher github update name Carlos")

def main():
    if len(sys.argv) < 3:
        show_usage()
        sys.exit(1)

    plugin_name = sys.argv[1]
    second_arg = sys.argv[2]

    if second_arg == 'check':
        command = 'check'
        item_id = None
    elif second_arg == 'update':
        if len(sys.argv) == 3:
            print("Usage: ./fetcher.py github update <field> <value>")
            print("Supported fields: name, bio, location, company, blog")
            sys.exit(1)
        command = 'update'
        item_id = ' '.join(sys.argv[3:])
    else:
        if len(sys.argv) == 3:
            # Just ID provided, use default type (card)
            command = 'card'
            item_id = second_arg
        else:
            # Type and ID provided
            command = second_arg  # This is the type
            item_id = sys.argv[3]

    load_plugin(plugin_name, command, item_id)

if __name__ == "__main__":
    main()
