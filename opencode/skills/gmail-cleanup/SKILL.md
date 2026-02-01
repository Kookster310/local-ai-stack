---
name: gmail-cleanup
description: Connect to Gmail API and perform inbox cleanup tasks. Use when managing email, clearing promotions, archiving old messages, or organizing labels.
---

# Gmail Cleanup

Manage Gmail inbox cleanup and organization tasks.

## Prerequisites

- Gmail API credentials (OAuth2 or service account)
- Credentials file at `/workspace/credentials/gmail-credentials.json`
- Token storage at `/workspace/credentials/gmail-token.json`

## Setup

### 1. Create Google Cloud Project

```bash
# Enable Gmail API in Google Cloud Console
# Download OAuth2 credentials as gmail-credentials.json
```

### 2. Install Dependencies

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

## Operations

### List Unread Messages

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

creds = Credentials.from_authorized_user_file('/workspace/credentials/gmail-token.json')
service = build('gmail', 'v1', credentials=creds)

results = service.users().messages().list(
    userId='me',
    q='is:unread',
    maxResults=50
).execute()
```

### Cleanup Promotions

```python
# Archive all promotional emails older than 30 days
results = service.users().messages().list(
    userId='me',
    q='category:promotions older_than:30d'
).execute()

for msg in results.get('messages', []):
    service.users().messages().modify(
        userId='me',
        id=msg['id'],
        body={'removeLabelIds': ['INBOX']}
    ).execute()
```

### Bulk Delete by Sender

```python
# Delete all emails from specific sender
results = service.users().messages().list(
    userId='me',
    q='from:newsletter@spam.com'
).execute()

for msg in results.get('messages', []):
    service.users().messages().trash(userId='me', id=msg['id']).execute()
```

## Common Cleanup Tasks

| Task | Gmail Query |
|------|-------------|
| Old promotions | `category:promotions older_than:30d` |
| Large attachments | `has:attachment larger:10M` |
| Unsubscribe candidates | `unsubscribe older_than:90d` |
| Social notifications | `category:social older_than:7d` |
| Read newsletters | `is:read category:updates older_than:14d` |

## Safety

- Always preview matches before bulk operations
- Use `trash()` instead of `delete()` for recoverability
- Log operations to `/workspace/logs/gmail-cleanup.log`
