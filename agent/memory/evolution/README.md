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

## Write path (per-run artifact + periodic consolidation)

Direct commits into every run would be noisy and, for cross-repo builds, land in
the wrong repo. Instead (operator's accepted v1 option, issue #158):

1. During a run the agent appends captured lessons to the file at
   `EVA_EVOLUTION_CAPTURE` (seeded empty by the store-load step). If the iEvo
   plugin is available it captures via the `/ievo:evolution` skill; otherwise it
   appends a brief dated note directly.
2. After the agent finishes, the workflow uploads that capture file as a build
   **artifact** (`eva-evolution-capture-*`).
3. **Consolidation** (periodic, operator/maintenance step — deferred in v1):
   captured lessons are reviewed and the durable, project-wide ones are appended
   to `lessons.md` here via a small PR to `ievo-ai/eva`, so future runs read them
   back. Same "auto-write only unambiguous lessons, park the rest for review"
   contract the plugin's auto-evolution mode uses for interactive sessions.

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
