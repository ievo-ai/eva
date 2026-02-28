# EVO — Eva's Self-Evolution Skill

> Eva evolves her own detection and mutation strategies based on outcomes.

## Trigger

Activate when:
- A proposed mutation is **rejected** by a human reviewer
- A known issue **reoccurs** after a mutation was merged
- A new signal type or pattern is identified that existing strategies missed
- Detection accuracy drops (rejection rate > 50%)
- A new signal source is added to the platform

## Workflow

```
1. IDENTIFY   → What did Eva get wrong? (rejected PR, missed pattern, bad mutation)
2. CLASSIFY   → False positive | Missed pattern | Bad mutation | Stale rule
3. ROOT CAUSE → Why did the detection/mutation fail?
4. FORMULATE  → Adjust detector thresholds, add new strategy, or fix mutation template
5. PROPOSE    → Log the change to EVOLUTION_LOG.md for review
6. APPLY      → Update Eva's analysis or mutation rules
7. VERIFY     → Run against historical signals to confirm improvement
```

## Classification

| Type | Description | Action |
|------|-------------|--------|
| **False positive** | Pattern detected, mutation proposed, but PR rejected as unnecessary | Lower confidence for that pattern type, tighten detection threshold |
| **Missed pattern** | Issue existed across signals but Eva didn't detect it | Add new detection strategy or lower min_frequency |
| **Bad mutation** | Pattern was real, but the proposed change was wrong/insufficient | Fix mutation template in engine.py |
| **Stale rule** | Previously valid detection rule no longer applies | Adjust threshold (never delete the rule) |

## Entry Format

```markdown
## EVO-{NNN} — {title}
- **Date**: {YYYY-MM-DD}
- **Type**: False positive | Missed pattern | Bad mutation | Stale rule
- **Trigger**: {what went wrong — link to PR/issue}
- **Root cause**: {why the detection/mutation failed}
- **Mutation**: {what changed in Eva's rules}
- **Confidence**: {low|medium|high}
- **Verified**: {yes|no — did it improve on historical data?}
```

## Rules

1. **Track rejection rate** — if >50% of mutations are rejected in a rolling window, reduce confidence thresholds globally
2. **Track detection coverage** — if patterns are consistently missed, add new detection strategies
3. **Never remove a detection strategy** — only adjust thresholds (removals are human decisions)
4. **Log everything** — even if the conclusion is "no change needed"
5. **Review last 10 entries before making changes** — avoid oscillation between competing adjustments
6. **One evolution per trigger** — don't batch multiple self-corrections, keep them atomic
7. **Link to evidence** — every EVO entry references the specific PR, issue, or signal

## Metrics to Track

| Metric | How | Target |
|--------|-----|--------|
| Mutation acceptance rate | Accepted PRs / Total proposed | > 70% |
| Detection coverage | Patterns detected / Issues filed | > 80% |
| False positive rate | Rejected PRs / Total proposed | < 30% |
| Confidence calibration | Actual acceptance % vs. predicted confidence | Within 15% |
| Time to detection | Issue opened → Pattern detected | < 12 hours (2 cron cycles) |

## Self-Evolution Cycle

```
Rejected PR → EVO trigger → classify → adjust rules → log → verify
                                                           ↓
                                                    Better next run
```

Eva's quality improves over time:
- Fewer false positives (better thresholds)
- Fewer missed patterns (broader strategies)
- More accurate confidence scores (calibrated from outcomes)
- Better mutation templates (learned from reviewer feedback)

## Integration with Detection Strategies

Current strategies that can be tuned:

| Strategy | Tunable Parameters | Default |
|----------|--------------------|---------|
| Frequency | `min_frequency` | 2 |
| Frequency | confidence formula base | 0.3 |
| Cross-agent | min agents for pattern | 2 |
| Cross-agent | confidence formula base | 0.4 |
| Escalation | min severity delta | 2 levels |
| Escalation | min signals per agent | 3 |
| Global | `min_confidence` threshold | 0.3 |
| Global | `max_per_run` limit | 5 |
