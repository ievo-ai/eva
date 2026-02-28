# iEvo — Architecture Decision Record

**Date**: 2026-02-27 (updated)
**Status**: Accepted
**Authors**: Denis + Claude

---

## 1. What We're Building

**iEvo** (ievo.ai) — self-evolving multi-agent SDD framework with agent marketplace.

Three separate repos:

```
ievo-marketplace/      → Repo с готовыми агентами (spec-writer, architect, coder...)
ievo-sdk/              → Dev SDK + Copier template для создания новых агентов
ievo-cli/              → CLI (`ievo init`, `ievo add`, `ievo learn`)
```

**Not another orchestrator.** We build:
1. **SDD methodology** — Spec → REQs → Priority → Plan → TDD → Gate
2. **Agent marketplace** — `ievo add spec-writer` pulls from registry
3. **Self-evolution** — agents learn from mistakes via EVO skill, feed back to marketplace

```
┌─────────────────────────────────────────────────────┐
│               iEvo ECOSYSTEM                       │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │  Marketplace  │  │   Dev SDK    │  │   CLI     │ │
│  │  (agents)     │  │   (Copier)   │  │  (ievo)  │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                  │                │       │
│         ▼                  ▼                ▼       │
│  ┌─────────────────────────────────────────────┐    │
│  │           SDD METHODOLOGY LAYER             │    │
│  │  Spec → Atomic REQs → Priority → Plan →     │    │
│  │  TDD → Gate → EVO feedback loop             │    │
│  └─────────────────────────────────────────────┘    │
│                        │                             │
│  ┌─────────────────────────────────────────────┐    │
│  │         EXECUTION ENGINE (pick one)          │    │
│  │  Claude Agent Teams │ Claude Code │ Manual   │    │
│  └─────────────────────────────────────────────┘    │
│                        │                             │
│  ┌─────────────────────────────────────────────┐    │
│  │              FOUNDATION                      │    │
│  │  Claude API │ MCP Servers │ File System │ Git│    │
│  └─────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 2. iEvo Marketplace (ievo-marketplace repo)

### Agent Package Structure

```
ievo-marketplace/
├── registry.yaml              # Index of all agents, versions, deps
├── agents/
│   ├── spec-writer/
│   │   ├── agent.yaml         # Metadata, version, dependencies, model tier
│   │   ├── ROLE.md            # Agent instructions (progressive disclosure)
│   │   ├── memory/            # Empty memory templates
│   │   │   ├── CONTEXT.md
│   │   │   ├── DECISIONS.md
│   │   │   ├── VOCABULARY.md
│   │   │   └── HISTORY.md
│   │   ├── skills/            # Agent-specific skills
│   │   │   └── evo/           # Self-evolution skill
│   │   │       └── SKILL.md
│   │   ├── templates/         # Spec templates (for spec-writer)
│   │   │   ├── REQUIREMENT_TEMPLATE.md
│   │   │   └── QUESTION_TEMPLATE.md
│   │   ├── mcp.json           # MCP servers this agent needs
│   │   └── plugins.json       # Claude Code plugins this agent uses
│   │
│   ├── architect/
│   │   ├── agent.yaml
│   │   ├── ROLE.md
│   │   ├── memory/
│   │   ├── skills/
│   │   │   └── evo/
│   │   └── mcp.json
│   │
│   ├── coder/
│   ├── tester/
│   ├── reviewer/
│   ├── pm/
│   │
│   └── domain/                # Domain-specific agents
│       ├── medical-researcher/
│       │   ├── agent.yaml     # deps: [spec-writer], mcp: pubmed
│       │   ├── ROLE.md
│       │   └── mcp.json       # → @cyanheads/pubmed-mcp-server
│       ├── unity-developer/
│       ├── devops/
│       └── security-officer/
```

### agent.yaml Format

```yaml
name: spec-writer
version: 0.1.0
description: "Requirements analyst — converts features into atomic, testable specs"
author: ievo-team

# Model routing
model:
  primary: sonnet    # Main work
  fallback: haiku    # Simple tasks (formatting, indexing)

# Dependencies — auto-installed
dependencies: []     # spec-writer has no deps
# Example: coder depends on architect
# dependencies:
#   - architect@>=0.1.0

# Required MCP servers
mcp:
  - name: filesystem
    builtin: true
  # Example for domain agent:
  # - name: pubmed
  #   package: "@cyanheads/pubmed-mcp-server"
  #   config_required: true   # Will prompt for API key on install

