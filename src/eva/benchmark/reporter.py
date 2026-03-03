"""Benchmark reporting — Rich console output and comparison tables."""

from typing import Any

from rich.console import Console
from rich.table import Table

from eva.benchmark.models import BenchmarkResult, FitnessDelta


def print_result(result: BenchmarkResult, console: Console | None = None) -> None:
    """Print a benchmark result as a Rich table."""
    con = console or Console()
    table = Table(title=f"Benchmark: {result.agent} (v{result.suite_version})")
    table.add_column("Task", style="cyan")
    table.add_column("Overall", justify="right")
    table.add_column("Status", style="dim")

    for score in result.scores:
        dims = ", ".join(f"{ds.dimension}={ds.score}" for ds in score.dimension_scores)
        table.add_row(
            score.task_id,
            f"{score.overall_score:.0f}",
            dims or "no scores",
        )

    table.add_section()
    table.add_row(
        "TOTAL",
        f"{result.overall_score:.1f}",
        f"{result.status.value} ({result.duration_sec:.1f}s)",
    )
    con.print(table)


def print_comparison(delta: FitnessDelta, console: Console | None = None) -> None:
    """Print a fitness delta comparison as a Rich table."""
    con = console or Console()
    table = Table(title=f"Fitness Delta: {delta.agent} ({delta.mutation_id})")
    table.add_column("Metric")
    table.add_column("Before", justify="right")
    table.add_column("After", justify="right")
    table.add_column("Delta", justify="right")

    if delta.improved:
        icon = "[green]+[/green]"
    elif delta.overall_delta < 0:
        icon = "[red]-[/red]"
    else:
        icon = "="
    table.add_row(
        "[bold]Overall[/bold]",
        f"{delta.before.overall_score:.1f}",
        f"{delta.after.overall_score:.1f}",
        f"{icon}{abs(delta.overall_delta):.1f}",
    )

    for dim, d in sorted(delta.per_dimension.items()):
        d_icon = "[green]+[/green]" if d > 0 else "[red]-[/red]" if d < 0 else "="
        table.add_row(dim, "—", "—", f"{d_icon}{abs(d):.1f}")

    con.print(table)


def print_history(
    results: list[dict[str, Any]], agent: str, console: Console | None = None
) -> None:
    """Print benchmark history as a Rich table."""
    con = console or Console()
    table = Table(title=f"Benchmark History: {agent}")
    table.add_column("Timestamp", style="dim")
    table.add_column("Label")
    table.add_column("Score", justify="right")
    table.add_column("Status")

    for r in results:
        table.add_row(
            r.get("timestamp", "?")[:19],
            r.get("agent_version_label", ""),
            f"{r.get('overall_score', 0):.1f}",
            r.get("status", "?"),
        )

    con.print(table)
