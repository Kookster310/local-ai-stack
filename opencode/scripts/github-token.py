#!/usr/bin/env python3
"""
Generate a GitHub App installation token.

Usage: python github-token.py
Output: Installation access token (valid for 1 hour)
"""

import json
import time
import sys
import jwt
import requests

CREDENTIALS_FILE = '/workspace/credentials/github-credentials.json'

def load_credentials():
    with open(CREDENTIALS_FILE) as f:
        return json.load(f)

def load_private_key(creds):
    key_file = f"/workspace/credentials/{creds['private_key_file']}"
    with open(key_file) as f:
        return f.read()

def generate_jwt(app_id, private_key):
    """Generate a JWT for GitHub App authentication."""
    now = int(time.time())
    payload = {
        'iat': now - 60,  # Issued 60 seconds ago
        'exp': now + (10 * 60),  # Expires in 10 minutes
        'iss': app_id
    }
    return jwt.encode(payload, private_key, algorithm='RS256')

def get_installation_token(jwt_token, installation_id):
    """Exchange JWT for an installation access token."""
    response = requests.post(
        f'https://api.github.com/app/installations/{installation_id}/access_tokens',
        headers={
            'Authorization': f'Bearer {jwt_token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
    )
    response.raise_for_status()
    return response.json()['token']

def main():
    creds = load_credentials()
    private_key = load_private_key(creds)
    
    jwt_token = generate_jwt(creds['app_id'], private_key)
    token = get_installation_token(jwt_token, creds['installation_id'])
    
    print(token)

if __name__ == '__main__':
    main()
