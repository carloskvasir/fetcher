"""
Spotify Plugin for Fetcher - Simplified Version
Just run 'spotify me' to see your profile
"""

import os
import json
import requests
import base64
import webbrowser
import http.server
import socketserver
import urllib.parse
from threading import Thread
from datetime import datetime, timedelta
from dotenv import load_dotenv
from .plugin_interface import PluginInterface
import threading
import socket
import time

# Load environment variables
load_dotenv()

class Plugin(PluginInterface):
    def __init__(self):
        self.base_url = "https://api.spotify.com/v1"
        self.auth_url = "https://accounts.spotify.com/api/token"
        self.authorize_url = "https://accounts.spotify.com/authorize"
        
        # Load credentials
        self.client_id = os.getenv('SPOTIFY_CLIENT_ID')
        self.client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        self.access_token = os.getenv('SPOTIFY_ACCESS_TOKEN')
        self.token_expiry = os.getenv('SPOTIFY_TOKEN_EXPIRY')
        
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "\nSpotify credentials not found in environment variables!"
                "\nPlease make sure you have set:"
                "\n- SPOTIFY_CLIENT_ID"
                "\n- SPOTIFY_CLIENT_SECRET"
                "\nin your .env file"
            )
            
        self.redirect_uri = "http://127.0.0.1:3003/callback"
        
        # Expanded command list
        self._commands = {
            "me": "Show your Spotify profile",
            "search": "Search for tracks, artists, or albums: search [type] [query] (types: track, artist, album)",
            "top": "Show your top tracks or artists: top [type] (types: tracks, artists)",
            "recent": "Show your recently played tracks",
            "playlists": "List your playlists",
            "playlist": "Show details of a playlist: playlist [playlist_id]",
            "create-playlist": "Create a new playlist: create-playlist [name] [description]",
            "edit-playlist": "Edit playlist details: edit-playlist [playlist_id] [name] [description]",
            "add-to-playlist": "Add tracks to a playlist: add-to-playlist [playlist_id] [track_id1] [track_id2] ...",
            "following": "Show artists you are following",
            "recommendations": "Get track recommendations based on seed tracks or artists",
            "test": "Test the Spotify plugin authentication",
            "charts": "Show top charts: charts [country] [limit] (e.g., brazil 50)"
        }
            
    def _save_token_to_env(self, access_token, expires_in):
        """Save access token and expiry time to .env file."""
        expiry_time = datetime.now() + timedelta(seconds=expires_in)
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        
        # Ler o arquivo atual
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        # Remover linhas antigas do token se existirem
        lines = [l for l in lines if not l.startswith('SPOTIFY_ACCESS_TOKEN=') and 
                not l.startswith('SPOTIFY_TOKEN_EXPIRY=')]
        
        # Adicionar novos valores
        lines.append(f'SPOTIFY_ACCESS_TOKEN={access_token}\n')
        lines.append(f'SPOTIFY_TOKEN_EXPIRY={expiry_time.isoformat()}\n')
        
        # Salvar arquivo
        with open(env_path, 'w') as f:
            f.writelines(lines)
        
        # Atualizar variáveis da instância
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
                
            # Testar o token com uma chamada simples à API
            headers = {'Authorization': f'Bearer {self.access_token}'}
            response = requests.get(f"{self.base_url}/me", headers=headers)
            return response.status_code == 200
            
        except (ValueError, TypeError):
            return False

    def _get_auth_code(self):
        """Get authorization code via browser."""
        scopes = [
            'user-read-private',
            'user-read-email',
            'user-top-read',
            'user-read-recently-played',
            'playlist-read-private',
            'playlist-modify-public',
            'user-follow-read'
        ]
        
        auth_params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': ' '.join(scopes)
        }
        auth_code = [None]
        server = None
        port = 3003  # Porta fixa

        class Handler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                nonlocal auth_code
                query = urllib.parse.urlparse(self.path).query
                params = urllib.parse.parse_qs(query)
                
                if 'code' in params:
                    auth_code[0] = params['code'][0]
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    response_html = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                            <h2 style="color: #1DB954;">✅ Authentication Successful!</h2>
                            <p>You can close this window and return to the terminal.</p>
                        </body>
                    </html>
                    """
                    self.wfile.write(response_html.encode())
                    threading.Timer(0.5, server.shutdown).start()
                elif 'error' in params:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    error_msg = params['error'][0]
                    error_desc = params.get('error_description', [''])[0]
                    response_html = f"""
                    <html>
                        <body style="font-family: Arial, sans-serif; padding: 20px; text-align: center;">
                            <h2 style="color: #E21B3C;">❌ Authentication Error</h2>
                            <p>Error: {error_msg}</p>
                            <p>Description: {error_desc}</p>
                        </body>
                    </html>
                    """
                    self.wfile.write(response_html.encode())
                    threading.Timer(0.5, server.shutdown).start()
            
            def log_message(self, format, *args):
                pass
        
        try:
            server = socketserver.TCPServer(('127.0.0.1', port), Handler)
            server.allow_reuse_address = True
            server_thread = Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            auth_url = f"{self.authorize_url}?{urllib.parse.urlencode(auth_params)}"
            
            print("\nIMPORTANT: Before proceeding, make sure you have configured your Spotify App:")
            print("1. Go to https://developer.spotify.com/dashboard")
            print("2. Select your app")
            print("3. Click 'Settings'")
            print("4. Under 'Redirect URIs', add EXACTLY this URI:")
            print(f"   {self.redirect_uri}")
            print("5. Click 'Save' at the bottom\n")
            
            print("Opening browser for Spotify login...")
            webbrowser.open(auth_url)
            
            while auth_code[0] is None:
                time.sleep(1)
            
            return auth_code[0]
            
        except Exception as e:
            print(f"\n❌ Error starting local server: {str(e)}")
            return None
        finally:
            if server:
                server.server_close()

    def _get_access_token(self, auth_code=None):
        """Get access token using authorization code or refresh existing."""
        # Verificar se já temos um token válido
        if self._is_token_valid():
            return self.access_token

        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        if auth_code:
            data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri
            }
        else:
            print("\n🔑 Starting Spotify authorization...")
            new_auth_code = self._get_auth_code()
            if not new_auth_code:
                print("❌ Authorization failed")
                return None
            return self._get_access_token(new_auth_code)

        try:
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            data = response.json()
            access_token = data['access_token']
            expires_in = data['expires_in']
            
            # Salvar token no .env
            self._save_token_to_env(access_token, expires_in)
            
            return access_token
            
        except requests.exceptions.HTTPError as e:
            print(f"\n❌ Error: {e.response.status_code}")
            print(f"Response: {e.response.text}")
            if e.response.status_code == 401:
                print("\n🔧 Please check your Spotify Developer Dashboard settings:")
                print("1. Go to https://developer.spotify.com/dashboard")
                print("2. Select your app")
                print("3. Click 'Settings'")
                print("4. Verify these items:")
                print(f"   - Redirect URI is exactly: {self.redirect_uri}")
                print(f"   - Client ID and Secret are correct")
            return None
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return None

    def get_user_info(self):
        """Get and display user profile."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                print("Failed to get access token")
                return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me", headers=headers)

        if response.status_code == 200:
            user = response.json()
            print("\nYour Spotify Profile:")
            print(f"Name: {user.get('display_name')}")
            print(f"Email: {user.get('email')}")
            print(f"Country: {user.get('country')}")
            print(f"Account Type: {user.get('product')}")
            print(f"Followers: {user.get('followers', {}).get('total')}")
            
            if user.get('images'):
                print(f"Profile Image: {user['images'][0].get('url')}")
        elif response.status_code == 401:
            print("Token expired, getting new one...")
            self.access_token = None
            self.get_user_info()
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

    def search(self, query_type, query):
        """Search for tracks, artists, or albums."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        valid_types = ['track', 'artist', 'album']
        if query_type not in valid_types:
            print(f"\n❌ Invalid search type. Must be one of: {', '.join(valid_types)}")
            return

        params = {
            'q': query,
            'type': query_type,
            'limit': 10
        }
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/search", headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            results = data[f"{query_type}s"]['items']
            
            print(f"\n🔍 Search results for {query_type}: '{query}'")
            for i, item in enumerate(results, 1):
                if query_type == 'track':
                    print(f"\n{i}. 🎵 {item['name']}")
                    print(f"   👤 {', '.join(artist['name'] for artist in item['artists'])}")
                    print(f"   💿 {item['album']['name']}")
                    print(f"   🔗 {item['external_urls']['spotify']}")
                elif query_type == 'artist':
                    print(f"\n{i}. 👤 {item['name']}")
                    print(f"   👥 Followers: {item['followers']['total']:,}")
                    print(f"   🎭 Genres: {', '.join(item['genres'])}")
                    print(f"   🔗 {item['external_urls']['spotify']}")
                elif query_type == 'album':
                    print(f"\n{i}. 💿 {item['name']}")
                    print(f"   👤 {', '.join(artist['name'] for artist in item['artists'])}")
                    print(f"   📅 {item['release_date']}")
                    print(f"   🔗 {item['external_urls']['spotify']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_top_items(self, item_type):
        """Get user's top tracks or artists."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        if item_type not in ['tracks', 'artists']:
            print("\n❌ Invalid type. Must be 'tracks' or 'artists'")
            return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me/top/{item_type}", headers=headers)

        if response.status_code == 200:
            items = response.json()['items']
            print(f"\n🌟 Your Top {item_type.title()}:")
            for i, item in enumerate(items, 1):
                if item_type == 'tracks':
                    print(f"\n{i}. 🎵 {item['name']}")
                    print(f"   👤 {', '.join(artist['name'] for artist in item['artists'])}")
                    print(f"   💿 {item['album']['name']}")
                else:  # artists
                    print(f"\n{i}. 👤 {item['name']}")
                    print(f"   👥 Followers: {item['followers']['total']:,}")
                    print(f"   🎭 Genres: {', '.join(item['genres'])}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_recent_tracks(self):
        """Get user's recently played tracks."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me/player/recently-played", headers=headers)

        if response.status_code == 200:
            items = response.json()['items']
            print("\n🕒 Recently Played Tracks:")
            for i, item in enumerate(items, 1):
                track = item['track']
                played_at = datetime.fromisoformat(item['played_at'].replace('Z', '+00:00'))
                print(f"\n{i}. 🎵 {track['name']}")
                print(f"   👤 {', '.join(artist['name'] for artist in track['artists'])}")
                print(f"   💿 {track['album']['name']}")
                print(f"   ⏰ Played: {played_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_playlists(self):
        """Get user's playlists."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me/playlists", headers=headers)

        if response.status_code == 200:
            items = response.json()['items']
            print("\n📋 Your Playlists:")
            for i, playlist in enumerate(items, 1):
                print(f"\n{i}. 📝 {playlist['name']}")
                print(f"   ℹ️ {playlist['description']}" if playlist['description'] else "   ℹ️ No description")
                print(f"   🎵 Tracks: {playlist['tracks']['total']}")
                print(f"   🔗 ID: {playlist['id']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_playlist(self, playlist_id):
        """Get playlist details."""
        if not self.access_token:
            self._get_access_token()
            if not self.access_token:
                return

        url = f"{self.base_url}/playlists/{playlist_id}"
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            playlist = response.json()
            print(f"\n📝 Playlist: {playlist['name']}")
            print(f"ℹ️ {playlist['description']}")
            print(f"👤 Created by: {playlist['owner']['display_name']}")
            print(f"🎵 Total tracks: {playlist['tracks']['total']}")
            print(f"🔗 URL: {playlist['external_urls']['spotify']}\n")
            
            print("Tracks:\n")
            for i, item in enumerate(playlist['tracks']['items'], 1):
                track = item['track']
                print(f"{i}. 🎵 {track['name']}")
                print(f"   👤 {', '.join(artist['name'] for artist in track['artists'])}")
                print(f"   💿 {track['album']['name']}\n")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def create_playlist(self, name, description=None):
        """Create a new playlist."""
        if not self.access_token:
            self._get_access_token()
            if not self.access_token:
                return

        # Primeiro, precisamos do ID do usuário
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me", headers=headers)
        
        if response.status_code != 200:
            print("\n❌ Error getting user profile")
            return
            
        user_id = response.json()['id']
        
        # Agora criamos a playlist
        url = f"{self.base_url}/users/{user_id}/playlists"
        data = {
            'name': name,
            'description': description if description else '',
            'public': True
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            playlist = response.json()
            print(f"\n✅ Playlist created successfully!")
            print(f"Name: {playlist['name']}")
            print(f"Description: {playlist['description']}")
            print(f"URL: {playlist['external_urls']['spotify']}")
            print(f"ID: {playlist['id']}")
            print("\nTip: Use this ID with the 'playlist' command to view details")
        else:
            print(f"\n❌ Error creating playlist: {response.status_code}")
            print(f"Response: {response.text}")

    def add_tracks_to_playlist(self, playlist_id, track_ids):
        """Add tracks to a playlist."""
        if not self.access_token:
            self._get_access_token()
            if not self.access_token:
                return

        # Verificar se os IDs das músicas são válidos
        if not track_ids:
            print("\n❌ No tracks provided")
            return

        # Formatar os IDs das músicas para a API
        track_uris = [f"spotify:track:{track_id}" for track_id in track_ids]
        
        # Adicionar as músicas à playlist
        url = f"{self.base_url}/playlists/{playlist_id}/tracks"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        data = {'uris': track_uris}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            print(f"\n✅ Successfully added {len(track_ids)} track(s) to the playlist!")
            
            # Buscar informações das músicas adicionadas
            tracks_info = []
            for track_id in track_ids:
                track_url = f"{self.base_url}/tracks/{track_id}"
                track_response = requests.get(track_url, headers=headers)
                if track_response.status_code == 200:
                    track = track_response.json()
                    tracks_info.append(f"🎵 {track['name']} - {', '.join(artist['name'] for artist in track['artists'])}")
            
            print("\nAdded tracks:")
            for track_info in tracks_info:
                print(track_info)
        else:
            print(f"\n❌ Error adding tracks: {response.status_code}")
            print(f"Response: {response.text}")

    def edit_playlist(self, playlist_id, name=None, description=None):
        """Edit playlist details."""
        if not self.access_token:
            self._get_access_token()
            if not self.access_token:
                return

        url = f"{self.base_url}/playlists/{playlist_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Get current playlist details if we're only updating one field
        if name is None or description is None:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                current = response.json()
                if name is None:
                    name = current['name']
                if description is None:
                    description = current['description']
            else:
                print(f"\n❌ Error getting playlist details: {response.status_code}")
                return
        
        data = {
            'name': name,
            'description': description
        }
        
        response = requests.put(url, headers=headers, json=data)
        
        if response.status_code == 200:
            print(f"\n✅ Playlist updated successfully!")
            print(f"Name: {name}")
            print(f"Description: {description}")
        else:
            print(f"\n❌ Error updating playlist: {response.status_code}")
            print(f"Response: {response.text}")

    def get_following(self):
        """Get followed artists."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/me/following?type=artist", headers=headers)

        if response.status_code == 200:
            artists = response.json()['artists']['items']
            print("\n🎭 Artists you follow:")
            for i, artist in enumerate(artists, 1):
                print(f"\n{i}. 👤 {artist['name']}")
                print(f"   👥 Followers: {artist['followers']['total']:,}")
                print(f"   🎭 Genres: {', '.join(artist['genres'])}")
                print(f"   🔗 {artist['external_urls']['spotify']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_recommendations(self):
        """Get track recommendations."""
        if not self.access_token:
            self.access_token = self._get_access_token()
            if not self.access_token:
                return

        # Primeiro, pegamos as top tracks do usuário para usar como seed
        headers = {'Authorization': f'Bearer {self.access_token}'}
        top_tracks = requests.get(f"{self.base_url}/me/top/tracks?limit=5", headers=headers)

        if top_tracks.status_code != 200:
            print("\n❌ Error getting top tracks for recommendations")
            return

        seed_tracks = ','.join(track['id'] for track in top_tracks.json()['items'][:2])
        
        params = {
            'seed_tracks': seed_tracks,
            'limit': 10
        }

        response = requests.get(f"{self.base_url}/recommendations", headers=headers, params=params)

        if response.status_code == 200:
            tracks = response.json()['tracks']
            print("\n🎯 Recommended Tracks based on your top tracks:")
            for i, track in enumerate(tracks, 1):
                print(f"\n{i}. 🎵 {track['name']}")
                print(f"   👤 {', '.join(artist['name'] for artist in track['artists'])}")
                print(f"   💿 {track['album']['name']}")
                print(f"   🔗 {track['external_urls']['spotify']}")
        else:
            print(f"\n❌ Error: {response.status_code}")
            print(response.text)

    def get_charts(self, country="brazil", limit=10):
        """Get top charts for a specific country."""
        country = country.lower()
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        charts = {
            "brazil": {
                "top50": "37i9dQZEVXbMXbN3EUUhlg"
            }
        }
        
        if country not in charts:
            return f"Charts not available for {country}. Available countries: {', '.join(charts.keys())}"
        
        print(f"\n📊 Top Charts - {country.title()}\n")
        
        for chart_name, playlist_id in charts[country].items():
            response = requests.get(
                f"{self.base_url}/playlists/{playlist_id}",
                headers={"Authorization": f"Bearer {self.access_token}"}
            )
            
            if response.status_code != 200:
                print(f"❌ Error fetching {chart_name}: {response.status_code}")
                continue
                
            playlist = response.json()
            tracks = playlist["tracks"]["items"]
            
            print(f"\n🎵 {playlist['name']}")
            print(f"🔗 {playlist['external_urls']['spotify']}\n")
            
            for i, item in enumerate(tracks[:limit], 1):
                track = item["track"]
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                album = track["album"]["name"]
                duration_ms = track["duration_ms"]
                duration_min = duration_ms / (1000 * 60)
                print(f"{i}. {track['name']} - {artists}")
                print(f"   💿 {album}")
                print(f"   ⏱️  {duration_min:.1f}min")
                print(f"   🔗 {track['external_urls']['spotify']}\n")
            
            print(f"\nTotal tracks in playlist: {len(tracks)}")
            print("-" * 50)

    def test(self):
        """Run basic plugin test."""
        print("Testing Spotify plugin...")
        self.get_user_info()
        return True

    def run(self, command: str, *args, **kwargs):
        """Execute plugin command."""
        if not command:
            return self.list_commands()
            
        # Always check token before running commands
        if not self._is_token_valid():
            self._get_access_token()
            
        if command == "me":
            return self.get_user_info()
        elif command == "search" and len(args) >= 2:
            return self.search(args[0], " ".join(args[1:]))
        elif command == "top" and args:
            return self.get_top_items(args[0])
        elif command == "recent":
            return self.get_recent_tracks()
        elif command == "playlists":
            return self.get_playlists()
        elif command == "playlist" and args:
            return self.get_playlist(args[0])
        elif command == "create-playlist" and len(args) >= 1:
            name = args[0]
            description = " ".join(args[1:]) if len(args) > 1 else None
            return self.create_playlist(name, description)
        elif command == "edit-playlist" and len(args) >= 2:
            playlist_id = args[0]
            name = args[1]
            description = " ".join(args[2:]) if len(args) > 2 else None
            return self.edit_playlist(playlist_id, name, description)
        elif command == "add-to-playlist" and len(args) >= 2:
            playlist_id = args[0]
            track_ids = args[1:]
            return self.add_tracks_to_playlist(playlist_id, track_ids)
        elif command == "following":
            return self.get_following()
        elif command == "recommendations":
            return self.get_recommendations()
        elif command == "test":
            return self.test()
        elif command == "charts":
            country = args[0] if args else "brazil"
            limit = args[1] if len(args) > 1 else 10
            return self.get_charts(country, limit)
        else:
            return f"Unknown command: {command}\nUse 'spotify' to see available commands."

    def list_commands(self):
        print("\nAvailable commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

def plugin():
    """Create plugin instance."""
    return Plugin()
