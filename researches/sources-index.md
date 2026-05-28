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
last_scan: 2026-05-28T08:00:00Z
status: unchanged
run_id: 26561249253
```

**Summary:** No new Claude Code or agent API announcements since May 22 (Project Glasswing). Prior entries: Stainless acquisition, Claude for Small Business, KPMG partnership (all pre-May-22).

History:
- 2026-05-28T08:00:00Z — unchanged: no new announcements since May 22 scan
- 2026-05-27T07:38:00Z — unchanged: no developer/agent-platform announcements; two non-technical posts (papal AI comment, Korea appointment)
- 2026-05-26T07:30:00Z — unchanged: Chris Olah article (May 25) interpretability; no Claude Code or agent API changes
- 2026-05-25T07:48:17Z — changed: Project Glasswing (May 22) security initiative; no model releases or Claude Code-specific changes
- 2026-05-24T07:23:12Z — changed: Project Glasswing announcement (May 22); no new model/Claude Code releases
- 2026-05-22T17:34:04Z — unchanged: no new announcements since 14:47 scan
- 2026-05-22T14:47:55Z — unchanged: no new Claude Code-relevant announcements since last scan
- 2026-05-22T10:50:58Z — changed: Stainless acquisition, Claude for Small Business, KPMG partnership; no model releases

---

## https://github.com/anthropics/claude-code/releases

```yaml
last_scan: 2026-05-28T08:00:00Z
status: changed
run_id: 26561249253
```

**Summary:** v2.1.152 (2026-05-27) — `disallowed-tools` frontmatter for skills (block tools while skill active); new `MessageDisplay` hook type (fires on every assistant message display); `SessionStart` hooks can return `{ reloadSkills: true, sessionTitle: "..." }`; `/reload-skills` command; auto mode no longer requires consent; `pluginSuggestionMarketplaces` managed setting. v2.1.153 (2026-05-28) — `skipLfs` option for `github`/`git` MCP plugins; status line scripts now receive `COLUMNS`/`LINES` env vars; `claude agents` autocomplete shows native commands and bundled skills. Prior: v2.1.150 internal-only.

History:
- 2026-05-28T08:00:00Z — changed: v2.1.152 disallowed-tools, MessageDisplay hook, SessionStart return fields, /reload-skills; v2.1.153 COLUMNS/LINES in status line, claude agents autocomplete
- 2026-05-27T07:38:00Z — changed: v2.1.152; `disallowed-tools` frontmatter, MessageDisplay hook, SessionStart enhancements, /reload-skills command; triggered F-2026-05-27-001, F-2026-05-27-002
- 2026-05-26T07:30:00Z — unchanged: no new releases after v2.1.150 (May 23); latest user-facing changes in v2.1.149
- 2026-05-25T07:48:17Z — changed: v2.1.149 effort: frontmatter fix, /usage per-category, Tab-completion fix; v2.1.150 internal; Routines + Channels newly documented
- 2026-05-24T07:23:12Z — changed: v2.1.149 (/usage per-category, PowerShell security fix, worktree sandbox fix, Bash find crash fix); v2.1.150 (infra only)
- 2026-05-22T17:34:04Z — unchanged: still at v2.1.148; no new releases since 14:47 scan
- 2026-05-22T14:47:55Z — unchanged: still at v2.1.148; no new releases since 10:54 scan; terminalSequence (v2.1.141) noted as evidence for hooks-setup proposal
- 2026-05-22T10:50:58Z — changed: CLAUDE_CODE_SUBAGENT_MODEL env var, /code-review breaking rename, multi-agent teams, MCP CLAUDE_PROJECT_DIR

---

## https://github.com/anthropics/claude-code-action/releases

```yaml
last_scan: 2026-05-28T08:00:00Z
status: unchanged
run_id: 26561249253
```

**Summary:** Latest v1.0.133 (2026-05-23) — Workload Identity Federation (OIDC). No new releases since May 23. Eva workflows audit (ievo-ai/eva#65) still open and unresolved.

History:
- 2026-05-28T08:00:00Z — unchanged: still at v1.0.133; no new releases since May 23
- 2026-05-27T07:38:00Z — unchanged: still at v1.0.133; no new releases
- 2026-05-26T07:30:00Z — unchanged: no new releases after v1.0.133 (May 23); eva#65 still open for workflow migration
- 2026-05-25T07:48:17Z — changed: v1.0.131–133; v1.0.133 adds OIDC Workload Identity Federation; no breaking input changes
- 2026-05-24T07:23:12Z — changed: v1.0.129-133; OIDC auth support (v1.0.130, v1.0.133); Eva workflows deferred audit still pending
- 2026-05-22T14:47:55Z — changed: v1.0 GA with breaking API; skills repo already on v1; check eva repo workflows
- 2026-05-22T10:50:58Z — error: not included in fetch batch this run; will scan next run

---

## https://docs.anthropic.com/en/docs/claude-code/overview

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Redirects to code.claude.com. Using more specific URLs (skills.md, routines.md, channels.md, sub-agents.md) for deeper tracking.

History:
- 2026-05-27T07:38:00Z — unchanged: redirects to code.claude.com; tracking sub-page URLs directly now
- 2026-05-25T07:48:17Z — changed: Routines + Channels now documented; effort: frontmatter documented in skills.md
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
last_scan: 2026-05-28T08:00:00Z
status: changed
run_id: 26561249253
```

