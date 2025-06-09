"""
Spotify Plugin for Fetcher - Simplified Version
Just run 'spotify me' to see your profile
"""

import base64
import getpass
import http.server
import json
import os
import re
import socket
import socketserver
import threading
import time
import urllib.parse
import uuid
import webbrowser
from datetime import datetime, timedelta
from threading import Thread

import psutil
import requests
from dotenv import load_dotenv

from .plugin_interface import PluginInterface

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
        self.client_token = os.getenv('SPOTIFY_CLIENT_TOKEN')  # Add client token
        
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
            "charts": "Show top charts: charts [country] [limit] (e.g., brazil 50)",
            "set-name": "Change your Spotify display name: set-name [new_name]"
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
                        <h1>✅ Autorização concluída!</h1>
                        <p>Você pode fechar esta janela e voltar ao terminal.</p>
                    </body></html>
                    """
                else:
                    response = """
                    <html><body>
                        <h1>❌ Erro na autorização</h1>
                        <p>Por favor, tente novamente.</p>
                    </body></html>
                    """
                
                self.wfile.write(response.encode())
                
            def log_message(self, format, *args):
                # Desabilita logs do servidor HTTP
                pass

        port = 3003  # Porta fixa que está configurada no Spotify Developer Dashboard
        self.redirect_uri = f"http://127.0.0.1:{port}/callback"
        
        # Tentar matar qualquer processo que esteja usando a porta
        try:
            import psutil
            for proc in psutil.process_iter():
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn, 'laddr') and isinstance(conn.laddr, tuple) and len(conn.laddr) >= 2:
                            if conn.laddr[1] == port:
                                print(f"\n🔄 Finalizando processo anterior na porta {port}...")
                                proc.terminate()
                                time.sleep(1)  # Esperar processo terminar
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception as e:
            # Se psutil falhar, tentar socket
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('127.0.0.1', port))
                    s.close()
            except socket.error:
                print(f"\n⚠️ A porta {port} está em uso. Por favor, aguarde um momento e tente novamente.")
                time.sleep(5)  # Dar tempo para o processo anterior terminar
        
        try:
            # Create server
            server = socketserver.TCPServer(("127.0.0.1", port), CallbackHandler)
            server.auth_code = None
            server.allow_reuse_address = True  # Permite reusar a porta se ela ainda estiver em TIME_WAIT
            
            # Start server in a thread
            server_thread = Thread(target=server.serve_forever)
            server_thread.daemon = True
            server_thread.start()
            
            return server
            
        except Exception as e:
            print(f"\n❌ Erro ao iniciar servidor: {str(e)}")
            if "Address already in use" in str(e):
                print("\nDica: Tente novamente em alguns segundos")
            return None

    def _get_user_auth(self):
        """Get user authorization through OAuth flow."""
        print("\n🔄 Iniciando fluxo de autorização...")
        
        # Start local server
        try:
            server = self._start_auth_server()
        except Exception as e:
            print(f"\n❌ Erro ao iniciar servidor local: {str(e)}")
            return None
        
        # Build authorization URL
        # Escopos oficiais do Spotify: https://developer.spotify.com/documentation/web-api/concepts/scopes
        scope = (
            "user-read-private "           # Ler perfil privado
            "user-read-email "             # Ler email
            "user-read-currently-playing "  # Ler música atual
            "playlist-read-private "        # Ler playlists privadas
            "playlist-modify-public "       # Modificar playlists públicas
            "playlist-modify-private "      # Modificar playlists privadas
            "user-read-playback-state "     # Ler estado do player
            "user-modify-playback-state "   # Controlar player
            "user-read-recently-played "    # Ler músicas recentes
            "user-top-read "               # Ler top artistas/músicas
            "user-follow-read "            # Ler quem você segue
            "user-follow-modify"           # Seguir/deixar de seguir
        ).strip()
        
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'scope': scope,
            'show_dialog': 'true'  # Força mostrar diálogo de autorização
        }
        auth_url = f"{self.authorize_url}?{urllib.parse.urlencode(params)}"
        
        print(f"\nDebug info:")
        print(f"Client ID: {self.client_id}")
        print(f"Redirect URI: {self.redirect_uri}")
        print(f"Scopes: {scope}")
        print(f"Auth URL: {auth_url}")
        
        # Open browser for auth
        print("\n🌐 Abrindo navegador para autorização...")
        webbrowser.open(auth_url)
        
        # Wait for callback
        start_time = time.time()
        while not server.auth_code and time.time() - start_time < 300:  # 5 min timeout
            time.sleep(1)
        
        # Shutdown server
        try:
            server.shutdown()
            server.server_close()
        except Exception as e:
            print(f"\n⚠️ Erro ao fechar servidor: {str(e)}")
        
        if not server.auth_code:
            print("\n❌ Timeout na autorização")
            return None
            
        # Exchange code for tokens
        print("\n🔄 Obtendo tokens...")
        auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            'Authorization': f'Basic {auth}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'authorization_code',
            'code': server.auth_code,
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
            print(f"\nDebug token request:")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                
                # Save tokens to env
                env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
                with open(env_path, 'r') as f:
                    lines = f.readlines()
                
                # Remove old tokens
                lines = [l for l in lines if not l.startswith(('SPOTIFY_ACCESS_TOKEN=', 'SPOTIFY_REFRESH_TOKEN='))]
                
                # Add new tokens
                lines.append(f'SPOTIFY_ACCESS_TOKEN={data["access_token"]}\n')
                if 'refresh_token' in data:
                    lines.append(f'SPOTIFY_REFRESH_TOKEN={data["refresh_token"]}\n')
                
                with open(env_path, 'w') as f:
                    f.writelines(lines)
                
                print("\n✅ Autorização concluída!")
                return self.access_token
                
            print(f"\n❌ Erro ao trocar código por tokens: {response.status_code}")
            if response.text:
                print("Mensagem:", response.text)
            return None
            
        except Exception as e:
            print(f"\n❌ Erro ao trocar código por tokens: {str(e)}")
            return None

    def _get_access_token(self):
        """Get access token from Spotify API."""
        if not self.client_id or not self.client_secret:
            print("\n❌ SPOTIFY_CLIENT_ID e SPOTIFY_CLIENT_SECRET precisam estar definidos no .env")
            return None

        # Tentar usar token existente
        if self.access_token:
            # Testar se o token ainda é válido
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Accept': 'application/json'
            }
            response = requests.get('https://api.spotify.com/v1/me', headers=headers)
            if response.status_code == 200:
                return self.access_token

        # Token expirado ou não existe
        # Primeiro tenta refresh token
        refresh_token = os.getenv('SPOTIFY_REFRESH_TOKEN')
        if refresh_token:
            auth = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers = {
                'Authorization': f'Basic {auth}',
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access_token']
                os.environ['SPOTIFY_ACCESS_TOKEN'] = self.access_token
                if 'refresh_token' in data:  # Nem sempre retorna um novo refresh token
                    os.environ['SPOTIFY_REFRESH_TOKEN'] = data['refresh_token']
                return self.access_token

        # Se não tem refresh token ou falhou, inicia fluxo OAuth
        return self._get_user_auth()

    def _get_user_id(self):
        """Get user ID from Spotify API."""
        if not self.access_token:
            self._get_access_token()
            if not self.access_token:
                return None

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }

        response = requests.get('https://api.spotify.com/v1/me', headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('id')
            
        print(f"\nErro ao obter user ID: {response.status_code}")
        if response.text:
            print("Mensagem:", response.text)
        return None

    def get_user_info(self):
        """Get and display user profile."""
        if not self.access_token:
            self._get_access_token()
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
            self._get_access_token()
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
            self._get_access_token()
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
            self._get_access_token()
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
            self._get_access_token()
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
            self._get_access_token()
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
            self._get_access_token()
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

    def _get_client_token(self):
        """Get client token from Spotify's clienttoken API."""
        print("\n🔄 Obtendo client token...")
        
        try:
            # Headers exatos usados pelo Web Player
            data = {
                "client_data": {
                    "client_version": "1.2.53.4.ga8485c87",
                    "client_id": "d8a5ed958d274c2e8ee717e6a4b0971d",  # Web Player Client ID
                    "js_sdk_data": {
                        "device_brand": "unknown",
                        "device_model": "desktop",
                        "os": "Linux",
                        "os_version": "unknown",
                        "device_id": str(uuid.uuid4()),
                        "device_type": "computer"
                    }
                }
            }

            headers = {
                'accept': 'application/json',
                'accept-language': 'en',
                'app-platform': 'WebPlayer',
                'content-type': 'application/json',
                'origin': 'https://open.spotify.com',
                'referer': 'https://open.spotify.com/',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'spotify-app-version': '1.2.53.4.ga8485c87',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }

            response = requests.post(
                "https://clienttoken.spotify.com/v1/clienttoken",
                headers=headers,
                json=data
            )

            if response.status_code == 200:
                token_data = response.json()
                if 'granted_token' in token_data:
                    client_token = token_data['granted_token']
                    if isinstance(client_token, dict):
                        client_token = client_token.get('token', '')
                    print("✅ Client token obtido com sucesso!")
                    os.environ['SPOTIFY_CLIENT_TOKEN'] = client_token
                    return client_token
            
            print(f"\n❌ Erro ao obter client token: {response.status_code}")
            if response.text:
                print("Mensagem:", response.text)
            return None
            
        except Exception as e:
            print(f"\n❌ Erro ao obter client token: {str(e)}")
            return None

    def _get_web_access_token(self, username, password):
        """Get access token through Web Player login."""
        print("\n🔄 Fazendo login no Web Player...")
        
        try:
            session = requests.Session()
            
            # Primeiro request - Login com email/senha
            login_url = "https://accounts.spotify.com/login/password"
            
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'content-type': 'application/json',
                'origin': 'https://accounts.spotify.com',
                'referer': 'https://accounts.spotify.com/en/login',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'spotify-app-version': '1.2.53.4.ga8485c87',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }
            
            data = {
                'username': username,
                'password': password,
                'remember': True
            }
            
            response = session.post(login_url, headers=headers, json=data)
            
            if response.status_code != 200:
                print(f"\n❌ Erro no login: {response.status_code}")
                if response.text:
                    print("Mensagem:", response.text)
                return None
                
            # Segundo request - Obter token de acesso
            token_url = "https://open.spotify.com/get_access_token"
            
            headers = {
                'accept': 'application/json',
                'accept-language': 'en-US,en;q=0.9',
                'app-platform': 'WebPlayer',
                'origin': 'https://open.spotify.com',
                'referer': 'https://open.spotify.com/',
                'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Linux"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'spotify-app-version': '1.2.53.4.ga8485c87',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
            }
            
            params = {
                'reason': 'transport',
                'productType': 'web_player'
            }
            
            response = session.get(token_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                access_token = data.get('accessToken')
                if access_token:
                    print("✅ Token de acesso obtido com sucesso!")
                    return access_token
                    
            print(f"\n❌ Erro ao obter token de acesso: {response.status_code}")
            if response.text:
                print("Mensagem:", response.text)
            return None
            
        except Exception as e:
            print(f"\n❌ Erro no processo de login: {str(e)}")
            return None

    def set_display_name_web(self, new_name):
        """Change display name through Spotify's Web Player API."""
        # Pegar credenciais do .env
        username = os.getenv('SPOTIFY_USERNAME')
        password = os.getenv('SPOTIFY_PASSWORD')
        
        if not username or not password:
            print("\n❌ Credenciais não encontradas!")
            print("Por favor, adicione SPOTIFY_USERNAME e SPOTIFY_PASSWORD ao seu arquivo .env")
            return False
        
        # Fazer login e obter token de acesso do Web Player
        access_token = self._get_web_access_token(username, password)
        if not access_token:
            print("\n❌ Não foi possível fazer login no Web Player")
            return False
            
        # Obter client token
        if not self.client_token:
            print("\n🔄 Obtendo client token...")
            self.client_token = self._get_client_token()
            if not self.client_token:
                print("\n❌ Não foi possível obter o client token")
                return False
            os.environ['SPOTIFY_CLIENT_TOKEN'] = self.client_token

        # Get user ID
        user_id = self._get_user_id()
        if not user_id:
            print("\n❌ Não foi possível obter seu ID do Spotify")
            return False

        session = requests.Session()
        
        print("\n🔄 Iniciando processo de alteração de nome...")
        
        # Headers exatos do Web Player
        headers = {
            'accept': 'application/json',
            'accept-language': 'en',
            'app-platform': 'WebPlayer',
            'authorization': f'Bearer {access_token}',  # Usando token do Web Player
            'client-token': self.client_token,
            'content-type': 'application/json',
            'origin': 'https://open.spotify.com',
            'referer': 'https://open.spotify.com/',
            'sec-ch-ua': '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'spotify-app-version': '1.2.53.4.ga8485c87',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        }

        # Endpoint do Web Player para alterar nome
        profile_url = f"https://spclient.wg.spotify.com/identity/v3/profile/{user_id}"
        
        # Dados no formato do Web Player
        update_data = {
            "displayName": new_name
        }
        
        print(f"\nDebug info:")
        print(f"User ID: {user_id}")
        print(f"Client Token: {self.client_token[:30]}...")
        print(f"URL: {profile_url}")
        print(f"Data: {json.dumps(update_data)}")
        
        # Tentar atualizar o perfil
        response = session.put(profile_url, headers=headers, json=update_data)
        
        if response.status_code in [200, 204]:
            print(f"\n✅ Nome alterado com sucesso para: {new_name}")
            time.sleep(2)  # Esperar propagação
            self.get_user_info()  # Mostrar perfil atualizado
            return True
            
        print(f"\n❌ Erro ao alterar nome: {response.status_code}")
        if response.text:
            print("Mensagem:", response.text)
            
        if response.status_code == 403:
            print("\nDica: O erro 403 pode indicar que o client token está inválido.")
            print("Tente limpar o SPOTIFY_CLIENT_TOKEN do seu .env e tentar novamente.")
            print("Ou pode ser necessário reautorizar. Tente limpar SPOTIFY_ACCESS_TOKEN e SPOTIFY_REFRESH_TOKEN também.")
        
        print("\nSe a alteração automática falhar, você pode alterar manualmente em:")
        print("https://open.spotify.com/")
        return False

    def test(self):
        """Run basic plugin test."""
        print("Testing Spotify plugin...")
        self.get_user_info()
        return True

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        # Sempre verificar/renovar token antes de executar comandos
        if not self._is_token_valid():
            if not self._get_access_token():
                print("\n❌ Não foi possível obter autorização")
                return
            
        if command == "set-name":
            if not args:
                print("Usage: set-name [new_name]")
                return
            new_name = " ".join(args)  # Permite nomes com espaços
            self.set_display_name_web(new_name)
        elif command == "me":
            self.get_user_info()
        elif command == "test":
            self.test()
        elif command == "playlists":
            self.get_playlists()
        elif command == "playlist":
            if not args:
                print("Usage: playlist [playlist_id]")
                return
            self.get_playlist(args[0])
        elif command == "search":
            if len(args) < 2:
                print("Usage: search [type] [query] (types: track, artist, album)")
                return
            self.search(args[0], " ".join(args[1:]))
        elif command == "top":
            if not args:
                print("Usage: top [type] (types: tracks, artists)")
                return
            self.get_top_items(args[0])
        elif command == "recent":
            self.get_recent_tracks()
        elif command == "create-playlist":
            if not args:
                print("Usage: create-playlist [name] [description]")
                return
            name = args[0]
            description = " ".join(args[1:]) if len(args) > 1 else None
            self.create_playlist(name, description)
        elif command == "edit-playlist":
            if len(args) < 3:
                print("Usage: edit-playlist [playlist_id] [name] [description]")
                return
            self.edit_playlist(args[0], args[1], " ".join(args[2:]))
        elif command == "add-to-playlist":
            if len(args) < 2:
                print("Usage: add-to-playlist [playlist_id] [track_id1] [track_id2] ...")
                return
            self.add_tracks_to_playlist(args[0], args[1:])
        elif command == "following":
            self.get_following()
        elif command == "recommendations":
            self.get_recommendations(*args)
        elif command == "charts":
            country = args[0] if args else "global"
            limit = int(args[1]) if len(args) > 1 else 50
            self.get_charts(country, limit)
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

    def list_commands(self):
        """List all available commands."""
        print("\nAvailable commands:")
        for cmd, desc in self._commands.items():
            print(f"  {cmd}: {desc}")

def plugin():
    """Create plugin instance."""
    return Plugin()
