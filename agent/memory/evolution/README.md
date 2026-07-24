# Eva evolution store

Eva's own cross-run learning store. When Eva operates autonomously (the
`eva-implement.yml` builder and the `eva-fix-pr.yml` review-fixer), every failure
signal she hits — a review that requested changes, a mid-build test failure she
had to iterate through, push/CI friction, a budget/handoff exit — is a lesson.
This store is where those lessons live so a *later* run can read them back.

Introduced by [#158](https://github.com/ievo-ai/eva/issues/158) (dogfood the iEvo
plugin inside Eva's agents). It is the answer to that issue's crux design point —
"an overlay nobody reads back is theater". The operator's decision (issue #158,
2026-07-04): the store is **Eva-side, in `ievo-ai/eva`, injected at run start**.
Lessons are Eva's *internal* knowledge — they are NOT committed into target-repo
PRs (noise + wrong ownership).

[#169](https://github.com/ievo-ai/eva/issues/169) closed the write-path gap #158
left open: v1 uploaded per-run captures as build artifacts with consolidation
"deferred" — nobody ever consumed them, so `lessons.md` stayed empty forever and
every run's read path loaded nothing back. The write path below (v2) commits the
lesson every time, with no human maintenance step in the loop.

## Files

| File | Role |
|------|------|
| `lessons.md` | The ledger. Append-only, human-readable. This is what runs READ at start. |
| `README.md` | This file — format + read/write contract. |

## Read path (mandatory)

Every `eva-implement` / `eva-fix-pr` run loads this store at start when the
`EVA_IEVO_PLUGIN_ENABLED` repo variable is `true`:

1. The workflow's "Load Eva evolution store" step fetches `lessons.md` from
   `ievo-ai/eva@main` via `gh api` (works cross-repo — the working tree is the
   *target* repo, so the store is pulled from eva, not the checkout) and writes it
   to a temp file.
2. The path is exposed to the agent as the `EVA_EVOLUTION_STORE` env var.
3. The agent reads it in its context-loading phase and applies relevant lessons
   before building/fixing.

A missing or empty store is fine (no lessons captured yet) and must never fail a
build — the read is best-effort.

## Write path (atomic commit or auto-consolidator — no human step, issue #169)

1. During a run the agent appends captured lessons to the file at
   `EVA_EVOLUTION_CAPTURE` (seeded empty by the store-load step). If the iEvo
   plugin is available it captures via the `/ievo:evolution` skill; otherwise it
   appends a brief dated note directly.
2. After the agent finishes, the workflow ALSO uploads that capture file as a
   build **artifact** (`eva-evolution-capture-*`) — kept as debug belt-and-braces
   only; nothing depends on the artifact being read.
3. **Persistence** happens before the agent's turn ends, by one of two paths
   depending on where the run happened:
   - **eva-repo run** (`eva-implement` / `eva-fix-pr` building/fixing in
     `ievo-ai/eva` itself): the agent appends the captured lesson to `lessons.md`
     directly in the working tree and stages it in the SAME commit as the fix —
     for `eva-implement` that's the PR-opening commit, for `eva-fix-pr` that's
     the `[pr-fix-N]` commit. Merging that ONE PR persists the lesson
     atomically; there is no second PR on this path.
   - **Cross-repo run** (building/fixing any other repo — cli, skills,
     marketplace, sdk, ievo.ai): lessons must not land in the target repo
     (operator's #158 Q1 answer), so the agent instead clones `ievo-ai/eva`,
     dedups against the current `lessons.md`, re-derives each new entry's `NN`
     against that fresh clone (eva#250 — see point 4), and — only if there is
     new content — opens a small append-only PR on an `evolution/consolidate-*`
     branch touching nothing but `agent/memory/evolution/lessons.md`.
     `eva-review-pr.yml`'s sensitive-path gate carries a narrow carve-out for
     exactly that branch-prefix + path-scope combination (mirroring the
     existing `research/audit-*` exception), so it auto-merges without
     operator involvement — the human gate on the REST of `agent/memory/`
     (`ROLE.md`, sessions, anything else shaping Eva's identity) is unchanged.
     If a review still blocks it (a rarer, narrower NN collision that slipped
     past the fresh re-derivation — e.g. two parallel runs racing the same
     window) or the PR goes `DIRTY` (a sibling merged first), `eva-fix-pr.yml`
     and `eva-conflict-scan.yml` respectively self-heal it: both renumber the
     colliding entries against CURRENT `main` and rebuild the branch, never
     touching an entry's body or any other file. A `evolution/consolidate-*`
     PR carries no linked issue, so if that recovery itself fails the PR is
     simply closed and flagged for the operator — a logged, accepted loss of
     that one batch of captured lessons (eva#169), not a build failure.
4. **Dedup + renumber**: an entry is skipped entirely (not appended, no PR
   opened) when a section with the exact same `## L-YYYY-MM-DD-NN — <title>`
   line already exists in `lessons.md`. Otherwise, before appending, each new
   entry's `NN` is re-derived as `max(existing same-date NN already in
   lessons.md) + 1` (eva#250) — the ID is picked against whatever's on disk
   at write time, not whatever was loaded at run start, so two runs that
   started from the same stale snapshot don't collide on the same `NN`. This
   matters because the ID is both the dedup key above AND the `[[L-...]]`
   cross-ref anchor other entries may link to — a collision makes both
   entries ambiguous. An empty capture (the gate passed on the first attempt,
   so there is no lesson) produces no commit and no PR on either path.

## `lessons.md` entry format

Each lesson is a `##`-headed section. Keep it terse and specific — this text is
loaded into every run's context, so it costs tokens:

```markdown
## L-YYYY-MM-DD-NN — <one-line lesson title>
- **Source**: <eva-implement | eva-fix-pr> run for <repo>#<issue-or-PR>
- **Signal**: <what went wrong — review finding / test failure / push friction / handoff>
- **Root cause**: <the wrong assumption, missed convention, or stale knowledge>
- **Apply next time**: <the concrete, checkable rule a future run should follow>
```
