# Session 015 — iEvo Architecture + Pipeline Redesign

**Date**: 2026-03-02
**Status**: in_progress

## What was done

### Phase 0: Session convention update
- Updated Eva CLAUDE.md — new directory-based session convention (`sessions/NNN/plan.md` + `log.md`)
- Migrated 14 session files: `sessions/NNN-topic.md` → `sessions/NNN/log.md`
- Added Status column to HISTORY.md (all 14 = `completed`, 015 = `planned`)
- Created `sessions/015/plan.md` + `sessions/015/log.md`

### Convention documentation
- Rewrote CLI `CLAUDE.md` — added interactive model, data map, session convention, startup flow, working rules
- Added "session plan = first priority" rule to Eva CLAUDE.md + MEMORY.md

### Pipeline clarification — 15-minute rule + Sprint/Backlog
- Denis corrected: Spec Writer does NOT own time estimates — only Architect does
- Established full pipeline: Backlog → Spec Writer → Sprint → Architect (≤15 min) → Coder → Acceptance → Docs → Done
- Architect ROLE.md: threshold 30 min → 15 min, strict rule #12, Coder escalation
- Coder ROLE.md: Acceptance feedback loop (step 5b), Architect escalation section
- Acceptance ROLE.md: formalized rejection flow with report file
- Researcher ROLE.md: rule #7 proposals go to Backlog
- Eva ROLE.md: full pipeline with Backlog/Sprint/EVO gates/Docs, updated children table
- Eva + CLI CLAUDE.md: 15-minute rule in working rules
- GitHub issue #17

### /acceptance skill
- Created `.claude/skills/acceptance/SKILL.md` — mandatory self-review gate before marking tasks done

### EVO agent (new)
- Research: Kanban > Scrum for AI agents, continuous observation > batch retrospectives
- Created `marketplace/agents/evo/` — continuous pipeline observer at every transition
- 4-layer evolution model: Self-correction → EVO → Curator → Eva
- Updated registry.yaml, Eva ROLE.md, CLAUDE.md, CLI ARCHITECTURE.md
- GitHub issue #18

### Docs agent (new)
- Created `marketplace/agents/docs/` — Haiku model, updates docs after Acceptance PASS
- Updated registry.yaml, Eva ROLE.md, CLAUDE.md, CLI ARCHITECTURE.md
- GitHub issue #19

### Domain Research in Architect
- Denis asked about Deep Researcher agent — merged into Architect instead (less handoffs, already Opus)
- Added responsibility #1 "Domain Research" to Architect ROLE.md
- Updated agent.yaml (network: true), registry.yaml description, Eva ROLE.md children table

## Repos affected
- **eva**: CLAUDE.md, ROLE.md, EVOLUTION_LOG.md, HISTORY.md, sessions, /acceptance skill
- **marketplace**: 3 new agents (acceptance, docs, evo), updated architect, coder, researcher, registry
- **cli**: CLAUDE.md, docs/ARCHITECTURE.md

## GitHub issues
- #17: Pipeline clarification — 15-minute rule, Sprint/Backlog, Acceptance loop
- #18: EVO as dedicated agent — continuous pipeline observer
- #19: Docs agent — dedicated documentation writer

## Pending
- [ ] Commit and push all changes
- [ ] Phase 1: Startup Flow implementation (CLI repo — separate session)
- [ ] Phase 2: Monorepo merge
- [ ] Phase 3: ievo team (Claude Code subagents)
- [ ] Phase 4: Evolution sharing
