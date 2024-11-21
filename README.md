# Fetcher

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)
[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/carloskvasir/fetcher/releases/tag/v1.0.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

A flexible Python-based tool for fetching information from multiple services (Trello, GitHub) through a plugin architecture.


## Features

- Plugin-based architecture
- Environment variable configuration
- Multiple service support:
  - Trello (boards, lists, cards)
  - GitHub (repos, issues, PRs, users, profile updates)
- Simple command-line interface
- Repository management capabilities

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
GITHUB_API_URL=https://api.github.com
GITHUB_GRAPHQL_URL=https://api.github.com/graphql
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

## Usage

### Trello Plugin

```bash
# Check connection
./fetcher.py trello check

# Fetch items
./fetcher.py trello 12345        # Default (card)
./fetcher.py trello card 12345   # Specific card
./fetcher.py trello board 67890  # Board details
./fetcher.py trello list 11111   # List details
```

### GitHub Plugin

```bash
# Check connection and list your repositories
./fetcher.py github check

# Fetch repository information
./fetcher.py github repo carloskvasir/fetcher  # Using owner/repo format
./fetcher.py github repo 12345                 # Using repository ID

# Fetch issue information
./fetcher.py github issue carloskvasir/fetcher/1  # Using owner/repo/number format
./fetcher.py github issue 1                       # Using issue number (in repository context)

# Fetch pull request information
./fetcher.py github pr carloskvasir/fetcher/1     # Using owner/repo/number format
./fetcher.py github pr 1                          # Using PR number (in repository context)

# Fetch user information
./fetcher.py github user carloskvasir

# Update GitHub profile
./fetcher.py github update name "Your Name"
./fetcher.py github update bio "Your Bio"
./fetcher.py github update location "Your Location"
./fetcher.py github update company "Your Company"
./fetcher.py github update blog "https://your-site.com"

# Update repository information
./fetcher.py github update repo owner/repo "New repository description"
```

## Global Installation

To use fetcher from anywhere in your system:

```bash
# User installation (recommended)
mkdir -p ~/bin
cp -r . ~/.local/lib/fetcher
ln -s ~/.local/lib/fetcher/fetcher.py ~/bin/fetcher
chmod +x ~/.local/lib/fetcher/fetcher.py

# Add to your .bashrc or .zshrc:
export PATH="$HOME/bin:$PATH"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## Roadmap

- [ ] Add more service plugins (GitLab, Jira)
- [ ] Implement caching for API requests
- [ ] Add interactive mode
- [ ] Support for colored output
- [ ] Add comprehensive test suite
- [ ] Publish to PyPI

## License

This project is licensed under the Mozilla Public License 2.0 - see the [LICENSE](LICENSE) file for details.

## Author

Carlos Kvasir ([@carloskvasir](https://github.com/carloskvasir)) - Building interesting tools to make developers' lives easier. 💼 Let's connect! Find me on [LinkedIn](https://www.linkedin.com/in/carloskvasir/) for professional networking and discussions about software development.
