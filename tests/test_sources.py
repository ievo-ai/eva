"""Tests for signal sources — evolution_logs, github_issues, reviews."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.config import SourceConfig
from eva.core.models import Severity, SignalType
from eva.sources.base import BaseSource
from eva.sources.evolution_logs import EvolutionLogsSource
from eva.sources.github_issues import GitHubIssuesSource, _classify_severity
from eva.sources.reviews import ReviewsSource, _classify_comment

# --- BaseSource ---


class ConcreteSource(BaseSource):
    """Concrete implementation for testing BaseSource."""

    name = "concrete"

    async def poll(self):
        return []

    async def healthcheck(self):
        return True


class TestBaseSource:
    def test_is_enabled_true(self):
        config = SourceConfig(enabled=True)
        source = ConcreteSource(config)
        assert source.is_enabled() is True

    def test_is_enabled_false(self):
        config = SourceConfig(enabled=False)
        source = ConcreteSource(config)
        assert source.is_enabled() is False

    def test_name(self):
        config = SourceConfig()
        source = ConcreteSource(config)
        assert source.name == "concrete"


# --- EvolutionLogsSource ---


class TestEvolutionLogsSource:
    def _make_evo_log(self, agent_dir: Path) -> None:
        """Create a valid EVOLUTION_LOG.md."""
        agent_dir.mkdir(parents=True, exist_ok=True)
        content = """\
# Evolution Log

