---
name: blog
description: Manage blog content via git repository. Use when creating posts, updating content, or publishing changes to the blog.
---

# Blog Management

Manage blog content through git-based workflows.

## Configuration

Store blog repo details in `/workspace/credentials/blog-config.yaml`:

```yaml
blog:
  repo_url: git@github.com:username/blog.git
  local_path: /workspace/blog
  branch: main
  posts_dir: content/posts
  deploy_branch: gh-pages  # or main for direct deploy
```

## Setup

### Clone Repository

```bash
git clone git@github.com:username/blog.git /workspace/blog
```

### Configure Git Identity

```bash
cd /workspace/blog
git config user.name "OpenCode Agent"
git config user.email "opencode@local"
```

## Content Operations

### Create New Post

```python
import os
import yaml
from datetime import datetime

with open('/workspace/credentials/blog-config.yaml') as f:
    config = yaml.safe_load(f)['blog']

def create_post(title, content, tags=None, draft=False):
    """Create a new blog post"""
    slug = title.lower().replace(' ', '-').replace("'", '')
    date = datetime.now()
    
    # Frontmatter
    frontmatter = {
        'title': title,
        'date': date.isoformat(),
        'draft': draft,
        'tags': tags or []
    }
    
    post_content = f"""---
{yaml.dump(frontmatter, default_flow_style=False)}---

{content}
"""
    
    # Create post file
    filename = f"{date.strftime('%Y-%m-%d')}-{slug}.md"
    filepath = os.path.join(config['local_path'], config['posts_dir'], filename)
    
    with open(filepath, 'w') as f:
        f.write(post_content)
    
    return filepath
```

### Update Existing Post

```python
def update_post(filename, new_content=None, new_frontmatter=None):
    """Update an existing blog post"""
    filepath = os.path.join(config['local_path'], config['posts_dir'], filename)
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Parse frontmatter and content
    parts = content.split('---', 2)
    if len(parts) >= 3:
        fm = yaml.safe_load(parts[1])
        body = parts[2]
        
        if new_frontmatter:
            fm.update(new_frontmatter)
        if new_content:
            body = '\n' + new_content + '\n'
        
        updated = f"---\n{yaml.dump(fm)}---{body}"
        
        with open(filepath, 'w') as f:
            f.write(updated)
    
    return filepath
```

### List Posts

```python
def list_posts(include_drafts=False):
    """List all blog posts"""
    posts_path = os.path.join(config['local_path'], config['posts_dir'])
    posts = []
    
    for filename in os.listdir(posts_path):
        if filename.endswith('.md'):
            with open(os.path.join(posts_path, filename)) as f:
                content = f.read()
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    fm = yaml.safe_load(parts[1])
                    if include_drafts or not fm.get('draft', False):
                        posts.append({
                            'filename': filename,
                            'title': fm.get('title'),
                            'date': fm.get('date'),
                            'draft': fm.get('draft', False)
                        })
    
    return sorted(posts, key=lambda x: x['date'], reverse=True)
```

## Git Operations

### Commit and Push Changes

```python
import subprocess

def commit_and_push(message):
    """Commit changes and push to remote"""
    repo_path = config['local_path']
    
    # Stage all changes
    subprocess.run(['git', 'add', '-A'], cwd=repo_path, check=True)
    
    # Commit
    subprocess.run(['git', 'commit', '-m', message], cwd=repo_path, check=True)
    
    # Push
    subprocess.run(['git', 'push', 'origin', config['branch']], cwd=repo_path, check=True)
    
    return True
```

### Pull Latest Changes

```python
def pull_latest():
    """Pull latest changes from remote"""
    subprocess.run(
        ['git', 'pull', 'origin', config['branch']],
        cwd=config['local_path'],
        check=True
    )
```

## Workflow Example

```python
# Full workflow: create post and publish
pull_latest()

filepath = create_post(
    title="Automated Post from OpenCode",
    content="This post was created automatically by the OpenCode agent.",
    tags=['automation', 'opencode']
)

commit_and_push(f"Add new post: {os.path.basename(filepath)}")
```

## Logging

Log operations to `/workspace/logs/blog-operations.log`.
