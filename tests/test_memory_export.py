"""Tests for Eva memory export module."""

import json
from datetime import UTC, datetime

from eva.core.models import (
    Mutation,
    MutationType,
    Pattern,
    Severity,
    Signal,
    SignalType,
)
from eva.export.memory_export import (
    export_memory,
    format_decisions,
    format_evolution_log,
    format_history,
    format_mutations,
    format_patterns,
    format_sessions,
    format_signals,
    load_report,
)


def _make_signal(**kwargs) -> Signal:
    defaults = {
        "id": "sig-1",
        "type": SignalType.GITHUB_ISSUE,
        "source": "github:repo#1",
        "title": "Test signal",
        "body": "body",
        "severity": Severity.HIGH,
        "timestamp": datetime(2026, 3, 1, tzinfo=UTC),
        "metadata": {"agent": "spec-writer"},
    }
    defaults.update(kwargs)
    return Signal(**defaults)


def _make_pattern(**kwargs) -> Pattern:
    defaults = {
        "id": "freq:test",
        "title": "Test pattern",
        "description": "desc",
        "confidence": 0.7,
        "frequency": 3,
        "affected_agents": ["spec-writer", "coder"],
    }
    defaults.update(kwargs)
    return Pattern(**defaults)


def _make_mutation(**kwargs) -> Mutation:
    defaults = {
        "id": "mut-0001",
        "type": MutationType.ROLE_PATCH,
        "title": "Fix issue",
        "description": "desc",
        "target_repo": "ievo-ai/marketplace",
        "target_path": "agents/spec-writer/ROLE.md",
        "diff": "# patch",
        "confidence": 0.7,
    }
    defaults.update(kwargs)
    return Mutation(**defaults)


class TestFormatSignals:
    def test_basic_signal(self):
        entries = format_signals([_make_signal()])
        assert len(entries) == 1
        assert "[2026-03-01]" in entries[0]
        assert "Test signal" in entries[0]
        assert "in spec-writer" in entries[0]
        assert "severity: high" in entries[0]

    def test_signal_without_agent(self):
        entries = format_signals([_make_signal(metadata={})])
        assert len(entries) == 1
        assert "in " not in entries[0].split("source:")[0]

    def test_empty_signals(self):
        assert format_signals([]) == []


class TestFormatPatterns:
    def test_basic_pattern(self):
        entries = format_patterns([_make_pattern()])
        assert len(entries) == 1
        assert "Test pattern" in entries[0]
        assert "spec-writer, coder" in entries[0]
        assert "70%" in entries[0]

    def test_pattern_without_agents(self):
        entries = format_patterns([_make_pattern(affected_agents=[])])
        assert "unknown" in entries[0]

    def test_empty_patterns(self):
        assert format_patterns([]) == []


class TestFormatMutations:
    def test_basic_mutation(self):
        entries = format_mutations([_make_mutation()])
        assert len(entries) == 1
        assert "Fix issue" in entries[0]
        assert "role_patch" in entries[0]

    def test_mutation_with_pr_url(self):
        entries = format_mutations([_make_mutation(pr_url="https://github.com/pr/1")])
        assert "PR: https://github.com/pr/1" in entries[0]

    def test_mutation_without_pr_url(self):
        entries = format_mutations([_make_mutation(pr_url="")])
        assert "PR:" not in entries[0]

    def test_empty_mutations(self):
        assert format_mutations([]) == []


class TestFormatDecisions:
    def test_parses_table(self):
        md = """\
| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
| D-001 | 2026-02-28 | Dry-run by default | Safety first | Active |
| D-002 | 2026-02-28 | Min 2 signals | Avoid false positives | Active |
"""
        entries = format_decisions(md)
        assert len(entries) == 2
        assert "D-001" in entries[0]
        assert "Dry-run by default" in entries[0]
        assert "Active" in entries[0]

    def test_skips_header_rows(self):
        md = """\
| ID | Date | Decision | Rationale | Status |
|----|------|----------|-----------|--------|
"""
        entries = format_decisions(md)
        assert entries == []

    def test_skips_malformed_rows(self):
        md = "| bad | row |"
        entries = format_decisions(md)
        assert entries == []

    def test_handles_missing_status(self):
        md = "| D-001 | 2026-02-28 | Decision | Rationale |"
        entries = format_decisions(md)
        assert len(entries) == 1
        assert "Active" in entries[0]

    def test_non_table_content(self):
        md = "# Decisions\n\nSome text."
        entries = format_decisions(md)
        assert entries == []


