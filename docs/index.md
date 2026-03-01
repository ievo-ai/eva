# iEvo — Self-Evolving AI Agent Framework

A multi-agent Spec-Driven Development (SDD) framework where AI agents write specs, plan architecture, implement code via strict TDD, and evolve from their mistakes.

## Agent Pipeline

```
User (Product Owner)
  ↓ free-form description
Spec Writer → REQ-xxx.md (atomic requirements)
  ↓ human reviews & approves
Architect → PLAN-REQ-xxx.md (implementation plan)
  ↓
Coder → code + tests (strict TDD)
```

## 3-Tier Evolution

| Level | Scope | Mechanism |
|-------|-------|-----------|
| **EVO** | Single agent | Error → classify → mutate ROLE.md |
| **Curator** | Marketplace | Cross-agent pattern → shared skill |
| **Eva** | Platform | Ecosystem observation → PRs to any repo |

## Ecosystem

| Repo | Purpose |
|------|---------|
| [**eva**](architecture.md) | Mother repo + platform-level evolution engine |
| [**cli**](ecosystem/cli.md) | `ievo` CLI + TUI dashboard |
| [**marketplace**](ecosystem/marketplace.md) | Agent registry — spec-writer, architect, coder, researcher |
| [**sdk**](ecosystem/sdk.md) | Agent development kit |
| [**curator**](ecosystem/curator.md) | Cross-agent pattern curator |

## Quick Start

```bash
# Install the CLI
pip install ievo-cli

# Create a project and add agents
ievo init my-project && cd my-project
ievo add spec-writer architect coder

# Start a spec writing session
ievo run spec-writer -m "Let's design a REST API for user management"

# Automated coding loop
ievo orchestrate --max 5 --agent coder
```

See [Getting Started](getting-started.md) for a full walkthrough.
