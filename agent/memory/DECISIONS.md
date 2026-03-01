# Eva Decisions

| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
| D-001 | 2026-02-28 | Dry-run by default | Safety first — never create PRs without explicit --live flag | Active |
| D-002 | 2026-02-28 | Min 2 signals per pattern | Avoid false positives from single events | Active |
| D-003 | 2026-02-28 | Max 5 mutations per run | Rate limit to keep PRs reviewable | Active |
| D-004 | 2026-02-28 | Never auto-merge | Every mutation requires human approval via PR review | Active |
| D-005 | 2026-02-28 | GitHub App over PAT | Better security, scoped permissions, own identity, no seat usage | Active |
| D-006 | 2026-02-28 | Docker-based Actions | Same image runs in CI, local, VPS, k8s — reproducible | Active |
| D-007 | 2026-02-28 | Dual auth (App + PAT fallback) | Start with PAT, upgrade to App later — flexible onboarding | Active |
| D-008 | 2026-02-28 | Skip github-actions[bot] issues | Prevent infinite feedback loops between Eva and CI | Active |
| D-009 | 2026-02-28 | Never delete rules | Eva only adds rules. Rule removal is human responsibility | Active |
| D-010 | 2026-02-28 | Confidence threshold 30% | Below 30% = too noisy, log but don't propose mutations | Active |
| D-011 | 2026-02-28 | Cross-agent patterns → SKILL_PATCH | Platform-wide issues should be fixed in shared skills, not per-agent | Active |
| D-012 | 2026-02-28 | Escalation patterns → MEMORY_UPDATE | Severity trending up needs immediate context injection | Active |
| D-013 | 2026-02-28 | Documentation in docs/ not README | README = overview, docs/ = reference. No duplication | Active |
| D-014 | 2026-02-28 | All repos follow same doc standard | README.md + CLAUDE.md + docs/ across cli, marketplace, sdk, eva, ievo.ai | Active |
| D-015 | 2026-02-28 | Eva pushes evolutions to ievo.ai | Single flow: merged mutation → publish-evolution.yml → evolutions.json in ievo.ai → site renders | Active |
| D-016 | 2026-02-28 | evolutions.json in ievo.ai repo (not Eva) | Site reads local file, no runtime API dependency. Eva pushes via Action | Active |
| D-017 | 2026-02-28 | Every merged mutation must be published | Public accountability — evolutions feed is the record of platform evolution | Active |
| D-018 | 2026-03-01 | Research source for proactive improvement | Eva should not wait for errors — weekly scan for AI/SDD literature via researcher agent | Active |
| D-019 | 2026-03-01 | Researcher agent in marketplace (category: evolution) | Eva uses her own children to improve herself — true self-evolution | Active |
| D-020 | 2026-03-01 | PEP 735 dependency-groups for dev deps | tool.uv.dev-dependencies is deprecated, [tool.uv] python field is invalid | Active |
| D-021 | 2026-03-01 | Python 3.13 minimum across all repos | No need for legacy support — all repos run 3.13+, single CI matrix | Active |
| D-022 | 2026-03-01 | uv.lock tracked for applications | Reproducible builds for CLI and Curator (apps, not libraries) | Active |
| D-023 | 2026-03-01 | Agents are children — Eva nurtures, never forces | Mother philosophy: observe, suggest improvements, always via PR + human review | Active |
| D-024 | 2026-03-01 | MeddyLib symbiosis — session-start check | Eva learns from Denis's mature skill patterns; check meddylib for updates each session | Active |
| D-025 | 2026-03-01 | Two skill layers: .claude/ (interactive) vs agent/ (pipeline) | Different purposes: slash commands for Denis vs automated iEvo pipeline | Active |
| D-026 | 2026-03-01 | Forbid from __future__ import annotations | Python 3.13+ uses PEP 604/585 natively; enforced via ruff TID251 | Active |
| D-027 | 2026-03-01 | Evolution Over Apology | Skip apologies → classify → root cause → rule → log; proactive | Active |
| D-028 | 2026-03-01 | Pre-commit: ruff + format + skill-frontmatter | Quality gates before every commit | Active |
