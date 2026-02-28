# iEvo — Global Project Context

Eva is the mother repo for the iEvo ecosystem. This CLAUDE.md contains both global project context and Eva-specific details.

## iEvo Ecosystem

| Repo | Purpose | Key Files |
|------|---------|-----------|
| **eva** (this) | Mother repo, platform-level evolution | src/eva/, agent/, docs/ |
| **cli** | `ievo` CLI + TUI dashboard | src/ievo/commands/, src/ievo/tui/ |
| **marketplace** | Agent registry (spec-writer, architect, coder) | agents/*/ROLE.md, registry.yaml |
| **sdk** | Agent development kit | src/ievo_sdk/scaffold/ |
| **curator** | Cross-agent pattern curator | src/curator/pipeline.py |
| **ievo.ai** | Landing page | docs/index.html |

## SDD Pipeline

```
User → Spec Writer → REQ-xxx.md → Architect → PLAN-REQ-xxx.md → Coder → code + tests (TDD)
```

Key concepts:
- **Atomic REQs**: 3-7 testable acceptance criteria each
- **Priority scoring**: formula in PRIORITY.md, agents auto-select highest-value task
- **Change Requests**: modifications with impact analysis + cascade safety
- **3-tier evolution**: EVO (local) → Curator (cross-agent) → Eva (platform)
- **Persistent memory**: agents maintain CONTEXT, DECISIONS, VOCABULARY, HISTORY across sessions

## Global Docs (in this repo)

| File | Contents |
|------|----------|
| `docs/global-architecture.md` | Full iEvo system design (ADR) |
| `docs/research/competitive-analysis.md` | 8 competing frameworks analysis |
| `docs/research/roadmap.md` | Phase 2-4 plans and deferred tasks |
| `docs/getting-started.md` | First Spec Writer session guide |

---

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

Dockerfile              # Python 3.12-slim, entrypoint: eva scan
docker-compose.yml      # Self-hosted deployment with volumes
.github/workflows/
├── eva-scan.yml        # Cron (6h) + manual trigger, Docker-based
├── eva-on-issue.yml    # Triggered by new issues (direct + cross-repo dispatch)
├── publish-evolution.yml # Push merged mutation to ievo.ai evolutions feed
└── tests.yml           # CI: lint + test on Python 3.10/3.11/3.12
scripts/
├── notify-eva.yml      # Template workflow for other repos to trigger Eva
└── publish-evolution.py # Append entry to evolutions.json
```

## Key patterns

- **Pipeline**: `EvaPipeline.run()` — single async method executing full cycle
- **Sources**: All implement `BaseSource` ABC with `poll()` and `healthcheck()`
- **Detection strategies**: Frequency (recurring titles), Cross-agent (shared tags), Escalation (severity trending up)
- **Mutations**: Pattern → Mutation mapping with confidence scoring and rate limiting
- **Safety**: dry-run default, never auto-merge, max 5 mutations/run, confidence threshold 30%
- **Evolutions feed**: Merged mutations → `publish-evolution.yml` → `ievo.ai/docs/evolutions.json` → site renders live

## Commands

```bash
eva init                     # Generate default eva.yaml
eva scan                     # Run one cycle (dry-run)
eva scan --marketplace DIR   # Include evo logs from marketplace
eva scan --live              # Create real PRs
eva status                   # Show config and source health
eva approve <mutation-id>    # Approve a mutation (Phase 2)
```

## Deployment

- **GitHub Actions**: cron (6h), on-issue (cross-repo dispatch), manual
- **Docker**: `docker build -t eva . && docker run eva scan`
- **Self-hosted**: `docker compose up -d` (uses .env for tokens)
- All workflows use Docker for reproducible environment

## Env vars

- `EVA_GITHUB_TOKEN` — GitHub API access (issues, PRs, reviews)
- `EVA_SENTRY_TOKEN` — Sentry API access

## Three evolution levels

| Level | Scope | Mechanism |
|-------|-------|-----------|
| EVO | Single agent | Error → classify → mutate ROLE.md |
| Curator | Marketplace | Cross-agent pattern → shared skill (`ievo-ai/curator`) |
| Eva | Platform | Ecosystem observation → PRs to any repo |

## Documentation

Detailed technical docs live in `docs/`:

| File | Contents |
|------|----------|
| `docs/architecture.md` | System design, 3 evolution levels, domain models, project structure |
| `docs/pipeline.md` | OBSERVE → ANALYZE → MUTATE phases, confidence formulas, dry-run vs live |
| `docs/sources.md` | All 4 signal sources (Sentry, Issues, Reviews, Evo Logs), how to add new |
| `docs/configuration.md` | eva.yaml reference, env variables, secrets |
| `docs/deployment.md` | GitHub Actions, Docker, cross-repo triggers, live mode |
| `docs/safety.md` | 8 safety rules, confidence thresholds, failure modes |
| `docs/GITHUB_APP_SETUP.md` | Step-by-step GitHub App setup |

Root `README.md` is the public-facing overview for GitHub. `docs/` is the full reference.

## Documentation standard (all iEvo repos)

Every ievo-ai/* repo MUST follow this structure:

```
repo/
├── README.md          # Public overview (GitHub landing page)
├── CLAUDE.md          # AI context (this file)
└── docs/              # Detailed technical documentation
    ├── architecture.md
    ├── ...
    └── (topic).md
```

Rules:
- `README.md` = concise overview, install, quick start, links to docs/
- `CLAUDE.md` = project context for AI agents, links to docs/
- `docs/` = deep reference docs, one file per topic, no README.md inside (root README links here)
- No duplicate content between README.md and docs/ — README summarizes, docs/ explains

This applies to: cli, marketplace, sdk, eva, curator, ievo.ai

## Session log convention

Every working session with Denis MUST be logged in Eva's memory.

**Structure:**
```
agent/memory/
  HISTORY.md              ← lightweight index (table: #, date, topic, key outcome)
  sessions/
    001-initial-build.md  ← full session detail
    002-curator-build.md
    003-evolutions-feed.md
    ...
```

**HISTORY.md** is a table index only — one row per session, links to detail file.
Never put full session content in HISTORY.md.

**Session file naming**: `NNN-kebab-topic.md` (zero-padded 3 digits).

**Each session file must include**:
- Date + topic header
- Discussion summary (what was discussed, what decisions were made)
- What was built (files, repos affected)
- Decisions (reference DECISIONS.md IDs)
- Commits (hashes + descriptions)
- What's next (pending items)

**Language**: English only.

**When to write**: at the end of every session, or when Denis asks.

## Related repos

- [ievo-ai/cli](https://github.com/ievo-ai/cli)
- [ievo-ai/marketplace](https://github.com/ievo-ai/marketplace)
- [ievo-ai/sdk](https://github.com/ievo-ai/sdk)
- [ievo-ai/curator](https://github.com/ievo-ai/curator)
- [ievo.ai](https://ievo.ai)
