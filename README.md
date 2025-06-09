# Fetcher

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/carloskvasir/fetcher/releases/tag/v1.0.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A flexible Python-based tool for fetching information from multiple services through a powerful plugin architecture. **Now with MCP (Model Context Protocol) support for seamless AI assistant integration!**

## 🚀 Key Features

- **🔌 Plugin Architecture** - Modular design for easy extension
- **🤖 MCP Integration** - Work with Claude, ChatGPT, and other AI assistants
- **🌐 Multi-Service Support** - GitHub, Spotify, Trello, LinkedIn all in one tool
- **⚡ Fast & Reliable** - Async operations with robust error handling
- **🔐 Secure** - Local credential storage, read-only by default
- **📚 Well Documented** - Comprehensive guides and examples

## 🎯 What Can You Do?

### 🐙 GitHub Integration
- **Research Projects**: Search repositories, analyze code trends, discover frameworks
- **Profile Management**: View user stats, repository insights, contribution patterns
- **Development Workflow**: Quick repo access, contributor analysis, project discovery
- **Automation**: Fetch custom data via API endpoints, batch operations

### 🎵 Spotify Integration  
- **Music Discovery**: Get AI-powered recommendations, explore global charts
- **Playlist Management**: Create themed playlists, organize collections
- **Listening Analytics**: Track your music habits, analyze preferences
- **Social Music**: Share discoveries, build collaborative playlists

### 📋 Trello Integration
- **Project Management**: Visual board overview, task tracking, progress monitoring
- **Team Collaboration**: Comment on tasks, move cards, update statuses
- **Productivity**: Quick board access, card management, workflow automation
- **Organization**: List management, board analytics, project structuring

### 💼 LinkedIn Integration
- **Professional Networking**: Manage connections, view network insights
- **Content Creation**: Share updates, engage with professional content
- **Career Development**: Track professional activities, showcase achievements
- **Brand Building**: Consistent professional presence, thought leadership

## Quick Start

### Option 1: Automated Setup (Recommended)

```bash
git clone https://github.com/carloskvasir/fetcher.git
cd fetcher
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Setup

1. Clone the repository:
```bash
git clone https://github.com/carloskvasir/fetcher.git
cd fetcher
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure your environment:
```bash
cp .env.example .env
# Edit .env with your credentials
nano .env
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

## 🤖 MCP (Model Context Protocol) - AI Assistant Integration

### What is MCP?
MCP enables AI assistants like Claude to directly interact with your services. Instead of copying/pasting data, AI can fetch real-time information and perform actions on your behalf.

### 🚀 Quick Start with MCP

```bash
# 1. Start the MCP server
python3 mcp_server.py

# 2. Test the integration
python3 test_mcp.py

