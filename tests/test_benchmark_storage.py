"""Tests for benchmark result storage."""

import json
from pathlib import Path

from eva.benchmark.storage import ResultStorage


def _make_result_dict(label: str = "v1", score: float = 75.0) -> dict:
    return {
        "agent": "spec-writer",
        "suite_version": "1",
        "overall_score": score,
        "agent_version_label": label,
        "status": "completed",
        "timestamp": "2026-03-03T10:00:00",
    }


class TestResultStorageSave:
    def test_save_creates_file(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        result = _make_result_dict()
        path = storage.save("spec-writer", result)

        assert path.exists()
        assert path.suffix == ".json"
        data = json.loads(path.read_text())
        assert data["agent"] == "spec-writer"

    def test_save_creates_agent_dir(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        storage.save("new-agent", _make_result_dict())
        assert (tmp_path / "new-agent").is_dir()

    def test_save_with_label(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        path = storage.save("sw", _make_result_dict(label="before"))
        assert "before" in path.name

    def test_save_without_label(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        path = storage.save("sw", {"agent": "sw"})
        assert path.name.endswith(".json")


class TestResultStorageLoad:
    def test_load_saved_file(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        original = _make_result_dict()
        path = storage.save("sw", original)

        loaded = storage.load(path)
        assert loaded["agent"] == "spec-writer"
        assert loaded["overall_score"] == 75.0


class TestResultStorageListResults:
    def test_list_empty(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        assert storage.list_results("sw") == []

    def test_list_nonexistent_agent(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        assert storage.list_results("nope") == []

    def test_list_returns_newest_first(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        agent_dir = tmp_path / "sw"
        agent_dir.mkdir()

        # Create files with different timestamps
        (agent_dir / "20260301-100000.json").write_text("{}")
        (agent_dir / "20260303-100000.json").write_text("{}")
        (agent_dir / "20260302-100000.json").write_text("{}")

        results = storage.list_results("sw")
        assert len(results) == 3
        # Newest first (sorted reverse)
        assert "20260303" in results[0].name
        assert "20260301" in results[2].name


class TestResultStorageLatest:
    def test_latest_returns_most_recent(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        agent_dir = tmp_path / "sw"
        agent_dir.mkdir()

        (agent_dir / "20260301-100000.json").write_text('{"score": 1}')
        (agent_dir / "20260303-100000.json").write_text('{"score": 3}')

        latest = storage.latest("sw")
        assert latest is not None
        assert latest["score"] == 3

    def test_latest_no_results(self, tmp_path: Path):
        storage = ResultStorage(tmp_path)
        assert storage.latest("sw") is None
