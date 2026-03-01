# Evolution Log

## 2026-03-01: Re-read YAML files between sequential edits

**Context:** While hardening GitHub Actions workflow files (quoting shell vars, moving `${{ }}` into `env:` blocks), two sequential Edit calls on `eva-scan.yml` without re-reading between them created a duplicate `env:` block — corrupting the YAML structure. Separately, a security hook blocked an edit to `eva-on-issue.yml` but I proceeded without verifying, requiring another edit cycle.

**Action:** Added "Editing rules" section to CLAUDE.md: (1) always re-read YAML workflow files between sequential edits, (2) when a hook blocks an Edit, verify file state before proceeding.

**Goal:** Prevent YAML file corruption from blind sequential edits. Prevent wasted edit cycles when hooks block changes.

## 2026-03-01: Always assignee on issues, no sensitive data in evo logs

**Context:** Created GitHub issue without `--assignee` — Denis had to remind me. Then guessed the wrong username instead of looking it up. Also applied `ievo` label to an issue meant for a human collaborator, not for Eva.

**Action:** Updated CLAUDE.md "Working rules": (1) always `--assignee` on issues, look up usernames first, (2) `ievo` label = Eva's task only, (3) evolution logs must never contain sensitive information. Updated `/evo` skill step 8 with assignee and label guidance.

**Goal:** Ensure issues are properly assigned. Keep evolution logs safe for public visibility. Correct label semantics.

## 2026-03-01: Include .gitattributes from the first commit

**Context:** CRLF warnings appeared on every commit since the project was created. Fixed only in session 006 by adding `.gitattributes` and normalizing 43 files. Should have been there from the start.

**Action:** Added rule to CLAUDE.md "Working rules": always include `.gitattributes` with `* text=auto eol=lf` from the first commit of any new repo.

**Goal:** Prevent CRLF/LF inconsistency from accumulating across the project lifecycle.

## 2026-03-01: Verify before acting — adopt fact-check skill

**Context:** Created children symlinks in `agent/children/` instead of `.claude/children/` — wrong path, Denis corrected. Earlier, rejected meddylib's `fact-check` skill as "medical domain-specific" without evaluating its core principle. The core principle — verify facts before acting — is universal and would have prevented multiple errors in this session (wrong paths, guessed usernames, wrong labels).

**Action:** Created `/verify` skill (adapted from meddylib's fact-check) for path verification, convention checking, GitHub API queries, and pattern evaluation. Added "verify before acting" to CLAUDE.md working rules. Reversed the original rejection of fact-check (D-024 adoption table).

**Goal:** Prevent errors from assumptions. Check conventions, paths, and API state before acting. Evaluate patterns by substance, not domain name.

## 2026-03-01: Enforce test coverage tooling before adding coverage rules

**Context:** Added "100% test coverage" working rule to CLAUDE.md with `uv run pytest --cov`, but `pytest-cov` was not in dependencies. The rule was unenforceable — running the command failed with "unrecognized arguments". Also, CI workflow (`tests.yml`) used bare `pip install` instead of `uv sync` and had no coverage step.

**Action:** Added `pytest-cov>=6.0` to dev dependencies. Added `[tool.coverage.run]` and `[tool.coverage.report]` config to `pyproject.toml` with `fail_under=54` (current baseline, target 100%). Updated CI to use `uv sync --group dev` and `pytest --cov`. Updated CLAUDE.md rule with "never lower fail_under".

**Goal:** Ensure every rule has working tooling behind it. Coverage ratchet prevents regression while allowing incremental improvement toward 100%.