# 3. Configure with Claude Desktop (see claude_desktop_config.json)
```

### 🎯 AI Assistant Examples

**GitHub Research:**
> *"Show me my GitHub profile and find Python CLI projects similar to mine"*
- Uses: `github_me`, `github_search`
- Result: Profile overview + relevant project suggestions

**Music Curation:**  
> *"Create a focus playlist based on my top tracks and current Brazil charts"*
- Uses: `spotify_top`, `spotify_charts`, `spotify_create_playlist`
- Result: Personalized playlist with trending elements

**Project Management:**
> *"What's the status of my Trello projects and any GitHub repos that need attention?"*
- Uses: `trello_boards`, `github_me`, `github_list`
- Result: Complete project overview across platforms

**Professional Networking:**
> *"Help me write a LinkedIn post about my recent GitHub contributions"*
- Uses: `github_me`, `linkedin_me`, `linkedin_share`
- Result: Crafted post with real data about your work

### 🛠️ Available MCP Tools

Each plugin exposes its commands as MCP tools using the `{plugin_name}_{command}` format:

| Plugin | MCP Tools | CLI Commands | Primary Use Cases |
|--------|-----------|--------------|-------------------|
| **GitHub** | `github_test`, `github_me`, `github_list`, `github_search`, `github_fetch` | `test`, `me`, `list`, `search`, `fetch` | Code research, developer analysis, repository discovery |
| **Spotify** | `spotify_test`, `spotify_me`, `spotify_search`, `spotify_top`, `spotify_recent`, `spotify_playlists`, `spotify_playlist`, `spotify_create_playlist`, `spotify_charts`, `spotify_recommendations` | `test`, `me`, `search`, `top`, `recent`, `playlists`, `playlist`, `create-playlist`, `charts`, `recommendations` | Music curation, discovery, analytics |
| **Trello** | `trello_test`, `trello_boards`, `trello_board`, `trello_card`, `trello_list`, `trello_add_comment`, `trello_move_card` | `test`, `boards`, `board`, `card`, `list`, `add_comment`, `move_card` | Project tracking, task management, workflow optimization |
| **LinkedIn** | `linkedin_test`, `linkedin_me`, `linkedin_posts`, `linkedin_share`, `linkedin_connections` | `test`, `me`, `posts`, `share`, `connections` | Professional networking, content strategy, career development |

### 🎯 Advanced AI Assistant Prompts

**Cross-Platform Research:**
> *"Help me research Python CLI tools on GitHub, then create a development playlist on Spotify, and track my findings in Trello"*

**Professional Content Creation:**
> *"Analyze my recent GitHub contributions and help me write a technical LinkedIn post about my projects"*

**Project Management Intelligence:**
> *"Review my Trello boards, check related GitHub repositories, and suggest workflow improvements"*

**Music-Driven Productivity:**
> *"Based on my top Spotify tracks, create focus playlists for different types of coding work and organize them by project"*

### 🔗 Integration Setup

**Claude Desktop Configuration:**
```json
{
  "mcpServers": {
    "fetcher": {
      "command": "python3",
      "args": ["/absolute/path/to/fetcher/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/fetcher"
      }
    }
  }
}
```

**Custom Integration Examples:**
- **OpenAI GPT Integration**: Use MCP client to connect with OpenAI's function calling
- **Anthropic Claude**: Direct MCP server integration via Claude Desktop
- **Local LLM Integration**: Connect via MCP protocol for privacy-focused AI assistance
- **VS Code Extension**: Build custom extensions using the MCP tools

**Advanced Setup Options:**
```json
{
  "mcpServers": {
    "fetcher-dev": {
      "command": "python3",
      "args": ["/path/to/fetcher/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/fetcher",
        "MCP_LOG_LEVEL": "DEBUG",
        "FETCHER_MODE": "development"
      }
    }
  }
}
```

### 🤖 AI Assistant Prompt Engineering Guide

#### 🎯 Effective Prompting Strategies

**1. Context-Rich Requests:**
Instead of: *"Show me my GitHub"*
Use: *"Analyze my GitHub profile, recent contributions, and top repositories to help me understand my coding patterns and suggest areas for improvement"*

**2. Multi-Platform Intelligence:**
*"Review my Trello project boards, check related GitHub repositories, analyze my current Spotify listening patterns, and suggest a productivity workflow that aligns my coding focus with appropriate background music"*

**3. Goal-Oriented Workflows:**
*"I want to build my professional brand as a Python developer. Help me: 1) Analyze my GitHub contributions, 2) Create LinkedIn content showcasing my work, 3) Organize my projects in Trello, and 4) Set up focused work playlists on Spotify"*

#### 🚀 Advanced Use Case Templates

**Research & Development:**
```
"I'm researching [TECHNOLOGY/TOPIC]. Please:
1. Search GitHub for related projects and trending repositories
2. Identify key contributors and active maintainers  
3. Create a Trello card with findings and insights
4. Suggest LinkedIn post angles to share my research
5. Recommend focus music for deep technical reading"
```

**Content Creation:**
```
"Help me create engaging technical content:
1. Analyze my recent GitHub commits and project updates
2. Identify interesting technical challenges I've solved
3. Draft LinkedIn posts with relevant hashtags and developer community appeal
4. Suggest follow-up engagement strategies
5. Create themed playlists for content creation sessions"
```

**Project Management:**
```
"Optimize my development workflow:
1. Review my Trello boards and identify bottlenecks
2. Correlate GitHub commit patterns with task completion
3. Analyze my music listening during productive coding sessions
4. Suggest improvements to my project organization
5. Create templates for future project planning"
```

**Professional Networking:**
```
"Expand my professional network strategically:
1. Analyze my GitHub projects to identify my technical expertise
2. Review my LinkedIn connections and posting patterns
3. Find GitHub projects and developers aligned with my interests
4. Suggest networking opportunities and collaboration ideas
5. Draft introduction messages for potential connections"
```

#### 💡 Power User Tips

**Chaining Commands:**
*"First show my GitHub profile, then search for Python CLI projects similar to mine, create a research playlist on Spotify, and document promising projects in my Trello research board"*

**Comparative Analysis:**
*"Compare my GitHub activity with my Trello task completion rates, identify patterns in my productivity cycles, and suggest optimal work schedules with matching music preferences"*

**Trend Analysis:**
*"Analyze GitHub trends in my technology stack, compare with my Spotify music trends, and help me create content that connects technical and personal interests for authentic LinkedIn posts"*

**Automated Reporting:**
*"Create a weekly summary combining: GitHub contribution stats, Trello project progress, top Spotify tracks, and LinkedIn engagement metrics. Suggest improvements for next week"*

## 🛠️ Plugin Command Reference

### 🐙 GitHub Plugin Commands

| Command | Description | Example | Use Case | MCP Tool |
|---------|-------------|---------|----------|----------|
| `test` | Test connection & auth | `python3 fetcher.py github test` | Verify setup | `github_test` |
| `me` | Show your profile | `python3 fetcher.py github me` | Profile overview, stats analysis | `github_me` |
| `list` | List user repositories | `python3 fetcher.py github list carloskvasir` | Developer research, repo discovery | `github_list` |
| `search` | Search repositories | `python3 fetcher.py github search "python cli"` | Technology research, trend analysis | `github_search` |
| `fetch` | Custom API endpoint | `python3 fetcher.py github fetch "user/repos"` | Advanced queries, custom data | `github_fetch` |

**Real-World Usage Examples:**
```bash
# Research trending Python projects
python3 fetcher.py github search "python machine learning stars:>1000"

