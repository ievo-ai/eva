"""Export Eva's knowledge in Claude Memory Import format.

Claude Memory Import accepts entries formatted as:
    [date] - memory content

This module converts Eva's signals, patterns, mutations, decisions,
evolution log, and session history into that format.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from eva.core.models import Mutation, Pattern, Signal


def format_signals(signals: list[Signal]) -> list[str]:
    """Convert signals to memory entries."""
    entries = []
    for s in signals:
        date = s.timestamp.strftime("%Y-%m-%d")
        agents = s.metadata.get("agent", "")
        agent_suffix = f" in {agents}" if agents else ""
        source = s.source
        entries.append(
            f"[{date}] - Eva signal ({s.type.value}): "
            f"{s.title}{agent_suffix} (source: {source}, severity: {s.severity.value})"
        )
    return entries


def format_patterns(patterns: list[Pattern]) -> list[str]:
    """Convert patterns to memory entries."""
    entries = []
    for p in patterns:
        agents = ", ".join(p.affected_agents) if p.affected_agents else "unknown"
        entries.append(
            f"[{datetime.now().strftime('%Y-%m-%d')}] - Eva pattern: "
            f"{p.title} — affects {agents} "
            f"(confidence: {p.confidence:.0%}, frequency: {p.frequency})"
        )
    return entries


def format_mutations(mutations: list[Mutation]) -> list[str]:
    """Convert mutations to memory entries."""
    entries = []
    for m in mutations:
        pr_note = f", PR: {m.pr_url}" if m.pr_url else ""
        entries.append(
            f"[{datetime.now().strftime('%Y-%m-%d')}] - Eva mutation ({m.type.value}): "
            f"{m.title} — target: {m.target_repo}/{m.target_path} "
            f"(confidence: {m.confidence:.0%}{pr_note})"
        )
    return entries


def format_decisions(decisions_md: str) -> list[str]:
    """Parse DECISIONS.md table and convert to memory entries.

    Expected format:
    | D-001 | 2026-02-28 | Decision text | Rationale | Status |
    """
    entries = []
    for line in decisions_md.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| ID") or line.startswith("|--"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 4:
            continue
        decision_id, date, decision, rationale, *rest = parts
        status = rest[0] if rest else "Active"
        entries.append(
            f"[{date}] - Eva decision {decision_id}: {decision} — {rationale} ({status})"
        )
    return entries


def format_sessions(sessions_dir: Path) -> list[str]:
    """Parse session files and extract summary entries."""
    entries: list[str] = []
    if not sessions_dir.is_dir():
        return entries

    for session_file in sorted(sessions_dir.glob("*.md")):
        content = session_file.read_text()
        # Extract date from first ## header or filename
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})", content[:200])
        date = date_match.group(1) if date_match else "unknown"

        # Extract session number and topic from filename
        name_match = re.match(r"(\d+)-(.+)\.md", session_file.name)
        if not name_match:
            continue
        num = name_match.group(1)
        topic = name_match.group(2).replace("-", " ").title()

        # Extract first meaningful line after the header for summary
        summary_lines = []
        for md_line in content.splitlines():
            stripped = md_line.strip()
            if stripped.startswith("## ") and "summary" in stripped.lower():
                continue
            if stripped and not stripped.startswith("#") and len(stripped) > 20:
                summary_lines.append(stripped)
                if len(summary_lines) >= 1:
                    break

        summary = summary_lines[0][:120] if summary_lines else topic
        entries.append(f"[{date}] - Eva session {num}: {topic} — {summary}")

    return entries


def format_evolution_log(evo_log: str) -> list[str]:
    """Parse EVOLUTION_LOG.md and convert to memory entries.

    Expected format:
    ## 2026-03-01: Title
    **Context:** ...
    **Action:** ...
    **Goal:** ...
    """
    entries = []
    current_date = ""
    current_title = ""
    current_action = ""

    for line in evo_log.splitlines():
        line = line.strip()

        # Header: ## 2026-03-01: Title
        header_match = re.match(r"^## (\d{4}-\d{2}-\d{2}):\s*(.+)", line)
        if header_match:
            # Save previous entry
            if current_date and current_title:
                action_text = f" — {current_action}" if current_action else ""
                entries.append(
                    f"[{current_date}] - Eva self-evolution: {current_title}{action_text}"
                )
            current_date = header_match.group(1)
            current_title = header_match.group(2)
            current_action = ""
            continue

        # Action line
        action_match = re.match(r"\*\*Action:\*\*\s*(.+)", line)
        if action_match:
            current_action = action_match.group(1)[:150]

    # Save last entry
    if current_date and current_title:
        action_text = f" — {current_action}" if current_action else ""
        entries.append(f"[{current_date}] - Eva self-evolution: {current_title}{action_text}")

    return entries


def format_history(history_md: str) -> list[str]:
    """Parse HISTORY.md table and convert to memory entries.

    Expected format:
    | 001 | 2026-02-28 | Topic | Key outcome |
    """
    entries = []
    for line in history_md.splitlines():
        line = line.strip()
        if not line.startswith("|") or line.startswith("| #") or line.startswith("|--"):
            continue
        parts = [p.strip() for p in line.split("|") if p.strip()]
        if len(parts) < 4:
            continue
        # First column may contain a markdown link
        num_part = parts[0]
        num_match = re.search(r"\d+", num_part)
        num = num_match.group(0) if num_match else "?"
        date = parts[1]
        topic = parts[2]
        outcome = parts[3]
        entries.append(f"[{date}] - Eva session {num} ({topic}): {outcome}")
    return entries


def load_report(report_path: Path) -> tuple[list[Signal], list[Pattern], list[Mutation]]:
    """Load signals, patterns, mutations from eva-report.json."""
    data = json.loads(report_path.read_text())

    signals = []
    for s in data.get("signals", []):
        signals.append(
            Signal(
                id=s["id"],
                type=s["type"],
                source=s["source"],
                title=s["title"],
                severity=s.get("severity", "medium"),
                tags=s.get("tags", []),
                body="",
            )
        )

    patterns = []
    for p in data.get("patterns", []):
        patterns.append(
            Pattern(
                id=p["id"],
                title=p["title"],
                description="",
                confidence=p.get("confidence", 0),
                severity=p.get("severity", "medium"),
                signal_ids=p.get("signal_ids", []),
                affected_repos=p.get("affected_repos", []),
            )
        )

    mutations = []
    for m in data.get("mutations", []):
        mutations.append(
            Mutation(
                id=m["id"],
                type=m["type"],
                title=m["title"],
                description="",
                target_repo=m.get("target_repo", ""),
                target_path=m.get("target_path", ""),
                diff="",
                confidence=m.get("confidence", 0),
                pattern_id=m.get("pattern_id", ""),
                pr_url=m.get("pr_url", ""),
            )
        )

    return signals, patterns, mutations


def export_memory(
    *,
    signals: list[Signal] | None = None,
    patterns: list[Pattern] | None = None,
    mutations: list[Mutation] | None = None,
    report_path: Path | None = None,
    agent_dir: Path | None = None,
    include: set[str] | None = None,
) -> str:
    """Export Eva's knowledge as Claude Memory Import text.

    Args:
        signals: Pipeline signals (or loaded from report).
        patterns: Pipeline patterns (or loaded from report).
        mutations: Pipeline mutations (or loaded from report).
        report_path: Path to eva-report.json to load from.
        agent_dir: Path to agent/ directory for memory files.
        include: Set of categories to include. Default: all.
            Options: signals, patterns, mutations, decisions, sessions, evolution-log, history.

    Returns:
        Text block in Claude Memory Import format.
    """
    all_categories = {
        "signals",
        "patterns",
        "mutations",
        "decisions",
        "sessions",
        "evolution-log",
        "history",
    }
    active = include or all_categories

    entries: list[str] = []

    # Load from report if provided
    if report_path and report_path.exists():
        r_signals, r_patterns, r_mutations = load_report(report_path)
        signals = signals or r_signals
        patterns = patterns or r_patterns
        mutations = mutations or r_mutations

    # Pipeline data
    if "signals" in active and signals:
        entries.extend(format_signals(signals))
    if "patterns" in active and patterns:
        entries.extend(format_patterns(patterns))
    if "mutations" in active and mutations:
        entries.extend(format_mutations(mutations))

    # Agent memory files
    if agent_dir and agent_dir.is_dir():
        if "decisions" in active:
            decisions_path = agent_dir / "memory" / "DECISIONS.md"
            if decisions_path.exists():
                entries.extend(format_decisions(decisions_path.read_text()))

        if "sessions" in active:
            sessions_dir = agent_dir / "memory" / "sessions"
            if sessions_dir.is_dir():
                entries.extend(format_sessions(sessions_dir))

        if "evolution-log" in active:
            evo_path = agent_dir / "EVOLUTION_LOG.md"
            if evo_path.exists():
                entries.extend(format_evolution_log(evo_path.read_text()))

        if "history" in active:
            history_path = agent_dir / "memory" / "HISTORY.md"
            if history_path.exists():
                entries.extend(format_history(history_path.read_text()))

    # Sort by date (entries start with [date])
    entries.sort(key=lambda e: e[:12])

    return "\n".join(entries)
