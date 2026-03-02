# Session 015 — iEvo Architecture + Conventions

**Date**: 2026-03-02
**Status**: in_progress

## Vision

iEvo is an **interactive console tool** (like Claude Code itself):
- Textual TUI is the primary interface (must-have)
- On start: generate session ID, check auth, offer telemetry
- When Claude needed → Docker sandbox starts interactively
- **Full native Claude Code preserved** + iEvo orchestration on top
- User is NEVER limited — orchestration is an addition, not a restriction

## Goals

### Done
- [x] Phase 0: Update session convention → directory-based (plan.md + log.md)
- [x] Phase 0: Migrate Eva sessions (14 files → directories)
- [x] Phase 0: Add Status column to HISTORY.md
- [x] Write session journal convention to Eva CLAUDE.md
- [x] Write session journal convention + data map + interactive model to CLI CLAUDE.md
- [x] Add "session plan = first priority" rule to Eva CLAUDE.md + memory

### Done (this session, continued context)
- [x] Pipeline clarification: 15-minute rule → Architect, Backlog/Sprint concepts
- [x] /acceptance skill: mandatory self-review gate
- [x] EVO agent: continuous pipeline observer (research + implementation)
- [x] Docs agent: dedicated documentation writer (Haiku)
- [x] Domain Research merged into Architect (not a separate agent)
- [x] Evolution log entries + GitHub issues #17, #18, #19

### Remaining (future sessions)
- [ ] Phase 1: Startup Flow (auth, Sentry, Docker .claude/ mount)
- [ ] Phase 2: Monorepo merge (curator + SDK → CLI → rename to `ievo`)
- [ ] Phase 3: ievo team (Claude Code subagents for SDD pipeline)
- [ ] Phase 4: Evolution sharing (filter sensitive info, user approval)

## Target Repo Structure

```
ievo-ai/
  eva/          ← private, mother agent (unchanged)
  ievo/         ← public monorepo (ex-cli + curator + sdk)
    src/ievo/
      commands/   run, team, add, learn, dev, config, ...
      curator/    pattern detection, local learning (ex-curator repo)
      scaffold/   agent templates, validation (ex-sdk repo)
      core/       agent, docker, config, prompt, team
      tui/        TUI dashboard (must-have)
    agents/       built-in agents (ex-marketplace, Phase 2)
    schemas/      agent.schema.json (ex-sdk)
    sandbox/      Dockerfile
    tests/
  marketplace/  ← stays for now (registry + downloadable agents)
  ievo.ai/      ← website (unchanged)
```

## Startup Data Flow

```
ievo (first run)
  ├── Generate session ID (UUID)
  ├── Check ~/.ievo/config.json for Claude auth
  │   └── If missing: run `claude auth` → save token
  ├── Telemetry opt-in (first run)
  │   ├── Yes: Sentry (hardcoded DSN) + evolution sharing
  │   └── No: local-only mode
  └── Docker sandbox (interactive)
      ├── Mount project → /workspace
      ├── Mount .claude/ → /workspace/.claude (persistence)
      ├── Pass CLAUDE_CODE_OAUTH_TOKEN
      └── Full native Claude + agents/teams on top
```

## Key Decisions

- Eva stays private/separate — communicates via GitHub API/PRs
- Subagents first (stable), Agent Teams later (experimental)
- Sentry DSN hardcoded in code, not env var
- `.claude/` mounted into Docker sandbox for persistence
- Textual TUI = must-have primary interface
- iEvo preserves full native Claude Code access, adds orchestration on top
- Session journal: directory-based `sessions/NNN/plan.md` + `sessions/NNN/log.md`
