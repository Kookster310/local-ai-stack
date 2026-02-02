---
name: github
description: Clone repositories, create branches, commit changes, and create pull requests on GitHub. Use when working with git repos or GitHub operations.
---

# GitHub Operations

Clone repos, create branches, and submit pull requests.

## Credentials

Uses GitHub App authentication. Credentials at `/workspace/credentials/github-credentials.json`:

```json
{
  "app_id": "123456",
  "installation_id": "12345678",
  "private_key_file": "github-app-private-key.pem",
  "commit_name": "OpenCode Agent",
  "commit_email": "agent@example.com",
  "default_repo": "owner/repo-name"
}
```

Also place your GitHub App private key at `/workspace/credentials/github-app-private-key.pem`.

Git and `gh` CLI are pre-configured. Tokens are generated automatically (valid 1 hour, refreshed as needed).

---

## Clone a Repository

```bash
# Clone via HTTPS (uses stored credentials)
git clone https://github.com/owner/repo.git

# Clone to specific directory
git clone https://github.com/owner/repo.git /workspace/repos/repo
```

## Create a Branch

```bash
cd /workspace/repos/repo
git checkout -b feature/my-new-feature
```

## Make Changes and Commit

```bash
# Stage changes
git add .

# Commit
git commit -m "feat: add new feature

Detailed description of changes"

# Push branch
git push -u origin feature/my-new-feature
```

---

## Create Pull Request

Using GitHub CLI (`gh`):

```bash
# Create PR from current branch
gh pr create --title "Add new feature" --body "Description of changes"

# Create PR with specific base branch
gh pr create --base main --title "Add new feature" --body "Description"

# Create draft PR
gh pr create --draft --title "WIP: New feature" --body "Work in progress"
```

## List Pull Requests

```bash
# List open PRs
gh pr list

# List your PRs
gh pr list --author @me

# View PR details
gh pr view 123
```

## Check PR Status

```bash
# Check CI status
gh pr checks 123

# View PR diff
gh pr diff 123
```

---

## Common Workflows

### Feature Branch Workflow

```bash
# Start from main
git checkout main
git pull

# Create feature branch
git checkout -b feature/my-feature

# Make changes...
git add .
git commit -m "feat: implement feature"

# Push and create PR
git push -u origin feature/my-feature
gh pr create --title "Implement feature" --body "Description"
```

### Quick Fix

```bash
git checkout main
git pull
git checkout -b fix/bug-description
# Fix the bug...
git add .
git commit -m "fix: resolve bug description"
git push -u origin fix/bug-description
gh pr create --title "Fix: Bug description" --body "Fixes #123"
```

---

## GitHub CLI Commands

| Command | Description |
|---------|-------------|
| `gh repo clone owner/repo` | Clone a repo |
| `gh pr create` | Create pull request |
| `gh pr list` | List PRs |
| `gh pr view NUM` | View PR details |
| `gh pr merge NUM` | Merge PR |
| `gh pr checkout NUM` | Checkout PR locally |
| `gh issue list` | List issues |
| `gh issue create` | Create issue |
| `gh release list` | List releases |

---

## Working Directory

Clone repos to `/workspace/repos/` for persistence:

```bash
mkdir -p /workspace/repos
git clone https://github.com/owner/repo.git /workspace/repos/repo
```

## Commit Message Format

```
type: short description

Longer description if needed.

Fixes #123
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