# Required Claude Code plugins
plugins: []

# Skills included
skills:
  - evo                  # Self-evolution (all agents get this)

# Lifecycle hooks
hooks:
  on_install: null       # Run after ievo add
  on_session_start: "load_memory"    # Read memory files
  on_session_end: "save_memory"      # Write memory files
  on_error: "evo_analyze"            # Trigger EVO skill

# Progressive disclosure tiers
disclosure:
  metadata: 100          # Always loaded (tokens)
  instructions: 400      # On activation
  resources: 600         # On demand
```

### Install Flow

```bash
ievo add spec-writer
# 1. Reads registry.yaml, finds spec-writer@0.1.0
# 2. Checks dependencies → none
# 3. Downloads agent package to project's agents/ dir
# 4. Creates empty memory files
# 5. Installs MCP servers if needed (prompts for API keys)
# 6. Done: "✓ spec-writer@0.1.0 installed"

ievo add medical-researcher
# 1. Reads registry.yaml
# 2. Checks dependencies → requires spec-writer
#    → spec-writer already installed ✓
# 3. Downloads agent package
# 4. MCP: pubmed requires API key
#    → "Enter PubMed API key: ___"
# 5. Done: "✓ medical-researcher@0.1.0 installed"
```

---

## 3. Dev SDK (ievo-sdk repo)

For developers creating new agents for the marketplace.

```
ievo-sdk/
├── copier.yml                 # Copier template config
├── template/
│   ├── {{agent_name}}/
│   │   ├── agent.yaml.jinja
│   │   ├── ROLE.md.jinja
│   │   ├── memory/
│   │   │   ├── CONTEXT.md
│   │   │   ├── DECISIONS.md
│   │   │   ├── VOCABULARY.md
│   │   │   └── HISTORY.md
│   │   ├── skills/
│   │   │   └── evo/
│   │   │       └── SKILL.md   # EVO skill (always included)
│   │   ├── mcp.json.jinja
│   │   └── plugins.json.jinja
│   └── tests/                 # Agent evaluation tests
│       └── test_{{agent_name}}.py.jinja
├── docs/
│   ├── CREATING_AGENTS.md
│   ├── PUBLISHING.md
│   └── BEST_PRACTICES.md
└── examples/
    └── hello-world-agent/
```

### Creating a New Agent

```bash
# Step 1: Scaffold from template
copier copy gh:ievo-ai/ievo-sdk my-agent

# Questions:
# Agent name? → security-auditor
# Description? → Reviews code for security vulnerabilities
# Model tier? → opus (critical decisions)
# Needs MCP servers? → yes
#   Which? → semgrep, snyk
# Dependencies? → coder

# Step 2: Edit ROLE.md with agent instructions
# Step 3: Test locally
ievo test security-auditor

# Step 4: Publish to marketplace
ievo publish security-auditor
```

---

## 4. EVO: Self-Evolution System

### How It Works

Every agent gets the EVO skill. When an agent makes a mistake:

```
┌─────────┐    /evo or     ┌──────────┐    lesson    ┌──────────────┐
│  Agent   │───auto-detect──│ EVO Skill │────────────│ ROLE.md      │
│  Error   │    on_error    │ (analyze) │            │ (updated)    │
└─────────┘                 └────┬─────┘            └──────────────┘
                                 │
                                 ▼
                         ┌──────────────┐
                         │ EVOLUTION_   │
                         │ LOG.md       │
                         │ (append)     │
                         └──────────────┘
```

### EVO Skill (included in every agent)

```markdown
## EVO Workflow
1. Identify error (user feedback, /evo command, or on_error hook)
2. Classify: code / process / communication / safety / style
3. Root cause analysis — what assumption was wrong?
4. Formulate actionable rule
5. Propose update to ROLE.md (get user approval)
6. Apply update
7. Log to EVOLUTION_LOG.md (Context / Action / Goal format)
8. Confirm understanding
```

### EVOLUTION_LOG.md Format

```markdown
## 2026-02-28: Spec Writer assumed tech stack without asking

**Context:** User described feature "add OAuth". Spec Writer wrote REQ
assuming Node.js + Passport.js. Project uses Python + FastAPI.

**Action:** Added rule to ROLE.md Section "STRICT RULES":
"NEVER assume tech stack. Check CONTEXT.md or ask user."