**Summary:** v0.134.0 (May 26, stable) — added subagent identity to hook inputs + trace_id to TurnStartedEvent (SubagentStart/SubagentStop/TurnStartedEvent hooks pre-date this release, Codex Hooks GA ~May 14); `--profile` flag as primary selector with profile inheritance and runtime refresh; extension tools can access conversation history; read-only MCP tools support concurrent execution when annotated. Prior alphas (May 22–23) had no changelog.

History:
- 2026-05-28T08:00:00Z — changed: v0.134.0 stable (May 26) — subagent identity in hook inputs + trace_id on TurnStartedEvent (SubagentStart/SubagentStop/TurnStartedEvent hooks pre-date this); --profile flag; conversation history in tools → triggered F-2026-05-28-001
- 2026-05-27T07:38:00Z — changed: rust-v0.134.0 stable (May 26); `--profile` breaking change, subagent identity in hooks, concurrent read-only MCP, OAuth for MCP
- 2026-05-26T07:30:00Z — unchanged: no new releases after alpha.3 (May 23); v0.132/0.133 highlights noted
- 2026-05-25T07:48:17Z — changed: rust-v0.134.0-alpha.1/2/3 (May 22-23); Rust rewrite in alpha; no breaking skill-format changes
- 2026-05-24T07:23:12Z — unchanged: v0.133.0 still latest stable; v0.134.0-alpha.1–alpha.3 tags dropped May 22–23 with no notes
- 2026-05-22T17:34:04Z — unchanged: still at v0.133.0; no new releases since 14:47 scan
- 2026-05-22T14:47:55Z — unchanged: still at v0.133.0; no new releases since 10:54 scan
- 2026-05-22T10:50:58Z — changed: codex doctor diagnostic (v0.131), extension lifecycle hooks (v0.133), permission profiles with inheritance

---

## https://blog.google/technology/google-deepmind/

```yaml
last_scan: 2026-05-25T07:48:17Z
status: unchanged
run_id: 26389613586
```

**Summary:** Most recent posts: Gemini for Science (May 8). No agent framework, MCP, or skill-spec relevant announcements since last scan.

History:
- 2026-05-25T07:48:17Z — unchanged: no new agent tooling posts since last scan
- 2026-05-22T10:50:58Z — unchanged: Gemini for Science post; no agent tooling changes relevant to skills repo

---

## https://agentskills.io/specification

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Required fields: `name` + `description` (≤1024 chars). Optional: `license`, `compatibility`, `metadata`, `allowed-tools` (experimental, space-separated pre-approved tools). `name` max 64 chars, lowercase alphanumeric+hyphens, no consecutive hyphens, must match directory. Progressive disclosure: metadata ~100 tokens at startup, full body on activation, referenced files on demand. Body ≤500 lines. Spec stable.

History:
- 2026-05-27T07:38:00Z — unchanged: spec stable; no new fields or breaking changes
- 2026-05-25T07:48:17Z — unchanged: spec stable; allowed-tools field noted (e.g. `Bash(git:*) Read`); no breaking changes
- 2026-05-24T07:23:12Z — changed: `compatibility` max 500 chars now documented; hooks-setup SKILL.md at 537 chars violates this (audit fix PR v0.6.13)
- 2026-05-22T17:34:04Z — unchanged: spec stable; progressive disclosure 3-layer model confirmed (metadata → body → resources)
- 2026-05-22T14:47:55Z — unchanged: spec stable; name field constraints confirmed (max 64, no consecutive hyphens, must match dir)
- 2026-05-22T10:50:58Z — unchanged: spec stable, no breaking changes; allowed-tools field confirmed experimental

---

