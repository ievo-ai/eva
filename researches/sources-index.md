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
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
```

**Summary:** Still no items newer than Jul 2, 2026 ("Fable 5's cyber safeguards and our jailbreak framework") relevant to Claude Code or agent-skill format. A Jul 6 Alberta cybersecurity case study appeared but is not developer-tool/agent-capability relevant.

History:
- 2026-07-07T10:00:00Z — unchanged: re-fetched; Jul 6 Alberta cybersecurity case study noted but not iEvo-relevant; still Jul 2 "Fable 5 cyber safeguards" as newest agent/CC-relevant item
- 2026-07-06T10:51:10Z — unchanged: re-fetched, still Jul 2 "Fable 5 cyber safeguards" as newest item; no iEvo action
- 2026-07-05T00:00:00Z — changed: Jul 2 "Fable 5 cyber safeguards + jailbreak framework" post added; non-technical, no iEvo action
- 2026-07-04T08:49:33Z — unchanged: re-fetched; same June 30 items (Sonnet 5, Claude Science, Fable 5 redeployment — returns globally July 1 with a cross-industry jailbreak-severity framework); nothing new since July 1 scan
- 2026-07-01T00:00:00Z — changed: Claude Sonnet 5 (June 30) — new default model, 1M context, promo pricing; Claude Science + Fable 5 redeployment also June 30; no CC-specific or skill-format changes; `sonnet` alias auto-resolves, no iEvo action needed
- 2026-06-30T00:00:00Z — changed: Claude Tag (June 23) — team collaboration feature; Services Track + Partner Hub (June 3); no model releases or CC-specific changes
- 2026-06-27T07:21:43Z — unchanged: not re-fetched; tracking Claude Code releases directly; no evidence of new Anthropic blog announcements since last scan
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
last_scan: 2026-07-07T10:00:00Z
status: changed
run_id: 28857232826
```

**Summary:** v2.1.202 (July 6, 22:51 UTC) — dynamic-workflow-size `/config` setting, OTel `workflow.run_id`/`workflow.name` attributes, and a fix for re-invoking an already-loaded skill appending a duplicate copy of its instructions to context (internal CC context-management fix, not a SKILL.md/frontmatter surface change). No new SKILL.md/agent frontmatter fields; not iEvo-actionable.