**Goal:** Prevent spec-writer from making tech-specific assumptions
that don't match the project.
```

### Collective Evolution: Feedback Loop to Marketplace

```
Project A: spec-writer EVOLUTION_LOG.md ──┐
Project B: spec-writer EVOLUTION_LOG.md ──┼──→ REST API ──→ Curator Agent
Project C: spec-writer EVOLUTION_LOG.md ──┘       │
                                                    ▼
                                           ┌──────────────┐
                                           │ Curator reads │
                                           │ all logs for  │
                                           │ spec-writer   │
                                           │               │
                                           │ Finds pattern:│
                                           │ 7/10 projects │
                                           │ same mistake  │
                                           │               │
                                           │ Updates agent  │
                                           │ in marketplace │
                                           └──────────────┘
                                                    │
                                                    ▼
                                          ievo update spec-writer
                                          (all projects get fix)
```

### Curator Agent

Lives in the marketplace repo. Periodically:
1. Reads EVOLUTION_LOGs from REST endpoint (anonymized, opt-in)
2. Groups by agent_name
3. Finds recurring patterns (>N projects, same error class)
4. Proposes ROLE.md update for marketplace agent
5. Creates PR in ievo-marketplace repo
6. Maintainer reviews & merges
7. `ievo update` pulls new version to projects

### Genetic Testing of Evolved Agents (Phase 3+)

**Problem**: After EVO mutates ROLE.md, how do we know it got better, not worse?

**Solution**: Genetic algorithm applied to agent evolution.

```
Mapping:
  Genome         = ROLE.md (set of rules/instructions)
  Mutation       = EVO change (add/modify/remove rule)
  Population     = variants of same agent from different projects
  Fitness func   = eval suite score (test scenarios → pass/fail/quality)
  Selection      = keep mutations that improve fitness, rollback others
  Crossover      = Curator combines best rules from different variants
```

**Eval Suite per Agent** — set of test scenarios:

```yaml
# ievo-marketplace/agents/spec-writer/evals/
evals:
  - name: "handles vague input"
    input: "add OAuth"
    expect:
      - creates REQ with auth flows
      - asks about provider (Google, GitHub, etc.)
      - asks about tech stack if not in CONTEXT.md
    anti_patterns:
      - assumes specific framework
      - writes implementation details

  - name: "rejects untestable criteria"
    input: "system should be fast"
    expect:
      - asks for measurable criteria (latency, throughput)
      - does NOT write "system should be fast" as acceptance criterion
    anti_patterns:
      - accepts vague requirement without question

  - name: "respects existing decisions"
    setup:
      DECISIONS.md: "D-001: Using PostgreSQL, not MongoDB"
    input: "add user profiles with NoSQL storage"
    expect:
      - flags conflict with D-001
      - creates Q-xxx asking PO to resolve
    anti_patterns:
      - silently accepts NoSQL
      - ignores existing decision
```

**Genetic Cycle (Curator level)**:

```
1. Collect: EVOLUTION_LOGs from N projects
2. Group: mutations by agent (spec-writer has 47 mutations from 12 projects)
3. Evaluate: run each mutation through eval suite
   - Mutation A: fitness 0.85 → 0.92 (improvement ✓)
   - Mutation B: fitness 0.85 → 0.78 (regression ✗)
   - Mutation C: fitness 0.85 → 0.86 (marginal)
4. Select: keep A, discard B, flag C for review
5. Crossover: combine top mutations from different projects
   - Project X added rule about tech stack assumptions
   - Project Y added rule about dependency checking
   - → merge both into marketplace agent
6. Evaluate combined: run eval suite on merged ROLE.md
7. Publish: if fitness improved → new version in marketplace
   - ievo update spec-writer → all projects get improvements
```

**Rollback safety**: if `ievo update` pulls a new version and agent
performs worse in a specific project, local EVO can override marketplace
rules. Local ROLE.md changes always take precedence over marketplace defaults.

**Format**: eval files live alongside agent in marketplace repo.
Format TBD — YAML for scenarios, Python for complex assertions, or both.
Decide when we reach Phase 3.

---

## 5. Project Structure (after `ievo init`)

```
my-project/
├── CLAUDE.md                  # Project config (filled by spec-writer on first session)
├── PRIORITY.md                # Scoring algorithm
├── ievo.yaml                # Project manifest (installed agents, versions)
├── spec/
│   ├── SPEC_INDEX.md
│   ├── requirements/
│   ├── changes/
│   ├── questions/
│   └── templates/             # Copied from spec-writer package
├── plans/
├── agents/                    # Installed agents (from marketplace)
│   ├── spec-writer/           # Pulled by `ievo add`
│   │   ├── agent.yaml
│   │   ├── ROLE.md
│   │   ├── memory/            # Filled by agent during sessions
│   │   ├── skills/
│   │   └── EVOLUTION_LOG.md   # Grows over time
│   ├── architect/
│   └── coder/
└── .github/
    └── workflows/
