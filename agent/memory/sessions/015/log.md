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

### Defrag agent (new) + rule redistribution
- Created `marketplace/agents/defrag/` — Haiku model, read-only, SCAN → COMPARE → REPORT
- Redistributed 16 rules to 6 agent ROLE.md files (Architect +4, Coder +5, Acceptance +2, EVO +2, Researcher +2, Docs +1)
- Reorganized Eva CLAUDE.md working rules into 3 sections
- GitHub issue #20

### Unified .ievo/ storage + IEVO.md overlay
- Created `.ievo/` directory structure: backlog/, spec/, plans/, reports/, memory/
- Created IEVO.md template — pipeline context overlay (auto-generated)
- Three-layer context model: CLAUDE.md → IEVO.md → ROLE.md
- Updated all 8 agent ROLE.md paths to `.ievo/` prefix
- `.ievo/version` file for CLI version tracking + auto-migration
- CLI template source: `cli/src/ievo/templates/IEVO.md`
- Acceptance report + proposal templates
- Updated SDK scaffold
- GitHub issue #21

## Repos affected
- **eva**: CLAUDE.md, ROLE.md, EVOLUTION_LOG.md, HISTORY.md, sessions, /acceptance skill
- **marketplace**: 4 new agents (acceptance, docs, evo, defrag), updated all 8 ROLE.md files, bootstrap restructured to .ievo/, templates
- **cli**: CLAUDE.md, docs/ARCHITECTURE.md, src/ievo/templates/IEVO.md
- **sdk**: template/ROLE.md.j2 updated to .ievo/ paths

## GitHub issues
- #17: Pipeline clarification — 15-minute rule, Sprint/Backlog, Acceptance loop
- #18: EVO as dedicated agent — continuous pipeline observer
- #19: Docs agent — dedicated documentation writer
- #20: Defrag agent — rules live where they're enforced
- #21: Unified .ievo/ storage + IEVO.md overlay

### Native Claude Code sub-agents migration

- Researched Claude Code sub-agent spec (frontmatter fields, auto-delegation, memory, skills)
- Designed frontmatter for all 9 agents (model, tools, memory: user, skills, maxTurns, permissionMode)
- Created 9 native `.md` agent files in `marketplace/agents/`:
  - spec-writer, architect, coder, acceptance, docs, researcher, evo, defrag, hr (new)
- Consolidated 6 templates to `marketplace/templates/`
- Deleted 8 old agent directories (58 files removed)
- Updated `registry.yaml`: added `file:`, `mandatory:` fields, bumped to 0.2.0
- Key decisions:
  - `memory: user` for all agents (cross-project learning)
  - No hooks for now
  - Fully automatic delegation via `description` field
  - EVO agent does NOT get `evo` skill (prevents circular self-evolution)
  - `permissionMode: plan` for defrag (read-only)
  - `permissionMode: acceptEdits` for coder and docs
  - Evolution overlay: agents read `.ievo/evolution/<name>.md` for project-specific rules
  - HR agent: mandatory, manages team deployment/updates/removal
- Commit: `3304068` in marketplace repo

### Post-migration refinements

- Removed `maxTurns` from all 9 agent frontmatter (unnecessary constraint)
- Created `/backlog` skill for quick idea capture (`IDEA-NNN-<slug>.md`)
  - Eva: `.claude/skills/backlog/SKILL.md`
  - Marketplace: `skills/backlog/SKILL.md`
- Added `IEVO.md` to `marketplace/templates/` and `registry.yaml` templates list
- Added Sessions section to IEVO.md:
  - Session structure (plan.md = intent, log.md = reality)
  - Session statuses: planned → in_progress → completed
  - HISTORY.md format with table columns
  - Session rules (plan first, incremental updates, sequential numbering)
- Added Cross-Linking section to IEVO.md:
  - Sessions → Artifacts (strong, required in log.md)
  - Artifacts → Sessions (weak, optional)
  - DECISIONS.md as cross-session decision log with D-NNN IDs
  - Summary table of all link directions
- Updated Document Lifecycle diagram with session wrapper
- Added 4 rows to Naming Conventions table (session plan, log, index, decision)
- Synced bootstrap example IEVO.md with template
- Commit: `c2ff023` in marketplace repo

## Pending
- [x] Commit and push all changes
- [x] Phase 3: ievo team (Claude Code subagents) — marketplace done
- [ ] Phase 1: Startup Flow implementation (CLI repo — separate session)
- [ ] Phase 2: Monorepo merge
- [ ] Phase 4: Evolution sharing
- [ ] CLI `ievo init` + `ievo update` to scaffold `.ievo/` and auto-migrate (future session)
- [ ] Update CLI to deploy native `.md` agents to `.claude/agents/` instead of old format
- [ ] Update SDK scaffold template for native format
