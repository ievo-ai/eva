# Session 003 — Evolutions Feed

**Date**: 2026-02-28
**Topic**: Public evolution logging system for ievo.ai

## Discussion
Denis raised the question: when Eva's mutation goes to production, there needs to be public logging. We discussed:

- **Terminology**: decided to call them **evolutions** (not mutations, not changes)
- **Two distinct logs**: EVOLUTION_LOG.md = internal agent self-corrections, evolutions.json = public mutations merged to production
- **Three architecture options**:
  1. Runtime fetch — site pulls JSON from Eva repo via GitHub API
  2. Eva pushes to site repo — Eva commits directly to ievo.ai ✅ **chosen**
  3. Dedicated evolutions repo — separate repository
- Denis chose option 2 — single flow, Eva commits to ievo.ai herself

## What was built

**ievo.ai repo:**
1. `docs/evolutions.json` — seed entry EVO-000 (Platform genesis)
2. `docs/index.html` — "eva evolutions --live" section:
   - CSS with color-coding by type (milestone=green, role_patch=amber, skill_patch=purple, memory_update=cyan)
   - HTML section before CTA
   - JS: fetches evolutions.json, renders newest-first, max 20 entries

**Eva repo:**
1. `scripts/publish-evolution.py` — CLI script: accepts --id, --title, --agent, --type, --target, --description, --confidence, --pr, --file; appends entry to evolutions.json
2. `.github/workflows/publish-evolution.yml` — workflow_dispatch with all fields; checks out ievo.ai with IEVO_BOT_TOKEN, runs script, commits and pushes
3. Updated: ROLE.md (Evolutions Feed section + schema), CONTEXT.md, DECISIONS.md (D-015, D-016, D-017), CLAUDE.md

## Decisions
- **D-015**: Eva pushes evolutions to ievo.ai — single flow, no intermediary
- **D-016**: evolutions.json lives in ievo.ai repo, not in Eva — no runtime API dependency
- **D-017**: Every merged mutation MUST be published — public accountability

## Evolutions schema
```json
{
  "id": "EVO-XXX",
  "date": "YYYY-MM-DD",
  "title": "...",
  "agent": "eva|curator|...",
  "type": "role_patch|skill_patch|memory_update|milestone|best_practice",
  "target": "repo/path",
  "description": "...",
  "confidence": 0.0-1.0,
  "pr": "url|null"
}
```

## Setup required
- **IEVO_BOT_TOKEN** — fine-grained PAT with Contents:Write on `ievo-ai/ievo.ai`, add to Eva repo secrets
- Test evolution: via Actions UI → Run workflow `Publish Evolution`, or locally via script

## Commits
- Eva: `03c617e` — feat: add evolutions feed system (6 files, +180 lines)
- ievo.ai: `6ac9a8b` — feat: add evolutions feed to landing page (3 files)

## What's next
- Push both commits
- Create IEVO_BOT_TOKEN and add to Eva repo secrets
- Run a test evolution via Actions UI
- Add `notify-eva.yml` to cli, marketplace, sdk repos
- Set up auto-publish evolution after mutation merge
