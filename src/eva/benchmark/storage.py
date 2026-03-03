"""Benchmark result storage — JSON-based historical tracking."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class ResultStorage:
    """Stores and retrieves benchmark results as JSON files."""

    def __init__(self, results_dir: Path) -> None:
        self._dir = results_dir

    def save(self, agent: str, result: dict[str, Any]) -> Path:
        """Save a benchmark result. Returns path to saved file."""
        agent_dir = self._dir / agent
        agent_dir.mkdir(parents=True, exist_ok=True)

        ts = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
        label = result.get("agent_version_label", "")
        suffix = f"-{label}" if label else ""
        filename = f"{ts}{suffix}.json"
        path = agent_dir / filename

        path.write_text(json.dumps(result, indent=2, default=str))
        return path

    def load(self, path: Path) -> dict[str, Any]:
        """Load a single result from a JSON file."""
        text = path.read_text()
        data: dict[str, Any] = json.loads(text)
        return data

    def list_results(self, agent: str) -> list[Path]:
        """List all stored results for an agent, newest first."""
        agent_dir = self._dir / agent
        if not agent_dir.exists():
            return []
        files = sorted(agent_dir.glob("*.json"), reverse=True)
        return files

    def latest(self, agent: str) -> dict[str, Any] | None:
        """Get the most recent result for an agent."""
        results = self.list_results(agent)
        if not results:
            return None
        return self.load(results[0])
