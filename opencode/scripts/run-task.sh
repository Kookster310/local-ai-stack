#!/bin/bash
# Run an OpenCode task with logging
#
# Usage: run-task.sh "task description" [log_name]
# Example: run-task.sh "Check TrueNAS health" truenas-health

TASK="$1"
LOG_NAME="${2:-task}"
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
LOG_FILE="/workspace/logs/${LOG_NAME}_${TIMESTAMP}.log"

echo "=== Task Started: $(date) ===" | tee "$LOG_FILE"
echo "Task: $TASK" | tee -a "$LOG_FILE"
echo "---" | tee -a "$LOG_FILE"

# Run opencode with the task
cd /workspace
opencode --yes "$TASK" 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

echo "---" | tee -a "$LOG_FILE"
echo "=== Task Completed: $(date) (exit: $EXIT_CODE) ===" | tee -a "$LOG_FILE"

exit $EXIT_CODE
