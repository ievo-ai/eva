"""Tests for benchmark task and rubric loader."""

from pathlib import Path

import pytest

from eva.benchmark.loader import TaskLoader


def _create_suite(tmp_path: Path, agent: str = "spec-writer") -> Path:
    """Create a minimal valid benchmark suite in tmp_path."""
    suite_dir = tmp_path / agent
    suite_dir.mkdir(parents=True)
    tasks_dir = suite_dir / "tasks"
    tasks_dir.mkdir()

    (suite_dir / "suite.yaml").write_text(
        f"agent: {agent}\nversion: '1'\nrubric: rubric.yaml\ntasks:\n  - tasks/task-001.yaml\n"
    )
    (suite_dir / "rubric.yaml").write_text(
        f"agent: {agent}\nversion: '1'\ndimensions:\n"
        "  - name: quality\n    weight: 1.0\n    description: Overall quality\n"
        "    criteria:\n      - Clear and testable\n"
    )
    (tasks_dir / "task-001.yaml").write_text(
        "id: test-001\nagent: spec-writer\ntitle: Test task\n"
        "input_prompt: Write a spec for user login\n"
        "context_files:\n  CONTEXT.md: Project info\n"
        "expected_artifacts:\n  - '*.md'\n"
        "metadata:\n  difficulty: easy\n"
    )
    return suite_dir


class TestTaskLoaderListSuites:
    def test_list_empty_dir(self, tmp_path: Path):
        loader = TaskLoader(tmp_path)
        assert loader.list_suites() == []

    def test_list_nonexistent_dir(self, tmp_path: Path):
        loader = TaskLoader(tmp_path / "nope")
        assert loader.list_suites() == []

    def test_list_one_suite(self, tmp_path: Path):
        _create_suite(tmp_path, "spec-writer")
        loader = TaskLoader(tmp_path)
        assert loader.list_suites() == ["spec-writer"]

    def test_list_multiple_suites(self, tmp_path: Path):
        _create_suite(tmp_path, "spec-writer")
        _create_suite(tmp_path, "architect")
        loader = TaskLoader(tmp_path)
        assert loader.list_suites() == ["architect", "spec-writer"]

    def test_ignores_dirs_without_suite_yaml(self, tmp_path: Path):
        (tmp_path / "not-a-suite").mkdir()
        loader = TaskLoader(tmp_path)
        assert loader.list_suites() == []


class TestTaskLoaderHasSuite:
    def test_has_suite_true(self, tmp_path: Path):
        _create_suite(tmp_path)
        loader = TaskLoader(tmp_path)
        assert loader.has_suite("spec-writer") is True

    def test_has_suite_false(self, tmp_path: Path):
        loader = TaskLoader(tmp_path)
        assert loader.has_suite("nonexistent") is False


class TestTaskLoaderLoadRubric:
    def test_load_valid_rubric(self, tmp_path: Path):
        _create_suite(tmp_path)
        loader = TaskLoader(tmp_path)
        rubric = loader.load_rubric("spec-writer")
        assert rubric.agent == "spec-writer"
        assert rubric.version == "1"
        assert len(rubric.dimensions) == 1
        assert rubric.dimensions[0].name == "quality"
        assert rubric.dimensions[0].weight == 1.0
        assert len(rubric.dimensions[0].criteria) == 1

    def test_load_rubric_no_suite(self, tmp_path: Path):
        loader = TaskLoader(tmp_path)
        with pytest.raises(FileNotFoundError, match="No benchmark suite"):
            loader.load_rubric("nope")

    def test_load_rubric_missing_file(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(
            "agent: sw\nrubric: missing.yaml\ntasks:\n  - t.yaml\n"
        )
        loader = TaskLoader(tmp_path)
        with pytest.raises(FileNotFoundError, match="Rubric file not found"):
            loader.load_rubric("sw")

    def test_load_rubric_empty_file(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(
            "agent: sw\nrubric: rubric.yaml\ntasks:\n  - t.yaml\n"
        )
        (suite_dir / "rubric.yaml").write_text("")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="Empty rubric"):
            loader.load_rubric("sw")

    def test_load_rubric_invalid_weights(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(
            "agent: sw\nrubric: rubric.yaml\ntasks:\n  - t.yaml\n"
        )
        (suite_dir / "rubric.yaml").write_text(
            "agent: sw\ndimensions:\n  - name: d1\n    weight: 0.5\n    description: half\n"
        )
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="weights sum to"):
            loader.load_rubric("sw")


class TestTaskLoaderLoadTasks:
    def test_load_valid_tasks(self, tmp_path: Path):
        _create_suite(tmp_path)
        loader = TaskLoader(tmp_path)
        tasks = loader.load_tasks("spec-writer")
        assert len(tasks) == 1
        assert tasks[0].id == "test-001"
        assert tasks[0].agent == "spec-writer"
        assert tasks[0].title == "Test task"
        assert "login" in tasks[0].input_prompt
        assert "CONTEXT.md" in tasks[0].context_files
        assert tasks[0].expected_artifacts == ["*.md"]
        assert tasks[0].metadata["difficulty"] == "easy"

    def test_load_tasks_no_suite(self, tmp_path: Path):
        loader = TaskLoader(tmp_path)
        with pytest.raises(FileNotFoundError, match="No benchmark suite"):
            loader.load_tasks("nope")

    def test_load_tasks_missing_file(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(
            "agent: sw\nrubric: r.yaml\ntasks:\n  - missing.yaml\n"
        )
        loader = TaskLoader(tmp_path)
        with pytest.raises(FileNotFoundError, match="Task file not found"):
            loader.load_tasks("sw")

    def test_load_tasks_empty_file(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        tasks_dir = suite_dir / "tasks"
        tasks_dir.mkdir()
        (suite_dir / "suite.yaml").write_text(
            "agent: sw\nrubric: r.yaml\ntasks:\n  - tasks/t.yaml\n"
        )
        (tasks_dir / "t.yaml").write_text("")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="Empty task"):
            loader.load_tasks("sw")


class TestTaskLoaderSuiteManifest:
    def test_invalid_manifest_missing_rubric(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text("agent: sw\ntasks:\n  - t.yaml\n")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="missing 'rubric'"):
            loader.load_tasks("sw")

    def test_invalid_manifest_missing_tasks(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text("agent: sw\nrubric: r.yaml\n")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="missing 'rubric' or 'tasks'"):
            loader.load_tasks("sw")

    def test_invalid_manifest_empty(self, tmp_path: Path):
        suite_dir = tmp_path / "sw"
        suite_dir.mkdir()
        (suite_dir / "suite.yaml").write_text("")
        loader = TaskLoader(tmp_path)
        with pytest.raises(ValueError, match="Invalid suite manifest"):
            loader.load_tasks("sw")
