"""Tests for Eva configuration."""

from pathlib import Path

from eva.core.config import BenchmarkConfig, EvaConfig


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


def test_load_minimal_yaml(tmp_path: Path):
    """Load a YAML with no repos, no sources, no safety keys — all branches miss."""
    path = tmp_path / "minimal.yaml"
    path.write_text("---\n")

    cfg = EvaConfig.load(path)
    assert cfg.dry_run is True
    assert "cli" in cfg.repos


def test_load_with_repos_only(tmp_path: Path):
    path = tmp_path / "repos.yaml"
    path.write_text("repos:\n  custom: custom-org/repo\n")

    cfg = EvaConfig.load(path)
    assert cfg.repos == {"custom": "custom-org/repo"}


def test_load_with_source_config(tmp_path: Path):
    path = tmp_path / "sources.yaml"
    path.write_text(
        "sources:\n"
        "  sentry:\n"
        "    enabled: true\n"
        "    endpoint: https://custom.sentry.io\n"
        "  github_issues:\n"
        "    enabled: false\n"
    )

    cfg = EvaConfig.load(path)
    assert cfg.sentry.enabled is True
    assert cfg.sentry.endpoint == "https://custom.sentry.io"
    assert cfg.github_issues.enabled is False


def test_load_source_unknown_key_ignored(tmp_path: Path):
    """Unknown keys in source config should be silently ignored."""
    path = tmp_path / "extra.yaml"
    path.write_text("sources:\n  sentry:\n    enabled: true\n    unknown_key: value\n")

    cfg = EvaConfig.load(path)
    assert cfg.sentry.enabled is True


def test_load_with_safety_keys(tmp_path: Path):
    path = tmp_path / "safety.yaml"
    path.write_text("auto_merge: true\nmax_mutations_per_run: 3\ndry_run: false\n")

    cfg = EvaConfig.load(path)
    assert cfg.auto_merge is True
    assert cfg.max_mutations_per_run == 3
    assert cfg.dry_run is False


def test_default_benchmark_config():
    cfg = EvaConfig()
    assert cfg.benchmark.enabled is True
    assert cfg.benchmark.judge_model == "haiku"
    assert cfg.benchmark.timeout_sec == 300
    assert cfg.benchmark.docker_image == "ievoai/sandbox:latest"
    assert cfg.benchmark.max_retries == 1


def test_benchmark_config_standalone():
    bc = BenchmarkConfig()
    assert bc.enabled is True
    assert "benchmarks" in str(bc.results_dir)


def test_load_with_benchmark_config(tmp_path: Path):
    path = tmp_path / "bench.yaml"
    path.write_text(
        "benchmark:\n"
        "  enabled: false\n"
        "  judge_model: sonnet\n"
        "  timeout_sec: 600\n"
        "  docker_image: custom:latest\n"
    )
    cfg = EvaConfig.load(path)
    assert cfg.benchmark.enabled is False
    assert cfg.benchmark.judge_model == "sonnet"
    assert cfg.benchmark.timeout_sec == 600
    assert cfg.benchmark.docker_image == "custom:latest"


def test_load_with_benchmark_results_dir(tmp_path: Path):
    path = tmp_path / "bench.yaml"
    path.write_text("benchmark:\n  results_dir: /tmp/eva-results\n")
    cfg = EvaConfig.load(path)
    assert cfg.benchmark.results_dir == Path("/tmp/eva-results")


def test_load_with_benchmark_unknown_key(tmp_path: Path):
    path = tmp_path / "bench.yaml"
    path.write_text("benchmark:\n  enabled: true\n  unknown_field: ignored\n")
    cfg = EvaConfig.load(path)
    assert cfg.benchmark.enabled is True


def test_save_includes_benchmark(tmp_path: Path):
    path = tmp_path / "eva.yaml"
    cfg = EvaConfig()
    cfg.benchmark.judge_model = "opus"
    cfg.save(path)

    loaded = EvaConfig.load(path)
    assert loaded.benchmark.judge_model == "opus"
