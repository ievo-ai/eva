# EVO — Eva's Self-Evolution Skill

> Eva evolves her own detection and mutation strategies.

## Trigger

Activate when:
- A proposed mutation is **rejected** by a human reviewer
- A known issue **reoccurs** after a mutation was merged
- A new signal type or pattern is identified that wasn't detected
- Detection accuracy drops below threshold

## Workflow

```
1. IDENTIFY  → What did Eva get wrong?
2. CLASSIFY  → False positive | Missed pattern | Bad mutation | Stale rule
3. ROOT CAUSE → Why did the detection/mutation fail?
4. FORMULATE → Adjust detector thresholds, add new strategy, or fix mutation template
5. PROPOSE   → Log the change for review
6. APPLY     → Update Eva's analysis or mutation rules
7. LOG       → Append to EVOLUTION_LOG.md
8. VERIFY    → Run against historical signals to confirm improvement
```

## Entry Format

```markdown
## EVO-{NNN} — {title}
- **Date**: {YYYY-MM-DD}
- **Type**: False positive | Missed pattern | Bad mutation | Stale rule
- **Trigger**: {what went wrong}
- **Root cause**: {why}
- **Mutation**: {what changed in Eva's rules}
- **Confidence**: {low|medium|high}
- **Verified**: {yes|no — did it improve on historical data?}
```

## Rules

1. Track rejection rate — if >50% of mutations are rejected, reduce confidence thresholds
2. Track detection coverage — if patterns are missed, add new detection strategies
3. Never remove a detection strategy, only adjust thresholds
4. Log everything, even if the conclusion is "no change needed"
5. Review last 10 entries before making changes — avoid oscillation