# Analyze a specific developer's work
python3 fetcher.py github list tensorflow

# Check community activity
python3 fetcher.py github search "react hooks updated:>2024-01-01"

# Custom API queries
python3 fetcher.py github fetch "search/repositories?q=language:python+topic:cli"
```

**AI Assistant Prompts:**
- *"Show me my GitHub profile and analyze my most active repositories"*
- *"Search for trending Python machine learning projects with high activity"*
- *"Find repositories related to web development frameworks updated this year"*
- *"Research developers working on similar projects to mine"*
- *"Help me discover new CLI tools written in Python"*

### 🎵 Spotify Plugin Commands

| Command | Description | Example | Use Case | MCP Tool |
|---------|-------------|---------|----------|----------|
| `test` | Test connection & auth | `python3 fetcher.py spotify test` | Verify setup, refresh tokens | `spotify_test` |
| `me` | Show your profile | `python3 fetcher.py spotify me` | Profile analytics, listening stats | `spotify_me` |
| `search` | Search music | `python3 fetcher.py spotify search track "Bohemian Rhapsody"` | Music discovery, research | `spotify_search` |
| `top` | Your top music | `python3 fetcher.py spotify top tracks` | Personal analytics, preferences | `spotify_top` |
| `recent` | Recently played | `python3 fetcher.py spotify recent` | Listen history, pattern analysis | `spotify_recent` |
| `playlists` | List playlists | `python3 fetcher.py spotify playlists` | Collection overview, organization | `spotify_playlists` |
| `playlist` | Playlist details | `python3 fetcher.py spotify playlist [id]` | Deep dive, track analysis | `spotify_playlist` |
| `create-playlist` | Create playlist | `python3 fetcher.py spotify create-playlist "My Mix" "Cool songs"` | Curation, organization | `spotify_create_playlist` |
| `charts` | Country charts | `python3 fetcher.py spotify charts brazil 20` | Trend discovery, market research | `spotify_charts` |
| `recommendations` | Get suggestions | `python3 fetcher.py spotify recommendations` | Personalized discovery | `spotify_recommendations` |

**Real-World Usage Examples:**
```bash
# Music analytics workflow
python3 fetcher.py spotify me
python3 fetcher.py spotify top artists
python3 fetcher.py spotify recent

