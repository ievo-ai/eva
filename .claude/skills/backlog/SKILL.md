---
name: backlog
description: >-
  Capture an idea into .ievo/backlog/ instantly.
  Use when you want to save an idea before it's lost.
argument-hint: "<idea in any form>"
---

# /backlog — Quick Idea Capture

Capture an idea into `.ievo/backlog/` instantly. No ceremony, no full proposal — just get it written before it's lost.

## Usage

```
/backlog <idea in any form>
```

## Workflow

1. **Read** `.ievo/backlog/` to find the next IDEA number
   - If no IDEA files exist → start at IDEA-001
   - Find the highest existing IDEA-NNN → increment

2. **Create** `.ievo/backlog/IDEA-NNN-<slug>.md`:

```markdown
# IDEA-NNN: <title>

**Date:** YYYY-MM-DD
**Source:** <session context or "user">
**Status:** raw

## Idea

<captured text — clean up grammar but preserve intent>

## Why

<1-2 sentences: what problem does this solve or what value does it add?>
```

3. **Confirm** — print the file path and one-line summary. Nothing else.

## Rules

- **Speed over polish.** This is a capture tool, not a proposal writer. 30 seconds max.
- **Preserve intent.** Clean up grammar but don't rewrite the idea. User's words matter.
- **Slug from title.** `IDEA-003-docker-sandbox.md` not `IDEA-003.md`
- **No duplicates.** Quickly scan existing ideas — if something very similar exists, mention it instead of creating a duplicate.
- **Status: raw.** Ideas start as `raw`. Researcher or human promotes them to proposals (`PROP-xxx`).
- **No evaluation.** Don't judge the idea. Don't add pros/cons. Just capture it.
