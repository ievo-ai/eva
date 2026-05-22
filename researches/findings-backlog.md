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
