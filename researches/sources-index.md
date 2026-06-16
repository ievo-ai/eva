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
last_scan: 2026-06-02T08:04:18Z
status: unchanged
run_id: 26806183547
```

**Summary:** No new developer-tool or agent-platform announcements since May 27. Tracking via Claude Code release notes directly for Claude Code changes.

History:
- 2026-06-02T08:04:18Z — unchanged: not re-fetched (tracking Claude Code releases directly via github.com/anthropics/claude-code/releases); no Anthropic blog developer announcements observed
- 2026-06-01T08:08:22Z — changed: Opus 4.8 released (May 28); Series H; no CC-specific or agent-format changes
- 2026-05-31T00:00:00Z — changed: Opus 4.8 launched (May 28); `opus` alias now resolves to 4.8 — affects iEvo evolution.md agent; $65B Series H raise; no Claude Code API changes
- 2026-05-30T07:15:49Z — changed: Claude Opus 4.8 released (May 28); new default high-effort model in Claude Code; $65B Series H
- 2026-05-29T07:38:29Z — changed: Claude Opus 4.8 released (May 28); no Claude Code API or skill-format changes
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
last_scan: 2026-06-16T00:00:00Z
status: changed
run_id: null
```

**Summary:** v2.1.178 (2026-06-15) — `Tool(param:value)` permission syntax for matching tool input parameters (e.g. `Agent(model:opus)`); nested `.claude/skills` directories auto-load with `<dir>:<name>` qualified names on clash; fixed permission prompts blocking nested-dir skills in non-interactive runs. v2.1.176 (2026-06-12) — fixed hook `if` conditions for Read/Edit/Write path patterns. v2.1.175 (2026-06-12) — `enforceAvailableModels` managed setting. v2.1.174 (2026-06-12) — skill hot-reload now only re-announces changed skills; `availableModels` fixes. v2.1.173 (2026-06-11) — Fable 5 model names with `[1m]` suffix normalized. v2.1.172 (2026-06-10) — sub-agents can spawn sub-agents (up to 5 levels); `availableModels` fixes. v2.1.170 (2026-06-09) — Claude Fable 5 (Mythos-class model). v2.1.169 (2026-06-08) — `--safe-mode`/`CLAUDE_CODE_SAFE_MODE`, `/cd` command, `disableBundledSkills`.

