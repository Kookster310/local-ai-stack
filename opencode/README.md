# OpenCode Agent Configuration

This directory contains the configuration and skills for the OpenCode AI agent, designed to automate home infrastructure tasks.

## Directory Structure

```
opencode/
├── Dockerfile              # Container build configuration
├── opencode.json           # OpenCode configuration (Ollama provider)
├── hosts.yaml              # SSH host definitions
├── SOUL.md                 # Agent memory and evolution document
├── credentials/            # Sensitive credentials (gitignored)
│   ├── id_rsa              # SSH private key
│   ├── gmail-credentials.json
│   ├── arr-config.yaml
│   └── ...
├── skills/                 # Agent skill definitions
│   ├── SKILL.md            # Skills index
│   ├── gmail-cleanup/
│   ├── ssh-management/
│   ├── truenas/
│   ├── arr-stack/
│   ├── moltbook/
│   ├── blog/
│   └── cron-tasks/
├── scripts/                # Automation scripts (created at runtime)
├── logs/                   # Task execution logs
└── cron/                   # Cron task definitions
```

## Skills

| Skill | Purpose |
|-------|---------|
| gmail-cleanup | Manage Gmail inbox, clean promotions, organize labels |
| ssh-management | Connect to network hosts via SSH |
| truenas | TrueNAS server, storage, arr stack (Radarr/Sonarr), Plex, Transmission |
| moltbook | Post updates to Moltbook platform |
| blog | Manage blog content via git repository |
| cron-tasks | Schedule and manage automated tasks |

## Setup

### 1. Configure Hosts

Edit `hosts.yaml` to add your network hosts:

```yaml
hosts:
  truenas:
    ip: 192.168.1.100
    port: 22
    user: root
    key: /workspace/credentials/id_rsa
```

### 2. Add Credentials

Copy your SSH keys and API credentials to the `credentials/` directory:

```bash
# SSH key
cp ~/.ssh/id_rsa opencode/credentials/

# Create API config files
cat > opencode/credentials/arr-config.yaml << EOF
radarr:
  url: http://radarr:7878
  api_key: YOUR_RADARR_API_KEY

sonarr:
  url: http://sonarr:8989
  api_key: YOUR_SONARR_API_KEY
EOF
```

### 3. Build and Run

```bash
# Build the container
docker compose build opencode

# Run interactively
docker compose run --rm opencode

# Or run with a specific command
docker compose run --rm opencode "Check TrueNAS container health"
```

## SOUL.md

The `SOUL.md` file serves as the agent's evolving memory. The agent can update this file to:

- Record learned user preferences
- Store troubleshooting solutions
- Track session context
- Log significant events and learnings

This allows the agent to improve over time and maintain continuity across sessions.

## Volumes

Mount these volumes in docker-compose.yml for persistence:

```yaml
volumes:
  - ./opencode/credentials:/workspace/credentials:ro
  - ./opencode/logs:/workspace/logs
  - ./opencode/SOUL.md:/workspace/SOUL.md
```

## Security Notes

- The `credentials/` directory is gitignored - never commit secrets
- SSH keys should have restrictive permissions (600)
- Consider using read-only mounts for credentials in production
- Review SOUL.md updates periodically for sensitive information
