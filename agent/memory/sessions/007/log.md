# Session 007 — Children Symlinks

**Date:** 2026-03-01
**Topic:** Local symlinks to marketplace agents + CRLF fix + evo cycles #3-#4

## Discussion Summary

Denis proposed creating symlinks to marketplace agents so Eva has direct filesystem access to her children. Key decisions: symlinks are local-only (gitignored, never committed), and belong in `.claude/children/` (not `agent/children/`) because `.claude/` is Claude Code's directory.

Also fixed CRLF line endings globally and ran `/evo` cycles #3 and #4. Cycle #4 adopted meddylib's fact-check skill as `/verify` — adapted for path checking, convention validation, and GitHub API state verification.

## What Was Built

### Children Symlinks
- `.claude/children/` directory with 4 symlinks → `ievo-ai/marketplace/agents/`
- spec-writer, architect, coder, researcher
- Added to `.gitignore` — not tracked
- Updated CLAUDE.md architecture tree and CONTEXT.md

### CRLF Fix
- Added `.gitattributes` with `* text=auto eol=lf`
- Renormalized all 43 files from CRLF to LF
- Set `git config --global core.autocrlf input`
- Re-checked out working copy to eliminate all CRLF warnings

### Evolution Cycle #3
- Entry: "Include .gitattributes from the first commit"
- Issue [#4](https://github.com/ievo-ai/eva/issues/4)

### Evolution Cycle #4
- Entry: "Verify before acting — adopt fact-check skill"
- Created `/verify` skill in `.claude/skills/verify/SKILL.md`
- Adapted from meddylib's fact-check — check paths, conventions, API state before acting
- Added "verify before acting" to CLAUDE.md working rules
- Issue [#5](https://github.com/ievo-ai/eva/issues/5)

## Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-035 | LF line endings enforced via .gitattributes | Eliminates CRLF warnings, consistent across platforms |
| D-037 | New repos must include .gitattributes from first commit | Prevent CRLF accumulation |
| D-038 | Children symlinks in .claude/children/ (not agent/) | .claude/ is Claude Code's directory, natural discovery |
| D-039 | Symlinks local-only, gitignored | Never commit symlinks — they're machine-specific paths |

## Commits

| Hash | Description |
|------|-------------|
| `59627a1` | chore: normalize line endings to LF via .gitattributes |
| `3759106` | evo: include .gitattributes from the first commit |
| `bc46159` | docs: update session 006 with evo #3, D-037 |
| `6b5154e` | feat: symlinks to marketplace agents in agent/children/ |
| `a7c0910` | fix: move children symlinks from agent/ to .claude/ |
| `263d72d` | docs: session 007 — children symlinks |
| `2a356ba` | evo: verify before acting — adopt fact-check skill |

## What's Next

- [ ] Machine user @ievo creation (issue #2, assigned to 27tech)
- [ ] Check Eva's sources for silent exception swallowing
- [ ] Bring Eva CLI to working state
- [ ] Phase 2: `handle-pr-review` skill
