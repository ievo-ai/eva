# Session 010: Telegram Integration + Evolution Publishing

**Date**: 2026-03-01
**Topic**: Integrate evolution publishing into Eva's session-end process + Telegram community bot

## Plan

### Phase 1: Core Models
- [x] `EvolutionEntry` dataclass + `EvolutionType` enum in `core/models.py`
- [x] Tests in `test_models.py`

### Phase 2: Telegram Package
- [x] `src/eva/telegram/client.py` — TelegramClient (async httpx)
- [x] `src/eva/telegram/formatter.py` — child vs Eva personality
- [x] `src/eva/telegram/responder.py` — EvaResponder (Claude API persona)
- [x] Tests: `test_telegram.py`, `test_telegram_responder.py`

### Phase 3: Publisher Refactor + Source
- [x] Refactor `EvolutionPublisher` for `EvolutionEntry` + Telegram
- [x] `src/eva/sources/telegram.py` — TelegramSource
- [x] Tests: `test_evolution_publisher.py`, `test_telegram_source.py`

### Phase 4: Integration
- [x] Config: add `telegram` to EvaConfig
- [x] Pipeline: wire TelegramSource + EvolutionEntry in Phase 5
- [x] CLI: `eva publish` + `eva tg-process` commands
- [x] Tests: `test_config.py`, `test_pipeline.py`, `test_cli.py`

### Phase 5: Infrastructure
- [x] `docker-compose.yml` — add `eva-tg` service
- [x] `.env` — add `TELEGRAM_COMMUNITY_CHAT`, `ANTHROPIC_API_KEY`
- [ ] GitHub secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_COMMUNITY_CHAT`, `ANTHROPIC_API_KEY`
- [x] Update `/evo` skill, CLAUDE.md, deprecate script

---

## Key Decisions

- Children (spec-writer, architect, coder, researcher) = open source, transparent evolutions
- Eva (mother) = closed source, mysterious "spiced" evolutions
- Telegram bot uses Claude API (haiku model) for community responses
- Docker service `eva-tg` runs on demand (not persistent)
- ROLE.md mounted read-only for Eva persona context
- `TELEGRAM_COMMUNITY_CHAT` as single env var (not separate CHAT_ID + ALLOWED_CHATS)
- `TELEGRAM_MESSAGE` added to SignalType enum (separate from GITHUB_ISSUE)

## New Rules Added

- **Never fit tests to results**: fix the code, not the assertion
- **Errors = evolution, panic = enemy**: stay calm, analyze, fix properly

## Discussion Summary

Denis specified:
1. Eva can create topics in Telegram if needed
2. Use `TELEGRAM_COMMUNITY_CHAT` env var (not CHAT_ID or ALLOWED_CHATS)
3. BotFather privacy mode needs disabling for @ievo_ai_bot
4. Tests must verify correctness, not be adjusted to match wrong output
5. Errors are part of evolution — panic is the enemy

## What Was Built

### New Files (8)
| File | Purpose |
|------|---------|
| `src/eva/telegram/__init__.py` | Package init |
| `src/eva/telegram/client.py` | Telegram Bot API client (send, topics, updates) |
| `src/eva/telegram/formatter.py` | Dual personality formatting (children vs Eva) |
| `src/eva/telegram/responder.py` | Claude API community responder with Eva persona |
| `src/eva/sources/telegram.py` | TelegramSource signal source for pipeline |
| `tests/test_telegram.py` | Client + formatter tests (30) |
| `tests/test_telegram_responder.py` | Responder tests (22) |
| `tests/test_telegram_source.py` | Source tests (23) |

### Modified Files (13)
| File | Change |
|------|--------|
| `src/eva/core/models.py` | Added EvolutionEntry, EvolutionType, TELEGRAM_MESSAGE |
| `src/eva/github/evolution_publisher.py` | Refactored for EvolutionEntry + Telegram |
| `src/eva/core/config.py` | Added telegram source config |
| `src/eva/pipeline.py` | Wired TelegramSource + _make_telegram_client() |
| `src/eva/cli.py` | Added `publish` and `tg-process` commands |
| `docker-compose.yml` | Added eva-tg service |
| `.claude/skills/evo/SKILL.md` | Added publish step |
| `CLAUDE.md` | Updated architecture, commands, env vars, rules |
| `scripts/publish-evolution.py` | Deprecation notice |
| `tests/test_cli.py` | 11 new tests (publish + tg-process) |
| `tests/test_evolution_publisher.py` | Rewritten for EvolutionEntry |
| `tests/test_models.py` | EvolutionEntry tests |
| `tests/test_pipeline.py` | TelegramSource + _make_telegram_client tests |

## Stats

- **349 tests**, 100% coverage
- **1462 statements**, 416 branches — all covered
- **21 files changed**, 2377 insertions, 50 deletions

## Commits

| Hash | Description |
|------|-------------|
| `0c0a3b6` | feat: integrate Telegram community + evolution publishing into Eva |

## What's Next

- [ ] Set GitHub secrets: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_COMMUNITY_CHAT`, `ANTHROPIC_API_KEY`
- [ ] Disable BotFather privacy mode for @ievo_ai_bot
- [ ] Set `TELEGRAM_COMMUNITY_CHAT` in .env after adding bot to group
- [ ] End-to-end test: `eva publish --live` + `eva tg-process`
- [ ] Session log + `/evo`
