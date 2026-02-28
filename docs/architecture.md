# Architecture

## Overview

Eva is the **meta-evolution mother agent** — the third and highest level of evolution in the iEvo ecosystem. She observes the entire platform (Sentry errors, GitHub issues, PR reviews, agent evolution logs) and proposes targeted improvements as Pull Requests.

Eva does not write specs, plans, or code directly. She is a **genetic algorithm applied at the platform level**: detecting patterns across all signals and proposing atomic mutations.

## Three Evolution Levels

```
EVO (local) → Curator (collective) → Eva (meta/platform)
```

| Level | Scope | Agent | Mechanism |
|-------|-------|-------|-----------|
| **EVO** | Single agent | Each agent (skill) | Error → classify → mutate ROLE.md |
| **Curator** | Marketplace | Phase 3 (planned) | Cross-agent pattern → shared skill update |
| **Eva** | Platform | Eva (this repo) | Ecosystem observation → PRs to any repo |

**EVO** is embedded inside every agent as a skill. When an agent encounters an error, EVO classifies it, updates the agent's ROLE.md with a new rule, and logs the mutation to `EVOLUTION_LOG.md`. Fully autonomous, fully local.

**Curator** (Phase 3) will detect patterns spanning multiple agents — e.g. the same class of error in 3 different agents — and propose updates to shared skills or marketplace templates.

**Eva** operates at the highest level, polling external sources and combining them with internal evolution logs to detect platform-wide patterns.

## Data Flow

```
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
                                                           │
                                                           ▼
                                                      Merge / Reject
```

## Key Principles

- **Stateless pipeline** — Each run is independent. Eva reads current state, analyzes, and proposes. No persistent state between runs (everything is in Git).
- **Source abstraction** — Every source implements `BaseSource` with `poll()` and `healthcheck()`. Adding a new source = implementing 2 methods.
- **Pattern strategies** — Detection strategies are independent and composable. Each strategy (frequency, cross-agent, escalation) runs on the full signal set.
- **Mutation templates** — The engine generates PR-ready diffs with full context. Each mutation targets a specific file in a specific repo.
- **Safety first** — Dry-run by default, never auto-merge, rate limited, confidence thresholds.

## Domain Models

Three core dataclasses in `eva.core.models`:

### Signal

The fundamental unit of observation. Every piece of data from any source is normalized into a Signal:

```python
@dataclass
class Signal:
    id: str                    # Unique identifier
    type: SignalType           # sentry_error, github_issue, user_review, etc.
    source: str                # e.g. "github:ievo-ai/cli#42"
    title: str                 # Human-readable title
    body: str                  # Full content
    severity: Severity         # CRITICAL, HIGH, MEDIUM, LOW, INFO
    timestamp: datetime        # When created/last updated
    metadata: dict[str, Any]   # Source-specific data
    tags: list[str]            # Classification tags
```

### Pattern

Emerges when the detector finds recurring themes:

```python
@dataclass
class Pattern:
    id: str                    # e.g. "freq:cli-crashes", "cross:timeout"
    title: str                 # Human-readable description
    signal_ids: list[str]      # Contributing signal IDs
    frequency: int             # Number of occurrences
    severity: Severity         # Max severity among signals
    affected_agents: list[str] # Which agents are affected
    confidence: float          # 0.0–1.0
```

### Mutation

A concrete proposed change ready for a Pull Request:

```python
@dataclass
class Mutation:
    id: str                    # e.g. "mut-0001"
    type: MutationType         # ROLE_PATCH, SKILL_PATCH, MEMORY_UPDATE, etc.
    target_repo: str           # e.g. "ievo-ai/marketplace"
    target_path: str           # e.g. "agents/spec-writer/ROLE.md"
    diff: str                  # Unified diff or full new content
    pattern_id: str            # Pattern that triggered this
    confidence: float          # Inherited from pattern
    approved: bool             # Human approval status
```

## Project Structure

```
eva/
├── src/eva/
│   ├── core/
│   │   ├── config.py          # EvaConfig, SourceConfig
│   │   └── models.py          # Signal, Pattern, Mutation
│   ├── sources/
│   │   ├── base.py            # BaseSource ABC
│   │   ├── sentry.py          # Sentry error tracking
│   │   ├── github_issues.py   # GitHub Issues polling
│   │   ├── reviews.py         # PR review comments
│   │   └── evolution_logs.py  # Agent EVOLUTION_LOG.md parser
│   ├── analysis/
│   │   └── detector.py        # PatternDetector (3 strategies)
│   ├── mutations/
│   │   └── engine.py          # MutationEngine
│   ├── pipeline.py            # EvaPipeline (orchestrator)
│   └── cli.py                 # Click CLI
├── agent/                     # Eva's own agent identity
│   ├── agent.yaml
│   ├── ROLE.md
│   ├── memory/
│   └── skills/evo/SKILL.md
├── .github/workflows/         # GitHub Actions
├── docs/                      # This documentation
├── tests/                     # 14 pytest tests
├── eva.yaml                   # Configuration
├── Dockerfile                 # Container image
└── docker-compose.yml         # Self-hosted deployment
```
