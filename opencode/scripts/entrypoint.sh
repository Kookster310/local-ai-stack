#!/bin/bash
# OpenCode Entrypoint
#
# Runs as root to set up credentials, then drops to opencode user

set -e

echo "=== OpenCode Entrypoint ==="

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

# Drop to opencode user and run the command
echo ""
exec gosu opencode "$@"
