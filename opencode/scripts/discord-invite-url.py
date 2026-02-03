#!/usr/bin/env python3
"""
Generate Discord bot invitation URL from credentials.

Usage: python3 /workspace/scripts/discord-invite-url.py
"""

import json
import sys

CREDENTIALS_FILE = '/workspace/credentials/discord-credentials.json'

# Common permission bits (add together for permissions_integer)
# https://discord.com/developers/docs/topics/permissions
PERMISSIONS = {
    'VIEW_CHANNEL': 1024,
    'SEND_MESSAGES': 2048,
    'SEND_MESSAGES_IN_THREADS': 274877906944,
    'EMBED_LINKS': 16384,
    'ATTACH_FILES': 32768,
    'READ_MESSAGE_HISTORY': 65536,
    'ADD_REACTIONS': 64,
    'USE_EXTERNAL_EMOJIS': 262144,
    'MENTION_EVERYONE': 131072,
}

# Default: view channels, send messages, read history, embeds
DEFAULT_PERMISSIONS = 84992  # 1024 + 2048 + 65536 + 16384

def main():
    try:
        with open(CREDENTIALS_FILE) as f:
            creds = json.load(f)
    except FileNotFoundError:
        print(f"Error: {CREDENTIALS_FILE} not found")
        sys.exit(1)

    app_id = creds.get('application_id')
    if not app_id:
        print("Error: application_id missing in credentials")
        sys.exit(1)

    perm = creds.get('permissions_integer')
    if perm is not None:
        perm = int(perm)
    else:
        perm = DEFAULT_PERMISSIONS

    url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={app_id}"
        f"&permissions={perm}"
        f"&scope=bot"
    )
    print(url)

if __name__ == '__main__':
    main()
