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
