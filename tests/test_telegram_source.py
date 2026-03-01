"""Tests for Telegram community source."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.config import SourceConfig
from eva.core.models import Severity, SignalType
from eva.sources.telegram import TelegramSource, _classify_severity


def _make_config(**kwargs) -> SourceConfig:
    defaults = {
        "enabled": True,
        "token_env": "TELEGRAM_BOT_TOKEN",
        "extra": {},
    }
    defaults.update(kwargs)
    return SourceConfig(**defaults)


def _mock_response(data: dict) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = data
    return resp


# ── Init ──────────────────────────────────────────────────


class TestTelegramSourceInit:
    def test_name(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())
        assert source.name == "telegram"

    def test_loads_token_from_env(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok-123", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())
        assert source._token == "tok-123"

    def test_loads_offset_from_extra(self):
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "tok"}, clear=True):
            source = TelegramSource(_make_config(extra={"offset": 42}))
        assert source._offset == 42


# ── Poll ──────────────────────────────────────────────────


class TestTelegramSourcePoll:
    @pytest.mark.asyncio
    async def test_returns_empty_without_token(self):
        with patch.dict("os.environ", {}, clear=True):
            source = TelegramSource(_make_config())
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_polls_messages(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "text": "Can you add dark mode?",
                        "date": 1709000000,
                        "chat": {"id": -100},
                        "from": {"username": "alice", "first_name": "Alice"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert len(signals) == 1
        assert signals[0].type == SignalType.TELEGRAM_MESSAGE
        assert signals[0].title == "Can you add dark mode?"
        assert signals[0].metadata["username"] == "alice"
        assert source._offset == 2

    @pytest.mark.asyncio
    async def test_filters_by_chat_id(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "text": "Wrong chat",
                        "date": 1709000000,
                        "chat": {"id": -999},
                        "from": {"first_name": "Eve"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_deduplicates(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        source._seen.add(101)

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "text": "Duplicate",
                        "date": 1709000000,
                        "chat": {"id": -100},
                        "from": {"first_name": "Bob"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_skips_messages_without_text(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "date": 1709000000,
                        "chat": {"id": -100},
                        "from": {"first_name": "Photo"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_api_failure_returns_empty(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response({"ok": False})
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_http_error_returns_empty(self):
        import httpx

        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        mock_httpx = AsyncMock()
        mock_httpx.get.side_effect = httpx.HTTPError("timeout")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_stores_offset_in_config(self):
        config = _make_config(extra={})
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(config)

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 5,
                    "message": {
                        "message_id": 101,
                        "text": "Hello",
                        "date": 1709000000,
                        "chat": {"id": -100},
                        "from": {"first_name": "User"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            await source.poll()

        assert config.extra["offset"] == 6

    @pytest.mark.asyncio
    async def test_sends_offset_param(self):
        config = _make_config(extra={"offset": 42})
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(config)

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response({"ok": True, "result": []})
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            await source.poll()

        call_kwargs = mock_httpx.get.call_args[1]["params"]
        assert call_kwargs["offset"] == 42

    @pytest.mark.asyncio
    async def test_no_chat_filter_accepts_all(self):
        """When TELEGRAM_COMMUNITY_CHAT is not set, accept all chats."""
        with patch.dict("os.environ", {"TELEGRAM_BOT_TOKEN": "tok"}, clear=True):
            source = TelegramSource(_make_config())

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "text": "Hello from any chat",
                        "date": 1709000000,
                        "chat": {"id": -999},
                        "from": {"first_name": "Any"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert len(signals) == 1

    @pytest.mark.asyncio
    async def test_username_fallback_to_first_name(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        updates = {
            "ok": True,
            "result": [
                {
                    "update_id": 1,
                    "message": {
                        "message_id": 101,
                        "text": "No username",
                        "date": 1709000000,
                        "chat": {"id": -100},
                        "from": {"first_name": "OnlyFirst"},
                    },
                }
            ],
        }

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response(updates)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            signals = await source.poll()

        assert signals[0].metadata["username"] == "OnlyFirst"


# ── Healthcheck ───────────────────────────────────────────


class TestTelegramSourceHealthcheck:
    @pytest.mark.asyncio
    async def test_healthy(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response({"ok": True, "result": {"id": 123}})
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            result = await source.healthcheck()

        assert result is True

    @pytest.mark.asyncio
    async def test_unhealthy(self):
        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        mock_httpx = AsyncMock()
        mock_httpx.get.return_value = _mock_response({"ok": False})
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            result = await source.healthcheck()

        assert result is False

    @pytest.mark.asyncio
    async def test_no_token(self):
        with patch.dict("os.environ", {}, clear=True):
            source = TelegramSource(_make_config())
        result = await source.healthcheck()
        assert result is False

    @pytest.mark.asyncio
    async def test_http_error(self):
        import httpx

        with patch.dict(
            "os.environ", {"TELEGRAM_BOT_TOKEN": "tok", "TELEGRAM_COMMUNITY_CHAT": "-100"}
        ):
            source = TelegramSource(_make_config())

        mock_httpx = AsyncMock()
        mock_httpx.get.side_effect = httpx.HTTPError("timeout")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.telegram.httpx.AsyncClient", return_value=mock_httpx):
            result = await source.healthcheck()

        assert result is False


# ── Severity Classification ──────────────────────────────


class TestClassifySeverity:
    def test_bug_keyword(self):
        assert _classify_severity("There is a bug in the code") == Severity.HIGH

    def test_crash_keyword(self):
        assert _classify_severity("App crash on startup") == Severity.CRITICAL

    def test_feature_keyword(self):
        assert _classify_severity("Feature request: dark mode") == Severity.LOW

    def test_default_severity(self):
        assert _classify_severity("Hello everyone") == Severity.LOW

    def test_case_insensitive(self):
        assert _classify_severity("HELP me please") == Severity.MEDIUM
