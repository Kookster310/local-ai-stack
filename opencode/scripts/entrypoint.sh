#!/bin/bash
# OpenCode Entrypoint
#
# Runs as root to set up permissions and cron, then drops to opencode user

set -e

echo "=== OpenCode Entrypoint ==="
echo "Timezone: $(cat /etc/timezone 2>/dev/null || echo 'unknown')"
echo "Local time: $(date)"

# Ensure directories exist
mkdir -p /workspace/logs
mkdir -p /workspace/credentials
mkdir -p /workspace/data
mkdir -p /workspace/memory

# Fix ownership on workspace directories
chown opencode:opencode /workspace/logs
chown opencode:opencode /workspace/credentials
chown opencode:opencode /workspace/data
chown opencode:opencode /workspace/memory

# Fix permissions on credential files
echo "Setting up credentials..."
if [ -d /workspace/credentials ]; then
    for f in /workspace/credentials/*; do
        if [ -f "$f" ]; then
            chown opencode:opencode "$f"
            chmod 600 "$f"
            echo "  Ready: $(basename "$f")"
        fi
    done
fi

# Set up Moltbook credentials if present
if [ -f /workspace/credentials/moltbook-credentials.json ]; then
    mkdir -p /home/opencode/.config/moltbook
    cp /workspace/credentials/moltbook-credentials.json /home/opencode/.config/moltbook/credentials.json
    chown -R opencode:opencode /home/opencode/.config/moltbook
    chmod 600 /home/opencode/.config/moltbook/credentials.json
    echo "  Moltbook credentials configured"
fi

# Set up GitHub credentials if present
if [ -f /workspace/credentials/github-credentials.json ]; then
    GITHUB_TOKEN=$(jq -r '.token' /workspace/credentials/github-credentials.json)
    GITHUB_TOKEN_OWNER=$(jq -r '.token_owner' /workspace/credentials/github-credentials.json)
    GITHUB_COMMIT_NAME=$(jq -r '.commit_name' /workspace/credentials/github-credentials.json)
    GITHUB_COMMIT_EMAIL=$(jq -r '.commit_email' /workspace/credentials/github-credentials.json)
    
    # Configure git commit identity (can be agent's name)
    git config --global user.name "$GITHUB_COMMIT_NAME"
    git config --global user.email "$GITHUB_COMMIT_EMAIL"
    git config --global credential.helper store
    git config --global init.defaultBranch main
    
    # Configure GitHub CLI
    mkdir -p /home/opencode/.config/gh
    echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null || true
    chown -R opencode:opencode /home/opencode/.config/gh
    
    # Store git credentials (uses token owner for auth)
    echo "https://${GITHUB_TOKEN_OWNER}:${GITHUB_TOKEN}@github.com" > /home/opencode/.git-credentials
    chown opencode:opencode /home/opencode/.git-credentials
    chmod 600 /home/opencode/.git-credentials
    
    echo "  GitHub configured - commits as: $GITHUB_COMMIT_NAME <$GITHUB_COMMIT_EMAIL>"
fi

echo "Credentials ready"

# Set up cron if crontab exists
if [ -f /workspace/cron/crontab ]; then
    echo "Setting up cron..."
    
    # Install crontab for opencode user
    crontab -u opencode /workspace/cron/crontab
    
    # Start cron daemon
    service cron start
    
    echo "Cron installed. Schedule:"
    crontab -u opencode -l | grep -v "^#" | grep -v "^$" || echo "  (no active jobs)"
else
    echo "No crontab found at /workspace/cron/crontab"
fi

# Drop to opencode user and run the command
echo ""
exec gosu opencode "$@"
