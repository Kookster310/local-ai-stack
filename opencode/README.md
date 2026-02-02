# OpenCode Agent Configuration

This directory contains the configuration and skills for the OpenCode AI agent, designed to automate home infrastructure tasks.

## Directory Structure

```
opencode/
├── Dockerfile              # Container build configuration
├── opencode.json           # OpenCode configuration (Ollama provider)
├── AGENTS.md               # Agent startup instructions (read on every session)
├── hosts.yaml.example      # SSH host template (copy to hosts.yaml)
├── SOUL.md.example         # Agent memory template (copy to SOUL.md)
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
│   ├── moltbook/
│   ├── blog/
│   └── cron-tasks/
├── scripts/                # Automation scripts
│   ├── entrypoint.sh       # Container entrypoint (runs as root)
│   ├── daemon.sh           # Daemon mode (runs as opencode)
│   └── run-task.sh         # Execute single task with logging
├── cron/                   # Scheduled tasks
│   └── crontab             # Cron schedule definition
└── logs/                   # Task execution logs (gitignored)
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

Copy `hosts.yaml.example` to `hosts.yaml` and fill in your IP addresses:

```bash
cp opencode/hosts.yaml.example opencode/hosts.yaml
# Edit hosts.yaml with your actual IPs
```

The `hosts.yaml` file is gitignored since it contains network-specific information.

### 2. Create aiagent User on Hosts

Create a dedicated `aiagent` user on each host for the agent to SSH into:

```bash
# On TrueNAS/Linux hosts
sudo useradd -m -s /bin/bash aiagent
sudo usermod -aG docker aiagent  # For container management

# Copy SSH public key
sudo mkdir -p /home/aiagent/.ssh
sudo cp ~/.ssh/authorized_keys /home/aiagent/.ssh/
sudo chown -R aiagent:aiagent /home/aiagent/.ssh
```

### 3. Add Credentials

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

### 4. Build and Run

```bash
# Build the container
docker compose build opencode

# Run interactively (one-off)
docker compose run --rm opencode

# Or run with a specific command
docker compose run --rm opencode "Check TrueNAS container health"
```

## Daemon Mode

Run the agent as a persistent container that stays running:

```bash
# Start the daemon
docker compose up -d opencode-daemon

# Run a task manually
docker exec -it opencode-daemon opencode "Check TrueNAS container health"

# View container logs
docker compose logs -f opencode-daemon

# Check task execution logs
ls -la opencode/logs/

# Stop the daemon
docker compose stop opencode-daemon
```

## Scheduled Tasks (Cron)

The daemon runs cron for scheduled tasks. Edit `cron/crontab` to configure:

```bash
# Default: Nightly reflection at 11 PM
0 23 * * * /workspace/scripts/run-task.sh "Perform nightly reflection..." reflection

# Add your own tasks:
0 8 * * * /workspace/scripts/run-task.sh "Morning health check" morning-check
```

The container uses your host's timezone (via `/etc/localtime` mount).

After editing the crontab, restart the daemon to apply changes:

```bash
docker compose restart opencode-daemon
```

## AGENTS.md

The `AGENTS.md` file contains instructions that OpenCode reads at the start of every session. It tells the agent about:

- Workspace structure and available files
- How to use skills for different tasks
- SSH host configuration in `hosts.yaml`
- How to read and update `SOUL.md` for persistent memory

## SOUL.md

The `SOUL.md` file serves as the agent's evolving memory. The agent can update this file to:

- Record learned user preferences
- Store troubleshooting solutions
- Track session context
- Log significant events and learnings

This allows the agent to improve over time and maintain continuity across sessions.

**Setup**: Copy `SOUL.md.example` to `SOUL.md` to initialize. The actual `SOUL.md` is gitignored since it contains personal agent evolution data.

The agent is instructed (via AGENTS.md) to:
1. Read SOUL.md at the start of each session
2. Update it after completing tasks or learning something new

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
