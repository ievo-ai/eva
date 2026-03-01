"""Tests for Eva configuration."""

from pathlib import Path

from eva.core.config import EvaConfig


def test_default_config():
    cfg = EvaConfig()
    assert cfg.dry_run is True
    assert cfg.auto_merge is False
    assert cfg.max_mutations_per_run == 5
    assert "cli" in cfg.repos


def test_save_and_load(tmp_path: Path):
    path = tmp_path / "eva.yaml"

    cfg = EvaConfig()
    cfg.dry_run = False
    cfg.max_mutations_per_run = 10
    cfg.save(path)

    loaded = EvaConfig.load(path)
    assert loaded.dry_run is False
    assert loaded.max_mutations_per_run == 10


def test_load_missing_file(tmp_path: Path):
    cfg = EvaConfig.load(tmp_path / "nope.yaml")
    assert cfg.dry_run is True  # defaults
