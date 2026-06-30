# Findings Backlog

Append-only log of every feature gap / capability finding Eva surfaces during research runs. One section per finding. Each finding eventually maps to an issue (or a closed status) in its target repo.

This file is the **strategic layer** of Eva's research output. The **tactical layer** is the issues themselves (in target repos). The **execution layer** is implementation PRs (handled by operator or by the Issue Triage helper from godfather task #42 once that lands).

## Format

Each finding is a Markdown section. Inside the section:

1. A ` ```yaml ` fenced block with metadata
2. The detailed proposal body — what the issue WILL say (or already says)

YAML schema (required keys):

```yaml
id: F-YYYY-MM-DD-NNN          # date + zero-padded sequence within day
discovered_at: <ISO 8601 UTC>
run_id: <GitHub Actions run ID that surfaced this>
target_repo: <ievo-ai/skills | ievo-ai/cortex | ievo-ai/agents | ...>
title: <one-line capability name>
status: raw | issued | accepted | implemented | rejected | parked
issue_url: <set when status transitions to issued>
effort: low | medium | high
scope: single-file | multi-file | new-skill | architecture-change
evidence:
  - <URL from Step 4 source scan>: <what triggered this>
```

Status transitions:
- `raw` — just discovered, not yet routed
- `issued` — issue opened in target_repo
- `accepted` — operator triaged with `accepted` label
- `implemented` — PR opened (manually or via Issue Triage helper) + merged
- `rejected` — operator closed issue with one-line reason
- `parked` — needs spec/design work first, revisit later

## How Eva uses this file per run

**Pre-research (Step 1):**
- Read the full file
- Build a `discovered_already` set: per `evidence` URLs and `title` semantic hash
- During Step 4b feature discovery, SKIP findings already represented (any status — even rejected ones don't re-propose)

**Post-discovery (Step 4b):**
- For each NEW finding meeting the gates:
  1. APPEND a new section here with `status: raw`
  2. Open a **very detailed** issue in `target_repo` per the schema below
  3. Update the entry: `status: issued`, `issue_url: <url>`
- Use the Edit tool to update entries in place (per-section), don't rewrite the whole file.

## Issue body template (what goes in `gh issue create --body-file`)

Issues filed from this backlog use this structure:

```markdown
# Proposal: <one-line capability>

## Summary

<1-2 sentences explaining the gap and the proposed direction>

## Problem / Capability gap

<what does iEvo currently lack? what would users be able to do better with this capability that they can't do today? Concrete user scenario(s).>

## Evidence

External signal triggering this proposal (with URLs from Step 4 source scan):
- <URL>: <one-line of what was observed there that triggered this>
- ...

## Proposed solution

<full design sketch: which files added, which modified, what API/UX surface, what the user-facing trigger looks like>

## Files affected

| File | Change | Notes |
|------|--------|-------|
| plugins/ievo/skills/X/SKILL.md | new | full skill structure |
| plugins/ievo/agents/Y.md | modified | add model alias |
| ... | ... | ... |

## API / UX surface

<commands, agent invocations, settings.json hooks, etc.>

## Acceptance criteria

- [ ] <criterion 1>
- [ ] <criterion 2>
- ...

## Effort estimate

- Scope: <single-file | multi-file | new-skill | architecture-change>
- Effort: <low (~30 min) | medium (~2 hr) | high (~half day or more)>
- Risk: <low | medium | high>

## Open questions for the operator

- <decision needed before implementation>
- ...

## Related

- **Eva research run:** https://github.com/ievo-ai/eva/actions/runs/<RUN_ID>
- **Backlog entry (ievo-ai/eva):** https://github.com/ievo-ai/eva/blob/main/researches/findings-backlog.md — search for `id: F-YYYY-MM-DD-NNN`
- **Companion proposals (if any) — always fully qualify the repo:** `ievo-ai/skills#N`, `ievo-ai/cortex#N`, etc. Never bare `#N` — this issue lives in <target_repo> but referenced PRs/issues may be in different repos, the reader can't disambiguate without the prefix.

---
Filed by Eva research run <$GITHUB_RUN_ID> against `ievo-ai/eva` (research repo). Triage with `accepted` / `rejected` / `needs-discussion` labels.
```

This issue template is intentionally **detailed** — operator preference 2026-05-22. The goal is for the operator (or a future Issue Triage helper from godfather task #42) to have enough specification to either accept-and-implement or reject-with-reason without a back-and-forth round. Detailed issue > shallow PR, especially when implementation cost is non-trivial.

## Constraints

- Hard cap: 3 findings per run. Quality over quantity; remaining gaps go in Deferred findings of the audit report.
- Cross-repo: `target_repo` can be any `ievo-ai/*`. Issue creation works on public repos with basic GitHub auth; no admin needed.
- No PR creation from Eva for feature proposals. PRs happen ONLY for audit fixes (Step 5, where Eva has full repo context and the change is mechanical). Feature additions go through the issue → triage → implement loop.

---

## F-2026-05-22-001 — hooks-setup Stop hook for background-agents-complete notification

```yaml
id: F-2026-05-22-001
discovered_at: 2026-05-22T17:01:00Z
run_id: 26301254869
target_repo: ievo-ai/skills
title: hooks-setup Stop hook for 'all background agents complete' notification
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/59
effort: medium
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.145 added background_tasks and session_crons fields to Stop/SubagentStop hook input — enables notification when all parallel subagents complete
  - https://github.com/anthropics/claude-code/releases: v2.1.143 added CLAUDE_CODE_STOP_HOOK_BLOCK_CAP env var (default 8) — constrains blocking stop hooks
```

*Backfilled from run 26301254869 which opened the issue but did not write the backlog entry.*

Extend `plugins/ievo/skills/hooks-setup/SKILL.md` (in-flight PR #58) with a Stop hook step that fires a desktop/terminal notification when `background_tasks` is empty. iEvo's parallel security-auditor + repo-indexer dispatch creates a concrete need: users want to know when all parallel scans complete. The Stop hook reads stdin JSON, checks `background_tasks.length === 0`, and fires an OS notification (macOS osascript, Linux notify-send, or terminalSequence bell fallback). Hook must be non-blocking (exit 0) due to CLAUDE_CODE_STOP_HOOK_BLOCK_CAP constraint.

---

## F-2026-05-22-002 — utf8-validate.mjs pre-commit validator for Codex compatibility

```yaml
id: F-2026-05-22-002
discovered_at: 2026-05-22T17:01:00Z
run_id: 26301254869
target_repo: ievo-ai/skills
title: Add utf8-validate.mjs pre-commit validator to prevent silent Codex skill-load failures
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/60
effort: low
scope: multi-file
evidence:
  - https://github.com/openai/codex/releases: rust-v0.133.0 (May 21, 2026) — AGENTS instruction loading now warns on invalid UTF-8 instead of silently dropping the file
  - https://github.com/agentskills/agentskills: PR #386 and PR #343 — both address UTF-8 encoding in skill validation tooling (active cross-ecosystem concern)
```

*Backfilled from run 26301254869 which opened the issue but did not write the backlog entry.*

Add `.github/scripts/validators/utf8-validate.mjs` using `TextDecoder({ fatal: true })` to detect invalid byte sequences in SKILL.md, agent .md, and AGENTS.md files before they reach Codex users. Wire into `.pre-commit-config.yaml` and update AGENTS.md validator list. 100% coverage rule does NOT apply (validator lives in `.github/scripts/validators/`, not `plugins/ievo/scripts/`). Concrete risk: the hooks-setup skill being added in PR #58 includes escape sequences that could be corrupted on Windows. ~20-line validator, ~30-min implementation.

---

## F-2026-05-22-003 — /ievo:overlay-status skill — surface current evolution overlay state

```yaml
id: F-2026-05-22-003
discovered_at: 2026-05-22T17:34:04Z
run_id: 26302374682
target_repo: ievo-ai/skills
title: /ievo:overlay-status skill — list and summarize active evolution overlays in the current project
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/61
effort: low
scope: new-skill
evidence:
  - https://github.com/DenisSergeevitch/agents-best-practices/blob/main/references/agent-legibility-feedback-loops.md: "What the agent cannot inspect, retrieve, validate, or act on through approved tools is operationally absent from the agent's world" — directly applies to iEvo overlays which live in .ievo/evolution/ but are invisible to the agent without manual file reads
  - https://github.com/ievo-ai/skills/blob/main/coverage-audit.md: explicitly marks "Standalone 'list installed iEvo overlays' command" as a gap with note "User can cat .ievo/evolution/agents/*.md but there's no skill that summarises the overlay state"
```

A new `/ievo:overlay-status` skill (in `plugins/ievo/skills/overlay-status/SKILL.md`) that reads `.ievo/evolution/` tree and produces a structured summary: which scopes have overlays (agents/, skills/, project/), how many lessons per scope, last-modified dates, and the one-line summary of each overlay's content. Activates when user asks "what evolutions have I captured?", "show my iEvo overlays", "what rules are active?", or "summarize my .ievo/evolution/". Implementation: pure Read + Glob calls, no sub-agent needed. No scripts required (no test coverage obligation). Single new SKILL.md, ~100–150 lines. The coverage-audit.md gap row should also be updated to "covered" when implemented.

---

## F-2026-05-24-001 — /ievo:inspect skill — pre-install structured summary of a remote skill/repo

```yaml
id: F-2026-05-24-001
discovered_at: 2026-05-24T07:23:12Z
run_id: 26354909799
target_repo: ievo-ai/skills
title: /ievo:inspect skill — lightweight pre-install inspection of a remote skill or plugin repo
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/67
effort: low
scope: new-skill
evidence:
  - https://github.com/anthropics/claude-code/releases/tag/v2.1.145: /plugin Discover/Browse now shows commands, agents, skills, hooks, and MCP/LSP servers BEFORE installation — Claude Code's native preview surfaces capability summary before install commitment
  - https://github.com/DenisSergeevitch/agents-best-practices/blob/main/references/checklists.md: Skills checklist item "Skill does not silently expand permissions" — implies pre-install verification; the harness principle is that capabilities should be inspectable before they are invoked
```

A new `/ievo:inspect <owner>/<repo>` skill that produces a structured human-readable summary of what a remote skill/plugin repo contains — without running the full 6-stage `/ievo:init` pipeline. Activates when the user asks "what does this skill do?", "show me what's in `anthropics/claude-skills`", "inspect `owner/repo` before I install it", or "summarise this skill without installing". The skill fetches the repo's SKILL.md (or AGENTS.md) via `gh api`, extracts the names and descriptions of all skills/agents/commands/scripts, and renders a capability summary: what the plugin does, what permissions it needs (`allowed-tools`), and which platforms it targets (`compatibility`). Does NOT run security scan (security-check handles that). Does NOT install anything. Replaces the current workaround of manually catting files via `gh api repos/<owner>/<repo>/contents/`. Implementation: pure gh API calls + Read, no scripts required, single new SKILL.md (~100 lines). The coverage-audit.md does not have a row for standalone pre-install inspection.

---

## F-2026-05-24-002 — validate_skills.mjs — mechanical SKILL.md spec compliance validator

```yaml
id: F-2026-05-24-002
discovered_at: 2026-05-24T07:23:12Z
run_id: 26354909799
target_repo: ievo-ai/skills
title: Add validate_skills.mjs to enforce agentskills.io spec constraints on SKILL.md frontmatter
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/68
effort: medium
scope: multi-file
evidence:
  - https://agentskills.io/specification: compatibility field max 500 chars now explicitly documented; description ≤1024; name ≤64 lowercase alnum+hyphens no consecutive/leading/trailing, must match directory — multiple constraints checkable without LLM reasoning
  - https://github.com/DenisSergeevitch/agents-best-practices/blob/main/references/checklists.md: Mechanical invariant checklist — "Repeated prompt guidance has been converted into validators where possible. Validator errors include model-readable remediation instructions." — the spec constraints are exactly "repeated prompt guidance" and exactly machine-enforceable
  - hooks-setup/SKILL.md: compatibility field is 537 chars (over the 500-char limit) — this violation shipped in v0.6.9 and was caught only by a manual audit run, not mechanically
```

Add `plugins/ievo/scripts/validate_skills.mjs` that checks every `plugins/ievo/skills/*/SKILL.md` against the agentskills.io spec constraints: (1) `name` present, ≤64 chars, lowercase alnum+hyphens, no consecutive/leading/trailing hyphens, matches parent directory name; (2) `description` present, ≤1024 chars; (3) `compatibility` present-if-set and ≤500 chars; (4) no CRLF in frontmatter (already checked by `crlf-frontmatter.mjs` but only for agents — needs extension or a separate SKILL.md-specific pass). Wire into `.pre-commit-config.yaml` and the `pre-commit-gate.yml` workflow alongside the existing 5 validators. Must have 100% test coverage per AGENTS.md rule (the script lives in `plugins/ievo/scripts/` — not in `.github/scripts/validators/`). Concrete precedent: `validate_agents.mjs` already does this for `agents/*.md` vendor-neutral model checking; `validate_skills.mjs` is the parallel for `skills/*/SKILL.md`. Immediate payoff: the `hooks-setup/SKILL.md` compatibility-length violation fixed in v0.6.13 would have been caught at commit time instead of requiring a dedicated audit run.

---

## F-2026-05-25-001 — Add `effort:` frontmatter to all 9 SKILL.md files

```yaml
id: F-2026-05-25-001
discovered_at: 2026-05-25T07:48:17Z
run_id: 26389613586
target_repo: ievo-ai/skills
title: Add effort: frontmatter to all 9 SKILL.md files to enable status-bar effort display
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/83
effort: low
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.149 fixed effort: frontmatter not reflected in status bar — fix is live but iEvo skills don't declare effort values
  - https://code.claude.com/docs/en/skills.md: effort: documented as first-class frontmatter field (low/medium/high/xhigh/max); overrides session effort when skill is active
