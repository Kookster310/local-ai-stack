---
name: ssh-management
description: SSH into network services and servers. Use when connecting to remote hosts, managing containers, or executing commands on network infrastructure.
---

# SSH Management

Connect to and manage remote hosts via SSH.

## Configuration

Host definitions are stored in `../hosts.yaml`. Reference this file for available endpoints.

## Prerequisites

- SSH key at `/workspace/credentials/id_rsa` (or specified in hosts.yaml)
- Hosts file at `/workspace/hosts.yaml`

## Basic Operations

### Connect to Host

```bash
# Using host alias from hosts.yaml
ssh -i /workspace/credentials/id_rsa user@hostname -p port
```

### Execute Remote Command

```bash
ssh -i /workspace/credentials/id_rsa user@host "command"
```

### Execute Multiple Commands

```bash
ssh user@host << 'EOF'
  command1
  command2
  command3
EOF
```

## Python SSH (Paramiko)

```python
import paramiko
import yaml

# Load hosts
with open('/workspace/hosts.yaml') as f:
    hosts = yaml.safe_load(f)

def connect_host(host_name):
    """Connect to a host from hosts.yaml"""
    host = hosts['hosts'][host_name]
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    client.connect(
        hostname=host['ip'],
        port=host.get('port', 22),
        username=host['user'],
        key_filename=host.get('key', '/workspace/credentials/id_rsa')
    )
    return client

def run_command(client, command):
    """Execute command and return output"""
    stdin, stdout, stderr = client.exec_command(command)
    return stdout.read().decode(), stderr.read().decode()
```

## Common Patterns

### Check Service Status

```python
client = connect_host('truenas')
out, err = run_command(client, 'systemctl status docker')
print(out)
client.close()
```

### List Docker Containers

```python
client = connect_host('truenas')
out, err = run_command(client, 'docker ps --format "table {{.Names}}\t{{.Status}}"')
print(out)
client.close()
```

### Tail Logs

```python
client = connect_host('truenas')
out, err = run_command(client, 'tail -100 /var/log/syslog')
print(out)
client.close()
```

## Security Notes

- Never store passwords in code; use SSH keys
- Keys should be stored in `/workspace/credentials/` with 600 permissions
- Log all SSH sessions to `/workspace/logs/ssh-sessions.log`
