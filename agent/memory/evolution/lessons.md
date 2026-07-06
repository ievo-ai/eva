# Eva evolution lessons

Append-only ledger of lessons Eva captured from her own autonomous work
(`eva-implement` / `eva-fix-pr`). Read at the start of every run; see
[`README.md`](README.md) for the format and the read/write contract (issue #158).

No lessons captured yet — this store is seeded empty. New entries are appended
below as Eva's runs surface durable, project-wide lessons: an eva-repo run
commits the lesson atomically with its own fix, a cross-repo run opens a small
append-only PR here (dedup'd against existing entries) — see `README.md`.

<!-- Lessons go below this line, newest last. Format: see README.md. -->

## L-2026-07-06-01 — ievo-ai/skills version bump omits evolution_candidates.mjs from AGENTS.md's checklist
- **Source**: eva-implement run for ievo-ai/skills#319
- **Signal**: `node --test plugins/ievo/scripts/tests/*.test.mjs` failed on the first local gate run — `evolution_candidates.test.mjs` asserts `SCRIPT_VERSION` in `plugins/ievo/scripts/evolution_candidates.mjs` equals `plugin.json`'s version, the same coupling pattern `discover.mjs` has.
- **Root cause**: followed AGENTS.md's documented "bump these four files" checklist literally; the checklist predates `evolution_candidates.mjs` (shipped in v0.45.0) and was never updated, even though that script carries an identical version-coupling test to `discover.mjs`.
- **Apply next time**: when bumping the plugin version in `ievo-ai/skills`, `grep -rn "SCRIPT_VERSION" plugins/ievo/scripts/*.mjs` (not just `discover.mjs`) and update every match before running the gate — the repo's documented file checklist is not exhaustive; the coupling tests are the real source of truth.
