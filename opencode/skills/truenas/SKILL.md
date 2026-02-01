---
name: truenas
description: Manage TrueNAS server, storage pools, and all hosted Docker services including arr stack (Radarr, Sonarr), Plex, Transmission, and other containers. Use when working with TrueNAS or any of its hosted services.
---

# TrueNAS Management

Manage the main TrueNAS server, storage, and all Docker services.

## Connection

Use SSH management skill with host alias `truenas` from hosts.yaml.

```python
from skills.ssh_management import connect_host, run_command

client = connect_host('truenas')
```

## Hosted Services

All services run as Docker containers on TrueNAS:

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| Radarr | radarr | 7878 | Movie management |
| Sonarr | sonarr | 8989 | TV show management |
| Prowlarr | prowlarr | 9696 | Indexer management |
| Plex | plex | 32400 | Media streaming |
| Transmission | transmission | 9091 | Torrent client |

---

## Storage Operations

### Check Pool Status

```bash
zpool status
```

### List Datasets

```bash
zfs list -o name,used,avail,refer,mountpoint
```

### Scrub Status

```bash
zpool status -v | grep -A5 "scan:"
```

### Disk Usage

```bash
df -h
```

---

## Container Management

### List All Containers

```bash
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Check Container Health

```bash
docker inspect --format='{{.Name}}: {{.State.Status}}' $(docker ps -aq)
```

### View Container Logs

```bash
docker logs --tail 100 container_name
```

### Restart Container

```bash
docker restart container_name
```

### Container Resource Usage

```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### Restart Failed Containers

```python
out, _ = run_command(client, 'docker ps -a --filter "status=exited" --format "{{.Names}}"')
failed = out.strip().split('\n')

for container in failed:
    if container:
        run_command(client, f'docker start {container}')
        print(f"Restarted: {container}")
```

---

## Arr Stack (Radarr/Sonarr)

### API Configuration

Store API keys in `/workspace/credentials/arr-config.yaml`:

```yaml
radarr:
  url: http://truenas-ip:7878
  api_key: YOUR_API_KEY

sonarr:
  url: http://truenas-ip:8989
  api_key: YOUR_API_KEY
```

### Check Queue Status

```python
import requests
import yaml

with open('/workspace/credentials/arr-config.yaml') as f:
    config = yaml.safe_load(f)

def get_queue(service):
    """Get download queue for Radarr or Sonarr"""
    cfg = config[service]
    response = requests.get(
        f"{cfg['url']}/api/v3/queue",
        headers={'X-Api-Key': cfg['api_key']}
    )
    return response.json()

radarr_queue = get_queue('radarr')
print(f"Radarr queue: {len(radarr_queue.get('records', []))} items")
```

### Find Failed Imports

```python
def get_history(service, page_size=20):
    cfg = config[service]
    response = requests.get(
        f"{cfg['url']}/api/v3/history",
        params={'pageSize': page_size, 'sortDirection': 'descending'},
        headers={'X-Api-Key': cfg['api_key']}
    )
    return response.json()

def check_failed_imports(service):
    """Find downloads that failed to import"""
    history = get_history(service, 50)
    
    failed = []
    for record in history.get('records', []):
        if record.get('eventType') == 'downloadFailed':
            failed.append({
                'title': record.get('sourceTitle'),
                'date': record.get('date'),
                'data': record.get('data', {})
            })
    return failed

for svc in ['radarr', 'sonarr']:
    failed = check_failed_imports(svc)
    if failed:
        print(f"\n{svc.upper()} Failed Imports:")
        for f in failed:
            print(f"  - {f['title']} ({f['date']})")
```

### Arr Health Check

```python
def get_health(service):
    cfg = config[service]
    response = requests.get(
        f"{cfg['url']}/api/v3/health",
        headers={'X-Api-Key': cfg['api_key']}
    )
    return response.json()

for svc in ['radarr', 'sonarr']:
    health = get_health(svc)
    if health:
        print(f"\n{svc.upper()} Health Issues:")
        for issue in health:
            print(f"  - [{issue['type']}] {issue['message']}")
```

### Common Import Failures

| Issue | Cause | Resolution |
|-------|-------|------------|
| Permission denied | File ownership | Check container user permissions |
| Path not found | Incorrect mapping | Verify docker volume mounts |
| Quality cutoff | Already have better | Check quality profiles |
| Sample | Detected as sample | Adjust minimum file size |

---

## Plex

### Check Plex Status

```bash
docker logs --tail 50 plex
```

### Trigger Library Scan

```python
import requests

PLEX_URL = "http://truenas-ip:32400"
PLEX_TOKEN = "YOUR_PLEX_TOKEN"

def scan_library(library_id):
    requests.get(
        f"{PLEX_URL}/library/sections/{library_id}/refresh",
        params={'X-Plex-Token': PLEX_TOKEN}
    )
```

---

## Transmission

### Check Active Downloads

```bash
docker exec transmission transmission-remote -l
```

### Via API

```python
import requests

TRANSMISSION_URL = "http://truenas-ip:9091/transmission/rpc"

def get_torrents():
    response = requests.post(
        TRANSMISSION_URL,
        json={
            "method": "torrent-get",
            "arguments": {"fields": ["name", "status", "percentDone"]}
        }
    )
    return response.json()
```

---

## System Monitoring

### Check System Resources

```bash
top -bn1 | head -20
iostat -x 1 3
```

### Temperature Monitoring

```bash
smartctl -A /dev/sdX | grep Temperature
```

---

## Daily Health Check

```python
# Full TrueNAS health check
checks = [
    'zpool status -x',
    'docker ps -q | wc -l',
    'df -h / | tail -1',
    'uptime'
]

for cmd in checks:
    out, _ = run_command(client, cmd)
    print(f"{cmd}: {out.strip()}")

# Plus arr stack health
for svc in ['radarr', 'sonarr']:
    health = get_health(svc)
    failed = check_failed_imports(svc)
    print(f"{svc}: {len(health)} issues, {len(failed)} failed imports")
```

## Alerts

Log issues to `/workspace/logs/truenas.log` when:
- Pool status is not ONLINE
- Container is unhealthy or exited
- Disk usage exceeds 85%
- Arr stack has failed imports
- Temperature exceeds thresholds
