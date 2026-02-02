#!/bin/bash
# OpenCode Daemon Mode
#
# Keeps the container running so the agent can be invoked as needed.
# Note: Credentials are set up by entrypoint.sh before this runs.

echo "=== OpenCode Daemon Starting ==="
echo "Time: $(date)"
echo "User: $(whoami)"

# Show credentials status
if [ -f /workspace/credentials/id_rsa ]; then
    echo "SSH key: ready"
    ls -la /workspace/credentials/id_rsa
else
    echo "SSH key: not found"
fi

echo ""
echo "=== Daemon Ready ==="
echo "Invoke tasks with: docker exec -it opencode-daemon opencode \"your task\""
echo "Logs: /workspace/logs/"
echo ""

# Keep container running
exec tail -f /dev/null
