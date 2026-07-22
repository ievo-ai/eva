# Deployment

Eva supports two deployment modes. Both use the same Docker image.

## GitHub Actions (Recommended)

Zero infrastructure needed. Eva runs on GitHub's runners.

### Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **Eva Scan** | `eva-scan.yml` | Cron (every 6h) + manual | Scheduled full pipeline scan |
| **Eva on Issue** | `eva-on-issue.yml` | New issue + `repository_dispatch` | Reactive scan when issues are opened |
| **Eva CI Failure Watchdog** | `eva-ci-failure.yml` | `repository_dispatch: ci-failure` + own `workflow_run` failures | Main-branch CI failure triage: supersede/dedup/rate-cap gates → transient re-run (once) or structured App-authored issue (eva#159) |
| **Eva Conflict Scan** | `eva-conflict-scan.yml` | Cron (every 2h) + manual | Recovers `eva-impl/*` PRs stranded `DIRTY` (merge-conflicting, invisible to every other trigger) — rebases cleanly onto `main` and pushes, or closes + re-queues the issue for a fresh build (eva#211) |
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

#### CI-failure forwarder (eva#159)

Eva watches for CI going red on `main` (or a scheduled workflow failing) across
the watch-list. Her own repo is covered directly by `eva-ci-failure.yml`'s
`workflow_run` subscription; every OTHER repo needs a thin forwarder that
dispatches `repository_dispatch: ci-failure` to `ievo-ai/eva`. Rollout is
repo-by-repo (skills first, same first-slice pattern as eva#143 — the forwarder
is a workflow file, so it lands in each repo via that repo's own PR).

Payload contract — **identifiers only**, no workflow names, no log text, no
free text (Eva re-reads everything from the API and re-verifies the failure
server-side): `repo` (slug), `run_id` / `workflow_id` / `run_attempt`
(numeric), `head_branch` / `head_sha` / `run_event` (enum/sha metadata),
`triggered_by` (actor login, observability only).

Template (adapt the `workflows:` list per repo — `workflow_run` requires exact
names, wildcards are not supported; never list forwarder/notify workflows or
the relay loops itself):

```yaml
# .github/workflows/forward-ci-failure.yml (per watch-list repo; skills first)
# Thin CI-failure forwarder — eva#159. Dispatches a metadata-only payload to
# ievo-ai/eva when a watched workflow FAILS on main. Eva's handler owns
# supersede/dedup/rate-cap; this stays dumb on purpose.
name: Forward CI Failure to Eva

on:
  workflow_run:
    workflows: ["Coverage Gate", "Pre-commit Gate", "Cut Release"]
    types: [completed]
    branches: [main]

permissions:
  contents: read

jobs:
  forward:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    concurrency:
      group: forward-ci-failure-${{ github.event.workflow_run.workflow_id }}
      cancel-in-progress: false
    if: >
      github.event.workflow_run.conclusion == 'failure' &&
      github.event.workflow_run.head_branch == 'main' &&
      github.event.workflow_run.head_repository.full_name == github.repository &&
      contains(fromJSON('["push","schedule","workflow_dispatch","repository_dispatch"]'),
               github.event.workflow_run.event)
    steps:
      - name: Generate App token
        id: app-token
        uses: actions/create-github-app-token@d72941d797fd3113feb6b93fd0dec494b13a2547  # v1.12.0
        with:
          app-id: ${{ secrets.APP_ID }}
          private-key: ${{ secrets.APP_PRIVATE_KEY }}
          owner: ievo-ai
          repositories: eva
      - name: Dispatch ci-failure
        uses: peter-evans/repository-dispatch@28959ce8df70de7be546dd1250a005dd32156697  # v4.0.1
        with:
          token: ${{ steps.app-token.outputs.token }}
          repository: ievo-ai/eva
          event-type: ci-failure
          client-payload: >
            {
              "repo": "${{ github.repository }}",
              "run_id": ${{ github.event.workflow_run.id }},
              "workflow_id": ${{ github.event.workflow_run.workflow_id }},
              "run_attempt": ${{ github.event.workflow_run.run_attempt }},
              "head_branch": "${{ github.event.workflow_run.head_branch }}",
              "head_sha": "${{ github.event.workflow_run.head_sha }}",
              "run_event": "${{ github.event.workflow_run.event }}",
              "triggered_by": "${{ github.event.workflow_run.triggering_actor.login }}"
            }
```

Known open question for the ievo.ai slice (operator acceptance test 1): it is
NOT yet verified whether `workflow_run` events fire for the GitHub-managed
`pages-build-deployment` workflow — verify before wiring that repo, don't
assume.

#### Conflict scan (eva#211)

`eva-review-pr.yml` only fires on Tests completing, `ready_for_review`, or a
dispatch — none of which re-fire on a PR that goes `DIRTY` (a real merge
conflict) with no new push, so a stranded `eva-impl/*` PR was previously
invisible to every automation loop. `eva-conflict-scan.yml` sweeps the same
watch-list as `eva-queue.yml` on a 2h cron (deterministic `gh`/`git` queries,
no LLM agent — resolving a merge conflict is a mechanical git question, not a
judgment call) and for each `DIRTY` `eva-impl/*` PR either rebases it cleanly
onto current `main` and pushes (re-entering the normal review chain), or —
when git itself can't resolve it — closes the PR and re-adds `approved` to
the issue it closes for a fresh build. Bounded by
`EVA_CONFLICT_SCAN_MAX_ACTIONS` per run and double-gated live like
`eva-queue.yml` (dry_run + `EVA_CONFLICT_SCAN_ENABLED`).

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
| `EVA_CI_WATCHDOG_ENABLED` | `true` / `false` | Safety valve for `eva-ci-failure.yml` (eva#159) — merged dormant, the operator flips it after the acceptance smoke tests |
| `EVA_CONFLICT_SCAN_ENABLED` | `true` / `false` | Safety valve for `eva-conflict-scan.yml` (eva#211) — gates BOTH the cron and a manual `dry_run=false` dispatch; merged dormant, flip to `true` to arm live runs (optionally smoke-test with one manual dispatch right after) |
| `EVA_CONFLICT_SCAN_MAX_ACTIONS` | integer (default `7`) | Per-run cap on rebase/close actions in `eva-conflict-scan.yml` |

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
| `EVA_MODEL_PUBLISH` | `haiku` | publish-evolution blurb (model only) |
| `EVA_MODEL_CI_WATCHDOG` | `sonnet` | eva-ci-failure (CI-failure triage) |
| `EVA_EFFORT_CI_WATCHDOG` | `high` | eva-ci-failure |

`high` is also the current model-default effort for the `opus` (Opus 4.8) and
`sonnet` (Sonnet 5) aliases, so the effort defaults are behavior-preserving — they
pin what the CLI already used implicitly. Effort is deliberately not parametrized
for `eva-research` / `publish-evolution` (model only). To try Fable, set the
relevant `EVA_MODEL_*` to `fable` (or `claude-fable-5`).

### Per-issue model escalation (eva#172)

The variables above are **global** — they flip a whole flow for every run. For a
finer lever, a single issue can be escalated to Fable without touching anyone
else's builds. Two paths feed the same resolution:

**Manual (label).** A collaborator labels an issue `model:fable` (and optionally
`effort:xhigh`). `eva-implement` reads the label at claim time and resolves the
build's model/effort as **label > repo variable > default**; `eva-fix-pr`
inherits the same escalation for its fix rounds by reading the label off the
issue the PR closes. Labels are collaborator-only (same trust boundary as
`approved`), so this is not an external cost-escalation vector.

- **Whitelist**: only `model:opus` / `model:fable` and
  `effort:{low,medium,high,xhigh,max}` are honoured. Any other `model:*`/`effort:*`
  label value is ignored (the flow falls back to variable → default) and a notice
  is posted on the issue. No free-form label text ever reaches the CLI invocation.

**Router auto-selection (autonomous).** At verdict time the Issue Router
(`eva-on-issue`) MAY apply `model:fable` itself, but only when the task is BOTH
**reasoning-heavy** (root-cause hunt, security/invariant design, cross-system
interaction) AND **narrow-surface** (≤~3 files, no sweeping edit). A
reasoning-heavy but WIDE task must be **split**, never escalated — Fable + volume
times out (the eva#159 50-min kill). The Router states the decision in its
analysis comment so it is auditable, and is bounded by:

- **Daily budget**: max 3 Router-applied `model:fable` builds per repo per 24h,
  counted statelessly from `model:fable` label-events whose actor is
  `ievo-eva[bot]` (the same pattern as the Skeptic-mode self-approve cap).
  Operator-applied labels do not count against it.
- **Operator label wins**: if a human applied or removed a `model:*` label, the
  Router never overrides it (same semantics as "the Router can never resurrect a
  terminal verdict"). The Router applies its label via the App token so its
  actor (`ievo-eva[bot]`) is distinguishable from a human's.

Because these workflow files are a sensitive path, a change to them still routes
the merge to the operator; the escalation labels themselves need no such gate.

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
