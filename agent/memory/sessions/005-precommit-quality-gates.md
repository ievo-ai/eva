# Session 005 — Pre-commit Quality Gates

**Date:** 2026-03-01
**Topic:** Expand pre-commit pipeline with mypy, actionlint, and workflow security hardening

## Discussion Summary

Continuation of session 004 (MeddyLib symbiosis). Denis asked to interview each of MeddyLib's pre-commit hooks and decide which to adopt. All candidates were selected:

1. **Basic hooks** (trailing-whitespace, end-of-file-fixer, check-yaml, check-merge-conflict) — adopted
2. **debug-statements** — adopted (catches forgotten breakpoint/pdb)
3. **actionlint** — adopted (lints GitHub Actions workflows)
4. **mypy strict** — adopted (full type checking for src/eva/)

## What Was Built

### Pre-commit Expansion (3 → 10 hooks)

New hooks added to `.pre-commit-config.yaml`:
- `trailing-whitespace`, `end-of-file-fixer`, `check-yaml`, `check-merge-conflict`
- `debug-statements`
- `actionlint`
- `mypy` (local hook, `entry: mypy src/eva`, strict mode)

### Mypy Strict Mode (62 errors → 0)

- Created `src/eva/py.typed` — PEP 561 marker for mypy to recognize package
- Added `[tool.mypy]` to `pyproject.toml`: `strict = true`, `mypy_path = "src"`, Python 3.13
- Added `types-PyYAML` stubs to dev dependencies
- Fixed `resp.json()` → explicit `dict[str, Any]` annotations in `github/client.py`
- Fixed `_before_send` signature: `Event`/`Hint` types from `sentry_sdk.types`
- Added `isinstance` guard for `breadcrumbs` (AnnotatedValue union)
- Added `Severity` type annotation to `_severity_color` helper
- Configured overrides for `sentry_sdk.*` and `git.*` (ignore missing imports)

### Workflow Security Hardening (SC2086 fixes)

Moved `${{ }}` expressions from `run:` blocks into `env:` blocks across all 3 workflow files:
- `.github/workflows/eva-on-issue.yml` — tokens, event context, workspace
- `.github/workflows/eva-scan.yml` — tokens, dry-run input, workspace
- `.github/workflows/publish-evolution.yml` — all 8 evolution inputs

Also quoted all shell variables (`"$GITHUB_OUTPUT"`, `"$GITHUB_ENV"`, `"$WORKSPACE/..."`).

### Other Fixes

- Removed last `from __future__ import annotations` in `scripts/generate-app-token.py`
- End-of-file newlines on SKILL.md files and AGENTS.md
- ruff-format adjustments on 3 files

## Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| D-029 | Pre-commit: 10 hooks (mypy strict, actionlint, basic hygiene) | Full quality gate pipeline adopted from MeddyLib interview |
| D-030 | Mypy as local hook with explicit entry | `mirrors-mypy` + `pass_filenames: false` doesn't pass files; local `entry: mypy src/eva` works |
| D-031 | Workflow security: env blocks over inline ${{ }} | Prevents shell injection, satisfies actionlint SC2086, follows GitHub security guide |

## Commits

| Hash | Description |
|------|-------------|
| `84b58d3` | feat: add pre-commit quality gates (mypy, actionlint, shellcheck) |

## What's Next

- [ ] Check Eva's sources for silent exception swallowing (from MeddyLib lesson)
- [ ] Bring Eva CLI to working state
- [ ] Phase 2: `handle-pr-review` skill
- [ ] MINDSET.md — capture Denis's thinking patterns
- [ ] Specialized subagents for Eva
