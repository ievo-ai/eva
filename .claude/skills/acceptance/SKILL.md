---
name: acceptance
description: >-
  Self-review before marking a requirement as done. Verifies all test types
  are present, real outcomes are checked, and edge cases are covered.
  Eva MUST invoke this before declaring any task complete.
argument-hint: "[requirement or task to verify]"
---

# Acceptance

Verify that a requirement is truly complete before marking it done. This is not optional — every completed requirement passes through this checklist.

## When to invoke

Eva invokes `/acceptance` BEFORE saying "done", "ready", "complete", or marking a task as finished. This is a mandatory self-review gate.

Triggers:
- About to mark a task/requirement as completed
- About to tell Denis "all tests pass, feature is done"
- About to commit with a message like "feat:", "fix:", "add:"
- Denis asks "is it done?" — run /acceptance first, then answer

## Checklist

### 1. Identify the requirement

State what was requested. Be specific — not "moved config" but "move project manifest from `ievo.yaml` to `.ievo/manifest.yaml`, make `.ievo/` the project marker."

### 2. List all changed files

```bash
git diff --name-only HEAD  # or git diff --staged --name-only
```

Categorize: source code, tests, docs, config.

### 3. Verify test completeness

For EACH changed source file, check:

| Test type | What to verify | How |
|-----------|---------------|-----|
| **Unit tests** | Every public function has a test. Error paths covered. Boundary values tested | Read test file, match functions to test functions |
| **Edge cases** | Empty input, missing files, permission errors, malformed data, None values | Search for edge case tests |
| **Integration tests** | Real files created/modified via `tmp_path`. Real state changes verified. NOT just `mock.assert_called_once()` | Search for `tmp_path` usage, verify assertions check actual outcomes |
| **UI/TUI tests** | If UI changed: Textual `app.run_test()` + Pilot API. Real widget interaction, not just mock widgets | Search for `run_test`, `pilot` |

### 4. Verify real outcomes

For each integration test, check that it asserts **actual outcomes**, not just function calls:

**Bad** (mock-only):
```python
mock_init.assert_called_once_with(name=".")  # proves wiring, not behavior
```

**Good** (real outcome):
```python
assert (tmp_path / ".ievo" / "manifest.yaml").is_file()  # proves files created
assert "spec-writer" in manifest["agents"]                # proves state changed
```

### 5. Run tests + coverage

```bash
uv run pytest --cov --cov-report=term-missing
```

Check coverage on changed files specifically — not just total coverage. Each changed source file should be at 100%.

### 6. Check docs

If the change affects user-facing behavior:
- [ ] CLAUDE.md updated?
- [ ] docs/ updated?
- [ ] README.md updated (if applicable)?

### 7. Report

Output format:

```
## Acceptance: [requirement summary]

### Changes
- [list of changed files]

### Test coverage
| File | Unit | Integration | Edge cases | UI | Coverage |
|------|------|-------------|------------|----|----------|
| file.py | Y | Y | Y | N/A | 100% |

### Gaps found
- [list gaps, or "None"]

### Verdict: PASS / FAIL
[If FAIL: list what needs to be added before this is done]
```

## Rules

- A requirement with FAIL verdict MUST NOT be marked as complete
- Gaps must be fixed and /acceptance re-run before marking done
- "Tests pass" is not the same as "tests are complete" — passing incomplete tests is worse than failing complete ones
- Mock-only tests count as gaps unless the mocked boundary is truly external (Docker, network, subprocess)
- If unsure whether a test type applies, it applies — write it

## Anti-patterns

- Saying "449 tests pass, 99% coverage, done!" without checking WHAT those tests verify
- Marking done because pre-commit is green — pre-commit checks style, not correctness
- Writing integration tests that only assert mock calls
- Skipping edge case tests because "the happy path works"
- Not testing the feature from the user's perspective (e.g., does `ievo` actually auto-init?)
