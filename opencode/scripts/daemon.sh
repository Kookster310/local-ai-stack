#!/bin/bash
# OpenCode Daemon Mode
#
# Keeps the container running so the agent can be invoked as needed.

set -e

echo "=== OpenCode Daemon Starting ==="
echo "Time: $(date)"

# Ensure directories exist
mkdir -p /workspace/logs
mkdir -p /workspace/credentials

# Copy credentials and fix permissions (mounted read-only, need writable copy)
echo "Looking for credentials..."
if [ -d /mnt/credentials ]; then
    echo "  Found /mnt/credentials"
    ls -la /mnt/credentials/
    
    echo "Copying credentials..."
    cp -rv /mnt/credentials/* /workspace/credentials/
    
    # Fix SSH key permissions
    if [ -f /workspace/credentials/id_rsa ]; then
        chmod 600 /workspace/credentials/id_rsa
        echo "  SSH key ready"
    else
        echo "  Warning: No id_rsa found after copy"
    fi
    
    # Fix any other credential files
    chmod 600 /workspace/credentials/*.yaml 2>/dev/null || true
    chmod 600 /workspace/credentials/*.json 2>/dev/null || true
    
    echo "Credentials directory:"
    ls -la /workspace/credentials/
else
    echo "  Warning: /mnt/credentials not found"
fi

echo ""
echo "=== Daemon Ready ==="
echo "Invoke tasks with: docker exec opencode-daemon opencode \"your task\""
echo "Logs: /workspace/logs/"
echo ""

# Keep container running
exec tail -f /dev/null
