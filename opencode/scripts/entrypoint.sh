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
    GITHUB_COMMIT_NAME=$(jq -r '.commit_name' /workspace/credentials/github-credentials.json)
    GITHUB_COMMIT_EMAIL=$(jq -r '.commit_email' /workspace/credentials/github-credentials.json)
    GITHUB_APP_ID=$(jq -r '.app_id // empty' /workspace/credentials/github-credentials.json)
    
    # Configure git commit identity
    git config --global user.name "$GITHUB_COMMIT_NAME"
    git config --global user.email "$GITHUB_COMMIT_EMAIL"
    git config --global init.defaultBranch main
    
    # Set up credential helper to use our token generator
    git config --global credential.helper '!/workspace/scripts/git-credential-github-app.sh'
    
    # Generate initial token for gh CLI
    if [ -n "$GITHUB_APP_ID" ]; then
        PRIVATE_KEY_FILE=$(jq -r '.private_key_file' /workspace/credentials/github-credentials.json)
        if [ -f "/workspace/credentials/$PRIVATE_KEY_FILE" ]; then
            GITHUB_TOKEN=$(python3 /workspace/scripts/github-token.py 2>/dev/null || echo "")
            if [ -n "$GITHUB_TOKEN" ]; then
                mkdir -p /home/opencode/.config/gh
                echo "$GITHUB_TOKEN" | gh auth login --with-token 2>/dev/null || true
                chown -R opencode:opencode /home/opencode/.config/gh
                echo "  GitHub App configured - commits as: $GITHUB_COMMIT_NAME"
            else
                echo "  Warning: Could not generate GitHub token"
            fi
        else
            echo "  Warning: GitHub private key file not found"
        fi
    fi
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
