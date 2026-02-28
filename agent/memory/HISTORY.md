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
- Build Curator (Level 2 evolution) — Phase 3
