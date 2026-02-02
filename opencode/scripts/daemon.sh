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
if [ -d /mnt/credentials ]; then
    echo "Setting up credentials..."
    cp -r /mnt/credentials/* /workspace/credentials/ 2>/dev/null || true
    
    # Fix SSH key permissions
    if [ -f /workspace/credentials/id_rsa ]; then
        chmod 600 /workspace/credentials/id_rsa
        echo "  SSH key ready"
    fi
    
    # Fix any other credential files
    chmod 600 /workspace/credentials/*.yaml 2>/dev/null || true
    chmod 600 /workspace/credentials/*.json 2>/dev/null || true
fi

echo ""
echo "=== Daemon Ready ==="
echo "Invoke tasks with: docker exec opencode-daemon opencode \"your task\""
echo "Logs: /workspace/logs/"
echo ""

# Keep container running
exec tail -f /dev/null
