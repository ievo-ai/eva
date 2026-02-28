"""Tests for GitHub integration (client, PR creator, evolution publisher)."""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.models import Mutation, MutationType
from eva.github.client import GitHubClient, PRResult
from eva.github.pr_creator import PRCreator, PRCreationResult, _apply_mutation, _confidence_note
from eva.github.evolution_publisher import EvolutionPublisher


# --- GitHubClient ---

class TestGitHubClient:
    def test_init_requires_token(self):
        with pytest.raises(ValueError, match="token is required"):
            GitHubClient("")

    def test_init_sets_headers(self):
        client = GitHubClient("test-token-123")
        assert client._headers["Authorization"] == "token test-token-123"
        assert "Accept" in client._headers


# --- PRCreator ---

class TestPRCreator:
    def test_init_requires_token(self):
        with pytest.raises(ValueError, match="No GitHub token"):
            with patch.dict("os.environ", {}, clear=True):
                PRCreator(token="")

    def test_init_with_explicit_token(self):
        creator = PRCreator(token="my-token")
        assert creator._token == "my-token"

    @pytest.mark.asyncio
    async def test_create_pr_success(self):
        mutation = _make_mutation()

        creator = PRCreator(token="test-token")
        creator._client = AsyncMock()
        creator._client.get_default_branch = AsyncMock(return_value="main")
        creator._client.get_ref_sha = AsyncMock(return_value="abc123def456")
        creator._client.create_branch = AsyncMock()
        creator._client.get_file_content = AsyncMock(return_value=None)
        creator._client.create_or_update_file = AsyncMock(return_value="commit-sha")
        creator._client.create_pull_request = AsyncMock(return_value=PRResult(
            pr_url="https://github.com/ievo-ai/marketplace/pull/1",
            pr_number=1,
            branch="eva/mut-0001",
            repo="ievo-ai/marketplace",
        ))
        creator._client.add_labels = AsyncMock()

        result = await creator.create_pr(mutation)

        assert result.success
        assert result.pr_url == "https://github.com/ievo-ai/marketplace/pull/1"
        assert mutation.pr_url == "https://github.com/ievo-ai/marketplace/pull/1"

    @pytest.mark.asyncio
    async def test_create_pr_failure(self):
        mutation = _make_mutation()

        creator = PRCreator(token="test-token")
        creator._client = AsyncMock()
        creator._client.get_default_branch = AsyncMock(side_effect=Exception("API error"))

        result = await creator.create_pr(mutation)

        assert not result.success
        assert "API error" in result.error

    @pytest.mark.asyncio
    async def test_create_all(self):
        mutations = [_make_mutation(id="mut-0001"), _make_mutation(id="mut-0002")]

        creator = PRCreator(token="test-token")
        creator.create_pr = AsyncMock(side_effect=[
            PRCreationResult(mutation_id="mut-0001", success=True, pr_url="https://url/1"),
            PRCreationResult(mutation_id="mut-0002", success=True, pr_url="https://url/2"),
        ])

        results = await creator.create_all(mutations)
        assert len(results) == 2
        assert all(r.success for r in results)


# --- _apply_mutation ---

class TestApplyMutation:
    def test_appends_to_existing(self):
        mutation = _make_mutation()
        result = _apply_mutation("# Existing content\n\nSome rules.", mutation)

        assert "Existing content" in result
        assert "Some rules." in result
        assert "Eva-generated" in result

    def test_handles_empty_file(self):
        mutation = _make_mutation()
        result = _apply_mutation("", mutation)
        assert "Eva-generated" in result


# --- _confidence_note ---

class TestConfidenceNote:
    def test_high(self):
        assert "High confidence" in _confidence_note(0.9)

    def test_medium(self):
        assert "Medium confidence" in _confidence_note(0.6)

    def test_low(self):
        assert "Low confidence" in _confidence_note(0.3)


# --- EvolutionPublisher ---

class TestEvolutionPublisher:
    def test_init_requires_token(self):
        with pytest.raises(ValueError):
            with patch.dict("os.environ", {}, clear=True):
                EvolutionPublisher(token="")

    @pytest.mark.asyncio
    async def test_publish_skips_without_pr_url(self):
        publisher = EvolutionPublisher(token="test-token")
        mutation = _make_mutation()
        mutation.pr_url = ""

        count = await publisher.publish([mutation])
        assert count == 0

    @pytest.mark.asyncio
    async def test_publish_success(self):
        publisher = EvolutionPublisher(token="test-token")
        publisher._client = AsyncMock()

        import base64
        existing = json.dumps([{"id": "EVO-002", "date": "2026-02-28", "title": "test"}])
        encoded = base64.b64encode(existing.encode()).decode()
        publisher._client.get_file_content = AsyncMock(return_value={
            "content": encoded,
            "sha": "abc",
        })
        publisher._client.create_or_update_file = AsyncMock(return_value="sha")

        mutation = _make_mutation()
        mutation.pr_url = "https://github.com/ievo-ai/marketplace/pull/1"

        count = await publisher.publish([mutation])
        assert count == 1

        # Verify the content written contains EVO-003
        call_args = publisher._client.create_or_update_file.call_args
        content = call_args.kwargs.get("content") or call_args[1].get("content")
        assert "EVO-003" in content


# --- Helpers ---

def _make_mutation(id: str = "mut-0001") -> Mutation:
    return Mutation(
        id=id,
        type=MutationType.ROLE_PATCH,
        title="Fix recurring issue in spec-writer",
        description="Pattern detected: spec-writer fails on empty input.",
        target_repo="ievo-ai/marketplace",
        target_path="agents/spec-writer/ROLE.md",
        diff=(
            "# Eva-generated patch for spec-writer/ROLE.md\n"
            "# Date: 2026-02-28\n"
            "# Pattern: freq:spec-writer-fails\n"
            "# Confidence: 70%\n"
            "#\n"
            "# Add to Rules section:\n"
            "#\n"
            "# ## Eva Rule (auto-generated)\n"
            "# Based on 3 occurrences of: spec-writer fails\n"
            "# Validate input is not empty before processing.\n"
        ),
        pattern_id="freq:spec-writer-fails",
        confidence=0.7,
    )
