# Configuration

Eva reads her configuration from `eva.yaml` in the repository root. All settings have safe defaults.

## eva.yaml Reference

```yaml
# Repositories Eva monitors and can submit PRs to
repos:
  cli: ievo-ai/cli
  marketplace: ievo-ai/marketplace
  sdk: ievo-ai/sdk
  eva: ievo-ai/eva
  landing: ievo-ai/ievo.ai

# Signal sources
sources:
  sentry:
    enabled: false
    # extra:
    #   org: your-sentry-org
    #   project: your-project
  github_issues:
    enabled: true
  reviews:
    enabled: false
  evolution_logs:
    enabled: true

# Safety settings
dry_run: true                # No PRs created (use --live to override)
max_mutations_per_run: 5     # Cap on mutations per pipeline execution
auto_merge: false            # Never auto-merge (always requires human review)
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `repos` | dict | 5 ievo-ai repos | Map of label → GitHub repo path. Eva polls all repos for issues and can submit PRs to any of them. |
| `sources.sentry.enabled` | bool | `false` | Enable Sentry error tracking source |
| `sources.sentry.extra.org` | str | `""` | Sentry organization slug |
| `sources.sentry.extra.project` | str | `""` | Sentry project slug |
| `sources.github_issues.enabled` | bool | `true` | Enable GitHub Issues polling |
| `sources.reviews.enabled` | bool | `false` | Enable PR review comments polling |
| `sources.evolution_logs.enabled` | bool | `true` | Enable agent evolution log parsing |
| `dry_run` | bool | `true` | Dry-run mode — mutations are logged but no PRs created |
| `max_mutations_per_run` | int | `5` | Maximum number of mutations per pipeline run |
| `auto_merge` | bool | `false` | Auto-merge flag (never recommended, requires human review) |

## Environment Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `EVA_GITHUB_TOKEN` | GitHub Issues, Reviews | GitHub PAT or App token for API access |
| `EVA_SENTRY_TOKEN` | Sentry | Sentry auth token for error tracking API |

### In GitHub Actions

Tokens are stored as **repository secrets** in `ievo-ai/eva`:

```
Settings → Secrets and variables → Actions → Secrets:
  EVA_GITHUB_TOKEN = ghp_...
  EVA_SENTRY_TOKEN = sntrys_...    (optional)
  APP_ID = 123456                  (if using GitHub App)
  APP_PRIVATE_KEY = -----BEGIN...  (if using GitHub App)
```

### In Docker

Tokens are passed via environment variables:

```bash
# Direct
docker run --rm -e EVA_GITHUB_TOKEN=ghp_... eva scan

# Via .env file
cp .env.example .env
# Edit .env with your tokens
docker compose up
```

## Source Config Details

Each source has a `SourceConfig` with common fields:

```python
@dataclass
class SourceConfig:
    enabled: bool = False
    endpoint: str = ""          # Custom API endpoint (override default)
    token_env: str = ""         # Env var name holding the auth token
    poll_interval_sec: int = 300  # Polling interval (for future cron use)
    extra: dict = {}            # Source-specific config
```

## Loading Config

Eva loads config in this order:

1. Create `EvaConfig` with defaults
2. If `eva.yaml` exists, override fields from file
3. CLI flags (`--live`, `--marketplace`) override config values

```python
config = EvaConfig.load(Path("eva.yaml"))
config.dry_run = not live  # CLI override
```

## Generating Default Config

```bash
eva init
```

Creates a new `eva.yaml` with sensible defaults. Interactive prompts let you configure repos and sources.
