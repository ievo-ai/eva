# Signal Sources

Eva collects signals from four types of sources. Each source normalizes external data into the unified `Signal` model.

All sources implement the `BaseSource` abstract class:

```python
class BaseSource(ABC):
    async def poll(self) -> list[Signal]: ...
    async def healthcheck(self) -> bool: ...
    def is_enabled(self) -> bool: ...
```

## Overview

| Source | Class | Token | Default | Data |
|--------|-------|-------|---------|------|
| Sentry | `SentrySource` | `EVA_SENTRY_TOKEN` | Disabled | Unresolved errors, crashes |
| GitHub Issues | `GitHubIssuesSource` | `EVA_GITHUB_TOKEN` | **Enabled** | Open issues across all repos |
| PR Reviews | `ReviewsSource` | `EVA_GITHUB_TOKEN` | Disabled | Code review comments |
| Evolution Logs | `EvolutionLogsSource` | (none) | **Enabled** | Agent self-correction logs |

## Sentry (`SentrySource`)

**File:** `src/eva/sources/sentry.py`

Polls Sentry API (`/api/0/projects/{org}/{project}/issues/`) for unresolved issues sorted by last seen date.

### Severity Mapping

| Sentry Level | Eva Severity |
|-------------|-------------|
| fatal | CRITICAL |
| error | HIGH |
| warning | MEDIUM |
| info | LOW |
| debug | INFO |

### Configuration

```yaml
# eva.yaml
sources:
  sentry:
    enabled: true
    extra:
      org: your-sentry-org
      project: your-project
```

Environment: `EVA_SENTRY_TOKEN` — Sentry auth token.

### Signal Metadata

- `count` — number of occurrences
- `culprit` — the code location
- `platform` — runtime platform
- `permalink` — link to Sentry issue

## GitHub Issues (`GitHubIssuesSource`)

**File:** `src/eva/sources/github_issues.py`

Polls open issues across all configured iEvo repositories via GitHub REST API. Fetches the 20 most recently updated issues per repo.

### Severity Mapping

Determined by issue labels:

| Label Contains | Eva Severity |
|---------------|-------------|
| `critical` | CRITICAL |
| `bug` | HIGH |
| `help wanted` | MEDIUM |
| `enhancement` | LOW |
| `feature` | LOW |
| `documentation` | INFO |
| (no match) | MEDIUM |

### Behavior

- Skips pull requests (GitHub returns them in the issues endpoint)
- Uses `since` parameter to avoid re-fetching old issues
- Each repo is labeled (e.g. `cli`, `marketplace`) for cross-agent detection

### Signal Metadata

- `repo` — full repo path (`ievo-ai/cli`)
- `repo_label` — short label (`cli`)
- `labels` — GitHub issue labels
- `author` — issue author login
- `comments` — comment count
- `url` — link to issue on GitHub

## PR Reviews (`ReviewsSource`)

**File:** `src/eva/sources/reviews.py`

Polls pull request comments and review comments across iEvo repos. Uses heuristic severity classification based on comment content.

### Severity Heuristics

Keywords in comment body determine severity:
- `critical`, `break`, `security` → CRITICAL/HIGH
- `bug`, `fix`, `wrong` → HIGH/MEDIUM
- `suggestion`, `nit`, `minor` → LOW
- Default → MEDIUM

### Use Cases

Detects recurring code review patterns, e.g.:
- "Missing error handling" appearing in 5 PRs → frequency pattern
- Same style issue across 3 repos → cross-agent pattern

## Evolution Logs (`EvolutionLogsSource`)

**File:** `src/eva/sources/evolution_logs.py`

Reads `EVOLUTION_LOG.md` files from the marketplace repository. These logs are written by individual agents' EVO skills when they self-correct.

### Parsing

Eva parses logs using regex to extract:
- Mutation date and type
- Error classification
- Rule that was added
- Severity of the original error

### Why This Matters

Evolution logs give Eva visibility into **what every agent has learned**. If the same class of error triggers EVO mutations in 3 different agents, Eva detects the cross-agent pattern and proposes a shared skill update instead of each agent solving it independently.

### Configuration

No token needed — reads directly from the filesystem (marketplace repo mounted as volume in Docker / checked out in GitHub Actions).

```yaml
sources:
  evolution_logs:
    enabled: true
```

## Adding a New Source

To add a new signal source:

1. Create `src/eva/sources/my_source.py`
2. Implement `BaseSource`:

```python
class MySource(BaseSource):
    name = "my_source"

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)

    async def poll(self) -> list[Signal]:
        # Fetch data, normalize to Signal objects
        return signals

    async def healthcheck(self) -> bool:
        # Return True if source is reachable
        return True
```

3. Register in `pipeline.py`:

```python
if config.my_source.enabled:
    self.sources.append(MySource(config.my_source))
```

4. Add config to `EvaConfig` in `config.py`
5. Add to `eva.yaml`
