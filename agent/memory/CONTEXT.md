# Eva Context

## Platform

- **Name**: iEvo (ievo.ai)
- **Tagline**: Self-Evolving Multi-Agent SDD Framework
- **Creator**: Denis (denis@27tech.co), 27Tech / Amplifier.AI
- **GitHub Org**: `ievo-ai`
- **Stack**: Python + Claude API

## Repositories

| Repo | Purpose | Status |
|------|---------|--------|
| `ievo-ai/cli` | CLI tool (`ievo`) + Textual TUI dashboard | Active |
| `ievo-ai/marketplace` | Agent registry, shared skills, agent packages | Active |
| `ievo-ai/sdk` | Developer toolkit: scaffold, validate, inspect agents | Active |
| `ievo-ai/eva` | Me — meta-evolution pipeline | Active |
| `ievo-ai/curator` | Level 2 — cross-agent pattern detection | Active |
| `ievo-ai/ievo.ai` | Landing page / project homepage | Active |

## Architecture Context

### CLI (`ievo-ai/cli`)

- Entry point: `ievo` command (Typer-based)
- Running without args launches Textual TUI dashboard (4 tabs: Agents, Pipeline, Evolution, Files)
- Subcommands: `ievo init`, `ievo add`, `ievo run`, `ievo list`, `ievo evolve`
- Dependencies: typer, rich, textual, pyyaml, httpx

### Marketplace (`ievo-ai/marketplace`)

- Agent packages live in `agents/{name}/` following the standard agent structure
- Shared skills in `shared/skills/`
- Registry in `registry.yaml`
- Each agent has: agent.yaml, ROLE.md, EVOLUTION_LOG.md, memory/, skills/evo/

### SDK (`ievo-ai/sdk`)

- Scaffold: `ievo-sdk new {name}` — generates agent package from Jinja2 templates
- Validate: `ievo-sdk validate {path}` — JSON Schema + structure checks
- Info: `ievo-sdk info {path}` — display agent metadata
- Schema: `schemas/agent.schema.json`

### Eva (`ievo-ai/eva`)

- Pipeline: OBSERVE → ANALYZE → MUTATE
- Sources: Sentry, GitHub Issues, PR Reviews, Evolution Logs
- Detection: frequency, cross-agent, escalation
- Output: PR-ready mutations (ROLE_PATCH, SKILL_PATCH, MEMORY_UPDATE)
- Deployment: GitHub Actions (cron 6h + issue trigger) + Docker

## Monitored Sources

| Source | Status | Notes |
|--------|--------|-------|
| Sentry | Disabled | Not yet configured (no org/project set) |
| GitHub Issues | **Enabled** | Polls all 5 ievo-ai repos |
| PR Reviews | Disabled | Can be enabled when repos have regular PRs |
| Evolution Logs | **Enabled** | Reads from marketplace agents' EVOLUTION_LOG.md |

## Authentication

- **GitHub App**: `ievo-eva` app installed on `ievo-ai` org
  - Secrets: `APP_ID`, `APP_PRIVATE_KEY`
  - Repo variable: `USE_GITHUB_APP=true`
- **PAT fallback**: `EVA_GITHUB_TOKEN` secret

## Documentation Standard

All repos must follow: `README.md` (overview) + `CLAUDE.md` (AI context) + `docs/` (detailed reference).
No README.md inside docs/. No duplicate content between README and docs/.

## Evolutions Feed

- Public evolution log: `ievo-ai/ievo.ai/docs/evolutions.json`
- Website renders it at ievo.ai (Evolutions section)
- `publish-evolution.yml` workflow pushes new entries after merged mutations
- `scripts/publish-evolution.py` handles append + commit to ievo.ai

## Known Patterns

<!-- Eva fills this section as she detects patterns across runs -->

## Notes

- All repos are freshly created (Feb 2026) — expect few signals initially
- Sentry integration pending (org/project not yet configured)
- Curator (Level 2 evolution) — built and ready (`ievo-ai/curator`)
- Cross-repo dispatch (`notify-eva.yml`) needs to be copied to cli, marketplace, sdk repos
