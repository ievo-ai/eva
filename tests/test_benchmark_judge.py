"""Tests for benchmark judge — G-Eval scoring via Claude CLI."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from eva.benchmark.judge import BenchmarkJudge, _format_rubric_section
from eva.benchmark.models import Dimension, Rubric


def _make_rubric() -> Rubric:
    return Rubric(
        agent="spec-writer",
        dimensions=[
            Dimension(
                name="testability",
                weight=0.6,
                description="ACs are testable",
                criteria=["Each AC maps to one test"],
            ),
            Dimension(
                name="atomicity",
                weight=0.4,
                description="One behavior per REQ",
                criteria=["3-7 ACs"],
            ),
        ],
    )


def _make_judge_response(scores: list[tuple[str, int]] | None = None) -> str:
    dims = scores or [("testability", 85), ("atomicity", 70)]
    data = {
        "dimensions": [
            {
                "dimension": name,
                "reasoning": f"{name} analysis",
                "score": val,
                "evidence": [f"Evidence for {name}"],
            }
            for name, val in dims
        ]
    }
    return json.dumps(data)


def _mock_subprocess(stdout: str, returncode: int = 0) -> AsyncMock:
    proc = AsyncMock()
    proc.communicate = AsyncMock(return_value=(stdout.encode(), b""))
    proc.returncode = returncode
    proc.kill = AsyncMock()
    return proc


class TestFormatRubricSection:
    def test_formats_dimensions(self):
        rubric = _make_rubric()
        section = _format_rubric_section(rubric)
        assert "### testability (weight: 0.6)" in section
        assert "ACs are testable" in section
        assert "Each AC maps to one test" in section
        assert "### atomicity (weight: 0.4)" in section

    def test_dimension_without_criteria(self):
        rubric = Rubric(
            agent="test",
            dimensions=[Dimension(name="d", weight=1.0, description="desc")],
        )
        section = _format_rubric_section(rubric)
        assert "### d (weight: 1.0)" in section
        assert "Criteria:" not in section


class TestBenchmarkJudgeInit:
    def test_default_model(self):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            judge = BenchmarkJudge()
        assert judge._model == "haiku"

    def test_custom_model(self):
        with patch("shutil.which", return_value="/usr/bin/claude"):
            judge = BenchmarkJudge(model="sonnet")
        assert judge._model == "sonnet"

    def test_no_claude_cli(self):
        with patch("shutil.which", return_value=None):
            judge = BenchmarkJudge()
        assert judge._claude_cli is None


class TestBenchmarkJudgeScore:
    @pytest.mark.asyncio
    async def test_score_success(self):
        response = _make_judge_response()
        proc = _mock_subprocess(response)
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("asyncio.create_subprocess_exec", return_value=proc),
        ):
            judge = BenchmarkJudge()
            result = await judge.score(
                task_id="sw-001",
                agent="spec-writer",
                rubric=_make_rubric(),
                agent_output="Some spec output",
            )
        assert result.task_id == "sw-001"
        assert result.agent == "spec-writer"
        assert len(result.dimension_scores) == 2
        assert result.dimension_scores[0].dimension == "testability"
        assert result.dimension_scores[0].score == 85
        assert result.dimension_scores[1].dimension == "atomicity"
        assert result.dimension_scores[1].score == 70
        assert result.raw_output == "Some spec output"
        assert result.judge_model == "haiku"

    @pytest.mark.asyncio
    async def test_score_empty_on_failure(self):
        proc = _mock_subprocess("error", returncode=1)
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("asyncio.create_subprocess_exec", return_value=proc),
        ):
            judge = BenchmarkJudge()
            result = await judge.score(
                task_id="sw-001",
                agent="spec-writer",
                rubric=_make_rubric(),
                agent_output="output",
            )
        assert result.dimension_scores == []

    @pytest.mark.asyncio
    async def test_score_no_cli_raises(self):
        with patch("shutil.which", return_value=None):
            judge = BenchmarkJudge()
            with pytest.raises(RuntimeError, match="Claude CLI not found"):
                await judge.score(
                    task_id="sw-001",
                    agent="spec-writer",
                    rubric=_make_rubric(),
                    agent_output="output",
                )


class TestBenchmarkJudgeTimeout:
    @pytest.mark.asyncio
    async def test_timeout_kills_process(self):
        proc = AsyncMock()
        proc.kill = AsyncMock()
        # After kill, communicate returns empty
        proc.communicate = AsyncMock(return_value=(b"", b""))

        async def _wait_for_that_times_out(*args: object, **kwargs: object) -> object:
            raise TimeoutError

        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("asyncio.create_subprocess_exec", return_value=proc),
            patch(
                "eva.benchmark.judge.asyncio.wait_for",
                side_effect=_wait_for_that_times_out,
            ),
        ):
            judge = BenchmarkJudge(timeout_sec=1)
            with pytest.raises(TimeoutError, match="timed out after 1s"):
                await judge.score(
                    task_id="sw-001",
                    agent="spec-writer",
                    rubric=_make_rubric(),
                    agent_output="output",
                )
        proc.kill.assert_called_once()


class TestBenchmarkJudgeParseResponse:
    def test_parse_valid_json(self):
        response = _make_judge_response()
        scores = BenchmarkJudge._parse_response(response)
        assert len(scores) == 2
        assert scores[0].dimension == "testability"
        assert scores[0].score == 85
        assert scores[0].reasoning == "testability analysis"
        assert scores[0].evidence == ["Evidence for testability"]

    def test_parse_empty_string(self):
        scores = BenchmarkJudge._parse_response("")
        assert scores == []

    def test_parse_invalid_json(self):
        scores = BenchmarkJudge._parse_response("not json at all")
        assert scores == []

    def test_parse_json_with_markdown_code_block(self):
        inner = _make_judge_response()
        wrapped = f"```json\n{inner}\n```"
        scores = BenchmarkJudge._parse_response(wrapped)
        assert len(scores) == 2

    def test_parse_missing_dimensions_key(self):
        scores = BenchmarkJudge._parse_response('{"other": "data"}')
        assert scores == []

    def test_parse_partial_dimension(self):
        data = json.dumps({"dimensions": [{"dimension": "d1", "score": 50}]})
        scores = BenchmarkJudge._parse_response(data)
        assert len(scores) == 1
        assert scores[0].dimension == "d1"
        assert scores[0].score == 50
        assert scores[0].reasoning == ""
        assert scores[0].evidence == []


class TestBenchmarkJudgeCallClaude:
    @pytest.mark.asyncio
    async def test_passes_correct_args(self):
        proc = _mock_subprocess('{"dimensions": []}')
        with (
            patch("shutil.which", return_value="/usr/local/bin/claude"),
            patch("asyncio.create_subprocess_exec", return_value=proc) as mock_exec,
        ):
            judge = BenchmarkJudge(model="sonnet", timeout_sec=60)
            await judge._call_claude("test prompt")

        mock_exec.assert_called_once()
        call_args = mock_exec.call_args[0]
        assert call_args[0] == "/usr/local/bin/claude"
        assert "-p" in call_args
        assert "--model" in call_args
        assert "sonnet" in call_args
        assert "test prompt" in call_args

    @pytest.mark.asyncio
    async def test_strips_claudecode_env(self):
        proc = _mock_subprocess('{"dimensions": []}')
        with (
            patch("shutil.which", return_value="/usr/bin/claude"),
            patch("asyncio.create_subprocess_exec", return_value=proc) as mock_exec,
            patch.dict("os.environ", {"CLAUDECODE": "1", "HOME": "/home"}),
        ):
            judge = BenchmarkJudge()
            await judge._call_claude("prompt")

        env_used = mock_exec.call_args[1]["env"]
        assert "CLAUDECODE" not in env_used
        assert "HOME" in env_used
