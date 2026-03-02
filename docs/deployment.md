# Deployment

Eva supports two deployment modes. Both use the same Docker image.

## GitHub Actions (Recommended)

Zero infrastructure needed. Eva runs on GitHub's runners.

### Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **Eva Scan** | `eva-scan.yml` | Cron (every 6h) + manual | Scheduled full pipeline scan |
| **Eva on Issue** | `eva-on-issue.yml` | New issue + `repository_dispatch` | Reactive scan when issues are opened |
| **Tests** | `tests.yml` | Push / PR | CI: ruff lint + pytest on Python 3.10/3.11/3.12 |

### How the Scan Works

1. **Checkout** — clones `eva` and `marketplace` repos
2. **Auth** — resolves token (GitHub App if `USE_GITHUB_APP=true`, otherwise PAT)
3. **Docker build** — builds `eva:local` from Dockerfile
4. **Run** — executes `eva scan --marketplace /app/marketplace` inside the container
5. **Artifacts** — uploads scan results (if any)

### Manual Trigger

Go to Actions → Eva Scan → Run workflow:
- `dry_run`: true (default) or false
- `marketplace_ref`: branch/tag of marketplace repo (default: `main`)

### Cross-Repo Triggers

When an issue is opened in any iEvo repo, Eva can react automatically. Copy `scripts/notify-eva.yml` to other repos:

```yaml
# .github/workflows/notify-eva.yml (in cli, marketplace, sdk repos)
name: Notify Eva
on:
  issues:
    types: [opened, labeled]

jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - name: Dispatch to Eva
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.EVA_DISPATCH_TOKEN }}
          repository: ievo-ai/eva
          event-type: external-issue
          client-payload: |
            {
              "repo": "${{ github.repository }}",
              "issue_number": "${{ github.event.issue.number }}",
              "title": "${{ github.event.issue.title }}"
            }
```

Required: `EVA_DISPATCH_TOKEN` secret with `repo` scope in the source repo.

### Required Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `EVA_GITHUB_TOKEN` | Yes (if no App) | GitHub PAT with issues/PRs read access |
| `EVA_SENTRY_TOKEN` | No | Sentry auth token |
| `APP_ID` | If using App | GitHub App ID |
| `APP_PRIVATE_KEY` | If using App | GitHub App private key (PEM) |

### Repository Variable

| Variable | Values | Description |
|----------|--------|-------------|
| `USE_GITHUB_APP` | `true` / `false` | Switch between GitHub App and PAT auth |

## Docker (Self-Hosted)

### Image

- Base: `python:3.12-slim`
- Non-root user: `eva`
- Entrypoint: `eva` CLI
- Default command: `scan`
- Healthcheck: `eva status`

### One-Shot Scan

```bash
docker build -t eva .
docker run --rm \
  -e EVA_GITHUB_TOKEN=ghp_... \
  -e EVA_SENTRY_TOKEN=sntrys_... \
  eva scan --marketplace /app/marketplace
```

### Persistent with Docker Compose

```bash
# Setup
cp .env.example .env
# Edit .env with your tokens:
#   EVA_GITHUB_TOKEN=ghp_...
#   EVA_SENTRY_TOKEN=sntrys_...

# Run
docker compose up -d

# Monitor
docker compose logs -f

# Stop
docker compose down
```

### Docker Compose Config

```yaml
services:
  eva:
    build: .
    env_file: .env
    volumes:
      - ./marketplace:/app/marketplace:ro
      - eva-data:/home/eva/.eva
    command: scan --marketplace /app/marketplace

volumes:
  eva-data:
```

### Adding Cron (Self-Hosted)

Option 1 — Host crontab:
```cron
0 */6 * * * cd /path/to/eva && docker compose run --rm eva scan
```

Option 2 — Separate cron container in docker-compose.yml (see `docker-compose.yml` in repo).

## GitHub Actions + Docker

The GitHub Actions workflows **build and run the Docker container**. This means:
- Same image works everywhere (CI, local, VPS, k8s)
- Reproducible execution regardless of runner
- Easy to test locally: `docker build -t eva . && docker run --rm eva scan`

## Live Mode

By default Eva runs in **dry-run mode**. To create actual PRs:

### GitHub Actions
Set `dry_run: false` in the manual workflow dispatch.

### Docker
```bash
docker run --rm -e EVA_GITHUB_TOKEN=ghp_... eva scan --live
```

### CLI
```bash
eva scan --live
```

In live mode, Eva will:
1. Create a branch (`eva/mut-0001`)
2. Commit the patch
3. Open a Pull Request with full context
4. **Never auto-merge** — human review required

## Digital Ocean (Autonomous TG Responder)

Eva's Telegram responder runs autonomously on a DO host via Docker Compose.

### Architecture

```
DO Host
└── /opt/ievo-ai/
    ├── eva/              ← docker compose up -d eva-tg-daemon
    ├── marketplace/      ← children agents
    ├── cli/
    ├── sdk/
    ├── curator/
    └── ievo.ai/
```

The `eva-tg-daemon` service runs `eva tg-process --limit 50` every 3 minutes in a loop with `restart: unless-stopped`.

### First-Time Setup

```bash
# On the DO host (as root):
export EVA_GITHUB_TOKEN=github_pat_...
scp scripts/deploy-do.sh root@eva-host:/tmp/
ssh root@eva-host bash /tmp/deploy-do.sh

# Then fill in .env:
ssh root@eva-host
vi /opt/ievo-ai/eva/.env
cd /opt/ievo-ai/eva && docker compose up -d eva-tg-daemon
```

### Required Env Vars (DO)

| Variable | Required | Description |
|----------|----------|-------------|
| `EVA_GITHUB_TOKEN` | Yes | GitHub PAT (git clone + API) |
| `ANTHROPIC_API_KEY` | Yes | Haiku API key (~$1/mo) |
| `TELEGRAM_BOT_TOKEN` | Yes | Telegram Bot API token |
| `TELEGRAM_COMMUNITY_CHAT` | Yes | Telegram chat ID |
| `TELEGRAM_EVOLUTIONS_TOPIC` | No | Forum topic ID |
| `EVA_SENTRY_DSN` | No | Eva's own error reporting |

### Operations

```bash
# Watch logs
docker compose logs -f eva-tg-daemon

# Restart
docker compose restart eva-tg-daemon

# Stop
docker compose stop eva-tg-daemon

# Update and restart
cd /opt/ievo-ai/eva && git pull --ff-only
docker compose build eva-tg-daemon
docker compose up -d eva-tg-daemon
```

### Auto-Deploy

The `deploy-do.yml` workflow auto-deploys on push to `main` when Eva source or config changes.

Required GitHub secrets: `DO_HOST`, `DO_USER`, `DO_SSH_KEY`.
