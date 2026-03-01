"""Tests for evolution publisher — publishes mutations to ievo.ai."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from eva.core.models import Mutation, MutationType
from eva.github.evolution_publisher import EvolutionPublisher


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


class TestEvolutionPublisherPublish:
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

        import base64

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

        import base64

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