# Discovery and curation
python3 fetcher.py spotify recommendations
python3 fetcher.py spotify charts brazil 50
python3 fetcher.py spotify create-playlist "Workout Mix" "High-energy tracks for fitness"

# Research trending music
python3 fetcher.py spotify search artist "Taylor Swift"
python3 fetcher.py spotify charts global 100

# Playlist management
python3 fetcher.py spotify playlists
python3 fetcher.py spotify playlist 37i9dQZF1DXcBWIGoYBM5M
```

**AI Assistant Prompts:**
- *"Create a focus playlist combining my top tracks with current trending music"*
- *"Analyze my music taste and suggest new artists I might like"*
- *"What are the current music trends in different countries?"*
- *"Help me organize my playlists by genre and mood"*
- *"Find songs similar to my recently played tracks and create a discovery playlist"*
- *"Compare my music taste with global charts and suggest popular tracks I haven't heard"*

### 📋 Trello Plugin Commands

| Command | Description | Example | Use Case | MCP Tool |
|---------|-------------|---------|----------|----------|
| `test` | Test connection & auth | `python3 fetcher.py trello test` | Verify setup, API connectivity | `trello_test` |
| `boards` | List all boards | `python3 fetcher.py trello boards` | Project overview, organization | `trello_boards` |
| `board` | Board details | `python3 fetcher.py trello board [board_id]` | Project deep dive, status check | `trello_board` |
| `card` | Card details | `python3 fetcher.py trello card [card_id]` | Task analysis, progress tracking | `trello_card` |
| `list` | List details | `python3 fetcher.py trello list [list_id]` | Column analysis, workflow insights | `trello_list` |
| `add_comment` | Add card comment | `python3 fetcher.py trello add_comment [card_id] "comment"` | Collaboration, updates | `trello_add_comment` |
| `move_card` | Move card | `python3 fetcher.py trello move_card [card_id] [list_id]` | Workflow management, progress | `trello_move_card` |

**Real-World Usage Examples:**
```bash
# Project status overview
python3 fetcher.py trello boards
python3 fetcher.py trello board 5f8b1234567890abcdef1234

# Task management workflow
python3 fetcher.py trello card 5f8b1234567890abcdef5678
python3 fetcher.py trello add_comment 5f8b1234567890abcdef5678 "Completed initial research phase"
python3 fetcher.py trello move_card 5f8b1234567890abcdef5678 5f8b1234567890abcdef9012

# Board analytics
python3 fetcher.py trello list 5f8b1234567890abcdef3456  # "In Progress" column
python3 fetcher.py trello list 5f8b1234567890abcdef7890  # "Done" column

