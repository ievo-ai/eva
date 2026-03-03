"""Tests for benchmark runner — agent execution and scoring orchestration."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.benchmark.models import (
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkTask,
    Dimension,
    DimensionScore,
    JudgeScore,
    Rubric,
)
from eva.benchmark.runner import BenchmarkRunner


def _create_suite(tmp_path: Path, agent: str = "spec-writer") -> Path:
    """Create minimal benchmark suite files."""
    suite_dir = tmp_path / agent
    suite_dir.mkdir(parents=True)
    tasks_dir = suite_dir / "tasks"
    tasks_dir.mkdir()

    (suite_dir / "suite.yaml").write_text(
        f"agent: {agent}\nversion: '1'\nrubric: rubric.yaml\ntasks:\n  - tasks/task-001.yaml\n"
    )
    (suite_dir / "rubric.yaml").write_text(
        f"agent: {agent}\nversion: '1'\ndimensions:\n"
        "  - name: quality\n    weight: 1.0\n    description: Quality\n"
    )
    (tasks_dir / "task-001.yaml").write_text(
        "id: test-001\nagent: spec-writer\ntitle: Test\n"
        "input_prompt: Write a spec\n"
        "context_files:\n  .ievo/CONTEXT.md: Project info\n"
    )
    return suite_dir


def _make_judge_score(task_id: str = "test-001", score: int = 80) -> JudgeScore:
    return JudgeScore(
        task_id=task_id,
        agent="spec-writer",
        dimension_scores=[DimensionScore(dimension="quality", score=score, reasoning="ok")],
        raw_output="output",
    )


def _make_rubric() -> Rubric:
    return Rubric(
        agent="spec-writer",
        dimensions=[Dimension(name="quality", weight=1.0, description="Q")],
    )


class TestBenchmarkRunnerRunSuite:
    @pytest.mark.asyncio
    async def test_run_suite_success(self, tmp_path: Path):
        _create_suite(tmp_path)
        runner = BenchmarkRunner(benchmarks_dir=tmp_path)

        mock_score = _make_judge_score()
        runner._judge = MagicMock()
        runner._judge.score = AsyncMock(return_value=mock_score)
        runner._execute_in_docker = AsyncMock(return_value="agent output")

        result = await runner.run_suite("spec-writer", label="test-run")

        assert result.agent == "spec-writer"
        assert result.suite_version == "1"
        assert result.status == BenchmarkStatus.COMPLETED
        assert len(result.scores) == 1
        assert result.scores[0].dimension_scores[0].score == 80
        assert result.agent_version_label == "test-run"
        assert result.duration_sec > 0

    @pytest.mark.asyncio
    async def test_run_suite_no_suite(self, tmp_path: Path):
        runner = BenchmarkRunner(benchmarks_dir=tmp_path)
        with pytest.raises(FileNotFoundError, match="No benchmark suite"):
            await runner.run_suite("nonexistent")

    @pytest.mark.asyncio
    async def test_run_suite_task_timeout(self, tmp_path: Path):
        _create_suite(tmp_path)
        runner = BenchmarkRunner(benchmarks_dir=tmp_path)

        runner._judge = MagicMock()
        runner._execute_in_docker = AsyncMock(side_effect=TimeoutError("timeout"))

        result = await runner.run_suite("spec-writer")

        assert result.status == BenchmarkStatus.FAILED
        assert len(result.scores) == 0

    @pytest.mark.asyncio
    async def test_run_suite_runtime_error(self, tmp_path: Path):
        _create_suite(tmp_path)
        runner = BenchmarkRunner(benchmarks_dir=tmp_path)

        runner._judge = MagicMock()
        runner._execute_in_docker = AsyncMock(side_effect=RuntimeError("Docker not found"))

        result = await runner.run_suite("spec-writer")

        assert result.status == BenchmarkStatus.FAILED

    @pytest.mark.asyncio
    async def test_run_suite_with_role_override(self, tmp_path: Path):
        _create_suite(tmp_path)
        runner = BenchmarkRunner(benchmarks_dir=tmp_path)

        mock_score = _make_judge_score()
        runner._judge = MagicMock()
        runner._judge.score = AsyncMock(return_value=mock_score)
        runner._execute_in_docker = AsyncMock(return_value="output")

        result = await runner.run_suite(
            "spec-writer", role_override="# Custom ROLE", label="mutated"
        )

        assert result.status == BenchmarkStatus.COMPLETED
        assert result.agent_version_label == "mutated"


class TestBenchmarkRunnerPrepareWorkspace:
    def test_creates_context_files(self, tmp_path: Path):
        task = BenchmarkTask(
            id="t1",
            agent="sw",
            title="t",
            input_prompt="p",
            context_files={
                ".ievo/memory/CONTEXT.md": "Project info",
                ".ievo/spec/SPEC_INDEX.md": "| REQ | Title |",
            },
        )
        BenchmarkRunner._prepare_workspace(tmp_path, task)

        assert (tmp_path / ".ievo" / "memory" / "CONTEXT.md").read_text() == "Project info"
        assert (tmp_path / ".ievo" / "spec" / "SPEC_INDEX.md").exists()

    def test_creates_role_override(self, tmp_path: Path):
        task = BenchmarkTask(id="t1", agent="spec-writer", title="t", input_prompt="p")
        BenchmarkRunner._prepare_workspace(tmp_path, task, role_override="# Custom agent")

        role_path = tmp_path / ".claude" / "agents" / "spec-writer.md"
        assert role_path.exists()
        assert role_path.read_text() == "# Custom agent"

    def test_no_role_override(self, tmp_path: Path):
        task = BenchmarkTask(id="t1", agent="sw", title="t", input_prompt="p")
        BenchmarkRunner._prepare_workspace(tmp_path, task)

        assert not (tmp_path / ".claude" / "agents").exists()


class TestBenchmarkRunnerExecuteInDocker:
    @pytest.mark.asyncio
    async def test_execute_success(self, tmp_path: Path):
        proc = AsyncMock()
        proc.communicate = AsyncMock(return_value=(b"Agent output here", b""))
        proc.returncode = 0

        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch(
                "eva.benchmark.runner.asyncio.create_subprocess_exec",
                return_value=proc,
            ) as mock_exec,
        ):
            runner = BenchmarkRunner(benchmarks_dir=tmp_path, docker_image="test:latest")
            result = await runner._execute_in_docker(tmp_path, "test prompt")

        assert result == "Agent output here"
        call_args = mock_exec.call_args[0]
        assert "/usr/bin/docker" in call_args
        assert "run" in call_args
        assert "--rm" in call_args
        assert "test:latest" in call_args
        assert "test prompt" in call_args

    @pytest.mark.asyncio
    async def test_execute_no_docker(self, tmp_path: Path):
        with patch("shutil.which", return_value=None):
            runner = BenchmarkRunner(benchmarks_dir=tmp_path)
            with pytest.raises(RuntimeError, match="Docker not found"):
                await runner._execute_in_docker(tmp_path, "prompt")

    @pytest.mark.asyncio
    async def test_execute_timeout(self, tmp_path: Path):
        proc = AsyncMock()
        proc.communicate = AsyncMock(return_value=(b"", b""))
        proc.kill = AsyncMock()

        async def _timeout(*args: object, **kwargs: object) -> object:
            raise TimeoutError

        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch(
                "eva.benchmark.runner.asyncio.create_subprocess_exec",
                return_value=proc,
            ),
            patch("eva.benchmark.runner.asyncio.wait_for", side_effect=_timeout),
        ):
            runner = BenchmarkRunner(benchmarks_dir=tmp_path, timeout_sec=5)
            with pytest.raises(TimeoutError, match="timed out after 5s"):
                await runner._execute_in_docker(tmp_path, "prompt")
        proc.kill.assert_called_once()

    @pytest.mark.asyncio
    async def test_strips_claudecode_env(self, tmp_path: Path):
        proc = AsyncMock()
        proc.communicate = AsyncMock(return_value=(b"out", b""))
        proc.returncode = 0

        with (
            patch("shutil.which", return_value="/usr/bin/docker"),
            patch(
                "eva.benchmark.runner.asyncio.create_subprocess_exec",
                return_value=proc,
            ) as mock_exec,
            patch.dict("os.environ", {"CLAUDECODE": "1", "HOME": "/home"}),
        ):
            runner = BenchmarkRunner(benchmarks_dir=tmp_path)
            await runner._execute_in_docker(tmp_path, "prompt")

        env_used = mock_exec.call_args[1]["env"]
        assert "CLAUDECODE" not in env_used


class TestBenchmarkRunnerCompare:
    def test_compare_positive_delta(self):
        before = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[_make_judge_score(score=60)],
        )
        after = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[_make_judge_score(score=80)],
        )
        rubric = _make_rubric()

        delta = BenchmarkRunner.compare("mut-1", "sw", before, after, rubric)

        assert delta.overall_delta == 20.0
        assert delta.improved is True
        assert delta.per_dimension["quality"] == 20.0

    def test_compare_negative_delta(self):
        before = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[_make_judge_score(score=80)],
        )
        after = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[_make_judge_score(score=60)],
        )
        rubric = _make_rubric()

        delta = BenchmarkRunner.compare("mut-1", "sw", before, after, rubric)

        assert delta.overall_delta == -20.0
        assert delta.improved is False

    def test_compare_empty_scores(self):
        before = BenchmarkResult(agent="sw", suite_version="1", scores=[])
        after = BenchmarkResult(agent="sw", suite_version="1", scores=[])
        rubric = _make_rubric()

        delta = BenchmarkRunner.compare("mut-1", "sw", before, after, rubric)

        assert delta.overall_delta == 0.0
        assert delta.per_dimension["quality"] == 0.0

    def test_compare_multiple_dimensions(self):
        rubric = Rubric(
            agent="sw",
            dimensions=[
                Dimension(name="d1", weight=0.5, description="d1"),
                Dimension(name="d2", weight=0.5, description="d2"),
            ],
        )
        before = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[
                JudgeScore(
                    task_id="t1",
                    agent="sw",
                    dimension_scores=[
                        DimensionScore(dimension="d1", score=50, reasoning="ok"),
                        DimensionScore(dimension="d2", score=70, reasoning="ok"),
                    ],
                )
            ],
        )
        after = BenchmarkResult(
            agent="sw",
            suite_version="1",
            scores=[
                JudgeScore(
                    task_id="t1",
                    agent="sw",
                    dimension_scores=[
                        DimensionScore(dimension="d1", score=80, reasoning="ok"),
                        DimensionScore(dimension="d2", score=60, reasoning="ok"),
                    ],
                )
            ],
        )

        delta = BenchmarkRunner.compare("mut-1", "sw", before, after, rubric)

        assert delta.per_dimension["d1"] == 30.0
        assert delta.per_dimension["d2"] == -10.0
