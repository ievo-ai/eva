"""Tests for Eva pipeline — the main observe → analyze → mutate loop."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.core.config import EvaConfig
from eva.core.models import (
    Mutation,
    MutationType,
    Pattern,
    Severity,
    Signal,
    SignalType,
)
from eva.github.pr_creator import PRCreationResult
from eva.pipeline import EvaPipeline, EvaRun, _severity_color


def _make_signal(id: str = "sig-1", **kwargs) -> Signal:
    defaults = {
        "id": id,
        "type": SignalType.GITHUB_ISSUE,
        "source": "test",
        "title": "Test signal",
        "body": "Test body",
        "severity": Severity.MEDIUM,
    }
    defaults.update(kwargs)
    return Signal(**defaults)


def _make_pattern(id: str = "freq:test", **kwargs) -> Pattern:
    defaults = {
        "id": id,
        "title": "Test pattern",
        "description": "Test desc",
        "signal_ids": ["sig-1"],
        "frequency": 2,
        "severity": Severity.MEDIUM,
        "confidence": 0.6,
    }
    defaults.update(kwargs)
    return Pattern(**defaults)


def _make_mutation(id: str = "mut-0001", **kwargs) -> Mutation:
    defaults = {
        "id": id,
        "type": MutationType.ROLE_PATCH,
        "title": "Fix issue",
        "description": "Fix desc",
        "target_repo": "ievo-ai/marketplace",
        "target_path": "agents/spec-writer/ROLE.md",
        "diff": "# patch",
        "pattern_id": "freq:test",
        "confidence": 0.7,
    }
    defaults.update(kwargs)
    return Mutation(**defaults)


class TestEvaRun:
    def test_defaults(self):
        run = EvaRun()
        assert run.signals == []
        assert run.patterns == []
        assert run.mutations == []
        assert run.pr_results == []


class TestEvaPipelineInit:
    def test_creates_sources_from_config(self):
        config = EvaConfig()
        config.sentry.enabled = True
        config.github_issues.enabled = True
        config.reviews.enabled = True
        config.evolution_logs.enabled = True

        pipeline = EvaPipeline(config)
        assert len(pipeline.sources) == 4

    def test_no_sources_when_all_disabled(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)
        assert len(pipeline.sources) == 0

    def test_marketplace_dir_passed_to_evo_logs(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = True

        pipeline = EvaPipeline(config, marketplace_dir=Path("/tmp/marketplace"))
        assert len(pipeline.sources) == 1
        assert pipeline.sources[0].name == "evolution_logs"


class TestEvaPipelineRun:
    @pytest.mark.asyncio
    async def test_empty_run_no_sources(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)
        result = await pipeline.run()

        assert result.signals == []
        assert result.patterns == []
        assert result.mutations == []

    @pytest.mark.asyncio
    async def test_run_with_signals_but_no_patterns(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        # Detector returns no patterns for single signal
        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = []

        result = await pipeline.run()
        assert len(result.signals) == 1
        assert result.patterns == []

    @pytest.mark.asyncio
    async def test_run_full_cycle_dry_run(self):
        config = EvaConfig()
        config.dry_run = True
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [_make_mutation()]

        result = await pipeline.run()
        assert len(result.signals) == 1
        assert len(result.patterns) == 1
        assert len(result.mutations) == 1
        assert result.pr_results == []  # Dry run — no PRs

    @pytest.mark.asyncio
    async def test_run_live_mode_creates_prs(self):
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        mutation = _make_mutation()
        mutation.pr_url = "https://github.com/test/pull/1"
        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [mutation]

        mock_pr_creator = MagicMock()
        mock_pr_creator.create_all = AsyncMock(
            return_value=[
                PRCreationResult(mutation_id="mut-0001", success=True, pr_url="https://url/1")
            ]
        )

        mock_publisher = MagicMock()
        mock_publisher.publish = AsyncMock(return_value=1)

        with (
            patch("eva.pipeline.PRCreator", return_value=mock_pr_creator),
            patch("eva.pipeline.EvolutionPublisher", return_value=mock_publisher),
        ):
            result = await pipeline.run()

        assert len(result.pr_results) == 1
        assert result.pr_results[0].success

    @pytest.mark.asyncio
    async def test_run_live_mode_handles_pr_creation_error(self):
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [_make_mutation()]

        with patch("eva.pipeline.PRCreator", side_effect=ValueError("No token")):
            result = await pipeline.run()

        assert result.pr_results == []

    @pytest.mark.asyncio
    async def test_run_live_mode_no_successful_prs_skips_publish(self):
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [_make_mutation()]

        mock_pr_creator = MagicMock()
        mock_pr_creator.create_all = AsyncMock(
            return_value=[PRCreationResult(mutation_id="mut-0001", success=False, error="fail")]
        )

        with patch("eva.pipeline.PRCreator", return_value=mock_pr_creator):
            result = await pipeline.run()

        assert len(result.pr_results) == 1
        assert not result.pr_results[0].success

    @pytest.mark.asyncio
    async def test_run_live_publisher_exception(self):
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        mutation = _make_mutation()
        mutation.pr_url = "https://github.com/test/pull/1"
        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [mutation]

        mock_pr_creator = MagicMock()
        mock_pr_creator.create_all = AsyncMock(
            return_value=[
                PRCreationResult(mutation_id="mut-0001", success=True, pr_url="https://url/1")
            ]
        )

        with (
            patch("eva.pipeline.PRCreator", return_value=mock_pr_creator),
            patch("eva.pipeline.EvolutionPublisher", side_effect=Exception("Publish error")),
        ):
            result = await pipeline.run()

        assert len(result.pr_results) == 1

    @pytest.mark.asyncio
    async def test_run_live_no_mutations(self):
        """Live mode with patterns but no mutations should skip PR creation."""
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = []

        result = await pipeline.run()
        assert result.mutations == []
        assert result.pr_results == []

    @pytest.mark.asyncio
    async def test_run_live_publisher_returns_zero(self):
        """Publisher returning 0 should not print success count."""
        config = EvaConfig()
        config.dry_run = False
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "test"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(return_value=[_make_signal()])
        pipeline.sources = [mock_source]

        pipeline.detector = MagicMock()
        pipeline.detector.ingest.return_value = [_make_pattern()]

        mutation = _make_mutation()
        mutation.pr_url = "https://github.com/test/pull/1"
        pipeline.mutator = MagicMock()
        pipeline.mutator.generate.return_value = [mutation]

        mock_pr_creator = MagicMock()
        mock_pr_creator.create_all = AsyncMock(
            return_value=[
                PRCreationResult(
                    mutation_id="mut-0001",
                    success=True,
                    pr_url="https://url/1",
                )
            ]
        )

        mock_publisher = MagicMock()
        mock_publisher.publish = AsyncMock(return_value=0)

        with (
            patch("eva.pipeline.PRCreator", return_value=mock_pr_creator),
            patch(
                "eva.pipeline.EvolutionPublisher",
                return_value=mock_publisher,
            ),
        ):
            result = await pipeline.run()

        assert len(result.pr_results) == 1
        mock_publisher.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_source_poll_exception(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "failing"
        mock_source.is_enabled.return_value = True
        mock_source.poll = AsyncMock(side_effect=RuntimeError("source down"))
        pipeline.sources = [mock_source]

        result = await pipeline.run()
        assert result.signals == []

    @pytest.mark.asyncio
    async def test_run_disabled_source_skipped(self):
        config = EvaConfig()
        config.sentry.enabled = False
        config.github_issues.enabled = False
        config.reviews.enabled = False
        config.evolution_logs.enabled = False

        pipeline = EvaPipeline(config)

        mock_source = MagicMock()
        mock_source.name = "disabled"
        mock_source.is_enabled.return_value = False
        mock_source.poll = AsyncMock()
        pipeline.sources = [mock_source]

        result = await pipeline.run()
        mock_source.poll.assert_not_called()
        assert result.signals == []


class TestPrintSummary:
    def test_print_summary_empty_run(self):
        config = EvaConfig()
        pipeline = EvaPipeline(config)
        run = EvaRun()
        pipeline.print_summary(run)  # Should not raise

    def test_print_summary_with_pr_results(self):
        config = EvaConfig()
        pipeline = EvaPipeline(config)
        run = EvaRun(
            signals=[_make_signal()],
            patterns=[_make_pattern()],
            mutations=[_make_mutation()],
            pr_results=[PRCreationResult(mutation_id="mut-0001", success=True, pr_url="url")],
        )
        pipeline.print_summary(run)  # Should not raise

    def test_print_summary_live_mode(self):
        config = EvaConfig()
        config.dry_run = False
        pipeline = EvaPipeline(config)
        run = EvaRun()
        pipeline.print_summary(run)


class TestSaveReport:
    def test_save_report(self, tmp_path):
        config = EvaConfig()
        pipeline = EvaPipeline(config)

        run = EvaRun(
            signals=[_make_signal()],
            patterns=[_make_pattern()],
            mutations=[_make_mutation()],
        )

        report_path = tmp_path / "report.json"
        pipeline.save_report(run, report_path)

        assert report_path.exists()
        data = json.loads(report_path.read_text())
        assert data["summary"]["signals_collected"] == 1
        assert data["summary"]["patterns_detected"] == 1
        assert data["summary"]["mutations_proposed"] == 1
        assert data["mode"] == "dry-run"

    def test_save_report_with_pr_results(self, tmp_path):
        config = EvaConfig()
        config.dry_run = False
        pipeline = EvaPipeline(config)

        run = EvaRun(
            signals=[],
            patterns=[],
            mutations=[],
            pr_results=[
                PRCreationResult(mutation_id="mut-0001", success=True, pr_url="url"),
                PRCreationResult(mutation_id="mut-0002", success=False, error="fail"),
            ],
        )

        report_path = tmp_path / "report.json"
        pipeline.save_report(run, report_path)

        data = json.loads(report_path.read_text())
        assert data["summary"]["prs_created"] == 1
        assert data["summary"]["prs_failed"] == 1
        assert data["mode"] == "live"


class TestSeverityColor:
    def test_all_severities(self):
        assert _severity_color(Severity.CRITICAL) == "red bold"
        assert _severity_color(Severity.HIGH) == "red"
        assert _severity_color(Severity.MEDIUM) == "yellow"
        assert _severity_color(Severity.LOW) == "cyan"
        assert _severity_color(Severity.INFO) == "dim"