## EVO-001 — Handle empty input gracefully
- Type: bug
- Trigger: Empty spec submitted by user
- Root cause: No validation on input
- Mutation: Added input check in process()
- Confidence: high
"""
        (agent_dir / "EVOLUTION_LOG.md").write_text(content)

    @pytest.mark.asyncio
    async def test_poll_no_marketplace(self):
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=None)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_nonexistent_marketplace(self, tmp_path):
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=tmp_path / "nonexistent")
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_no_agents_dir(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        marketplace.mkdir()
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_parses_evo_entries(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        agents_dir = marketplace / "agents"
        self._make_evo_log(agents_dir / "spec-writer")

        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)
        signals = await source.poll()

        assert len(signals) == 1
        s = signals[0]
        assert s.type == SignalType.EVOLUTION_LOG
        assert "spec-writer" in s.title
        assert s.severity == Severity.HIGH  # bug → HIGH
        assert "spec-writer" in s.tags
        assert "evo" in s.tags

    @pytest.mark.asyncio
    async def test_poll_deduplicates(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        agents_dir = marketplace / "agents"
        self._make_evo_log(agents_dir / "spec-writer")

        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)

        signals1 = await source.poll()
        signals2 = await source.poll()

        assert len(signals1) == 1
        assert len(signals2) == 0  # Already seen

    @pytest.mark.asyncio
    async def test_poll_skips_non_dirs(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        agents_dir = marketplace / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "README.md").write_text("# Agents")

        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_skips_agent_without_evo_log(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        agents_dir = marketplace / "agents"
        (agents_dir / "coder").mkdir(parents=True)

        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_healthcheck_with_dir(self, tmp_path):
        marketplace = tmp_path / "marketplace"
        marketplace.mkdir()
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=marketplace)
        assert await source.healthcheck() is True

    @pytest.mark.asyncio
    async def test_healthcheck_no_dir(self):
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=None)
        assert await source.healthcheck() is False

    @pytest.mark.asyncio
    async def test_healthcheck_nonexistent_dir(self, tmp_path):
        config = SourceConfig(enabled=True)
        source = EvolutionLogsSource(config, marketplace_dir=tmp_path / "nonexistent")
        assert await source.healthcheck() is False


# --- GitHubIssuesSource ---


class TestGitHubIssuesSource:
    def _mock_httpx_response(self, json_data, status_code=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = json_data
        return mock_resp

    @pytest.mark.asyncio
    async def test_poll_returns_signals(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        issues = [
            {
                "number": 42,
                "title": "Bug in parser",
                "body": "Parser crashes on empty input",
                "labels": [{"name": "bug"}],
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "testuser"},
                "comments": 3,
                "html_url": "https://github.com/ievo-ai/cli/issues/42",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(issues)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config, repos)
            signals = await source.poll()

        assert len(signals) == 1
        s = signals[0]
        assert s.type == SignalType.GITHUB_ISSUE
        assert s.title == "Bug in parser"
        assert s.severity == Severity.HIGH  # bug label
        assert "cli" in s.tags

    @pytest.mark.asyncio
    async def test_poll_skips_pull_requests(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        issues = [
            {
                "number": 1,
                "title": "PR: fix bug",
                "body": "",
                "labels": [],
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "testuser"},
                "comments": 0,
                "html_url": "url",
                "pull_request": {"url": "pr-url"},
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(issues)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config, repos)
            signals = await source.poll()

        assert len(signals) == 0

    @pytest.mark.asyncio
    async def test_poll_handles_api_error(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        import httpx

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config, repos)
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_without_token(self):
        config = SourceConfig(enabled=True, token_env="NONEXISTENT")
        repos = {"cli": "ievo-ai/cli"}

        issues = [
            {
                "number": 1,
                "title": "Public issue",
                "body": "",
                "labels": [],
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "anon"},
                "comments": 0,
                "html_url": "url",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(issues)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client):
            source = GitHubIssuesSource(config, repos)
            signals = await source.poll()

        assert len(signals) == 1

    @pytest.mark.asyncio
    async def test_poll_sets_since_after_signals(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        issues = [
            {
                "number": 1,
                "title": "Issue",
                "body": "",
                "labels": [],
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "user"},
                "comments": 0,
                "html_url": "url",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(issues)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config, repos)
            assert source._since is None
            await source.poll()
            assert source._since is not None

    @pytest.mark.asyncio
    async def test_poll_passes_since_param(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        issues = [
            {
                "number": 1,
                "title": "Issue",
                "body": "",
                "labels": [],
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "user"},
                "comments": 0,
                "html_url": "url",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(issues)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config, repos)
            await source.poll()

            # Second poll should include 'since' in params
            await source.poll()
            second_call = mock_client.get.call_args_list[-1]
            assert "since" in second_call[1]["params"]

    @pytest.mark.asyncio
    async def test_healthcheck_success(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response({}, status_code=200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config)
            result = await source.healthcheck()

        assert result is True

    @pytest.mark.asyncio
    async def test_healthcheck_failure(self):
        import httpx

        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("fail")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config)
            result = await source.healthcheck()

        assert result is False

    @pytest.mark.asyncio
    async def test_healthcheck_non_200(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_resp = MagicMock()
        mock_resp.status_code = 403

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client),
        ):
            source = GitHubIssuesSource(config)
            result = await source.healthcheck()

        assert result is False

    @pytest.mark.asyncio
    async def test_healthcheck_without_token(self):
        """Healthcheck without token should still work (no Authorization header)."""
        config = SourceConfig(enabled=True, token_env="NONEXISTENT")

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response({}, status_code=200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.github_issues.httpx.AsyncClient", return_value=mock_client):
            source = GitHubIssuesSource(config)
            result = await source.healthcheck()

        assert result is True


class TestClassifySeverity:
    def test_bug_label(self):
        assert _classify_severity(["bug"]) == Severity.HIGH

    def test_critical_label(self):
        assert _classify_severity(["critical"]) == Severity.CRITICAL

    def test_enhancement_label(self):
        assert _classify_severity(["enhancement"]) == Severity.LOW

    def test_documentation_label(self):
        assert _classify_severity(["documentation"]) == Severity.INFO

    def test_help_wanted_label(self):
        assert _classify_severity(["help wanted"]) == Severity.MEDIUM

    def test_feature_label(self):
        assert _classify_severity(["feature"]) == Severity.LOW

    def test_no_matching_label(self):
        assert _classify_severity(["unknown"]) == Severity.MEDIUM

    def test_empty_labels(self):
        assert _classify_severity([]) == Severity.MEDIUM

    def test_first_match_wins(self):
        assert _classify_severity(["documentation", "critical"]) == Severity.INFO


# --- ReviewsSource ---


class TestReviewsSource:
    def _mock_httpx_response(self, json_data, status_code=200):
        mock_resp = MagicMock()
        mock_resp.status_code = status_code
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = json_data
        return mock_resp

    @pytest.mark.asyncio
    async def test_poll_returns_signals(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        comments = [
            {
                "id": 100,
                "body": "This function has a bug that needs fixing",
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "reviewer"},
                "html_url": "https://github.com/ievo-ai/cli/pull/1#comment-100",
                "pull_request_url": "https://api.github.com/repos/ievo-ai/cli/pulls/1",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(comments)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config, repos)
            signals = await source.poll()

        assert len(signals) == 1
        s = signals[0]
        assert s.type == SignalType.PR_COMMENT
        assert s.severity == Severity.HIGH  # "bug" in body
        assert "review" in s.tags

    @pytest.mark.asyncio
    async def test_poll_deduplicates(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        comments = [
            {
                "id": 100,
                "body": "Nice code",
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "reviewer"},
                "html_url": "url",
                "pull_request_url": "pr-url",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(comments)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config, repos)
            signals1 = await source.poll()
            signals2 = await source.poll()

        assert len(signals1) == 1
        assert len(signals2) == 0

    @pytest.mark.asyncio
    async def test_poll_handles_api_error(self):
        import httpx

        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")
        repos = {"cli": "ievo-ai/cli"}

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("fail")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config, repos)
            signals = await source.poll()

        assert signals == []

    @pytest.mark.asyncio
    async def test_poll_without_token(self):
        config = SourceConfig(enabled=True, token_env="NONEXISTENT")
        repos = {"cli": "ievo-ai/cli"}

        comments = [
            {
                "id": 200,
                "body": "Suggestion: improve docs",
                "updated_at": "2026-03-01T10:00:00Z",
                "user": {"login": "user"},
                "html_url": "url",
                "pull_request_url": "pr-url",
            }
        ]

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response(comments)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client):
            source = ReviewsSource(config, repos)
            signals = await source.poll()

        assert len(signals) == 1

    @pytest.mark.asyncio
    async def test_healthcheck_success(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response({}, status_code=200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config)
            result = await source.healthcheck()

        assert result is True

    @pytest.mark.asyncio
    async def test_healthcheck_failure(self):
        import httpx

        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("fail")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config)
            result = await source.healthcheck()

        assert result is False

    @pytest.mark.asyncio
    async def test_healthcheck_non_200(self):
        config = SourceConfig(enabled=True, token_env="TEST_TOKEN")

        mock_resp = MagicMock()
        mock_resp.status_code = 403

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_resp
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with (
            patch.dict("os.environ", {"TEST_TOKEN": "token"}),
            patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client),
        ):
            source = ReviewsSource(config)
            result = await source.healthcheck()

        assert result is False

    @pytest.mark.asyncio
    async def test_healthcheck_without_token(self):
        """Healthcheck without token should still work (no Authorization header)."""
        config = SourceConfig(enabled=True, token_env="NONEXISTENT")

        mock_client = AsyncMock()
        mock_client.get.return_value = self._mock_httpx_response({}, status_code=200)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.reviews.httpx.AsyncClient", return_value=mock_client):
            source = ReviewsSource(config)
            result = await source.healthcheck()

        assert result is True


class TestClassifyComment:
    def test_critical_words(self):
        assert _classify_comment("This is broken") == Severity.CRITICAL
        assert _classify_comment("App crashes on load") == Severity.CRITICAL
        assert _classify_comment("Fatal error") == Severity.CRITICAL
        assert _classify_comment("Critical issue") == Severity.CRITICAL
        assert _classify_comment("This is a blocker") == Severity.CRITICAL

    def test_high_words(self):
        assert _classify_comment("There's a bug here") == Severity.HIGH
        assert _classify_comment("Got an error") == Severity.HIGH
        assert _classify_comment("This is wrong") == Severity.HIGH
        assert _classify_comment("Incorrect output") == Severity.HIGH
        assert _classify_comment("Tests fail") == Severity.HIGH

    def test_low_words(self):
        assert _classify_comment("You should rename this") == Severity.LOW
        assert _classify_comment("Could be better") == Severity.LOW
        assert _classify_comment("Improve naming") == Severity.LOW
        assert _classify_comment("I suggest using X") == Severity.LOW
        assert _classify_comment("Nitpick: spacing") == Severity.LOW

    def test_default_medium(self):
        assert _classify_comment("LGTM") == Severity.MEDIUM
        assert _classify_comment("") == Severity.MEDIUM
