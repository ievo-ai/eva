"""Benchmark task and rubric loader."""

from pathlib import Path
from typing import Any

import yaml

from eva.benchmark.models import BenchmarkTask, Dimension, Rubric


class TaskLoader:
    """Loads benchmark tasks and rubrics from YAML files."""

    def __init__(self, benchmarks_dir: Path) -> None:
        self._dir = benchmarks_dir

    def list_suites(self) -> list[str]:
        """List available benchmark suite names (agent names)."""
        if not self._dir.exists():
            return []
        return sorted(
            d.name for d in self._dir.iterdir() if d.is_dir() and (d / "suite.yaml").exists()
        )

    def has_suite(self, agent: str) -> bool:
        """Check if a benchmark suite exists for the given agent."""
        return (self._dir / agent / "suite.yaml").exists()

    def load_rubric(self, agent: str) -> Rubric:
        """Load rubric for an agent from YAML."""
        suite = self._load_suite_manifest(agent)
        rubric_path = self._dir / agent / suite["rubric"]
        if not rubric_path.exists():
            msg = f"Rubric file not found: {rubric_path}"
            raise FileNotFoundError(msg)
        return self._parse_rubric(rubric_path)

    def load_agent_role(self, agent: str) -> str:
        """Load default agent ROLE.md content from suite, if specified."""
        suite = self._load_suite_manifest(agent)
        role_file: str = suite.get("role_file", "")
        if not role_file:
            return ""
        role_path = self._dir / agent / role_file
        if not role_path.exists():
            return ""
        return role_path.read_text()

    def load_tasks(self, agent: str) -> list[BenchmarkTask]:
        """Load all benchmark tasks for an agent."""
        suite = self._load_suite_manifest(agent)
        tasks = []
        for task_rel in suite["tasks"]:
            task_path = self._dir / agent / task_rel
            if not task_path.exists():
                msg = f"Task file not found: {task_path}"
                raise FileNotFoundError(msg)
            tasks.append(self._parse_task(task_path))
        return tasks

    def _load_suite_manifest(self, agent: str) -> dict[str, Any]:
        """Load and validate suite.yaml."""
        suite_path = self._dir / agent / "suite.yaml"
        if not suite_path.exists():
            msg = f"No benchmark suite found for agent '{agent}' at {suite_path}"
            raise FileNotFoundError(msg)
        raw = yaml.safe_load(suite_path.read_text())
        if not raw or "rubric" not in raw or "tasks" not in raw:
            msg = f"Invalid suite manifest: missing 'rubric' or 'tasks' in {suite_path}"
            raise ValueError(msg)
        data: dict[str, Any] = raw
        return data

    @staticmethod
    def _parse_rubric(path: Path) -> Rubric:
        """Parse a rubric YAML file into a Rubric domain object."""
        data = yaml.safe_load(path.read_text())
        if not data:
            msg = f"Empty rubric file: {path}"
            raise ValueError(msg)
        dimensions = [
            Dimension(
                name=d["name"],
                weight=d["weight"],
                description=d["description"],
                criteria=d.get("criteria", []),
            )
            for d in data.get("dimensions", [])
        ]
        rubric = Rubric(
            agent=data.get("agent", ""),
            dimensions=dimensions,
            version=str(data.get("version", "1")),
        )
        rubric.validate()
        return rubric

    @staticmethod
    def _parse_task(path: Path) -> BenchmarkTask:
        """Parse a task YAML file into a BenchmarkTask domain object."""
        data = yaml.safe_load(path.read_text())
        if not data:
            msg = f"Empty task file: {path}"
            raise ValueError(msg)
        return BenchmarkTask(
            id=data["id"],
            agent=data.get("agent", ""),
            title=data.get("title", ""),
            input_prompt=data.get("input_prompt", ""),
            context_files=data.get("context_files", {}),
            expected_artifacts=data.get("expected_artifacts", []),
            metadata=data.get("metadata", {}),
        )
