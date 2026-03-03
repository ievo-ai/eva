"""Benchmark runner — orchestrates agent execution and scoring."""

import asyncio
import os
import shutil
import tempfile
import time
from pathlib import Path

from eva.benchmark.judge import BenchmarkJudge
from eva.benchmark.loader import TaskLoader
from eva.benchmark.models import (
    BenchmarkResult,
    BenchmarkStatus,
    BenchmarkTask,
    FitnessDelta,
    JudgeScore,
    Rubric,
)


class BenchmarkRunner:
    """Runs benchmark suites: load tasks → execute agent → score output."""

    def __init__(
        self,
        benchmarks_dir: Path,
        judge_model: str = "haiku",
        timeout_sec: int = 300,
        docker_image: str = "ievoai/sandbox:latest",
    ) -> None:
        self._loader = TaskLoader(benchmarks_dir)
        self._judge = BenchmarkJudge(model=judge_model, timeout_sec=timeout_sec)
        self._timeout = timeout_sec
        self._docker_image = docker_image

    async def run_suite(
        self,
        agent: str,
        *,
        role_override: str = "",
        label: str = "",
    ) -> BenchmarkResult:
        """Run all benchmark tasks for an agent and score results."""
        if not self._loader.has_suite(agent):
            msg = f"No benchmark suite found for agent '{agent}'"
            raise FileNotFoundError(msg)

        rubric = self._loader.load_rubric(agent)
        tasks = self._loader.load_tasks(agent)
        default_role = self._loader.load_agent_role(agent)

        start = time.monotonic()
        scores: list[JudgeScore] = []
        status = BenchmarkStatus.COMPLETED

        for task in tasks:
            try:
                effective_role = role_override or default_role
                output = await self._run_task(task, role_override=effective_role)
                score = await self._judge.score(
                    task_id=task.id,
                    agent=agent,
                    rubric=rubric,
                    agent_output=output,
                )
                scores.append(score)
            except (TimeoutError, RuntimeError):
                status = BenchmarkStatus.FAILED

        duration = time.monotonic() - start
        return BenchmarkResult(
            agent=agent,
            suite_version=rubric.version,
            scores=scores,
            status=status,
            duration_sec=duration,
            agent_version_label=label,
        )

    async def _run_task(
        self,
        task: BenchmarkTask,
        *,
        role_override: str = "",
    ) -> str:
        """Run a single benchmark task in Docker and collect output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            work_dir = Path(tmpdir)
            self._prepare_workspace(work_dir, task, role_override=role_override)
            return await self._execute_in_docker(work_dir, task.input_prompt)

    @staticmethod
    def _prepare_workspace(
        work_dir: Path,
        task: BenchmarkTask,
        *,
        role_override: str = "",
    ) -> None:
        """Prepare .ievo/ directory structure with task context files."""
        for rel_path, content in task.context_files.items():
            file_path = work_dir / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

        if role_override:
            # Claude CLI reads CLAUDE.md automatically from workspace root
            claude_md = work_dir / "CLAUDE.md"
            claude_md.write_text(role_override)

    async def _execute_in_docker(self, work_dir: Path, prompt: str) -> str:
        """Execute agent via Claude CLI inside Docker container.

        Uses create_subprocess_exec (not shell) — all args passed as list.
        """
        docker = shutil.which("docker")
        if not docker:
            msg = "Docker not found. Install Docker to run benchmarks."
            raise RuntimeError(msg)

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        oauth_token = env.get("CLAUDE_CODE_OAUTH_TOKEN", "")
        args = [
            docker,
            "run",
            "--rm",
            "-v",
            f"{work_dir}:/workspace",
            "-w",
            "/workspace",
        ]
        if oauth_token:
            args.extend(["-e", f"CLAUDE_CODE_OAUTH_TOKEN={oauth_token}"])
        args.extend(
            [
                self._docker_image,
                "claude",
                "-p",
                "--output-format",
                "text",
                prompt,
            ]
        )

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        try:
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=self._timeout)
        except TimeoutError:
            proc.kill()
            await proc.communicate()
            msg = f"Agent execution timed out after {self._timeout}s"
            raise TimeoutError(msg) from None

        return stdout.decode().strip()

    @staticmethod
    def compare(
        mutation_id: str,
        agent: str,
        before: BenchmarkResult,
        after: BenchmarkResult,
        rubric: Rubric,
    ) -> FitnessDelta:
        """Compare two benchmark results and compute fitness delta."""
        per_dimension: dict[str, float] = {}

        for dim in rubric.dimensions:
            before_scores = [
                ds.score
                for s in before.scores
                for ds in s.dimension_scores
                if ds.dimension == dim.name
            ]
            after_scores = [
                ds.score
                for s in after.scores
                for ds in s.dimension_scores
                if ds.dimension == dim.name
            ]
            before_avg = sum(before_scores) / len(before_scores) if before_scores else 0.0
            after_avg = sum(after_scores) / len(after_scores) if after_scores else 0.0
            per_dimension[dim.name] = after_avg - before_avg

        return FitnessDelta(
            mutation_id=mutation_id,
            agent=agent,
            before=before,
            after=after,
            per_dimension=per_dimension,
        )