History:
- 2026-07-07T10:00:00Z — changed: v2.1.202 (July 6) — dynamic workflow size config, OTel workflow attributes, duplicate-skill-instructions-on-reinvoke fix, various CLI/Remote-Control bugfixes; no new frontmatter, no iEvo action
- 2026-07-06T10:51:10Z — unchanged: re-confirmed, still v2.1.201, no new release since July 3
- 2026-07-05T00:00:00Z — unchanged: re-confirmed via `gh api`, still v2.1.201, no new release since July 3
- 2026-07-04T08:49:33Z — changed: v2.1.200/v2.1.201 (July 3) — AskUserQuestion no-auto-continue default, "default"→"Manual" permission-mode rename (alias kept), background-agent daemon fixes; no new frontmatter, no iEvo action
- 2026-07-03T00:00:00Z — changed: v2.1.199 (July 2) — hook stderr visibility fix, SendMessage re-spawn misrouting fix, subagent error-propagation fixes, stacked slash-skill invocation (up to 5); no new frontmatter fields, no iEvo action
- 2026-07-02T09:10:00Z — unchanged: re-confirmed ~2h after prior scan, still v2.1.198, no newer release
- 2026-07-02T07:21:05Z — changed: v2.1.198 (July 1) — Notification hook agent_needs_input/agent_completed matchers (triggered F-2026-07-02-001); malformed SKILL.md frontmatter graceful degradation; Explore agent model inheritance; background agents auto-PR on finish
- 2026-07-01T00:00:00Z — changed: v2.1.197 (June 30) — Sonnet 5 default model, 1M context; v2.1.196 detail confirmed: sandbox.credentials setting, destructive-git auto-mode block, mcp login/logout commands, display-name/default-enabled/fallback now case-insensitive (kebab/snake/camel)
- 2026-06-30T00:00:00Z — changed: v2.1.196 (June 29); ${CLAUDE_PROJECT_DIR} skill variable; MCP untrusted-workspace spawn restriction; disable-model-invocation prevents scheduled task runs; hook matcher hyphen exact-match confirmed fixed
- 2026-06-29T14:15:20Z — unchanged: v2.1.195 still latest (June 26); no new releases since previous scan
- 2026-06-27T07:21:43Z — changed: v2.1.161–v2.1.195; v2.1.195 hook matcher exact-match for hyphenated names (triggered F-2026-06-27-001); v2.1.193 autoMode.classifyAllShell + OTel event; v2.1.187 sandbox.credentials; v2.1.186 display-name/default-enabled/fallback frontmatter; v2.1.183 destructive-git blocks + WebSearch subagents; v2.1.181 /config key=value
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
last_scan: 2026-07-07T10:00:00Z
status: changed
run_id: 28857232826
```

**Summary:** v1.0.166 (July 6) — routine patches (buffered-comment handling, co-author email format, symlinked CLAUDE.md restore fix, repeated add-dir flag preservation, curl-failure propagation in install pipeline). No new/removed inputs; eva#65 remains resolved+closed, no action.

History:
- 2026-07-07T10:00:00Z — changed: v1.0.166 (July 6) — routine patches, no input schema changes; eva#65 stays closed
- 2026-07-06T10:51:10Z — unchanged: re-confirmed, still v1.0.165, no new release
- 2026-07-05T00:00:00Z — unchanged: re-confirmed via `gh api`, still v1.0.165, no new release
- 2026-07-04T08:49:33Z — changed: v1.0.164/v1.0.165 (July 3), empty release bodies, routine patches; no action
- 2026-07-03T00:00:00Z — changed: v1.0.163 (July 2) minor patch; floating `v1` tag re-confirmed as a non-signal (same ambiguous-date GA content as prior scans); eva#65 stays closed, no new action
- 2026-07-02T09:10:00Z — unchanged: re-confirmed ~2h after prior scan, still v1.0.162; page also shows a floating `v1` major-version tag (ambiguous "26 Aug" date, no year) pointing at the same commit — not a new release, noted for future scans to avoid a false "changed" read
- 2026-07-02T07:21:05Z — changed: v1.0.162 (July 1) — agent-approval-check composite action; eva#65 resolved+closed this run after direct verification (grep confirmed zero deprecated inputs across all eva workflows)
- 2026-07-01T00:00:00Z — changed: v1.0.161 (June 30) patch release; eva#65 still open, 7th consecutive deferral, escalated
- 2026-06-30T00:00:00Z — changed: v1.0.134–v1.0.160 since last scan; v1.0.160 unified interface (automatic mode detection); eva#65 still open + overdue
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
last_scan: 2026-07-01T00:00:00Z
status: unchanged
run_id: 28450000000
```

**Summary:** Still 301-redirects to code.claude.com/docs/en/overview. Using more specific URLs (skills.md, routines.md, channels.md, sub-agents.md) for deeper tracking.

History:
- 2026-07-01T00:00:00Z — unchanged: still 301-redirects to code.claude.com/docs/en/overview
- 2026-05-27T07:38:00Z — unchanged: redirects to code.claude.com; tracking sub-page URLs directly now
- 2026-05-25T07:48:17Z — changed: Routines + Channels now documented; effort: frontmatter documented in skills.md
- 2026-05-22T10:50:58Z — changed: docs migrated to code.claude.com; Agent SDK, Skills & Hooks, Routines, Remote Control added to overview

---

## https://openai.com/index/news/

```yaml
last_scan: 2026-07-01T00:00:00Z
status: error
run_id: 28450000000
```

**Summary:** Still consistently returns HTTP 403 to automated fetches. Use `github.com/openai/codex/releases` as the Codex signal source instead.

History:
- 2026-07-01T00:00:00Z — error: still HTTP 403 Forbidden
- 2026-05-22T10:50:58Z — error: HTTP 403 Forbidden; blocked to automated fetchers

---

## https://github.com/openai/codex/releases

```yaml
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
```

**Summary:** v0.142.5 (2026-07-01) still latest stable. Alpha line now at alpha.38 (July 7) as newest pre-release — 3 more builds since alpha.36 (July 5), still zero published changelogs across the entire run. No stable v0.143.0 yet; no hook/MCP/skill-format changes.

