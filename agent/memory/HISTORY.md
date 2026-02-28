# Session History

## 2026-02-28 — Initial Build

### What happened
Eva was built from scratch in a single session:

1. **Core models** — Signal, Pattern, Mutation dataclasses with enums (SignalType, Severity, MutationType)
2. **Sources** — 4 signal sources implemented: Sentry, GitHub Issues, PR Reviews, Evolution Logs
3. **Pattern detection** — PatternDetector with 3 strategies: frequency, cross-agent, escalation
4. **Mutation engine** — MutationEngine converting patterns to PR-ready changes with confidence scoring
5. **Pipeline** — EvaPipeline orchestrating OBSERVE → ANALYZE → MUTATE with Rich output
6. **CLI** — Click-based CLI: scan, status, init, approve commands
7. **Agent identity** — ROLE.md, agent.yaml, memory/, skills/evo/ — Eva's own self-knowledge
8. **Tests** — 14 pytest tests covering config, detector, models, mutations

### Deployment setup
1. **Dockerfile** — Python 3.12-slim, non-root user, HEALTHCHECK
2. **docker-compose.yml** — Self-hosted with volumes and .env
3. **GitHub Actions** — 3 workflows: eva-scan (cron 6h), eva-on-issue (reactive), tests (CI)
4. **Dual auth** — GitHub App (ievo-eva) + PAT fallback via USE_GITHUB_APP variable
5. **Cross-repo triggers** — `scripts/notify-eva.yml` template for other repos

### Documentation
1. **docs/architecture.md** — System design, evolution levels, data flow
2. **docs/pipeline.md** — Detailed pipeline phases with confidence formulas
3. **docs/sources.md** — All 4 sources with severity mapping and extension guide
4. **docs/configuration.md** — eva.yaml reference, env variables
5. **docs/deployment.md** — GitHub Actions + Docker deployment guide
6. **docs/safety.md** — 8 safety rules, failure modes
7. **docs/GITHUB_APP_SETUP.md** — Step-by-step GitHub App creation

### Key metrics
- **33 files created**, ~2,400 lines of code + docs
- **14 tests** passing
- **First workflow run**: green (dry-run scan, 0 signals — repos are new)

### Decisions made
- See DECISIONS.md for full list (D-001 through D-014)

### What's next
- Add `notify-eva.yml` to cli, marketplace, sdk repos for cross-repo triggers
- Configure Sentry integration (org + project)
- Create test issues to verify Eva picks them up
- Apply same docs/ structure to other iEvo repos
- ~~Build Curator (Level 2 evolution)~~ — DONE (`ievo-ai/curator`)
- Eva ↔ Curator cross-repo dispatch integration

---

## 2026-02-28 — Session 2: Curator Build

### What happened
Built the entire Curator repo (`ievo-ai/curator`) from scratch — Level 2 collective evolution agent.

1. **Core code** (from Session 1 tail) — scanner, parser, detector, proposer, config, pipeline, CLI
2. **Agent identity** — agent.yaml, ROLE.md, EVOLUTION_LOG.md, memory/ (CONTEXT, DECISIONS D-001–D-014, VOCABULARY, HISTORY), skills/evo/SKILL.md
3. **Documentation** — docs/architecture.md, docs/pipeline.md, docs/configuration.md
4. **Tests** — 36 pytest tests across 6 files (parser, detector, proposer, config, scanner, pipeline) — all green
5. **Deployment** — Dockerfile, .github/workflows/curator-scan.yml (weekly + dispatch), tests.yml (CI matrix 3.10/3.11/3.12)
6. **Project docs** — README.md, CLAUDE.md, .gitignore, .dockerignore, .env.example, curator.yaml

### Eva updates for Curator
Updated 5 Eva files to acknowledge Curator as built and ready:
- agent/ROLE.md — added Curator to repos table
- agent/memory/CONTEXT.md — changed "not yet implemented" → "built and ready"
- agent/memory/VOCABULARY.md — expanded Curator definition
- agent/memory/HISTORY.md — struck through "Build Curator" as DONE
- CLAUDE.md — added Curator to related repos

### Commits
- Curator: `fc24de3` — 41 files, +2,761 lines
- Eva: `7542929` — 5 files updated with Curator knowledge

---

## 2026-02-28 — Session 3: Evolutions Feed

### Discussion
Denis raised the question: when Eva's mutation goes to production, there needs to be public logging. We discussed:

- **Terminology**: decided to call them **evolutions** (not mutations, not changes)
- **Two distinct logs**: EVOLUTION_LOG.md = internal agent self-corrections, evolutions.json = public mutations merged to production
- **Three architecture options**:
  1. Runtime fetch — site pulls JSON from Eva repo via GitHub API
  2. Eva pushes to site repo — Eva commits directly to ievo.ai ✅ **chosen**
  3. Dedicated evolutions repo — separate repository
- Denis chose option 2 — single flow, Eva commits to ievo.ai herself

### What was built

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

### Decisions
- **D-015**: Eva pushes evolutions to ievo.ai — single flow, no intermediary
- **D-016**: evolutions.json lives in ievo.ai repo, not in Eva — no runtime API dependency
- **D-017**: Every merged mutation MUST be published — public accountability

### Evolutions schema
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

### Setup required
- **IEVO_BOT_TOKEN** — fine-grained PAT with Contents:Write on `ievo-ai/ievo.ai`, add to Eva repo secrets
- Test evolution: via Actions UI → Run workflow `Publish Evolution`, or locally via script

### Commits
- Eva: `03c617e` — feat: add evolutions feed system (6 files, +180 lines)
- ievo.ai: `6ac9a8b` — feat: add evolutions feed to landing page (3 files)

### What's next
- Push both commits
- Create IEVO_BOT_TOKEN and add to Eva repo secrets
- Run a test evolution via Actions UI
- Add `notify-eva.yml` to cli, marketplace, sdk repos
- Set up auto-publish evolution after mutation merge
