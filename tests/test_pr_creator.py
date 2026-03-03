"""Tests for PR creator — turns mutations into GitHub PRs."""

import base64
from unittest.mock import AsyncMock, patch

import pytest

from eva.core.models import Mutation, MutationType
from eva.github.pr_creator import (
    PRCreationResult,
    PRCreator,
    _apply_mutation,
    _confidence_note,
    _format_fitness_section,
)


def _make_mutation(**kwargs) -> Mutation:
    defaults = {
        "id": "mut-0001",
        "type": MutationType.ROLE_PATCH,
        "title": "Fix issue",
        "description": "Fix description",
        "target_repo": "ievo-ai/marketplace",
        "target_path": "agents/spec-writer/ROLE.md",
        "diff": "# patch\nNew rule here",
        "pattern_id": "freq:test",
        "confidence": 0.7,
    }
    defaults.update(kwargs)
    return Mutation(**defaults)


class TestPRCreatorInit:
    def test_raises_without_token(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="No GitHub token"),
        ):
            PRCreator(token=None)

    def test_accepts_explicit_token(self):
        creator = PRCreator(token="test-token")
        assert creator._token == "test-token"


class TestConfidenceNote:
    def test_high(self):
        assert "safe" in _confidence_note(0.9).lower()

    def test_medium(self):
        assert "carefully" in _confidence_note(0.6).lower()

    def test_low(self):
        assert "manual" in _confidence_note(0.3).lower()


class TestApplyMutation:
    def test_appends_content(self):
        current = "# ROLE.md\n\nExisting content."
        mutation = _make_mutation(diff="# comment line\nNew rule added")
        result = _apply_mutation(current, mutation)
        assert "Existing content." in result
        assert "comment line" in result
        assert "New rule added" in result

    def test_converts_comment_lines(self):
        mutation = _make_mutation(diff="# This is a comment\nNot a comment")
        result = _apply_mutation("existing", mutation)
        assert "This is a comment" in result
        assert "Not a comment" in result


class TestPRCreationResult:
    def test_defaults(self):
        r = PRCreationResult(mutation_id="mut-001", success=True)
        assert r.pr_url == ""
        assert r.error == ""

    def test_with_values(self):
        r = PRCreationResult(
            mutation_id="mut-001",
            success=False,
            error="fail",
        )
        assert r.error == "fail"