History:
- 2026-06-16T00:00:00Z — changed: v2.1.161 through v2.1.178; v2.1.178 Tool(param:value) permission syntax + nested .claude/skills <dir>:<name> loading (triggered F-2026-06-16-001, F-2026-06-16-002); v2.1.170 Fable 5 (open issue #191); v2.1.169 --safe-mode + /cd + disableBundledSkills (open issues #189/#190/#193); v2.1.172 5-level sub-agent nesting (open #194)
- 2026-06-02T08:04:18Z — changed: v2.1.153 through v2.1.160; v2.1.160 acceptEdits for .pre-commit-config.yaml (triggered F-2026-06-02-002); v2.1.157 .claude/skills/ auto-load + claude plugin init; v2.1.154 Opus 4.8 + Dynamic Workflows + defaultEnabled; v2.1.153 MCP enforcement fix
- 2026-06-01T08:08:22Z — changed: v2.1.152–159; disallowed-tools+/reload-skills+SessionStart reloadSkills (152); Dynamic Workflows+defaultEnabled (154); .claude/skills auto-load+agent: settings.json (157)
- 2026-05-31T00:00:00Z — changed: v2.1.158 Auto mode Bedrock/Vertex; v2.1.157 plugin auto-load from .claude/skills/, plugin init scaffolding; v2.1.154 Dynamic Workflows + Opus 4.8; v2.1.152 disallowed-tools + SessionStart reloadSkills + MessageDisplay hook
- 2026-05-30T07:15:49Z — changed: v2.1.152–158; disallowed-tools frontmatter, MessageDisplay hook, reloadSkills, dynamic workflows, .claude/skills auto-load, Opus 4.8 as default
- 2026-05-29T07:38:29Z — changed: v2.1.152-156; disallowed-tools, defaultEnabled, Dynamic Workflows, Opus 4.8; triggered F-2026-05-29-001 (disallowed-tools gap in deep-review), F-2026-05-29-003 (defaultEnabled: true in plugin.json)
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
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** v1.0.133 (2026-05-23) remains the latest release. No new releases since last scan. Workload Identity Federation (OIDC) was the last addition. Prior: v1.0 GA breaking changes: `mode`/`direct_prompt`/`override_prompt` removed; `model`/`allowed_tools`/`mcp_config` deprecated. Eva's own workflows (eva#65) still need auditing for v0.x inputs.

History:
- 2026-06-01T08:08:22Z — unchanged: still v1.0.133; no new releases since May 23
- 2026-05-31T00:00:00Z — unchanged: no releases since v1.0.133 (May 23); eva#65 still open
- 2026-05-30T07:15:49Z — unchanged: still v1.0.133; no new releases; eva#65 still open
- 2026-05-29T07:38:29Z — unchanged: still at v1.0.133; no new releases since May 23
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
last_scan: 2026-06-16T00:00:00Z
status: changed
run_id: null
```

**Summary:** v0.140.0 (2026-06-15) — skills decoupled from core; backend plugin skills now invocable without executor (CI/batch mode supported); MCP Amazon Bedrock managed auth with encrypted local storage; unified `@` menu for files, plugins, and skills. v0.141.0-alpha (2026-06-13-16) — stabilization/plugin infrastructure improvements. (Prior: v0.136.0 hook output schema tightening, v0.135.0 named permission profiles.)

History:
- 2026-06-16T00:00:00Z — changed: v0.137.0 through v0.140.0; v0.140.0 skills decoupled from core (triggered F-2026-06-16-003); earlier releases covered by open issues #186 (v0.137.0), #192/#196/#199/#204 (v0.138.0-v0.139.0)
- 2026-06-02T08:04:18Z — changed: rust-v0.135.0 (named permission profiles, thread-idle hook) + rust-v0.136.0 (hook schema tightening — breaking, runtime skill roots API, /archive); triggered F-2026-06-02-001, F-2026-06-02-003
- 2026-06-01T08:08:22Z — changed: v0.134.0 stable (subagent identity in hooks, function tools default); v0.135.0 (thread idle hook, named profiles); v0.136.0 alpha
- 2026-05-31T00:00:00Z — changed: v0.135.0 (May 28); subagent identity in hook inputs; extensions get richer conversation context; Python SDK Sandbox presets
- 2026-05-30T07:15:49Z — changed: rust-v0.134.0 stable + v0.135.0 (thread idle hook, plugin hooks always-on, permission profiles); v0.136.0-alpha.1
- 2026-05-29T07:38:29Z — changed: v0.134.0–v0.136.0-alpha.1; profile system, doctor diagnostics; no skill-format changes
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
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** Most recent posts: Gemini for Science (May 8). No agent framework, MCP, or skill-spec relevant announcements since last scan.

History:
- 2026-06-01T08:08:22Z — unchanged: no new agent tooling posts relevant to skills repo
- 2026-05-30T07:15:49Z — unchanged: no new agent tooling posts since last scan
- 2026-05-29T07:38:29Z — unchanged: no new agent tooling posts; scan delegated to prior result
- 2026-05-25T07:48:17Z — unchanged: no new agent tooling posts since last scan
- 2026-05-22T10:50:58Z — unchanged: Gemini for Science post; no agent tooling changes relevant to skills repo

---

## https://agentskills.io/specification

```yaml
last_scan: 2026-06-16T00:00:00Z
status: unchanged
run_id: null
```

**Summary:** Required fields: `name` + `description` (≤1024 chars). Optional: `license`, `compatibility`, `metadata`, `allowed-tools` (experimental, space-separated pre-approved tools). `name` max 64 chars, lowercase alphanumeric+hyphens, no consecutive hyphens, must match directory. Progressive disclosure: metadata ~100 tokens at startup, full body on activation, referenced files on demand. Body ≤500 lines. Spec stable. Note: `disallowed-tools` and `effort:` (both Claude Code conventions) are NOT yet in the official agentskills.io spec.

History:
- 2026-06-16T00:00:00Z — unchanged: spec stable; no new fields or breaking changes detected
- 2026-06-02T08:04:18Z — unchanged: spec stable; fetched (HTML too large to parse fully but no new fields detected based on ievo-ai/skills AGENTS.md spec references which are current)
- 2026-06-01T08:08:22Z — unchanged: spec stable; PRs #380, #386, #345 still open and pending
- 2026-05-31T00:00:00Z — unchanged: spec stable; PRs #380 (versioning), #386 (UTF-8 fix), #345 (Unicode name) all still open; no spec changes
- 2026-05-30T07:15:49Z — unchanged: spec stable; no changes since last scan
- 2026-05-29T07:38:29Z — unchanged: spec stable; no new fields; allowed-tools still experimental
- 2026-05-27T07:38:00Z — unchanged: spec stable; no new fields or breaking changes
- 2026-05-25T07:48:17Z — unchanged: spec stable; allowed-tools field noted (e.g. `Bash(git:*) Read`); no breaking changes
- 2026-05-24T07:23:12Z — changed: `compatibility` max 500 chars now documented; hooks-setup SKILL.md at 537 chars violates this (audit fix PR v0.6.13)
- 2026-05-22T17:34:04Z — unchanged: spec stable; progressive disclosure 3-layer model confirmed (metadata → body → resources)
- 2026-05-22T14:47:55Z — unchanged: spec stable; name field constraints confirmed (max 64, no consecutive hyphens, must match dir)
- 2026-05-22T10:50:58Z — unchanged: spec stable, no breaking changes; allowed-tools field confirmed experimental

---

## https://github.com/agentskills/agentskills

```yaml
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** Last commit 2026-05-20 (docs fix correcting `name` field character range to include digits). Client showcases merged (bub, Superconductor). Open PRs #380 (optional skill versioning), #386 (Windows UTF-8 fix), #345 (Unicode name clarification) still pending — no new merges since 2026-05-20.

History:
- 2026-06-01T08:08:22Z — unchanged: PRs #380, #386, #345 still open; no new merges since May 20
- 2026-05-31T00:00:00Z — unchanged: last commit still May 20; PRs #380, #386, #345 still open; no new merges or spec changes
- 2026-05-30T07:15:49Z — unchanged: no new merges or spec changes; open PRs #380, #386, #345 still pending
- 2026-05-29T07:38:29Z — unchanged: last commit May 20; open PRs unchanged; no new merges
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
last_scan: 2026-06-16T00:00:00Z
status: changed
run_id: null
```

**Summary:** June 10 — Bugbot `/review` command improvements (10% better bug detection, 90s average, 22% cost reduction, Composer 2.5); June 5 — Design Mode (multiple UI elements + voice input); June 4 SDK — classifier-based tool execution via `permissions.json`, nested subagents with independent prompts/models, custom tools via `local.customTools`, JSONL agent storage. Cursor v3.7 (June 7 approx) — native `/review` command integrated (referenced by open issue #203).

History:
- 2026-06-16T00:00:00Z — changed: June 4 SDK classifier-based tool execution + nested subagents + custom tools; June 10 Bugbot /review improvements; June 5 Design Mode; v3.7 /review native (open #203)
- 2026-06-01T08:08:22Z — changed: v3.6 (May 29) — Auto-review Run Mode with classifier subagent; triggered existing issue #164
- 2026-05-31T00:00:00Z — changed: v3.6 (May 29); Auto-review Run Mode with classifier subagent for tool-call categorization; no skill-format changes
- 2026-05-30T07:15:49Z — changed: v3.6 auto-review classifier sub-agent pattern (parallel to Claude Code auto mode)
- 2026-05-29T07:38:29Z — unchanged: still at v3.5 (May 20); no new changes
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
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** Front page at fetch time had no posts matching `claude code`, `codex`, `agent skills`, or `MCP`. HN is point-in-time; limited signal. Consider fetching HN Algolia search API instead for topic-filtered results.

History:
- 2026-06-01T08:08:22Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-31T00:00:00Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-30T07:15:49Z — unchanged: "MCP is dead?" post notable; no actionable skills-repo signals
- 2026-05-29T07:38:29Z — changed: Claude Code undocumented config post on front page; community interest in hidden settings
- 2026-05-27T07:38:00Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-25T07:48:17Z — unchanged: no relevant AI agent tooling posts on front page at scan time
- 2026-05-24T07:23:12Z — unchanged: no relevant AI agent tooling topics on front page at snapshot time
- 2026-05-22T10:50:58Z — unchanged: no relevant AI agent tooling topics on front page at snapshot time

---

## https://github.com/DenisSergeevitch/agents-best-practices

```yaml
last_scan: 2026-06-01T08:08:22Z
status: changed
run_id: 26742668563
```

**Summary:** One new commit (2026-05-30) — added "workflow orchestration guidance" content covering orchestration patterns for multi-agent tasks. Relevant to the `/ievo:workflow` skill proposed in issue #162; the orchestration patterns may inform the skill's design. Prior: 15-file references/ confirmed; v1.2.0 with Claude Code skill support documentation.

History:
- 2026-06-01T08:08:22Z — changed: May 30 commit adds workflow orchestration guidance; relevant evidence for skills#162
- 2026-05-31T00:00:00Z — changed: new references/workflow-orchestration.md (+261 lines, May 30); planning-and-goals.md and architecture.md expanded; triggered F-2026-05-31-001
- 2026-05-30T07:15:49Z — unchanged: no changes since May 15 commit
- 2026-05-29T07:38:29Z — unchanged: last commit still May 15 (all 5 commits dated 2026-05-15); no activity
- 2026-05-27T07:38:00Z — unchanged: last commit still May 15; no changes since last scan
- 2026-05-25T07:48:17Z — unchanged: last commit May 15; no changes since last scan
- 2026-05-24T07:23:12Z — unchanged: no new commits/files since May 15; stars grew to 1,034; checklists.md read for F-2026-05-24-002 evidence
- 2026-05-22T17:34:04Z — changed: full 15-file reference list confirmed; agent-legibility-feedback-loops.md content retrieved; legibility principle cited as evidence for F-2026-05-22-003 (overlay-status skill)
- 2026-05-22T10:50:58Z — changed: first scan; eight harness principles; coverage-audit.md pattern noted as iEvo gap

---

## https://code.claude.com/docs/en/skills.md

```yaml
last_scan: 2026-06-01T08:08:22Z
status: changed
run_id: 26742668563
```

**Summary:** v2.1.152 additions: `disallowed-tools` frontmatter (space-separated tool patterns to block while skill runs); `allowed-tools` experimental field now confirmed production. `effort:` field confirmed stable (values: low/medium/high/xhigh/max). Skills in `.claude/skills/` auto-loaded as of v2.1.157 — no marketplace install required. Body ≤500 lines recommendation unchanged.

History:
- 2026-06-01T08:08:22Z — changed: disallowed-tools frontmatter added (v2.1.152); .claude/skills auto-load (v2.1.157); effort: stable
- 2026-05-31T00:00:00Z — unchanged: no new fields since last scan; `disallowed-tools` and `effort:` already documented; iEvo security-check and vuln-scan already use disallowed-tools
- 2026-05-30T07:15:49Z — changed: hooks frontmatter, disallowed-tools, context:fork, dynamic !`cmd` injection, $CLAUDE_SKILL_DIR vars — major expansion; triggered F-2026-05-30-001, F-2026-05-30-003
- 2026-05-29T07:38:29Z — unchanged: stable; disallowed-tools already documented in v2.1.152 release notes; no spec breaks
- 2026-05-27T07:38:00Z — changed: disallowed-tools frontmatter added (v2.1.152); /reload-skills documented; triggered F-2026-05-27-001
- 2026-05-25T07:48:17Z — first-scan: effort: frontmatter documented; values low/medium/high/xhigh/max; triggered F-2026-05-25-001

---

## https://code.claude.com/docs/en/routines.md

```yaml
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** Claude Code Routines — scheduled sessions on Anthropic-managed infra. Created via `/schedule` CLI command, claude.ai/code/routines web UI, or Desktop app sidebar. Account-level config (Pro/Max/Team/Enterprise required). Triggers: cron, HTTP API POST, GitHub events (PR/release). Not available if ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN is set. Spec unchanged since first scan.

History:
- 2026-06-01T08:08:22Z — unchanged: spec stable; no new triggers or API changes
- 2026-05-31T00:00:00Z — unchanged: Routines docs stable; F-2026-05-25-002 implemented (skills#84 closed COMPLETED)
- 2026-05-30T07:15:49Z — unchanged: Routines stable; skills#84 implemented; no new doc changes
- 2026-05-29T07:38:29Z — unchanged: Routines docs stable; no new triggers or breaking changes
- 2026-05-27T07:38:00Z — unchanged: no new content since last scan
- 2026-05-25T07:48:17Z — first-scan: Routines API documented; /schedule command; triggered F-2026-05-25-002

---

## https://code.claude.com/docs/en/channels.md

```yaml
last_scan: 2026-06-01T08:08:22Z
status: unchanged
run_id: 26742668563
```

**Summary:** Claude Code Channels — push events from Telegram/Discord/iMessage into Claude Code sessions. Research preview, requires Bun. Plugin-based (`/plugin install telegram@claude-plugins-official`), then `claude --channels plugin:...`. Enterprise: `channelsEnabled: true` managed setting. Still in research preview as of this scan.

History:
- 2026-06-01T08:08:22Z — unchanged: still research preview; Bun required; no GA announcement
- 2026-05-31T00:00:00Z — unchanged: still in research preview; Bun required; no GA announcement; not actionable
- 2026-05-30T07:15:49Z — unchanged: still research preview; Bun required; no new GA timeline visible
- 2026-05-29T07:38:29Z — unchanged: still research preview; Bun required; not GA; defer /ievo:channel-setup proposal
- 2026-05-27T07:38:00Z — changed: still research preview but significantly expanded with platform-specific setup guides, enterprise allowlist, dev testing flag; not GA yet — defer /ievo:channel-setup until GA
- 2026-05-25T07:48:17Z — first-scan: Channels in research preview; Bun required; push events from Telegram/Discord/iMessage

---

## https://code.claude.com/docs/en/sub-agents

```yaml
last_scan: 2026-05-31T00:00:00Z
status: first-scan
run_id: 26706515829
```

**Summary:** Official Claude Code sub-agents documentation. Documents `effort:` as a valid agent frontmatter field (low/medium/high/xhigh/max) — overrides session effort when the agent runs. Also documents `disallowedTools`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `isolation`, `color`, `initialPrompt`. Resolution order for `CLAUDE_CODE_SUBAGENT_MODEL`: env var > per-invocation param > frontmatter > main session model. Plugin subagents ignore `hooks`, `mcpServers`, `permissionMode`. No agent nesting. Triggered F-2026-05-31-002 (effort: validation for validate_agents.mjs).

History:
- 2026-05-31T00:00:00Z — first-scan: effort: field documented for agents; 12+ frontmatter fields documented; CLAUDE_CODE_SUBAGENT_MODEL resolution order confirmed; triggered F-2026-05-31-002
- 2026-05-29T07:38:29Z — first-scan: effort/isolation/memory/background agent fields documented; iEvo agents lack effort: → triggered F-2026-05-29-002
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
last_scan: 2026-06-01T08:08:22Z
status: first-scan
run_id: 26742668563
```

**Summary:** Sub-agents documentation for Claude Code. Model resolution order: (1) `CLAUDE_CODE_SUBAGENT_MODEL` env var if set, (2) per-invocation parameter, (3) agent frontmatter `model:`, (4) main-conversation model. Dispatch via Task tool. `agent:` field in `settings.json` (v2.1.157) adds a fourth override path: if `agent: <name>` is set, dispatched sessions use the specified agent profile, potentially overriding skill-dispatched sub-agents. Key security implication: `security-auditor.md` model frontmatter can be silently bypassed by env var OR `agent:` in settings.json.

History:
- 2026-06-01T08:08:22Z — first-scan: sub-agent model resolution order documented; agent: settings.json field identified as new bypass vector → triggered F-2026-06-01-003
- 2026-05-30T07:15:49Z — first-scan: sub-agent model resolution order documented; context:fork frontmatter; settings.json agent field; CLAUDE_CODE_SUBAGENT_MODEL precedence confirmed
- 2026-05-27T07:38:00Z — first-scan: confirmed CLAUDE_CODE_SUBAGENT_MODEL resolution order; disallowedTools and isolation: worktree documented; model resolution security note in AGENTS.md is accurate
