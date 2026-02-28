# Eva — Meta-Evolution Mother Agent

Third level of iEvo evolution. Observes platform → detects patterns → proposes mutations.

## Project

- **Name**: ievo-eva
- **Language**: Python 3.10+
- **Framework**: Click (CLI) + httpx (async sources) + Rich (output)
- **Package manager**: uv (hatchling build)
- **Entry point**: `eva` → `src/eva/cli.py`

## Architecture

```
src/eva/
├── cli.py              # Click CLI (scan, status, init, approve)
├── pipeline.py         # Main OBSERVE → ANALYZE → MUTATE loop
├── core/
│   ├── config.py       # EvaConfig, SourceConfig — loaded from eva.yaml
│   └── models.py       # Signal, Pattern, Mutation domain models
├── sources/            # Signal connectors (all async)
│   ├── base.py         # BaseSource ABC
│   ├── sentry.py       # Sentry error tracking
│   ├── github_issues.py # GitHub Issues across repos
│   ├── evolution_logs.py # Agent EVOLUTION_LOG.md files
│   └── reviews.py      # PR comments and reviews
├── analysis/
│   └── detector.py     # PatternDetector — frequency, cross-agent, escalation
└── mutations/
    └── engine.py       # MutationEngine — pattern → concrete file changes

agent/                  # Eva's own agent identity
├── agent.yaml          # Package manifest (opus tier)
├── ROLE.md             # Eva's instructions
├── EVOLUTION_LOG.md    # Self-evolution history
├── memory/             # Context, decisions, vocabulary, history
└── skills/evo/SKILL.md # Eva's self-evolution skill

tests/                  # 14 tests
├── test_config.py
├── test_detector.py
├── test_models.py
└── test_mutations.py
```

## Key patterns

- **Pipeline**: `EvaPipeline.run()` — single async method executing full cycle
- **Sources**: All implement `BaseSource` ABC with `poll()` and `healthcheck()`
- **Detection strategies**: Frequency (recurring titles), Cross-agent (shared tags), Escalation (severity trending up)
- **Mutations**: Pattern → Mutation mapping with confidence scoring and rate limiting
- **Safety**: dry-run default, never auto-merge, max 5 mutations/run, confidence threshold 30%

## Commands

```bash
eva init                     # Generate default eva.yaml
eva scan                     # Run one cycle (dry-run)
eva scan --marketplace DIR   # Include evo logs from marketplace
eva scan --live              # Create real PRs
eva status                   # Show config and source health
eva approve <mutation-id>    # Approve a mutation (Phase 2)
```

## Env vars

- `EVA_GITHUB_TOKEN` — GitHub API access (issues, PRs, reviews)
- `EVA_SENTRY_TOKEN` — Sentry API access

## Three evolution levels

| Level | Scope | Mechanism |
|-------|-------|-----------|
| EVO | Single agent | Error → classify → mutate ROLE.md |
| Curator | Marketplace | Cross-agent pattern → shared skill (Phase 3) |
| Eva | Platform | Ecosystem observation → PRs to any repo |

## Related repos

- [ievo-ai/cli](https://github.com/ievo-ai/cli)
- [ievo-ai/marketplace](https://github.com/ievo-ai/marketplace)
- [ievo-ai/sdk](https://github.com/ievo-ai/sdk)
- [ievo.ai](https://ievo.ai)