## https://github.com/agentskills/agentskills

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Last commit 2026-05-20 (docs fix correcting `name` field character range to include digits). Open PRs #380 (optional skill versioning), #386 (Windows UTF-8 fix), #345 (Unicode name clarification) still pending — no new merges since May 20.

History:
- 2026-05-27T07:38:00Z — unchanged: last commit still May 20; open PRs #345, #380, #386 still pending; no spec changes
- 2026-05-26T07:30:00Z — unchanged: 29 open issues, 13 open PRs; #380/#386/#345 still open; no new merges
- 2026-05-25T07:48:17Z — unchanged: last commit May 20; open PRs #380, #386, #345 still pending; no spec changes
- 2026-05-24T07:23:12Z — changed: new PRs #402 (ZeroClaw clients) + #403 (flowhunt-skill submission); tracked PRs #380, #386, #345 still open
- 2026-05-22T17:34:04Z — changed: client showcase PRs #377, #340, #349, #334, #332 confirmed merged; no spec-level changes; open PRs #380, #386, #345 still pending
- 2026-05-22T14:47:55Z — unchanged: same open PRs (#380, #386); no new merges since 10:54 scan; PR #345 (unicode name clarification) noted
- 2026-05-22T10:50:58Z — changed: PR #384 name-field validation fix merged; PR #380 optional skill versioning proposed; PR #386 Windows UTF-8 fix

---

## https://www.cursor.com/changelog

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Most recent entry is v3.5 (2026-05-20) — shared canvases and /loop skill. No new entries since May 20.

History:
- 2026-05-27T07:38:00Z — unchanged: most recent entry still v3.5 (May 20); no new entries
- 2026-05-26T07:30:00Z — unchanged: still at v3.5 (May 20); no new entries
- 2026-05-25T07:48:17Z — unchanged: most recent entry v3.5 (May 20); no new changes
- 2026-05-24T07:23:12Z — unchanged: no new entries since May 20
- 2026-05-22T17:34:04Z — unchanged: no new entries since 14:47 scan
- 2026-05-22T14:47:55Z — unchanged: no new entries since 10:54 scan; same v3.4/v3.5 content
- 2026-05-22T10:50:58Z — changed: Composer 2.5, Jira integration, multi-repo Automations, Dockerfile cloud dev envs

---

## https://news.ycombinator.com

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Front page at fetch time had no posts matching `claude code`, `codex`, `agent skills`, or `MCP`. HN is point-in-time; limited signal. Consider fetching HN Algolia search API instead for topic-filtered results.

History:
- 2026-05-27T07:38:00Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-25T07:48:17Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-24T07:23:12Z — unchanged: no relevant AI agent tooling topics on front page at snapshot time
- 2026-05-22T10:50:58Z — unchanged: no relevant AI agent tooling topics on front page at snapshot time

---

## https://github.com/DenisSergeevitch/agents-best-practices

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Last commit was 2026-05-15 (v1.2.0 skill release with reformatted README and Claude Code skill support documentation). No changes since May 15.

History:
- 2026-05-27T07:38:00Z — unchanged: last commit still May 15; no changes since last scan
- 2026-05-25T07:48:17Z — unchanged: last commit May 15; no changes since last scan
- 2026-05-24T07:23:12Z — unchanged: no new commits/files since May 15; stars grew to 1,034; checklists.md read for F-2026-05-24-002 evidence
- 2026-05-22T17:34:04Z — changed: full 15-file reference list confirmed; agent-legibility-feedback-loops.md content retrieved; legibility principle cited as evidence for F-2026-05-22-003 (overlay-status skill)
- 2026-05-22T10:50:58Z — changed: first scan; eight harness principles; coverage-audit.md pattern noted as iEvo gap

---

## https://code.claude.com/docs/en/skills.md

```yaml
last_scan: 2026-05-27T07:38:00Z
status: changed
run_id: 26497701957
```

**Summary:** Updated to document `disallowed-tools` in skill frontmatter (added in v2.1.152) — skills can now explicitly block specific tools during their execution, complementing `allowed-tools`. Also documents `effort:` (low/medium/high/xhigh/max), `name`, `description`, `compatibility`, `metadata`, `allowed-tools`. `/reload-skills` command documented for reloading skills without restarting Claude Code.

History:
- 2026-05-27T07:38:00Z — changed: disallowed-tools frontmatter added (v2.1.152); /reload-skills documented; triggered F-2026-05-27-001
- 2026-05-25T07:48:17Z — first-scan: effort: frontmatter documented; values low/medium/high/xhigh/max; triggered F-2026-05-25-001

---

## https://code.claude.com/docs/en/routines.md

```yaml
last_scan: 2026-05-27T07:38:00Z
status: unchanged
run_id: 26497701957
```

**Summary:** Claude Code Routines — scheduled sessions on Anthropic-managed infra. Created via `/schedule` CLI command, claude.ai/code/routines web UI, or Desktop app sidebar. Account-level config (Pro/Max/Team/Enterprise required). Triggers: cron, HTTP API POST, GitHub events (PR/release). Not available if ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN is set.

History:
- 2026-05-27T07:38:00Z — unchanged: no new content since last scan
- 2026-05-25T07:48:17Z — first-scan: Routines API documented; /schedule command; triggered F-2026-05-25-002

---

## https://code.claude.com/docs/en/channels.md

```yaml
last_scan: 2026-05-27T07:38:00Z
status: changed
run_id: 26497701957
```

**Summary:** Still research preview (not GA), still requires Bun — but significantly expanded with full setup guides for Telegram, Discord, and iMessage plugins, `allowedChannelPlugins` enterprise managed setting (allowlist model), `--dangerously-load-development-channels` flag for custom channel testing, and fakechat quickstart demo. More production-ready docs but still gated behind research preview status.

History:
- 2026-05-27T07:38:00Z — changed: still research preview but significantly expanded with platform-specific setup guides, enterprise allowlist, dev testing flag; not GA yet — defer /ievo:channel-setup until GA
- 2026-05-25T07:48:17Z — first-scan: Channels in research preview; Bun required; push events from Telegram/Discord/iMessage

---

## https://code.claude.com/docs/en/sub-agents

```yaml
last_scan: 2026-05-26T07:30:00Z
status: first-scan
run_id: 26438438877
```

**Summary:** Claude Code sub-agents docs. Model resolution order: (1) CLAUDE_CODE_SUBAGENT_MODEL env var, (2) per-invocation model parameter, (3) agent frontmatter model:, (4) main-conversation model. New features: forked subagents (experimental, CLAUDE_CODE_FORK_SUBAGENT=1) inherit full conversation context; subagent resume (continue previous work with full history); skill preloading via frontmatter; background subagent execution with auto-denial of unprompted permissions. SubagentStart + SubagentStop lifecycle hooks. CLAUDE_CODE_SUBAGENT_MODEL precedence already documented in iEvo AGENTS.md.

History:
- 2026-05-26T07:30:00Z — first-scan: model resolution order confirmed; forked subagents (experimental) noted; skill preloading via frontmatter noted; triggered awareness of missing vuln-scan orchestrator (F-2026-05-26-001)

---

## https://www.anthropic.com/research/glasswing-initial-update

```yaml
last_scan: 2026-05-26T07:30:00Z
status: first-scan
run_id: 26438438877
```

**Summary:** Project Glasswing vulnerability scanning research. Multi-phase: Mythos Preview detection → security personnel triage → fix verification → maintainer reports. Results: 1,752 vulnerabilities, 90.6% true positives (1,587), 62.4% confirmed high/critical. Infrastructure: scanning harness maps codebase + spins up scanning subagents; triage + threat modeling for prioritization. Key insight: exploit-chain validation requirement is what achieves high true-positive rate vs traditional SAST. Bottleneck: remediation lag (~2 weeks for high/critical despite fast detection).

History:
- 2026-05-26T07:30:00Z — first-scan: multi-phase orchestration architecture documented; 90.6% true-positive rate via exploit-chain validation; triggered F-2026-05-26-001 (missing vuln-scan orchestrator)

---

## https://code.claude.com/docs/en/sub-agents.md

```yaml
last_scan: 2026-05-27T07:38:00Z
status: first-scan
run_id: 26497701957
```

**Summary:** Official sub-agents documentation — full coverage of model resolution order: (1) `CLAUDE_CODE_SUBAGENT_MODEL` env var, (2) per-invocation `model` parameter, (3) agent frontmatter `model:`, (4) main conversation model. Also documents `disallowedTools` denylist in agent definitions (separate from skill-level `disallowed-tools`), `isolation: worktree` for clean-slate agent execution, persistent memory (`agent.memory` field), background mode, and `/agents` TUI. Confirms AGENTS.md security model note is accurate.

History:
- 2026-05-27T07:38:00Z — first-scan: confirmed CLAUDE_CODE_SUBAGENT_MODEL resolution order; disallowedTools and isolation: worktree documented; model resolution security note in AGENTS.md is accurate
