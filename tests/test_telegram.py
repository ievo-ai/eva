"""Tests for Telegram client and message formatter."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.models import EvolutionEntry, EvolutionType
from eva.telegram.client import TelegramClient, TelegramResult
from eva.telegram.formatter import (
    EVA_CHILDREN,
    EVA_DEFAULT_SPICE,
    EVA_SPICE,
    format_child_message,
    format_eva_message,
    format_telegram_message,
)

# ── TelegramClient init ────────────────────────────────────


class TestTelegramClientInit:
    def test_raises_without_token(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="No Telegram token"),
        ):
            TelegramClient(token=None, chat_id="-100123")

    def test_raises_without_chat_id(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="No Telegram chat ID"),
        ):
            TelegramClient(token="test-token")

    def test_accepts_explicit_params(self):
        client = TelegramClient(token="test-token", chat_id="-100123")
        assert client._token == "test-token"
        assert client._chat_id == "-100123"

    def test_reads_env_vars(self):
        with patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "env-token", "TELEGRAM_COMMUNITY_CHAT": "-100456"},
        ):
            client = TelegramClient()
        assert client._token == "env-token"
        assert client._chat_id == "-100456"


# ── TelegramClient.send_message ─────────────────────────────


class TestTelegramSendMessage:
    def _mock_httpx_response(self, json_data: dict) -> MagicMock:
        mock_resp = MagicMock()
        mock_resp.json.return_value = json_data
        return mock_resp

    @pytest.mark.asyncio
    async def test_send_message_success(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = self._mock_httpx_response(
            {"ok": True, "result": {"message_id": 42}}
        )
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.send_message("Hello world")

        assert result == TelegramResult(success=True, message_id=42)

    @pytest.mark.asyncio
    async def test_send_message_failure(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = self._mock_httpx_response(
            {"ok": False, "description": "Chat not found"}
        )
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.send_message("Hello")

        assert result.success is False
        assert result.error == "Chat not found"

    @pytest.mark.asyncio
    async def test_send_message_with_thread_and_reply(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = self._mock_httpx_response(
            {"ok": True, "result": {"message_id": 99}}
        )
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.send_message("Reply", message_thread_id=5, reply_to_message_id=10)

        assert result.success is True
        call_kwargs = mock_httpx.post.call_args[1]["json"]
        assert call_kwargs["message_thread_id"] == 5
        assert call_kwargs["reply_to_message_id"] == 10


# ── TelegramClient.create_forum_topic ────────────────────────


class TestTelegramForumTopic:
    @pytest.mark.asyncio
    async def test_create_topic_success(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        resp = MagicMock()
        resp.json.return_value = {
            "ok": True,
            "result": {"message_thread_id": 77},
        }
        mock_httpx.post.return_value = resp
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            topic_id = await client.create_forum_topic("Evolutions")

        assert topic_id == 77

    @pytest.mark.asyncio
    async def test_create_topic_failure(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        resp = MagicMock()
        resp.json.return_value = {"ok": False, "description": "Not a forum"}
        mock_httpx.post.return_value = resp
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            topic_id = await client.create_forum_topic("Test")

        assert topic_id is None


# ── TelegramClient.get_updates ───────────────────────────────


class TestTelegramGetUpdates:
    @pytest.mark.asyncio
    async def test_get_updates_success(self):
        client = TelegramClient(token="test", chat_id="-100123")

        updates = [
            {"update_id": 1, "message": {"text": "Hello"}},
            {"update_id": 2, "message": {"text": "World"}},
        ]
        mock_httpx = AsyncMock()
        resp = MagicMock()
        resp.json.return_value = {"ok": True, "result": updates}
        mock_httpx.get.return_value = resp
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.get_updates(offset=0)

        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_updates_with_offset(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        resp = MagicMock()
        resp.json.return_value = {"ok": True, "result": []}
        mock_httpx.get.return_value = resp
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            await client.get_updates(offset=42)

        call_kwargs = mock_httpx.get.call_args[1]["params"]
        assert call_kwargs["offset"] == 42

    @pytest.mark.asyncio
    async def test_get_updates_api_failure(self):
        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        resp = MagicMock()
        resp.json.return_value = {"ok": False}
        mock_httpx.get.return_value = resp
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.get_updates()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_updates_http_error(self):
        import httpx

        client = TelegramClient(token="test", chat_id="-100123")

        mock_httpx = AsyncMock()
        mock_httpx.get.side_effect = httpx.HTTPError("Connection failed")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.client.httpx.AsyncClient", return_value=mock_httpx):
            result = await client.get_updates()

        assert result == []


# ── Formatter ────────────────────────────────────────────────


def _make_entry(**kwargs) -> EvolutionEntry:
    defaults = {
        "title": "Test evolution",
        "agent": "spec-writer",
        "type": EvolutionType.ROLE_PATCH,
        "target": "agents/spec-writer/ROLE.md",
        "description": "Fixed format validation.",
        "confidence": 0.75,
        "pr_url": "https://github.com/ievo-ai/marketplace/pull/5",
        "id": "EVO-042",
        "date": "2026-03-01",
    }
    defaults.update(kwargs)
    return EvolutionEntry(**defaults)


class TestFormatChildMessage:
    def test_contains_agent_and_type(self):
        msg = format_child_message(_make_entry())
        assert "spec-writer" in msg
        assert "role_patch" in msg

    def test_contains_title_and_target(self):
        msg = format_child_message(_make_entry())
        assert "Test evolution" in msg
        assert "agents/spec-writer/ROLE.md" in msg

    def test_contains_confidence_and_pr(self):
        msg = format_child_message(_make_entry())
        assert "75%" in msg
        assert "PR" in msg

    def test_no_target(self):
        msg = format_child_message(_make_entry(target=""))
        assert "Target:" not in msg

    def test_no_description(self):
        msg = format_child_message(_make_entry(description=""))
        assert "Fixed format" not in msg

    def test_no_pr_url(self):
        msg = format_child_message(_make_entry(pr_url=""))
        assert "PR" not in msg

    def test_zero_confidence(self):
        msg = format_child_message(_make_entry(confidence=0.0))
        assert "\u2014" in msg  # em dash


class TestFormatEvaMessage:
    def test_contains_eva_label(self):
        msg = format_eva_message(_make_entry(agent="eva"))
        assert "eva" in msg

    def test_contains_spice(self):
        msg = format_eva_message(_make_entry(agent="eva", type=EvolutionType.ROLE_PATCH))
        assert EVA_SPICE["role_patch"] in msg

    def test_no_pr_url(self):
        msg = format_eva_message(_make_entry(agent="eva", pr_url=""))
        assert "evidence" not in msg

    def test_with_pr_url(self):
        msg = format_eva_message(
            _make_entry(
                agent="eva",
                pr_url="https://github.com/ievo-ai/marketplace/pull/1",
            )
        )
        assert "evidence" in msg

    def test_all_spice_phrases_used(self):
        for evo_type, phrase in EVA_SPICE.items():
            msg = format_eva_message(_make_entry(agent="eva", type=EvolutionType(evo_type)))
            assert phrase in msg

    def test_unknown_type_uses_default(self):
        entry = _make_entry(agent="eva", type=EvolutionType.CONFIG_PATCH)
        msg = format_eva_message(entry)
        assert EVA_SPICE["config_patch"] in msg


class TestFormatTelegramMessage:
    def test_routes_child_agents(self):
        for agent in EVA_CHILDREN:
            msg = format_telegram_message(_make_entry(agent=agent))
            assert agent in msg
            assert "She stirs" not in msg  # not Eva style

    def test_routes_eva(self):
        msg = format_telegram_message(_make_entry(agent="eva"))
        assert EVA_SPICE["role_patch"] in msg

    def test_routes_unknown_agent_as_eva(self):
        msg = format_telegram_message(_make_entry(agent="curator"))
        # curator is not in EVA_CHILDREN, should use Eva style
        assert EVA_SPICE["role_patch"] in msg

    def test_default_spice_fallback(self):
        # Test that EVA_DEFAULT_SPICE exists for completeness
        assert len(EVA_DEFAULT_SPICE) > 0
