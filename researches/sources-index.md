# Sources Index

Append-only log of external news / docs / release sources Eva scans during research runs (Step 4 of `.github/workflows/eva-research.yml`).

## Format

Each level-2 heading (`## <URL>`) is one source. Inside the section:

1. A ` ```yaml ` fenced block with the latest scan metadata
2. A `**Summary:**` line — the most recent observation
3. A `History:` bulleted list — chronological scan log, newest at top

YAML schema (required keys, future pre-commit may enforce):

```yaml
last_scan: <ISO 8601 UTC timestamp or "never">
status: <first-scan | changed | unchanged | error>
run_id: <GitHub Actions run ID or null>
```

## How Eva uses this file per run

- **Pre-scan (Step 1):** read each URL section to know the prior state (status, last summary). Build a diff map.
- **Post-scan (Step 4):** for each URL scanned, update the YAML block atop the section AND prepend a new entry to History. Use the `Edit` tool to modify only the relevant section — never rewrite the whole file.
- **New URLs:** if you find a source not yet listed, add a new section at the bottom following the same format.

## Status semantics

- `first-scan` — bootstrap entry, never visited yet
- `changed` — content differs from last scan (worth deep summary)
- `unchanged` — content matches last scan (brief note, skip deep dive)
- `error` — fetch failed, 404, rate-limited, or otherwise unavailable

---

## https://www.anthropic.com/news

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Anthropic acquired Stainless (May 18, likely impacting API/SDK tooling), launched Claude for Small Business (May 13), and announced KPMG strategic partnership deploying Claude to 276,000+ employees (May 19). No model releases or Claude Code-specific breaking changes in the window.

History:
- 2026-05-22T14:47:55Z — unchanged: no new Claude Code-relevant announcements since last scan
- 2026-05-22T10:50:58Z — changed: Stainless acquisition, Claude for Small Business, KPMG partnership; no model releases

---

## https://github.com/anthropics/claude-code/releases

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Very active cadence — 10 releases (v2.1.139–v2.1.148) in 14-day window. Key new features: `CLAUDE_CODE_SUBAGENT_MODEL` env var (operator-level model override for subagents — **potential security-auditor impact**), `/code-review` command (replaces `/simplify` — BREAKING rename), `claude agents` unified dashboard, `/goal` autonomous completion, MCP stdio now receives `CLAUDE_PROJECT_DIR`, hook `args: string[]` exec-form support (v2.1.139), `terminalSequence` hook field (v2.1.141), multi-agent team orchestration with agent ID tracking in OTEL.

History:
- 2026-05-22T14:47:55Z — unchanged: still at v2.1.148; no new releases since 10:54 scan; terminalSequence (v2.1.141) noted as evidence for hooks-setup proposal
- 2026-05-22T10:50:58Z — changed: CLAUDE_CODE_SUBAGENT_MODEL env var, /code-review breaking rename, multi-agent teams, MCP CLAUDE_PROJECT_DIR

---

## https://github.com/anthropics/claude-code-action/releases

```yaml
last_scan: 2026-05-22T14:47:55Z
status: changed
run_id: 26294170594
```

**Summary:** v1.0 GA released (breaking changes from v0.x): `mode`/`direct_prompt`/`override_prompt` removed — replaced by single `prompt` input; `custom_instructions`/`model`/`allowed_tools`/`mcp_config` deprecated — replaced by `claude_args`. Skills repo already uses `@v1` (both `claude-code-review.yml` and `claude.yml`) — no action needed there. v1.0.130: Workload Identity Federation (OIDC) support added. Eva's own eva-review-pr.yml and similar workflows should be verified against v1.0 migration guide.

History:
- 2026-05-22T14:47:55Z — changed: v1.0 GA with breaking API; skills repo already on v1; check eva repo workflows
- 2026-05-22T10:50:58Z — error: not included in fetch batch this run; will scan next run

---

## https://docs.anthropic.com/en/docs/claude-code/overview

```yaml
last_scan: 2026-05-22T10:50:58Z
status: changed
run_id: 26283289533
```

**Summary:** Docs moved to code.claude.com (redirects cleanly). Overview now prominently features Agent SDK, Skills & Hooks, Routines/scheduling, Remote Control (cross-platform session mobility), and MCP integrations (Google Drive, Jira, Slack). Auto memory and Agent teams listed as current capabilities.

History:
- 2026-05-22T10:50:58Z — changed: docs migrated to code.claude.com; Agent SDK, Skills & Hooks, Routines, Remote Control added to overview

---

## https://openai.com/index/news/

```yaml
last_scan: 2026-05-22T10:50:58Z
status: error
run_id: 26283289533
```

**Summary:** Consistently returns HTTP 403 to automated fetches. Use `github.com/openai/codex/releases` as the Codex signal source instead.

History:
- 2026-05-22T10:50:58Z — error: HTTP 403 Forbidden; blocked to automated fetchers

---

## https://github.com/openai/codex/releases

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Three releases in the window (v0.131–v0.133): v0.131.0 (May 18) — unified `@` mentions, plugin marketplace commands, `codex doctor` diagnostic tool; v0.132.0 (May 20) — Python SDK auth, simplified turn APIs, `--output-schema`; v0.133.0 (May 21) — goals by default with dedicated storage, **extension lifecycle hooks** (subagent start/stop + tool execution), expanded permission profiles with inheritance. Strong trend toward autonomous orchestration and policy-based access control.

History:
- 2026-05-22T14:47:55Z — unchanged: still at v0.133.0; no new releases since 10:54 scan
- 2026-05-22T10:50:58Z — changed: codex doctor diagnostic (v0.131), extension lifecycle hooks (v0.133), permission profiles with inheritance

---

## https://blog.google/technology/google-deepmind/

```yaml
last_scan: 2026-05-22T10:50:58Z
status: unchanged
run_id: 26283289533
```

**Summary:** Most recent post in window: "Gemini for Science" (May 8) — AI tools for scientific research. No agent framework, MCP, or skill-spec relevant announcements visible on the blog index.

History:
- 2026-05-22T10:50:58Z — unchanged: Gemini for Science post; no agent tooling changes relevant to skills repo

---

## https://agentskills.io/specification

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Required fields: `name` + `description` (≤1024 chars). Optional: `license`, `compatibility`, `metadata`, `allowed-tools` (experimental). `name` must be max 64 chars, lowercase alphanumeric + hyphens, no consecutive hyphens, must match directory name. Spec emphasizes progressive disclosure (metadata ~100 tokens at startup, full body on activation, referenced files on demand) and body ≤500 lines. No breaking changes documented.

History:
- 2026-05-22T14:47:55Z — unchanged: spec stable; name field constraints confirmed (max 64, no consecutive hyphens, must match dir)
- 2026-05-22T10:50:58Z — unchanged: spec stable, no breaking changes; allowed-tools field confirmed experimental

---

## https://github.com/agentskills/agentskills

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Active development in window. PR #384 (May 20, MERGED) — fixed `name` field alphanumeric range validation in spec. PR #386 (May 19) — Windows UTF-8 fix in `skills-ref` validation tool. New client showcases: Superconductor, Vita, Tabnine, bub (May 19–20). Open (not merged): PR #380 proposes optional skill versioning in `.well-known` spec; PR #254 adds `.well-known` URI spec itself. PR #345 open — clarifying Unicode in skill name (no consecutive hyphens rule).

History:
- 2026-05-22T14:47:55Z — unchanged: same open PRs (#380, #386); no new merges since 10:54 scan; PR #345 (unicode name clarification) noted
- 2026-05-22T10:50:58Z — changed: PR #384 name-field validation fix merged; PR #380 optional skill versioning proposed; PR #386 Windows UTF-8 fix

---

## https://www.cursor.com/changelog

```yaml
last_scan: 2026-05-22T14:47:55Z
status: unchanged
run_id: 26294170594
```

**Summary:** Notable May 8–22: Composer 2.5 (May 18, better long-task performance), Cursor in Jira (May 19 — `@Cursor` mentions trigger cloud agents from tickets), multi-repo and no-repo Automations in Agents window (May 20), v3.4 (May 13 — Dockerfile-based cloud agent dev environments, 70% faster cached builds, MCP/OAuth fixes). Strong trend toward autonomous multi-repo agent orchestration and third-party workflow integrations.

History:
- 2026-05-22T14:47:55Z — unchanged: no new entries since 10:54 scan; same v3.4/v3.5 content
- 2026-05-22T10:50:58Z — changed: Composer 2.5, Jira integration, multi-repo Automations, Dockerfile cloud dev envs

---

## https://news.ycombinator.com

```yaml
last_scan: 2026-05-22T10:50:58Z
status: unchanged
run_id: 26283289533
```

**Summary:** Front page at fetch time had no posts matching `claude code`, `codex`, `agent skills`, or `MCP`. HN is point-in-time; limited signal from a single snapshot. Consider fetching HN Algolia search API instead for topic-filtered results.

History:
- 2026-05-22T10:50:58Z — unchanged: no relevant AI agent tooling topics on front page at snapshot time

---

## https://github.com/DenisSergeevitch/agents-best-practices

```yaml
last_scan: 2026-05-22T10:50:58Z
status: changed
run_id: 26283289533
```

**Summary:** Provider-neutral agent skill best-practices repo (~950 stars, agentskills.io-compatible). Defines eight core harness principles: harness acts/model proposes, every tool call gets a result, risk-tiered loop design, draft-vs-commit separation, selective context construction, runtime budgets, progressive skill disclosure, failure-driven harness features. Ships 13+ structured reference guides in `references/` and a formal `coverage-audit.md` for gap tracking. Key patterns iEvo lacks explicitly: **runtime budgets as product requirements** (step/time/token/cost/tool-call limits) and a **formal coverage-audit file**.

History:
- 2026-05-22T10:50:58Z — changed: first scan; eight harness principles; coverage-audit.md pattern noted as iEvo gap
