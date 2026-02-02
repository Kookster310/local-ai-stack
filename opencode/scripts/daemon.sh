#!/bin/bash
# OpenCode Daemon Mode
#
# Keeps the container running so the agent can be invoked as needed.

set -e

echo "=== OpenCode Daemon Starting ==="
echo "Time: $(date)"

# Ensure log directory exists
mkdir -p /workspace/logs

echo ""
echo "=== Daemon Ready ==="
echo "Invoke tasks with: docker exec opencode-daemon opencode \"your task\""
echo "Logs: /workspace/logs/"
echo ""

# Keep container running
exec tail -f /dev/null
