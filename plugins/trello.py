# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Copyright (c) 2024 Carlos Kvasir
# https://github.com/carloskvasir
#

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_connection():
    try:
        url = f"{os.getenv('TRELLO_BASE_URL')}/members/me"
        params = {
            'key': os.getenv('TRELLO_API_KEY'),
            'token': os.getenv('TRELLO_TOKEN')
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✓ Connection to Trello established successfully!")
            print(f"User: {user_info['fullName']}")
            print(f"Email: {user_info['email']}")
            
            # List all boards
            boards_url = f"{os.getenv('TRELLO_BASE_URL')}/members/me/boards"
            boards_response = requests.get(boards_url, params=params)
            
            if boards_response.status_code == 200:
                boards = boards_response.json()
                print("\nYour Boards:")
                for board in boards:
                    print(f"- {board['name']} (ID: {board['id']})")
            
        elif response.status_code == 401:
            print("✗ Authentication error. Check your credentials in .env file")
        else:
            print(f"✗ Error connecting to Trello (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error trying to connect to Trello: {str(e)}")

def fetch_info(type=None, item_id=None):
    try:
        # Use 'card' as default type
        if type is None:
            type = 'card'
        
        if type not in ['card', 'board', 'list']:
            print(f"Invalid type: {type}. Supported types are: card, board, list")
            return

        url = f"{os.getenv('TRELLO_BASE_URL')}/{type}s/{item_id}"
        params = {
            'key': os.getenv('TRELLO_API_KEY'),
            'token': os.getenv('TRELLO_TOKEN')
        }
        
        if type == 'board':
            # For boards, also fetch lists and cards
            params['lists'] = 'open'
            params['cards'] = 'open'
            
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            info = response.json()
            if type == 'card':
                print(f"Card Name: {info['name']}")
                print(f"Description: {info['desc']}")
                print(f"Due Date: {info.get('due', 'No due date')}")
                print(f"URL: {info.get('url', 'No URL')}")
            elif type == 'board':
                print(f"Board Name: {info['name']}")
                print(f"Description: {info.get('desc', 'No description')}")
                print(f"URL: {info.get('url', 'No URL')}")
                
                if 'lists' in info:
                    print("\nLists:")
                    for lst in info['lists']:
                        print(f"- {lst['name']} (ID: {lst['id']})")
                        
                if 'cards' in info:
                    print("\nCards:")
                    for card in info['cards']:
                        print(f"- {card['name']} (ID: {card['id']})")
            elif type == 'list':
                print(f"List Name: {info['name']}")
                
                # Fetch cards in this list
                cards_url = f"{os.getenv('TRELLO_BASE_URL')}/lists/{item_id}/cards"
                cards_response = requests.get(cards_url, params=params)
                
                if cards_response.status_code == 200:
                    cards = cards_response.json()
                    print("\nCards in this list:")
                    for card in cards:
                        print(f"- {card['name']} (ID: {card['id']})")
        else:
            print(f"Unable to fetch information for {type} {item_id}.")
    except Exception as e:
        print(f"Error: {str(e)}")
