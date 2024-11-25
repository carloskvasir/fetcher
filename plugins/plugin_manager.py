import os
import importlib
import sys
from .plugin_interface import PluginInterface

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        plugin_dir = os.path.dirname(__file__)
        for filename in os.listdir(plugin_dir):
            if filename.endswith('_plugin.py') and filename != '__init__.py':
                # Remove '_plugin.py' from the filename to get the plugin name
                plugin_name = filename[:-10]  # remove '_plugin.py'
                try:
                    module = importlib.import_module(f'plugins.{filename[:-3]}')
                    if hasattr(module, 'Plugin'):
                        plugin_instance = module.Plugin()
                        if isinstance(plugin_instance, PluginInterface):
                            self.plugins[plugin_name] = plugin_instance
                        else:
                            print(f"Plugin {plugin_name} does not implement PluginInterface")
                except ImportError as e:
                    print(f"Error loading plugin {plugin_name}: {e}")

    def get_plugin_usage(self, plugin_name):
        if plugin_name in self.plugins:
            return self.plugins[plugin_name].usage()
        else:
            return f"Plugin '{plugin_name}' not found."

    def run_plugin(self, plugin_name, command=None, *args, **kwargs):
        if plugin_name in self.plugins:
            if command is None:
                self.plugins[plugin_name].list_commands()
            else:
                self.plugins[plugin_name].run(command, *args, **kwargs)
        else:
            print(f"Plugin '{plugin_name}' not found")
            print("Available plugins:")
            for name in self.plugins:
                print(f"  - {name}")

    def run(self, plugin_name, command, *args, **kwargs):
        if plugin_name in self.plugins:
            plugin = self.plugins[plugin_name]
            if hasattr(plugin, command):
                return getattr(plugin, command)(*args, **kwargs)
            else:
                print(f"Command '{command}' not found in plugin '{plugin_name}'")
        else:
            print(f"Plugin '{plugin_name}' not found")

    def load(self):
        self.load_plugins()

# Create a global instance of the plugin manager
manager = PluginManager()
manager.load()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'load':
            manager.load()
        elif command == 'run':
            if len(sys.argv) > 3:
                plugin_name = sys.argv[2]
                command = sys.argv[3]
                manager.run(plugin_name, command)
            else:
                print("Usage: python plugin_manager.py run <plugin_name> <command>")
        else:
            print("Usage: python plugin_manager.py [load|run]")
