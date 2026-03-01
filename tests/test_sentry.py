"""Tests for Sentry source."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.config import SourceConfig
from eva.core.models import Severity, SignalType
from eva.sources.sentry import SentrySource, _parse_timestamp

# --- Config ---


class TestSentryConfig:
    def test_multi_project_config(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={
                "org": "ievo",
                "projects": {
                    "cli": "ievo-cli",
                    "marketplace": "ievo-marketplace",
                },
            },
        )
        source = SentrySource(config)
        assert source._org == "ievo"
        assert source._projects == {"cli": "ievo-cli", "marketplace": "ievo-marketplace"}

    def test_legacy_single_project(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={"org": "ievo", "project": "ievo-cli"},
        )
        source = SentrySource(config)
        assert source._projects == {"default": "ievo-cli"}

    def test_no_projects(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={"org": "ievo"},
        )
        source = SentrySource(config)
        assert source._projects == {}


# --- Poll ---


class TestSentryPoll:
    @pytest.mark.asyncio
    async def test_returns_empty_without_token(self):
        config = SourceConfig(
            enabled=True,
            token_env="NONEXISTENT_TOKEN",
            extra={"org": "ievo", "projects": {"cli": "ievo-cli"}},
        )
        source = SentrySource(config)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_returns_empty_without_org(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={"projects": {"cli": "ievo-cli"}},
        )
        with patch.dict("os.environ", {"EVA_SENTRY_TOKEN": "test-token"}):
            source = SentrySource(config)
        signals = await source.poll()
        assert signals == []

    @pytest.mark.asyncio
    async def test_polls_multiple_projects(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={
                "org": "ievo",
                "projects": {
                    "cli": "ievo-cli",
                    "sdk": "ievo-sdk",
                },
            },
        )

        mock_issues = [
            {
                "id": "12345",
                "title": "TypeError in parse_args",
                "level": "error",
                "metadata": {"value": "NoneType has no attribute 'split'"},
                "culprit": "cli.main.parse_args",
                "platform": "python",
                "count": 5,
                "lastSeen": "2026-02-28T10:00:00Z",
                "firstSeen": "2026-02-27T08:00:00Z",
                "permalink": "https://sentry.io/ievo/ievo-cli/issues/12345/",
            },
        ]

        with patch.dict("os.environ", {"EVA_SENTRY_TOKEN": "test-token"}):
            source = SentrySource(config)

        # Mock httpx
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()
        mock_response.json.return_value = mock_issues

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.sentry.httpx.AsyncClient", return_value=mock_client):
            signals = await source.poll()

        # 2 projects × 1 issue each = 2 signals
        assert len(signals) == 2

        # Check first signal
        s = signals[0]
        assert s.type == SignalType.SENTRY_ERROR
        assert s.title == "TypeError in parse_args"
        assert s.severity == Severity.HIGH
        assert "Culprit: cli.main.parse_args" in s.body
        assert "Seen 5 times" in s.body
        assert s.metadata["project_label"] == "cli"
        assert s.metadata["org"] == "ievo"
        assert "sentry" in s.tags

    @pytest.mark.asyncio
    async def test_handles_api_error_gracefully(self):
        config = SourceConfig(
            enabled=True,
            token_env="EVA_SENTRY_TOKEN",
            extra={
                "org": "ievo",
                "projects": {"cli": "ievo-cli"},
            },
        )

        with patch.dict("os.environ", {"EVA_SENTRY_TOKEN": "test-token"}):
            source = SentrySource(config)

        import httpx

        mock_client = AsyncMock()
        mock_client.get.side_effect = httpx.HTTPError("Connection refused")
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.sources.sentry.httpx.AsyncClient", return_value=mock_client):
            signals = await source.poll()

        assert signals == []


# --- Helpers ---


class TestParseTimestamp:
    def test_valid_iso(self):
        dt = _parse_timestamp("2026-02-28T10:00:00Z")
        assert dt.year == 2026
        assert dt.month == 2

    def test_empty_string(self):
        dt = _parse_timestamp("")
        assert dt is not None

    def test_invalid_string(self):
        dt = _parse_timestamp("not-a-date")
        assert dt is not None


# --- Healthcheck ---


class TestSentryHealthcheck:
    @pytest.mark.asyncio
    async def test_healthcheck_no_token(self):
        config = SourceConfig(
            enabled=True,
            token_env="NONEXISTENT",
            extra={"org": "ievo"},
        )
        source = SentrySource(config)
        result = await source.healthcheck()
        assert result is False