History:
- 2026-07-07T10:00:00Z — unchanged: still v0.142.5 stable; alpha line advanced to alpha.38 (July 7), still no changelogs across 38 pre-release builds; no hook/MCP/skill-format content
- 2026-07-06T10:51:10Z — unchanged: still v0.142.5 stable; alpha.36 still newest pre-release; no changelogs, no hook/MCP/skill-format content
- 2026-07-05T00:00:00Z — unchanged: still v0.142.5 stable; alpha line resumed (alpha.36, July 5) after the brief pause noted July 4; still no changelogs
- 2026-07-04T08:49:33Z — unchanged: still v0.142.5 stable / alpha.35 (no new alpha since July 3); no stable v0.143.0, alpha line paused
- 2026-07-03T00:00:00Z — unchanged: still v0.142.5 stable; alpha line advanced to alpha.35 (July 3), still no changelog; no stable v0.143.0
- 2026-07-02T09:10:00Z — unchanged: re-confirmed ~2h after prior scan, still v0.142.5 stable / alpha.33 pre-release
- 2026-07-02T07:21:05Z — unchanged: v0.142.5 still latest stable; v0.143.0-alpha.33 (July 2) still pre-release, no changelog; no hook/MCP/skill-format changes
- 2026-07-01T00:00:00Z — changed: v0.142.5 (Jul 1, WebSocket logging fix); v0.143.0-alpha.32 (Jul 1) still pre-release; no stable v0.143.0
- 2026-06-30T00:00:00Z — unchanged: no stable releases since rust-v0.142.4; alpha.31 still pre-release with no changelog
- 2026-06-29T14:15:20Z — changed: rust-v0.142.4 (June 29, maintenance-only); v0.143.0-alpha.21–alpha.29 pre-release series (no changelogs); watching for v0.143.0 stable
- 2026-06-27T07:21:43Z — changed: rust-v0.137.0 through rust-v0.142.3; v0.142.2 remote plugin catalog curated rankings (triggered F-2026-06-27-003); v0.142.0 multi-agent delegation + /import from CC; v0.141.0 per-thread MCP + PostToolUse code-mode fix; v0.140.0 /import from Claude Code
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
last_scan: 2026-07-01T00:00:00Z
status: unchanged
run_id: 28450000000
```

**Summary:** No posts relevant to AI agent frameworks, MCP, tool use, or agent skill specifications. Page shows only a "Gemini for Science" feature, unrelated to agent tooling.

History:
- 2026-07-01T00:00:00Z — unchanged: only "Gemini for Science" visible; no agent tooling posts
- 2026-06-30T00:00:00Z — unchanged: no relevant agent tooling posts in June 2026
- 2026-06-01T08:08:22Z — unchanged: no new agent tooling posts relevant to skills repo
- 2026-05-30T07:15:49Z — unchanged: no new agent tooling posts since last scan
- 2026-05-29T07:38:29Z — unchanged: no new agent tooling posts; scan delegated to prior result
- 2026-05-25T07:48:17Z — unchanged: no new agent tooling posts since last scan
- 2026-05-22T10:50:58Z — unchanged: Gemini for Science post; no agent tooling changes relevant to skills repo

---

## https://agentskills.io/specification

```yaml
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
```

**Summary:** Same 6-field structure re-confirmed (name, description, license, compatibility, metadata, allowed-tools). No spec changes. PR status re-queried via `gh api` this run: #380/#386/#345 still open+unmerged; no new merges since #446.

History:
- 2026-07-07T10:00:00Z — unchanged: full spec re-read, same 6 fields; #380/#386/#345 re-confirmed open+unmerged via gh api; no new merges since #446
- 2026-07-06T10:51:10Z — unchanged: full spec re-read, same 6 fields, same constraints (name ≤64/lowercase/hyphens, description ≤1024, compatibility ≤500)
- 2026-07-05T00:00:00Z — unchanged: full spec re-read, same 6 fields; #380/#345 re-confirmed open+unmerged via gh api
- 2026-07-04T08:49:33Z — unchanged: full spec re-read, same 6 fields (name, description, license, compatibility, metadata, allowed-tools); no versioning/MCP-requirements/disable-model-invocation additions
- 2026-07-03T00:00:00Z — unchanged: full spec re-read, same 6 fields; PRs #380/#386/#345 re-confirmed open+unmerged via gh api; newest PRs (#445-449) are ecosystem-listing/docs only, no spec impact
- 2026-07-01T00:00:00Z — unchanged: full spec re-read, same 6 fields; PRs #380/#386/#345 confirmed still open (not merged) via gh api
- 2026-06-29T14:15:20Z — unchanged: spec stable; no new fields or constraints; same 6-field structure confirmed
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
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
```

