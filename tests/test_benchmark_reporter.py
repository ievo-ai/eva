"""Tests for benchmark reporter — Rich console output."""

from io import StringIO

from rich.console import Console

from eva.benchmark.models import (
    BenchmarkResult,
    DimensionScore,
    FitnessDelta,
    JudgeScore,
)
from eva.benchmark.reporter import print_comparison, print_history, print_result


def _make_console() -> Console:
    return Console(file=StringIO(), force_terminal=True)


def _make_result(score: int = 80) -> BenchmarkResult:
    return BenchmarkResult(
        agent="spec-writer",
        suite_version="1",
        scores=[
            JudgeScore(
                task_id="t1",
                agent="sw",
                dimension_scores=[DimensionScore(dimension="quality", score=score, reasoning="ok")],
            )
        ],
        duration_sec=5.0,
    )


class TestPrintResult:
    def test_prints_without_error(self):
        con = _make_console()
        result = _make_result()
        print_result(result, con)
        output = con.file.getvalue()
        assert "spec-writer" in output
        assert "t1" in output

    def test_prints_empty_scores(self):
        con = _make_console()
        result = BenchmarkResult(agent="sw", suite_version="1")
        print_result(result, con)
        output = con.file.getvalue()
        assert "0.0" in output

    def test_prints_with_no_dimension_scores(self):
        con = _make_console()
        result = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[JudgeScore(task_id="t1", agent="sw")],
        )
        print_result(result, con)
        output = con.file.getvalue()
        assert "no scores" in output

    def test_default_console(self):
        # Just verify it doesn't crash with default console
        result = _make_result()
        print_result(result)  # uses Console() by default


class TestPrintComparison:
    def test_prints_positive_delta(self):
        con = _make_console()
        delta = FitnessDelta(
            mutation_id="mut-1",
            agent="sw",
            before=_make_result(60),
            after=_make_result(80),
            per_dimension={"quality": 20.0},
        )
        print_comparison(delta, con)
        output = con.file.getvalue()
        assert "mut-1" in output
        assert "20.0" in output

    def test_prints_negative_delta(self):
        con = _make_console()
        delta = FitnessDelta(
            mutation_id="mut-2",
            agent="sw",
            before=_make_result(80),
            after=_make_result(60),
            per_dimension={"quality": -20.0},
        )
        print_comparison(delta, con)
        output = con.file.getvalue()
        assert "20.0" in output

    def test_prints_zero_delta(self):
        con = _make_console()
        delta = FitnessDelta(
            mutation_id="mut-3",
            agent="sw",
            before=_make_result(70),
            after=_make_result(70),
            per_dimension={"quality": 0.0},
        )
        print_comparison(delta, con)
        output = con.file.getvalue()
        assert "=" in output

    def test_default_console(self):
        delta = FitnessDelta(
            mutation_id="m",
            agent="a",
            before=_make_result(),
            after=_make_result(),
            per_dimension={},
        )
        print_comparison(delta)


class TestPrintHistory:
    def test_prints_history(self):
        con = _make_console()
        results = [
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
        print_history(results, "spec-writer", con)
        output = con.file.getvalue()
        assert "spec-writer" in output
        assert "80.0" in output
        assert "65.0" in output

    def test_empty_history(self):
        con = _make_console()
        print_history([], "sw", con)
        output = con.file.getvalue()
        assert "sw" in output

    def test_partial_data(self):
        con = _make_console()
        print_history([{"timestamp": "?"}], "sw", con)

    def test_default_console(self):
        print_history([], "sw")