```

### ievo.yaml (project manifest)

```yaml
project: my-project
version: 0.1.0
created: 2026-02-27

agents:
  spec-writer: 0.1.0
  architect: 0.1.0
  coder: 0.1.0

# Custom overrides per agent
overrides:
  coder:
    model:
      primary: opus    # Override: this project needs Opus for coder
```

---

## 6. CLI Commands (ievo-cli)

```bash
# Project lifecycle
ievo init                    # Create ievo.yaml, spec/, plans/
ievo add <agent>             # Pull agent from marketplace + deps
ievo remove <agent>          # Remove agent
ievo update [agent]          # Update agent(s) to latest marketplace version
ievo list                    # Show installed agents

# Running agents
ievo run <agent> [message]   # Start agent session (interactive)
ievo run <agent> -p <file>   # Feed file as input (batch)
ievo team <agents...>        # Run Agent Teams with specified agents

# Self-evolution
ievo learn [agent]             # Trigger EVO analysis for last error
ievo learn log [agent]         # Show evolution history
ievo learn push                # Send anonymized logs to REST API (opt-in)

# Development (for agent creators)
ievo dev new                 # Scaffold new agent (Copier)
ievo dev test <agent>        # Run agent evaluation tests
ievo dev publish <agent>     # Publish to marketplace
```

---

## 7. Onboarding Flow (PO → Spec Writer)

**Key insight**: Spec Writer is the entry point. No pre-warming needed.

```
ievo init
  → Creates empty project skeleton (ievo.yaml, spec/, plans/)

ievo add spec-writer
  → Pulls spec-writer from marketplace with empty memory

ievo run spec-writer
  → PO talks to Spec Writer naturally:
    "We're building a fintech app, Python + FastAPI, need OAuth..."
  → Spec Writer fills its OWN memory during conversation:
    - CONTEXT.md ← project description, stack, constraints
    - VOCABULARY.md ← terms PO uses (fintech jargon, internal names)
    - DECISIONS.md ← decisions PO confirms ("yes, JWT not sessions")
    - HISTORY.md ← summary of this onboarding session
  → Also creates first REQ files
  → Also fills CLAUDE.md (project-level config)
