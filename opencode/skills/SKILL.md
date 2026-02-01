---
name: opencode-skills
description: Index of available skills for the OpenCode agent. Reference this file to discover capabilities and navigate to specific skill instructions.
---

# OpenCode Skills

This directory contains skills that extend OpenCode's capabilities for automation, system management, and productivity tasks.

## Available Skills

| Skill | Description | Location |
|-------|-------------|----------|
| [gmail-cleanup](gmail-cleanup/SKILL.md) | Connect to Gmail and manage inbox cleanup | `skills/gmail-cleanup/` |
| [ssh-management](ssh-management/SKILL.md) | SSH into network services and servers | `skills/ssh-management/` |
| [truenas](truenas/SKILL.md) | TrueNAS server, storage, arr stack, Plex, Transmission | `skills/truenas/` |
| [moltbook](moltbook/SKILL.md) | Post content to Moltbook | `skills/moltbook/` |
| [blog](blog/SKILL.md) | Manage blog via git repository | `skills/blog/` |
| [cron-tasks](cron-tasks/SKILL.md) | Schedule and manage automated tasks | `skills/cron-tasks/` |

## Configuration Files

- **hosts.yaml**: SSH endpoints and connection details → `../hosts.yaml`
- **SOUL.md**: Agent memory and evolution → `../SOUL.md` (copy from `SOUL.md.example`)

## Usage

When performing a task, reference the appropriate skill file for detailed instructions. Skills can be combined for complex workflows.

### Example Workflow

```
1. SSH into TrueNAS → skills/ssh-management/SKILL.md + skills/truenas/SKILL.md
2. Check arr stack imports → (included in truenas skill)
3. Post status to Moltbook → skills/moltbook/SKILL.md
```
