# Session 012 — CLI E2E Test (Failed)

**Date**: 2026-03-02
**Topic**: End-to-end test of iEvo CLI pipeline on a fresh project
**Result**: FAIL — pipeline cannot complete without manual workarounds

## What was tested

Fresh project setup in `/Users/denis/projects/amplifier.ai/super-agent/ievo-test`:
1. `ievo init .` → project scaffold
2. `ievo add spec-writer architect coder` → agent install
3. `ievo run spec-writer -m "..."` → first requirement

Goal: user types 3 commands and gets a working REQ file. Zero manual editing.

## Issues found (7 GitHub issues created)

| # | Issue | Severity | Repo |
|---|-------|----------|------|
| [#2](https://github.com/ievo-ai/cli/issues/2) | Publish ievo to PyPI (`pip install ievo`) | high | cli |
| [#3](https://github.com/ievo-ai/cli/issues/3) | `ievo init` should auto-install core agents + offer extras from marketplace | high | cli |
| [#4](https://github.com/ievo-ai/cli/issues/4) | `ievo init` should auto-generate CLAUDE.md from project scan + user interview | high | cli |
| [#5](https://github.com/ievo-ai/cli/issues/5) | `ievo` should be seamless single-process experience (TUI-driven) | medium | cli |
| [#6](https://github.com/ievo-ai/cli/issues/6) | `ievo run` shows no progress — looks frozen | high | cli |
| [#7](https://github.com/ievo-ai/cli/issues/7) | `ievo run` must configure Claude permissions for agent file operations | critical | cli |
| [#8](https://github.com/ievo-ai/cli/issues/8) | `ievo init` should handle git repo initialization | medium | cli |

## Failure chain

```
User runs `ievo` → command not found (not in PATH, no PyPI)
User runs `ievo init .` → must manually `git init` first
User gets empty CLAUDE.md → must manually fill in project context
User runs `ievo add` → works fine ✓
User runs `ievo run spec-writer` → no progress shown, looks frozen
Agent tries to write files → blocked by missing permissions
```

## Key insight

The **critical blocker** is #7 (permissions). Without it, no agent can write any file. Everything else is UX friction. Fix order:

1. **#7** — permissions (unblocks the pipeline)
2. **#6** — progress feedback (user knows what's happening)
3. **#8** — git init (remove manual step)
4. **#4** — auto-generate CLAUDE.md (remove manual step)
5. **#3** — auto-install agents (remove manual step)
6. **#2** — PyPI publish (remove install friction)
7. **#5** — seamless TUI (long-term UX vision)

## Eva bug found

Eva fabricated GitHub username "dennisdup" instead of looking up via API. Violates CLAUDE.md rule. Recorded in memory #1111. Needs /evo.

## Decisions

- D-012-1: ievo CLI needs significant UX work before public launch
- D-012-2: Core pipeline (init → add → run) must work in 1 command for MVP
- D-012-3: Permissions must be auto-configured — users should never see permission errors

## What's next

- [ ] Fix #7 (permissions) — critical path
- [ ] Fix #6 (progress) — user trust
- [ ] Run /evo for username fabrication bug
- [ ] Re-test E2E after fixes
