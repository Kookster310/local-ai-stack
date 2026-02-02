#!/bin/bash
# OpenCode Entrypoint
#
# Runs as root to set up credentials and cron, then drops to opencode user

set -e

echo "=== OpenCode Entrypoint ==="
echo "Timezone: $(cat /etc/timezone 2>/dev/null || echo 'unknown')"
echo "Local time: $(date)"

# Ensure directories exist and are owned by opencode
mkdir -p /workspace/logs
mkdir -p /workspace/credentials
chown opencode:opencode /workspace/logs
chown opencode:opencode /workspace/credentials

# Copy credentials and fix permissions (must run as root to read mounted files)
if [ -d /mnt/credentials ]; then
    echo "Setting up credentials..."
    
    # Copy all credential files
    for f in /mnt/credentials/*; do
        if [ -f "$f" ]; then
            cp "$f" /workspace/credentials/
            filename=$(basename "$f")
            chown opencode:opencode "/workspace/credentials/$filename"
            chmod 600 "/workspace/credentials/$filename"
            echo "  Copied: $filename"
        fi
    done
    
    echo "Credentials ready"
else
    echo "Warning: /mnt/credentials not found"
fi

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