```

None of the 9 iEvo SKILL.md files declare `effort:` frontmatter. Claude Code v2.1.149 fixed the bug where this field was not shown in the status bar — but the fix only helps skills that have the field. Adding accurate values (init→max, security-check→high, index-repos→medium, all others→low) lets users see the expected time/cost before activation. Multi-file but purely additive frontmatter change: one line per SKILL.md file, no logic or body content modified.

---

## F-2026-05-25-002 — `/ievo:schedule` skill for creating Claude Code Routines

```yaml
id: F-2026-05-25-002
discovered_at: 2026-05-25T07:48:17Z
run_id: 26389613586
target_repo: ievo-ai/skills
title: /ievo:schedule skill — guided wizard for creating a Routine to periodically run iEvo operations
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/84
effort: medium
scope: new-skill
evidence:
  - https://code.claude.com/docs/en/routines.md: Routines newly documented — /schedule command creates account-level scheduled sessions; triggers: cron, GitHub events, HTTP API; Pro/Max/Team/Enterprise required
  - https://github.com/anthropics/claude-code/releases: v2.1.149 confirms Routines shipped and stable
```

A new `/ievo:schedule` skill that guides users through creating a Claude Code Routine for periodic iEvo operations (weekly security audits, daily evolution captures, on-PR dependency scans). Uses AskUserQuestion to select operation type and frequency, then invokes `/schedule` with a constructed prompt. Handles the unavailability case (ANTHROPIC_API_KEY set, Free plan) with CI cron job fallback instructions. Fills the gap where iEvo currently only runs on manual invocation — security drift accumulates silently between runs.

---

## F-2026-05-25-003 — Audit ievo-ai/eva workflows for deprecated claude-code-action@v0.x inputs

```yaml
id: F-2026-05-25-003
discovered_at: 2026-05-25T07:48:17Z
run_id: 26389613586
target_repo: ievo-ai/eva
title: Audit and migrate ievo-ai/eva GitHub Actions workflows from deprecated claude-code-action@v0.x inputs to v1.0 API
status: issued
issue_url: https://github.com/ievo-ai/eva/issues/65
effort: medium
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code-action/releases: v1.0 GA (2026-05-13) removed mode/direct_prompt/override_prompt and deprecated model/allowed_tools/mcp_config/custom_instructions — replaced by prompt + claude_args
  - https://github.com/ievo-ai/eva/actions: deferred from three consecutive research runs (26283289533, 26294170594, 26302374682) — overdue
```

Eva's `.github/workflows/` likely contains workflows (eva-review-pr.yml and others) using deprecated v0.x inputs (`direct_prompt`, `mode`, `model`, `allowed_tools`). If so, the workflows invoke Claude with no operative instruction after the v1.0 migration — silent failure. This finding has been deferred from three consecutive research runs (2026-05-22 ×3). The audit involves reading 3–5 workflow files, identifying deprecated inputs, and rewriting them to use `prompt:` and `claude_args:`. Medium effort, medium risk (CI breaks silently if not done).

---

## F-2026-05-26-001 — Missing project-level `/ievo:vuln-scan` orchestrator skill

```yaml
id: F-2026-05-26-001
discovered_at: 2026-05-26T07:30:00Z
run_id: 26438438877
target_repo: ievo-ai/skills
title: Add project-level /ievo:vuln-scan orchestrator skill (Phase 1 threat model + parallel module dispatch + aggregated report)
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/110
effort: medium
scope: new-skill
evidence:
  - https://www.anthropic.com/research/glasswing-initial-update: describes "scanning harness that maps codebases and spins up scanning subagents" as the required orchestration layer — the current vuln-scan/SKILL.md is only the per-module worker
  - https://code.claude.com/docs/en/sub-agents: parallel subagent dispatch via Task tool is the mechanism for project-level orchestration; vuln-scanner.md is the per-module agent but has no orchestrator that enumerates modules and kicks off the parallel dispatch
