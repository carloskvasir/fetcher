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
        url = f"{os.getenv('GITHUB_API_URL')}/user"
        headers = {
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'Accept': 'application/vnd.github.v3+json'
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print("✓ Connection to GitHub established successfully!")
            print(f"User: {user_info['login']}")
            print(f"Name: {user_info.get('name', 'Not set')}")
            print(f"Email: {user_info.get('email', 'Not public')}")
            
            # List repositories
            repos_url = f"{os.getenv('GITHUB_API_URL')}/user/repos"
            repos_response = requests.get(repos_url, headers=headers)
            
            if repos_response.status_code == 200:
                repos = repos_response.json()
                print("\nYour Repositories:")
                for repo in repos:
                    print(f"- {repo['name']} ({repo['visibility']}) - {repo['html_url']}")
            
        elif response.status_code == 401:
            print("✗ Authentication error. Check your GITHUB_TOKEN in .env file")
        else:
            print(f"✗ Error connecting to GitHub (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Error trying to connect to GitHub: {str(e)}")

def fetch_info(type=None, item_id=None):
    try:
        # Use 'repo' as default type
        if type is None:
            type = 'repo'
        
        if type not in ['repo', 'issue', 'pr', 'user']:
            print(f"Invalid type: {type}. Supported types are: repo, issue, pr, user")
            return

        headers = {
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        base_url = os.getenv('GITHUB_API_URL')
        
        if type == 'repo':
            # Check if item_id is a number or owner/repo format
            if '/' in item_id:
                url = f"{base_url}/repos/{item_id}"
            else:
                url = f"{base_url}/repositories/{item_id}"
                
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                info = response.json()
                print(f"Repository: {info['full_name']}")
                print(f"Description: {info.get('description', 'No description')}")
                print(f"Stars: {info['stargazers_count']}")
                print(f"Forks: {info['forks_count']}")
                print(f"Open Issues: {info['open_issues_count']}")
                print(f"URL: {info['html_url']}")
                
                # Get languages
                langs_response = requests.get(info['languages_url'], headers=headers)
                if langs_response.status_code == 200:
                    print("\nLanguages:")
                    for lang, bytes_count in langs_response.json().items():
                        print(f"- {lang}: {bytes_count} bytes")
                
        elif type == 'issue':
            # Assuming item_id format is "owner/repo/number" or just "number" for current repo
            if '/' in item_id:
                owner, repo, number = item_id.split('/')
                url = f"{base_url}/repos/{owner}/{repo}/issues/{number}"
            else:
                current_repo = os.getenv('GITHUB_REPOSITORY')
                if not current_repo:
                    print("Error: When using just the issue number, you must be in a GitHub repository")
                    return
                url = f"{base_url}/repos/{current_repo}/issues/{item_id}"
                
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                info = response.json()
                print(f"Issue: #{info['number']} - {info['title']}")
                print(f"State: {info['state']}")
                print(f"Created by: {info['user']['login']}")
                print(f"Created at: {info['created_at']}")
                print(f"Comments: {info['comments']}")
                print(f"URL: {info['html_url']}")
                if info.get('body'):
                    print("\nDescription:")
                    print(info['body'])
                
        elif type == 'pr':
            # Similar to issues
            if '/' in item_id:
                owner, repo, number = item_id.split('/')
                url = f"{base_url}/repos/{owner}/{repo}/pulls/{number}"
            else:
                current_repo = os.getenv('GITHUB_REPOSITORY')
                if not current_repo:
                    print("Error: When using just the PR number, you must be in a GitHub repository")
                    return
                url = f"{base_url}/repos/{current_repo}/pulls/{item_id}"
                
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                info = response.json()
                print(f"Pull Request: #{info['number']} - {info['title']}")
                print(f"State: {info['state']}")
                print(f"Created by: {info['user']['login']}")
                print(f"Created at: {info['created_at']}")
                print(f"Comments: {info['comments']}")
                print(f"Commits: {info['commits']}")
                print(f"Changed Files: {info['changed_files']}")
                print(f"URL: {info['html_url']}")
                if info.get('body'):
                    print("\nDescription:")
                    print(info['body'])
                
        elif type == 'user':
            url = f"{base_url}/users/{item_id}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                info = response.json()
                print(f"User: {info['login']}")
                print(f"Name: {info.get('name', 'Not set')}")
                print(f"Bio: {info.get('bio', 'No bio')}")
                print(f"Location: {info.get('location', 'Not set')}")
                print(f"Public Repos: {info['public_repos']}")
                print(f"Followers: {info['followers']}")
                print(f"Following: {info['following']}")
                print(f"URL: {info['html_url']}")
                
                # List repositories
                repos_url = f"{base_url}/users/{item_id}/repos?sort=updated&direction=desc"
                repos_response = requests.get(repos_url, headers=headers)
                
                if repos_response.status_code == 200:
                    repos = repos_response.json()
                    print("\nRepositories (most recent first):")
                    for repo in repos[:3]:  # Show only the 3 most recent
                        print(f"\n- {repo['name']}")
                        print(f"  Description: {repo.get('description', 'No description')}")
                        print(f"  Language: {repo.get('language', 'Not specified')}")
                        print(f"  Updated at: {repo['updated_at']}")
                        print(f"  URL: {repo['html_url']}")
                
        else:
            print(f"Error: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching information: {str(e)}")

def update_profile(field=None, value=None):
    """
    Update GitHub profile information
    Supported fields: name, bio, location, company, blog
    """
    try:
        if field not in ['name', 'bio', 'location', 'company', 'blog']:
            print(f"Invalid field: {field}. Supported fields are: name, bio, location, company, blog")
            return

        url = f"{os.getenv('GITHUB_API_URL')}/user"
        headers = {
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Get current profile data
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error getting current profile: Status code {response.status_code}")
            return
            
        current_data = response.json()
        
        # Update only the specified field
        data = {
            field: value
        }
        
        # Make PATCH request to update profile
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            info = response.json()
            print(f"✓ Successfully updated {field}!")
            print(f"Old {field}: {current_data.get(field, 'Not set')}")
            print(f"New {field}: {info.get(field, 'Not set')}")
        else:
            print(f"✗ Error updating profile: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error updating profile: {str(e)}")

def update_repo(repo_name, description):
    """
    Update GitHub repository information
    Currently supports updating description
    """
    try:
        base_url = os.getenv('GITHUB_API_URL')
        headers = {
            'Authorization': f"Bearer {os.getenv('GITHUB_TOKEN')}",
            'Accept': 'application/vnd.github.v3+json'
        }
        
        url = f"{base_url}/repos/{repo_name}"
        data = {
            'description': description
        }
        
        response = requests.patch(url, headers=headers, json=data)
        
        if response.status_code == 200:
            info = response.json()
            print(f"✓ Successfully updated repository description!")
            print(f"New description: {info.get('description', 'No description')}")
        else:
            print(f"✗ Error updating repository: Status code {response.status_code}")
            
    except Exception as e:
        print(f"Error updating repository: {str(e)}")
