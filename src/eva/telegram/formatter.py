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
    # Confidence is a proposal-quality signal from Eva's pattern detector
    # (it produces 0.3\u20130.9). A shipped/published evolution (a merged PR) has
    # no meaningful confidence \u2014 it already landed \u2014 and the publish path
    # hard-codes 1.0, which rendered a meaningless "Confidence: 100%" on every
    # announcement. Surface the score ONLY when it's a genuine sub-certain
    # proposal score (0 < c < 1); for shipped evolutions show just the PR link.
    footer = []
    if 0 < entry.confidence < 1:
        footer.append(f"Confidence: {entry.confidence:.0%}")
    if entry.pr_url:
        footer.append(f'<a href="{entry.pr_url}">PR</a>')
    if footer:
        lines.append(" | ".join(footer))
    return "\n".join(lines)
