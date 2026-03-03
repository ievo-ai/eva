"""Tests for benchmark CLI commands."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from eva.benchmark.models import (
    BenchmarkResult,
    DimensionScore,
    JudgeScore,
)
from eva.cli import main


@pytest.fixture
def runner():
    return CliRunner()


def _make_benchmark_result(agent: str = "spec-writer", score: int = 80) -> BenchmarkResult:
    return BenchmarkResult(
        agent=agent,
        suite_version="1",
        scores=[
            JudgeScore(
                task_id="t1",
                agent=agent,
                dimension_scores=[DimensionScore(dimension="quality", score=score, reasoning="ok")],
            )
        ],
        duration_sec=5.0,
    )


class TestBenchmarkGroup:
    def test_benchmark_help(self, runner):
        result = runner.invoke(main, ["benchmark", "--help"])
        assert result.exit_code == 0
        assert "run" in result.output
        assert "history" in result.output


class TestBenchmarkRun:
    def test_run_agent(self, runner, tmp_path):
        mock_result = _make_benchmark_result()
        mock_runner = MagicMock()
        mock_runner.run_suite = AsyncMock(return_value=mock_result)

        with (
            patch("eva.cli.EvaConfig.load"),
            patch("eva.benchmark.runner.BenchmarkRunner", return_value=mock_runner),
            patch("eva.benchmark.storage.ResultStorage") as mock_storage_cls,
        ):
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage

            result = runner.invoke(
                main,
                ["benchmark", "run", "spec-writer", "-b", str(tmp_path)],
            )

        assert result.exit_code == 0

    def test_run_compare(self, runner, tmp_path):
        before_file = tmp_path / "before.md"
        after_file = tmp_path / "after.md"
        before_file.write_text("# Old ROLE")
        after_file.write_text("# New ROLE")

        mock_result_before = _make_benchmark_result(score=60)
        mock_result_after = _make_benchmark_result(score=80)
        mock_runner_instance = MagicMock()
        mock_runner_instance.run_suite = AsyncMock(
            side_effect=[mock_result_before, mock_result_after]
        )
        mock_runner_instance._loader = MagicMock()

        from eva.benchmark.models import Dimension, FitnessDelta, Rubric

        mock_runner_instance._loader.load_rubric.return_value = Rubric(
            agent="spec-writer",
            dimensions=[Dimension(name="quality", weight=1.0, description="q")],
        )

        mock_runner_cls = MagicMock(return_value=mock_runner_instance)
        mock_runner_cls.compare = MagicMock(
            return_value=FitnessDelta(
                mutation_id="manual",
                agent="spec-writer",
                before=mock_result_before,
                after=mock_result_after,
                per_dimension={"quality": 20.0},
            )
        )

        with (
            patch("eva.cli.EvaConfig.load"),
            patch("eva.benchmark.runner.BenchmarkRunner", mock_runner_cls),
            patch("eva.benchmark.storage.ResultStorage") as mock_storage_cls,
        ):
            mock_storage = MagicMock()
            mock_storage_cls.return_value = mock_storage

            result = runner.invoke(
                main,
                [
                    "benchmark",
                    "run",
                    "spec-writer",
                    "--compare",
                    str(before_file),
                    str(after_file),
                    "-b",
                    str(tmp_path),
                ],
            )

        assert result.exit_code == 0


class TestBenchmarkHistory:
    def test_history_with_results(self, runner, tmp_path):
        mock_storage = MagicMock()
        mock_storage.list_results.return_value = [
            tmp_path / "result1.json",
            tmp_path / "result2.json",
        ]
        mock_storage.load.side_effect = [
            {
                "timestamp": "2026-03-03T10:00:00",
                "agent_version_label": "v1",
                "overall_score": 80.0,
                "status": "completed",
            },
            {
                "timestamp": "2026-03-02T10:00:00",
                "agent_version_label": "v0",
                "overall_score": 65.0,
                "status": "completed",
            },
        ]

        with (
            patch("eva.cli.EvaConfig.load"),
            patch("eva.benchmark.storage.ResultStorage", return_value=mock_storage),
        ):
            result = runner.invoke(main, ["benchmark", "history", "spec-writer"])

        assert result.exit_code == 0

    def test_history_no_results(self, runner):
        mock_storage = MagicMock()
        mock_storage.list_results.return_value = []

        with (
            patch("eva.cli.EvaConfig.load"),
            patch("eva.benchmark.storage.ResultStorage", return_value=mock_storage),
        ):
            result = runner.invoke(main, ["benchmark", "history", "spec-writer"])

        assert result.exit_code == 0
        assert "No benchmark history" in result.output
