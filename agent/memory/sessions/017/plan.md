# Session 017 — Issue Pipeline Migration (Phase 1: Eva issue brain)

## Context

Decision D-004 (godfather `knowledge/decisions.md`) + eva#106: centralize org-wide
issue/PR automation in Eva (private), thin forwarders in public repos. The skills
repo built a working v1 (`issue-pipeline.yml`, #261) — router analysis + full-opt-out
implement + auto-merge. This session relocates that brain INTO Eva, reconciling with
Eva's existing automation (eva-on-issue triage, eva-review-pr auto-merge, eva-scan).

Recon (eva#106 comment) found Eva already has: cross-repo dispatch receivers
(`new-issue`/`review-pr`), opus PR review + **auto-merge with sensitive-path gate**,
and the App has `workflows: write`. Merge-gate decision (operator): KEEP auto-merge +
sensitive-path gate (full opt-out). The real gaps: (1) `new-issue` forwarding is dormant
(no senders), (2) eva-on-issue is triage-only (no router-depth analysis, no implement),
(3) no state-machine labels.

## Phases (this session = Phase 1, sub-step 1a)

- **1a (this PR):** Upgrade `eva-on-issue.yml` from shallow triage → deep ROUTER:
  - Rich analysis (Understanding / Approach / Questions / Conflicts / Risks) replacing
    the thin triage comment — matching skills-v1 `issue-router.md` depth.
  - Routing verdict marker in the comment (`<!-- ievo-verdict: implement|hold -->`),
    fail-safe to hold. Full-opt-out gate: low-risk → implement-candidate; else hold.
  - State-machine labels: `triage → needs-discussion → approved`. (Implement consumes
    `approved` in 1b.)
  - `@ievo-eva` comment trigger (re-analysis / discussion) in addition to
    `issues:opened` + `new-issue` dispatch.
  - STILL comment+label only — NO autonomous code-writing/merging yet (that is 1b).
- **1b (this PR):** Implement path — `approved` + low-risk → Eva builds → PR →
  eva-review-pr auto-merges (sensitive-path gated). Rate-limit. Built:
  - `.github/workflows/eva-implement.yml` — triggers `issues:[labeled]`(approved)
    + `repository_dispatch:[implement-issue]`. **Dormant** behind repo var
    `EVA_IMPLEMENT_ENABLED == 'true'` (operator flips after smoke test — this is
    the most autonomous workflow: Eva writes code that auto-merges). Claim swaps
    `approved` → `eva-implementing` (distinct from router's operator-only
    `in-progress`); best-effort rate-limit MAX_INFLIGHT=3. Checkout + PR via
    `EVA_PAT_GITHUB_TOKEN` (real-user identity) so eva-review-pr (App) can approve
    + auto-merge (App can't self-approve its own authored PR).
  - `.github/prompts/eva-implement.md` — build+PR-only handler (adapted from
    skills `issue-handler.md`, **without** the review/fix loop — eva-review-pr
    owns review+merge). **Build-on-branch → open READY PR at the end** (NOT
    draft→ready): eva-review-pr only approves via the App identity on the
    `workflow_run` path (fired by `pull_request: opened`); the
    `ready_for_review` path runs the reviewer as the same PAT user that authored
    the PR → self-approval block → no auto-merge. Opening ready directly fires
    opened → Tests → workflow_run → App APPROVE → auto-merge. Gate run via
    `uv run ruff/pytest/mypy` (pre-commit's system-mypy hook needs venv on PATH;
    `uv run` is reliable). eva scope-lock + ROLE.md safety; comment trust gate
    (marker AND MEMBER/OWNER author); no version bump (eva isn't plugin-versioned).
- **Phase 2:** wire `new-issue` forwarders from public repos (skills last, replacing v1).
- **Phase 3:** remove skills v1.

## Constraints

- PR-only on eva (no direct push to main). eva-review-pr's sensitive-path gate covers
  `.github/workflows/` → this workflow PR will require operator merge (correct for infra).
- Untrusted issue text never reaches `run:` via `${{ }}` — only via `gh issue view`
  inside the agent (existing pattern, preserve it).
- Bot-author gate stays (don't process Eva's / github-actions' own issues).
- Verify any tool/action input before adding (eva rule).

## Decisions to make during build

- Label colors / exact names for the state machine (align with eva's existing label set:
  it already has `needs-discussion`, `accepted`, `rejected` operator-only).
- Whether `@ievo-eva` re-analysis re-runs full router or a lighter pass.
