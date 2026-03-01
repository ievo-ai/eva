"""Tests for evolution publisher — publishes mutations to ievo.ai."""

import base64
import json
from unittest.mock import AsyncMock, patch

import pytest

from eva.core.models import EvolutionEntry, EvolutionType, Mutation, MutationType
from eva.github.evolution_publisher import EvolutionPublisher
from eva.telegram.client import TelegramResult


def _make_mutation(**kwargs) -> Mutation:
    defaults = {
        "id": "mut-0001",
        "type": MutationType.ROLE_PATCH,
        "title": "Fix issue",
        "description": "Fix description",
        "target_repo": "ievo-ai/marketplace",
        "target_path": "agents/spec-writer/ROLE.md",
        "diff": "# patch",
        "confidence": 0.7,
        "pr_url": "https://github.com/ievo-ai/marketplace/pull/1",
    }
    defaults.update(kwargs)
    return Mutation(**defaults)


def _make_entry(**kwargs) -> EvolutionEntry:
    defaults = {
        "title": "Test evolution",
        "agent": "spec-writer",
        "type": EvolutionType.ROLE_PATCH,
        "target": "agents/spec-writer/ROLE.md",
        "description": "Fixed format validation.",
        "confidence": 0.75,
        "pr_url": "https://github.com/ievo-ai/marketplace/pull/5",
    }
    defaults.update(kwargs)
    return EvolutionEntry(**defaults)


class TestEvolutionPublisherInit:
    def test_raises_without_token(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="No token"),
        ):
            EvolutionPublisher(token=None)

    def test_accepts_explicit_token(self):
        publisher = EvolutionPublisher(token="test-token")
        assert publisher._token == "test-token"

    def test_reads_env_token(self):
        with patch.dict("os.environ", {"EVA_GITHUB_TOKEN": "env-token"}):
            publisher = EvolutionPublisher()
        assert publisher._token == "env-token"

    def test_accepts_telegram_client(self):
        with patch.dict(
            "os.environ",
            {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_COMMUNITY_CHAT": "-100"},
        ):
            tg = AsyncMock()
            publisher = EvolutionPublisher(token="test", telegram=tg)
        assert publisher._telegram is tg

    def test_no_telegram_by_default(self):
        publisher = EvolutionPublisher(token="test")
        assert publisher._telegram is None


class TestPublishMutations:
    @pytest.mark.asyncio
    async def test_skips_mutations_without_pr_url(self):
        publisher = EvolutionPublisher(token="test")
        count = await publisher.publish([_make_mutation(pr_url="")])
        assert count == 0

    @pytest.mark.asyncio
    async def test_publishes_successful_mutations(self):
        publisher = EvolutionPublisher(token="test")

        existing_evolutions = [
            {"id": "EVO-001", "date": "2026-02-28", "title": "First"},
        ]
        existing_content = json.dumps(existing_evolutions).encode()

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(
            return_value={"content": base64.b64encode(existing_content).decode()}
        )
        mock_client.create_or_update_file = AsyncMock()

        count = await publisher.publish([_make_mutation()])
        assert count == 1
        mock_client.create_or_update_file.assert_called_once()

        # Verify the content written includes the new entry
        call_kwargs = mock_client.create_or_update_file.call_args[1]
        written = json.loads(call_kwargs["content"])
        assert len(written) == 2
        assert written[1]["id"] == "EVO-002"

    @pytest.mark.asyncio
    async def test_handles_empty_existing_file(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        count = await publisher.publish([_make_mutation()])
        assert count == 1

        call_kwargs = mock_client.create_or_update_file.call_args[1]
        written = json.loads(call_kwargs["content"])
        assert written[0]["id"] == "EVO-001"

    @pytest.mark.asyncio
    async def test_handles_malformed_evo_ids(self):
        publisher = EvolutionPublisher(token="test")

        existing = [
            {"id": "EVO-bad", "title": "Malformed"},
            {"id": "not-evo", "title": "No prefix"},
            {"id": "EVO-005", "title": "Valid"},
        ]
        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(
            return_value={"content": base64.b64encode(json.dumps(existing).encode()).decode()}
        )
        mock_client.create_or_update_file = AsyncMock()

        count = await publisher.publish([_make_mutation()])
        assert count == 1

        call_kwargs = mock_client.create_or_update_file.call_args[1]
        written = json.loads(call_kwargs["content"])
        assert written[-1]["id"] == "EVO-006"

    @pytest.mark.asyncio
    async def test_handles_publish_exception(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("API error"))

        count = await publisher.publish([_make_mutation()])
        assert count == 0


class TestPublishEntries:
    @pytest.mark.asyncio
    async def test_publishes_entries(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        entry = _make_entry()
        count = await publisher.publish_entries([entry])
        assert count == 1
        assert entry.id == "EVO-001"
        assert entry.date != ""

    @pytest.mark.asyncio
    async def test_preserves_existing_id_and_date(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        entry = _make_entry(id="EVO-099", date="2026-01-01")
        count = await publisher.publish_entries([entry])
        assert count == 1
        assert entry.id == "EVO-099"
        assert entry.date == "2026-01-01"

    @pytest.mark.asyncio
    async def test_empty_entries_returns_zero(self):
        publisher = EvolutionPublisher(token="test")
        count = await publisher.publish_entries([])
        assert count == 0

    @pytest.mark.asyncio
    async def test_publish_entries_exception(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("fail"))

        count = await publisher.publish_entries([_make_entry()])
        assert count == 0


class TestNotifyTelegram:
    @pytest.mark.asyncio
    async def test_sends_to_telegram(self):
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=True, message_id=42)
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        count = await publisher.publish_entries([_make_entry()])
        assert count == 1
        mock_tg.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_telegram_error_does_not_fail_publish(self):
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=False, error="Chat not found")
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        count = await publisher.publish_entries([_make_entry()])
        assert count == 1

    @pytest.mark.asyncio
    async def test_no_telegram_skips_notification(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        # Should not raise — just skips Telegram
        count = await publisher.publish_entries([_make_entry()])
        assert count == 1

    @pytest.mark.asyncio
    async def test_sends_to_evolutions_topic(self):
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=True, message_id=55)

        with patch.dict("os.environ", {"TELEGRAM_EVOLUTIONS_TOPIC": "10"}):
            publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        await publisher.publish_entries([_make_entry()])
        call_kwargs = mock_tg.send_message.call_args[1]
        assert call_kwargs["message_thread_id"] == 10

    @pytest.mark.asyncio
    async def test_no_topic_env_sends_without_thread(self):
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=True, message_id=56)

        with patch.dict("os.environ", {}, clear=False):
            publisher = EvolutionPublisher(token="test", telegram=mock_tg)
            publisher._evolutions_topic = None

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        await publisher.publish_entries([_make_entry()])
        call_kwargs = mock_tg.send_message.call_args[1]
        assert call_kwargs["message_thread_id"] is None
