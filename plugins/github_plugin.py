"""
GitHub Plugin for Fetcher

This plugin provides functionality to interact with GitHub's API.

Commands:
    fetch - Fetch data from GitHub
    list - List repositories
    search - Search for repositories
    test - Test GitHub plugin
    me - Show authenticated user information
"""

import requests
import json
import os
from .plugin_interface import PluginInterface

class Plugin(PluginInterface):
    def __init__(self):
        self.api_url = "https://api.github.com"
        self.headers = {}
        if 'GITHUB_TOKEN' in os.environ:
            self.headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
        self._commands = {
            "test": "Run basic plugin tests",
            "list": "List repositories for a user: list [username]",
            "search": "Search repositories: search [query]",
            "fetch": "Fetch data from a specific endpoint: fetch [endpoint]",
            "me": "Show authenticated user information"
        }

    def list_commands(self):
        """List all available plugin commands."""
        print("Available commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

    def fetch(self, endpoint, params=None):
        url = f"{self.api_url}/{endpoint}"
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Error fetching data from {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Please check if GITHUB_TOKEN environment variable is properly set.")
            return None

    def list_repos(self, username):
        """List repositories for a given username."""
        repos = self.fetch(f"users/{username}/repos")
        if repos:
            for repo in repos:
                print(f"- {repo['name']}: {repo['description']}")

    def search_repos(self, query):
        """Search GitHub repositories."""
        repos = self.fetch("search/repositories", {"q": query})
        if repos and 'items' in repos:
            for repo in repos['items']:
                print(f"- {repo['full_name']}: {repo['description']}")

    def test(self):
        """Run basic plugin tests."""
        print("Testing GitHub plugin...")
        
        print("\nTesting authentication:")
        user_data = self.get_user_info()
        
        if user_data:
            print("\nListing repositories for authenticated user:")
            self.list_repos(user_data['login'])
        else:
            print("\nListing repositories for user 'carloskvasir':")
            self.list_repos("carloskvasir")
        
        print("\nSearching repositories with 'python fetcher':")
        self.search_repos("python fetcher")

    def get_user_info(self):
        """Get authenticated user information."""
        user_data = self.fetch("user")
        if user_data:
            print("\nUser Information:")
            print(f"  Name: {user_data.get('name', 'N/A')}")
            print(f"  Login: {user_data.get('login', 'N/A')}")
            print(f"  Bio: {user_data.get('bio', 'N/A')}")
            print(f"  Email: {user_data.get('email', 'N/A')}")
            print(f"  Location: {user_data.get('location', 'N/A')}")
            print(f"  Public repositories: {user_data.get('public_repos', 0)}")
            print(f"  Followers: {user_data.get('followers', 0)}")
            print(f"  Following: {user_data.get('following', 0)}")
            return user_data
        return None

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        if command == "test":
            self.test()
        elif command == "list":
            if len(args) < 1:
                print("Usage: list [username]")
                return
            username = args[0]
            self.list_repos(username)
        elif command == "search":
            if len(args) < 1:
                print("Usage: search [query]")
                return
            query = args[0]
            self.search_repos(query)
        elif command == "fetch":
            if len(args) < 1:
                print("Usage: fetch [endpoint]")
                return
            endpoint = args[0]
            print(self.fetch(endpoint))
        elif command == "me":
            self.get_user_info()
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

def plugin():
    """Create and return a new plugin instance."""
    return Plugin()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python github.py [command] [options]")
        sys.exit(1)
    
    command = sys.argv[1]
    github = Plugin()
    github.run(command, *sys.argv[2:])
