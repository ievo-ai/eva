# Pipeline

> OBSERVE → ANALYZE → MUTATE

Every Eva run executes three sequential phases. The pipeline is implemented in `eva.pipeline.EvaPipeline`.

## Phase 1: OBSERVE

Eva polls all enabled signal sources. Each source returns a list of normalized `Signal` objects.

```python
for source in self.sources:
    signals = await source.poll()
    result.signals.extend(signals)
```

Key behavior:
- Sources that fail return empty lists (no pipeline interruption)
- Enabled sources are configured in `eva.yaml`
- Each source authenticates independently via environment variables
- Signals are deduplicated by their `key` property (`type:source:id`)
- **If 0 signals → pipeline exits early** (no patterns, no mutations)

## Phase 2: ANALYZE

The `PatternDetector` ingests all collected signals and runs **three independent detection strategies**:

### 2.1 Frequency Detection

Groups signals by simplified title (first 5 words, lowercase). If the same title appears ≥2 times, a recurring pattern is created.

```
confidence = min(0.3 + count × 0.1, 0.9)
```

Example: If "CLI crashes on empty config" appears 4 times → confidence = 0.7

### 2.2 Cross-Agent Detection

Checks if the same tag appears in signals from ≥2 different agents/repos. Indicates systemic issues that span the platform.

```
confidence = min(0.4 + agent_count × 0.15, 0.85)
```

Generic tags (`github`, `sentry`, `evo`, `review`) are excluded. Cross-agent patterns are automatically marked `HIGH` severity.

### 2.3 Escalation Detection

Monitors per-agent severity trends. Takes the last 5 signals per agent, ranks severity (INFO=0 → CRITICAL=4), checks if trend is upward.

```
confidence = min(0.5 + severity_delta × 0.1, 0.9)
```

Triggers when severity jumps ≥2 levels. Escalation patterns are marked `CRITICAL`.

### Filtering

Patterns below the **30% confidence threshold** are discarded by the MutationEngine. They still appear in logs as informational.

## Phase 3: MUTATE

The `MutationEngine` converts patterns into concrete changes.

### Ranking

Patterns are ranked by `severity_weight × confidence` (descending):

| Severity | Weight |
|----------|--------|
| CRITICAL | 1.0 |
| HIGH | 0.8 |
| MEDIUM | 0.5 |
| LOW | 0.3 |
| INFO | 0.1 |

### Pattern → Mutation Mapping

| Pattern Type | Mutation Type | Target |
|-------------|---------------|--------|
| `freq:*` (recurring) | `ROLE_PATCH` | `agents/*/ROLE.md` — add rule to prevent recurrence |
| `cross:*` (cross-agent) | `SKILL_PATCH` | `shared/skills/evo/SKILL.md` — update shared skill |
| `escalation:*` | `MEMORY_UPDATE` | `agents/*/memory/CONTEXT.md` — add warning + guardrails |

### Output

Each mutation contains:
- **target_repo** — which repo to submit the PR to
- **target_path** — which file to modify
- **diff** — the actual patch content (PR-ready)
- **confidence** — inherited from pattern (may be reduced for cross-agent)
- **pattern_id** — link back to the evidence

### Dry-Run vs Live

| Mode | Flag | Behavior |
|------|------|----------|
| **Dry-run** (default) | `--dry-run` or no flag | Mutations logged + displayed, no PRs |
| **Live** | `--live` or `--no-dry-run` | Branch created, commit pushed, PR opened |

In both modes, Eva never auto-merges. Every PR requires human review.

## Pipeline Summary Output

After each run, Eva prints a Rich-formatted summary table:

```
┌─────────────────────────────────────┐
│          Eva Run Summary            │
├───────────────────┬─────────────────┤
│ Metric            │           Count │
├───────────────────┼─────────────────┤
│ Signals collected │               8 │
│ Patterns detected │               2 │
│ Mutations proposed│               2 │
│ Mode              │        dry-run  │
└───────────────────┴─────────────────┘
```

## Error Handling

- Source failures are caught and logged (pipeline continues)
- Zero signals → early exit (no wasted analysis)
- Zero patterns → early exit (no mutation attempt)
- Mutations capped at `max_mutations_per_run` (default: 5)
