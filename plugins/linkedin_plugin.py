"""
LinkedIn Plugin for Fetcher

This plugin provides functionality to interact with LinkedIn's API.

Commands:
    test - Test LinkedIn plugin
    me - Show authenticated user information
    posts - List recent posts
    share - Share a new post: share [text]
    connections - List your connections
"""

import os
import json
import requests
import webbrowser
import http.server
import socketserver
import urllib.parse
from threading import Thread
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .plugin_interface import PluginInterface

# Load environment variables
load_dotenv()

class Plugin(PluginInterface):
    def __init__(self):
        self.base_url = "https://api.linkedin.com/v2"
        self.auth_url = "https://www.linkedin.com/oauth/v2/accessToken"
        self.authorize_url = "https://www.linkedin.com/oauth/v2/authorization"
        
        # Load credentials
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.token_expiry = os.getenv('LINKEDIN_TOKEN_EXPIRY')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "\nLinkedIn credentials not found in environment variables!"
                "\nPlease make sure you have set:"
                "\n- LINKEDIN_CLIENT_ID"
                "\n- LINKEDIN_CLIENT_SECRET"
                "\nin your .env file"
            )
            
        self.redirect_uri = "http://127.0.0.1:3004/callback"
        self.scopes = ['openid', 'profile', 'w_member_social', 'email']
        
        self._commands = {
            "test": "Test connection and show user information",
            "me": "Show authenticated user information",
            "posts": "List your recent posts",
            "share": "Share a new post: share [text]",
            "connections": "List your connections"
        }

    def _save_token_to_env(self, access_token, expires_in):
        """Save access token and expiry time to .env file."""
        expiry_time = datetime.now() + timedelta(seconds=expires_in)
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # Read current file
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Remove old token lines if they exist
        lines = [l for l in lines if not l.startswith('LINKEDIN_ACCESS_TOKEN=') and 
                not l.startswith('LINKEDIN_TOKEN_EXPIRY=')]
        
        # Add new values
        lines.append(f'LINKEDIN_ACCESS_TOKEN={access_token}\n')
        lines.append(f'LINKEDIN_TOKEN_EXPIRY={expiry_time.isoformat()}\n')
        
        # Save file
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        # Update instance variables
        self.access_token = access_token
        self.token_expiry = expiry_time.isoformat()

    def _is_token_valid(self):
        """Check if current token is valid."""
        if not self.access_token or not self.token_expiry:
            return False
            
        try:
            expiry_time = datetime.fromisoformat(self.token_expiry)
            if datetime.now() >= expiry_time:
                return False
                
            # Test token with a simple API call
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.base_url}/me", headers=headers)
            return response.status_code == 200
            
        except (ValueError, TypeError):
            return False

    def _start_auth_server(self):
        """Start local server to receive OAuth callback."""
        class CallbackHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
                
                if 'code' in query_components:
                    # Store the auth code
                    self.server.auth_code = query_components['code'][0]
                    response = """
                    <html><body>
                        <h1>✅ Authorization completed!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body></html>
                    """
                else:
                    response = """
                    <html><body>
                        <h1>❌ Authorization error</h1>
                        <p>Please try again.</p>
                    </body></html>
                    """
                
                self.wfile.write(response.encode())
                
            def log_message(self, format, *args):
                # Disable HTTP server logs
                pass

        port = 3004
        self.redirect_uri = f"http://127.0.0.1:{port}/callback"
        
        try:
            # Create server
            server = socketserver.TCPServer(("127.0.0.1", port), CallbackHandler)
            server.auth_code = None
            server.allow_reuse_address = True
            
            # Start server in a thread
            server_thread = Thread(target=server.serve_forever)
            server_thread.daemon = False  # Change to non-daemon
            server_thread.start()
            print("Server started successfully on port", port)
            
            return server
            
        except Exception as e:
            print(f"\n❌ Error starting server: {str(e)}")
            if "Address already in use" in str(e):
                print("\nTip: Try again in a few seconds")
            return None

    def _get_user_auth(self):
        """Get user authorization through OAuth flow."""
        print("\n🔄 Starting authorization flow...")
        
        # Start local server
        server = self._start_auth_server()
        if not server:
            return None
        
        # Construct authorization URL
        auth_params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(self.scopes),
            'state': 'random_state_string'
        }
        
        auth_url = f"{self.authorize_url}?{'&'.join(f'{k}={v}' for k, v in auth_params.items())}"
        
        print("\n🌐 Opening browser for authorization...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        print("\n⏳ Waiting for authorization...")
        timeout = 300  # 5 minutes
        start_time = datetime.now()
        
        while not server.auth_code:
            if (datetime.now() - start_time).total_seconds() > timeout:
                print("\n❌ Authorization timeout. Please try again.")
                server.shutdown()
                return None
                
            if not Thread(target=server.serve_forever).is_alive():
                print("\n❌ Server stopped unexpectedly. Please try again.")
                return None
                
            time.sleep(1)
        
        auth_code = server.auth_code
        server.shutdown()
        
        return auth_code

    def _get_access_token(self):
        """Get access token from LinkedIn API."""
        if self._is_token_valid():
            return self.access_token
        
        # Get authorization code through OAuth flow
        auth_code = self._get_user_auth()
        if not auth_code:
            return None
        
        # Exchange authorization code for access token
        token_data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        response = requests.post(self.auth_url, data=token_data)
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info['access_token']
            expires_in = token_info.get('expires_in', 3600)  # Default to 1 hour if not provided
            
            # Save token to .env file
            self._save_token_to_env(access_token, expires_in)
            
            return access_token
        else:
            print(f"\n❌ Error getting access token: {response.status_code}")
            print(response.text)
            return None

    def list_commands(self):
        """List all available plugin commands."""
        print("Available commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

    def fetch(self, endpoint, params=None):
        """Make a GET request to LinkedIn API."""
        # Ensure we have a valid token
        access_token = self._get_access_token()
        if not access_token:
            return None

        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching data from {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Token might be expired.")
                # Clear token and try again
                self.access_token = None
                return self.fetch(endpoint, params)
            return None

    def post(self, endpoint, data):
        """Make a POST request to LinkedIn API."""
        # Ensure we have a valid token
        access_token = self._get_access_token()
        if not access_token:
            return None

        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code in [200, 201]:
            return response.json()
        else:
            print(f"Error posting data to {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Token might be expired.")
                # Clear token and try again
                self.access_token = None
                return self.post(endpoint, data)
            return None

    def get_user_info(self):
        """Get authenticated user information."""
        user_data = self.fetch("me")
        if user_data:
            print("\nUser Information:")
            print(f"  Name: {user_data.get('localizedFirstName', '')} {user_data.get('localizedLastName', '')}")
            print(f"  Headline: {user_data.get('headline', 'N/A')}")
            print(f"  ID: {user_data.get('id', 'N/A')}")
            return user_data
        return None

    def list_posts(self):
        """List user's recent posts."""
        posts = self.fetch(f"ugcPosts?q=authors&authors={self.get_user_info()['id']}")
        if posts and 'elements' in posts:
            print("\nYour Recent Posts:")
            for post in posts['elements']:
                print(f"- {post.get('specificContent', {}).get('com.linkedin.ugc.ShareContent', {}).get('shareCommentary', {}).get('text', 'No text')}")
            return posts['elements']
        return None

    def share_post(self, text):
        """Share a new post."""
        user_id = self.get_user_info()['id']
        post_data = {
            "author": f"urn:li:person:{user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = self.post("ugcPosts", post_data)
        if response:
            print("\nPost shared successfully!")
            return True
        return False

    def list_connections(self):
        """List user's connections."""
        connections = self.fetch("connections")
        if connections and 'elements' in connections:
            print("\nYour Connections:")
            for connection in connections['elements']:
                print(f"- {connection.get('firstName', '')} {connection.get('lastName', '')}")
            return connections['elements']
        return None

    def test(self):
        """Run basic plugin tests."""
        print("Testing LinkedIn plugin...")
        
        print("\nTesting authentication:")
        self.get_user_info()

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        if command == "test":
            self.test()
        elif command == "me":
            self.get_user_info()
        elif command == "posts":
            self.list_posts()
        elif command == "share":
            if len(args) < 1:
                print("Usage: share [text]")
                return
            self.share_post(args[0])
        elif command == "connections":
            self.list_connections()
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

def plugin():
    """Create and return a new plugin instance."""
    return Plugin()
