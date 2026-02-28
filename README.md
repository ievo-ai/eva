# Eva — Meta-Evolution Mother Agent

Eva is the third level of evolution in the iEvo ecosystem. She observes the entire platform — Sentry errors, GitHub issues, user reviews, agent evolution logs — and proposes targeted improvements as Pull Requests.

```
EVO (local) → Curator (collective) → Eva (meta/platform)
```

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

## Safety

- **Dry-run by default** — `--live` required for real PRs
- **Never auto-merge** — every mutation needs human approval
- **Rate limited** — max 5 mutations per run
- **Confidence threshold** — below 30% = flagged only, not proposed
- **Atomic changes** — one concern per mutation

## Related

- [ievo-ai/cli](https://github.com/ievo-ai/cli) — CLI tool
- [ievo-ai/marketplace](https://github.com/ievo-ai/marketplace) — Agent registry
- [ievo-ai/sdk](https://github.com/ievo-ai/sdk) — Developer toolkit
- [ievo.ai](https://ievo.ai) — Project homepage
