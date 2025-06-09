"""
GitHub Plugin for Fetcher

This plugin provides functionality to interact with GitHub's API.

Commands:
    fetch - Fetch data from GitHub
    list - List repositories
    search - Search for repositories
    test - Test GitHub plugin
    me - Show authenticated user information
"""

import json
import os

import requests

from .plugin_interface import PluginInterface


class Plugin(PluginInterface):
    def __init__(self):
        self.api_url = "https://api.github.com"
        self.headers = {}
        if 'GITHUB_TOKEN' in os.environ:
            self.headers['Authorization'] = f'token {os.environ["GITHUB_TOKEN"]}'
        self._commands = {
            "test": "Run basic plugin tests",
            "list": "List repositories for a user: list [username]",
            "search": "Search repositories: search [query]",
            "fetch": "Fetch data from a specific endpoint: fetch [endpoint]",
            "me": "Show authenticated user information",
            "repo": "Get repository information: repo [owner/repo]",
            "issues": "List repository issues: issues [owner/repo]",
            "issue": "Get specific issue details: issue [owner/repo] [issue_number]",
            "create_issue": "Create new issue: create_issue [owner/repo] [title] [body]"
        }

    def list_commands(self):
        """List all available plugin commands."""
        print("Available commands:")
        for cmd, desc in self._commands.items():
            print(f"  - {cmd}: {desc}")

    def fetch(self, endpoint, params=None):
        url = f"{self.api_url}/{endpoint}"
        response = requests.get(url, params=params, headers=self.headers)
        
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Error fetching data from {url}: {response.status_code}")
            if response.status_code == 401:
                print("Authentication error. Please check if GITHUB_TOKEN environment variable is properly set.")
            return None

    def list_repos(self, username):
        """List repositories for a given username."""
        repos = self.fetch(f"users/{username}/repos")
        if repos:
            for repo in repos:
                print(f"- {repo['name']}: {repo['description']}")

    def search_repos(self, query):
        """Search GitHub repositories."""
        repos = self.fetch("search/repositories", {"q": query})
        if repos and 'items' in repos:
            for repo in repos['items']:
                print(f"- {repo['full_name']}: {repo['description']}")

    def test(self):
        """Run basic plugin tests."""
        print("Testing GitHub plugin...")
        
        print("\nTesting authentication:")
        user_data = self.get_user_info()
        
        if user_data:
            print("\nListing repositories for authenticated user:")
            self.list_repos(user_data['login'])
        else:
            print("\nListing repositories for user 'carloskvasir':")
            self.list_repos("carloskvasir")
        
        print("\nSearching repositories with 'python fetcher':")
        self.search_repos("python fetcher")

    def get_user_info(self):
        """Get authenticated user information."""
        user_data = self.fetch("user")
        if user_data:
            print("\nUser Information:")
            print(f"  Name: {user_data.get('name', 'N/A')}")
            print(f"  Login: {user_data.get('login', 'N/A')}")
            print(f"  Bio: {user_data.get('bio', 'N/A')}")
            print(f"  Email: {user_data.get('email', 'N/A')}")
            print(f"  Location: {user_data.get('location', 'N/A')}")
            print(f"  Public repositories: {user_data.get('public_repos', 0)}")
            print(f"  Followers: {user_data.get('followers', 0)}")
            print(f"  Following: {user_data.get('following', 0)}")
            return user_data
        return None

    def get_repo_info(self, repo_full_name):
        """Get detailed repository information."""
        repo_data = self.fetch(f"repos/{repo_full_name}")
        if repo_data:
            print(f"\n📁 Repository: {repo_data['full_name']}")
            print(f"📝 Description: {repo_data.get('description', 'No description')}")
            print(f"🌐 Language: {repo_data.get('language', 'Not specified')}")
            print(f"⭐ Stars: {repo_data.get('stargazers_count', 0)}")
            print(f"🍴 Forks: {repo_data.get('forks_count', 0)}")
            print(f"👁️ Watchers: {repo_data.get('watchers_count', 0)}")
            print(f"🐛 Open Issues: {repo_data.get('open_issues_count', 0)}")
            print(f"📅 Created: {repo_data.get('created_at', 'Unknown')}")
            print(f"🔄 Updated: {repo_data.get('updated_at', 'Unknown')}")
            print(f"🌍 URL: {repo_data.get('html_url', 'N/A')}")
            
            if repo_data.get('topics'):
                print(f"🏷️ Topics: {', '.join(repo_data['topics'])}")
            
            print(f"🔓 Private: {'Yes' if repo_data.get('private') else 'No'}")
            print(f"📜 License: {repo_data.get('license', {}).get('name', 'No license') if repo_data.get('license') else 'No license'}")
            
            return repo_data
        return None

    def list_issues(self, repo_full_name, state='open'):
        """List issues for a repository."""
        issues = self.fetch(f"repos/{repo_full_name}/issues", {"state": state})
        if issues:
            print(f"\n🐛 Issues for {repo_full_name} (State: {state}):")
            print("=" * 60)
            
            for issue in issues:
                # Skip pull requests (they appear in issues API)
                if 'pull_request' in issue:
                    continue
                    
                print(f"\n#{issue['number']} - {issue['title']}")
                print(f"👤 Author: {issue['user']['login']}")
                print(f"📅 Created: {issue['created_at']}")
                print(f"🏷️ State: {issue['state']}")
                
                if issue.get('labels'):
                    labels = [label['name'] for label in issue['labels']]
                    print(f"🔖 Labels: {', '.join(labels)}")
                
                if issue.get('assignee'):
                    print(f"👥 Assignee: {issue['assignee']['login']}")
                
                # Show first 100 chars of body
                body = issue.get('body', '')
                if body:
                    preview = body[:100] + "..." if len(body) > 100 else body
                    print(f"📝 Preview: {preview}")
                
                print(f"🔗 URL: {issue['html_url']}")
            
            return issues
        return None

    def get_issue_details(self, repo_full_name, issue_number):
        """Get detailed information about a specific issue."""
        issue = self.fetch(f"repos/{repo_full_name}/issues/{issue_number}")
        if issue:
            print(f"\n🐛 Issue #{issue['number']}: {issue['title']}")
            print("=" * 80)
            print(f"📝 Repository: {repo_full_name}")
            print(f"👤 Author: {issue['user']['login']}")
            print(f"📅 Created: {issue['created_at']}")
            print(f"🔄 Updated: {issue['updated_at']}")
            print(f"🏷️ State: {issue['state']}")
            
            if issue.get('labels'):
                labels = [f"{label['name']} ({label['color']})" for label in issue['labels']]
                print(f"🔖 Labels: {', '.join(labels)}")
            
            if issue.get('milestone'):
                print(f"🎯 Milestone: {issue['milestone']['title']}")
            
            if issue.get('assignee'):
                print(f"👥 Assignee: {issue['assignee']['login']}")
            
            if issue.get('assignees') and len(issue['assignees']) > 1:
                assignees = [user['login'] for user in issue['assignees']]
                print(f"👥 Assignees: {', '.join(assignees)}")
            
            print(f"💬 Comments: {issue.get('comments', 0)}")
            print(f"🔗 URL: {issue['html_url']}")
            
            if issue.get('body'):
                print(f"\n📄 Description:")
                print("-" * 40)
                print(issue['body'])
                print("-" * 40)
            
            # Get comments if any
            if issue.get('comments', 0) > 0:
                self.get_issue_comments(repo_full_name, issue_number)
            
            return issue
        return None

    def get_issue_comments(self, repo_full_name, issue_number):
        """Get comments for a specific issue."""
        comments = self.fetch(f"repos/{repo_full_name}/issues/{issue_number}/comments")
        if comments:
            print(f"\n💬 Comments ({len(comments)}):")
            print("=" * 50)
            
            for i, comment in enumerate(comments, 1):
                print(f"\nComment #{i}")
                print(f"👤 Author: {comment['user']['login']}")
                print(f"📅 Posted: {comment['created_at']}")
                if comment['created_at'] != comment['updated_at']:
                    print(f"🔄 Updated: {comment['updated_at']}")
                print(f"💬 Content:")
                print("-" * 30)
                print(comment['body'])
                print("-" * 30)
            
            return comments
        return None

    def create_issue(self, repo_full_name, title, body="", labels=None):
        """Create a new issue in a repository."""
        if not self.headers.get('Authorization'):
            print("❌ Authentication required to create issues. Please set GITHUB_TOKEN.")
            return None
        
        url = f"{self.api_url}/repos/{repo_full_name}/issues"
        
        issue_data = {
            "title": title,
            "body": body
        }
        
        if labels:
            issue_data["labels"] = labels if isinstance(labels, list) else [labels]
        
        response = requests.post(url, json=issue_data, headers=self.headers)
        
        if response.status_code == 201:
            issue = response.json()
            print(f"✅ Issue created successfully!")
            print(f"📝 Title: {issue['title']}")
            print(f"🔢 Number: #{issue['number']}")
            print(f"🔗 URL: {issue['html_url']}")
            return issue
        else:
            print(f"❌ Error creating issue: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    def run(self, command: str, *args, **kwargs):
        """Execute a specific plugin command."""
        if command == "test":
            self.test()
        elif command == "list":
            if len(args) < 1:
                print("Usage: list [username]")
                return
            username = args[0]
            self.list_repos(username)
        elif command == "search":
            if len(args) < 1:
                print("Usage: search [query]")
                return
            query = args[0]
            self.search_repos(query)
        elif command == "fetch":
            if len(args) < 1:
                print("Usage: fetch [endpoint]")
                return
            endpoint = args[0]
            print(self.fetch(endpoint))
        elif command == "me":
            self.get_user_info()
        elif command == "repo":
            if len(args) < 1:
                print("Usage: repo [owner/repo]")
                return
            repo_name = args[0]
            self.get_repo_info(repo_name)
        elif command == "issues":
            if len(args) < 1:
                print("Usage: issues [owner/repo] [state]")
                return
            repo_name = args[0]
            state = args[1] if len(args) > 1 else 'open'
            self.list_issues(repo_name, state)
        elif command == "issue":
            if len(args) < 2:
                print("Usage: issue [owner/repo] [issue_number]")
                return
            repo_name = args[0]
            issue_number = args[1]
            self.get_issue_details(repo_name, issue_number)
        elif command == "create_issue":
            if len(args) < 2:
                print("Usage: create_issue [owner/repo] [title] [body]")
                return
            repo_name = args[0]
            title = args[1]
            body = args[2] if len(args) > 2 else ""
            self.create_issue(repo_name, title, body)
        else:
            print(f"Unknown command: {command}")
            self.list_commands()

def plugin():
    """Create and return a new plugin instance."""
    return Plugin()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python github.py [command] [options]")
        sys.exit(1)
    
    command = sys.argv[1]
    github = Plugin()
    github.run(command, *sys.argv[2:])