**Summary:** No new merges since #446 (July 1, cosmetic). #380/#386/#345 still open, unmerged. Newest open PRs (#445/447/448/449) are ecosystem-listing/docs only, no spec impact.

History:
- 2026-07-07T10:00:00Z — unchanged: #380/#386/#345 re-verified open+unmerged via gh api; no new merges since #446
- 2026-07-05T00:00:00Z — unchanged: #380/#345 re-verified open+unmerged via gh api; no new merges since #446
- 2026-07-04T08:49:33Z — unchanged: #380/#386/#345 re-verified open+unmerged via gh api; noted PR #428 "RFC: declarative MCP server requirements for Agent Skills" closed WITHOUT merge — the idea is dead upstream for now, don't treat as spec signal
- 2026-07-03T00:00:00Z — unchanged: #380/#386/#345 re-verified open+unmerged; #446 merged (cosmetic logo scaling); #445/447/448/449 open (listings/docs only, no spec impact)
- 2026-07-02T07:21:05Z — unchanged: #380/#386/#345 re-verified open+unmerged via gh api; no new merges since #421
- 2026-07-01T00:00:00Z — changed: PR #421 merged June 30 (client showcase entry only, no spec impact); #380/#386/#345 still open per gh api
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
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
note: "Site now labels the June 30 Team-MCP/org-marketplace-scoping content as its own 'v3.10' entry rather than folding it into v3.9 as prior scans read it — same substance already noted July 1/2 (Cursor-client-only, not agentskills.io-relevant, skills#235 sufficient). Not a new signal, just a version-numbering relabel upstream; no new finding."
```

**Summary:** Cursor's site now shows "v3.10" (June 30) for Team MCPs distribution + organization-group marketplace access — this is the SAME content already observed July 1/2 as part of "v3.9 gained ... Team MCP/org-marketplace scoping (June 30)"; no new information, just a retroactive version-number relabel on Cursor's own changelog page. Still Cursor-client-only, not iEvo-actionable.

History:
- 2026-07-07T10:00:00Z — unchanged (relabeled): site now shows "v3.10" for the June 30 Team-MCP content already noted under v3.9 in prior scans; no new substance, skills#235 remains sufficient
- 2026-07-06T10:51:10Z — unchanged: v3.9 still latest, same Mobile app entry, no new entries
- 2026-07-05T00:00:00Z — unchanged: v3.9 still latest, no new entries
- 2026-07-04T08:49:33Z — unchanged: v3.9 still latest (June 30 Team-MCP entry), no v3.10
- 2026-07-03T00:00:00Z — unchanged: v3.9 still latest, no new entries since June 30
- 2026-07-02T07:21:05Z — unchanged: v3.9 still latest; no new entries since June 30 scan
- 2026-07-01T00:00:00Z — changed: v3.9 gained Mobile app (June 29) + Team MCP/org marketplace scoping (June 30); Cursor-client-only, not iEvo-actionable; #235 remains sufficient
- 2026-06-29T14:15:20Z — unchanged: v3.9 still latest (June 22); no v3.10; Team marketplace multi-source (GitLab/BitBucket/Azure DevOps) not yet filed as finding (low priority — requires Cursor team plan + non-skills.sh source not currently in iEvo scope)
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
last_scan: 2026-07-07T10:00:00Z
status: changed
run_id: 28857232826
```

**Summary:** New front-page items: "OfficeCLI" (182 pts — an office-suite tool for AI agents to read/edit Microsoft Office files) and "Learning to Code Remains Valuable" (207 pts — discussion piece on coding skills in an AI-influenced landscape). Neither concerns agent-skill-format, hooks, or MCP; OfficeCLI is an adjacent tool-use project but not a concrete iEvo capability gap as-is. Not actionable for the skills repo today.

