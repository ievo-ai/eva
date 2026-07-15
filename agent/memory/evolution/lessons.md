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

## L-2026-07-13-01 — A DoS size-guard that short-circuits a read must propagate an explicit "unscanned" state, not collapse into the "absent" return shape
- **Source**: eva-fix-pr run for ievo-ai/skills#376
- **Signal**: Eva's own REQUEST_CHANGES review flagged that the CWE-400 read-guard fix computed an `oversized`/`manifest_oversized` signal but dropped it before `renderIndexMd()` and `main()`'s manifest — so a plugin whose `hooks.json`/`.mcp.json`/`SKILL.md`/`plugin.json` was padded past the 256 KB cap rendered identically to "no hooks" / `has_hooks:false` instead of "unknown — not scanned". A fail-silent integrity regression (CWE-693) in a *security* index: it hides the exact hook/MCP/broad-grant an attacker would plant, and the review judged it worse than the OOM the guard fixes.
- **Root cause**: when adding a defensive short-circuit that skips reading attacker-controlled input, the implementer reused the function's existing empty/error return shape and treated "skipped read" as equivalent to a genuine "absent/none present". The computed skip signal was never threaded into the downstream consumers that map presence→a security-relevant boolean. In a security context, "not scanned" ≠ "not present"; collapsing them erases the signal.
- **Apply next time**: whenever a size/DoS guard short-circuits a read of security-relevant attacker-controlled data, propagate an explicit "unscanned/unknown" state ALL the way to every downstream rendering AND every persisted boolean (add companion `*_unscanned` fields rather than overloading the existing `has_*` boolean), and add a test asserting the unscanned surface renders distinctly from a genuine absent one. Never let a skipped read reuse the "absent" output shape unmarked.

## L-2026-07-15-01 — Cross-repo build's git `origin` remote can point at the wrong repo even though the checked-out file content is correct
- **Source**: eva-implement run for ievo-ai/skills#387 (cross-repo build)
- **Signal**: `git remote -v` showed `origin` = `https://.../ievo-ai/eva.git` even though the working tree's actual file content matched `$TARGET_REPO` (`ievo-ai/skills`) exactly — AGENTS.md, `plugins/ievo/**`, etc. all present and correct. `git push -u origin HEAD` under that stale remote succeeded silently (GitHub allows pushing a new branch with unrelated history), creating a foreign `eva-impl/*` branch in `ievo-ai/eva` containing `ievo-ai/skills`' entire commit history plus the new commit. `gh` CLI (`GH_TOKEN`) was correctly scoped to `$TARGET_REPO` the whole time — `gh api repos/$TARGET_REPO/contents/...` and `gh issue comment` both worked fine — only the git-level `origin` URL was wrong, so a "gh works against the target repo" check does NOT prove the git remote is also correct.
- **Root cause**: not fully diagnosed (harness/runner detail) — the working directory's file content was swapped to the cross-repo target, but `origin`'s URL was left pointing at the repo the runner job is nominally named after (eva).
- **Apply next time**: before the first `git push` in ANY cross-repo build (`$TARGET_REPO != ievo-ai/eva`), explicitly verify `git remote get-url origin` resolves to `$TARGET_REPO` — do not infer this from file-tree content or from `gh` calls succeeding, since `gh`'s auth is independent of the git remote config. If mismatched, `git remote set-url origin "https://x-access-token:${GH_TOKEN}@github.com/$TARGET_REPO.git"` before pushing — `GH_TOKEN` already carries a correctly-scoped token. If a push already landed on the wrong repo, clean it up immediately via `gh api -X DELETE repos/<wrong-repo>/git/refs/heads/<branch>` (the branches-list API can lag a few seconds after the ref delete — re-check with a short retry before assuming the delete failed).
