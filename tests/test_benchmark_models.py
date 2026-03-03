"""Tests for benchmark domain models."""

from datetime import datetime

import pytest

from eva.benchmark.models import (
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkTask,
    Dimension,
    DimensionScore,
    FitnessDelta,
    JudgeScore,
    Rubric,
)


class TestDimension:
    def test_basic_construction(self):
        d = Dimension(name="testability", weight=0.3, description="test desc")
        assert d.name == "testability"
        assert d.weight == 0.3
        assert d.description == "test desc"
        assert d.criteria == []

    def test_with_criteria(self):
        d = Dimension(
            name="atomicity",
            weight=0.25,
            description="one behavior per REQ",
            criteria=["3-7 ACs", "no compound REQs"],
        )
        assert len(d.criteria) == 2


class TestRubric:
    def _make_rubric(self, weights: list[float] | None = None) -> Rubric:
        w = weights or [0.3, 0.25, 0.25, 0.2]
        dims = [
            Dimension(name=f"dim{i}", weight=w[i], description=f"desc{i}") for i in range(len(w))
        ]
        return Rubric(agent="spec-writer", dimensions=dims, version="1")

    def test_dimension_names(self):
        r = self._make_rubric()
        assert r.dimension_names == ["dim0", "dim1", "dim2", "dim3"]

    def test_validate_valid(self):
        r = self._make_rubric()
        r.validate()  # should not raise

    def test_validate_invalid(self):
        r = self._make_rubric(weights=[0.5, 0.5, 0.5, 0.5])
        with pytest.raises(ValueError, match="weights sum to 2.0"):
            r.validate()

    def test_validate_close_to_one(self):
        # 0.33 + 0.33 + 0.34 = 1.0
        r = self._make_rubric(weights=[0.33, 0.33, 0.34])
        r.validate()  # within tolerance

    def test_empty_dimensions(self):
        r = Rubric(agent="test")
        assert r.dimension_names == []

    def test_empty_dimensions_raises(self):
        r = Rubric(agent="test")
        with pytest.raises(ValueError, match="weights sum to 0"):
            r.validate()


class TestBenchmarkTask:
    def test_basic(self):
        t = BenchmarkTask(
            id="sw-001",
            agent="spec-writer",
            title="User auth",
            input_prompt="Add authentication",
        )
        assert t.id == "sw-001"
        assert t.context_files == {}
        assert t.expected_artifacts == []
        assert t.metadata == {}

    def test_with_context(self):
        t = BenchmarkTask(
            id="sw-002",
            agent="spec-writer",
            title="CRUD API",
            input_prompt="Add product catalog",
            context_files={"CONTEXT.md": "Project info"},
            expected_artifacts=[".ievo/spec/requirements/REQ-*.md"],
            metadata={"difficulty": "hard"},
        )
        assert "CONTEXT.md" in t.context_files
        assert len(t.expected_artifacts) == 1
        assert t.metadata["difficulty"] == "hard"


class TestDimensionScore:
    def test_basic(self):
        ds = DimensionScore(dimension="testability", score=85, reasoning="Good ACs")
        assert ds.dimension == "testability"
        assert ds.score == 85
        assert ds.evidence == []

    def test_with_evidence(self):
        ds = DimensionScore(
            dimension="atomicity",
            score=70,
            reasoning="Some compound ACs",
            evidence=["AC-3 combines two behaviors"],
        )
        assert len(ds.evidence) == 1


class TestJudgeScore:
    def _make_score(self, scores: list[tuple[str, int]] | None = None) -> JudgeScore:
        dim_scores = [
            DimensionScore(dimension=name, score=val, reasoning=f"{name} ok")
            for name, val in (scores or [("testability", 80), ("atomicity", 60)])
        ]
        return JudgeScore(
            task_id="sw-001",
            agent="spec-writer",
            dimension_scores=dim_scores,
            raw_output="Some spec output",
        )

    def test_overall_score(self):
        js = self._make_score()
        assert js.overall_score == 70.0  # (80 + 60) / 2

    def test_overall_score_empty(self):
        js = JudgeScore(task_id="t1", agent="a")
        assert js.overall_score == 0.0

    def test_compute_weighted(self):
        js = self._make_score()
        rubric = Rubric(
            agent="spec-writer",
            dimensions=[
                Dimension(name="testability", weight=0.6, description="t"),
                Dimension(name="atomicity", weight=0.4, description="a"),
            ],
        )
        # 80 * 0.6 + 60 * 0.4 = 48 + 24 = 72
        assert js.compute_weighted(rubric) == 72.0

    def test_compute_weighted_missing_dimension(self):
        js = self._make_score([("testability", 80)])
        rubric = Rubric(
            agent="spec-writer",
            dimensions=[
                Dimension(name="testability", weight=0.6, description="t"),
                Dimension(name="completeness", weight=0.4, description="c"),
            ],
        )
        # 80 * 0.6 + 0 * 0.4 = 48
        assert js.compute_weighted(rubric) == 48.0

    def test_to_dict(self):
        js = self._make_score()
        d = js.to_dict()
        assert d["task_id"] == "sw-001"
        assert d["agent"] == "spec-writer"
        assert d["overall"] == 70.0
        assert "testability" in d["dimensions"]
        assert d["dimensions"]["testability"]["score"] == 80
        assert d["judge_model"] == "haiku"
        assert "timestamp" in d

    def test_default_timestamp(self):
        js = JudgeScore(task_id="t1", agent="a")
        assert isinstance(js.timestamp, datetime)