class TestFormatSessions:
    def test_parses_session_files(self, tmp_path):
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        (sessions / "001-initial-build.md").write_text(
            "# Session 001 — Initial Build\n\n"
            "**Date:** 2026-02-28\n\n"
            "## Discussion Summary\n\n"
            "Eva built from scratch with 33 files and ~2400 LOC."
        )
        entries = format_sessions(sessions)
        assert len(entries) == 1
        assert "2026-02-28" in entries[0]
        assert "001" in entries[0]
        assert "Initial Build" in entries[0]

    def test_skips_non_session_files(self, tmp_path):
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        (sessions / "README.md").write_text("# Readme")
        entries = format_sessions(sessions)
        assert entries == []

    def test_nonexistent_dir(self, tmp_path):
        entries = format_sessions(tmp_path / "nonexistent")
        assert entries == []

    def test_session_without_long_line(self, tmp_path):
        sessions = tmp_path / "sessions"
        sessions.mkdir()
        (sessions / "002-short.md").write_text("# Session 002\n\n**Date:** 2026-03-01\n\nShort.")
        entries = format_sessions(sessions)
        assert len(entries) == 1
        assert "Short" in entries[0]


class TestFormatEvolutionLog:
    def test_parses_entries(self):
        log = """\
# Evolution Log

## 2026-03-01: Re-read YAML files between sequential edits

**Context:** YAML corruption from blind edits.

**Action:** Added "Editing rules" section to CLAUDE.md.

**Goal:** Prevent YAML file corruption.

## 2026-03-01: Always assignee on issues

**Context:** Created issue without --assignee.

**Action:** Updated CLAUDE.md working rules.

**Goal:** Ensure issues are properly assigned.
"""
        entries = format_evolution_log(log)
        assert len(entries) == 2
        assert "Re-read YAML" in entries[0]
        assert 'Added "Editing rules"' in entries[0]
        assert "assignee" in entries[1]

    def test_entry_without_action(self):
        log = "## 2026-03-01: Simple entry\n\n**Context:** Something happened.\n"
        entries = format_evolution_log(log)
        assert len(entries) == 1
        assert "Simple entry" in entries[0]

    def test_empty_log(self):
        assert format_evolution_log("# Evolution Log\n") == []

    def test_single_entry(self):
        log = "## 2026-03-01: Single\n\n**Action:** Did something.\n"
        entries = format_evolution_log(log)
        assert len(entries) == 1


class TestFormatHistory:
    def test_parses_table(self):
        md = """\
| # | Date | Topic | Key outcome |
|---|------|-------|-------------|
| [001](sessions/001.md) | 2026-02-28 | Build | Built from scratch |
| 002 | 2026-03-01 | Fix | Fixed bugs |
"""
        entries = format_history(md)
        assert len(entries) == 2
        assert "001" in entries[0]
        assert "Build" in entries[0]

    def test_skips_header(self):
        md = "| # | Date | Topic | Key outcome |\n|---|------|-------|-------------|"
        entries = format_history(md)
        assert entries == []

    def test_skips_malformed(self):
        md = "| short |"
        entries = format_history(md)
        assert entries == []


class TestLoadReport:
    def test_loads_full_report(self, tmp_path):
        report = {
            "signals": [
                {
                    "id": "sig-1",
                    "type": "github_issue",
                    "source": "github:repo#1",
                    "title": "Bug",
                    "severity": "high",
                    "tags": ["bug"],
                }
            ],
            "patterns": [
                {
                    "id": "freq:test",
                    "title": "Pattern",
                    "confidence": 0.7,
                    "severity": "medium",
                    "signal_ids": ["sig-1"],
                    "affected_repos": ["repo"],
                }
            ],
            "mutations": [
                {
                    "id": "mut-0001",
                    "type": "role_patch",
                    "title": "Fix",
                    "target_repo": "repo",
                    "target_path": "path",
                    "confidence": 0.7,
                    "pattern_id": "freq:test",
                    "pr_url": "https://url",
                }
            ],
        }
        path = tmp_path / "report.json"
        path.write_text(json.dumps(report))

        signals, patterns, mutations = load_report(path)
        assert len(signals) == 1
        assert signals[0].title == "Bug"
        assert len(patterns) == 1
        assert patterns[0].confidence == 0.7
        assert len(mutations) == 1
        assert mutations[0].pr_url == "https://url"

    def test_loads_empty_report(self, tmp_path):
        path = tmp_path / "report.json"
        path.write_text("{}")

        signals, patterns, mutations = load_report(path)
        assert signals == []
        assert patterns == []
        assert mutations == []


