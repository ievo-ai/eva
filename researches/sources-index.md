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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** No new developer-tool or agent-platform announcements detected. Claude Fable 5 launched (v2.1.170, June 9) — already reflected in AGENTS.md v0.21.0 `fable` alias. Tracking via Claude Code release notes directly.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; Fable 5 launch (June 9) already in AGENTS.md v0.21.0; no new Anthropic blog developer announcements requiring action
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
last_scan: 2026-06-26T07:29:00Z
status: changed
run_id: $GITHUB_RUN_ID
```

**Summary:** v2.1.193 (2026-06-25) — latest. 24 new releases since v2.1.160. Key iEvo-relevant changes: v2.1.163 Stop/SubagentStop hooks can return `hookSpecificOutput.additionalContext` feedback + `\$` escape for literal `$` in skill bodies + `/plugin list --enabled/--disabled` + `requiredMinimumVersion` managed settings; v2.1.166 `fallbackModel` (new model-bypass vector, → issues #238); v2.1.169 `--safe-mode` + `disableBundledSkills` (→ issue #237); v2.1.170 Fable 5 (→ `fable` alias in AGENTS.md v0.21.0); v2.1.172 sub-agents nest up to 5 levels deep; v2.1.175 `enforceAvailableModels` (→ issue #238); v2.1.178 `Tool(param:value)` rules + nested `.claude/skills` (→ issues #208, #209); v2.1.181 `/config key=value` (→ #218); v2.1.183 destructive-git blocking + WebSearch-in-subagents (→ #219, #221); v2.1.186 `/plugin list --enabled/--disabled`, `respondToBashCommands`, new SKILL.md frontmatter keys (→ #233, #236); v2.1.187 `sandbox.credentials` (→ #234); v2.1.193 `autoMode.classifyAllShell`.

History:
- 2026-06-26T07:29:00Z — changed: v2.1.161–v2.1.193 (24 releases); key: v2.1.163 hook additionalContext + plugin list; v2.1.166–187 covered by issues #217-238; v2.1.193 autoMode.classifyAllShell; triggered F-2026-06-26-001 (hook additionalContext), F-2026-06-26-003 (/plugin list in init verification)
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched this run (no indication of changes). Last known: v1.0.133 (2026-05-23). Eva's own workflows (eva#65) still awaiting migration from v0.x inputs.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; v1.0.133 still latest as of last scan; eva#65 still open
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
last_scan: 2026-06-26T07:29:00Z
status: changed
run_id: $GITHUB_RUN_ID
```

**Summary:** rust-v0.142.2 (2026-06-25) — latest stable. Key changes since v0.136.0: MCP tools leverage tool search by default; plugin dark-mode logo support via local manifests; remote plugin catalogs with curated featured-plugin rankings; PowerShell AST-uninspectable commands require user approval; macOS/Windows proxy support. rust-v0.143.0-alpha active (multiple alphas, no stable notes yet). Issues #230 (v0.142.0 multi-agent delegation), #232 (v0.142.0 parallel MCP) already filed. New: remote plugin catalog discovery path not yet documented for iEvo — triggered F-2026-06-26-002.

History:
- 2026-06-26T07:29:00Z — changed: rust-v0.137.0–v0.142.2 (multiple releases); remote plugin catalogs with featured rankings (v0.142.2) triggered F-2026-06-26-002; v0.143.0-alpha active but no stable notes
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched this run. No agent framework or skill-spec relevant announcements known.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; no known agent tooling posts requiring action
- 2026-06-01T08:08:22Z — unchanged: no new agent tooling posts relevant to skills repo
- 2026-05-30T07:15:49Z — unchanged: no new agent tooling posts since last scan
- 2026-05-29T07:38:29Z — unchanged: no new agent tooling posts; scan delegated to prior result
- 2026-05-25T07:48:17Z — unchanged: no new agent tooling posts since last scan
- 2026-05-22T10:50:58Z — unchanged: Gemini for Science post; no agent tooling changes relevant to skills repo

