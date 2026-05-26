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