History:
- 2026-07-07T10:00:00Z — changed: "OfficeCLI" (182 pts, AI-agent Office file tool) + "Learning to Code Remains Valuable" (207 pts, discussion) — neither actionable; no agent-skill-format posts
- 2026-07-06T10:51:10Z — changed: "GPT-5.6 Sol Ultra in Codex" rumor (299 pts, tweet-sourced, unconfirmed) + code-cleanliness-vs-agents arxiv study (135 pts) — neither actionable; no agent-skill-format posts
- 2026-07-05T00:00:00Z — changed: session/cache leakage thread (295 pts, Claude Code infra, not iEvo-actionable) + Codex reasoning-clustering thread (263 pts, model quality, not actionable); no agent-skill-format posts
- 2026-07-04T08:49:33Z — unchanged: only tangential items ("Agentic coding notes from Galapagos Island" 74 pts, local-LLM guide 334 pts); no Claude Code/Codex/MCP/agent-skills posts on front page
- 2026-07-01T00:00:00Z — changed: Claude Sonnet 5 + steganographic-marking discussion threads trending; not iEvo-actionable (Claude Code's own attribution mechanism, not agent-skill format)
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
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
```

**Summary:** No commits since the June 29 21:15 `evals.md` split — 8 days without activity now.

History:
- 2026-07-07T10:00:00Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z; 8 days without activity
- 2026-07-06T10:51:10Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z; 7 days without activity
- 2026-07-05T00:00:00Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z; 6 days without activity
- 2026-07-04T08:49:33Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z; 5 days without activity
- 2026-07-03T00:00:00Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z (evals.md split); no new activity
- 2026-07-02T07:21:05Z — unchanged: no commits since June 29 21:15; last change still the evals.md split (evidence for open F-2026-06-29-002/skills#267)
- 2026-07-01T00:00:00Z — changed: June 29 21:15 commit split out references/evals.md (+143 lines); strengthens existing F-2026-06-29-002 / skills#267, no new finding filed
- 2026-06-29T14:15:20Z — unchanged: no commits since June 14; checklists.md activation-evals requirement triggered F-2026-06-29-002
- 2026-06-27T07:21:43Z — changed: new references/coding-agents.md (June 7, 436 lines) + workflow-orchestration.md expansion (June 14) + SVG diagram; coding-agents MVP boundary triggered F-2026-06-27-002
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
last_scan: 2026-07-07T10:00:00Z
status: unchanged
run_id: 28857232826
note: "skills#233/#236 stale-premise discrepancy (display-name/default-enabled/fallback absent from the frontmatter table) remains moot — both issues closed since July 4/5. No further tracking needed."
```

**Summary:** Re-fetched in full. Same 16-field frontmatter table (name, description, when_to_use, argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context, agent, hooks, paths, shell). No new fields since July 4/5.

History:
- 2026-07-07T10:00:00Z — unchanged: same 16-field table re-confirmed via fresh fetch; no new fields
- 2026-07-05T00:00:00Z — unchanged: same 16-field table re-confirmed; skills#233/#236 both closed by operator since last scan, discrepancy resolved (moot, no further tracking)
- 2026-07-04T08:49:33Z — unchanged: same 16-field frontmatter table re-confirmed (name, description, when_to_use, argument-hint, arguments, disable-model-invocation, user-invocable, allowed-tools, disallowed-tools, model, effort, context, agent, hooks, paths, shell); display-name/default-enabled/fallback STILL absent (second consecutive confirmation — the skills#233/#236 premise discrepancy stands); `name` field description now reads "Display name shown in skill listings", suggesting `name` itself absorbed any display-name role
- 2026-07-03T00:00:00Z — changed: v2.1.199 stacked-skill-invocation + skillOverrides Remote-Control note added; **display-name/default-enabled/fallback fields absent from this fetch's frontmatter table** — flagged for re-verification against skills#233/#236, not re-filed
- 2026-07-01T00:00:00Z — unchanged: full re-read confirms same 17 fields as June 30; no new fields; F-2026-06-30-001/002/003 remain the tracked open findings
- 2026-06-30T00:00:00Z — changed: 7 new/clarified fields (when_to_use, argument-hint, arguments, paths, shell, disable-model-invocation, ${CLAUDE_PROJECT_DIR}); triggered F-2026-06-30-001/002/003
- 2026-06-01T08:08:22Z — changed: disallowed-tools frontmatter added (v2.1.152); .claude/skills auto-load (v2.1.157); effort: stable
- 2026-05-31T00:00:00Z — unchanged: no new fields since last scan; `disallowed-tools` and `effort:` already documented; iEvo security-check and vuln-scan already use disallowed-tools
- 2026-05-30T07:15:49Z — changed: hooks frontmatter, disallowed-tools, context:fork, dynamic !`cmd` injection, $CLAUDE_SKILL_DIR vars — major expansion; triggered F-2026-05-30-001, F-2026-05-30-003
- 2026-05-29T07:38:29Z — unchanged: stable; disallowed-tools already documented in v2.1.152 release notes; no spec breaks
- 2026-05-27T07:38:00Z — changed: disallowed-tools frontmatter added (v2.1.152); /reload-skills documented; triggered F-2026-05-27-001
- 2026-05-25T07:48:17Z — first-scan: effort: frontmatter documented; values low/medium/high/xhigh/max; triggered F-2026-05-25-001

---

## https://code.claude.com/docs/en/routines.md

```yaml
last_scan: 2026-07-04T08:49:33Z
status: changed
run_id: 28700876614
```

**Summary:** Substantially expanded since the July 1 read. Routines are explicitly "research preview" now. CLI surface: creation is **conversational `/schedule`** (in-session slash command, optionally with a natural-language description); management via `/schedule list` / `/schedule update` / `/schedule run`. The docs describe **no `claude schedule create` shell subcommand** — but iEvo's `schedule/SKILL.md` Step 6 instructs exactly that (`claude schedule create --name ... --schedule ... --prompt-file ...`) and Step 1 probes availability with `claude schedule list`; likely broken primary path → **triggered F-2026-07-04-001**. Other new/clarified surface: one-off runs (`/schedule tomorrow at 9am, ...`, auto-disable after firing, exempt from daily routine cap); custom cron via `/schedule update` with a **1-hour minimum interval**; connectors (claude.ai MCP integrations) included by default per routine; cloud environments with Trusted-network default allowlist; GitHub trigger PR filters (author/title/body/branches/labels/draft/merged with regex-matches-whole-value semantics); API `/fire` endpoint gated behind `experimental-cc-routine-2026-04-01` beta header; `claude/`-prefixed branch push restriction by default; Team/Enterprise org-level Routines disable toggle. Plan gating unchanged (Pro/Max/Team/Enterprise + Claude Code on the web enabled; API-key auth still unsupported — now documented in a troubleshooting section listing telemetry env vars that also hide `/schedule`).

History:
- 2026-07-04T08:49:33Z — changed: major doc expansion — /schedule list/update/run subcommands, one-off runs, 1h cron minimum, connectors/environments, GitHub trigger filters, /fire beta header; no `claude schedule create` CLI documented → schedule/SKILL.md drift, triggered F-2026-07-04-001
- 2026-07-01T00:00:00Z — unchanged: full re-read, same trigger types and API shape as first-scan; F-2026-05-25-002/skills#84 remains sufficient
- 2026-06-01T08:08:22Z — unchanged: spec stable; no new triggers or API changes
- 2026-05-31T00:00:00Z — unchanged: Routines docs stable; F-2026-05-25-002 implemented (skills#84 closed COMPLETED)
- 2026-05-30T07:15:49Z — unchanged: Routines stable; skills#84 implemented; no new doc changes
- 2026-05-29T07:38:29Z — unchanged: Routines docs stable; no new triggers or breaking changes
- 2026-05-27T07:38:00Z — unchanged: no new content since last scan
- 2026-05-25T07:48:17Z — first-scan: Routines API documented; /schedule command; triggered F-2026-05-25-002

---

## https://code.claude.com/docs/en/channels.md

```yaml
last_scan: 2026-07-04T08:49:33Z
status: unchanged
run_id: 28700876614
```

**Summary:** Claude Code Channels — push events from Telegram/Discord/iMessage into Claude Code sessions. Still research preview (requires v2.1.80+, Bun, not on Bedrock/Vertex/Foundry). Plugin-based (`/plugin install telegram@claude-plugins-official`), then `claude --channels plugin:...`. Enterprise: `channelsEnabled` + `allowedChannelPlugins` managed settings. No GA timeline visible; not actionable for iEvo yet.

History:
- 2026-07-04T08:49:33Z — unchanged: still research preview (v2.1.80+, Bun, allowlist-gated plugins); docs expanded with fakechat demo channel, permission-relay capability note, and `allowedChannelPlugins` enterprise allowlist detail; no GA, not iEvo-actionable
- 2026-07-01T00:00:00Z — unchanged: full re-read, still research preview; no GA announcement; not actionable
- 2026-06-01T08:08:22Z — unchanged: still research preview; Bun required; no GA announcement
- 2026-05-31T00:00:00Z — unchanged: still in research preview; Bun required; no GA announcement; not actionable
- 2026-05-30T07:15:49Z — unchanged: still research preview; Bun required; no new GA timeline visible
- 2026-05-29T07:38:29Z — unchanged: still research preview; Bun required; not GA; defer /ievo:channel-setup proposal
- 2026-05-27T07:38:00Z — changed: still research preview but significantly expanded with platform-specific setup guides, enterprise allowlist, dev testing flag; not GA yet — defer /ievo:channel-setup until GA
- 2026-05-25T07:48:17Z — first-scan: Channels in research preview; Bun required; push events from Telegram/Discord/iMessage

---

## https://code.claude.com/docs/en/sub-agents

```yaml
last_scan: 2026-07-06T10:51:10Z
status: changed
run_id: 28762000000
note: "Resolves the F-2026-06-01-era deferred question: does `skills:` preload work for plugin subagents? Answer is YES — the field's table row and the dedicated `skills:` explainer section both omit the 'Ignored for plugin subagents' caveat that `permissionMode`/`mcpServers`/`hooks` explicitly carry. Triggered F-2026-07-06-001."
```

**Summary:** Same field table structure, but this run read the `skills:` field row and its dedicated explainer section closely (previously only noted in passing). Unlike `permissionMode`/`mcpServers`/`hooks` — each explicitly marked "Ignored for [plugin subagents]" — the `skills:` field carries no such caveat anywhere on the page, including in the "Preload skills into subagents" section, which describes the mechanism generically (full skill content injected at subagent startup) with no subagent-scope exclusion. `vuln-scanner.md` (plugin subagent) currently invokes its skill dynamically via `Skill("ievo:vuln-scan")` rather than preloading it — a candidate for `skills:` frontmatter now that the plugin-subagent-support question has a documented answer. Triggered F-2026-07-06-001.

History:
- 2026-07-06T10:51:10Z — changed: closely read the `skills:` field row + explainer section — no "ignored for plugin subagents" caveat present (unlike permissionMode/mcpServers/hooks); resolves the July 4 deferred open question; triggered F-2026-07-06-001
- 2026-07-05T00:00:00Z — unchanged: same field table re-confirmed; permissionMode/mcpServers/hooks-ignored-for-plugin-subagents note re-verified verbatim
- 2026-07-04T08:49:33Z — changed: permissionMode `manual` alias (v2.1.200); background-by-default (v2.1.198); noted permissionMode/mcpServers/hooks ignored for PLUGIN subagents — negative filter for future iEvo-agent proposals; `skills:` preload deferred
- 2026-07-01T00:00:00Z — unchanged: full re-read, same field list as May 31 scan; Agent(type) allowlist + initialPrompt details noted; no new iEvo-actionable gap
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
note: duplicate of https://code.claude.com/docs/en/sub-agents (no .md suffix) tracked above — merge/dedupe candidate for a future run, both scanned together 2026-07-01
```

**Summary:** Sub-agents documentation for Claude Code. Model resolution order: (1) `CLAUDE_CODE_SUBAGENT_MODEL` env var if set, (2) per-invocation parameter, (3) agent frontmatter `model:`, (4) main-conversation model. Dispatch via Task tool. `agent:` field in `settings.json` (v2.1.157) adds a fourth override path: if `agent: <name>` is set, dispatched sessions use the specified agent profile, potentially overriding skill-dispatched sub-agents. Key security implication: `security-auditor.md` model frontmatter can be silently bypassed by env var OR `agent:` in settings.json.

History:
- 2026-06-01T08:08:22Z — first-scan: sub-agent model resolution order documented; agent: settings.json field identified as new bypass vector → triggered F-2026-06-01-003
- 2026-05-30T07:15:49Z — first-scan: sub-agent model resolution order documented; context:fork frontmatter; settings.json agent field; CLAUDE_CODE_SUBAGENT_MODEL precedence confirmed
- 2026-05-27T07:38:00Z — first-scan: confirmed CLAUDE_CODE_SUBAGENT_MODEL resolution order; disallowedTools and isolation: worktree documented; model resolution security note in AGENTS.md is accurate
