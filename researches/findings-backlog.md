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
