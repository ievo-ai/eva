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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** Re-fetched — no items newer than Aug 14 ("How Claude's text watermark works" still newest). No Claude Code API or skill-format change.

History:
- 2026-08-24T07:14:49Z — unchanged: re-fetched, no items newer than Aug 14; no iEvo action
- 2026-08-23T00:00:00Z — unchanged: re-fetched, no items newer than Aug 14; no iEvo action
- 2026-08-21T06:58:19Z — unchanged: re-fetched, no items newer than Aug 14; no iEvo action
- 2026-08-18T00:00:00Z — unchanged: re-fetched, no items newer than Aug 14; no iEvo action
- 2026-08-15T06:47:01Z — changed: 3 new items since Jul 24 — text watermark explainer (Aug 14), Fable 5 biology safeguards (Aug 7), Cuéllar Chief Global Affairs Officer hire (Aug 4); all non-technical, no iEvo action
- 2026-08-12T00:00:00Z — unchanged: not deep-re-fetched (low cadence, no signal expected — the week's real activity is on the claude-code/codex release trackers below); no items newer than Jul 24 known
- 2026-08-11T00:00:00Z — unchanged: not deep-re-fetched (low cadence, no signal expected — the week's real activity is on the claude-code/codex release trackers below); no items newer than Jul 24 known
- 2026-08-09T07:07:40Z — unchanged: not deep-re-fetched (low cadence, no signal expected — the week's real activity is on the claude-code/codex release trackers below); no items newer than Jul 24 known
- 2026-08-05T09:05:00Z — unchanged: re-fetched, no items newer than Jul 24 (Opus 5); no iEvo action
- 2026-08-02T08:50:05Z — unchanged: re-fetched, no items newer than Jul 24 (Opus 5); no iEvo action
- 2026-08-01T08:32:39Z — unchanged: re-fetched, no items newer than Jul 27; no iEvo action
- 2026-07-31T00:00:00Z — unchanged: re-fetched, same 3 newest items (Opus 5 Jul 24, Economic Index Connector Jul 22, Making of Claude Code Jul 6); no new item since Jul 27 scan
- 2026-07-30T08:45:00Z — unchanged: re-fetched, no items newer than Jul 27; no iEvo action
- 2026-07-29T00:00:00Z — changed: Jul 27 items (open-weights-models position statement, Cognizant enterprise partnership) — both non-technical, no iEvo action
- 2026-07-27T10:30:00Z — changed: Claude Opus 5 (Jul 24) — new default Opus model, 1M context; no CC-specific or skill-format changes; no iEvo action
- 2026-07-23T09:00:00Z — unchanged: re-fetched, no items newer than Jul 20 "AI for Science" grants; no iEvo action
- 2026-07-22T00:00:00Z — changed: Jul 20 "AI for Science" rare-disease grants item; non-technical, no iEvo action; no items between Jul 14 and Jul 20
- 2026-07-16T00:00:00Z — unchanged: re-fetched, no items newer than Jul 14; no iEvo action
- 2026-07-15T00:00:00Z — changed: 2 new Jul 14 items (Claude for Teachers, Canada AI research commitment) — both non-technical, no iEvo action
- 2026-07-14T00:00:00Z — unchanged: re-fetched, no items newer than Jul 9; same 4 items as last scan
- 2026-07-13T09:40:07Z — unchanged: re-fetched, no items newer than Jul 9; same 4 items as last scan
- 2026-07-12T08:26:18Z — unchanged: re-fetched, no items newer than Jul 9; same 4 items as last scan
- 2026-07-10T09:52:47Z — changed: 4 new Jul 9 items (physical-AI case study, public-Q&A commitment, Bernanke Trust appointment, usage-reflection feature) — all non-technical, no iEvo action
- 2026-07-09T10:09:26Z — unchanged: re-fetched, no items newer than Jul 6 "The Making of Claude Code"; no iEvo action
- 2026-07-08T10:00:00Z — changed: Jul 6 "The Making of Claude Code" feature article added; non-technical retrospective, no CC-specific capability or format change, no iEvo action
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** `gh api` confirms v2.1.241 (Aug 23) still latest — no new release in the ~1-day gap. Prior scan already covered v2.1.239-241's content in full (marketplace `pluginRoot` resolution fix, UTF-8 BOM skill-load fix); nothing new to add.

History:
- 2026-08-24T07:14:49Z — unchanged: `gh api` confirms v2.1.241 (Aug 23) still latest; no new release
- 2026-08-23T00:00:00Z — changed: v2.1.239 (Aug 21, large bugfix/QoL release — marketplace `pluginRoot` resolution fix, UTF-8 BOM skill-load fix, cost-estimate/proxy/session-title/hooks bugfixes) + v2.1.240/v2.1.241 (Aug 22-23, bugfix-only, no changelog detail); no new frontmatter fields, no iEvo action
- 2026-08-21T06:58:19Z — changed: v2.1.235 (Aug 18, spellcheck setting, misc TUI/perf fixes) + v2.1.236 (Aug 19, `ANTHROPIC_DEFAULT_MODEL`, cross-session `notify_when_idle`, macOS sandbox wildcard-read-deny precedence fix) + v2.1.237 (Aug 20, prompt-caching-under-gateway fix, "Concise" output style) + v2.1.238 (Aug 20, plugin-marketplace `headersHelper` install/update confirmation dialog, MCP `headersHelper`/inline-MCP trust-dialog requirement, `claude self-hosted-runner` proxy-auth flags, bundled `claude-api` skill updated for Managed Agents Aug 19); no new SKILL.md/agent/sub-agent frontmatter fields; marketplace headersHelper confirmation is hardening of an existing feature, not a new schema surface iEvo needs to adopt
- 2026-08-18T00:00:00Z — changed: v2.1.234 (Aug 17) — CLAUDE_CODE_PROJECT_DIR_NAME env var, GitLab MR badge, NT-namespace path-rejection hardening, MCP diagnostics secret-redaction fix, strictKnownMarketplaces SCP-host-mismatch fix; no new frontmatter fields, no iEvo action
- 2026-08-15T06:47:01Z — changed: v2.1.229-233 (Aug 12-14) — `claude plugin validate` now checks bare `.claude/skills` (SKILL.md frontmatter parse-failure reporting, v2.1.233); GitLab plugin-marketplace support + marketplace alias settings (v2.1.232); new `command`-source marketplace type for local/IDE-driven plugin dirs (v2.1.229); Todo/task tools off by default on newer models unless `CLAUDE_CODE_ENABLE_TODO_TOOLS=1` (v2.1.233) — worth a follow-up check against iEvo's own agents; no new frontmatter fields
- 2026-08-12T00:00:00Z — changed: v2.1.228 (Aug 11) — bugfix/UI-polish only (TUI redraw stall, Windows git-launch, `/tui` model-revert, cross-session inbox, Remote Control `/resume` leak, self-hosted-runner fixes, marketplace-entry merge fix, Write-tool read-before-overwrite rule extended to newer models); one item ("hardened skills synced from claude.ai") considered — different surface from plugin-installed skills, not iEvo-actionable; no new frontmatter fields
- 2026-08-11T00:00:00Z — changed: v2.1.227 (Aug 10) — bugfix/polish only (feature-flag/subscription-tier fix, claude-code-action Bash-under-allowed_non_write_users fix, /tui rewind fix, slash-menu UI polish, perf); no new frontmatter fields, no iEvo action
- 2026-08-09T07:07:40Z — changed: v2.1.223 (Aug 6) through v2.1.226 (Aug 8) — marketplace owner-wildcards, Bash/permission-dialog security fixes, `/review`→`/code-review` alias (v2.1.223); **`archive` plugin source (zip-over-HTTPS install, v2.1.224) — matches already-open skills#585 exactly, filed same-day, no new action needed**; cross-session SendMessage, sandbox credential-masking extensions (v2.1.224); gateway spend-limit, workspace-trust prompt (v2.1.225); bugfix-only (v2.1.226); no new frontmatter fields
- 2026-08-05T09:05:00Z — changed: v2.1.221 (Aug 3) + v2.1.222 (Aug 4) — sandbox.credentials file-level mask mode (already tracked via open skills#559), zsh/PowerShell permission-check fixes, worktree-isolation hardening, org-model-alias step-down fix; no new frontmatter fields
- 2026-08-02T08:50:05Z — unchanged: `gh api` confirms v2.1.220 (Jul 25) still latest; no new release (8-day gap since it shipped)
- 2026-08-01T08:32:39Z — unchanged: `gh api` confirms v2.1.220 (Jul 25) still latest; no new release in the 1-day gap since the last audit run (2026-07-31)
- 2026-07-31T00:00:00Z — unchanged: `gh api` confirms v2.1.220 (Jul 25) still latest; no new release since last scan (6-day gap)
- 2026-07-30T08:45:00Z — unchanged: `gh api` confirms v2.1.220 (Jul 25) still latest; no new release since last scan
- 2026-07-29T00:00:00Z — unchanged: `gh api` confirms v2.1.220 (Jul 25) still latest; no new release since last scan
- 2026-07-27T10:30:00Z — changed: confirmed still v2.1.220 (Jul 25) latest via gh api; v2.1.219 nesting-depth-3 default already tracked via skills' own AGENTS.md; skills.md table has a `background` field not previously itemized (17 fields total now) — behavior already known, just updating the field inventory; sub-agents.md still 16 fields; no new iEvo action
- 2026-07-23T09:00:00Z — changed: v2.1.218 (Jul 22) — boolean frontmatter accepts yes/no/on/off/1/0, agent names reject `:`, context:fork backgrounds by default, agent-hook workspace-trust requirement, worktree-isolation mutation fix; v2.1.217 (Jul 21) — subagent concurrency cap 20 (CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS), nested-subagent-spawn now off by default (CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH to re-enable), --max-budget-usd fix for background subagents; no new SKILL.md/agent/sub-agent frontmatter fields (full field-by-field re-confirm, 16-field skills.md + 16-field sub-agents tables)
- 2026-07-22T00:00:00Z — changed: v2.1.212-217 (Jul 17-21) — subagent spawn/concurrency caps, glob-permission-bypass fix, worktree/rewind symlink hardening, plugin-skill name-prefix fix, budget enforcement fix; Claude's own /verify+/code-review auto-invocation removed (not iEvo's skills); no new frontmatter fields (full re-confirm)
- 2026-07-16T00:00:00Z — changed: v2.1.211 (Jul 15, 23:02Z) — permission-preview homograph hardening, PreToolUse `ask`-floor fix, subagent model-override persistence, nested rules-loading scope fix, prompt-caching billing fix; no new frontmatter fields, no iEvo action
- 2026-07-15T00:00:00Z — changed: v2.1.210 (Jul 14, 23:45Z) — 30+ item release; permission-rule startup warning, worktree-isolation git-mutation fix, prompt-injection hardening on Agent tool, positional-placeholder preservation fix; no new frontmatter fields, no iEvo action
- 2026-07-14T00:00:00Z — changed: v2.1.208 (`${user_config.*}` shell-injection rejection for plugin hooks/monitors/headersHelper, pluginConfigs no longer read from project settings, transcript-size/checkpoint/memory-leak fixes) + v2.1.209 (`/model` dialog fix); no new frontmatter fields; skills.md re-confirmed 16 fields
- 2026-07-13T09:40:07Z — unchanged: re-fetched, still v2.1.207 as latest; no new release since July 11
- 2026-07-12T08:26:18Z — changed: v2.1.207 (July 11) — Auto mode on Bedrock/Vertex/Foundry without opt-in, `${user_config.*}` shell-injection fix for plugin hooks/monitors/headersHelper, various bugfixes; no new frontmatter, no direct iEvo action (iEvo doesn't use user_config interpolation)
- 2026-07-10T09:52:47Z — changed: v2.1.206 (July 10) — `/cd` suggestions, `/doctor` CLAUDE.md-trim proposal, `/commit-push-pr` pushDefault support, worktree-outside-project confirm, background-agent upgrade-timing fix, MCP timeout/OAuth bugfixes; no new frontmatter, no iEvo action; skills.md + sub-agents field tables independently re-confirmed unchanged (16 fields each)
- 2026-07-09T10:09:26Z — changed: v2.1.205 (July 8) — `/doctor` full checkup + `/checkup` alias, MCP Claude Browser reservation, plugin LSP fix, agent-view UI polish; no new frontmatter, no iEvo action
- 2026-07-08T10:00:00Z — changed: v2.1.203 (July 7) — extensive background-agent/daemon fixes, VSCode remote-control toggle, binary size/memory reduction; v2.1.204 (July 7) — SessionStart hook streaming fix in headless mode; no new frontmatter, no iEvo action
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** `gh api` confirms v1.0.201 (Aug 23) still latest (floating `v1` tag excluded per established practice) — no new release in the ~1-day gap. eva#65 stays closed.

History:
- 2026-08-24T07:14:49Z — unchanged: `gh api` confirms v1.0.201 (Aug 23) still latest; no new release; eva#65 stays closed
- 2026-08-23T00:00:00Z — changed: v1.0.199 (Aug 21, GITHUB_GRAPHQL_URL fix, base-branch-revert-leak fix, mcp__github aggregate-selector fix, claude_args --allowedTools signed-prompt fix) + v1.0.200/v1.0.201 (Aug 22-23, empty-body patches); no input schema changes; eva#65 stays closed
- 2026-08-21T06:58:19Z — changed: v1.0.195 (Aug 18, empty-body patch) + v1.0.196 (Aug 19, unify secret redaction in public comment outputs #1693, strip unused ALL_INPUTS env var #1692, bot-actor GraphQL __typename matching fix #1616) + v1.0.197 (Aug 20, neutralize checkout credential under actions/checkout v6+ include layout #1526 — security-relevant, adjacent to GH-Actions-hardening tracking) + v1.0.198 (Aug 20, empty-body patch); no input schema changes; eva#65 stays closed
- 2026-08-18T00:00:00Z — changed: v1.0.194 (Aug 17) — delete_files path-validation hardening, shell-quote CVE-2026-9277 fix, image-attachment download bounding, fork-PR CI skip; no input schema changes; eva#65 stays closed
- 2026-08-15T06:47:01Z — changed: v1.0.192 (Aug 13) — MCP GH Actions pagination fix, structured tool-result text-block truncation fix, binary-file detection by content not extension; v1.0.193 (Aug 14) empty-body patch; no input schema changes; eva#65 stays closed
- 2026-08-12T00:00:00Z — changed: v1.0.191 (Aug 11) — empty-body patch, no documented input schema changes; eva#65 stays closed
- 2026-08-11T00:00:00Z — changed: v1.0.190 (Aug 10) — empty-body patch, no documented input schema changes; eva#65 stays closed
- 2026-08-09T07:07:40Z — changed: v1.0.186 (formatter-hook fix) through v1.0.189 (empty-body patch) — notably v1.0.187's own redaction/scoping hardening (credential/bearer-token redaction from published run output) and v1.0.188's max-turn-limit enforcement + GraphQL large-PR null-files fix; no input schema changes; eva#65 stays closed
- 2026-08-05T09:05:00Z — changed: v1.0.184 + v1.0.185 (both Aug 4) — trigger-timestamp derivation, MCP bun-config pin, image-asset matching, workflow_run collaborator-permission check; no input schema changes; eva#65 stays closed
- 2026-08-02T08:50:05Z — unchanged: `gh api` confirms v1.0.183 (Jul 25) still latest, `v1` floating tag excluded; no new release; eva#65 stays closed
- 2026-08-01T08:32:39Z — unchanged: `gh api` confirms v1.0.183 (Jul 25) still latest; no new release; eva#65 stays closed
- 2026-07-31T00:00:00Z — unchanged: `gh api` confirms v1.0.183 (Jul 25) still latest, `v1` floating tag excluded per established practice; no new release; eva#65 stays closed
- 2026-07-30T08:45:00Z — unchanged: `gh api` confirms v1.0.183 (Jul 25) still latest; no new release; eva#65 stays closed
- 2026-07-29T00:00:00Z — unchanged: `gh api` confirms v1.0.183 (Jul 25) still latest; no new release; eva#65 stays closed
- 2026-07-27T10:30:00Z — changed: v1.0.182 (Jul 24) + v1.0.183 (Jul 25), both empty-body compare-link-only patches, gh api-verified; no input schema changes; WebFetch this run hallucinated a false Aug-2026 v1 GA date — corrected via gh api; eva#65 stays closed
- 2026-07-23T09:00:00Z — changed: v1.0.181 (Jul 22) — credential-sharing fix for spawned processes; no input schema changes; eva#65 stays closed
- 2026-07-22T00:00:00Z — changed: v1.0.176 through v1.0.180 (Jul 17-21), routine patches tracking claude-code's release cadence; no input schema changes visible; eva#65 stays closed
- 2026-07-16T00:00:00Z — changed: v1.0.175 (empty-body routine patch); no input schema changes; eva#65 stays closed
- 2026-07-15T00:00:00Z — changed: v1.0.174 (ghu_ token redaction fix in sanitizer); no input schema changes; eva#65 stays closed
- 2026-07-14T00:00:00Z — changed: v1.0.172 (SDK is_error/success-subtype fix) + v1.0.173 (empty-body patch); no input schema changes; eva#65 stays closed
- 2026-07-13T09:40:07Z — unchanged: re-fetched, still v1.0.171 as latest; no new release
- 2026-07-12T08:26:18Z — changed: v1.0.171 (July 11) — empty-body patch, no documented input schema changes; eva#65 stays closed
- 2026-07-10T09:52:47Z — changed: v1.0.170 (July 9) — empty-body patch, no documented input schema changes; eva#65 stays closed
- 2026-07-09T10:09:26Z — changed: v1.0.169 (July 8) — minor patch, no documented input schema changes; eva#65 stays closed
- 2026-07-08T10:00:00Z — changed: v1.0.167 (July 7) + v1.0.168 (July 8), both empty-body routine patches; no input schema changes visible; eva#65 stays closed
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Not re-fetched (low cadence, redirect-only; v2.1.235-238 release notes reviewed directly, no overview-relevant product-surface change mentioned).

History:
- 2026-08-21T06:58:19Z — unchanged: not re-fetched (low cadence, redirect-only); v2.1.235-238 release notes reviewed directly, no new product surface
- 2026-08-18T00:00:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-15T06:47:01Z — unchanged: followed redirect, full read of code.claude.com/docs/en/overview — same sections as previously known, no new product surface
- 2026-08-12T00:00:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-11T00:00:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-09T07:07:40Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-05T09:05:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (low cadence, redirect-only)
- 2026-07-01T00:00:00Z — unchanged: still 301-redirects to code.claude.com/docs/en/overview
- 2026-05-27T07:38:00Z — unchanged: redirects to code.claude.com; tracking sub-page URLs directly now
- 2026-05-25T07:48:17Z — changed: Routines + Channels now documented; effort: frontmatter documented in skills.md
- 2026-05-22T10:50:58Z — changed: docs migrated to code.claude.com; Agent SDK, Skills & Hooks, Routines, Remote Control added to overview

---

## https://openai.com/index/news/

```yaml
last_scan: 2026-08-21T06:58:19Z
status: error
run_id: 32456237667
```

**Summary:** Not re-attempted this run (persistent 403 across many consecutive prior attempts, low cadence). Use `github.com/openai/codex/releases` as the Codex signal source instead.

History:
- 2026-08-24T07:14:49Z — error: not re-attempted (persistent 403, low cadence)
- 2026-08-21T06:58:19Z — error: re-attempted, still HTTP 403 Forbidden
- 2026-08-18T00:00:00Z — error: re-attempted, still HTTP 403 Forbidden
- 2026-08-15T06:47:01Z — error: re-attempted, still HTTP 403 Forbidden
- 2026-08-12T00:00:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-08-11T00:00:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-08-09T07:07:40Z — error: not re-fetched (persistent 403, low cadence)
- 2026-08-05T09:05:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-08-02T08:50:05Z — error: not re-fetched (persistent 403, low cadence)
- 2026-08-01T08:32:39Z — error: not re-fetched (persistent 403, low cadence)
- 2026-07-31T00:00:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-07-30T08:45:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-07-29T00:00:00Z — error: not re-fetched (persistent 403, low cadence)
- 2026-07-01T00:00:00Z — error: still HTTP 403 Forbidden
- 2026-05-22T10:50:58Z — error: HTTP 403 Forbidden; blocked to automated fetchers

---

## https://github.com/openai/codex/releases

```yaml
last_scan: 2026-08-24T07:14:49Z
status: changed
run_id: 32699971736
```

**Summary:** rust-v0.149.1 shipped today (Aug 24) — confirmed empty-body (`## Changelog` + compare link only, `gh api repos/openai/codex/releases/tags/rust-v0.149.1 --jq '.body'`), no skill-format signal. No other stable release since v0.149.0.

History:
- 2026-08-24T07:14:49Z — changed: rust-v0.149.1 (Aug 24) — confirmed empty-body patch release, no skill-format signal
- 2026-08-23T00:00:00Z — unchanged: `gh api` confirms rust-v0.149.0 (Aug 20) still latest stable; no new stable release in the 3-day gap; pre-release line at rust-v0.150.0-alpha.7.2 (Aug 22), not fetched for content (established low-signal precedent for alpha tags)
- 2026-08-21T06:58:19Z — changed: rust-v0.148.0 (Aug 18) — skill-creator guide refocused + validation rejects unfinished TODO placeholders (possible capability-gap signal, see report), async/MCP-capable hooks, Bedrock provider; rust-v0.149.0 (Aug 20) — `codex agents` dashboard, `codex queue`, SDK `max`/`ultra` reasoning effort; no confirmed SKILL.md/frontmatter change
- 2026-08-18T00:00:00Z — unchanged: `gh api` confirms rust-v0.147.0 still latest stable (Aug 7); no new stable release in the 11-day gap
- 2026-08-15T06:47:01Z — unchanged: `gh api` confirms rust-v0.147.0 still latest stable (Aug 7); no new stable release in the 8-day gap; pre-release line now at 0.148.0-alpha.19 (Aug 15), still empty-body, no skill-format signal
- 2026-08-12T00:00:00Z — unchanged: `gh api` confirms rust-v0.147.0 still latest stable (Aug 7); no new stable release in the 5-day gap; pre-release line now at 0.148.0-alpha.9 (Aug 12), still empty-body, no skill-format signal
- 2026-08-11T00:00:00Z — unchanged: `gh api` confirms rust-v0.147.0 still latest stable (Aug 7); no new stable release in the 4-day gap; pre-release line not checked (no signal expected from alpha/empty-body tags)
- 2026-08-09T07:07:40Z — changed: rust-v0.147.0 STABLE (Aug 7) — portable Agent Plugins install + multi-catalog search (agent-plugins.org spec, relevant to already-shipped skills#501 but no confirmed precedence-order change per a PR-title search — see Summary), `--approve-for-me`, Cursor-skill import/sync, MCP 2026-07-28 protocol, secret/bearer-token redaction hardening, plugin-isolation hardening; rust-v0.146.1 patch (Aug 5); no confirmed skill-format/frontmatter signal; not filed as a finding (insufficient evidence of an actual gap, see Summary)
- 2026-08-05T09:05:00Z — unchanged: `gh api` confirms rust-v0.146.0 still latest stable; pre-release line active through 0.147.0-alpha.6.x/alpha.7 (Aug 4), still empty-body, no skill-format signal
- 2026-08-02T08:50:05Z — unchanged: `gh api` confirms rust-v0.146.0 still latest stable; 0.147.0-alpha.4 (Jul 31) still newest pre-release, empty-body, no skill-format signal
- 2026-08-01T08:32:39Z — unchanged: `gh api` confirms rust-v0.146.0 still latest stable; 0.147.0-alpha.1 through alpha.4 (Jul 31) empty-body pre-releases, no skill-format signal
- 2026-07-31T00:00:00Z — unchanged: rust-v0.146.0 (Jul 29) still latest stable; 0.147.0-alpha.1/alpha.2 (Jul 29-30) empty-body pre-releases; no new skill-format signal
- 2026-07-30T08:45:00Z — unchanged: still rust-v0.146.0 STABLE (Jul 29) latest; 0.147.0-alpha.1/alpha.2 (Jul 29-30) empty-body pre-releases, no skill-format signal
- 2026-07-29T00:00:00Z — changed: **rust-v0.146.0 STABLE (Jul 29)** — Agent Plugins 1.0.0 root plugin.json recognition (agent-plugins.org spec, TSC = Amazon/Cursor/Microsoft/OpenAI/Vercel), Claude Code plugin marketplace inference, Bedrock plugin marketplace, executor-skill resource reads, skill-catalog-truncation warnings — triggered F-2026-07-29-001
- 2026-07-27T10:30:00Z — unchanged: still rust-v0.145.0 STABLE (Jul 21) as latest; 0.146.0-alpha.5 through alpha.12 (Jul 24-27), all empty-body; no skill-format signal
- 2026-07-23T09:00:00Z — unchanged: still rust-v0.145.0 STABLE (Jul 21) as latest; pre-release line at 0.146.0-alpha.4 (Jul 23), no notes published; no skill-format signal
- 2026-07-22T00:00:00Z — changed: rust-v0.145.0 STABLE (Jul 21) — permission-hook/MCP-OAuth-serialization/multi-agent-v2 model-override hardening, Windows sandbox fixes; no skill-format signal; 0.146.0-alpha.1-2 (Jul 22) already started; skills#170 still unconfirmed
- 2026-07-16T00:00:00Z — changed: rust-v0.144.5 stable (July 16) — dangerous-command-detection improvement (#33455, more forced-rm forms, clearer rejection reasons); not skill-format-relevant; 0.145.0-alpha.14-16 (July 15-16) still empty-body pre-releases; skills#170 still unconfirmed
- 2026-07-15T00:00:00Z — unchanged: still rust-v0.144.4 stable; 0.145.0-alpha.8 through alpha.13 (July 14-15) all empty-body pre-releases; no skill-format signal; skills#170 still unconfirmed
- 2026-07-14T00:00:00Z — changed: rust-v0.144.4 stable (no user-facing changes, July 14); rust-v0.144.2 (July 13) reverted an auto-review prompting regression; 0.145.0-alpha.7-10 (July 13-14) still empty-body pre-releases; no skill-format signal; skills#170 still unconfirmed
- 2026-07-13T09:40:07Z — changed: rust-v0.144.2 + rust-v0.144.3 stable (July 13); 0.145.0-alpha.4 (July 11) still latest pre-release; no new skill-format signal beyond the already-noted `writes` app-approval mode; skills#170 still unconfirmed
- 2026-07-12T08:26:18Z — unchanged: still v0.144.1 stable; 0.145.0-alpha.1-4 (July 9-11) all empty-body pre-releases; skills#170 flag-rename still unconfirmed
- 2026-07-10T09:52:47Z — changed: rust-v0.144.0 STABLE + v0.144.1 (July 9) — `writes` app-approval mode, interactive MCP auth, runtime app-server auth, terminal-control-sequence TUI fix, plugin skill-loading perf; no skill-format changes; skills#170 flag-rename still unconfirmed (not mentioned in this changelog); new 0.145.0-alpha.1/2 line started, no changelogs yet
- 2026-07-09T10:09:26Z — unchanged: still v0.143.0 stable; new 0.144.0-alpha.1/2/4 pre-release line started (July 8-9), no changelogs yet; skills#170 flag-rename re-verification still pending a live Codex CLI
- 2026-07-08T10:00:00Z — changed: rust-v0.143.0 STABLE (July 8) — remote plugins by default, Bedrock GPT-5.6 models, MCP tool-search-by-default, system-proxy routing, sandbox-permission-profile flag rename (#30095, worth re-checking against open skills#170); ends the 6-week alpha watch
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Re-fetched — only "Introducing Gemini Robotics ER 2" visible (robotics video-understanding/tool-orchestration model); not agent-skill-format relevant.

History:
- 2026-08-21T06:58:19Z — unchanged: re-fetched, only "Introducing Gemini Robotics ER 2" visible; not agent-skill-format relevant
- 2026-08-18T00:00:00Z — unchanged: not re-fetched (low cadence)
- 2026-08-15T06:47:01Z — unchanged: re-fetched, only "Introducing Gemini Robotics ER 2" visible; not agent-skill-format relevant
- 2026-08-12T00:00:00Z — unchanged: not re-fetched (low cadence)
- 2026-08-11T00:00:00Z — unchanged: not re-fetched (low cadence)
- 2026-08-09T07:07:40Z — unchanged: not re-fetched (low cadence)
- 2026-08-05T09:05:00Z — unchanged: not re-fetched (low cadence)
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (low cadence)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (low cadence)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (low cadence)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (low cadence)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (low cadence)
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** `gh api` PR check only (no full spec re-fetch — no new merges to trigger one) — still no new merges since #492 (Aug 9, now 15-day gap); same open PR set (#508/#506/#500/#486/#380/#386/#345/#254) all still open+unmerged.

History:
- 2026-08-24T07:14:49Z — unchanged: `gh api` PR check — no new merges since #492 (15-day gap); same open PR set unchanged, not deep-re-fetched (no signal to trigger one)
- 2026-08-23T00:00:00Z — unchanged: full spec re-fetched, same 6 fields and constraints confirmed field-by-field; no new merges since #492 (14-day gap); no new open PRs since #508
- 2026-08-21T06:58:19Z — unchanged: full spec re-read, same 6 fields and constraints confirmed field-by-field; no new merges since #492; new open PR #508 (cosmetic client showcase, unmerged)
- 2026-08-18T00:00:00Z — unchanged: `gh pr list --state merged` — no new merges since #492; new open PR #506 (cosmetic, unmerged); #500/#486/#380/#386/#345/#254 still open+unmerged
- 2026-08-15T06:47:01Z — unchanged: full spec re-read, same 6 fields and constraints confirmed field-by-field; `skills-ref validate` CLI validator section noted (pre-existing, not new); new open PR #500 (reference Python SDK + schema validator) on sibling repo — see that entry
- 2026-08-12T00:00:00Z — unchanged: full spec re-read this run, same 6 fields and constraints confirmed field-by-field; no new merges to agentskills/agentskills since #492 (see sibling entry)
- 2026-08-11T00:00:00Z — unchanged: `gh pr list --state merged --limit 5` — 2 new merges since #479 (#491/#492, both cosmetic client-showcase, see sibling entry); no spec/schema field impact; not deep-re-fetched (low cadence)
- 2026-08-09T07:07:40Z — unchanged: `gh pr list --state merged --limit 10` — no new merges since #479 (Aug 4); not deep-re-fetched (low cadence)
- 2026-08-05T09:05:00Z — unchanged: `gh api` PR check — 5 new merges since #447 (#475-479, all client-branding/docs-clarification, see agentskills/agentskills entry below), no spec/schema field impact; not deep-re-fetched (low cadence)
- 2026-08-02T08:50:05Z — unchanged: no new merges to agentskills/agentskills since last scan (`gh api` PR check); not deep-re-fetched (low cadence)
- 2026-08-01T08:32:39Z — unchanged: no new merges to agentskills/agentskills since last scan (`gh api` PR check); not deep-re-fetched (low cadence)
- 2026-07-31T00:00:00Z — unchanged: `gh api` PR check — no new merges since #447; not deep-re-fetched (low cadence)
- 2026-07-30T08:45:00Z — unchanged: `gh api` PR-state check — #380/#386/#345/#254 confirmed still open; no new merges since #447
- 2026-07-29T00:00:00Z — unchanged: no new merges to agentskills/agentskills since last scan; not deep-re-fetched (2-day gap, low cadence); noted a new sibling spec (agent-plugins.org) discovered via today's Codex release, tracked separately
- 2026-07-27T10:30:00Z — unchanged: full spec re-read, same 6 fields; still Experimental
- 2026-07-23T09:00:00Z — unchanged: full spec re-read, same 6 fields; #254/#380/#386/#345 all still open+unmerged
- 2026-07-22T00:00:00Z — unchanged: full spec re-read, same 6 fields; new open PR #254 (`.well-known` distribution spec, companion to #380) noted but unmerged — watch alongside #380/#386/#345
- 2026-07-16T00:00:00Z — unchanged: full spec re-read, same 6 fields; `gh api` PR check confirms no new merges since #457, #380/#386/#345 still open
- 2026-07-15T00:00:00Z — unchanged (not re-fetched): `gh api` PR check — no new merges since #457; #380 (updated Jun 10)/#386 (May 19)/#345 (Apr 29) all still open, no new activity
- 2026-07-14T00:00:00Z — unchanged (not re-fetched): PR-level `gh api` check found one new merge since #447 (#457, "Add Hermes Agent to client showcase") — cosmetic/listing only; #380/#386/#345 still open; skip deep re-fetch
- 2026-07-13T09:40:07Z — unchanged (not re-fetched): PR-level `gh api` check found one new merge since #446 (#447, "Add Pulumi Neo to client showcase", July 10) — cosmetic/listing only, no spec impact; skip deep re-fetch
- 2026-07-12T08:26:18Z — unchanged (not re-fetched): PR-level `gh api` check (see agentskills/agentskills entry) found no new merges since #446; skip deep re-fetch this run
- 2026-07-10T09:52:47Z — unchanged (not re-fetched): PR-level `gh api` check (see agentskills/agentskills entry) found no new merges, so page content assumed unchanged; skip deep re-fetch this run
- 2026-07-09T10:09:26Z — unchanged: full spec re-read, same 6 fields and constraints; no additions
- 2026-07-08T10:00:00Z — unchanged: full spec re-read, same 6 fields and constraints; no version/versioning-field/MCP-requirements additions
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** No new merges since #492 (Aug 9) — now a 15-day gap. No new open PRs beyond #508 (Aug 18, cosmetic client showcase). All previously-tracked substantive open PRs unchanged: #506 (eval-rubric rename, docs-only), #500 (reference Python SDK + schema validator), #486 (`name` field constraint clarification), #380 (versioning), #386/#345 (UTF-8/Unicode name), #254 (`.well-known` spec).

History:
- 2026-08-24T07:14:49Z — unchanged: `gh api` PR check — no new merges since #492 (15-day gap); no new open PRs since #508; #506/#500/#486/#380/#386/#345/#254 all still open+unmerged
- 2026-08-23T00:00:00Z — unchanged: `gh api` PR check — no new merges since #492 (14-day gap); no new open PRs since #508; #506/#500/#486/#380/#386/#345/#254 all still open+unmerged
- 2026-08-21T06:58:19Z — unchanged: `gh api` PR check — no new merges since #492 (12-day gap); new open PR #508 (client showcase, cosmetic); #506/#500/#486/#380/#386/#345/#254 still open+unmerged
- 2026-08-18T00:00:00Z — unchanged: `gh api` PR check — no new merges since #492; new open PR #506 (cosmetic docs rename, unmerged); #500/#486/#380/#386/#345/#254 still open+unmerged
- 2026-08-15T06:47:01Z — changed: new open PR #500 (Aug 14) — reference Python SDK + automated schema validator for SKILL.md compliance, not yet merged; no new merges since #492; #486/#380/#386/#345/#254 still open+unmerged
- 2026-08-12T00:00:00Z — unchanged: `gh pr list --state merged --limit 5` — no new merges since #492 (Aug 9); several new open client-showcase PRs (#493/#488/#482/#412) plus #486/#380/#386/#345/#254 still open+unmerged
- 2026-08-11T00:00:00Z — changed: `gh pr list --state merged --limit 5` — #491/#492 (Aug 9) merged, both client-showcase listings, no spec impact; #380/#386/#345/#254 confirmed still open+unmerged
- 2026-08-09T07:07:40Z — unchanged: `gh pr list --state merged --limit 10` — no new merges since #479 (Aug 4); #380/#386/#345/#254 confirmed still open+unmerged; new open PR #486 ("Clarify `name` field constraints", Aug 8) not yet merged, watch alongside #345 (same topic area)
- 2026-08-05T09:05:00Z — changed: `gh api` PR check — 5 new merges since #447 (#475-479, Aug 3-4), all client-branding/docs-clarification (incl. a `metadata` frontmatter field clarification, #479 — wording only, not a new field); #380/#386/#345/#254 confirmed still open+unmerged
- 2026-08-02T08:50:05Z — unchanged: `gh api` PR check — no new merges since #447; no new open PRs beyond the already-logged set (#473/#472/#470/#469/#465/#449); #380/#386/#345/#254 confirmed still open+unmerged
- 2026-08-01T08:32:39Z — unchanged: `gh api` PR check — no new merges since #447; #473 (AgentUse client showcase, Jul 29, already logged as new on the Jul 30 line below) still open, cosmetic listing only; #380/#386/#345/#254 confirmed still open+unmerged
- 2026-07-31T00:00:00Z — unchanged: `gh api` PR check — no new merges since #447; 22 open PRs (unchanged count from spec-impact perspective)
- 2026-07-30T08:45:00Z — unchanged: `gh api` PR check — no new merges since #447; new open PR #473 (client showcase, cosmetic); #380/#386/#345/#254 confirmed still open+unmerged
- 2026-07-29T00:00:00Z — unchanged: `gh api` PR check — no new merges since #447; new open PRs (#472, #470, #465-showcase area, #449) all cosmetic listing/docs; #380/#386/#345/#254 confirmed still open+unmerged
- 2026-07-27T10:30:00Z — unchanged: recent merges all cosmetic (client showcase/docs); new open PR #469 "Initial commit" appears to be spam (0 files changed); #380/#386/#345 confirmed still open
- 2026-07-23T09:00:00Z — unchanged: direct `gh api` PR check — no new merges since #461; #465 (client showcase, Jul 22) new open PR, listing-only; #380/#386/#345/#254 confirmed still open
- 2026-07-22T00:00:00Z — changed: #461 (client showcase) merged since #457 — listing-only, no spec impact; #380/#386/#345 confirmed still open; #254 new open PR noted
- 2026-07-16T00:00:00Z — unchanged: direct `gh api` PR list check — no new merges since #457; #380/#386/#345 confirmed still open
- 2026-07-15T00:00:00Z — unchanged: direct `gh api` PR list check — no new merges since #457; #380/#386/#345 confirmed still open
- 2026-07-14T00:00:00Z — changed: #457 (client showcase) merged since #447 — listing-only, no spec impact; #380/#386/#345 confirmed still open
- 2026-07-13T09:40:07Z — changed: #447 (client showcase) + #402 (client showcase) merged since #446 — both listing-only, no spec impact; #380/#386/#345 confirmed still open
- 2026-07-12T08:26:18Z — unchanged: direct `gh api` PR list check — #380/#386/#345 confirmed still open, no new activity; no new merges since #446
- 2026-07-10T09:52:47Z — unchanged: direct `gh api` PR list check (not WebFetch) — #380/#386/#345 confirmed still open with no new activity; newest PRs are docs/listing-only; no new merges since #446
- 2026-07-09T10:09:26Z — unchanged (shallow check only): WebFetch of repo root didn't surface PR list; agentskills.io/specification re-read same run found no new fields, so treated as unchanged — recommend a direct `gh api` PR check next run rather than the repo homepage
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** Re-fetched — still "Cloud Agents and Cursor Harness Improvements" (Aug 19, Custom Modes/Subscriptions/Subagents-on-own-machines/`/goal`/Steering) as the newest entry; no new entries in the 5-day gap.

History:
- 2026-08-24T07:14:49Z — unchanged: re-fetched, still Aug 19 "Cloud Agents and Cursor Harness Improvements" as newest entry; no new plugin/MCP/skills capability shipped since
- 2026-08-23T00:00:00Z — unchanged: re-fetched, still Aug 19 "Custom Modes" as newest entry; no new plugin/MCP/skills capability shipped since
- 2026-08-21T06:58:19Z — changed: "Custom Modes" (Aug 19) — pin any skill as an "always on" mode for the session; client-runtime UX feature, no known Claude Code equivalent, not a packaging-format signal — considered, not filed (see report)
- 2026-08-18T00:00:00Z — changed: "Origin Code Hosting" (Aug 17) — new Cursor code-hosting platform, GitHub-integrated; Cursor-infra-only, not iEvo-actionable
- 2026-08-15T06:47:01Z — changed: "Cloud Agents Start 3x Faster with Builds" (Aug 13) — pre-built dev environments for faster agent init; Cursor-client-only, not iEvo-actionable
- 2026-08-11T00:00:00Z — unchanged: re-fetched, still "Google Workspace Plugins" (Aug 3) as newest entry; no new plugin/MCP/skills capability shipped since
- 2026-08-09T07:07:40Z — unchanged: re-fetched, still "Google Workspace Plugins" (Aug 3) as newest entry; no new plugin/MCP/skills capability shipped since
- 2026-08-05T09:05:00Z — changed: "Google Workspace Plugins" (Aug 3) — new Gmail/Drive/Calendar integration plugins; content-integration capability, not a packaging/discovery-format change; not iEvo-actionable
- 2026-08-02T08:50:05Z — unchanged: re-fetched, still "Cursor, now on iPad" (Jul 29) as newest; no new plugin/MCP/skills capability shipped since
- 2026-08-01T08:32:39Z — unchanged: re-fetched, still "Cursor Start"/Cursor for iPad (Jul 29 entry) as newest; no new plugin/MCP/skills capability shipped since
- 2026-07-31T00:00:00Z — changed: "Cursor, now on iPad" (Jul 29) — iPad client availability; not iEvo-actionable
- 2026-07-30T08:45:00Z — unchanged: re-fetched, still "Cursor Start" (Jul 28) as newest; no new entries
- 2026-07-29T00:00:00Z — changed: "Cursor Start" (Jul 28) — new regional pricing tier; mentions existing plugins/MCP/skills/hooks bundling, no new capability; not iEvo-actionable
- 2026-07-27T10:30:00Z — unchanged: re-fetched, still "Cursor Router" (Jul 22) as newest; no new entries
- 2026-07-23T09:00:00Z — changed: "Cursor Router" (Jul 22) — model routing feature (Intelligence/Balance/Cost modes); Cursor-client-only, not iEvo-actionable
- 2026-07-22T00:00:00Z — unchanged: re-fetched, still v3.11 (July 10) as newest; no new entries
- 2026-07-16T00:00:00Z — unchanged: re-fetched, still v3.11 (July 10) as newest; no new entries
- 2026-07-15T00:00:00Z — unchanged: re-confirmed, still v3.11 (July 10) as newest; same hook set (beforeSubmitPrompt/afterAgentResponse/afterAgentThought/stop/subagentStart), already documented via F-2026-07-12-001/skills#367
- 2026-07-14T00:00:00Z — unchanged: re-confirmed, still v3.11 (July 10) as newest; F-2026-07-12-001/skills#367 already shipped as v0.51.0 (Cursor hooks doc)
- 2026-07-13T09:40:07Z — unchanged: re-confirmed, still v3.11 (July 10) as newest; F-2026-07-12-001/skills#367 already shipped as v0.51.0 (Cursor hooks doc)
- 2026-07-12T08:26:18Z — changed: v3.11 (July 10) — Side Chats, Conversation Search, Project/Repo pickers, Cloud Agent Hooks (beforeSubmitPrompt/afterAgentResponse/afterAgentThought/stop/subagentStart on stable hooks.json system); hooks-setup/SKILL.md has no Cursor coverage — triggered F-2026-07-12-001
- 2026-07-10T09:52:47Z — unchanged: v3.10 still newest (June 30); re-confirmed same feature set (Team MCPs, unified Customize page, /automate, /in-cloud); no new version
- 2026-07-09T10:09:26Z — unchanged: v3.10 still newest (June 30); no new version
- 2026-07-08T10:00:00Z — unchanged: same entries as July 7 (v3.10 newest, June 30); no new version
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
last_scan: 2026-08-24T07:14:49Z
status: changed
run_id: 32699971736
```

**Summary:** Different top-story set from Aug 23. "My agent.md to improve LLM-assisted code quality" (289pts) — a prompting/AGENTS.md-authoring guide, not a packaging/skill-format capability iEvo lacks; "Anthropic's best AI model struggles to attract users as cheaper tools thrive" (438pts) — market-adoption commentary, not actionable. No Claude Code/Codex/MCP/agent-skills-format capability items in the top 20. Nothing filed.

History:
- 2026-08-24T07:14:49Z — changed: different top-story set; "My agent.md to improve LLM-assisted code quality" (289pts, prompting-style guide, not a format gap) + "Anthropic's best AI model struggles to attract users" (438pts, market commentary); none agent-skill-format actionable, nothing filed
- 2026-08-23T00:00:00Z — changed: different top-story set; "A week of using Codex more than Claude" (179pts, just outside top 20, comparative usage) + "How a Texas student blew the whistle on a rogue AI hacking attempt" (148pts, AI-safety incident); none agent-skill-format actionable, nothing filed
- 2026-08-21T06:58:19Z — changed: different top-story set; "Codex on AWS Bedrock bug causing 10x charges" (billing, not format), "Malicious Rust crate Arrayref build-time payload" (465pts, supply-chain, corroborates known risk class not a new mechanism); none agent-skill-format actionable, nothing filed
- 2026-08-18T00:00:00Z — unchanged: quiet day; "AI-Generated GitHub Copilot Autofix Allowed Compromise of Snowflake's Jira" (354pts) considered — different mechanism, no iEvo capability-gap match — not filed
- 2026-08-15T06:47:01Z — unchanged: quiet day, no Claude Code/Codex/MCP/agent-skills/security items in top 15; "Maximizing the value of your Claude Code sessions" (~182pts, just outside top 15, usage tips not skill-format) considered, not filed
- 2026-08-12T00:00:00Z — unchanged: quiet day, no Claude Code/Codex/MCP/agent-skills/security items in top 15; nothing filed
- 2026-08-11T00:00:00Z — changed: quiet day; "Mcptoon" MCP CLI client (27pts, not actionable) + "How Claude marks AI-generated content" (115pts, watermarking not skill-format); neither filed
- 2026-08-09T07:07:40Z — changed: quiet day in top 15; "Message your other Claude Code sessions" (106pts, same feature as this run's claude-code/releases v2.1.224 entry, no separate action) + "Real-time MCP interceptor..." (8pts, considered, not filed — see Summary); neither filed as a new finding
- 2026-08-05T09:05:00Z — changed: "Stateless MCP has recaptured my interest" (173pts, MCP transport architecture, not iEvo-actionable — no MCP server/session in this plugin) + "Zero-Mem: Zero-Token Memory Operations for LLM Agents" (30pts, arxiv, agent-memory research, not actionable); neither filed
- 2026-08-02T08:50:05Z — changed: no agent-coding/Claude-Code/Codex/MCP/agent-skills/security items in today's top 15; quiet day, nothing filed
- 2026-08-01T08:32:39Z — changed: "qm – Multiplayer agent harness for work" (554 pts, standalone competing agent-orchestration platform, not a skill-format/plugin-packaging signal) — competitive context, not filed; "Tailscale didn't stop the Hugging Face intrusion" (540 pts, network-security incident, not skills-repo actionable) — considered, not filed
- 2026-07-31T00:00:00Z — changed: "GCC steering committee AI policy" (289 pts) + "Investigating three real-world incidents in our cybersecurity evaluations" (178 pts, Anthropic's own post, no iEvo action) + "Show HN: AI agent GUI" (44 pts); none agent-skill-format actionable
- 2026-07-30T08:45:00Z — changed: "Anatomy of a Frontier Lab Agent Intrusion" (375 pts, HuggingFace production incident — config-driven template-injection RCE) considered, not filed — no matching exploit chain in iEvo's own config-handling (structural-facts-only, no template evaluation); Gemma-in-2GB (779 pts), Superlogical (678 pts), Kimi K3 (422 pts) not actionable
- 2026-07-29T00:00:00Z — changed: "Codex Security" (490 pts, OpenAI's own new vuln-scan CLI product) — competitive context, not filed (too broad for an atomic finding); "Discovering Cryptographic Weaknesses with Claude" (215 pts, Anthropic model-capability research, no iEvo action); Kimi K3 (410 pts, model architecture, not actionable)
- 2026-07-27T10:30:00Z — changed: Kimi K3 + Postgres visualization + GrapheneOS wipe incident + TypeScript compiler + htmx trending; no agent-skill-format actionable items; none filed
- 2026-07-23T09:00:00Z — changed: Tao/ChatGPT math thread (852 pts) + Bento HTML-slideshow Show HN (816 pts) + Dvorak obituary (736 pts) + GigaToken fast-tokenization (490 pts); "ANSI escape injection in MCP servers" (8 pts) corroborates already-open #378, not a new finding; none filed
- 2026-07-22T00:00:00Z — changed: OpenAI/HF security-incident story (1099 pts) + ChatGPT ads (716 pts) + Gemini 3.6 Flash (682 pts) + Kimi K3 (588 pts) + Anthropic book-settlement (334 pts); MCP-server-usability-grading post (7 pts) considered, not a skills-repo gap; none filed
- 2026-07-16T00:00:00Z — changed: Inkling open-weights model (934 pts) + Grok Build open source (424 pts) + Coasty computer-use-agent API Launch HN (34 pts); none agent-skill-format actionable
- 2026-07-15T00:00:00Z — changed: "Cursor 0day" git.exe auto-exec disclosure (348 pts, vetted+rejected as an iEvo gap — see vetted-rejections.md) + Claude prompt-injection/secret-leak story (188 pts, already covered by existing security-auditor design); neither filed
- 2026-07-14T00:00:00Z — changed: "Clawk" disposable-VM-for-agents (191 pts) + agent-maturity-benchmark Show HN (4 pts) — both adjacent, neither a skills-repo capability gap; not filed
- 2026-07-13T09:40:07Z — changed: "Claude Code sends 33k tokens before reading the prompt" (587 pts) — token-overhead comparison, considered but not a skills-repo capability gap; not filed
- 2026-07-12T08:26:18Z — changed: Mindwalk agent-session-replay tool (19 pts) + Mesh LLM (233 pts) + Lisp-agent-in-100-lines (132 pts) + SQLite strict tables (278 pts); none agent-skill-format actionable
- 2026-07-10T09:52:47Z — changed: GPT-5.6 (1,270 pts) + Postgres-in-Rust (660 pts) + Ghostty/Zig interview (248 pts) + Muse Spark 1.1 + EU Chat Control discussion; none agent-skill-format actionable
- 2026-07-09T10:09:26Z — changed: coding-agent-eval-methodology posts (OpenAI "signal from noise" 217 pts, Databricks benchmarking 88 pts) + Microsoft Flint agent-visualization tool (285 pts) + GPT-Live (707 pts) + TypeScript 7 (624 pts); none actionable for the skills repo
- 2026-07-08T10:00:00Z — changed: "GitLost" GitHub-AI-agent private-repo-leak writeup (123 pts) — untrusted issue body -> agent tool call -> public exfiltration; directly informed a new security-hardening finding on security-auditor.md's report_template excerpt-quoting (see findings-backlog.md); "Show HN: Rowboat" (155 pts) not actionable
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
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** No new commits since `47c5590a` (Aug 10, "Add environment-adaptive tool guidance") — 14-day gap now. Confirmed via direct `gh api` commit check.

History:
- 2026-08-24T07:14:49Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); 14 days without activity
- 2026-08-23T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); 13 days without activity
- 2026-08-21T06:58:19Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); 11 days without activity
- 2026-08-18T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); 8 days without activity
- 2026-08-15T06:47:01Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); 5 days without activity
- 2026-08-12T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `47c5590a` (Aug 10); no new activity in the 2-day gap
- 2026-08-11T00:00:00Z — changed: 2 new commits after 42 days dormant — self-refining-recursive-harnesses guidance (Aug 9) + environment-adaptive-tools.md (Aug 10, 408-line new reference, SKILL.md v1.3.0→1.4.0); evaluated against iEvo's fixed-registry architecture, not directly applicable — considered, not filed (see Summary)
- 2026-08-09T07:07:40Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 41 days without activity
- 2026-08-05T09:05:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 37 days without activity
- 2026-08-02T08:50:05Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 34 days without activity
- 2026-08-01T08:32:39Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 33 days without activity
- 2026-07-31T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 32 days without activity
- 2026-07-30T08:45:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 31 days without activity
- 2026-07-29T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 30 days without activity
- 2026-07-27T10:30:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 28 days without activity
- 2026-07-23T09:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 24 days without activity
- 2026-07-22T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 23 days without activity
- 2026-07-16T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 17 days without activity
- 2026-07-15T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 16 days without activity
- 2026-07-14T00:00:00Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 15 days without activity
- 2026-07-13T09:40:07Z — unchanged: direct `gh api` commit check — latest commit still `b612ddbc`; 14 days without activity
- 2026-07-12T08:26:18Z — unchanged: direct `gh api` commit + reference-file-list check — latest commit still `b612ddbc`; 13 days without activity; 17 reference files, same set
- 2026-07-10T09:52:47Z — unchanged: direct `gh api repos/.../commits` check — latest commit still `b612ddbc` (June 29 21:15:08Z); 11 days without activity
- 2026-07-09T10:09:26Z — unchanged (shallow check only): WebFetch of repo root didn't surface commit timestamps; no visible new reference files in the overview; recommend `gh api repos/DenisSergeevitch/agents-best-practices/commits` next run instead of the webpage
- 2026-07-08T10:00:00Z — unchanged: gh api confirms latest commit still 2026-06-29T21:15:08Z (sha b612ddbc); 9 days without activity
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Not re-fetched; v2.1.235-238 release notes reviewed directly (spellcheck setting, ANTHROPIC_DEFAULT_MODEL, output style, plugin-marketplace headersHelper hardening, self-hosted-runner flags), none mention a SKILL.md frontmatter change.

History:
- 2026-08-21T06:58:19Z — unchanged: not re-fetched; v2.1.235-238 release notes reviewed directly, no SKILL.md frontmatter change mentioned
- 2026-08-18T00:00:00Z — unchanged: not re-fetched; v2.1.234 release notes reviewed directly, no SKILL.md frontmatter change mentioned
- 2026-08-15T06:47:01Z — unchanged: full independent re-fetch, same full frontmatter field set re-confirmed; noted (not new, previously un-itemized) the hard-error behavior for claude.ai/Skills-API packaging when a field outside the spec's 6 is present
- 2026-08-12T00:00:00Z — unchanged: not re-fetched; v2.1.228 release notes reviewed directly, no SKILL.md frontmatter change mentioned
- 2026-08-11T00:00:00Z — unchanged: not re-fetched; v2.1.227 release notes reviewed directly, no SKILL.md frontmatter change mentioned
- 2026-08-09T07:07:40Z — unchanged: not re-fetched; v2.1.223-226 release notes reviewed directly, no SKILL.md frontmatter change mentioned in any of the four
- 2026-08-05T09:05:00Z — unchanged: full re-fetch (triggered by v2.1.221/222), same 17-field table re-confirmed field-by-field; no new fields
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (no claude-code release since the July 27 full re-confirm — still v2.1.220)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (no claude-code release since the July 27 full re-confirm)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (no claude-code release since last full re-confirm)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (3-day gap since full re-confirm, no claude-code release since then — still v2.1.220)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (2-day gap since full re-confirm, no claude-code release since then)
- 2026-07-27T10:30:00Z — changed: field inventory correction — `background` field was always documented but not previously itemized (17 fields total now); underlying behavior already tracked; no new capability, no iEvo action
- 2026-07-23T09:00:00Z — unchanged: full re-fetch (no truncation), same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-16T00:00:00Z — unchanged (fetch truncated before reaching the frontmatter table twice; inferred unchanged from v2.1.211 release notes showing no new fields — flag for retry next run if truncation recurs)
- 2026-07-15T00:00:00Z — unchanged (not re-fetched): low cadence, v2.1.210's release notes (independently checked this run) show no new frontmatter fields; assumed stable
- 2026-07-14T00:00:00Z — unchanged: full re-fetch, same 16-field table; no new fields
- 2026-07-13T09:40:07Z — unchanged: full re-fetch, same 16-field table; no new fields
- 2026-07-12T08:26:18Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-10T09:52:47Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-09T10:09:26Z — unchanged: same 16-field table re-confirmed; noted docs now explicitly state commands/skills are unified (`.claude/commands/*.md` == `.claude/skills/*/SKILL.md`), confirms iEvo's existing `plugins/ievo/commands/` files are already skill-equivalent — no action needed
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Not re-fetched (low cadence, no signal expected — none of v2.1.235-238 mention Routines).

History:
- 2026-08-21T06:58:19Z — unchanged: not re-fetched (low cadence, no signal expected — none of v2.1.235-238 mention Routines)
- 2026-08-18T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.234 doesn't mention Routines)
- 2026-08-15T06:47:01Z — changed: full re-fetch (first since Jul 12) — run-history query via `/schedule` (v2.1.227+), CLI GitHub-trigger add requires v2.1.225+, expanded example-use-case list (Deploy verification/Docs drift/Library port); still no `claude schedule create` shell subcommand — F-2026-07-04-001 still stands; all other mechanics unchanged
- 2026-08-12T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.228 is bugfix/UI-polish only)
- 2026-08-11T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.227 is bugfix/UI-polish only)
- 2026-08-09T07:07:40Z — unchanged: not re-fetched (low cadence, no signal expected — none of v2.1.223-226 mention Routines)
- 2026-08-05T09:05:00Z — unchanged: not re-fetched (low cadence, no signal expected from v2.1.221/222 — neither release mentions Routines)
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (low cadence, no new claude-code release since v2.1.220)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-27T10:30:00Z — unchanged: quick check only (low cadence source), still "research preview," content reflects features already known as of Jul 22; no new dated capabilities
- 2026-07-12T08:26:18Z — unchanged: full re-read against the July 4 baseline (schedule list/update/run, one-off runs, 1h cron minimum, connectors/environments, GitHub trigger filters, /fire beta header) — no new or changed content
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Not re-fetched (low cadence, no signal expected — none of v2.1.235-238 mention Channels).

History:
- 2026-08-21T06:58:19Z — unchanged: not re-fetched (low cadence, no signal expected — none of v2.1.235-238 mention Channels)
- 2026-08-18T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.234 doesn't mention Channels)
- 2026-08-15T06:47:01Z — unchanged: full re-fetch, still research preview with same Telegram/Discord/iMessage/fakechat set; no GA, no new plugin
- 2026-08-12T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.228 is bugfix/UI-polish only)
- 2026-08-11T00:00:00Z — unchanged: not re-fetched (low cadence, no signal expected — v2.1.227 is bugfix/UI-polish only)
- 2026-08-09T07:07:40Z — unchanged: not re-fetched (low cadence, no signal expected — none of v2.1.223-226 mention Channels)
- 2026-08-05T09:05:00Z — unchanged: not re-fetched (low cadence, no signal expected from v2.1.221/222 — neither release mentions Channels)
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (low cadence, no new claude-code release)
- 2026-07-27T10:30:00Z — unchanged: quick check only (low cadence source), still "research preview," still Telegram/Discord/iMessage/fakechat plugin set; no GA, not iEvo-actionable
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
last_scan: 2026-08-21T06:58:19Z
status: unchanged
run_id: 32456237667
```

**Summary:** Not re-fetched; v2.1.235-238 release notes reviewed directly, none mention a sub-agent frontmatter change.

History:
- 2026-08-21T06:58:19Z — unchanged: not re-fetched; v2.1.235-238 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-18T00:00:00Z — unchanged: not re-fetched; v2.1.234 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-15T06:47:01Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-08-12T00:00:00Z — unchanged: not re-fetched; v2.1.228 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-11T00:00:00Z — unchanged: not re-fetched; v2.1.227 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-09T07:07:40Z — unchanged: not re-fetched; v2.1.223-226 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-05T09:05:00Z — unchanged: not re-fetched; v2.1.221/222 release notes reviewed directly, no sub-agent frontmatter change mentioned
- 2026-08-02T08:50:05Z — unchanged: not re-fetched (no new claude-code release since the July 27 full re-confirm)
- 2026-08-01T08:32:39Z — unchanged: not re-fetched (no new claude-code release since the July 27 full re-confirm)
- 2026-07-31T00:00:00Z — unchanged: not re-fetched (no new claude-code release since last full re-confirm)
- 2026-07-30T08:45:00Z — unchanged: not re-fetched (3-day gap, no new claude-code release)
- 2026-07-29T00:00:00Z — unchanged: not re-fetched (2-day gap, no new claude-code release)
- 2026-07-27T10:30:00Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-23T09:00:00Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-22T00:00:00Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-14T00:00:00Z — unchanged (not independently re-fetched): no signal of change from the adjacent skills.md re-fetch; same 16-field table assumed stable
- 2026-07-13T09:40:07Z — unchanged: full re-fetch, same 16-field table; no new fields
- 2026-07-12T08:26:18Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-10T09:52:47Z — unchanged: full re-fetch, same 16-field table re-confirmed field-by-field; no new fields
- 2026-07-09T10:09:26Z — unchanged: full re-read, same field table and `skills:`/`disallowedTools` semantics as July 6; no new fields
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

---

## https://agent-plugins.org

```yaml
last_scan: 2026-08-24T07:14:49Z
status: unchanged
run_id: 32699971736
```

**Summary:** No new activity since PR #65 (Aug 19, 1.1.0 working draft) — `#66`/`#67` (the two feature proposals against the 1.1.0 draft) both still open, unmerged; #67 last updated Aug 22, #66 last updated Aug 21 (comment activity only, no merge). Still watch-only.

History:
- 2026-08-24T07:14:49Z — unchanged: `gh api` PR check — #66 (updated Aug 21)/#67 (updated Aug 22) still open+unmerged, comment activity only; no new PRs against the 1.1.0 draft
- 2026-08-23T00:00:00Z — unchanged: `gh api` PR check — #66/#67 still open+unmerged, no new activity since Aug 19; no new PRs against the 1.1.0 draft
- 2026-08-21T06:58:19Z — changed: Agent Plugins 1.1.0 working draft started (PR #65 merged Aug 19) — spec/schemas forked from 1.0.0 into spec/1.1.0.md; two open proposal PRs against it same day: #67 namespaced skill discovery (skills/<namespace>/<skill>/ to avoid name collisions), #66 displayName + assets/icon.<format> convention for plugin.json; both unmerged, first confirmed spec movement since Aug 6 — see report for capability-gap read
- 2026-08-18T00:00:00Z — unchanged: `gh api` commit check — latest commit still `bd383552`/PR #38 (Aug 6); 12 days without activity
- 2026-08-15T06:47:01Z — unchanged: `gh api` commit check — latest commit still `bd383552`/PR #38 (Aug 6); 9 days without activity
- 2026-08-12T00:00:00Z — unchanged: `gh api` commit check — latest commit still `bd383552`/PR #38 (Aug 6); no new activity
- 2026-08-11T00:00:00Z — unchanged: `gh api` commit check — latest commit still `bd383552`/PR #38 (Aug 6); no new activity
- 2026-08-09T07:07:40Z — changed: `gh api` commit check — new commit `bd383552`/PR #38 (Aug 6, "Describe Agent Plugins as an open standard") — terminology-only, no schema/contract change per the PR's own description
- 2026-08-05T09:05:00Z — unchanged: `gh api` commit check on agentplugins/agent-plugins-spec — latest commit still the Jul 31 Lead Core Maintainer governance merge (`a8b0c5f9`); no new activity
- 2026-08-02T08:50:05Z — unchanged: `gh api` commit check on agentplugins/agent-plugins-spec — latest commit still the Jul 31 Lead Core Maintainer governance merge; no new activity
- 2026-08-01T08:32:39Z — unchanged: re-fetched; the Lead Core Maintainer governance record (2026-07-31) was already logged as governance-only activity on the Jul 31 line below — no new spec-repo activity since then; iEvo's own root `plugin.json` (F-2026-07-29-001/skills#501) has shipped and is now AGENTS.md-documented with two follow-up caveat paragraphs
- 2026-07-31T00:00:00Z — unchanged: spec repo governance-only activity (DCO removal, maintainer selection) since Jul 29; no schema change; no new confirmed consumer
- 2026-07-30T08:45:00Z — unchanged: `gh api` commit check on agentplugins/agent-plugins-spec — latest commit still 2026-07-27 push, no new activity; no new consumer-adoption signal
- 2026-07-29T00:00:00Z — first-scan: Agent Plugins 1.0.0 spec discovered via Codex rust-v0.146.0's new root plugin.json support; TSC = Amazon/Cursor/Microsoft/OpenAI/Vercel; triggered F-2026-07-29-001
