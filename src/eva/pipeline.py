"""Eva pipeline — the main observe → analyze → mutate loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from eva.core.config import EvaConfig
from eva.core.models import Mutation, Pattern, Signal
from eva.sources.base import BaseSource
from eva.sources.sentry import SentrySource
from eva.sources.github_issues import GitHubIssuesSource
from eva.sources.evolution_logs import EvolutionLogsSource
from eva.sources.reviews import ReviewsSource
from eva.analysis.detector import PatternDetector
from eva.mutations.engine import MutationEngine

console = Console()


@dataclass
class EvaRun:
    """Result of a single Eva pipeline run."""

    signals: list[Signal] = field(default_factory=list)
    patterns: list[Pattern] = field(default_factory=list)
    mutations: list[Mutation] = field(default_factory=list)


class EvaPipeline:
    """The main Eva pipeline: observe → analyze → mutate.

    ```
    ┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
    │   Sources    │───▶│  Signals  │───▶│ Patterns  │───▶│ Mutations│
    │ Sentry       │    │ normalized│    │ frequency │    │ PR-ready │
    │ GitHub Issues│    │ stream    │    │ cross-agnt│    │ patches  │
    │ Evo Logs     │    │           │    │ escalation│    │          │
    │ Reviews      │    │           │    │           │    │          │
    └─────────────┘    └───────────┘    └───────────┘    └──────────┘
                                                               │
                                                               ▼
                                                         Human Review
                                                               │
                                                               ▼
                                                          Merge / Reject
    ```
    """

    def __init__(self, config: EvaConfig, marketplace_dir: Path | None = None) -> None:
        self.config = config
        self.detector = PatternDetector()
        self.mutator = MutationEngine(max_per_run=config.max_mutations_per_run)

        # Initialize sources
        self.sources: list[BaseSource] = []

        if config.sentry.enabled:
            self.sources.append(SentrySource(config.sentry))

        if config.github_issues.enabled:
            self.sources.append(GitHubIssuesSource(config.github_issues, config.repos))

        if config.reviews.enabled:
            self.sources.append(ReviewsSource(config.reviews, config.repos))

        if config.evolution_logs.enabled:
            self.sources.append(EvolutionLogsSource(
                config.evolution_logs,
                marketplace_dir=marketplace_dir,
            ))

    async def run(self) -> EvaRun:
        """Execute one full observe → analyze → mutate cycle.

        Returns:
            EvaRun with all signals, patterns, and mutations.
        """
        result = EvaRun()

        # Phase 1: Observe — collect signals from all sources
        console.print("\n[bold cyan]Phase 1: Observe[/bold cyan]")
        for source in self.sources:
            if not source.is_enabled():
                console.print(f"  [dim]⊘ {source.name} (disabled)[/dim]")
                continue

            try:
                signals = await source.poll()
                result.signals.extend(signals)
                console.print(f"  [green]✓[/green] {source.name}: {len(signals)} signals")
            except Exception as e:
                console.print(f"  [red]✗[/red] {source.name}: {e}")

        if not result.signals:
            console.print("  [dim]No new signals.[/dim]")
            return result

        # Phase 2: Analyze — detect patterns
        console.print("\n[bold cyan]Phase 2: Analyze[/bold cyan]")
        result.patterns = self.detector.ingest(result.signals)
        console.print(f"  Patterns detected: {len(result.patterns)}")

        for p in result.patterns:
            console.print(
                f"  [{_severity_color(p.severity)}]●[/{_severity_color(p.severity)}] "
                f"{p.title} [dim](confidence: {p.confidence:.0%})[/dim]"
            )

        if not result.patterns:
            console.print("  [dim]No patterns detected.[/dim]")
            return result

        # Phase 3: Mutate — generate proposed changes
        console.print("\n[bold cyan]Phase 3: Mutate[/bold cyan]")
        result.mutations = self.mutator.generate(result.patterns)
        console.print(f"  Mutations proposed: {len(result.mutations)}")

        if self.config.dry_run:
            console.print("  [yellow]⚠ DRY RUN — no PRs created[/yellow]")

        for m in result.mutations:
            console.print(
                f"  [bold]{m.id}[/bold] [{m.type.value}] {m.title[:60]} "
                f"[dim]→ {m.target_repo}[/dim]"
            )

        return result

    def print_summary(self, run: EvaRun) -> None:
        """Print a summary table of the run."""
        console.print("\n")
        table = Table(title="Eva Run Summary")
        table.add_column("Metric", style="bold")
        table.add_column("Count", justify="right")

        table.add_row("Signals collected", str(len(run.signals)))
        table.add_row("Patterns detected", str(len(run.patterns)))
        table.add_row("Mutations proposed", str(len(run.mutations)))
        table.add_row("Mode", "[yellow]dry-run[/yellow]" if self.config.dry_run else "[green]live[/green]")

        console.print(table)
        console.print()


def _severity_color(s) -> str:
    from eva.core.models import Severity
    return {
        Severity.CRITICAL: "red bold",
        Severity.HIGH: "red",
        Severity.MEDIUM: "yellow",
        Severity.LOW: "cyan",
        Severity.INFO: "dim",
    }.get(s, "white")
