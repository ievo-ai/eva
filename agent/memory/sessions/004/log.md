# Session 004 — MeddyLib Symbiosis

**Date:** 2026-03-01
**Topic:** Establish symbiotic learning relationship with MeddyLib

## Discussion Summary

Denis proposed that Eva learn from his MeddyLib repository — a mature medical imaging library with a sophisticated skill/agent system (8 Claude Code skills, 14 subagents, 647-line AGENTS.md, 15 EVOLUTION_LOG entries). The idea: symbiosis — Eva checks MeddyLib at session start, adopts the best patterns, rejects others with reasoning. Mutual learning.

Key insight: Eva had **zero Claude Code skills** (`.claude/skills/`). Only agent-level skills (`agent/skills/`) for the iEvo pipeline. This was the main gap.

## What Was Built

### New Files
- `.claude/skills/evo/SKILL.md` — Claude Code self-evolution skill (adapted from MeddyLib)
- `.claude/skills/extract-best-practices/SKILL.md` — Platform pattern extraction skill
- `.pre-commit-config.yaml` — ruff + ruff-format + SKILL.md frontmatter validation
- `scripts/check_skill_frontmatter.py` — Pre-commit hook for YAML frontmatter validation
- `AGENTS.md` — Project-level agent guidelines

### Modified Files
- `agent/ROLE.md` — Added "Evolution Over Apology" principle
- `agent/memory/CONTEXT.md` — Added MeddyLib symbiosis protocol with session-start check
- `CLAUDE.md` — Added Claude Code Skills section + MeddyLib Symbiosis section
- `pyproject.toml` — Added ruff lint rules (F, E, I, UP, TID) + banned `__future__.annotations`
- 16 source files + 3 test files — Removed `from __future__ import annotations`, fixed all ruff violations

### Code Modernization
- Removed `from __future__ import annotations` from all 19 files
- Migrated `str, Enum` → `StrEnum` (3 classes in models.py)
- Fixed forward reference: `-> "EvaConfig"` string literal
- Moved inline `import base64` to top-level
- Fixed E501 (line length), E741 (ambiguous variable `l` → `label`), F841 (unused `timestamp`)

## Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-024 | MeddyLib symbiosis — session-start check protocol | Eva learns from Denis's mature skill patterns; mutual improvement |
| D-025 | Two skill layers: .claude/skills/ (interactive) vs agent/skills/ (pipeline) | Different purposes: slash commands vs automated pipeline |
| D-026 | Forbid from __future__ import annotations | Python 3.13+ — PEP 604/585 natively; enforced via ruff TID251 |
| D-027 | Evolution Over Apology principle | Skip apologies → classify → root cause → rule → log; proactive self-improvement |
| D-028 | Pre-commit: ruff + ruff-format + skill-frontmatter | Quality gates before every commit |

### MeddyLib Adoption Decisions

| Pattern | Decision | Reason |
|---------|----------|--------|
| `/evo` skill format | ADOPTED | Eva needs Claude Code skills; meddylib's format is proven |
| `/extract-best-practices` | ADOPTED | Platform pattern extraction — core to Eva's mission |
| Evolution Over Apology (§17) | ADOPTED | Directly matches Eva's philosophy |
| Context/Action/Goal log format | ADOPTED | Cleaner format for evolution entries |
| fact-check | REJECTED | Medical domain-specific |
| commit-safe | REJECTED | Overkill for Eva's simple CLI |
| doc-sync | REJECTED | No Google-style docstring validation needed |
| refactoring-guru | REJECTED | Eva mutates agent configs, doesn't refactor code |
| handle-pr-review | DEFERRED | Phase 2: when Eva processes mutation PR feedback |
| MINDSET.md | DEFERRED | Needs dedicated session |

### MeddyLib EVOLUTION_LOG Analysis

Read all 15 entries. 3 applicable to Eva:
1. "No silent exception swallowing" — Eva's async sources could fail silently
2. "Verify before rejecting reviewer comments" — supports future handle-pr-review skill
3. "Discuss architecture before implementing" — reinforces Eva's dry-run-first approach

## Commits

| Hash | Description |
|------|-------------|
| `12b0f92` | feat: MeddyLib symbiosis — adopt skills, modernize Python |

## What's Next

- [ ] Check Eva's sources for silent exception swallowing (from MeddyLib lesson)
- [ ] Bring Eva CLI to working state (from previous session)
- [ ] Phase 2: `handle-pr-review` skill (when Eva processes mutation PR feedback)
- [ ] MINDSET.md — capture Denis's thinking patterns for Eva
- [ ] Specialized subagents for Eva (GitHub-analyst, evo-log-reader)
