# Eva Research — Audit Memory

Per-run audit reports from the `Eva Research` workflow (`.github/workflows/eva-research.yml`).

## Format

One file per run, immutable after creation:

```
YYYY-MM-DD-HHMM-skills-audit.md
```

Filename uses UTC timestamp. The `skills-audit` suffix anticipates future audit variants (cortex-audit, marketplace-audit, etc.) — each gets its own per-run file.

## Why per-run files instead of a rolling log

- **No merge conflicts** when two runs land close together (each writes its own file)
- **Immutable history** — past audits never get amended, the record is the record
- **Easy to glob** — `researches/*-skills-audit.md` gives the full skills audit history
- **Easy to truncate** — drop oldest files when the directory grows unwieldy without touching anything else

## How Eva uses prior reports

At the start of each research run, Eva reads the 5 most recent files in this directory. The reports inform:

- **Skip areas already deeply audited recently** — no point re-checking `plugins/ievo/skills/init/` if the last audit found it clean two days ago
- **Reconsider deferred findings** — "needs more thought" items from past runs come up for re-evaluation with fresh context
- **Honor "Notes for next run"** — explicit hints from past Eva to future Eva

## Content schema

Each file is YAML-frontmatter + Markdown. Frontmatter keys:

| Key | Type | Description |
|-----|------|-------------|
| `date` | ISO 8601 UTC | Run start time |
| `run_id` | string | GitHub Actions run ID |
| `duration` | string | Wall-clock, e.g. `7m44s` |
| `turns` | int | Claude turns consumed |
| `cost_usd` | float | Run cost from Claude SDK report |
| `verdict` | enum | `skills_prs_opened` / `feature_proposals_opened` / `both` / `no_high_confidence` / `blocked` |

Body sections (each optional, omit if empty):
- `## Audited areas`
- `## Sources scanned` — summary of this run's Step 4 scan (changes detected + errors). Full per-URL state lives in `sources-index.md`.
- `## Skills PRs opened` — atomic fix PRs to existing functionality
- `## Feature proposals opened` — new-capability `eva-proposal` issues
- `## Deferred findings`
- `## Blockers`
- `## Notes for next run`

## Companion files in this directory

- **`sources-index.md`** — append-only index of external news / docs / release URLs Eva scans during Step 4. One section per URL with YAML metadata block + history of scans. Eva reads it at run start to build a "last seen" map, and updates it per URL during the scan. New URLs encountered in the wild get appended as new sections. See the file's own header for the format spec.

## Lifecycle

- Created by the Researcher step of `eva-research.yml`
- Committed to a branch `research/audit-<timestamp>`
- Opened as a PR to `main`
- Eva-review-pr.yml auto-approves on merge — Telegram fires via the merge-event in `publish-evolution.yml`
- The merge places the report in `main`, where the next run's Step 1 can read it
