# Deployment

Eva supports two deployment modes. Both use the same Docker image.

## GitHub Actions (Recommended)

Zero infrastructure needed. Eva runs on GitHub's runners.

### Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **Eva Scan** | `eva-scan.yml` | Cron (every 6h) + manual | Scheduled full pipeline scan |
| **Eva on Issue** | `eva-on-issue.yml` | New issue + `repository_dispatch` | Reactive scan when issues are opened |
| **Eva: Backlog Re-Triage** | `eva-triage-backlog.yml` | Cron (daily 08:19 UTC) + manual | Bulk re-verify the oldest open `feature-proposal` issues in ievo-ai/skills against the current codebase: close stale/duplicate (with cited evidence), stamp `backlog-verified`, or escalate `needs-operator` (eva#167). Dormant until `EVA_TRIAGE_ENABLED=true`; manual dispatch defaults to dry-run. |
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
| `EVA_TRIAGE_ENABLED` | `true` / `false` | Safety valve for `eva-triage-backlog.yml` (same pattern as `EVA_IMPLEMENT_ENABLED` / `EVA_QUEUE_ENABLED`): scheduled runs no-op and manual dispatches are forced to dry-run until set to `true` |

#### Agent model + effort (per-flow, eva#161)

Each autonomous-agent workflow reads its Claude model and reasoning effort from
an Actions variable, falling back to today's value when the variable is unset —
so switching a flow's model/effort is an ops action (change a variable → next run
uses it), not a workflow-file edit. Repo-level variables override org-level
(GitHub precedence), so per-repo experiments are possible. Values may be an alias
(`opus`, `sonnet`, `haiku`, `fable`) or a full id (e.g. `claude-fable-5`); effort
is one of `low` / `medium` / `high` / `xhigh` / `max`.

| Variable | Default | Flow |
|----------|---------|------|
| `EVA_MODEL_IMPLEMENT` | `opus` | eva-implement (issue → PR builder) |
| `EVA_EFFORT_IMPLEMENT` | `high` | eva-implement |
| `EVA_MODEL_FIX` | `opus` | eva-fix-pr (review-fix loop) |
| `EVA_EFFORT_FIX` | `high` | eva-fix-pr |
| `EVA_MODEL_REVIEW` | `opus` | eva-review-pr (PR gatekeeper) |
| `EVA_EFFORT_REVIEW` | `high` | eva-review-pr |
| `EVA_MODEL_ROUTER` | `sonnet` | eva-on-issue (issue router) |
| `EVA_EFFORT_ROUTER` | `high` | eva-on-issue |
| `EVA_MODEL_RESEARCH` | `sonnet` | eva-research (model only) |
| `EVA_MODEL_TRIAGE` | `sonnet` | eva-triage-backlog (backlog re-triage) |
| `EVA_EFFORT_TRIAGE` | `high` | eva-triage-backlog |
| `EVA_MODEL_PUBLISH` | `haiku` | publish-evolution blurb (model only) |

`high` is also the current model-default effort for the `opus` (Opus 4.8) and
`sonnet` (Sonnet 5) aliases, so the effort defaults are behavior-preserving — they
pin what the CLI already used implicitly. Effort is deliberately not parametrized
for `eva-research` / `publish-evolution` (model only). To try Fable, set the
relevant `EVA_MODEL_*` to `fable` (or `claude-fable-5`).

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

The `eva-tg-daemon` service runs `eva tg-process --limit 50` every 10 seconds in a loop with `restart: unless-stopped`. Eva uses Claude Code CLI (`claude -p --model opus`) with full tool access (`--allowedTools Bash,Read,Glob,Grep,WebFetch`) — no direct Anthropic API.

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
| `EVA_GITHUB_TOKEN` | Yes | GitHub PAT (git clone + API + `GH_TOKEN` for `gh` CLI) |
| `CLAUDE_CODE_OAUTH_TOKEN` | Yes | Claude Code subscription auth |
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
