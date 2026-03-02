"""Format evolution entries for Telegram messages.

All agents (Eva included) use the same transparent format.
iEvo is open source — no need to hide internals.
"""

from eva.core.models import EvolutionEntry


def format_telegram_message(entry: EvolutionEntry) -> str:
    """Format evolution entry for Telegram."""
    lines = [
        f"\U0001f9ec <b>{entry.id}</b> | <code>{entry.agent}</code>"
        f" | <code>{entry.type.value}</code>",
        f"<b>{entry.title}</b>",
    ]
    if entry.target:
        lines.append(f"Target: <code>{entry.target}</code>")
    if entry.description:
        lines.append(entry.description[:200])
    confidence_pct = f"{entry.confidence:.0%}" if entry.confidence else "\u2014"
    pr_link = f' | <a href="{entry.pr_url}">PR</a>' if entry.pr_url else ""
    lines.append(f"Confidence: {confidence_pct}{pr_link}")
    return "\n".join(lines)