# Project coordination
python3 fetcher.py trello boards | grep -i "development"
python3 fetcher.py trello board [dev_board_id]
```

**AI Assistant Prompts:**
- *"Show me the status of all my active projects across Trello boards"*
- *"What tasks are currently in progress and which ones need attention?"*
- *"Help me organize my project workflow and suggest improvements"*
- *"Analyze my completed tasks this week and provide a summary"*
- *"Move overdue tasks to the appropriate columns and add status updates"*
- *"Create a productivity report based on my Trello activity"*

### 💼 LinkedIn Plugin Commands

| Command | Description | Example | Use Case | MCP Tool |
|---------|-------------|---------|----------|----------|
| `test` | Test connection & auth | `python3 fetcher.py linkedin test` | Verify setup, token validation | `linkedin_test` |
| `me` | Show your profile | `python3 fetcher.py linkedin me` | Professional profile analysis | `linkedin_me` |
| `posts` | Recent posts | `python3 fetcher.py linkedin posts` | Content performance, engagement | `linkedin_posts` |
| `share` | Share post | `python3 fetcher.py linkedin share "Hello LinkedIn!"` | Content creation, announcements | `linkedin_share` |
| `connections` | List connections | `python3 fetcher.py linkedin connections` | Network analysis, relationship mapping | `linkedin_connections` |

**Real-World Usage Examples:**
```bash
# Professional presence audit
python3 fetcher.py linkedin me
python3 fetcher.py linkedin posts
python3 fetcher.py linkedin connections

# Content strategy
python3 fetcher.py linkedin share "Excited to share my latest Python project on GitHub! 🚀"
python3 fetcher.py linkedin share "Just published a technical blog post about MCP integration"

# Network analysis
python3 fetcher.py linkedin connections | grep -i "developer"
python3 fetcher.py linkedin posts | head -20  # Recent activity overview

# Professional updates
python3 fetcher.py linkedin share "Attending PyCon 2025! Looking forward to connecting with fellow Python developers"
```

**AI Assistant Prompts:**
- *"Analyze my LinkedIn profile and suggest improvements for better professional visibility"*
- *"Help me craft a technical post about my recent GitHub projects with appropriate hashtags"*
- *"Review my recent LinkedIn activity and suggest content strategy improvements"*
- *"Create a professional update about my latest coding achievements"*
- *"Analyze my LinkedIn network and identify key professional connections"*
- *"Help me write engaging posts about my technical projects and learning journey"*

## 🚀 Real-World Use Cases & Workflows

### 🎯 Music Discovery & Curation Workflow
```bash
# 1. Analyze your musical preferences
python3 fetcher.py spotify me
python3 fetcher.py spotify top tracks
python3 fetcher.py spotify top artists

# 2. Get personalized recommendations
python3 fetcher.py spotify recommendations

# 3. Explore global and local trends
python3 fetcher.py spotify charts global 50
python3 fetcher.py spotify charts brazil 50

# 4. Create themed playlists
python3 fetcher.py spotify create-playlist "Focus Code" "Programming background music"
python3 fetcher.py spotify create-playlist "Discovery Weekly Custom" "AI-curated music discovery"
```

**AI Prompts**: 
- *"Help me discover new music based on my listening history and create genre-specific playlists"*
- *"Analyze music trends across different countries and suggest culturally diverse tracks"*
- *"Create a work productivity playlist combining my favorite tracks with focus-enhancing music"*

### 🔍 Comprehensive Project Research Workflow
```bash
# 1. Search for relevant projects and technologies
python3 fetcher.py github search "machine learning python stars:>1000"
python3 fetcher.py github search "cli tools rust trending"

# 2. Analyze specific developers and organizations  
python3 fetcher.py github list tensorflow
python3 fetcher.py github list microsoft

# 3. Check your own contributions and stats
python3 fetcher.py github me
python3 fetcher.py github list [your_username]

# 4. Document findings in Trello
python3 fetcher.py trello boards
python3 fetcher.py trello add_comment [research_card_id] "Found interesting ML projects: [project_links]"
python3 fetcher.py trello move_card [research_card_id] [completed_list_id]
```

**AI Prompts**: 
- *"Research trending Python machine learning libraries, analyze their GitHub activity, and organize findings in my Trello research board"*
- *"Find innovative CLI tools, study their implementation patterns, and create a comparison document"*
- *"Discover new frameworks in my field and track them in my technology research project"*

### 📈 Professional Brand Building Workflow  
```bash
# 1. Audit your current professional presence
python3 fetcher.py linkedin me
python3 fetcher.py linkedin posts
python3 fetcher.py linkedin connections