```

**No separate onboarding agent.** Spec Writer's conversation mode IS onboarding.
The first session is both "get to know the project" and "start writing specs".

---

## 8. What We Take From Whom

| Source | What We Take | Where It Goes |
|--------|--------------|---------------|
| **wshobson/agents** | 3-tier model routing, progressive disclosure, plugin format | agent.yaml, ROLE.md tiers |
| **claude-flow** | Context archival, importance ranking | Memory system Phase 2 (SQLite) |
| **OpenClaw** | Gateway pattern, lifecycle hooks, cron, selective skill injection | agent.yaml hooks, CLI routing |
| **Kiro IDE** | EARS notation for requirements | REQUIREMENT_TEMPLATE.md (evaluate) |
| **Claude Agent Teams** | Parallel agent execution | `ievo team` command |
| **Copier** | 3-way merge project templating | ievo-sdk (agent dev only) |
| **CrewAI** | Nothing (too abstract, memory resets) | — |

---

## 9. Model Cost Strategy

| Agent | Phase | Model | Cost/1M | Rationale |
|-------|-------|-------|---------|-----------|
| Spec Writer | Requirements | Sonnet | $3.00 | Good reasoning, not Opus-level |
| Architect | Planning | Opus | $15.00 | Critical decisions, security |
| Coder (impl) | Implementation | Sonnet | $3.00 | Follows plan |
| Coder (tests) | Test writing | Haiku | $0.80 | Deterministic: spec → assertions |
| Tester | Validation | Sonnet | $3.00 | Edge case reasoning |
| Reviewer | Quality | Opus | $15.00 | Must catch what others missed |
| PM | Dashboard | Haiku | $0.80 | Read statuses, format report |
| Curator | Evolution | Sonnet | $3.00 | Pattern matching across logs |

**Estimated savings vs all-Opus**: ~49%

---

## 10. Communication Protocols

**Now (Phase 0-1)**: File-based handoff
```
Spec Writer writes REQ-005.md → Architect reads → PLAN → Coder reads PLAN
```

**Future (Phase 3+)**: ACP (Agent Context Protocol)
```
Spec Writer --ACP--> Architect --ACP--> Coder
```

**Future (Phase 4)**: OpenClaw Gateway pattern for multi-channel input
```
Telegram → Gateway → Spec Writer
GitHub webhook → Gateway → Coder
Slack → Gateway → PM
```

---

## 11. Implementation Phases

### Phase 0: What We Have (DONE)
- ROLE.md for spec-writer, architect, coder
- Memory system (markdown)
- Spec templates
- Priority scoring

### Phase 1: Marketplace + CLI (NEXT)
1. ievo-marketplace repo — package spec-writer, architect, coder
2. agent.yaml format — metadata, deps, model tier, hooks
3. ievo-cli — `init`, `add`, `run`, basic commands
4. EVO skill — include in every agent
5. First real test: `ievo init` → `ievo add spec-writer` → `ievo run spec-writer`

### Phase 2: Dev SDK + Plugin Format
1. ievo-sdk repo — Copier template for new agents
2. `ievo dev new` / `ievo dev test` / `ievo dev publish`
3. Progressive disclosure in ROLE.md (3 tiers)
4. 3-tier model routing in ievo-cli

### Phase 3: Full Team + Evolution Loop
1. Tester, PM, Reviewer agents in marketplace
2. Curator agent for collective evolution
3. REST API for EVOLUTION_LOG collection
4. `ievo learn push` (opt-in telemetry)
5. ACP evaluation for agent-to-agent communication

### Phase 4: Scale + Multi-channel
1. Gateway pattern for Telegram/Slack/GitHub inputs
2. SQLite memory for long sessions
3. Cross-agent memory sharing
4. Domain agent marketplace (community contributions)

### Phase 5: Eva — the Mother Agent
1. Eva meta-agent that scans external signals (Sentry, GitHub Issues, user reviews, bug reports)
2. Auto-creates PRs in ievo-cli, ievo-sdk, marketplace based on patterns found
3. Fitness tracking of Eva's own PRs — did system metrics improve?
4. Self-evolution: Eva's ROLE.md mutates based on the success of her changes
5. Human gate: Eva never merges her own PRs, only proposes
6. Connects via MCP to Sentry API, GitHub API, review/feedback platforms

**Three levels of evolution:**
```
Level 1: EVO      — agent learns from mistakes (local, per-project)
Level 2: Curator  — aggregates lessons across projects → improves marketplace agents
Level 3: Eva      — scans external signals → improves the platform itself
```

Eva is the recursive layer: she improves the system that improves agents, and she improves herself in the process. Same genetic algorithm (genome=ROLE.md, mutation=change, fitness=metrics), but applied to the framework, not to individual agents.

---

## 12. Key Decisions Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| 1 | Build SDD layer, not orchestrator | Market saturated with orchestrators. Nobody owns methodology. | 2026-02-27 |
| 2 | Agent marketplace as separate repo | Agents evolve independently, version-controlled, pip-like install | 2026-02-27 |
| 3 | Copier for Dev SDK only (not project init) | Projects use `ievo init` + `ievo add`. Copier for agent devs. | 2026-02-27 |
| 4 | Spec Writer = onboarding agent | No separate bootstrap. First conversation fills memory naturally. | 2026-02-27 |
| 5 | EVO skill in every agent | Self-evolution is core, not optional. Collective learning. | 2026-02-27 |
| 6 | Curator agent for marketplace evolution | Aggregates lessons from all projects → improves agents for everyone | 2026-02-27 |
| 7 | agent.yaml as package manifest | Like package.json — deps, version, model, hooks, disclosure tiers | 2026-02-27 |
| 8 | Memory as markdown first, SQLite later | Simple, git-tracked, works now | 2026-02-27 |
| 9 | MCP for tools, ACP for agents (Phase 3+) | Complementary protocols | 2026-02-27 |
| 10 | OpenClaw patterns, not platform | Gateway, hooks, cron — architecture ideas, not the codebase | 2026-02-27 |
| 11 | Eva — meta-evolution Mother agent | Scans Sentry/Issues/reviews, auto-PRs to platform repos, self-evolves | 2026-02-27 |
| 12 | Three evolution levels: EVO → Curator → Eva | Local → collective → meta. Each applies genetic algorithm at its scope | 2026-02-27 |
