"""
Trello Plugin for Fetcher

This plugin provides functionality to interact with Trello's API.

Commands:
    test - Test Trello plugin
    boards - List all boards
    board - Get board information: board [board_id]
    card - Get card information: card [card_id]
    list - Get list information: list [list_id]
    add_comment - Add a comment to a card: add_comment [card_id] [comment]
    move_card - Move a card to a different list: move_card [card_id] [list_id]
"""

import os
import json
import requests
from dotenv import load_dotenv
from .plugin_interface import PluginInterface

# Load environment variables from .env file
load_dotenv()

class Plugin(PluginInterface):
    def __init__(self):
        self.base_url = os.getenv('TRELLO_BASE_URL', 'https://api.trello.com/1')
        self.api_key = os.getenv('TRELLO_API_KEY')
        self.token = os.getenv('TRELLO_TOKEN')
        
        self._commands = {
            "test": "Test connection and show user information",
            "boards": "List all boards",
            "board": "Get board information: board [board_id]",
            "card": "Get card information: card [card_id]",
            "list": "Get list information: list [list_id]",
            "add_comment": "Add a comment to a card: add_comment [card_id] [comment]",
            "move_card": "Move a card to a different list: move_card [card_id] [list_id]"
        }

    def list_commands(self):
        """List all available plugin commands."""
        print("Available commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

    def fetch(self, endpoint, params=None):
        """Make a request to Trello API."""
        url = f"{self.base_url}/{endpoint}"
        default_params = {
            'key': self.api_key,
            'token': self.token
        }
        if params:
            default_params.update(params)
            
        response = requests.get(url, params=default_params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Please check if TRELLO_API_KEY and TRELLO_TOKEN environment variables are properly set.")
            return None

    def post(self, endpoint, data=None):
        """Make a POST request to Trello API."""
        url = f"{self.base_url}/{endpoint}"
        default_params = {
            'key': self.api_key,
            'token': self.token
        }
        
        response = requests.post(url, params=default_params, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error posting data to {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Please check if TRELLO_API_KEY and TRELLO_TOKEN environment variables are properly set.")
            return None

    def put(self, endpoint, data=None):
        """Make a PUT request to Trello API."""
        url = f"{self.base_url}/{endpoint}"
        default_params = {
            'key': self.api_key,
            'token': self.token
        }
        
        response = requests.put(url, params=default_params, json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error updating data at {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Please check if TRELLO_API_KEY and TRELLO_TOKEN environment variables are properly set.")
            return None

    def get_user_info(self):
        """Get authenticated user information."""
        user_data = self.fetch("members/me")
        if user_data:
            print("\nUser Information:")
            print(f"  Name: {user_data.get('fullName', 'N/A')}")
            print(f"  Username: {user_data.get('username', 'N/A')}")
            print(f"  Email: {user_data.get('email', 'N/A')}")
            print(f"  URL: {user_data.get('url', 'N/A')}")
            return user_data
        return None

    def list_boards(self):
        """List all boards for the authenticated user."""
        boards = self.fetch("members/me/boards")
        if boards:
            print("\nYour Boards:")
            for board in boards:
                print(f"- {board['name']} (ID: {board['id']})")
            return boards
        return None

    def get_board_info(self, board_id):
        """Get detailed information about a board."""
        board = self.fetch(f"boards/{board_id}", {'lists': 'open', 'cards': 'open'})
        if board:
            print(f"\nBoard: {board['name']}")
            print(f"Description: {board.get('desc', 'No description')}")
            print(f"URL: {board.get('url', 'No URL')}")
            
            if 'lists' in board:
                print("\nLists:")
                for lst in board['lists']:
                    print(f"- {lst['name']} (ID: {lst['id']})")
            
            if 'cards' in board:
                print("\nCards:")
                for card in board['cards']:
                    print(f"- {card['name']} (ID: {card['id']})")
            return board
        return None

    def get_card_info(self, card_id):
        """Get detailed information about a card."""
        card = self.fetch(f"cards/{card_id}")
        if card:
            print(f"\nCard: {card['name']}")
            print(f"Description: {card.get('desc', 'No description')}")
            print(f"Due Date: {card.get('due', 'No due date')}")
            print(f"URL: {card.get('url', 'No URL')}")
            return card
        return None

    def get_list_info(self, list_id):
        """Get detailed information about a list."""
        list_data = self.fetch(f"lists/{list_id}", {'cards': 'open'})
        if list_data:
            print(f"\nList: {list_data['name']}")
            print(f"Closed: {'Yes' if list_data.get('closed', False) else 'No'}")
            
            if 'cards' in list_data:
                print("\nCards in this list:")
                for card in list_data['cards']:
                    print(f"- {card['name']} (ID: {card['id']})")
            return list_data
        return None

    def add_comment_to_card(self, card_id, comment):
        """Add a comment to a card."""
        response = self.post(f"cards/{card_id}/actions/comments", {"text": comment})
        if response:
            print(f"\nComment added successfully to card {card_id}")
            return True
        return False

    def move_card(self, card_id, list_id):
        """Move a card to a different list."""
        response = self.put(f"cards/{card_id}", {"idList": list_id})
        if response:
            print(f"\nCard moved successfully to list {list_id}")
            return True
        return False

    def test(self):
        """Run basic plugin tests."""
        print("Testing Trello plugin...")
        
        print("\nTesting authentication:")
        user_data = self.get_user_info()
        
        if user_data:
            print("\nListing boards:")
            self.list_boards()

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        if command == "test":
            self.test()
        elif command == "boards":
            self.list_boards()
        elif command == "board":
            if len(args) < 1:
                print("Usage: board [board_id]")
                return
            self.get_board_info(args[0])
        elif command == "card":
            if len(args) < 1:
                print("Usage: card [card_id]")
                return
            self.get_card_info(args[0])
        elif command == "list":
            if len(args) < 1:
                print("Usage: list [list_id]")
                return
            self.get_list_info(args[0])
        elif command == "add_comment":
            if len(args) < 2:
                print("Usage: add_comment [card_id] [comment]")
                return
            self.add_comment_to_card(args[0], args[1])
        elif command == "move_card":
            if len(args) < 2:
                print("Usage: move_card [card_id] [list_id]")
                return
            self.move_card(args[0], args[1])
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

def plugin():
    """Create and return a new plugin instance."""
    return Plugin()
