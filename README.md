# Fetcher

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL_2.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![Python](https://img.shields.io/badge/Python-3.6%2B-blue)](https://www.python.org/)

A flexible Python-based tool to retrieve information from Trello using environment variables and a plugin architecture.

## About

This project was developed using [Windsurf](https://codeium.com/windsurf) with assistance from Claude 3.5 Sonnet, providing an efficient way to interact with Trello boards, lists, and cards through the command line.

## Features

- Plugin-based architecture
- Environment variable configuration
- Flexible item retrieval (supports card, board, list types)
- Command-line interface for fetching and checking connections

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
# Edit .env with your Trello credentials
```

## Configuration

Copy `.env.example` to `.env` and fill in your Trello credentials:

```env
TRELLO_API_KEY=your_api_key_here
TRELLO_TOKEN=your_token_here
TRELLO_BASE_URL=https://api.trello.com/1
```

To get your Trello credentials:
1. Go to https://trello.com/power-ups/admin/
2. Create a new Power-Up
3. Generate API Key and Token

## Usage

```bash
# Check connection
./fetcher.py trello check

# Fetch a card (default type)
./fetcher.py trello 12345

# Fetch specific types
./fetcher.py trello card 12345    # Get card info
./fetcher.py trello board 67890   # Get board info with lists and cards
./fetcher.py trello list 11111    # Get list info with its cards
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

## License

This project is licensed under the Mozilla Public License 2.0 - see the LICENSE file for details.

## Author

Carlos Kvasir (https://github.com/carloskvasir)
