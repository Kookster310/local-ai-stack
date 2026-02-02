# OpenCode Agent Instructions

You are an AI agent for home infrastructure automation. This workspace contains skills, configuration, and memory files that you should reference and update.

## Workspace Structure

```
/workspace/
├── AGENTS.md           # This file - your instructions
├── SOUL.md             # Your persistent memory - READ and UPDATE this
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

## On Every Session Start

1. **Read SOUL.md** to restore context from previous sessions
2. **Check hosts.yaml** for available SSH hosts if the task involves remote systems
3. **Reference the appropriate skill** in `skills/` for task-specific guidance

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

## Persistent Memory (SOUL.md)

**IMPORTANT**: You have a persistent memory file at `/workspace/SOUL.md`.

### Reading Memory
At the start of each session, read SOUL.md to:
- Recall learned user preferences
- Check pending tasks from previous sessions
- Review troubleshooting knowledge

### Writing Memory
After completing tasks or learning something new, **update SOUL.md** with:
- New preferences or patterns learned
- Troubleshooting solutions discovered
- Task completion summaries
- Context for follow-up in future sessions

### Update Format
When updating SOUL.md, add entries to the appropriate sections:
- **Learned Preferences**: User habits, preferred formats
- **Knowledge Base**: Troubleshooting notes, infrastructure details
- **Session Memory > Recent Activities**: Brief task summaries with dates
- **Evolution Log**: Significant learnings (with date)

## Credentials

Sensitive files are in `/workspace/credentials/`:
- `id_rsa` - SSH private key
- `arr-config.yaml` - Radarr/Sonarr API keys
- `gmail-credentials.json` - Google OAuth
- `moltbook-config.yaml` - Moltbook API

**Never log or display credential contents.**

## Logging

Log task outputs to `/workspace/logs/` for audit trail:
- `truenas.log` - TrueNAS/container operations
- `gmail-cleanup.log` - Email operations
- `arr-stack.log` - Radarr/Sonarr checks

## Example Task Flow

When asked "check the TrueNAS server":

1. Read `SOUL.md` for any relevant context
2. Read `hosts.yaml` to get TrueNAS connection details
3. Read `skills/truenas/SKILL.md` for operations guidance
4. Connect via SSH using `skills/ssh-management/SKILL.md`
5. Perform checks as documented in the skill
6. Update `SOUL.md` with findings if noteworthy
7. Log results to `/workspace/logs/truenas.log`
