# Session 014 — PR Gatekeeper Pipeline

**Date**: 2026-03-02
**Topic**: Eva as PR gatekeeper — full automation pipeline

## Summary

Implemented the complete PR-only workflow across all ievo-ai/* repos. Eva now reviews PRs via Claude Code CLI, auto-merges on approval, publishes evolutions to GitHub + Telegram.

## What was built

### Eva PR Review Workflow (`eva-review-pr.yml`)
- Triggers: `repository_dispatch` (child repos) + `workflow_run` (self-review)
- Auth: GitHub App (`ievo-eva[bot]`) preferred, PAT fallback
- Claude Code CLI review with structured APPROVE/REQUEST_CHANGES output
- Auto-merge on approval (squash)
- Evolution publishing after merge (triggers `publish-evolution.yml`)
- Safety: loop prevention, draft skip, large PR skip (>10k lines), 15min timeout

### Evolution Publishing (`publish-evolution.yml`)
- Rewritten to use native `eva publish --live` instead of curl scripts
- Maps `EVA_PAT_GITHUB_TOKEN` → `EVA_GITHUB_TOKEN` (code expects this name)
- Publishes to both GitHub (evolutions.json) and Telegram (Evolutions topic)

### Child Repo Notify Workflow (`notify-eva.yml`)
- Installed on: cli, marketplace, sdk, curator
- Dispatches to Eva when tests pass on non-draft PRs
- Uses unified `EVA_PAT_GITHUB_TOKEN` secret

### CLAUDE.md Updates
- Added authorship rule: `Co-Authored-By: iEVO Eva <noreply@ievo.ai>`
- No version number in signature (Denis corrected)

### Secret Unification
- Renamed `EVA_DISPATCH_TOKEN` → `EVA_PAT_GITHUB_TOKEN` across all repos
- Renamed `EVA_GITHUB_TOKEN` → `EVA_PAT_GITHUB_TOKEN` in docker-compose.yml

## Repos affected
- **eva**: workflows, CLAUDE.md, docker-compose.yml
- **cli**: notify-eva.yml, tests.yml, test PRs (#16, #17)
- **marketplace**: notify-eva.yml
- **sdk**: notify-eva.yml (existed already)
- **curator**: notify-eva.yml

## Key decisions
- GitHub App for review identity (`ievo-eva[bot]`), PAT for dispatch/workflow triggers
- App tokens cannot trigger `workflow_dispatch` — must use PAT
- Claude CLI prompts piped via file (shell escaping issues with direct args)
- COMMENT fallback when APPROVE fails (own-PR restriction)
- Native `eva publish --live` over curl scripts

## Errors encountered & fixed
1. `EVA_PAT_GITHUB_TOKEN` not set on child repos → set on all 5
2. ievo-eva PAT can't see private Eva repo → temporary Denis PAT
3. Claude CLI "Input must be provided" → file + stdin pipe
4. "Cannot approve own PR" → COMMENT fallback
5. Branch protection check name mismatch (`test` vs `Lint & Test`) → fixed
6. App token can't trigger workflow_dispatch → use PAT for publish step
7. `EVA_GITHUB_TOKEN` vs `EVA_PAT_GITHUB_TOKEN` → env mapping in workflow
8. Telegram messages in General topic → added `TELEGRAM_EVOLUTIONS_TOPIC` env var
9. shellcheck SC2016/SC2034 warnings → fixed

## E2E verification
- PR #16 (CLI): Tests → Eva dispatch → Claude review → APPROVED → Auto-merge → PyPI publish `v26.03.02.1350` ✓
- PR #17 (CLI): Full cycle including evolution publishing → EVO-018, EVO-019 ✓
- Telegram: messages routed to Evolutions topic (after topic ID fix) ✓

## Commits

### Eva repo
- `8aad36a` feat: Eva PR gatekeeper — review + auto-merge workflow
- `52b7bed` chore: unify secret name to EVA_PAT_GITHUB_TOKEN
- `6c2aa15` docs: add Eva commit & PR authorship rule
- `efddb39` fix: remove version number from Eva signature
- `15a11cb` evo: docs ship with code — not as afterthoughts
- `4455f1f` fix: pipe prompt via file to Claude CLI, fallback review to COMMENT
- `f53cd24` feat: publish evolution + Telegram after PR merge
- `63c9d2f` refactor: use eva publish --live instead of curl scripts
- `8adbffc` fix: use PAT for workflow dispatch in publish step
- `b44c7f1` fix: map EVA_PAT_GITHUB_TOKEN to EVA_GITHUB_TOKEN for eva publish
- `90b0eff` fix: pass TELEGRAM_EVOLUTIONS_TOPIC to publish workflow

### CLI repo
- `23c783d` feat: PR workflow — tests on PRs + Eva review dispatch
- `f2c0324` chore: rename secret to EVA_PAT_GITHUB_TOKEN
- `0dd759c` docs: add Eva review note to CLI docstring (#16)
- `b4879ff` docs: add evolution publishing note to CLI docstring

## Pending
- [ ] Replace Denis's PAT with ievo-eva's when account unblocked
- [ ] Update branch protection check names on marketplace, sdk, curator
- [ ] Issue #13: contributor credits system