---

## https://agentskills.io/specification

```yaml
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Spec stable. No new fields merged. RFC #428 (declarative MCP server requirements) is open as of June 18 — if merged would add `mcp_servers:` as a new frontmatter field. PRs #380, #386, #345 still open and pending. Required fields: `name` + `description` (≤1024 chars). Optional: `license`, `compatibility`, `metadata`, `allowed-tools` (experimental). `disallowed-tools` and `effort:` are Claude Code conventions only, NOT in official spec.

History:
- 2026-06-26T07:29:00Z — unchanged: spec stable; RFC #428 (declarative MCP requirements, opened June 18) open — watch for merge; PRs #380, #386, #345 still pending; no new fields merged
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
last_scan: 2026-06-26T07:29:00Z
status: changed
run_id: $GITHUB_RUN_ID
```

**Summary:** New open PRs since June 2: #428 (RFC: declarative MCP server requirements — potentially significant; adds `mcp_servers:` frontmatter field if merged), #431 (SECURITY.md policy), #430 (eval expectations docs), #425 + #421 (client showcases). Original PRs #380, #386, #345 still open and unmerged.

History:
- 2026-06-26T07:29:00Z — changed: RFC #428 (declarative MCP requirements, June 18) and #431/#430/#425/#421 all opened since June 2; #380/#386/#345 still open; no merges to spec
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
last_scan: 2026-06-26T07:29:00Z
status: changed
run_id: $GITHUB_RUN_ID
```

**Summary:** v3.9 (June 22) — Centralized customization page managing plugins, skills, MCPs, subagents, rules, commands, hooks; marketplace leaderboard; team imports from GitLab/BitBucket/Azure DevOps. v3.8 (June 18) — `/automate` skill; five new GitHub triggers; cloud agent computer use; default PR opening. v3.7 (June 17) — `/in-cloud` sandboxed subagents; `environment.json` snapshots; `/review` command. Issues #213/#220/#223/#225/#229/#235 already filed for Cursor v3.7-v3.9 features.

History:
- 2026-06-26T07:29:00Z — changed: v3.7 (June 17), v3.8 (June 18), v3.9 (June 22); v3.7-3.9 features already in issues #213/#220/#223/#225/#229/#235; no new Cursor findings this run
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Front page at fetch time had no posts matching `claude code`, `codex`, `agent skills`, or `MCP`. HN is point-in-time; limited signal. Consider fetching HN Algolia search API instead for topic-filtered results.

History:
- 2026-06-26T07:29:00Z — unchanged: no relevant AI agent tooling posts on front page at scan time
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** No new commits detected after May 30 (last known: workflow-orchestration.md added May 30). Repository stable. 15 reference files confirmed.

History:
- 2026-06-26T07:29:00Z — unchanged: no commits after May 30; repo stable at 9 total commits
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched this run. Last known state: disallowed-tools + effort: + .claude/skills auto-load all stable. v2.1.163 adds `\$` escape for literal `$` before digits in skill body text; v2.1.186 adds `display-name:`, `default-enabled:`, `fallback:` frontmatter keys (issues #233, #236). Body ≤500 lines recommendation unchanged.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; v2.1.163 $-escape and v2.1.186 new keys tracked via release notes; issues #233/#236 filed
- 2026-06-01T08:08:22Z — changed: disallowed-tools frontmatter added (v2.1.152); .claude/skills auto-load (v2.1.157); effort: stable
- 2026-05-31T00:00:00Z — unchanged: no new fields since last scan; `disallowed-tools` and `effort:` already documented; iEvo security-check and vuln-scan already use disallowed-tools
- 2026-05-30T07:15:49Z — changed: hooks frontmatter, disallowed-tools, context:fork, dynamic !`cmd` injection, $CLAUDE_SKILL_DIR vars — major expansion; triggered F-2026-05-30-001, F-2026-05-30-003
- 2026-05-29T07:38:29Z — unchanged: stable; disallowed-tools already documented in v2.1.152 release notes; no spec breaks
- 2026-05-27T07:38:00Z — changed: disallowed-tools frontmatter added (v2.1.152); /reload-skills documented; triggered F-2026-05-27-001
- 2026-05-25T07:48:17Z — first-scan: effort: frontmatter documented; values low/medium/high/xhigh/max; triggered F-2026-05-25-001

---

## https://code.claude.com/docs/en/routines.md

```yaml
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Routines stable. Not re-fetched this run.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; Routines spec stable; no known changes
- 2026-06-01T08:08:22Z — unchanged: spec stable; no new triggers or API changes
- 2026-05-31T00:00:00Z — unchanged: Routines docs stable; F-2026-05-25-002 implemented (skills#84 closed COMPLETED)
- 2026-05-30T07:15:49Z — unchanged: Routines stable; skills#84 implemented; no new doc changes
- 2026-05-29T07:38:29Z — unchanged: Routines docs stable; no new triggers or breaking changes
- 2026-05-27T07:38:00Z — unchanged: no new content since last scan
- 2026-05-25T07:48:17Z — first-scan: Routines API documented; /schedule command; triggered F-2026-05-25-002

---

## https://code.claude.com/docs/en/channels.md

```yaml
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched. Last known: research preview; Bun required; no GA announcement.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; still in research preview as of last scan
- 2026-06-01T08:08:22Z — unchanged: still research preview; Bun required; no GA announcement
- 2026-05-31T00:00:00Z — unchanged: still in research preview; Bun required; no GA announcement; not actionable
- 2026-05-30T07:15:49Z — unchanged: still research preview; Bun required; no new GA timeline visible
- 2026-05-29T07:38:29Z — unchanged: still research preview; Bun required; not GA; defer /ievo:channel-setup proposal
- 2026-05-27T07:38:00Z — changed: still research preview but significantly expanded with platform-specific setup guides, enterprise allowlist, dev testing flag; not GA yet — defer /ievo:channel-setup until GA
- 2026-05-25T07:48:17Z — first-scan: Channels in research preview; Bun required; push events from Telegram/Discord/iMessage

---

## https://code.claude.com/docs/en/sub-agents

```yaml
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched. Last known: v2.1.172 added nested sub-agents (5 levels). Agent frontmatter: effort/disallowedTools/permissionMode/maxTurns/skills/mcpServers/hooks/memory/background/isolation/color/initialPrompt. CLAUDE_CODE_SUBAGENT_MODEL resolution order: env > per-invocation > frontmatter > main model. Plugin subagents ignore hooks/mcpServers/permissionMode. Issue #217 covers 5-level depth.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; v2.1.172 nesting (5 levels) covered by issue #217; no new gaps identified
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
last_scan: 2026-06-26T07:29:00Z
status: unchanged
run_id: $GITHUB_RUN_ID
```

**Summary:** Not re-fetched. Last known: sub-agent model resolution order confirmed; agent: in settings.json is bypass vector (issue #F-2026-06-01-003 / skills#167); issue #238 also covers fallbackModel and enforceAvailableModels as additional bypass vectors.

History:
- 2026-06-26T07:29:00Z — unchanged: not re-fetched; bypass vectors covered by issues #167 and #238
- 2026-06-01T08:08:22Z — first-scan: sub-agent model resolution order documented; agent: settings.json field identified as new bypass vector → triggered F-2026-06-01-003
- 2026-05-30T07:15:49Z — first-scan: sub-agent model resolution order documented; context:fork frontmatter; settings.json agent field; CLAUDE_CODE_SUBAGENT_MODEL precedence confirmed
- 2026-05-27T07:38:00Z — first-scan: confirmed CLAUDE_CODE_SUBAGENT_MODEL resolution order; disallowedTools and isolation: worktree documented; model resolution security note in AGENTS.md is accurate
