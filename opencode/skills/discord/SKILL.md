---
name: discord
description: Read and post messages to Discord channels. Use when interacting with Discord servers, reading channel history, or posting updates.
---

# Discord Integration

Read channels and post messages to Discord.

## Credentials

Store at `/workspace/credentials/discord-credentials.json`:

```json
{
  "bot_token": "MTxxxxxxxxxx...",
  "application_id": "123456789012345678",
  "permissions_integer": "84992",
  "default_guild_id": "123456789012345678",
  "default_channel_id": "123456789012345678"
}
```

### permissions_integer

Optional. Used to generate the bot invite URL. Sum the permission bits you need:

| Permission | Value |
|------------|-------|
| View Channels | 1024 |
| Send Messages | 2048 |
| Read Message History | 65536 |
| Embed Links | 16384 |
| Attach Files | 32768 |
| Add Reactions | 64 |

**Example:** Read + post + embeds = `1024 + 2048 + 65536 + 16384` = **84992**

Generate the invite URL:
```bash
python3 /workspace/scripts/discord-invite-url.py
```
Open the printed URL to invite the bot with these permissions.

## Setup

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Create New Application → name it (e.g., "OpenCode Agent")
3. Go to **Bot** → Create Bot → Copy the **Token**
4. Fill `discord-credentials.json` with `application_id` (Application ID in OAuth2) and `permissions_integer`
5. Run `python3 /workspace/scripts/discord-invite-url.py` → open the URL to invite the bot
6. Get **guild_id** and **channel_id**: Enable Developer Mode in Discord, right-click server/channel → Copy ID

---

## Reading Messages

```python
import json
import requests

# Load credentials
with open('/workspace/credentials/discord-credentials.json') as f:
    creds = json.load(f)

HEADERS = {
    'Authorization': f"Bot {creds['bot_token']}",
    'Content-Type': 'application/json'
}
BASE_URL = 'https://discord.com/api/v10'

def get_channel_messages(channel_id, limit=50):
    """Get recent messages from a channel."""
    response = requests.get(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=HEADERS,
        params={'limit': limit}
    )
    response.raise_for_status()
    return response.json()

# Get last 10 messages from default channel
messages = get_channel_messages(creds['default_channel_id'], limit=10)
for msg in messages:
    print(f"{msg['author']['username']}: {msg['content']}")
```

## Sending Messages

```python
def send_message(channel_id, content):
    """Send a message to a channel."""
    response = requests.post(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=HEADERS,
        json={'content': content}
    )
    response.raise_for_status()
    return response.json()

# Send to default channel
send_message(creds['default_channel_id'], "Hello from OpenCode Agent!")
```

## Send Embed

```python
def send_embed(channel_id, title, description, color=0x5865F2, fields=None):
    """Send a rich embed message."""
    embed = {
        'title': title,
        'description': description,
        'color': color
    }
    if fields:
        embed['fields'] = fields
    
    response = requests.post(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=HEADERS,
        json={'embeds': [embed]}
    )
    response.raise_for_status()
    return response.json()

# Send status embed
send_embed(
    creds['default_channel_id'],
    title="🖥️ System Status",
    description="All systems operational",
    color=0x00FF00,  # Green
    fields=[
        {'name': 'TrueNAS', 'value': 'Online', 'inline': True},
        {'name': 'Containers', 'value': '5 running', 'inline': True}
    ]
)
```

---

## Channel Operations

### List Guild Channels

```python
def get_guild_channels(guild_id):
    """Get all channels in a guild."""
    response = requests.get(
        f"{BASE_URL}/guilds/{guild_id}/channels",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()

channels = get_guild_channels(creds['default_guild_id'])
for ch in channels:
    if ch['type'] == 0:  # Text channel
        print(f"#{ch['name']} ({ch['id']})")
```

### Get Channel Info

```python
def get_channel(channel_id):
    """Get channel details."""
    response = requests.get(
        f"{BASE_URL}/channels/{channel_id}",
        headers=HEADERS
    )
    response.raise_for_status()
    return response.json()
```

---

## Searching Messages

```python
def search_messages(channel_id, limit=100, before=None, after=None):
    """Search through channel messages."""
    params = {'limit': min(limit, 100)}
    if before:
        params['before'] = before
    if after:
        params['after'] = after
    
    response = requests.get(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=HEADERS,
        params=params
    )
    response.raise_for_status()
    return response.json()

def find_messages_containing(channel_id, search_term, limit=100):
    """Find messages containing a search term."""
    messages = search_messages(channel_id, limit=limit)
    return [m for m in messages if search_term.lower() in m['content'].lower()]
```

---

## Reply to Message

```python
def reply_to_message(channel_id, message_id, content):
    """Reply to a specific message."""
    response = requests.post(
        f"{BASE_URL}/channels/{channel_id}/messages",
        headers=HEADERS,
        json={
            'content': content,
            'message_reference': {'message_id': message_id}
        }
    )
    response.raise_for_status()
    return response.json()
```

---

## React to Message

```python
def add_reaction(channel_id, message_id, emoji):
    """Add a reaction to a message."""
    # URL encode the emoji if it's a unicode emoji
    import urllib.parse
    emoji_encoded = urllib.parse.quote(emoji)
    
    response = requests.put(
        f"{BASE_URL}/channels/{channel_id}/messages/{message_id}/reactions/{emoji_encoded}/@me",
        headers=HEADERS
    )
    response.raise_for_status()

# Add thumbs up reaction
add_reaction(channel_id, message_id, "👍")
```

---

## Common Colors for Embeds

| Color | Hex | Use Case |
|-------|-----|----------|
| Discord Blurple | `0x5865F2` | Default |
| Green | `0x00FF00` | Success |
| Red | `0xFF0000` | Error |
| Yellow | `0xFFFF00` | Warning |
| Blue | `0x0099FF` | Info |

---

## Rate Limits

Discord has rate limits. The API returns headers:
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: When limit resets

For simple use, add small delays between bulk operations:

```python
import time
time.sleep(0.5)  # 500ms between messages
```