class TestPRCreatorCreatePR:
    @pytest.mark.asyncio
    async def test_create_pr_success_with_existing_file(self):
        creator = PRCreator(token="test")
        mock_client = creator._client

        existing_content = base64.b64encode(b"# Old content").decode()

        mock_client.get_default_branch = AsyncMock(return_value="main")
        mock_client.get_ref_sha = AsyncMock(return_value="sha123")
        mock_client.create_branch = AsyncMock()
        mock_client.get_file_content = AsyncMock(
            return_value={"content": existing_content, "sha": "file-sha"}
        )
        mock_client.create_or_update_file = AsyncMock()

        from eva.github.client import PRResult

        mock_client.create_pull_request = AsyncMock(
            return_value=PRResult(
                pr_url="https://github.com/test/pull/1",
                pr_number=1,
                branch="eva/mut-0001",
                repo="ievo-ai/marketplace",
            )
        )
        mock_client.add_labels = AsyncMock()

        mutation = _make_mutation()
        result = await creator.create_pr(mutation)

        assert result.success is True
        assert result.pr_url == "https://github.com/test/pull/1"
        assert mutation.pr_url == "https://github.com/test/pull/1"

    @pytest.mark.asyncio
    async def test_create_pr_success_new_file(self):
        creator = PRCreator(token="test")
        mock_client = creator._client

        mock_client.get_default_branch = AsyncMock(return_value="main")
        mock_client.get_ref_sha = AsyncMock(return_value="sha123")
        mock_client.create_branch = AsyncMock()
        mock_client.get_file_content = AsyncMock(return_value=None)
        mock_client.create_or_update_file = AsyncMock()

        from eva.github.client import PRResult

        mock_client.create_pull_request = AsyncMock(
            return_value=PRResult(
                pr_url="https://github.com/test/pull/2",
                pr_number=2,
                branch="eva/mut-0001",
                repo="ievo-ai/marketplace",
            )
        )
        mock_client.add_labels = AsyncMock()

        mutation = _make_mutation()
        result = await creator.create_pr(mutation)

        assert result.success is True
        # When file doesn't exist, raw diff is used
        call_kwargs = mock_client.create_or_update_file.call_args[1]
        assert call_kwargs["content"] == mutation.diff

    @pytest.mark.asyncio
    async def test_create_pr_failure(self):
        creator = PRCreator(token="test")
        mock_client = creator._client
        mock_client.get_default_branch = AsyncMock(side_effect=RuntimeError("API error"))

        result = await creator.create_pr(_make_mutation())

        assert result.success is False
        assert "API error" in result.error

    @pytest.mark.asyncio
    async def test_create_pr_with_fitness_delta(self):
        """PR body includes fitness delta section when metadata has it."""
        creator = PRCreator(token="test")
        mock_client = creator._client

        existing_content = base64.b64encode(b"# Old content").decode()

        mock_client.get_default_branch = AsyncMock(return_value="main")
        mock_client.get_ref_sha = AsyncMock(return_value="sha123")
        mock_client.create_branch = AsyncMock()
        mock_client.get_file_content = AsyncMock(
            return_value={"content": existing_content, "sha": "file-sha"}
        )
        mock_client.create_or_update_file = AsyncMock()

        from eva.github.client import PRResult

        mock_client.create_pull_request = AsyncMock(
            return_value=PRResult(
                pr_url="https://github.com/test/pull/3",
                pr_number=3,
                branch="eva/mut-0001",
                repo="ievo-ai/marketplace",
            )
        )
        mock_client.add_labels = AsyncMock()

        mutation = _make_mutation()
        mutation.metadata["fitness_delta"] = {
            "overall_delta": 5.2,
            "improved": True,
            "before_score": 60.0,
            "after_score": 65.2,
            "per_dimension": {"testability": 3.0, "atomicity": 2.2},
        }
        result = await creator.create_pr(mutation)

        assert result.success is True
        # Verify the PR body included fitness data
        pr_body = mock_client.create_pull_request.call_args[1]["body"]
        assert "Benchmark Fitness Delta" in pr_body
        assert "65.2" in pr_body

    @pytest.mark.asyncio
    async def test_create_all(self):
        creator = PRCreator(token="test")
        mock_client = creator._client
        mock_client.get_default_branch = AsyncMock(side_effect=RuntimeError("No access"))

        results = await creator.create_all(
            [_make_mutation(id="mut-001"), _make_mutation(id="mut-002")]
        )

        assert len(results) == 2
        assert all(not r.success for r in results)


class TestFormatFitnessSection:
    def test_improved_mutation(self):
        fitness_data = {
            "overall_delta": 5.2,
            "improved": True,
            "before_score": 60.0,
            "after_score": 65.2,
            "per_dimension": {"testability": 3.0, "atomicity": 2.2},
        }
        result = _format_fitness_section(fitness_data)
        assert "Benchmark Fitness Delta" in result
        assert "60.0" in result
        assert "65.2" in result
        assert "+5.2" in result
        assert "testability" in result
        assert "atomicity" in result

    def test_degraded_mutation(self):
        fitness_data = {
            "overall_delta": -2.5,
            "improved": False,
            "before_score": 70.0,
            "after_score": 67.5,
        }
        result = _format_fitness_section(fitness_data)
        assert "-2.5" in result

    def test_no_change(self):
        fitness_data = {
            "overall_delta": 0,
            "improved": False,
            "before_score": 50.0,
            "after_score": 50.0,
        }
        result = _format_fitness_section(fitness_data)
        assert "=0" in result

    def test_per_dimension_with_negative(self):
        fitness_data = {
            "overall_delta": 1.0,
            "improved": True,
            "before_score": 50.0,
            "after_score": 51.0,
            "per_dimension": {"testability": 5.0, "completeness": -4.0},
        }
        result = _format_fitness_section(fitness_data)
        assert "+5.0" in result
        assert "-4.0" in result

    def test_no_per_dimension(self):
        fitness_data = {
            "overall_delta": 3.0,
            "improved": True,
            "before_score": 50.0,
            "after_score": 53.0,
        }
        result = _format_fitness_section(fitness_data)
        assert "Overall" in result
        # No dimension rows
        lines = result.strip().split("\n")
        # Header + separator + overall row = 4 lines min
        assert len(lines) >= 4
