"""Eva configuration and paths."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SourceConfig:
    """Configuration for a signal source."""

    enabled: bool = False
    endpoint: str = ""
    token_env: str = ""  # env var name holding the token
    poll_interval_sec: int = 300
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkConfig:
    """Configuration for the benchmark subsystem."""

    enabled: bool = True
    results_dir: Path = field(default_factory=lambda: Path.home() / ".eva" / "benchmarks")
    judge_model: str = "haiku"
    max_retries: int = 1
    timeout_sec: int = 300
    docker_image: str = "ievoai/sandbox:latest"


@dataclass
class EvaConfig:
    """Top-level Eva configuration."""

    # Target repos Eva can submit PRs to
    repos: dict[str, str] = field(
        default_factory=lambda: {
            "cli": "ievo-ai/cli",
            "marketplace": "ievo-ai/marketplace",
            "sdk": "ievo-ai/sdk",
            "eva": "ievo-ai/eva",
            "landing": "ievo-ai/ievo.ai",
        }
    )

    # Signal sources
    sentry: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            token_env="EVA_SENTRY_TOKEN",
        )
    )
    github_issues: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            token_env="EVA_GITHUB_TOKEN",
            enabled=True,
        )
    )
    reviews: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            token_env="EVA_GITHUB_TOKEN",
        )
    )
    evolution_logs: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            enabled=True,
        )
    )
    research: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            enabled=True,
        )
    )
    telegram: SourceConfig = field(
        default_factory=lambda: SourceConfig(
            token_env="TELEGRAM_BOT_TOKEN",
        )
    )

    # Benchmark
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)

    # Safety
    auto_merge: bool = False  # never auto-merge without human review
    max_mutations_per_run: int = 5
    dry_run: bool = True  # default safe mode

    # Paths
    workspace: Path = field(default_factory=lambda: Path.home() / ".eva")
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".eva" / "cache")

    @classmethod
    def load(cls, path: Path) -> "EvaConfig":
        """Load config from eva.yaml."""
        if not path.exists():
            return cls()
        data = yaml.safe_load(path.read_text()) or {}
        config = cls()

        # Override repos
        if "repos" in data:
            config.repos = data["repos"]

        # Override sources
        for source_name in (
            "sentry",
            "github_issues",
            "reviews",
            "evolution_logs",
            "research",
            "telegram",
        ):
            if source_name in data.get("sources", {}):
                src_data = data["sources"][source_name]
                src_config = getattr(config, source_name)
                for k, v in src_data.items():
                    if hasattr(src_config, k):
                        setattr(src_config, k, v)

        # Override benchmark
        if "benchmark" in data:
            bm_data = data["benchmark"]
            for k, v in bm_data.items():
                if hasattr(config.benchmark, k):
                    if k == "results_dir":
                        v = Path(v)
                    setattr(config.benchmark, k, v)

        # Override safety
        for key in ("auto_merge", "max_mutations_per_run", "dry_run"):
            if key in data:
                setattr(config, key, data[key])

        return config

    def save(self, path: Path) -> None:
        """Save config to eva.yaml."""
        data = {
            "repos": self.repos,
            "sources": {
                "sentry": {"enabled": self.sentry.enabled},
                "github_issues": {"enabled": self.github_issues.enabled},
                "reviews": {"enabled": self.reviews.enabled},
                "evolution_logs": {"enabled": self.evolution_logs.enabled},
                "research": {"enabled": self.research.enabled},
                "telegram": {"enabled": self.telegram.enabled},
            },
            "benchmark": {
                "enabled": self.benchmark.enabled,
                "judge_model": self.benchmark.judge_model,
                "timeout_sec": self.benchmark.timeout_sec,
                "docker_image": self.benchmark.docker_image,
            },
            "auto_merge": self.auto_merge,
            "max_mutations_per_run": self.max_mutations_per_run,
            "dry_run": self.dry_run,
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))
