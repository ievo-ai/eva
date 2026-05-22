# Sources Index

Append-only log of external news / docs / release sources Eva scans during research runs (Step 4 of `.github/workflows/eva-research.yml`).

## Format

Each level-2 heading (`## <URL>`) is one source. Inside the section:

1. A ` ```yaml ` fenced block with the latest scan metadata
2. A `**Summary:**` line — the most recent observation
3. A `History:` bulleted list — chronological scan log, newest at top

YAML schema (required keys, future pre-commit may enforce):

```yaml
last_scan: <ISO 8601 UTC timestamp or "never">
status: <first-scan | changed | unchanged | error>
run_id: <GitHub Actions run ID or null>
```

## How Eva uses this file per run

- **Pre-scan (Step 1):** read each URL section to know the prior state (status, last summary). Build a diff map.
- **Post-scan (Step 4):** for each URL scanned, update the YAML block atop the section AND prepend a new entry to History. Use the `Edit` tool to modify only the relevant section — never rewrite the whole file.
- **New URLs:** if you find a source not yet listed, add a new section at the bottom following the same format.

## Status semantics

- `first-scan` — bootstrap entry, never visited yet
- `changed` — content differs from last scan (worth deep summary)
- `unchanged` — content matches last scan (brief note, skip deep dive)
- `error` — fetch failed, 404, rate-limited, or otherwise unavailable

---

## https://www.anthropic.com/news

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Anthropic's main news/announcements page — Claude releases, Claude Code updates, Anthropic policy announcements.

History:
- (none yet)

---

## https://github.com/anthropics/claude-code/releases

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Claude Code CLI release log — version bumps, new features, breaking changes. We depend on this CLI in `eva-review-pr.yml`.

History:
- (none yet)

---

## https://github.com/anthropics/claude-code-action/releases

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. The GitHub Action `eva-research.yml` runs on. Breaking changes here can break this workflow directly.

History:
- (none yet)

---

## https://docs.anthropic.com/en/docs/claude-code/overview

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Claude Code documentation — new features, new tools, agent SDK changes.

History:
- (none yet)

---

## https://openai.com/index/news/

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. OpenAI announcements — Codex updates, API changes, new models.

History:
- (none yet)

---

## https://github.com/openai/codex/releases

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Codex CLI release log.

History:
- (none yet)

---

## https://blog.google/technology/google-deepmind/

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Google DeepMind blog — Gemini, Antigravity, Google AI agent updates.

History:
- (none yet)

---

## https://agentskills.io/specification

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. The standard our skills conform to. Spec changes = compliance audits needed.

History:
- (none yet)

---

## https://github.com/agentskills/agentskills

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Reference implementation of the agentskills.io spec + `skills-ref` CLI used for validation.

History:
- (none yet)

---

## https://www.cursor.com/changelog

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. Cursor changelog — often anticipates Claude Code direction (e.g. agent patterns, MCP integrations).

History:
- (none yet)

---

## https://news.ycombinator.com

```yaml
last_scan: never
status: first-scan
run_id: null
```

**Summary:** Not yet scanned. HN top stories filtered for `claude code`, `codex`, `agent skills`, `MCP` — community signal of what practitioners care about this week.

History:
- (none yet)
