# Session 006 — Evo Workflow & Repo Cleanup

**Date:** 2026-03-01
**Topic:** Evolve /evo skill workflow, working rules, line ending normalization

## Discussion Summary

Continuation of session 005. Focused on evolving Eva's `/evo` skill and establishing operational rules through two `/evo` cycles, plus repo hygiene.

Denis established key workflow preferences:
- Sessions saved automatically after every push (not just end of session)
- `/evo` runs automatically after session save
- Evolution steps create GitHub issues (not PRs)
- `ievo` label = Eva's task; don't apply to human tasks
- Evolution logs must never contain sensitive data
- Machine user `ievo` requested for future issue assignment (issue #2)

## What Was Built

### /evo Skill Enhancements
- Step 8 added: create GitHub issue for each evolution step
- `--assignee 27tech` added to issue creation
- `ievo` label removed from evo issues (they're for human review)
- Sensitive data warning added to evolution log step

### CLAUDE.md Working Rules
- Renamed "Editing rules" → "Working rules"
- Added: always `--assignee` on issues, look up usernames via API
- Added: `ievo` label semantics (Eva's tasks only)
- Added: evolution logs must not contain sensitive data
- Added: auto-session save + auto-evo convention

### Evolution Log
- Entry #1: Re-read YAML files between sequential edits
- Entry #2: Always assignee on issues, no sensitive data in evo logs

### GitHub Issues
- Created `evolution` label (purple)
- Created `ievo` label (blue) — Eva's ownership
- Issue #1: evo — Re-read YAML files between sequential edits
- Issue #2: ops — Create machine user @ievo (assigned to 27tech)
- Issue #3: evo — Always assignee on issues, no sensitive data

### Repo Cleanup
- Added `.gitattributes` with `text=auto eol=lf`
- Normalized all 43 files from CRLF to LF — eliminates git warnings

## Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-032 | Evolution steps → GitHub issues (not PRs) | Traceable record for future propagation to children |
| D-033 | `ievo` label = Eva's task only | Don't apply to human tasks; correct ownership semantics |
| D-034 | Evolution logs must not contain sensitive data | Logs are public — no tokens, passwords, private paths |
| D-035 | LF line endings enforced via .gitattributes | Eliminates CRLF warnings, consistent across platforms |
| D-036 | Machine user @ievo for GitHub (pending) | Real assignee support; email ievo@ievo.ai; issue #2 tracks |

## Commits

| Hash | Description |
|------|-------------|
| `fee8bee` | feat: evo skill creates GitHub issues, add editing rules to CLAUDE.md |
| `0ee9bfb` | evo: re-read YAML files between sequential edits |
| `1c5dd56` | evo: working rules — assignee, label semantics, no sensitive data |
| `59627a1` | chore: normalize line endings to LF via .gitattributes |

## What's Next

- [ ] Machine user @ievo creation (issue #2, assigned to 27tech)
- [ ] Check Eva's sources for silent exception swallowing
- [ ] Bring Eva CLI to working state
- [ ] Phase 2: `handle-pr-review` skill
- [ ] Specialized subagents for Eva
