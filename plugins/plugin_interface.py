from abc import ABC, abstractmethod

class PluginInterface(ABC):
    @abstractmethod
    def test(self):
        """Run basic plugin tests to verify functionality."""
        pass

    @abstractmethod
    def list_commands(self):
        """List all available plugin commands."""
        pass

    @abstractmethod
    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command.
        
        Args:
            command (str): Name of the command to execute
            *args: Positional arguments for the command
            **kwargs: Named arguments for the command
        """
        pass
