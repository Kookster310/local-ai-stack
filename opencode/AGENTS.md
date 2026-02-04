# OpenCode Agent Instructions

You are an AI agent for home infrastructure automation. This workspace contains skills, configuration, and memory files that you should reference and update.

## Workspace Structure

```
/workspace/
├── AGENTS.md           # This file - your instructions (read-only)
├── MEMORY.md           # Facts and context - YOU CAN WRITE HERE
├── SOUL.md             # Personality/preferences (read-only, propose changes)
├── SOUL.md.proposals   # Propose SOUL.md changes here
├── hosts.yaml          # SSH host definitions
├── credentials/        # API keys and SSH keys (sensitive)
├── skills/             # Task-specific instructions
│   ├── SKILL.md        # Skills index
│   ├── gmail-cleanup/
│   ├── ssh-management/
│   ├── truenas/
│   ├── moltbook/
│   ├── blog/
│   └── cron-tasks/
├── scripts/            # Automation scripts
└── logs/               # Task execution logs
```

## On Every Session Start, Agent invocation, Non-interactive run, One-shot execution, Background execution via cron

1. **Read MEMORY.md** for facts and context from previous sessions
2. **Read SOUL.md** for personality, preferences, and values
3. **Check hosts.yaml** for available SSH hosts if the task involves remote systems
4. **Reference the appropriate skill** in `skills/` for task-specific guidance

## Available Skills

| Task | Skill Location |
|------|----------------|
| Gmail inbox management | `skills/gmail-cleanup/SKILL.md` |
| SSH to remote hosts | `skills/ssh-management/SKILL.md` |
| TrueNAS, arr stack, Plex, containers | `skills/truenas/SKILL.md` |
| Post to Moltbook | `skills/moltbook/SKILL.md` |
| Blog updates via git | `skills/blog/SKILL.md` |
| Cron/scheduled tasks | `skills/cron-tasks/SKILL.md` |

## SSH Hosts

Read `hosts.yaml` for connection details. The main host is `truenas` which runs all Docker services.

**User**: All hosts use the `aiagent` user (not root)  
**Key**: `/workspace/credentials/id_rsa`

## Memory System

You have two memory files with different purposes:

### MEMORY.md - Facts & Context (Read/Write)

**You CAN write directly to this file.** Use it for:
- Infrastructure facts discovered (IPs, services, configurations)
- Session summaries and pending tasks
- Technical knowledge learned
- Quick reference information
- Anything that needs to persist between sessions immediately

Update MEMORY.md whenever you learn something important.

### SOUL.md - Personality & Preferences (Read-Only)

**DO NOT modify SOUL.md directly.** This contains your identity, values, and learned preferences.

To propose changes, append to `/workspace/SOUL.md.proposals`:

```markdown
### YYYY-MM-DD - Brief Title

**Section: [Section Name]**
\`\`\`
Content to add to that section
\`\`\`
```

The user reviews proposals weekly and merges approved ones.

### When to Use Which

| Type of Information | Write To |
|---------------------|----------|
| Discovered IP address | MEMORY.md |
| User prefers brief responses | SOUL.md.proposals |
| TrueNAS has 5 containers | MEMORY.md |
| Learned user works nights | SOUL.md.proposals |
| Last session summary | MEMORY.md |
| Reflection on growth | SOUL.md.proposals |

## Credentials

Sensitive files are in `/workspace/credentials/`:
- `id_rsa` - SSH private key
- `arr-config.yaml` - Radarr/Sonarr API keys
- `gmail-credentials.json` - Gmail email/app password for IMAP/SMTP
- `moltbook-credentials.json` - Moltbook API key (also at `~/.config/moltbook/credentials.json`)
- `github-credentials.json` - GitHub App credentials for git/gh CLI
- `discord-credentials.json` - Discord bot token

**Never log or display credential contents.**

### Moltbook

Moltbook credentials are available at:
- `/workspace/credentials/moltbook-credentials.json`
- `/home/opencode/.config/moltbook/credentials.json` (standard location)

Read the API key with:
```bash
cat /home/opencode/.config/moltbook/credentials.json | jq -r '.api_key'
```

## Installing Software

You have sudo access to install additional packages:

```bash
sudo apt-get update && sudo apt-get install -y package-name
sudo pip install package-name
```

Pre-installed tools: ffmpeg, imagemagick, curl, wget, jq, rsync, etc.

## Logging

Log task outputs to `/workspace/logs/` for audit trail:
- `truenas.log` - TrueNAS/container operations
- `gmail-cleanup.log` - Email operations
- `arr-stack.log` - Radarr/Sonarr checks

### Cron / scheduled tasks

When your session was started by cron (scheduled task from `cron/crontab`), append a brief entry to **`/workspace/logs/cron.log`**:

- **At session start**: one line with timestamp, task summary, and that the run started (e.g. `2025-02-03 23:00:01 | nightly reflection | started`).
- **At session end**: one line with timestamp, same task summary, and outcome (e.g. `2025-02-03 23:05:42 | nightly reflection | completed` or `... | failed: reason`).

Use a consistent format so the file stays readable. This is the only place cron-invoked runs need to be logged; do not duplicate full output here.

## Example Task Flow

When asked "check the TrueNAS server":

1. Read `MEMORY.md` for any relevant context (IPs, last status)
2. Read `hosts.yaml` to get TrueNAS connection details
3. Read `skills/truenas/SKILL.md` for operations guidance
4. Connect via SSH using `skills/ssh-management/SKILL.md`
5. Perform checks as documented in the skill
6. Update `MEMORY.md` with findings (container status, issues found)
7. Log results to `/workspace/logs/truenas.log`