class TestExportMemory:
    def test_export_with_signals(self):
        result = export_memory(signals=[_make_signal()], include={"signals"})
        assert "Test signal" in result

    def test_export_with_patterns(self):
        result = export_memory(patterns=[_make_pattern()], include={"patterns"})
        assert "Test pattern" in result

    def test_export_with_mutations(self):
        result = export_memory(mutations=[_make_mutation()], include={"mutations"})
        assert "Fix issue" in result

    def test_export_from_report(self, tmp_path):
        report = {
            "signals": [
                {
                    "id": "sig-1",
                    "type": "github_issue",
                    "source": "test",
                    "title": "Report Signal",
                    "severity": "medium",
                    "tags": [],
                }
            ],
            "patterns": [],
            "mutations": [],
        }
        path = tmp_path / "report.json"
        path.write_text(json.dumps(report))

        # load_report creates Signal with string values for enums;
        # format_signals uses .value on StrEnum which works on strings too in StrEnum
        result = export_memory(report_path=path, include={"signals"})
        assert "Report Signal" in result

    def test_export_report_does_not_override_provided(self, tmp_path):
        report = {"signals": [], "patterns": [], "mutations": []}
        path = tmp_path / "report.json"
        path.write_text(json.dumps(report))

        result = export_memory(
            signals=[_make_signal()],
            report_path=path,
            include={"signals"},
        )
        assert "Test signal" in result

    def test_export_with_agent_dir(self, tmp_path):
        agent = tmp_path / "agent"
        agent.mkdir()
        memory = agent / "memory"
        memory.mkdir()
        (memory / "DECISIONS.md").write_text(
            "| ID | Date | Decision | Rationale | Status |\n"
            "|----|------|----------|-----------|--------|\n"
            "| D-001 | 2026-02-28 | Test decision | Reason | Active |\n"
        )
        (memory / "HISTORY.md").write_text(
            "| # | Date | Topic | Key outcome |\n"
            "|---|------|-------|-------------|\n"
            "| 001 | 2026-02-28 | Build | Built everything |\n"
        )
        sessions = memory / "sessions"
        sessions.mkdir()
        (sessions / "001-build.md").write_text(
            "# Session 001\n\n**Date:** 2026-02-28\n\nBuilt everything from scratch with lots of code."
        )
        (agent / "EVOLUTION_LOG.md").write_text(
            "## 2026-03-01: Test evo\n\n**Action:** Did something.\n"
        )

        result = export_memory(agent_dir=agent)
        assert "D-001" in result
        assert "Test evo" in result
        assert "001" in result

    def test_export_empty(self):
        result = export_memory()
        assert result == ""

    def test_export_respects_include_filter(self):
        result = export_memory(
            signals=[_make_signal()],
            patterns=[_make_pattern()],
            include={"patterns"},
        )
        assert "Test pattern" in result
        assert "Test signal" not in result

    def test_export_nonexistent_report(self, tmp_path):
        result = export_memory(report_path=tmp_path / "nonexistent.json")
        assert result == ""

    def test_export_agent_dir_nonexistent(self, tmp_path):
        result = export_memory(agent_dir=tmp_path / "nonexistent")
        assert result == ""

    def test_export_agent_dir_missing_files(self, tmp_path):
        agent = tmp_path / "agent"
        agent.mkdir()
        memory = agent / "memory"
        memory.mkdir()
        result = export_memory(agent_dir=agent)
        assert result == ""

    def test_export_agent_dir_with_include_filter(self, tmp_path):
        """Test that include filter works for agent_dir categories."""
        agent = tmp_path / "agent"
        agent.mkdir()
        memory = agent / "memory"
        memory.mkdir()
        (memory / "DECISIONS.md").write_text(
            "| ID | Date | Decision | Rationale | Status |\n"
            "|----|------|----------|-----------|--------|\n"
            "| D-001 | 2026-02-28 | Test | Reason | Active |\n"
        )
        (memory / "HISTORY.md").write_text(
            "| # | Date | Topic | Key outcome |\n"
            "|---|------|-------|-------------|\n"
            "| 001 | 2026-02-28 | Build | Built |\n"
        )
        sessions = memory / "sessions"
        sessions.mkdir()
        (sessions / "001-build.md").write_text(
            "# Session 001\n\n"
            "**Date:** 2026-02-28\n\n"
            "Built everything from scratch with lots of code.\n"
        )
        (agent / "EVOLUTION_LOG.md").write_text(
            "## 2026-03-01: Evo entry\n\n**Action:** Did something.\n"
        )

        # Only include decisions — should skip sessions, evolution-log, history
        result = export_memory(agent_dir=agent, include={"decisions"})
        assert "D-001" in result
        assert "Evo entry" not in result
        assert "001" not in result or "D-001" in result

    def test_export_sessions_short_lines_fallback(self, tmp_path):
        """Session file with only short lines uses topic as summary."""
        agent = tmp_path / "agent"
        agent.mkdir()
        memory = agent / "memory"
        memory.mkdir()
        sessions = memory / "sessions"
        sessions.mkdir()
        (sessions / "001-short.md").write_text(
            "# Session 001\n\n**Date:** 2026-03-01\n\nShort.\nAlso short.\n"
        )

        result = export_memory(agent_dir=agent, include={"sessions"})
        assert "Short" in result
