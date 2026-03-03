"""Benchmark domain models."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class BenchmarkStatus(StrEnum):
    """Status of a benchmark run."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Dimension:
    """A single scoring dimension in a rubric."""

    name: str
    weight: float  # 0.0–1.0, all weights in rubric sum to 1.0
    description: str
    criteria: list[str] = field(default_factory=list)


@dataclass
class Rubric:
    """Scoring rubric for an agent type.

    Defines quality dimensions, weights, and scoring criteria.
    """

    agent: str
    dimensions: list[Dimension] = field(default_factory=list)
    version: str = "1"

    @property
    def dimension_names(self) -> list[str]:
        return [d.name for d in self.dimensions]

    def validate(self) -> None:
        """Verify weights sum to 1.0 (within float tolerance)."""
        total = sum(d.weight for d in self.dimensions)
        if abs(total - 1.0) > 0.01:
            msg = f"Rubric weights sum to {total}, expected 1.0"
            raise ValueError(msg)


@dataclass
class BenchmarkTask:
    """A single benchmark task for an agent."""

    id: str
    agent: str
    title: str
    input_prompt: str
    context_files: dict[str, str] = field(default_factory=dict)
    expected_artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DimensionScore:
    """Score for a single dimension from the judge."""

    dimension: str
    score: int  # 0–100
    reasoning: str
    evidence: list[str] = field(default_factory=list)


@dataclass
class JudgeScore:
    """Complete judge evaluation of an agent's output."""

    task_id: str
    agent: str
    dimension_scores: list[DimensionScore] = field(default_factory=list)
    raw_output: str = ""
    judge_model: str = "haiku"
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))

    @property
    def overall_score(self) -> float:
        """Simple average across all dimensions."""
        if not self.dimension_scores:
            return 0.0
        return sum(ds.score for ds in self.dimension_scores) / len(self.dimension_scores)

    def compute_weighted(self, rubric: Rubric) -> float:
        """Compute weighted score using rubric dimension weights."""
        score_map = {ds.dimension: ds.score for ds in self.dimension_scores}
        total = 0.0
        for dim in rubric.dimensions:
            total += score_map.get(dim.name, 0) * dim.weight
        return total

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "agent": self.agent,
            "overall": round(self.overall_score, 1),
            "dimensions": {
                ds.dimension: {"score": ds.score, "reasoning": ds.reasoning}
                for ds in self.dimension_scores
            },
            "judge_model": self.judge_model,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class BenchmarkResult:
    """Result of running a complete benchmark suite for an agent."""

    agent: str
    suite_version: str
    scores: list[JudgeScore] = field(default_factory=list)
    status: BenchmarkStatus = BenchmarkStatus.COMPLETED
    duration_sec: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
    agent_version_label: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def overall_score(self) -> float:
        """Average across all task scores."""
        if not self.scores:
            return 0.0
        return sum(s.overall_score for s in self.scores) / len(self.scores)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent": self.agent,
            "suite_version": self.suite_version,
            "overall_score": round(self.overall_score, 1),
            "scores": [s.to_dict() for s in self.scores],
            "status": self.status.value,
            "duration_sec": round(self.duration_sec, 2),
            "timestamp": self.timestamp.isoformat(),
            "agent_version_label": self.agent_version_label,
        }


@dataclass
class FitnessDelta:
    """Comparison between two benchmark results — before vs after mutation."""

    mutation_id: str
    agent: str
    before: BenchmarkResult
    after: BenchmarkResult
    per_dimension: dict[str, float] = field(default_factory=dict)

    @property
    def overall_delta(self) -> float:
        """Overall score change: positive = improvement."""
        return self.after.overall_score - self.before.overall_score

    @property
    def improved(self) -> bool:
        return self.overall_delta > 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "mutation_id": self.mutation_id,
            "agent": self.agent,
            "overall_delta": round(self.overall_delta, 1),
            "improved": self.improved,
            "per_dimension": {k: round(v, 1) for k, v in self.per_dimension.items()},
            "before_score": round(self.before.overall_score, 1),
            "after_score": round(self.after.overall_score, 1),
        }

    def format_pr_section(self) -> str:
        """Format for inclusion in mutation PR description."""
        icon = "+" if self.improved else ("-" if self.overall_delta < 0 else "=")
        lines = [
            "### Benchmark Fitness Delta",
            "",
            "| Metric | Before | After | Delta |",
            "|--------|--------|-------|-------|",
            f"| **Overall** | {self.before.overall_score:.1f} "
            f"| {self.after.overall_score:.1f} "
            f"| {icon}{abs(self.overall_delta):.1f} |",
        ]
        for dim, delta in sorted(self.per_dimension.items()):
            d_icon = "+" if delta > 0 else ("-" if delta < 0 else "=")
            lines.append(f"| {dim} | — | — | {d_icon}{abs(delta):.1f} |")
        return "\n".join(lines)
