# Fetcher

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/carloskvasir/fetcher/releases/tag/v1.0.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A flexible Python-based tool for fetching information from multiple services (Trello, GitHub, Spotify) through a plugin architecture.

## Features

- Plugin-based architecture
- Environment variable configuration
- Multiple service support:
  - Trello (boards, lists, cards)
  - GitHub (repositories, users, search)
  - Spotify (user profile, playlists, tracks, artists, albums)
- Simple command-line interface
- Standardized plugin interface

## Installation

1. Clone the repository:
```bash
git clone https://github.com/carloskvasir/fetcher.git
cd fetcher
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your environment:
```bash
cp .env.example .env
# Edit .env with your credentials
```

## Configuration

Copy `.env.example` to `.env` and fill in your credentials:

```env
# Trello API Credentials
TRELLO_API_KEY=your_trello_api_key
TRELLO_TOKEN=your_trello_token
TRELLO_BASE_URL=https://api.trello.com/1

# GitHub API Credentials
GITHUB_TOKEN=your_github_token

# Spotify API Credentials
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_ACCESS_TOKEN=
SPOTIFY_TOKEN_EXPIRY=
SPOTIFY_PORT=3003
```

### Getting Credentials

#### Trello
1. Go to https://trello.com/power-ups/admin/
2. Create a new Power-Up
3. Generate API Key and Token

#### GitHub
1. Go to https://github.com/settings/tokens
2. Generate a new token with the following scopes:
   - `repo` - Full control of private repositories
   - `user` - Update all user data
   - `read:user` - Read all user profile data
   - `user:email` - Access user email addresses
3. Copy the token to your `.env` file

#### Spotify
1. Go to https://developer.spotify.com/dashboard
2. Create a new application
3. Get your Client ID and Client Secret
4. Add http://127.0.0.1:3003/callback as the redirect URI
5. Copy the Client ID and Client Secret to your `.env` file
6. Run `spotify test` to authenticate - it will open your browser automatically

## Usage

### Basic Usage

List available plugins:
```bash
python fetcher.py
```

List available commands for a plugin:
```bash
python fetcher.py github
python fetcher.py trello
python fetcher.py spotify
```

### GitHub Plugin

```bash
# Test connection and show user information
python fetcher.py github test

# Show authenticated user information
python fetcher.py github me

# List repositories for a user
python fetcher.py github list carloskvasir

# Search repositories
python fetcher.py github search "python cli"
```

### Spotify Plugin

```bash
# Test Spotify connection and authentication
python fetcher.py spotify test

# Show your profile
python fetcher.py spotify me

# Search for tracks, artists, or albums
python fetcher.py spotify search track "The Beatles Here Comes The Sun"

# Show your playlists
python fetcher.py spotify playlists

# Show specific playlist details
python fetcher.py spotify playlist [playlist_id]

# Create a new playlist
python fetcher.py spotify create-playlist "My Awesome Playlist" "Description"

# Edit a playlist
python fetcher.py spotify edit-playlist [playlist_id] "New Name" "New Description"

# Add tracks to a playlist
python fetcher.py spotify add-to-playlist [playlist_id] [track_id]

# View your top tracks and artists
python fetcher.py spotify top tracks
python fetcher.py spotify top artists

# Show your recently played tracks
python fetcher.py spotify recent

# Get personalized recommendations
python fetcher.py spotify recommendations

# Show top charts for Brazil (or other countries)
python fetcher.py spotify charts brazil        # shows top 10 by default
python fetcher.py spotify charts brazil 50     # shows all 50 tracks
```

#### Demo Playlists
Check out our demo playlists created with the Fetcher CLI:
 [My Awesome Playlist](https://open.spotify.com/playlist/2hxqaM0xlfhn0VvrEAKy4c)

### Trello Plugin

```bash
# Test connection and show user information
python fetcher.py trello test

# List all boards
python fetcher.py trello boards

# Get board information
python fetcher.py trello board BOARD_ID

# Get card information
python fetcher.py trello card CARD_ID

# Get list information
python fetcher.py trello list LIST_ID
```

## Creating New Plugins

To create a new plugin:

1. Create a new file in the `plugins` directory with the name `your_plugin.py`
2. Implement the `PluginInterface` class with the required methods:
   - `test()`: Run basic plugin tests
   - `list_commands()`: List available commands
   - `run(command, *args, **kwargs)`: Execute a specific command
3. Create a `plugin()` function that returns an instance of your plugin class

Example:
```python
from .plugin_interface import PluginInterface

class Plugin(PluginInterface):
    def __init__(self):
        self._commands = {
            "test": "Run basic plugin tests",
            "command1": "Description of command1",
            "command2": "Description of command2"
        }

    def test(self):
        """Run basic plugin tests."""
        print("Testing plugin...")

    def list_commands(self):
        """List all available plugin commands."""
        print("\nAvailable commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        if command == "test":
            self.test()
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

def plugin():
    """Create and return a new plugin instance."""
    return Plugin()
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a new Pull Request

## Author

👤 **Carlos "kvasir" Lima**

* GitHub: [@carloskvasir](https://github.com/carloskvasir)
* LinkedIn: [@carloskvasir](https://linkedin.com/in/carloskvasir)

## Show your support

Give a ⭐️ if this project helped you!

## License

This project is licensed under the MPL-2.0 License - see the [LICENSE](LICENSE) file for details.
