"""Tests for eva export-memory — Claude Memory Import format."""

from datetime import datetime
from pathlib import Path

from eva.core.models import Mutation, MutationType, Pattern, Severity, Signal, SignalType
from eva.export.memory_export import (
    export_memory,
    format_decisions,
    format_evolution_log,
    format_history,
    format_mutations,
    format_patterns,
    format_signals,
)


def _make_signal(**kwargs) -> Signal:
    defaults = {
        "id": "sig-1",
        "type": SignalType.GITHUB_ISSUE,
        "source": "github:ievo-ai/cli#42",
        "title": "Markdown table parsing fails",
        "body": "Details...",
        "severity": Severity.HIGH,
        "timestamp": datetime(2026, 3, 1, 10, 0, 0),
        "metadata": {"agent": "coder"},
        "tags": ["parsing"],
    }
    defaults.update(kwargs)
    return Signal(**defaults)


def _make_pattern(**kwargs) -> Pattern:
    defaults = {
        "id": "freq:markdown-parsing",
        "title": "Recurring markdown parsing failures",
        "description": "Multiple agents fail on markdown tables",
        "signal_ids": ["sig-1", "sig-2"],
        "frequency": 3,
        "severity": Severity.HIGH,
        "affected_agents": ["coder", "spec-writer"],
        "confidence": 0.75,
    }
    defaults.update(kwargs)
    return Pattern(**defaults)


def _make_mutation(**kwargs) -> Mutation:
    defaults = {
        "id": "mut-0001",
        "type": MutationType.ROLE_PATCH,
        "title": "Add markdown whitespace handling",
        "description": "Update ROLE.md",
        "target_repo": "ievo-ai/marketplace",
        "target_path": "agents/coder/ROLE.md",
        "diff": "...",
        "confidence": 0.68,
        "pattern_id": "freq:markdown-parsing",
    }
    defaults.update(kwargs)
    return Mutation(**defaults)


DECISIONS_MD = """\
# Eva Decisions

| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
| D-001 | 2026-02-28 | Dry-run by default | Safety first | Active |
| D-002 | 2026-02-28 | Min 2 signals per pattern | Avoid false positives | Active |
"""

EVOLUTION_LOG_MD = """\
# Evolution Log

## 2026-03-01: Re-read YAML files between sequential edits

**Context:** While hardening workflow files, two sequential edits corrupted YAML.

**Action:** Added re-read rule to CLAUDE.md for sequential YAML edits.

**Goal:** Prevent YAML corruption.

## 2026-03-01: Include .gitattributes from the first commit

**Context:** CRLF warnings appeared since project creation.

**Action:** Added .gitattributes rule to CLAUDE.md working rules.

**Goal:** Prevent CRLF accumulation.
"""

HISTORY_MD = """\
# Session History

| # | Date | Topic | Key outcome |
|---|------|-------|-------------|
| [001](sessions/001-initial-build.md) | 2026-02-28 | Initial Build | Eva built from scratch |
| [002](sessions/002-curator-build.md) | 2026-02-28 | Curator Build | Level 2 evolution repo |
"""


def test_format_signals() -> None:
    signals = [_make_signal()]
    entries = format_signals(signals)
    assert len(entries) == 1
    assert entries[0].startswith("[2026-03-01]")
    assert "Markdown table parsing fails" in entries[0]
    assert "severity: high" in entries[0]
    assert "in coder" in entries[0]


def test_format_patterns() -> None:
    patterns = [_make_pattern()]
    entries = format_patterns(patterns)
    assert len(entries) == 1
    assert "Recurring markdown parsing failures" in entries[0]
    assert "coder, spec-writer" in entries[0]
    assert "75%" in entries[0]


def test_format_mutations() -> None:
    mutations = [_make_mutation()]
    entries = format_mutations(mutations)
    assert len(entries) == 1
    assert "Add markdown whitespace handling" in entries[0]
    assert "ievo-ai/marketplace" in entries[0]
    assert "68%" in entries[0]


def test_format_decisions() -> None:
    entries = format_decisions(DECISIONS_MD)
    assert len(entries) == 2
    assert entries[0].startswith("[2026-02-28]")
    assert "D-001" in entries[0]
    assert "Dry-run by default" in entries[0]
    assert "Safety first" in entries[0]


def test_format_evolution_log() -> None:
    entries = format_evolution_log(EVOLUTION_LOG_MD)
    assert len(entries) == 2
    assert "[2026-03-01]" in entries[0]
    assert "Re-read YAML files" in entries[0]
    assert "re-read rule" in entries[0].lower() or "Added" in entries[0]
    assert ".gitattributes" in entries[1]


def test_format_history() -> None:
    entries = format_history(HISTORY_MD)
    assert len(entries) == 2
    assert "[2026-02-28]" in entries[0]
    assert "session 001" in entries[0].lower() or "001" in entries[0]
    assert "Eva built from scratch" in entries[0]


def test_export_memory_combined(tmp_path: Path) -> None:
    """All sources combined and sorted by date."""
    # Create agent dir with memory files
    agent_dir = tmp_path / "agent"
    memory_dir = agent_dir / "memory"
    memory_dir.mkdir(parents=True)

    (memory_dir / "DECISIONS.md").write_text(DECISIONS_MD)
    (memory_dir / "HISTORY.md").write_text(HISTORY_MD)
    (agent_dir / "EVOLUTION_LOG.md").write_text(EVOLUTION_LOG_MD)

    signals = [_make_signal()]
    patterns = [_make_pattern()]
    mutations = [_make_mutation()]

    text = export_memory(
        signals=signals,
        patterns=patterns,
        mutations=mutations,
        agent_dir=agent_dir,
    )

    lines = [ln for ln in text.splitlines() if ln.strip()]
    # Should have: 1 signal + 1 pattern + 1 mutation + 2 decisions + 2 evo + 2 history = 9
    assert len(lines) >= 9
    # All lines start with [date]
    for line in lines:
        assert line.startswith("["), f"Line doesn't start with [date]: {line}"


def test_export_memory_include_filter(tmp_path: Path) -> None:
    """--include filtering works."""
    agent_dir = tmp_path / "agent"
    memory_dir = agent_dir / "memory"
    memory_dir.mkdir(parents=True)
    (memory_dir / "DECISIONS.md").write_text(DECISIONS_MD)

    text = export_memory(
        signals=[_make_signal()],
        agent_dir=agent_dir,
        include={"decisions"},
    )

    lines = [ln for ln in text.splitlines() if ln.strip()]
    assert len(lines) == 2  # only 2 decisions
    assert all("decision" in ln.lower() for ln in lines)
