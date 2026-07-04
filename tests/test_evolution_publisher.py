"""Tests for evolution publisher — publishes mutations to ievo.ai."""

import base64
import json
from unittest.mock import AsyncMock, patch

import pytest

from eva.core.models import EvolutionEntry, EvolutionType, Mutation, MutationType
from eva.github.evolution_publisher import EvolutionPublisher, EvolutionPublishError
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
    async def test_publish_exception_raises(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("API error"))

        with pytest.raises(EvolutionPublishError, match="feed: API error"):
            await publisher.publish([_make_mutation()])


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
    async def test_publish_entries_exception_raises(self):
        publisher = EvolutionPublisher(token="test")

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("fail"))

        with pytest.raises(EvolutionPublishError, match="feed: fail"):
            await publisher.publish_entries([_make_entry()])

    @pytest.mark.asyncio
    async def test_feed_failure_still_attempts_telegram(self):
        """eva#160: a feed failure must not silence Telegram — both channels
        are attempted independently, and the aggregate error reports the feed."""
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=True, message_id=7)
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("409 Conflict"))

        with pytest.raises(EvolutionPublishError, match="feed: 409 Conflict"):
            await publisher.publish_entries([_make_entry()])
        mock_tg.send_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_both_channels_fail_reports_both(self):
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=False, error="Chat gone")
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(side_effect=RuntimeError("409 Conflict"))

        with pytest.raises(
            EvolutionPublishError, match="feed: 409 Conflict; telegram: .*Chat gone"
        ):
            await publisher.publish_entries([_make_entry()])


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
    async def test_telegram_error_raises_after_feed_success(self):
        """eva#160: a Telegram failure fails the publish even when the feed
        write succeeded — the run must show red if EITHER channel failed."""
        mock_tg = AsyncMock()
        mock_tg.send_message.return_value = TelegramResult(success=False, error="Chat not found")
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        with pytest.raises(EvolutionPublishError, match="telegram: .*Chat not found"):
            await publisher.publish_entries([_make_entry()])
        # Feed write still happened — channels are independent.
        mock_client.create_or_update_file.assert_called_once()

    @pytest.mark.asyncio
    async def test_telegram_send_exception_recorded_per_entry(self):
        """An exception in one send is recorded and the loop continues."""
        mock_tg = AsyncMock()
        mock_tg.send_message.side_effect = [
            RuntimeError("network down"),
            TelegramResult(success=True, message_id=8),
        ]
        publisher = EvolutionPublisher(token="test", telegram=mock_tg)

        mock_client = publisher._client
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        with pytest.raises(EvolutionPublishError, match="telegram: .*network down"):
            await publisher.publish_entries([_make_entry(), _make_entry(title="Second")])
        assert mock_tg.send_message.call_count == 2

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