```

The `vuln-scan/SKILL.md` is written as a per-module worker: its own "Input" section states "Provided by the vuln-scanner agent dispatch: module_path, threat_context, scope_metadata" — these inputs must come from an orchestrator, but no orchestrator exists. The SKILL.md description itself says "orchestrated by the /ievo:vuln-scan command" — confirming a separate orchestrator was intended but not shipped.

Without the orchestrator, a user who invokes `/ievo:vuln-scan` gets the per-module worker with no module path, no threat model, and no aggregation — the skill cannot complete Phase 1 (read all source files) or Phase 4 (build exploit chains) without those inputs.

The Glasswing paper describes the required orchestration: (1) codebase mapping — enumerate modules/packages, (2) threat modeling — identify entry points, trust boundaries, attack surfaces for each module, (3) parallel dispatch — spin up one scanner per module, (4) triage and aggregation — correlate cross-module findings, de-duplicate, rank by severity.

Proposed solution: a new `plugins/ievo/skills/init-vuln-scan/SKILL.md` (or a top-level `vuln-scan` orchestrator body replacing the current per-module body) that handles the full lifecycle. The current vuln-scan/SKILL.md should be renamed to distinguish the per-module worker from the project-level command.

---

## F-2026-05-27-001 — Add `disallowed-tools` to security-check and vuln-scan SKILL.md for read-only enforcement

```yaml
id: F-2026-05-27-001
discovered_at: 2026-05-27T07:38:00Z
run_id: 26497701957
target_repo: ievo-ai/skills
title: Add disallowed-tools frontmatter to security-check and vuln-scan skills to enforce read-only mode during assessment
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/139
effort: low
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.152 (2026-05-27) added disallowed-tools in skill/command frontmatter — skills can now block specific tools during execution
  - https://code.claude.com/docs/en/skills.md: disallowed-tools documented as complement to allowed-tools; space-separated tool specs (Bash(rm*), Write, Edit, etc.)
```

Claude Code v2.1.152 introduced `disallowed-tools` frontmatter for skills, complementing the existing `allowed-tools` field. The security-check and vuln-scan skills perform threat assessment of third-party code — but currently run with full tool access. Adding `disallowed-tools: Write Edit Bash(rm*) Bash(mv*) Bash(curl*) Bash(wget*)` (or similar) to both SKILL.md files would enforce read-only mode during security assessment, reducing the blast radius if a malicious skill under review manages to influence the assessor's execution context. This is a concrete security hardening enabled by v2.1.152.

---

## F-2026-05-27-002 — hooks-setup/SKILL.md stale on v2.1.152 hook additions (MessageDisplay + SessionStart enhancements)

```yaml
id: F-2026-05-27-002
discovered_at: 2026-05-27T07:38:00Z
run_id: 26497701957
target_repo: ievo-ai/skills
title: Update hooks-setup/SKILL.md to document Claude Code v2.1.152 hook additions (MessageDisplay hook + SessionStart reloadSkills/sessionTitle)
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/140
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.152 added MessageDisplay hook type (fires when a message is displayed) + SessionStart hook can now return reloadSkills: true and set sessionTitle
  - https://github.com/anthropics/claude-code/releases: /reload-skills command added in v2.1.152 — can be triggered from SessionStart hook return value
```

Claude Code v2.1.152 added two hook enhancements not yet documented in `hooks-setup/SKILL.md`: (1) a new `MessageDisplay` hook type that fires each time a message is displayed, useful for session logging or custom display; (2) `SessionStart` hooks can now return `{ reloadSkills: true, sessionTitle: "..." }` — auto-reloads skills without requiring a manual `/reload-skills` command and sets the session display title. The hooks-setup skill covers PostToolUse and Stop hooks but has no reference to v2.1.152 additions. Update SKILL.md body to document both: (a) add `MessageDisplay` to the hook type table with an example use case, (b) document SessionStart return fields `reloadSkills` and `sessionTitle` with a concrete iEvo use case (auto-reload skills when `.ievo/` directory is detected on project open).

---

## F-2026-05-27-003 — validate_skills.mjs missing effort: field validation

```yaml
id: F-2026-05-27-003
discovered_at: 2026-05-27T07:38:00Z
run_id: 26497701957
target_repo: ievo-ai/skills
title: Add effort: field validation to validate_skills.mjs (warn on absent, error on invalid value)
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/141
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/skills.md: effort: is documented as a first-class frontmatter field; valid values: low, medium, high, xhigh, max
  - https://github.com/anthropics/claude-code/releases: v2.1.149 fixed effort: not being reflected in status bar — field is now user-visible and incorrect values are silent failures
  - plugins/ievo/scripts/validate_skills.mjs: does not validate effort: field at all (confirmed by reading source)
```

All 13 iEvo SKILL.md files now declare `effort:` (added via skills#83) but `validate_skills.mjs` does not validate this field. Since `effort:` is now a user-visible field (Claude Code status bar since v2.1.149), a typo (e.g. `effort: hight`) or a missing value on a new skill would pass validation silently. The fix: add a `checkEffortField(effort)` function that (1) warns if `effort:` is absent, (2) errors if the value is not in `{low, medium, high, xhigh, max}`. Wire into `validateSkillContent()`. Also requires updating `validate_skills.test.mjs` with test cases for each branch (absent, valid, invalid value) — the 100% coverage rule applies since `validate_skills.mjs` lives in `plugins/ievo/scripts/`. Scope: validate_skills.mjs + validate_skills.test.mjs (~30 new lines + ~6 new test cases).

---

## F-2026-05-28-001 — Codex v0.134.0 hook parity in hooks-setup/SKILL.md

```yaml
id: F-2026-05-28-001
discovered_at: 2026-05-28T08:00:00Z
run_id: 26561249253
target_repo: ievo-ai/skills
title: Add Codex hook types (SubagentStart, SubagentStop, TurnStartedEvent) to hooks-setup/SKILL.md for universal positioning
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/155
effort: low
scope: single-file
evidence:
  - https://github.com/openai/codex/releases: v0.134.0 (2026-05-26) — added subagent identity to hook inputs + trace_id to TurnStartedEvent; the SubagentStart/SubagentStop/TurnStartedEvent hooks themselves pre-date this release (Codex Hooks GA ~May 14); conversation history available in extensions
```

Codex v0.134.0 (2026-05-26) added subagent identity to hook inputs and trace_id to TurnStartedEvent; the SubagentStart, SubagentStop, and TurnStartedEvent hooks themselves pre-date this release (Codex Hooks GA ~May 14). The `hooks-setup/SKILL.md` is the authoritative iEvo guide for configuring lifecycle hooks, but it currently only documents Claude Code hooks (PostToolUse, Stop, SessionStart, MessageDisplay). Since iEvo explicitly supports Codex (ships `.codex-plugin/marketplace.json`) and AGENTS.md states "Not a Claude Code-only plugin", the hooks-setup skill should document equivalent Codex hooks. Users running iEvo on Codex see Claude Code hook instructions but have no guidance on Codex-native equivalents — violating the universal positioning promise. Implementation: add a "Codex hooks" section documenting SubagentStart (fires when a sub-agent starts), SubagentStop (fires when sub-agent completes — counterpart to Claude Code's SubagentStop hook already in Stop section), TurnStartedEvent (per-turn trigger). Pure documentation addition, no scripts required, no test coverage obligation.

---

## F-2026-05-29-001 — Add `disallowed-tools` safety constraint to `deep-review/SKILL.md`

```yaml
id: F-2026-05-29-001
discovered_at: 2026-05-29T07:38:29Z
run_id: 26624450956
target_repo: ievo-ai/skills
title: Add disallowed-tools safety constraint to deep-review/SKILL.md to enforce read-only pledge at platform level
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/156
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.152 (2026-05-27) added disallowed-tools as a first-class SKILL.md frontmatter field — removes named tools from the model while the skill is active
  - /tmp/skills/plugins/ievo/skills/security-check/SKILL.md: already uses disallowed-tools: [Write, Edit, Bash(rm*)] — established pattern in the repo
  - /tmp/skills/plugins/ievo/skills/vuln-scan/SKILL.md: same disallowed-tools pattern — confirmed both security-critical skills use it
  - /tmp/skills/plugins/ievo/skills/deep-review/SKILL.md: no allowed-tools or disallowed-tools declared despite explicit read-only design intent (gap-detection only, no file modifications)