# 2. Review your technical contributions
python3 fetcher.py github me
python3 fetcher.py github list [your_username]

# 3. Create content connecting your work
python3 fetcher.py linkedin share "Just published a new Python tool on GitHub! 🚀 It helps developers integrate multiple APIs seamlessly. Check it out: [github_link] #Python #OpenSource #Development"

# 4. Track engagement and follow-up
python3 fetcher.py linkedin posts | head -10  # Check recent post performance
```

**AI Prompts**: 
- *"Analyze my GitHub contributions from the past month and help me craft compelling LinkedIn posts about my technical achievements"*
- *"Review my LinkedIn profile against my GitHub activity and suggest ways to better showcase my technical skills"*
- *"Create a content calendar linking my GitHub projects to professional LinkedIn updates"*

### 🎨 Creative Project Management & Productivity
```bash
# 1. Set up and review project boards
python3 fetcher.py trello boards
python3 fetcher.py trello board [creative_project_board_id]

# 2. Track development progress across platforms
python3 fetcher.py trello card [current_task_id]
python3 fetcher.py github list [project_repo_owner]

# 3. Create themed work environment
python3 fetcher.py spotify create-playlist "Deep Work" "Instrumental focus music for coding sessions"
python3 fetcher.py spotify create-playlist "Creative Flow" "Inspiring tracks for design and ideation"

# 4. Document milestones and share progress
python3 fetcher.py trello add_comment [milestone_card_id] "Completed MVP - repository: [github_link]"
python3 fetcher.py linkedin share "Exciting milestone reached on my latest project! 🎉 [project_description] #TechInnovation"
```

**AI Prompts**: 
- *"Help me organize my creative projects across Trello and GitHub, then create appropriate focus playlists for different work phases"*
- *"Analyze my project completion patterns in Trello and suggest workflow optimizations"*
- *"Create a productivity system that integrates my GitHub commits, Trello tasks, and focus music preferences"*

### 🌐 Cross-Platform Intelligence & Automation
```bash
# 1. Comprehensive status check
python3 fetcher.py github me | grep -i "contributions"
python3 fetcher.py trello boards | wc -l  # Count active projects  
python3 fetcher.py spotify recent | head -5  # Latest listening activity
python3 fetcher.py linkedin posts | head -3  # Recent professional activity

# 2. Intelligent content creation
python3 fetcher.py github search "$(python3 fetcher.py spotify top artists | head -1 | cut -d' ' -f1) music visualization"
python3 fetcher.py trello add_comment [inspiration_card_id] "Found music-tech crossover projects for reference"

# 3. Professional network expansion  
python3 fetcher.py github search "contributors:>10 language:python" | head -20
python3 fetcher.py linkedin connections | grep -i "python\|developer"
```

**AI Prompts**:
- *"Analyze my activity across all platforms and create a weekly productivity report with insights and recommendations"*
- *"Find connections between my GitHub interests, Spotify preferences, and LinkedIn network to suggest new professional opportunities"*
- *"Help me build a personal brand strategy that leverages my technical skills, music taste, and professional network"*

# 3. Analyze your network and expand strategically
python3 fetcher.py linkedin connections

# 4. Share your technical achievements  
python3 fetcher.py linkedin share "Just published a new Python tool on GitHub! 🚀 It integrates multiple APIs through MCP protocol. Check it out: [link] #Python #OpenSource #AI"
```

**AI Prompts**: 
- *"Help me craft compelling LinkedIn posts about my recent coding projects and technical achievements"*
- *"Analyze my professional network and suggest strategies for meaningful connections in tech"*
- *"Create a content strategy that showcases my GitHub work through LinkedIn posts"*