class TestBenchmarkResult:
    def _make_result(self, overall_scores: list[float] | None = None) -> BenchmarkResult:
        scores_list = []
        for i, val in enumerate(overall_scores or [70.0, 80.0]):
            ds = [DimensionScore(dimension="d", score=int(val), reasoning="ok")]
            scores_list.append(JudgeScore(task_id=f"t{i}", agent="sw", dimension_scores=ds))
        return BenchmarkResult(
            agent="spec-writer",
            suite_version="1",
            scores=scores_list,
            duration_sec=12.5,
            agent_version_label="v1",
        )

    def test_overall_score(self):
        r = self._make_result([70.0, 80.0])
        assert r.overall_score == 75.0

    def test_overall_score_empty(self):
        r = BenchmarkResult(agent="sw", suite_version="1")
        assert r.overall_score == 0.0

    def test_to_dict(self):
        r = self._make_result([70.0])
        d = r.to_dict()
        assert d["agent"] == "spec-writer"
        assert d["suite_version"] == "1"
        assert d["overall_score"] == 70.0
        assert len(d["scores"]) == 1
        assert d["status"] == "completed"
        assert d["duration_sec"] == 12.5
        assert d["agent_version_label"] == "v1"

    def test_default_status(self):
        r = BenchmarkResult(agent="sw", suite_version="1")
        assert r.status == BenchmarkStatus.COMPLETED

    def test_failed_status(self):
        r = BenchmarkResult(agent="sw", suite_version="1", status=BenchmarkStatus.FAILED)
        assert r.to_dict()["status"] == "failed"


class TestBenchmarkStatus:
    def test_values(self):
        assert BenchmarkStatus.PENDING == "pending"
        assert BenchmarkStatus.RUNNING == "running"
        assert BenchmarkStatus.COMPLETED == "completed"
        assert BenchmarkStatus.FAILED == "failed"


class TestFitnessDelta:
    def _make_delta(self, before_score: float = 60.0, after_score: float = 75.0) -> FitnessDelta:
        before_ds = [DimensionScore(dimension="d", score=int(before_score), reasoning="ok")]
        after_ds = [DimensionScore(dimension="d", score=int(after_score), reasoning="ok")]
        before = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[JudgeScore(task_id="t1", agent="sw", dimension_scores=before_ds)],
        )
        after = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[JudgeScore(task_id="t1", agent="sw", dimension_scores=after_ds)],
        )
        return FitnessDelta(
            mutation_id="mut-001",
            agent="spec-writer",
            before=before,
            after=after,
            per_dimension={"testability": after_score - before_score},
        )

    def test_overall_delta_positive(self):
        fd = self._make_delta(60.0, 75.0)
        assert fd.overall_delta == 15.0
        assert fd.improved is True

    def test_overall_delta_negative(self):
        fd = self._make_delta(80.0, 60.0)
        assert fd.overall_delta == -20.0
        assert fd.improved is False

    def test_overall_delta_zero(self):
        fd = self._make_delta(70.0, 70.0)
        assert fd.overall_delta == 0.0
        assert fd.improved is False

    def test_to_dict(self):
        fd = self._make_delta(60.0, 75.0)
        d = fd.to_dict()
        assert d["mutation_id"] == "mut-001"
        assert d["agent"] == "spec-writer"
        assert d["overall_delta"] == 15.0
        assert d["improved"] is True
        assert d["before_score"] == 60.0
        assert d["after_score"] == 75.0
        assert "testability" in d["per_dimension"]

    def test_format_pr_section_positive(self):
        fd = self._make_delta(60.0, 75.0)
        section = fd.format_pr_section()
        assert "### Benchmark Fitness Delta" in section
        assert "+15.0" in section
        assert "testability" in section

    def test_format_pr_section_negative(self):
        fd = self._make_delta(80.0, 60.0)
        section = fd.format_pr_section()
        assert "-20.0" in section

    def test_format_pr_section_zero(self):
        fd = self._make_delta(70.0, 70.0)
        section = fd.format_pr_section()
        assert "=0.0" in section

    def test_format_pr_section_dimension_delta_negative(self):
        fd = self._make_delta(60.0, 75.0)
        fd.per_dimension["completeness"] = -5.0
        section = fd.format_pr_section()
        assert "-5.0" in section

    def test_format_pr_section_dimension_delta_zero(self):
        fd = self._make_delta(60.0, 75.0)
        fd.per_dimension["atomicity"] = 0.0
        section = fd.format_pr_section()
        assert "=0.0" in section
