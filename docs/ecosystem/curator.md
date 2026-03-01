# Curator

The Curator is Level 2 of the iEvo evolution system — it detects cross-agent patterns and proposes shared skill updates.

**Repo**: [ievo-ai/curator](https://github.com/ievo-ai/curator)

## Pipeline

```
COLLECT → ANALYZE → PROPOSE
```

1. **Collect**: Read all agents' `EVOLUTION_LOG.md` files from the marketplace
2. **Analyze**: Run 3 detection strategies across agent boundaries
3. **Propose**: Generate shared skill updates or marketplace-wide changes

## Detection Strategies

| Strategy | What It Finds |
|----------|---------------|
| **Error class clustering** | Same error types appearing in multiple agents |
| **Tag overlap** | Agents using similar tags in their evolution logs |
| **Rule convergence** | Multiple agents independently arriving at similar rules |

## Relationship to Eva

```
EVO (agent-local) → Curator (cross-agent) → Eva (platform-wide)
```

- **EVO** handles single-agent self-correction
- **Curator** detects patterns spanning multiple agents
- **Eva** observes the entire platform including external signals

Eva can trigger Curator via `repository_dispatch` when cross-agent patterns are detected in her analysis.

## Stack

- **Python 3.13+** with uv
- **httpx** for GitHub API access
- **36 tests**, all passing
