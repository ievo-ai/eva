"""Eva CLI — meta-evolution Mother agent."""

import asyncio
from pathlib import Path

import click
import sentry_sdk
from rich.console import Console
from rich.panel import Panel

from eva import __version__
from eva.core.config import EvaConfig
from eva.telemetry import capture_scan_context, init_sentry

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
            "[dim]Meta-evolution Mother agent. Observes → analyzes → proposes improvements.[/dim]\n"
        )
        console.print(ctx.get_help())


@main.command()
@click.option("--config", "-c", type=click.Path(), default="eva.yaml", help="Config file path.")
@click.option("--marketplace", "-m", type=click.Path(), default=None, help="Marketplace dir.")
@click.option("--dry-run/--live", default=True, help="Dry run mode (default: dry-run).")
@click.option(
    "--report",
    "-r",
    type=click.Path(),
    default="eva-report.json",
    help="Report output path.",
)
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

    console.print(
        Panel.fit(
            f"[bold]Eva[/bold] v{__version__}\n"
            f"Mode: [yellow]{'dry-run' if cfg.dry_run else 'live'}[/yellow]\n"
            f"Max mutations/run: {cfg.max_mutations_per_run}\n"
            f"Auto-merge: [{'red' if cfg.auto_merge else 'green'}]"
            f"{'ON' if cfg.auto_merge else 'OFF'}[/]\n",
            title="Status",
        )
    )

    console.print("[bold]Sources:[/bold]")
    for name in ("sentry", "github_issues", "reviews", "evolution_logs", "telegram"):
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
    console.print("  Edit it to enable sources and configure repos.")


@main.command("export-memory")
@click.option(
    "--output", "-o", type=click.Path(), default=None, help="Output file (stdout if omitted)."
)
@click.option(
    "--from-report",
    type=click.Path(exists=True),
    default=None,
    help="Load from eva-report.json instead of running a scan.",
)
@click.option(
    "--agent-dir",
    type=click.Path(exists=True),
    default="agent",
    help="Agent directory for memory files.",
)
@click.option(
    "--include",
    type=str,
    default=None,
    help="Categories: signals,patterns,mutations,decisions,sessions,evolution-log,history",
)
def export_memory(
    output: str | None,
    from_report: str | None,
    agent_dir: str,
    include: str | None,
) -> None:
    """Export Eva's knowledge in Claude Memory Import format."""
    from eva.export.memory_export import export_memory as do_export

    include_set = set(include.split(",")) if include else None
    report_path = Path(from_report) if from_report else None
    agent_path = Path(agent_dir) if agent_dir else None

    text = do_export(
        report_path=report_path,
        agent_dir=agent_path,
        include=include_set,
    )

    if not text.strip():
        console.print("[yellow]No memory entries to export.[/yellow]")
        return

    entry_count = text.count("\n") + 1

    if output:
        Path(output).write_text(text + "\n")
        console.print(f"[green]✓[/green] Exported {entry_count} entries → {output}")
    else:
        console.print(text)
        console.print(f"\n[dim]({entry_count} entries)[/dim]")


@main.command()
@click.argument("mutation_id")
@click.option("--config", "-c", type=click.Path(), default="eva.yaml")
def approve(mutation_id: str, config: str) -> None:
    """Approve a mutation and create PR (Phase 2)."""
    console.print("[yellow]⚠ PR creation not yet implemented.[/yellow]")
    console.print(f"  Mutation {mutation_id} would be turned into a PR.")
    console.print("  Coming in Eva Phase 2.")


@main.command()
@click.option("--title", required=True, help="Evolution title.")
@click.option("--agent", default="eva", help="Agent name.")
@click.option(
    "--type",
    "evo_type",
    required=True,
    type=click.Choice(
        ["role_patch", "skill_patch", "memory_update", "config_patch", "milestone", "best_practice"]
    ),
    help="Evolution type.",
)
@click.option("--target", default="", help="Target file.")
@click.option("--description", default="", help="Short description.")
@click.option("--confidence", type=float, default=0.0, help="Confidence score.")
@click.option("--pr", "pr_url", default="", help="PR URL.")
@click.option("--dry-run/--live", default=True, help="Preview without publishing.")
def publish(
    title: str,
    agent: str,
    evo_type: str,
    target: str,
    description: str,
    confidence: float,
    pr_url: str,
    dry_run: bool,
) -> None:
    """Publish an evolution entry to ievo.ai and Telegram."""
    from eva.core.models import EvolutionEntry, EvolutionType
    from eva.telegram.formatter import format_telegram_message

    entry = EvolutionEntry(
        title=title,
        agent=agent,
        type=EvolutionType(evo_type),
        target=target,
        description=description,
        confidence=confidence,
        pr_url=pr_url,
    )

    if dry_run:
        console.print("\n[bold cyan]Preview (dry-run):[/bold cyan]")
        console.print(format_telegram_message(entry))
        console.print("\n[dim]Use --live to publish.[/dim]")
        return

    from eva.github.evolution_publisher import EvolutionPublisher
    from eva.telegram.client import TelegramClient

    telegram = None
    try:
        telegram = TelegramClient()
    except ValueError:
        console.print("[dim]No Telegram config — publishing to GitHub only.[/dim]")

    try:
        pub = EvolutionPublisher(telegram=telegram)
        count = asyncio.run(pub.publish_entries([entry]))
        if count:
            console.print(f"[green]✓[/green] Published {entry.id}")
        else:
            console.print("[yellow]⚠[/yellow] Nothing published.")
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")


@main.command("tg-process")
@click.option("--limit", default=50, help="Max messages to process.")
def tg_process(limit: int) -> None:
    """Process new Telegram community messages as Eva."""
    from eva.telegram.client import TelegramClient
    from eva.telegram.responder import EvaResponder

    try:
        tg = TelegramClient()
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        return

    try:
        responder = EvaResponder()
    except ValueError as e:
        console.print(f"[red]✗[/red] {e}")
        return

    async def _process() -> int:
        updates = await tg.get_updates(limit=limit)
        if not updates:
            console.print("[dim]No new messages.[/dim]")
            return 0

        processed = 0
        last_update_id = 0
        for update in updates:
            last_update_id = max(last_update_id, update.get("update_id", 0))
            msg = update.get("message", {})
            text = msg.get("text", "")
            if not text:
                continue

            # Skip messages from the bot itself
            sender = msg.get("from", {})
            if sender.get("is_bot"):
                continue

            msg_id = msg.get("message_id", 0)
            username = sender.get("username", sender.get("first_name", "?"))

            response, category = await responder.process_message(text)

            if response:
                result = await tg.send_message(
                    response,
                    reply_to_message_id=msg_id,
                )
                status = "[green]✓[/green]" if result.success else "[red]✗[/red]"
                console.print(f"  {status} @{username} \\[{category}]")
                processed += 1
            else:
                console.print(f"  [dim]⊘ @{username} \\[{category}][/dim]")

        # Confirm processed updates so they don't appear again
        await tg.get_updates(offset=last_update_id + 1, limit=1)

        return processed

    count = asyncio.run(_process())
    console.print(f"\n[bold]Processed {count} message(s).[/bold]")


if __name__ == "__main__":
    main()