## 🧩 Advanced Plugin Integration Patterns

### 🔄 Cross-Platform Data Flow
```bash
# Research → Document → Share workflow
github_search="$(python3 fetcher.py github search 'python ai tools' | head -10)"
python3 fetcher.py trello add_comment [research_card] "$github_search"
python3 fetcher.py linkedin share "Exploring innovative Python AI tools: [insights]"
```

### 🎵 Context-Aware Music Selection
```bash
# Project-based playlist creation
project_type="web development"
python3 fetcher.py spotify search playlist "$project_type focus"
python3 fetcher.py spotify create-playlist "Dev Focus - $project_type" "Curated for coding sessions"
```

### 📊 Productivity Analytics  
```bash
# Weekly activity summary
echo "=== Weekly Productivity Summary ==="
echo "GitHub Activity:"
python3 fetcher.py github me | grep -E "(contributions|repositories)"
echo "Trello Progress:"  
python3 fetcher.py trello boards | wc -l
echo "Music Stats:"
python3 fetcher.py spotify recent | head -5
echo "Professional Engagement:"
python3 fetcher.py linkedin posts | head -3
```

## Creating New Plugins

To create a new plugin:

1. Create a new file in the `plugins` directory with the name `your_service_plugin.py`
2. Implement the `PluginInterface` class with the required methods:
   - `test()`: Run basic plugin tests
   - `list_commands()`: List available commands
   - `run(command, *args, **kwargs)`: Execute a specific command
3. Add a `_commands` dictionary with command descriptions
4. Ensure your plugin works with both CLI and MCP interfaces

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

Your plugin will automatically be available via:
- CLI: `python3 fetcher.py your_service command`  
- MCP: `your_service_command` tool

## Troubleshooting

### Common Issues

**MCP Server Not Starting:**
```bash
# Check Python version (3.7+ required)
python3 --version

# Check dependencies
pip3 install -r requirements.txt

# Test plugin loading
python3 -c "from plugins.plugin_manager import PluginManager; m = PluginManager(); m.load_plugins(); print('Loaded plugins:', list(m.plugins.keys()))"

# Debug MCP server
MCP_LOG_LEVEL=DEBUG python3 mcp_server.py
```

**Authentication Errors:**
```bash
# Verify credentials are set
grep -E "(GITHUB_TOKEN|SPOTIFY_CLIENT_ID|TRELLO_API_KEY)" .env

# Test individual plugins
python3 fetcher.py github test
python3 fetcher.py spotify test  
python3 fetcher.py trello test
python3 fetcher.py linkedin test

# Check token expiration (Spotify)
python3 -c "
import os
from datetime import datetime
expiry = os.getenv('SPOTIFY_TOKEN_EXPIRY', '0')
if int(expiry) < datetime.now().timestamp():
    print('Spotify token expired - run: python3 fetcher.py spotify test')
else:
    print('Spotify token valid')
"
```

**Plugin Not Found:**
```bash
# Check plugin file structure
ls -la plugins/*_plugin.py

# Verify plugin implements interface
python3 -c "
from plugins.github_plugin import plugin
p = plugin()
print('Commands:', list(p._commands.keys()))
"

# Test plugin loading individually
python3 -c "
from plugins.plugin_manager import PluginManager
pm = PluginManager()
pm.load_plugins()
for name, plugin in pm.plugins.items():
    print(f'{name}: {plugin.__class__.__name__}')
"
```

**MCP Tools Not Working:**
```bash
# Test MCP functionality comprehensively  
python3 test_mcp.py

# Check server logs with detailed output
MCP_LOG_LEVEL=DEBUG python3 mcp_server.py 2>&1 | tee mcp_debug.log

# Test specific MCP tools
python3 mcp_client.py list_tools
python3 mcp_client.py call_tool github_test '{}'

# Validate JSON-RPC communication
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python3 mcp_server.py
```

**Service-Specific Issues:**

