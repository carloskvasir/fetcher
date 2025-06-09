"""
LinkedIn Web Plugin for Fetcher

This plugin provides functionality to interact with LinkedIn through their web API endpoints,
based on HAR analysis. It uses requests to simulate browser-like interactions.

Commands:
    profile - Get profile information
    search - Search for profiles: search [query]
    connect - Send connection request: connect [profile_url]
    posts - Get posts from feed
"""

import os
import json
import time
import requests
from urllib.parse import quote
from dotenv import load_dotenv
from .plugin_interface import PluginInterface

# Load environment variables
load_dotenv()

class Plugin(PluginInterface):
    def __init__(self):
        self.base_url = "https://www.linkedin.com"
        self.api_url = "https://www.linkedin.com/voyager/api"
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.session = requests.Session()
        self.csrf_token = None
        self._is_authenticated = False
        
        if not self.email or not self.password:
            raise ValueError(
                "\nLinkedIn credentials not found in environment variables!"
                "\nPlease make sure you have set:"
                "\n- LINKEDIN_EMAIL"
                "\n- LINKEDIN_PASSWORD"
                "\nin your .env file"
            )
        
        self._commands = {
            "profile": "Get profile information",
            "search": "Search for profiles: search [query]",
            "connect": "Send connection request: connect [profile_url]",
            "posts": "Get posts from feed"
        }
        
        # Default headers based on HAR analysis
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'accept': 'application/vnd.linkedin.normalized+json+2.1',
            'accept-language': 'en-US,en;q=0.9',
            'x-li-lang': 'en_US',
            'x-restli-protocol-version': '2.0.0',
            'x-li-track': '{"clientVersion":"1.13.89","mpVersion":"1.13.89","osName":"web","timezoneOffset":-7,"timezone":"America/Los_Angeles"}'
        }
    
    def _get_csrf_token(self):
        """Get CSRF token from login page"""
        try:
            response = self.session.get(f"{self.base_url}/login")
            if 'csrfToken' in response.text:
                csrf_token = response.text.split('csrfToken')[1].split('"')[2]
                return csrf_token
            if 'JSESSIONID' in self.session.cookies:
                return self.session.cookies['JSESSIONID'].replace('"', '')
            return None
        except Exception as e:
            print(f"❌ Failed to get CSRF token: {str(e)}")
            return None

    def _ensure_authenticated(self):
        """Ensure we're authenticated before making requests"""
        if self._is_authenticated:
            # Test if session is still valid
            try:
                test_response = self.session.get(
                    f"{self.api_url}/me",
                    headers=self.headers
                )
                if test_response.status_code == 200:
                    return True
            except:
                pass
        
        # Need to authenticate
        return self._login()

    def _login(self):
        """Login to LinkedIn using requests"""
        try:
            # Get CSRF token
            self.csrf_token = self._get_csrf_token()
            if not self.csrf_token:
                print("❌ Failed to get CSRF token")
                return False
            
            # Update headers with CSRF token
            self.headers['csrf-token'] = self.csrf_token
            self.session.headers.update(self.headers)
            
            # Login request
            login_data = {
                'session_key': self.email,
                'session_password': self.password,
                'csrfToken': self.csrf_token,
                'loginCsrfParam': self.csrf_token,
            }
            
            response = self.session.post(
                f"{self.base_url}/checkpoint/lg/login-submit",
                data=login_data,
                headers=self.headers,
                allow_redirects=True
            )
            
            # Verify login success
            if response.status_code == 200:
                # Test API access
                test_response = self.session.get(
                    f"{self.api_url}/me",
                    headers=self.headers
                )
                if test_response.status_code == 200:
                    self._is_authenticated = True
                    return True
            
            self._is_authenticated = False
            return False
            
        except Exception as e:
            self._is_authenticated = False
            print(f"❌ Login failed: {str(e)}")
            return False
    
    def _get_profile(self):
        """Get profile information"""
        try:
            response = self.session.get(
                f"{self.api_url}/me",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Failed to get profile: {str(e)}")
            return None
    
    def _search_profiles(self, query):
        """Search for profiles"""
        try:
            params = {
                'keywords': query,
                'origin': 'GLOBAL_SEARCH_HEADER',
                'q': 'all',
                'start': 0
            }
            response = self.session.get(
                f"{self.api_url}/search/blended",
                params=params,
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Search failed: {str(e)}")
            return None
    
    def _send_connection_request(self, profile_url):
        """Send connection request"""
        try:
            # Extract profile ID from URL
            profile_id = profile_url.split('/in/')[-1].split('/')[0]
            
            # Get invitation token
            token_response = self.session.get(
                f"{self.api_url}/growth/normInvitations",
                params={'q': 'invitee', 'profileID': profile_id},
                headers=self.headers
            )
            
            if token_response.status_code != 200:
                return False
                
            # Send connection request
            data = {
                'invitee': {
                    'com.linkedin.voyager.growth.invitation.InviteeProfile': {
                        'profileId': profile_id
                    }
                },
                'trackingId': token_response.json().get('trackingId')
            }
            
            response = self.session.post(
                f"{self.api_url}/growth/normInvitations",
                json=data,
                headers=self.headers
            )
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"❌ Failed to send connection request: {str(e)}")
            return False
    
    def _get_feed_posts(self):
        """Get posts from feed"""
        try:
            response = self.session.get(
                f"{self.api_url}/feed/updates",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Failed to get feed posts: {str(e)}")
            return None

    def run(self, command, *args):
        """Run a command with arguments"""
        # Ensure we're authenticated before running any command
        if not self._ensure_authenticated():
            print("❌ Authentication failed")
            return None
            
        if command == "profile":
            return self._get_profile()
        elif command == "search":
            if not args:
                print("❌ Please provide a search query")
                return None
            return self._search_profiles(args[0])
        elif command == "connect":
            if not args:
                print("❌ Please provide a profile URL")
                return None
            return self._send_connection_request(args[0])
        elif command == "posts":
            return self._get_feed_posts()
        else:
            print(f"❌ Unknown command: {command}")
            return None

    def list_commands(self):
        """List available commands"""
        return self._commands

    def test(self):
        """Test the plugin"""
        try:
            success = self._ensure_authenticated()
            if success:
                print("✅ LinkedIn Web plugin test successful")
                return True
            else:
                print("❌ LinkedIn Web plugin test failed")
                return False
        except Exception as e:
            print(f"❌ LinkedIn Web plugin test failed: {str(e)}")
            return False

    def __del__(self):
        """Cleanup when object is destroyed"""
        if self.session:
            self.session.close()

# Create plugin instance
def plugin():
    return Plugin()
