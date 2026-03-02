# Session 011 — Full Claude Code Access via Telegram

**Date:** 2026-03-02
**Topic:** Refactor Eva's Telegram responder from API fallback to pure Claude Code CLI with tools

## Summary

Transformed Eva's Telegram bot from a stateless API-based responder into a full Claude Code CLI agent with tool access, persistent memory, and sender identity. Removed all unnecessary complexity: API fallback, message classifier, system prompts, role context loading.

## What Was Built

### Responder Refactored (`src/eva/telegram/responder.py`)
- Removed `_call_claude_api`, `CLASSIFY_SYSTEM`, `COMMUNITY_SYSTEM`, `API_SYSTEM`
- Removed `httpx`, `DEFAULT_MODEL`, `DEFAULT_ROLE_PATH`, `_role_context`
- CLI-only: `claude -p --model opus --allowedTools Bash,Read,Glob,Grep,WebFetch`
- Session persistence: `--continue` flag + marker file (`~/.claude/.eva-session`)
- Stale session auto-recovery: if `--continue` fails, marker deleted, retry fresh
- Username in prompt: `[@username]: message text`

### Docker (`Dockerfile`)
- Added `gh` CLI installation for GitHub issue creation
- Replaced `pip` with `uv` + BuildKit cache mounts (`--mount=type=cache,target=/root/.cache/uv`)

### Docker Compose (`docker-compose.yml`)
- Added `GH_TOKEN=${EVA_GITHUB_TOKEN}` environment mapping for `eva-tg-daemon`

### GitHub Client (`src/eva/github/client.py`)
- Added `create_issue()` method with labels support

### CLI (`src/eva/cli.py`)
- `respond(text, username=username)` — passes sender identity

### Tests
- Complete rewrite of `tests/test_telegram_responder.py` (19 tests)
- Added `create_issue` tests in `tests/test_github_client.py`
- 348 tests total, 100% coverage maintained

## Decisions

- **No API fallback** — Claude Code CLI is installed in Docker, tests mock everything
- **No system prompt for CLI** — CLAUDE.md in /app provides all context
- **Opus model** — upgraded from haiku for smarter responses
- **`--allowedTools` whitelist** — Bash, Read, Glob, Grep, WebFetch (not all tools)
- **uv over pip** — faster builds with cache mounts

## Evolutions

1. **Minimal path first** (EVO-015) — don't build fallbacks preemptively
2. **Design for deployment context** — include sender identity in group chat interfaces
3. **Post-push checklist** (EVO-016) — session save + evolution publish after every push
4. **Unified evolution format** (EVO-017) — open source = same transparent format for all agents

## Commits

| Hash | Description |
|------|-------------|
| `816a840` | fix: separate classify/respond sessions |
| `4e5f990` | refactor: professional community support persona |
| `df98050` | simplify: remove classifier entirely |
| `97e9ef3` | feat: persistent conversation memory + opus |
| `fd32b47` | feat: full Claude Code access — remove API, add tools + username |
| `28422c0` | perf: uv with cache mount in Dockerfile |
| `376b799` | evo: minimal path first — remove preemptive fallbacks |
| `46c3cd0` | evo: post-push checklist + session 011 |
| `bc4df9e` | simplify: unified evolution format |

## What's Next

- [ ] Verify Eva responds via Telegram with tools enabled
- [ ] Test GitHub issue creation from Telegram conversation
- [ ] Fix .env CRLF issue on DO host
- [ ] Session 012: children agent development
