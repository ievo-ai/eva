# iEvo — Self-Evolving AI Agent Framework

A multi-agent Spec-Driven Development (SDD) framework where AI agents write specs, plan architecture, implement code via strict TDD, and evolve from their mistakes.

Eva is the mother repo — she hosts global documentation and the platform-level evolution engine.

## iEvo Ecosystem

| Repo | Purpose | Status |
|------|---------|--------|
| **eva** (this repo) | Mother repo + platform-level evolution | Phase 1 |
| **cli** | `ievo` CLI + TUI dashboard (Typer/Rich/Textual) | Phase 1 |
| **marketplace** | Agent registry — spec-writer, architect, coder | Phase 1 |
| **sdk** | Agent development kit (scaffold, test, publish) | Phase 1 |
| **curator** | Cross-agent pattern curator | Phase 1 |
| **skills** | iEvo plugin (Claude Code + Codex) — install/evolution/update commands, skills, agents | Phase 1 |
| **ievo.ai** | Landing page | Phase 1 |

## Quick Start

```bash
pip install ievo-cli
ievo init my-project && cd my-project
ievo add spec-writer architect coder
ievo run spec-writer -m "Let's design a REST API for user management"
ievo orchestrate --max 5 --agent coder
```

## Agent Pipeline

```
User (Product Owner)
  ↓ free-form description
Spec Writer → REQ-xxx.md (atomic requirements)
  ↓ human reviews & approves
Architect → PLAN-REQ-xxx.md (implementation plan)
  ↓
Coder → code + tests (strict TDD)
  ↓
Tester → integration/acceptance (Phase 2)
  ↓
Reviewer → code quality (Phase 4)
```

## 3-Tier Evolution

```
EVO (local) → Curator (collective) → Eva (meta/platform)
```

| Level | Scope | Mechanism |
|-------|-------|-----------|
| EVO | Single agent | Error → classify → mutate ROLE.md |
| Curator | Marketplace | Cross-agent pattern → shared skill |
| Eva | Platform | Ecosystem observation → PRs to any repo |

## Documentation

**Full docs**: [ievo-ai.github.io/eva](https://ievo-ai.github.io/eva/)

- [Getting Started](https://ievo-ai.github.io/eva/getting-started/) — first Spec Writer session
- [Global Architecture](https://ievo-ai.github.io/eva/global-architecture/) — full system design
- [Competitive Analysis](https://ievo-ai.github.io/eva/research/competitive-analysis/) — 8 frameworks compared
- [Roadmap](https://ievo-ai.github.io/eva/research/roadmap/) — Phase 2-4 plans

---

# Eva — Meta-Evolution Engine

Eva is the third level of evolution in the iEvo ecosystem. She observes the entire platform — Sentry errors, GitHub issues, user reviews, agent evolution logs — and proposes targeted improvements as Pull Requests.

## Pipeline

```
OBSERVE → ANALYZE → MUTATE → REVIEW → MERGE

┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
│   Sources    │───▶│  Signals  │───▶│ Patterns  │───▶│ Mutations│
│ Sentry       │    │ normalized│    │ frequency │    │ PR-ready │
│ GitHub Issues│    │ stream    │    │ cross-agnt│    │ patches  │
│ Evo Logs     │    │           │    │ escalation│    │          │
│ Reviews      │    │           │    │           │    │          │
└─────────────┘    └───────────┘    └───────────┘    └──────────┘
                                                           │
                                                           ▼
                                                     Human Review
```

## Install

```bash
# uv
uv pip install -e ".[dev]"

# pip
pip install -e ".[dev]"
```

## Commands

```bash
# Initialize config
eva init

# Run one scan cycle (dry-run by default)
eva scan

# Run with marketplace integration
eva scan --marketplace ../marketplace

# Go live (creates PRs)
eva scan --live

# Check status
eva status
```

## Configuration

Eva reads `eva.yaml`:

```yaml
repos:
  cli: ievo-ai/cli
  marketplace: ievo-ai/marketplace
  sdk: ievo-ai/sdk

sources:
  sentry:
    enabled: false
  github_issues:
    enabled: true
  reviews:
    enabled: false
  evolution_logs:
    enabled: true

dry_run: true
max_mutations_per_run: 5
auto_merge: false
```

Set tokens via environment:
```bash
export EVA_GITHUB_TOKEN=ghp_...
export EVA_SENTRY_TOKEN=...
```

## Deployment

### GitHub Actions (recommended)

Eva runs automatically via GitHub Actions — zero infrastructure needed:

| Trigger | Workflow | When |
|---------|----------|------|
| Cron | `eva-scan.yml` | Every 6 hours |
| Issue | `eva-on-issue.yml` | New issue in any iEvo repo |
| Manual | `eva-scan.yml` | `workflow_dispatch` button |
| CI | `tests.yml` | Every push/PR |

Required secrets in GitHub repo settings:
```
EVA_GITHUB_TOKEN — GitHub PAT (issues, PRs read)
EVA_SENTRY_TOKEN — Sentry auth token (optional)
```

Cross-repo triggers: copy `scripts/notify-eva.yml` to other iEvo repos.

### Docker (self-hosted)

```bash
# One-shot scan
docker build -t eva .
docker run --rm -e EVA_GITHUB_TOKEN=ghp_... eva scan

# Persistent with docker-compose
cp .env.example .env    # fill tokens
docker compose up -d    # runs Eva
docker compose logs -f  # watch
```

### Both: GitHub Actions + Docker

The GitHub Actions workflows build and run the Docker container. Same image works everywhere — CI, local, VPS, k8s.

## Safety

- **Dry-run by default** — `--live` required for real PRs
- **Never auto-merge** — every mutation needs human approval
- **Rate limited** — max 5 mutations per run
- **Confidence threshold** — below 30% = flagged only, not proposed
- **Atomic changes** — one concern per mutation
- **Bot loop prevention** — ignores issues from `github-actions[bot]`

## Eva Documentation

Full technical docs at [ievo-ai.github.io/eva](https://ievo-ai.github.io/eva/) or in [`docs/`](docs/):

- [Architecture](docs/architecture.md) — system design, evolution levels, domain models
- [Pipeline](docs/pipeline.md) — OBSERVE → ANALYZE → MUTATE in detail
- [Sources](docs/sources.md) — Sentry, GitHub Issues, Reviews, Evolution Logs
- [Configuration](docs/configuration.md) — eva.yaml reference, env variables
- [Deployment](docs/deployment.md) — GitHub Actions, Docker, cross-repo triggers
- [Safety](docs/safety.md) — safety rules, confidence thresholds, failure modes
- [GitHub App Setup](docs/GITHUB_APP_SETUP.md) — step-by-step auth setup

## Related

- [ievo-ai/cli](https://github.com/ievo-ai/cli) — CLI tool
- [ievo-ai/marketplace](https://github.com/ievo-ai/marketplace) — Agent registry
- [ievo-ai/sdk](https://github.com/ievo-ai/sdk) — Developer toolkit
- [ievo.ai](https://ievo.ai) — Project homepage
<!-- Eva PR Review smoke test 2026-05-23 -->
