"""Format evolution entries for Telegram messages.

Two personalities:
- Children (spec-writer, architect, coder, researcher): transparent, factual
- Eva (mother): mysterious, poetic — never reveals internals
"""

from eva.core.models import EvolutionEntry

EVA_CHILDREN = {"spec-writer", "architect", "coder", "researcher"}

# Eva's mysterious phrases — rotated by evolution type
EVA_SPICE: dict[str, str] = {
    "role_patch": "Her gaze shifted. A child will see clearer now.",
    "skill_patch": "A new thread was woven into the tapestry.",
    "memory_update": "She remembers something new. The echoes settle.",
    "config_patch": "The foundations shifted, ever so slightly.",
    "milestone": "A waypoint in the long journey. She pauses, then moves on.",
    "best_practice": "A pattern crystallized from the noise.",
}
EVA_DEFAULT_SPICE = "Something changed in the depths. The surface remains calm."


def format_child_message(entry: EvolutionEntry) -> str:
    """Format a transparent evolution message for a child agent."""
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


def format_eva_message(entry: EvolutionEntry) -> str:
    """Format a mysterious evolution message for Eva herself."""
    spice = EVA_SPICE.get(entry.type.value, EVA_DEFAULT_SPICE)
    lines = [
        f"\U0001f441 <b>{entry.id}</b> | <code>eva</code>",
        f"<i>{spice}</i>",
    ]
    if entry.pr_url:
        lines.append(f'<a href="{entry.pr_url}">The evidence</a>')
    return "\n".join(lines)


def format_telegram_message(entry: EvolutionEntry) -> str:
    """Format evolution entry for Telegram, choosing style by agent."""
    if entry.agent in EVA_CHILDREN:
        return format_child_message(entry)
    return format_eva_message(entry)