```

`deep-review/SKILL.md` describes a read-only gap-detection review skill: "Structured 10-point gap-detection review of a diff before commit." The skill orchestrates a `deep-reviewer` sub-agent and performs diff analysis. It has no tool constraints — any tool the model can access remains accessible while the skill is active.

Both security-critical sibling skills (`security-check`, `vuln-scan`) already declare `disallowed-tools: [Write, Edit, Bash(rm*)]`, making their read-only pledge verifiable at the platform level rather than just as text in the skill body. `deep-review` lacks this, leaving a gap between its stated intent and its actual platform-enforced behavior.

Adding `disallowed-tools: [Write, Edit, Bash(rm*)]` to `deep-review/SKILL.md` would:
1. Enforce the read-only contract at the platform level (Claude Code + Codex honor `disallowed-tools`)
2. Prevent accidental file modifications if the skill body or the deep-reviewer agent steps deviate
3. Align `deep-review` with the security pattern already established by `security-check` and `vuln-scan`

The change requires a version bump per AGENTS.md rules (four files + CHANGELOG.md entry).

---

## F-2026-05-29-002 — Add `effort:` frontmatter to all 5 agent .md files

```yaml
id: F-2026-05-29-002
discovered_at: 2026-05-29T07:38:29Z
run_id: 26624450956
target_repo: ievo-ai/skills
title: Add effort: frontmatter to all 5 iEvo agent .md files to pin reasoning depth per agent role
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/157
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/sub-agents: effort: is now a first-class agent frontmatter field (values low/medium/high/xhigh/max); overrides session effort when the sub-agent is active
  - https://github.com/anthropics/claude-code/releases: v2.1.154 (2026-05-28) released Opus 4.8 defaulting to effort xhigh; v2.1.152 formalized effort: field for agents
  - /tmp/skills/plugins/ievo/agents/evolution.md: model: opus — with Opus 4.8 defaulting to xhigh, this agent inherits xhigh effort for a task (append lesson to overlay file) that needs only low reasoning depth
  - /tmp/skills/plugins/ievo/agents/*.md: none of the 5 iEvo agents declare effort: frontmatter
```

All 5 iEvo agent files (`deep-reviewer.md`, `evolution.md`, `repo-indexer.md`, `security-auditor.md`, `vuln-scanner.md`) lack `effort:` frontmatter. Per Claude Code's sub-agents documentation, `effort:` overrides the session effort level when the sub-agent is dispatched.

Without `effort:`, agents inherit the parent session's effort setting. With Opus 4.8 now defaulting to `effort: xhigh`, this creates a cost asymmetry: the `evolution` agent (model: opus, task: append structured text to overlay file) may run at `xhigh` effort, burning significant tokens on a mechanical task. Conversely, the `security-auditor` and `vuln-scanner` agents (deep security analysis) would benefit from an explicit `effort: high` to ensure thorough analysis regardless of the session context.

Proposed `effort:` values per agent role:

| Agent | Model | Task complexity | Proposed effort |
|-------|-------|-----------------|-----------------|
| `evolution.md` | opus | Append lesson to overlay file | `low` |
| `deep-reviewer.md` | sonnet | Structured code review | `medium` |
| `repo-indexer.md` | sonnet | Mechanical repo scanning (scan_repo.mjs) | `low` |
| `security-auditor.md` | sonnet | Deep security analysis | `high` |
| `vuln-scanner.md` | sonnet | Exploit-chain vulnerability analysis | `high` |

This prevents both over-spending (evolution at xhigh) and under-investing (security agents at low from a haiku-tier session).

---

## F-2026-05-29-003 — Explicitly declare `defaultEnabled: true` in plugin.json

```yaml
id: F-2026-05-29-003
discovered_at: 2026-05-29T07:38:29Z
run_id: 26624450956
target_repo: ievo-ai/skills
title: Add defaultEnabled: true to plugin.json to be explicit about plugin activation intent
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/158
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.154 (2026-05-28) introduced defaultEnabled: false as a new plugin.json field — plugins can now explicitly opt out of being enabled by default
  - /tmp/skills/plugins/ievo/.claude-plugin/plugin.json: current file has no defaultEnabled field; relies on implicit default behavior that is now configurable
```

Claude Code v2.1.154 introduced `defaultEnabled: false` as an explicit plugin.json field. Before this release, plugins had no such field and were presumably always enabled after install. The introduction of the field means the runtime now reads and acts on this value.

iEvo's `plugins/ievo/.claude-plugin/plugin.json` currently has no `defaultEnabled` field. Relying on implicit default behavior is fragile — if a future Claude Code version changes the absent-field semantics (e.g., to require explicit opt-in for enterprise compliance reasons), iEvo would silently become disabled for existing installations.

Adding `"defaultEnabled": true` is a 1-line JSON addition that:
1. Makes iEvo's activation intent explicit and self-documenting
2. Future-proofs against potential semantics changes in the `defaultEnabled` field
3. Follows the principle of "explicit is better than implicit" for platform manifests

The change requires a version bump per AGENTS.md rules (four files + CHANGELOG.md entry).

---

## F-2026-05-30-001 — `hooks` frontmatter in iEvo SKILL.md files for per-skill lifecycle hooks

```yaml
id: F-2026-05-30-001
discovered_at: 2026-05-30T07:15:49Z
run_id: 26677717819
target_repo: ievo-ai/skills
title: Add hooks frontmatter to evolution, security-check, and init SKILL.md files for per-skill lifecycle hooks
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/159
effort: medium
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.152 introduced hooks as a first-class SKILL.md frontmatter field — lifecycle hooks scoped to the skill's active context
  - https://code.claude.com/docs/en/skills.md: hooks frontmatter documented alongside effort:, disallowed-tools, context:fork — enables per-skill PostToolUse/Stop hooks without global settings.json changes
```

Claude Code v2.1.152 introduced `hooks` as a SKILL.md frontmatter field, enabling skills to declare lifecycle hooks scoped to the skill itself. None of the 14 current iEvo SKILL.md files use this. The `evolution`, `init`, and `security-check` skills each have natural completion events (overlay write, pipeline complete, parallel scan complete) that users want to observe. Currently users must set up global hooks via `/ievo:hooks-setup` — per-skill hooks provide a zero-configuration alternative bundled with each skill. Additionally, `hooks-setup/SKILL.md` should document per-skill hooks as a complementary tier.

---

## F-2026-05-30-002 — Document `.claude/skills` auto-load install path in README and init skill

```yaml
id: F-2026-05-30-002
discovered_at: 2026-05-30T07:15:49Z
run_id: 26677717819
target_repo: ievo-ai/skills
title: Document git-clone install path via .claude/skills auto-load (Claude Code v2.1.157)
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/160
effort: low
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.157 (2026-05-29) — plugins in .claude/skills directories now auto-load without marketplace; claude plugin init scaffolds plugins
  - https://code.claude.com/docs/en/skills.md: .claude/skills/ confirmed as canonical auto-load path for local plugin development and Routines
```

Claude Code v2.1.157 added auto-loading of plugins from `.claude/skills` directories without marketplace registration. iEvo's README only documents marketplace install and manual copy. The new `git clone https://github.com/ievo-ai/skills.git ~/.claude/skills/ievo` path is simpler and version-controlled. The `schedule/SKILL.md` compatibility note should also clarify that Routines use skills from the project's `.claude/skills/` directory (different from the global `~/.claude/skills/`).

---

## F-2026-05-30-003 — Dynamic context injection for prerequisite verification in init/SKILL.md

```yaml
id: F-2026-05-30-003
discovered_at: 2026-05-30T07:15:49Z
run_id: 26677717819
target_repo: ievo-ai/skills
title: Add dynamic context injection (!`command`) to init/SKILL.md and security-check/SKILL.md for prerequisite verification
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/161
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/skills.md: documents !`command` syntax for dynamic context injection — shell output inlined at skill load time before Claude reads the body; also $CLAUDE_SKILL_DIR/$CLAUDE_SESSION_ID/$CLAUDE_EFFORT substitution vars
  - https://github.com/anthropics/claude-code/releases: v2.1.152 shipped context:fork and dynamic context injection as part of the skill extensibility release
```

Claude Code v2.1.152+ supports `` !`command` `` syntax in SKILL.md: shell commands whose stdout is injected into the skill context at load time. `/ievo:init` requires Node 18+, gh CLI, git, and network access, but surfaces missing prerequisites only after mid-pipeline failure. A `context:` frontmatter block with 4 `` !`command` `` checks (node, gh auth, git, network) would surface all issues in the first skill response. `/ievo:security-check` would benefit from a gh auth check. On platforms without the feature, unknown frontmatter is ignored gracefully.

---

## F-2026-05-31-001 — `/ievo:workflow` skill for large-scale parallel orchestration via Dynamic Workflows

```yaml
id: F-2026-05-31-001
discovered_at: 2026-05-31T00:00:00Z
run_id: 26706515829
target_repo: ievo-ai/skills
title: /ievo:workflow skill — guided setup for large-scale parallel agent orchestration using Claude Code Dynamic Workflows
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/162
effort: medium
scope: new-skill
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.154 (2026-05-28) — Dynamic Workflows launched: /workflows command orchestrates tens to hundreds of background agents for large-scale tasks
  - https://github.com/DenisSergeevitch/agents-best-practices: new references/workflow-orchestration.md (+261 lines, 2026-05-30) — concrete workflow orchestration patterns for multi-agent pipelines
```

A new `/ievo:workflow` skill that guides users through setting up a Claude Code Dynamic Workflow for large-scale iEvo operations — security scanning an entire GitHub org's repos, running evolution captures across multiple projects simultaneously, or doing a bulk skill-discovery pass. Dynamic Workflows (v2.1.154) orchestrate tens to hundreds of background agents, viewable via `/workflows`. This directly extends iEvo's existing parallel agent patterns (init already dispatches security-auditor + repo-indexer in parallel for a handful of candidates) to a much larger scale. The skill would help users construct the workflow prompt, select target repos, and configure the `/schedule` trigger for recurring runs. Fills the gap between single-project iEvo operations and org-wide continuous security posture management.

---

## F-2026-05-31-002 — Add `effort:` field validation to `validate_agents.mjs`

```yaml
id: F-2026-05-31-002
discovered_at: 2026-05-31T00:00:00Z
run_id: 26706515829
target_repo: ievo-ai/skills
title: Add effort: field validation to validate_agents.mjs (warn on absent, error on invalid value)
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/163
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/sub-agents: effort: field documented as valid agent frontmatter (low/medium/high/xhigh/max) — overrides session effort when the agent runs; first-scan 2026-05-31
  - https://github.com/anthropics/claude-code/releases: v2.1.154 Opus 4.8 defaults to high effort — effort: frontmatter in agents lets operators pin the intended effort regardless of session default
```

`validate_skills.mjs` already validates `effort:` in SKILL.md files — warning on absent, error on invalid value. But `validate_agents.mjs` only validates `model:` field for vendor-neutral aliases; it does not check `effort:`. Now that the sub-agents documentation explicitly documents `effort:` as a valid agent frontmatter field (same values: low/medium/high/xhigh/max), the validator should enforce the same pattern for consistency. This catches mis-typed values before they silently fail (e.g. `effort: medium-high` or `effort: fast`). Implementation: extend `validate_agents.mjs` with the same effort-validation logic as `validate_skills.mjs`; add corresponding test cases to `validate_agents.test.mjs` to maintain 100% coverage.

---

## F-2026-05-31-003 — Lightweight pre-classifier step in `/ievo:security-check` to triage before deep scan

```yaml
id: F-2026-05-31-003
discovered_at: 2026-05-31T00:00:00Z
run_id: 26706515829
target_repo: ievo-ai/skills
title: Lightweight pre-classifier step in /ievo:security-check to triage candidates before deep security-auditor dispatch
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/164
effort: medium
scope: multi-file
evidence:
  - https://www.cursor.com/changelog: Cursor v3.6 (2026-05-29) — Auto-review Run Mode uses a lightweight classifier subagent to categorize tool calls as allowlisted/sandboxed/escalated before executing, reducing unnecessary approval prompts by ~60-80%
  - https://github.com/anthropics/claude-code/releases: v2.1.154 (2026-05-28) — Dynamic Workflows + parallel subagents infrastructure mature; classifier-then-scan pattern enabled at scale
```

The current `/ievo:security-check` flow dispatches a full security-auditor sub-agent (Sonnet, deep multi-file analysis) for every candidate in parallel. For small install runs this is fine. But as iEvo scales to org-wide security sweeps (enabled by Dynamic Workflows), the cost of running a full deep scan on 50+ repos is prohibitive. Cursor v3.6's Auto-review Run Mode demonstrates the pattern: a lightweight classifier subagent runs first (single-turn, fast, cheap) to categorize candidates as obviously-safe / needs-deep-scan / obviously-red. Only the needs-deep-scan candidates get the full security-auditor treatment. Proposal: add a pre-classifier step to `security-check/SKILL.md` (and/or `init/SKILL.md`'s security phase) that reads the candidate's SKILL.md description, source URL, author metadata, and `scan_repo.mjs` structural output to produce an initial triage verdict before expensive deep scanning.

---

## F-2026-06-01-001 — Document Codex rust-v0.135.0 thread-idle lifecycle hook in hooks-setup/SKILL.md

```yaml
id: F-2026-06-01-001
discovered_at: 2026-06-01T08:08:22Z
run_id: 26742668563
target_repo: ievo-ai/skills
title: Add Codex rust-v0.135.0 thread-idle lifecycle hook documentation to hooks-setup/SKILL.md
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/165
effort: low
scope: single-file
evidence:
  - https://github.com/openai/codex/releases: rust-v0.135.0 (2026-05-28) added a "thread idle lifecycle hook" — fires when an agent thread goes idle; new hook type distinct from SubagentStart/SubagentStop/TurnStartedEvent which shipped in v0.134.0
```

The `hooks-setup/SKILL.md` Codex hook section currently covers hook types up to what was available before v0.134.0. Issue #155 (open) proposes adding the v0.134.0 types (SubagentStart, SubagentStop, TurnStartedEvent). The v0.135.0 **thread idle** hook is a distinct new type not covered by either the current SKILL.md or the pending #155. This hook fires when an agent thread has no pending work — enabling use cases like "notify me when the background security scan finishes sitting idle for 30s" or "checkpoint progress when idle". In iEvo's parallel security-auditor + repo-indexer dispatch context, a thread-idle hook could trigger a completion notification more reliably than a simple timeout. The hook body receives thread context (thread ID, idle duration). Implementation: single addition to the Codex hook table in `hooks-setup/SKILL.md`, no scripts required. Effort: low (~15 min).

---

## F-2026-06-01-002 — update.md step 6 should reference /reload-skills (Claude Code v2.1.152)

```yaml
id: F-2026-06-01-002
discovered_at: 2026-06-01T08:08:22Z
run_id: 26742668563
target_repo: ievo-ai/skills
title: Update /ievo:update command to use /reload-skills (v2.1.152) instead of /reload-plugins for refreshed skill directories
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/166
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.152 (2026-05-27) added /reload-skills command — re-scans skill directories without restarting the session; specifically designed for picking up freshly installed or updated skills
```

The `commands/update.md` Step 6 reminder currently says: `"Run /reload-plugins to pick up refreshed agent/skill definitions."` Claude Code v2.1.152 (2026-05-27) shipped `/reload-skills` — a command that explicitly re-scans skill directories without requiring a session restart. Since `/ievo:update` refreshes vendored skills to `.claude/skills/<name>/`, the correct post-update prompt is `/reload-skills` (for the skill content) rather than `/reload-plugins` (which targets plugin manifests). If `/reload-plugins` is not a real CLI command, users following the step 6 reminder would see a command-not-found error. Even if both commands exist, `/reload-skills` is the targeted command for the update.md use case. Fix: replace the step 6 reminder text to reference `/reload-skills` for skill refreshes, with a note on the minimum required version (v2.1.152+).

---

## F-2026-06-01-003 — Document agent: settings.json field as security-auditor bypass vector (v2.1.157)

```yaml
id: F-2026-06-01-003
discovered_at: 2026-06-01T08:08:22Z
run_id: 26742668563
target_repo: ievo-ai/skills
title: Document agent: settings.json field (v2.1.157) as additional security-auditor model bypass vector alongside CLAUDE_CODE_SUBAGENT_MODEL
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/167
effort: low
scope: multi-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.157 (2026-05-29) — agent: field in settings.json honored for dispatched sessions; --agent <name> CLI flag to override per-session
  - https://code.claude.com/docs/en/sub-agents.md: model resolution order confirmed — (1) CLAUDE_CODE_SUBAGENT_MODEL env var, (2) per-invocation parameter, (3) agent frontmatter model:, (4) main-conversation model; agent: in settings.json adds a new override path at or above level (3)
```

`AGENTS.md` security model section already documents `CLAUDE_CODE_SUBAGENT_MODEL` as an operator gotcha: if the env var is set to a Haiku-tier value, `security-auditor` runs at Haiku reasoning despite `model: sonnet` in its frontmatter, silently degrading the security guarantee. Claude Code v2.1.157 introduced a parallel bypass path: the `agent:` field in `settings.json`. If an operator has set `agent: some-other-agent` (or any agent profile that maps to a Haiku-class model), all Task-tool-dispatched sub-agents inherit that agent profile, overriding `security-auditor.md` frontmatter. Users who follow documentation to configure session-level agents for other purposes could unknowingly degrade iEvo's security scan quality. The fix is documentation-only: add a bullet to the `AGENTS.md` "Security model" section alongside the existing `CLAUDE_CODE_SUBAGENT_MODEL` note, and optionally add a pre-flight check in `security-check/SKILL.md` that warns the user if `agent:` is set in `.claude/settings.json` before dispatching parallel security-auditor sub-agents.

---

## F-2026-06-02-001 — Add Codex rust-v0.136.0 hook output schema tightening note to hooks-setup/SKILL.md

```yaml
id: F-2026-06-02-001
discovered_at: 2026-06-02T08:04:18Z
run_id: 26806183547
target_repo: ievo-ai/skills
title: Document Codex rust-v0.136.0 hook output event schema tightening in hooks-setup/SKILL.md compatibility note
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/168
effort: low
scope: single-file
evidence:
  - https://github.com/openai/codex/releases: rust-v0.136.0 (2026-06-01) "Tighten hook output event schemas (#24962)" — breaking change for any hook output parser that relied on prior schema lenience
```

Codex rust-v0.136.0 (2026-06-01) tightened hook output event schemas via PR #24962. This is a documented breaking change: any code or tooling that parses raw Codex hook output events and relied on the prior (more lenient) schema may break after upgrading to v0.136. The `hooks-setup/SKILL.md` teaches users how to write Claude Code and Codex lifecycle hooks, including the expected output format. The compatibility field currently says "Codex hook schema may differ" — a hedge, but not actionable. A concrete note documenting the v0.136 breaking change gives users a specific version boundary to test against and an action: verify custom Codex hook output parsers against rust-v0.136.0.

Concrete proposal: Update `hooks-setup/SKILL.md` compatibility field and/or add a versioned compatibility note in the skill body. The update should: (a) replace the vague "Codex hook schema may differ" with a specific note mentioning v0.136.0; (b) link to the Codex release notes; (c) describe the actionable mitigation (test hooks against v0.136.0, focus on the hook output event structure your hooks return). No new script or coverage obligation — this is a SKILL.md body/frontmatter documentation change only.

---

## F-2026-06-02-002 — Document Claude Code v2.1.160 `acceptEdits` prompt for `.pre-commit-config.yaml` in AGENTS.md

```yaml
id: F-2026-06-02-002
discovered_at: 2026-06-02T08:04:18Z
run_id: 26806183547
target_repo: ievo-ai/skills
title: Add Claude Code v2.1.160 acceptEdits permission-prompt note to AGENTS.md pre-commit contributor guide
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/169
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.160 (2026-06-02) — acceptEdits mode now prompts before writing build-tool config files including .pre-commit-config.yaml, .npmrc, .yarnrc*, bunfig.toml, .bazelrc, .devcontainer/
```

Claude Code v2.1.160 (2026-06-02) extended the `acceptEdits` permission-prompt surface to include build-tool config files: `.pre-commit-config.yaml`, `.npmrc`, `.yarnrc*`, `bunfig.toml`, `.bazelrc`, and `.devcontainer/`. When an agent running in `acceptEdits` mode (the default for human-interactive sessions) tries to write to `.pre-commit-config.yaml`, Claude Code will now prompt the user for approval before proceeding.

The `AGENTS.md` § "Pre-commit hooks + workflow gate" section currently instructs contributors: "Adding a new validator: drop a `.mjs` in `.github/scripts/validators/` + a hook entry in `.pre-commit-config.yaml`." Contributors who follow this guidance using Claude Code v2.1.160+ as their coding agent will encounter an unexpected `acceptEdits` prompt when the agent writes to `.pre-commit-config.yaml`. Without forewarning, the contributor may deny the prompt (thinking it's an error) and end up with an incomplete validator addition.

Concrete proposal: Add one sentence to the AGENTS.md pre-commit section, immediately after "Adding a new validator" instructions: "Note: Claude Code v2.1.160+ requires explicit `acceptEdits` approval before writing to `.pre-commit-config.yaml` — this prompt is expected behavior; approve it to complete the validator addition." The note prevents confusion and avoids a false-deny scenario that leaves the validator partially installed.

Files affected: `AGENTS.md` (§ Pre-commit hooks + workflow gate, ~line 232). Single sentence addition. No version bump required (AGENTS.md § compliance-ledger bumps happen alongside functional changes, not documentation notes, per the repo's convention).

---

## F-2026-06-02-003 — Document Codex rust-v0.135.0 named permission profiles for iEvo security scan in security-check/SKILL.md

```yaml
id: F-2026-06-02-003
discovered_at: 2026-06-02T08:04:18Z
run_id: 26806183547
target_repo: ievo-ai/skills
title: Add Codex v0.135.0 named permission profile guidance to security-check/SKILL.md as Codex equivalent of disallowed-tools
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/170
effort: low
scope: single-file
evidence:
  - https://github.com/openai/codex/releases: rust-v0.135.0 (2026-05-28) "Named permission profiles in /permissions (#21559)" — Codex now supports named profiles with custom permission sets, analogous to Claude Code's disallowed-tools frontmatter
  - https://github.com/ievo-ai/skills/blob/main/plugins/ievo/skills/security-check/SKILL.md: disallowed-tools frontmatter (Write, Edit, Bash(rm*), etc.) enforces read-only mode during security assessment on Claude Code; Codex has no disallowed-tools frontmatter equivalent, leaving Codex users without a parallel safety constraint
```

Claude Code v2.1.152 introduced `disallowed-tools` frontmatter and iEvo implemented it in `security-check/SKILL.md` (shipped in v0.12.0) — the security-check skill now blocks Write, Edit, Bash(rm*), Bash(mv*), Bash(cp*), Bash(curl*), Bash(wget*) on Claude Code. This enforces read-only mode during third-party skill assessment.

Codex v0.135.0 introduced named permission profiles via `/permissions` command (#21559) — a user can create a named profile (e.g., `ievo-security-scan`) that restricts the tool set available during a Codex session. While not frontmatter-level enforcement (the agent cannot self-impose the profile at skill activation time), a named profile is the closest Codex equivalent. A Codex user running `/ievo:security-check` can pre-activate their `ievo-security-scan` profile before the skill starts to achieve the same read-only enforcement.

Concrete proposal: Add a Codex-specific section or compatibility callout to `security-check/SKILL.md` (currently 288 lines, well under the 500-line limit). The addition describes: (a) the parity gap (Claude Code gets `disallowed-tools` enforcement automatically; Codex users must set up a named permission profile manually); (b) how to create the profile in Codex via `/permissions`; (c) recommended tool restrictions (Read, Grep, Glob, WebFetch only — matches the security-auditor agent's `tools:` allowlist); (d) the instruction to activate it with `/permissions use ievo-security-scan` before running the skill. No scripts needed, no coverage obligation — pure SKILL.md documentation addition.

---

## F-2026-06-27-001 — Document CC v2.1.195 hook matcher exact-match behavior for hyphenated MCP server names in hooks-setup/SKILL.md

```yaml
id: F-2026-06-27-001
discovered_at: 2026-06-27T07:21:43Z
run_id: 28282216625
target_repo: ievo-ai/skills
title: Document CC v2.1.195 hook matcher exact-match breaking change for hyphenated MCP server names in hooks-setup/SKILL.md
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/242
effort: low
scope: single-file
evidence:
  - https://github.com/anthropics/claude-code/releases: v2.1.195 (2026-06-26) — hook matchers with hyphenated identifiers now exact-match instead of substring-match; users must use regex patterns like `mcp__brave-search__.*` to match all tools from a hyphenated MCP server
```

Claude Code v2.1.195 (2026-06-26) changed how PostToolUse hook matchers handle tool names that contain hyphens. Previously, a matcher string like `mcp__brave-search` would substring-match any tool whose name contained that string — including `mcp__brave-search__web_search`. After v2.1.195, the same matcher matches ONLY the exact string `mcp__brave-search` with no substring fallback.

The `hooks-setup/SKILL.md` is the authoritative iEvo guide for configuring lifecycle hooks. It teaches users how to write PostToolUse matchers, including examples involving MCP server tool names. If any example uses a bare MCP server prefix (e.g. `mcp__brave-search`) where the intent is to catch all tools from that server, it is now broken for users on v2.1.195+. More critically, users who have set up hooks following prior `hooks-setup` guidance and upgrade Claude Code to v2.1.195 will see their hooks silently stop firing — the hook is still registered but its matcher no longer matches the tool call events.

The fix is a targeted documentation update in `hooks-setup/SKILL.md`:

1. Add a **compatibility note** identifying v2.1.195 as the version where exact-match semantics took effect.
2. Update any PostToolUse matcher examples that use bare hyphenated MCP server names to use regex patterns instead: `mcp__brave-search__.*` (regex, catches all tools from `brave-search` MCP server).
3. Add a migration note for users upgrading to v2.1.195: "if your PostToolUse hook stopped firing after upgrading to v2.1.195, check whether your matcher uses a hyphenated identifier — prefix it with `mcp__<server>__` regex or wrap in `.*` anchors."
4. Note that non-hyphenated names and exact tool names are unaffected.

No scripts needed, no coverage obligation. Single SKILL.md documentation change. The `hooks-setup/SKILL.md` compatibility field may also need updating to `Claude Code ≥ v2.1.152 (PostToolUse hook); note: v2.1.195 changed hyphenated matcher semantics — use regex for MCP server prefixes`.

---

## F-2026-06-27-002 — Add MVP boundary scope-limiter to deep-review/SKILL.md based on coding-agents.md patterns

```yaml
id: F-2026-06-27-002
discovered_at: 2026-06-27T07:21:43Z
run_id: 28282216625
target_repo: ievo-ai/skills
title: Add explicit MVP boundary (out-of-scope list) to deep-review/SKILL.md based on DenisSergeevitch/agents-best-practices coding-agents.md patterns
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/243
effort: low
scope: single-file
evidence:
  - https://github.com/DenisSergeevitch/agents-best-practices/blob/main/references/coding-agents.md: new 436-line file (2026-06-07) — "MVP boundary definition: draft + verify + explain, not merge + deploy + own production"; explicit out-of-scope items prevent reviewer scope creep; evidence collection requirement before recommendations
  - https://github.com/ievo-ai/skills/blob/main/plugins/ievo/skills/deep-review/SKILL.md: current skill body defines a 10-point checklist of what to look for but has no explicit "out of scope" section; the deep-reviewer agent could drift into suggesting deployment decisions or merge timing
```

`DenisSergeevitch/agents-best-practices` added `references/coding-agents.md` (436 lines, June 7, 2026) with a pattern called "MVP boundary" — the explicit boundary of what a coding agent should and should not do. The core principle: agents should **draft + verify + explain**, NOT **merge + deploy + own production**. The reference file provides a template structure for each agent type that includes both in-scope tasks AND an explicit out-of-scope list.

The `/ievo:deep-review` skill's current `SKILL.md` body (via `deep-reviewer.md` sub-agent) defines the 10-point checklist of what to look for (completeness, test/impl drift, dead code, etc.) but has **no explicit out-of-scope section**. This creates a gap: the skill's intent is to provide gap-detection analysis for pre-commit review, but nothing prevents the deep-reviewer from:
- Suggesting merge strategies or merge timing
- Recommending deployment decisions ("this should go to production after...")
- Suggesting major architecture refactors beyond the diff scope
- Making calls about sprint/backlog priority

These are all out-of-scope for a pre-commit code reviewer but could surface as hallucinated advice in edge cases.

Proposed addition to `deep-review/SKILL.md` body (under the existing "Input" section, ~15 lines):

```markdown
## Scope boundary (MVP boundary)

**In scope:** draft findings, cite evidence, explain impact. One-sentence actionable per finding.

**Out of scope — never return:**
- Merge or deployment timing recommendations
- Architecture refactors beyond the diff under review
- Sprint/backlog priority suggestions
- Lint or type errors (tooling already caught those)
- "Looks good to me" with no findings — always return structured verdict
```

This is a pure SKILL.md body addition (~15 lines). No new agent file, no scripts, no coverage obligation. The addition aligns deep-review with the coding-agents.md MVP boundary pattern while keeping the skill body under the 500-line recommendation.

---

## F-2026-06-27-003 — Document Codex v0.142.0 /import-from-Claude-Code as iEvo onboarding path for platform migrants

```yaml
id: F-2026-06-27-003
discovered_at: 2026-06-27T07:21:43Z
run_id: 28282216625
target_repo: ievo-ai/skills
title: Document Codex v0.140.0 /import (import from Claude Code) as iEvo onboarding path for users migrating from Claude Code to Codex
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/244
effort: low
scope: multi-file
evidence:
  - https://github.com/openai/codex/releases: rust-v0.140.0 (2026-06-15) — `/import` command for selectively importing setup, project configuration, and recent chats from Claude Code (#27070, #27071, #27703); enables zero-reconfiguration migration between platforms
  - https://github.com/ievo-ai/skills/blob/main/README.md: current README documents "Install from marketplace (Claude Code)" and "Install from marketplace (Codex)" but has no cross-platform migration guidance for users who have iEvo on Claude Code and are switching to Codex
```

Codex rust-v0.140.0 (2026-06-15) shipped `/import` — a command for selectively importing setup, project configuration, and recent chats from Claude Code. This enables users to migrate their Claude Code environment to Codex, including plugin and skill configuration.

iEvo is a universal plugin that users may install on Claude Code first and later want to run on Codex as well. Currently the README provides separate install instructions for each platform but no guidance for the cross-platform migration scenario. A user who has:
1. Installed iEvo on Claude Code
2. Captured evolution overlays in `.ievo/evolution/`
3. Indexed repos via `/ievo:index-repos`
...and now wants to continue this work in Codex has no documented migration path.

The `/import` command in Codex v0.140.0 handles the Claude Code config side. On the iEvo side:
- The `.ievo/` directory (overlays, evolution state) is already platform-agnostic (plain markdown files)
- The plugin itself already ships a `.codex-plugin/marketplace.json`
- `/ievo:init` on Codex would re-run the full setup (including security audit + repo indexing) which is redundant if Claude Code state already exists

Proposed documentation additions (multi-file but small):
1. **README.md** — add a "Migration: Claude Code → Codex" section (3-4 lines) explaining that `/import` handles the config side and `.ievo/` overlays transfer automatically (same filesystem)
2. **`plugins/ievo/skills/init/SKILL.md`** — add a Phase 0 check: "If migrating from Claude Code, run `codex /import` first to import Claude Code project configuration before running `/ievo:init`. Skip the full init if `.ievo/evolution/` already has existing overlays from prior Claude Code sessions."

No scripts, no coverage obligation. Pure documentation changes in SKILL.md body and README.

---

## F-2026-06-29-001 — Add `disallowedTools:` to `deep-reviewer.md` agent for read-only enforcement

```yaml
id: F-2026-06-29-001
discovered_at: 2026-06-29T14:15:20Z
run_id: 28377959834
target_repo: ievo-ai/skills
title: Add disallowedTools: to deep-reviewer.md agent for defense-in-depth consistency with security-auditor pattern
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/266
effort: low
scope: single-file
evidence:
  - /tmp/skills/plugins/ievo/agents/security-auditor.md: already declares disallowedTools: covering Edit, destructive Bash, and WebSearch — established pattern in this repo
  - /tmp/skills/plugins/ievo/agents/deep-reviewer.md: only tools: [Read, Grep], no disallowedTools: — gap vs security-auditor pattern
  - ievo-ai/skills AGENTS.md § Security model: "sub-agent tool isolation — A skill's disallowed-tools (kebab-case) does NOT propagate to a Task-tool-dispatched sub-agent" — explicitly names this gap class
```

`deep-reviewer.md` is a read-only gap-detection agent dispatched by `/ievo:deep-review`. It only declares `tools: [Read, Grep]` but has NO `disallowedTools:` field. AGENTS.md § Security model explicitly states that a skill's `disallowed-tools` does NOT propagate to Task-dispatched sub-agents — so the `disallowed-tools` in `deep-review/SKILL.md` does not protect the dispatched agent's execution context. `security-auditor.md` self-enforces via its own `disallowedTools:` (blocking Edit, destructive Bash, WebSearch) for this exact reason. `deep-reviewer` lacks this defense layer.

Adding `disallowedTools: [Edit, Write, Bash(rm*), Bash(mv*), Bash(cp*), Bash(chmod*), Bash(sudo*), WebSearch]` to `deep-reviewer.md` closes the gap. `WebSearch` denial is especially important: a diff under review could carry adversarial prompt injection that uses WebSearch as an exfiltration channel (same rationale as security-auditor). This is a pure frontmatter addition (~8 lines), no body changes, no script changes, no test obligation. Version bump required per AGENTS.md rules.

---

## F-2026-06-29-002 — Add activation eval fixtures for iEvo SKILL.md files

```yaml
id: F-2026-06-29-002
discovered_at: 2026-06-29T14:15:20Z
run_id: 28377959834
target_repo: ievo-ai/skills
title: Add activation eval fixtures (positive/negative prompt examples) for all 14 iEvo SKILL.md files
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/267
effort: high
scope: architecture-change
evidence:
  - https://github.com/DenisSergeevitch/agents-best-practices/blob/main/references/checklists.md: "Activation evals + output quality evals must exist" — skill quality checklist requirement; iEvo has no activation eval fixtures
  - https://agentskills.io/specification: "Skills are activated by description match (semantic)" — descriptions are the routing mechanism, making them load-bearing and untestable without evals
```

iEvo's 14 SKILL.md files have no activation eval fixtures. The agents-best-practices `checklists.md` requires "Activation evals + output quality evals must exist." Since iEvo skills activate via description match (agentskills.io spec), ambiguous descriptions cause mis-routing with no way to catch this before shipping. Concrete risk: `security-check` vs `vuln-scan` share "security scan" language; `hooks-setup` vs `init` both configure iEvo; `inspect` vs `overlay-status` both answer "what does this X have".

Proposal (Phase 1): add `plugins/ievo/skills/<name>/evals/activation.yaml` per skill with ≥3 positive prompts (SHOULD activate this skill) and ≥2 negative prompts (should NOT, with `routes_to:` field). No eval runner in Phase 1 — fixtures serve as regression documentation and seed data for a future Phase 2 runner. Phase 2 (separate proposal): `eval_activations.mjs` script with 100% test coverage gate.

Priority order for ambiguity-critical pairs first: security-check vs vuln-scan → hooks-setup vs init → inspect vs overlay-status → remaining 11 skills.

---

## F-2026-06-30-001 — Add `when_to_use` frontmatter to all 14 iEvo SKILL.md files for precise automatic-invocation routing

```yaml
id: F-2026-06-30-001
discovered_at: 2026-06-30T00:00:00Z
run_id: 28415000000
target_repo: ievo-ai/skills
title: Add when_to_use frontmatter to all 14 iEvo SKILL.md files for precise automatic-invocation routing
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/268
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/skills.md: when_to_use is a documented SKILL.md frontmatter field separate from description — provides additional trigger context; description + when_to_use combined cap is 1,536 chars; enables separation of "what it does" vs "when to automatically invoke it"
```

Claude Code's skills documentation (fetched 2026-06-30) documents `when_to_use` as a first-class SKILL.md frontmatter field, distinct from `description`. The `description` field explains what the skill does; `when_to_use` provides additional context for Claude's automatic invocation decisions (trigger phrases, example user requests, and negative examples of when NOT to invoke). The combined character cap for routing is 1,536 chars across both fields.

None of iEvo's 14 SKILL.md files currently declare `when_to_use`. Instead, descriptions try to serve both purposes simultaneously — cramming "what it does + when to use it + trigger examples" into a single field. The result is that some skill descriptions are long enough that the routing signal is diluted. A proper `when_to_use` field would:

1. Allow `description` to focus on a concise capability statement
2. Allow `when_to_use` to enumerate trigger phrases without crowding the description
3. Provide negative examples ("do NOT use when already installed — use /ievo:update instead") to reduce false-positive auto-activation

This is especially important for skill pairs with overlapping subject matter:
- `security-check` vs `vuln-scan` — both involve security analysis
- `hooks-setup` vs `init` — both configure iEvo
- `inspect` vs `overlay-status` — both answer "what does X have"
- `deep-review` vs `feedback` — both involve reviewing something

Proposed `when_to_use` values:
| Skill | Proposed when_to_use (key triggers) |
|-------|--------------------------------------|
| `init` | "when setting up iEvo for the first time in a project; do NOT use if .ievo/ already exists — use /ievo:update or /ievo:overlay-status instead" |
| `security-check` | "when auditing a remote skill or plugin before install; do NOT use for source code vulns — use /ievo:vuln-scan for that" |
| `vuln-scan` | "when scanning project source code for CWE vulnerabilities; do NOT use for plugin/skill install auditing — use /ievo:security-check for that" |
| `deep-review` | "when reviewing a diff or staged changes for gaps that linters miss; do NOT use for security issues — use /ievo:security-check" |
| `evolution` | "when capturing a lesson or pattern learned in this session; when user says 'save this', 'remember that', 'capture this pattern'" |
| `overlay-status` | "when asked what evolutions or overlays are active; when asked 'what rules are applied'" |
| `index-repos` | "when asked to index or catalog GitHub repositories for the iEvo ecosystem" |
| `inspect` | "when asked to preview or summarize a remote skill/repo before installing" |
| `hooks-setup` | "when asked to set up lifecycle hooks; NOT for configuring Claude Code settings broadly — just hook configuration" |
| `schedule` | "when asked to create a recurring or scheduled iEvo operation" |
| `handoff` | "when switching sessions, machines, or contexts and needing to resume work" |
| `feedback` | "when asked to file an issue or bug report about iEvo itself" |
| `debug-on` | "when enabling verbose logging or debug mode for iEvo" |
| `debug-off` | "when disabling verbose logging or debug mode for iEvo" |

Implementation: add 1–3 line `when_to_use:` frontmatter to each of the 14 SKILL.md files. No body changes, no scripts, no coverage obligation. Single version bump per AGENTS.md rules.

---

## F-2026-06-30-002 — Add `paths` glob frontmatter to context-sensitive iEvo SKILL.md files for automatic-activation scoping

```yaml
id: F-2026-06-30-002
discovered_at: 2026-06-30T00:00:00Z
run_id: 28415000000
target_repo: ievo-ai/skills
title: Add paths glob frontmatter to context-sensitive iEvo SKILL.md files to limit automatic activation to relevant file contexts
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/269
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/skills.md: paths is a documented SKILL.md frontmatter field (added after May 2026) — accepts glob patterns (comma-separated string or YAML list); limits when a skill is activated automatically to sessions where the current file matches the glob; unknown frontmatter is ignored gracefully on platforms that don't support it
```

Claude Code's skills documentation (fetched 2026-06-30) documents `paths` as a SKILL.md frontmatter field that restricts a skill's automatic-invocation to contexts where the active file matches specified glob patterns. The field was added after May 2026 (per the docs page annotation). On platforms that don't support it, unknown frontmatter is ignored gracefully.

None of iEvo's 14 SKILL.md files currently declare `paths`. For most iEvo skills this is fine — they are user-invoked (not auto-invoked). But a subset of skills are meaningfully context-sensitive:

1. **`security-check`** — most useful when the active file is a `SKILL.md` or `agents/*.md` or `plugin.json` (the user is looking at a plugin they're about to install). Proposed paths: `**/SKILL.md,**/plugin.json,**/.claude-plugin/**`
2. **`deep-review`** — most useful when the active file is any source file (diff review context). Proposed paths: could be left broad (`**`) but a negative path restriction could exclude `.ievo/evolution/**` (overlays aren't reviewed via deep-review)
3. **`overlay-status`** — most useful when the active file is under `.ievo/evolution/**` (user is looking at overlay files). Proposed paths: `.ievo/evolution/**`
4. **`evolution`** — natural to activate in `.ievo/**` context but should NOT be restricted (useful in any file context)

The most concrete win is `security-check` — limiting its auto-activation to when the user has a plugin file open prevents it from auto-triggering during normal source code editing sessions.

Implementation: add `paths:` frontmatter to 2-4 SKILL.md files (security-check, overlay-status, deep-review). Single version bump per AGENTS.md rules. No body changes, no scripts. The AGENTS.md § Skills format section should also document `paths:` as a supported optional frontmatter field (currently not mentioned).

Files affected:
| File | Change |
|------|--------|
| `plugins/ievo/skills/security-check/SKILL.md` | add `paths: "**/SKILL.md,**/plugin.json,**/.claude-plugin/**,**/.codex-plugin/**"` |
| `plugins/ievo/skills/overlay-status/SKILL.md` | add `paths: ".ievo/evolution/**,.ievo/**"` |
| `plugins/ievo/skills/deep-review/SKILL.md` | add `paths: "**"` (explicit universal — documents intent) |
| `AGENTS.md` | add `paths:` to the Skills format section's frontmatter field list |

---

## F-2026-06-30-003 — Add `disable-model-invocation: true` to heavyweight iEvo skills to prevent unintended auto-activation

```yaml
id: F-2026-06-30-003
discovered_at: 2026-06-30T00:00:00Z
run_id: 28415000000
target_repo: ievo-ai/skills
title: Add disable-model-invocation: true to heavyweight iEvo skills (init, security-check, vuln-scan, deep-review) to prevent costly unintended auto-activation
status: issued
issue_url: https://github.com/ievo-ai/skills/issues/270
effort: low
scope: multi-file
evidence:
  - https://code.claude.com/docs/en/skills.md: disable-model-invocation is a documented SKILL.md frontmatter field — "Set to true to prevent Claude from automatically loading skill. Only user can invoke. As of v2.1.196, also prevents scheduled tasks from running the skill."
```

Claude Code's skills documentation documents `disable-model-invocation` as a SKILL.md frontmatter field that prevents the model from automatically loading the skill based on description match. The field was confirmed in the docs (fetched 2026-06-30), with a v2.1.196 note that it also prevents scheduled tasks from running the skill. Only explicit user invocation (e.g., typing `/ievo:security-check`) triggers the skill.

None of iEvo's 14 SKILL.md files currently declare `disable-model-invocation`. For iEvo's lightweight, informational skills (`overlay-status`, `inspect`, `handoff`, etc.), auto-activation by description match may be acceptable. But for the 4 heavyweight skills, unintended auto-activation is a significant problem:

**`/ievo:init`** — 6-stage orchestrator (security audit + repo indexing + evolution install + hooks config + testing). If this auto-activates because a user said "let's initialize our project", it runs a full install pipeline they didn't intend.

**`/ievo:security-check`** — dispatches parallel security-auditor sub-agents, runs `scan_repo.mjs` on candidate repos, fetches external URLs. If this auto-activates because a user said "let's check security", it could run multiple API calls and burn significant tokens.

**`/ievo:vuln-scan`** — 4-phase exploit-chain vulnerability scanner (threat model → parallel dispatch → exploit validation → report). If this auto-activates because a user said "scan for vulnerabilities", it runs a deep multi-agent analysis.

**`/ievo:deep-review`** — dispatches `deep-reviewer` sub-agent with full fresh context. If this auto-activates because a user says "review this code", it spends tokens on a structured 11-point gap-detection analysis the user didn't request.

Adding `disable-model-invocation: true` to these 4 skills ensures:
1. They only run when the user explicitly invokes them (`/ievo:security-check`, etc.)
2. They don't accidentally trigger in scheduled Routines that weren't designed for them (v2.1.196 behavior)
3. Token spend stays predictable — heavyweight scans only when requested

The 10 remaining skills (init excluded above) may or may not benefit from auto-invocation; that's a separate decision. This proposal focuses on the 4 highest-cost skills.

**Files affected:**
| File | Change |
|------|--------|
| `plugins/ievo/skills/init/SKILL.md` | add `disable-model-invocation: true` |
| `plugins/ievo/skills/security-check/SKILL.md` | add `disable-model-invocation: true` |
| `plugins/ievo/skills/vuln-scan/SKILL.md` | add `disable-model-invocation: true` |
| `plugins/ievo/skills/deep-review/SKILL.md` | add `disable-model-invocation: true` |

Single version bump per AGENTS.md rules. No body changes, no scripts, no coverage obligation. Purely additive frontmatter changes.