**GitHub API Rate Limiting:**
```bash
# Check rate limit status
python3 fetcher.py github fetch "rate_limit"

# Use authenticated requests (add to .env)
GITHUB_TOKEN=your_personal_access_token_here
```

**Spotify Authentication Flow:**
```bash
# Clear expired tokens
sed -i '/SPOTIFY_ACCESS_TOKEN=/c\SPOTIFY_ACCESS_TOKEN=' .env
sed -i '/SPOTIFY_TOKEN_EXPIRY=/c\SPOTIFY_TOKEN_EXPIRY=' .env

# Re-authenticate
python3 fetcher.py spotify test
```

**Trello Board Access:**
```bash
# Verify board permissions
python3 fetcher.py trello boards | grep -i "permission\|access"

# Test with different board IDs
python3 fetcher.py trello board [public_board_id]
```

**LinkedIn Connection Issues:**
```bash
# Check LinkedIn API status
python3 fetcher.py linkedin test

# Verify profile access permissions
python3 fetcher.py linkedin me | grep -i "error\|permission"
```

### Performance Optimization

**Plugin Loading:**
```bash
# Profile plugin load times
python3 -c "
import time
from plugins.plugin_manager import PluginManager

start = time.time()
pm = PluginManager()
pm.load_plugins()
print(f'Loaded {len(pm.plugins)} plugins in {time.time() - start:.2f}s')
"
```

**Memory Usage:**
```bash
# Monitor memory during MCP operations
python3 -c "
import psutil, os
import subprocess

proc = subprocess.Popen(['python3', 'mcp_server.py'], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE)
                       
p = psutil.Process(proc.pid)
print(f'MCP Server Memory: {p.memory_info().rss / 1024 / 1024:.1f} MB')
proc.terminate()
"
```
python3 fetcher.py spotify test  
python3 fetcher.py trello test
```

**Plugin Not Found:**
- Ensure plugin file ends with `_plugin.py`
- Check plugin implements `PluginInterface`
- Verify plugin file is in `plugins/` directory

**MCP Tools Not Working:**
```bash
# Test MCP functionality
python3 test_mcp.py

# Check server logs
MCP_LOG_LEVEL=DEBUG python3 mcp_server.py
```

### Getting Help

- 📖 See [MCP_GUIDE.md](MCP_GUIDE.md) for detailed MCP documentation
- 🔍 See [MCP_EXAMPLES.md](MCP_EXAMPLES.md) for AI assistant integration examples
- 🛠️ Use `claude_desktop_config.json` as template for Claude Desktop integration
- 🐛 Check [Issues](https://github.com/carloskvasir/fetcher/issues) for known problems  
- 💬 Start a [Discussion](https://github.com/carloskvasir/fetcher/discussions) for questions

## Project Structure

```
fetcher/
├── README.md                    # Main documentation
├── MCP_GUIDE.md                # Detailed MCP guide  
├── MCP_EXAMPLES.md             # AI assistant examples
├── fetcher.py                  # CLI interface
├── mcp_server.py              # MCP server implementation
├── mcp_client.py              # MCP client for testing
├── test_mcp.py                # Comprehensive MCP tests
├── mcp_config.json            # MCP server metadata
├── claude_desktop_config.json # Claude Desktop configuration
├── setup.sh                   # Automated setup script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── plugins/
    ├── plugin_interface.py    # Plugin base class
    ├── plugin_manager.py     # Plugin loader
    ├── github_plugin.py      # GitHub integration
    ├── spotify_plugin.py     # Spotify integration
    ├── trello_plugin.py      # Trello integration
    └── linkedin_plugin.py    # LinkedIn integration
```

### Useful Commands

```bash
# List all available plugins
python3 fetcher.py

# Show plugin commands
python3 fetcher.py github
python3 fetcher.py spotify  
python3 fetcher.py trello

# Test everything
python3 test_mcp.py

# Setup from scratch
./setup.sh
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
