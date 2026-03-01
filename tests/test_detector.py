"""Tests for pattern detection."""

from eva.analysis.detector import PatternDetector
from eva.core.models import Severity, Signal, SignalType


def _make_signal(id: str, title: str, agent: str = "", tags: list[str] | None = None) -> Signal:
    return Signal(
        id=id,
        type=SignalType.GITHUB_ISSUE,
        source=f"test:{id}",
        title=title,
        body="",
        metadata={"agent": agent, "repo_label": agent} if agent else {},
        tags=tags or [],
    )


def test_frequency_detection():
    """Signals with same title prefix should form a pattern."""
    detector = PatternDetector(min_frequency=2)

    signals = [
        _make_signal("1", "spec-writer fails on empty input", agent="spec-writer"),
        _make_signal("2", "spec-writer fails on empty input again", agent="spec-writer"),
        _make_signal("3", "spec-writer fails on empty input third time", agent="spec-writer"),
    ]

    patterns = detector.ingest(signals)
    assert len(patterns) >= 1
    freq_patterns = [p for p in patterns if p.id.startswith("freq:")]
    assert len(freq_patterns) >= 1
    assert freq_patterns[0].frequency >= 2


def test_no_pattern_for_single_signal():
    """A single signal should not form a pattern."""
    detector = PatternDetector(min_frequency=2)
    signals = [_make_signal("1", "unique error title xyz")]
    patterns = detector.ingest(signals)
    freq_patterns = [p for p in patterns if p.id.startswith("freq:")]
    assert len(freq_patterns) == 0


def test_cross_agent_detection():
    """Same tag in multiple agents should form a cross-agent pattern."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        _make_signal("1", "A", agent="spec-writer", tags=["validation"]),
        _make_signal("2", "B", agent="coder", tags=["validation"]),
    ]

    patterns = detector.ingest(signals)
    cross = [p for p in patterns if p.id.startswith("cross:")]
    assert len(cross) >= 1
    assert "spec-writer" in cross[0].affected_agents
    assert "coder" in cross[0].affected_agents


def test_escalation_detection():
    """Increasing severity signals should trigger escalation pattern."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        Signal(
            id="1",
            type=SignalType.GITHUB_ISSUE,
            source="t:1",
            title="Minor issue",
            body="",
            severity=Severity.LOW,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="2",
            type=SignalType.GITHUB_ISSUE,
            source="t:2",
            title="Medium issue",
            body="",
            severity=Severity.MEDIUM,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="3",
            type=SignalType.GITHUB_ISSUE,
            source="t:3",
            title="Critical issue",
            body="",
            severity=Severity.CRITICAL,
            metadata={"agent": "coder"},
            tags=[],
        ),
    ]

    patterns = detector.ingest(signals)
    escalation = [p for p in patterns if p.id.startswith("escalation:")]
    assert len(escalation) >= 1
    assert escalation[0].severity == Severity.CRITICAL
