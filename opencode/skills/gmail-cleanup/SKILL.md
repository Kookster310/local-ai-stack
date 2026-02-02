---
name: gmail-cleanup
description: Connect to Gmail and perform inbox cleanup tasks. Use when managing email, clearing promotions, archiving old messages, sending emails, or organizing labels.
---

# Gmail Management

Manage Gmail inbox, send emails, and perform cleanup tasks.

## Credentials

Store credentials at `/workspace/credentials/gmail-credentials.json`:

```json
{
  "email": "youragent@gmail.com",
  "app_password": "xxxx xxxx xxxx xxxx",
  "imap_server": "imap.gmail.com",
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587
}
```

**Setup App Password:**
1. Go to Google Account → Security → 2-Step Verification (enable if not already)
2. Go to App Passwords → Generate new app password
3. Copy the 16-character password (with spaces)

---

## Reading Email (IMAP)

```python
import imaplib
import email
import json

# Load credentials
with open('/workspace/credentials/gmail-credentials.json') as f:
    creds = json.load(f)

# Connect
mail = imaplib.IMAP4_SSL(creds['imap_server'])
mail.login(creds['email'], creds['app_password'])
mail.select('INBOX')

# Search for unread messages
status, messages = mail.search(None, 'UNSEEN')
message_ids = messages[0].split()

print(f"Found {len(message_ids)} unread messages")

# Read a message
for msg_id in message_ids[:5]:  # First 5
    status, data = mail.fetch(msg_id, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    print(f"From: {msg['From']}")
    print(f"Subject: {msg['Subject']}")
    print("---")

mail.logout()
```

## Sending Email (SMTP)

```python
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load credentials
with open('/workspace/credentials/gmail-credentials.json') as f:
    creds = json.load(f)

def send_email(to, subject, body, html=False):
    """Send an email via Gmail SMTP"""
    msg = MIMEMultipart('alternative')
    msg['From'] = creds['email']
    msg['To'] = to
    msg['Subject'] = subject
    
    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))
    
    with smtplib.SMTP(creds['smtp_server'], creds['smtp_port']) as server:
        server.starttls()
        server.login(creds['email'], creds['app_password'])
        server.send_message(msg)
    
    return True

# Example
send_email(
    to="human@example.com",
    subject="Status Report",
    body="Everything is running smoothly!"
)
```

---

## Common IMAP Operations

### Search Queries

```python
# Search examples
mail.search(None, 'UNSEEN')                    # Unread
mail.search(None, 'FROM', '"sender@example.com"')  # From specific sender
mail.search(None, 'SUBJECT', '"alert"')        # Subject contains
mail.search(None, 'SINCE', '01-Jan-2026')      # Since date
mail.search(None, 'BEFORE', '01-Jan-2026')     # Before date
mail.search(None, '(UNSEEN FROM "alerts")')    # Combined
```

### Mark as Read

```python
mail.store(msg_id, '+FLAGS', '\\Seen')
```

### Delete (Move to Trash)

```python
mail.store(msg_id, '+FLAGS', '\\Deleted')
mail.expunge()
```

### Move to Folder

```python
mail.copy(msg_id, 'Archive')
mail.store(msg_id, '+FLAGS', '\\Deleted')
mail.expunge()
```

---

## Cleanup Tasks

### Archive Old Promotions

```python
mail.select('[Gmail]/Promotions')
status, messages = mail.search(None, 'BEFORE', '01-Dec-2025')

for msg_id in messages[0].split():
    mail.copy(msg_id, '[Gmail]/All Mail')
    mail.store(msg_id, '+FLAGS', '\\Deleted')

mail.expunge()
```

### Get Inbox Summary

```python
def inbox_summary():
    mail.select('INBOX')
    
    _, all_msgs = mail.search(None, 'ALL')
    _, unread = mail.search(None, 'UNSEEN')
    
    return {
        'total': len(all_msgs[0].split()),
        'unread': len(unread[0].split())
    }
```

---

## Gmail Folders

| Folder | IMAP Name |
|--------|-----------|
| Inbox | `INBOX` |
| Sent | `[Gmail]/Sent Mail` |
| Drafts | `[Gmail]/Drafts` |
| Spam | `[Gmail]/Spam` |
| Trash | `[Gmail]/Trash` |
| All Mail | `[Gmail]/All Mail` |
| Starred | `[Gmail]/Starred` |
| Promotions | `[Gmail]/Promotions` |
| Social | `[Gmail]/Social` |
| Updates | `[Gmail]/Updates` |

---

## Safety

- Always preview matches before bulk operations
- Move to Trash instead of permanent delete
- Log operations to `/workspace/logs/gmail.log`
- Never log email contents, only metadata
