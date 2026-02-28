# Safety Rules

Eva is designed with safety as a first-class concern. These rules are enforced at the code level.

## Core Rules

### 1. Never Auto-Merge

Every mutation requires human approval via PR review. The `auto_merge` config defaults to `false`. Even if set to `true`, the actual merge button requires a human click. Eva creates PRs, humans merge them.

### 2. Dry-Run by Default

Eva runs in dry-run mode unless explicitly invoked with `--live`. In dry-run:
- Mutations are logged and displayed in terminal
- No branches are created
- No commits are pushed
- No PRs are opened

This is the default in both GitHub Actions and Docker.

### 3. Rate Limited

Maximum **5 mutations per run** (configurable via `max_mutations_per_run`). This prevents noisy runs from flooding repos with PRs. Patterns are ranked by priority, so the most important mutations are generated first.

### 4. Confidence Threshold

Patterns below **30% confidence** are discarded by the MutationEngine. They appear in logs as informational signals but don't generate mutations. The threshold is hardcoded in `MutationEngine.min_confidence`.

Confidence formulas:

| Strategy | Formula | Range |
|----------|---------|-------|
| Frequency | `0.3 + count × 0.1` | 0.3 – 0.9 |
| Cross-agent | `0.4 + agents × 0.15` | 0.4 – 0.85 |
| Escalation | `0.5 + delta × 0.1` | 0.5 – 0.9 |

### 5. Atomic Changes

One concern per mutation. Each PR addresses exactly one pattern. This makes:
- **Review** straightforward (reviewer sees one focused change)
- **Rollback** safe (revert one PR = undo one change)
- **Tracking** clear (each PR links to one evidence chain)

### 6. Never Delete

Eva only **adds** rules, never removes them. Rule removal is exclusively a human responsibility. This prevents Eva from accidentally removing a critical guardrail.

### 7. Full Transparency

Every mutation includes the full evidence chain:
- Which **signals** triggered the pattern
- Which **pattern** triggered the mutation
- What the **confidence score** is
- What the **severity** assessment is

PR descriptions contain all of this context so the reviewer can make an informed decision.

### 8. Bot Loop Prevention

GitHub Actions workflows skip issues created by `github-actions[bot]`. This prevents Eva from:
1. Creating a PR
2. The PR triggering a new issue
3. Eva scanning the issue
4. Eva creating another PR
5. (infinite loop)

## Quality Checklist

Before proposing any mutation, Eva verifies:

- [ ] Pattern supported by ≥2 signals
- [ ] Confidence ≥ 30%
- [ ] Target file identified and path verified
- [ ] Change is atomic (one concern per mutation)
- [ ] PR description includes full evidence chain
- [ ] No contradiction with existing rules

## Eva's Own Evolution

Eva evolves too. Her EVO skill tracks:
- **False positives** — mutations that got rejected by human reviewers
- **Missed patterns** — issues that slipped through detection
- **Detection accuracy** — confidence calibration over time

When a mutation is rejected, Eva updates her analysis rules. When a pattern is missed, she adds a new detection strategy.

## Failure Modes

| Scenario | Behavior |
|----------|----------|
| Source API down | Source returns empty list, pipeline continues |
| Token expired | Source auth fails, returns 0 signals |
| Too many signals | Only latest 20 per repo fetched |
| All patterns low-confidence | 0 mutations proposed (safe) |
| Max mutations reached | Remaining patterns queued for next run |
| Docker OOM | Container has healthcheck, compose restarts |

## Recommended Workflow

1. **Start with dry-run** — run Eva in dry-run mode for a week, review the logs
2. **Tune confidence** — adjust `min_confidence` if too many/few mutations
3. **Enable live mode** — switch to `--live` when comfortable with the output quality
4. **Review every PR** — never skip the human review step
5. **Monitor false positives** — if Eva proposes bad mutations, the patterns need refinement
