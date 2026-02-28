# Competitive Landscape & Research

Researched 2026-02-27. Extracted from original TODO.md for reference.

---

## Existing Solutions

| Project | Stars | What It Does | Use/Learn/Ignore |
|---------|-------|-------------|-----------------|
| [wshobson/agents](https://github.com/wshobson/agents) | 29.5k | 112 agents, 72 plugins, 3-tier model strategy | LEARN: plugin arch, model tiering |
| [claude-flow/Ruflo](https://github.com/ruvnet/claude-flow) | 15.3k | Self-learning orchestrator, neural routing, 60+ agents | LEARN: token efficiency, adaptation |
| [Claude Agent Teams](https://code.claude.com/docs/en/agent-teams) | Native | Built-in Claude Code: team lead + teammates, shared tasks | USE AS BASE ENGINE |
| [Kiro IDE](https://kiro.dev/) | Closed | Amazon's spec-driven IDE, EARS notation → code | LEARN: EARS notation, arch generation |
| [Agent Factory SDD](https://agentfactory.panaversity.org/docs/General-Agents-Foundations/spec-driven-development) | Methodology | SDD methodology for Claude Code | LEARN: methodology foundation |
| [claude-mpm](https://github.com/bobmatnyc/claude-mpm) | 78 | PM orchestration, 47+ agents, TDD skills | LEARN: session resumption |
| [CrewAI](https://github.com/crewAIInc/crewAI) | 44k | Generic multi-agent framework, model-agnostic | EVALUATED: too abstract for us |
| [OpenClaw](https://github.com/openclaw/openclaw) | 236k | Personal AI assistant (WhatsApp/Telegram/Slack) | FUTURE: PM notifications |

## Our Unique Position (nobody does all of this together)
- Formal spec → atomic requirements → priority scoring → architecture plan → strict TDD → review gates
- Pluggable domain agents via MCP (medical, unity, devops, security)
- Copier-based project templates with `copier update` for evolution
- Persistent agent memory across sessions

## Strategic Decision
- **Build ON TOP of Agent Teams + wshobson/agents plugins**
  - Agent Teams = coordination engine (who talks to whom)
  - wshobson plugins = agent capabilities (TDD, code review, debugging)
  - Our framework = SDD methodology (what they work on, in what order, with what rules)

---

## Ideas to Adopt

### From wshobson/agents
- **3-tier model strategy**: Opus (architecture, security) → Sonnet (implementation, review) → Haiku (tests, scaffold). 49% token savings.
- **Progressive disclosure for ROLE.md**: 3 tiers (metadata=always, instructions=on-activate, resources=on-demand)
- **Conductor pattern**: persistent state in `.conductor/`, semantic revert, track/phase/task hierarchy
- **Plugin format**: package agents as Claude Code plugins
- **TDD orchestrator**: evaluate if `tdd-workflows` plugin replaces Coder agent

### From claude-flow/Ruflo
- **Context archival**: archive old turns to SQLite, restore by importance
- **Importance ranking**: score loaded context by recency + semantic relevance
- **Cost routing**: estimate complexity → pick cheapest viable model

### From OpenClaw
- **Gateway pattern**: single entry point routing messages to agents by binding rules
- **Selective skill injection**: inject only relevant skills per turn
- **ACP (Agent Context Protocol)**: agent-to-agent communication (IBM Research → Linux Foundation)
- **Cron scheduler**: auto-trigger agents on schedule (isolated sessions per job)
- **Lifecycle hooks**: session_start, session_end, before_tool_call, after_tool_call, agent:bootstrap
- **Memory improvements**: file watcher, semantic search, memory as source of truth
- **Multi-channel delivery**: WhatsApp, Telegram, Slack for PM agent

### From Kiro IDE
- **EARS notation** for REQUIREMENT_TEMPLATE.md

---

## Architecture Decisions (from original research)

### Copier (not Cookiecutter)
- Supports updating existing projects when template evolves (3-way merge)
- Stores `.copier-answers.yml` — remembers original template + answers
- `copier update` in any project → get new agents, fixes, improvements

### Claude Agent SDK (Python) — Hybrid approach
- Each agent = Python package with ROLE.md + agent.py + mcp.json
- ROLE.md works standalone with `claude -p` AND as system_prompt in SDK
- Agent SDK gives: hooks, sub-agents, MCP from code
- Versionable: `pip install --upgrade ievo-spec-writer`

### CrewAI — Evaluated, NOT recommended
- Adds abstraction layer, memory resets between runs, too rigid for TDD workflow

### OpenClaw — Evaluated, NOT for our core use case
- Designed for personal assistant, not dev pipeline orchestration
- Useful later for PM agent notifications
