---
name: cron-tasks
description: Schedule and manage automated cron tasks. Use when setting up recurring jobs, checking task schedules, or troubleshooting cron execution.
---

# Cron Task Management

Schedule and manage automated tasks using cron.

## Configuration

Task definitions stored in `/workspace/cron/tasks.yaml`:

```yaml
tasks:
  gmail_cleanup:
    schedule: "0 6 * * *"  # Daily at 6 AM
    command: "python /workspace/scripts/gmail_cleanup.py"
    description: "Clean up Gmail inbox"
    
  arr_check:
    schedule: "*/30 * * * *"  # Every 30 minutes
    command: "python /workspace/scripts/arr_check.py"
    description: "Check arr stack for import issues"
    
  truenas_health:
    schedule: "0 */4 * * *"  # Every 4 hours
    command: "python /workspace/scripts/truenas_health.py"
    description: "TrueNAS health check"
    
  blog_sync:
    schedule: "0 9 * * 1"  # Monday at 9 AM
    command: "python /workspace/scripts/blog_sync.py"
    description: "Sync blog repository"
```

## Cron Schedule Reference

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * *
```

### Common Schedules

| Pattern | Description |
|---------|-------------|
| `0 * * * *` | Every hour |
| `*/15 * * * *` | Every 15 minutes |
| `0 6 * * *` | Daily at 6 AM |
| `0 0 * * 0` | Weekly on Sunday |
| `0 0 1 * *` | Monthly on 1st |

## Task Management

### Generate Crontab

```python
import yaml

def generate_crontab():
    """Generate crontab from tasks.yaml using modular wrapper"""
    with open('/workspace/cron/tasks.yaml') as f:
        config = yaml.safe_load(f)
    
    lines = [
        "# OpenCode Automated Tasks",
        "",
        "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
        ""
    ]
    
    for name, task in config['tasks'].items():
        lines.append(f"# {task['description']}")
        lines.append(f"{task['schedule']} /workspace/scripts/run-cron-task.py {name} \"{task['prompt']}\" --log {name}.log")
        lines.append("")
    
    return '\n'.join(lines)

# Write crontab file
crontab = generate_crontab()
with open('/workspace/cron/crontab', 'w') as f:
    f.write(crontab)
```

### Install Crontab

```bash
crontab /workspace/cron/crontab
```

### Using the Modular Wrapper

The `/workspace/scripts/run-cron-task.py` wrapper ensures:
- Proper context loading (MEMORY.md, SOUL.md, hosts.yaml)
- Automatic logging to `/workspace/logs/cron.log` as required by AGENTS.md
- Optional task-specific log files
- Environment setup for agent execution

**Usage:**
```bash
/workspace/scripts/run-cron-task.py <task_name> "<prompt>" [--log <log_file>]
```

**Examples:**
```bash
# Simple task with only cron.log
/workspace/scripts/run-cron-task.py health-check "Check system health"

# Task with specific log file
/workspace/scripts/run-cron-task.py email-check "Process emails" --log email-check.log
```

### List Current Tasks

```bash
crontab -l
```

## Task Scripts Template

### Base Script Structure

```python
#!/usr/bin/env python3
"""
Task: [Description]
Schedule: [Cron schedule]
"""

import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='/workspace/logs/task_name.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    logging.info("Task started")
    
    try:
        # Task logic here
        pass
        
        logging.info("Task completed successfully")
    except Exception as e:
        logging.error(f"Task failed: {e}")
        raise

if __name__ == '__main__':
    main()
```

## Monitoring

### Check Last Run

```python
import os
from datetime import datetime

def check_task_status(task_name):
    """Check when task last ran"""
    log_file = f'/workspace/logs/{task_name}.log'
    
    if os.path.exists(log_file):
        mtime = os.path.getmtime(log_file)
        last_run = datetime.fromtimestamp(mtime)
        
        # Read last few lines
        with open(log_file) as f:
            lines = f.readlines()
            last_lines = lines[-5:] if len(lines) >= 5 else lines
        
        return {
            'last_run': last_run,
            'recent_output': ''.join(last_lines)
        }
    
    return None
```

### Health Dashboard

```python
def task_health_report():
    """Generate health report for all tasks"""
    with open('/workspace/cron/tasks.yaml') as f:
        config = yaml.safe_load(f)
    
    report = []
    for name, task in config['tasks'].items():
        status = check_task_status(name)
        report.append({
            'name': name,
            'description': task['description'],
            'schedule': task['schedule'],
            'last_run': status['last_run'] if status else 'Never',
            'status': 'OK' if status else 'Unknown'
        })
    
    return report
```

## Directory Structure

```
/workspace/cron/
├── tasks.yaml      # Task definitions
├── crontab         # Generated crontab file
└── README.md       # Documentation

/workspace/scripts/
├── gmail_cleanup.py
├── arr_check.py
├── truenas_health.py
└── blog_sync.py

/workspace/logs/
├── gmail_cleanup.log
├── arr_check.log
├── truenas_health.log
└── blog_sync.log
```