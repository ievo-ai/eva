"""Eva CLI — meta-evolution Mother agent."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

import sentry_sdk

from eva import __version__
from eva.core.config import EvaConfig
from eva.telemetry import init_sentry, capture_scan_context

console = Console()

LOGO = r"""[bold magenta]
  ███████╗██╗   ██╗ █████╗
  ██╔════╝██║   ██║██╔══██╗
  █████╗  ██║   ██║███████║
  ██╔══╝  ╚██╗ ██╔╝██╔══██║
  ███████╗ ╚████╔╝ ██║  ██║
  ╚══════╝  ╚═══╝  ╚═╝  ╚═╝[/bold magenta]"""


@click.group(invoke_without_command=True)
@click.option("--version", "-v", is_flag=True, help="Show version.")
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """Eva — meta-evolution Mother agent for iEvo."""
    # Initialize Sentry early (silent if DSN not set)
    init_sentry()

    if version:
        console.print(f"eva {__version__}")
        return

    if ctx.invoked_subcommand is None:
        console.print(LOGO, markup=True)
        console.print(
            "[dim]Meta-evolution Mother agent. "
            "Observes → analyzes → proposes improvements.[/dim]\n"
        )
        console.print(ctx.get_help())


@main.command()
@click.option("--config", "-c", type=click.Path(), default="eva.yaml", help="Config file path.")
@click.option("--marketplace", "-m", type=click.Path(), default=None, help="Marketplace dir.")
@click.option("--dry-run/--live", default=True, help="Dry run mode (default: dry-run).")
@click.option("--report", "-r", type=click.Path(), default="eva-report.json", help="Report output path.")
def scan(config: str, marketplace: str | None, dry_run: bool, report: str) -> None:
    """Run one observe → analyze → mutate cycle."""
    cfg = EvaConfig.load(Path(config))
    cfg.dry_run = dry_run

    marketplace_dir = Path(marketplace) if marketplace else None

    from eva.pipeline import EvaPipeline

    pipeline = EvaPipeline(cfg, marketplace_dir=marketplace_dir)

    try:
        with sentry_sdk.start_transaction(op="eva.scan", name="Eva Scan"):
            sentry_sdk.set_tag("mode", "dry-run" if dry_run else "live")
            result = asyncio.run(pipeline.run())

            # Report scan metrics to Sentry context
            capture_scan_context(
                mode="dry-run" if dry_run else "live",
                signals=len(result.signals),
                patterns=len(result.patterns),
                mutations=len(result.mutations),
                prs_created=sum(1 for r in result.pr_results if r.success),
            )

        pipeline.print_summary(result)
        pipeline.save_report(result, Path(report))

    except Exception as e:
        sentry_sdk.capture_exception(e)
        console.print(f"\n[red bold]Eva scan failed:[/red bold] {e}")
        raise


@main.command()
@click.option("--config", "-c", type=click.Path(), default="eva.yaml", help="Config file path.")
def status(config: str) -> None:
    """Show Eva status and source health."""
    cfg = EvaConfig.load(Path(config))

    console.print(Panel.fit(
        f"[bold]Eva[/bold] v{__version__}\n"
        f"Mode: [yellow]{'dry-run' if cfg.dry_run else 'live'}[/yellow]\n"
        f"Max mutations/run: {cfg.max_mutations_per_run}\n"
        f"Auto-merge: [{'red' if cfg.auto_merge else 'green'}]"
        f"{'ON' if cfg.auto_merge else 'OFF'}[/]\n",
        title="Status",
    ))

    console.print("[bold]Sources:[/bold]")
    for name in ("sentry", "github_issues", "reviews", "evolution_logs"):
        src = getattr(cfg, name)
        status_icon = "[green]●[/green]" if src.enabled else "[dim]○[/dim]"
        console.print(f"  {status_icon} {name}")

    console.print("\n[bold]Repos:[/bold]")
    for label, repo in cfg.repos.items():
        console.print(f"  [cyan]{label:15}[/cyan] → {repo}")
    console.print()


@main.command()
@click.option("--output", "-o", type=click.Path(), default="eva.yaml", help="Output path.")
def init(output: str) -> None:
    """Generate default eva.yaml config."""
    path = Path(output)
    if path.exists():
        console.print(f"[yellow]⚠ {path} already exists. Overwrite? (y/N)[/yellow]")
        if input().strip().lower() != "y":
            console.print("[dim]Aborted.[/dim]")
            return

    cfg = EvaConfig()
    cfg.save(path)
    console.print(f"[green]✓[/green] Created {path}")
    console.print(f"  Edit it to enable sources and configure repos.")


@main.command()
@click.argument("mutation_id")
@click.option("--config", "-c", type=click.Path(), default="eva.yaml")
def approve(mutation_id: str, config: str) -> None:
    """Approve a mutation and create PR (Phase 2)."""
    console.print(f"[yellow]⚠ PR creation not yet implemented.[/yellow]")
    console.print(f"  Mutation {mutation_id} would be turned into a PR.")
    console.print(f"  Coming in Eva Phase 2.")


if __name__ == "__main__":
    main()
