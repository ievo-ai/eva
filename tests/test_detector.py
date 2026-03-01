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


def test_frequency_update_existing_pattern():
    """Second ingest with same title should update existing pattern."""
    detector = PatternDetector(min_frequency=2)

    first_batch = [
        _make_signal("1", "spec-writer fails on empty input", agent="spec-writer"),
        _make_signal("2", "spec-writer fails on empty input again", agent="spec-writer"),
    ]
    patterns1 = detector.ingest(first_batch)
    assert len([p for p in patterns1 if p.id.startswith("freq:")]) >= 1

    second_batch = [
        _make_signal("3", "spec-writer fails on empty input third", agent="spec-writer"),
        _make_signal("4", "spec-writer fails on empty input fourth", agent="spec-writer"),
    ]
    patterns2 = detector.ingest(second_batch)
    freq_patterns = [p for p in patterns2 if p.id.startswith("freq:")]
    assert len(freq_patterns) >= 1
    # Updated pattern should have more signal IDs
    assert freq_patterns[0].frequency > 2


def test_cross_agent_skips_generic_tags():
    """Generic tags like 'github', 'sentry' should not form cross-agent patterns."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        _make_signal("1", "A", agent="spec-writer", tags=["github", "sentry"]),
        _make_signal("2", "B", agent="coder", tags=["github", "sentry"]),
    ]

    patterns = detector.ingest(signals)
    cross = [p for p in patterns if p.id.startswith("cross:")]
    assert len(cross) == 0


def test_cross_agent_skips_single_agent_tag():
    """Tags only seen in one agent should not form cross-agent patterns."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        _make_signal("1", "A", agent="spec-writer", tags=["validation"]),
        _make_signal("2", "B", agent="spec-writer", tags=["validation"]),
    ]

    patterns = detector.ingest(signals)
    cross = [p for p in patterns if p.id.startswith("cross:")]
    assert len(cross) == 0


def test_cross_agent_skips_existing_pattern():
    """Same cross-agent pattern should not be detected twice."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        _make_signal("1", "A", agent="spec-writer", tags=["validation"]),
        _make_signal("2", "B", agent="coder", tags=["validation"]),
    ]

    patterns1 = detector.ingest(signals)
    cross1 = [p for p in patterns1 if p.id.startswith("cross:")]
    assert len(cross1) == 1

    # Second ingest with same tag — should not duplicate
    signals2 = [
        _make_signal("3", "C", agent="spec-writer", tags=["validation"]),
        _make_signal("4", "D", agent="architect", tags=["validation"]),
    ]
    patterns2 = detector.ingest(signals2)
    cross2 = [p for p in patterns2 if p.id.startswith("cross:")]
    assert len(cross2) == 0


def test_escalation_skips_existing_pattern():
    """Same escalation pattern should not be detected twice."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        Signal(
            id="1",
            type=SignalType.GITHUB_ISSUE,
            source="t:1",
            title="Low",
            body="",
            severity=Severity.LOW,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="2",
            type=SignalType.GITHUB_ISSUE,
            source="t:2",
            title="Med",
            body="",
            severity=Severity.MEDIUM,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="3",
            type=SignalType.GITHUB_ISSUE,
            source="t:3",
            title="Crit",
            body="",
            severity=Severity.CRITICAL,
            metadata={"agent": "coder"},
            tags=[],
        ),
    ]

    patterns1 = detector.ingest(signals)
    esc1 = [p for p in patterns1 if p.id.startswith("escalation:")]
    assert len(esc1) == 1

    # Second batch for same agent
    more = [
        Signal(
            id="4",
            type=SignalType.GITHUB_ISSUE,
            source="t:4",
            title="Low2",
            body="",
            severity=Severity.LOW,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="5",
            type=SignalType.GITHUB_ISSUE,
            source="t:5",
            title="Crit2",
            body="",
            severity=Severity.CRITICAL,
            metadata={"agent": "coder"},
            tags=[],
        ),
    ]
    patterns2 = detector.ingest(more)
    esc2 = [p for p in patterns2 if p.id.startswith("escalation:")]
    assert len(esc2) == 0


def test_patterns_property():
    """The patterns property should return all detected patterns."""
    detector = PatternDetector(min_frequency=2)

    signals = [
        _make_signal("1", "spec-writer fails on empty input", agent="spec-writer"),
        _make_signal("2", "spec-writer fails on empty input again", agent="spec-writer"),
    ]
    detector.ingest(signals)

    all_patterns = detector.patterns
    assert len(all_patterns) >= 1
    assert all(hasattr(p, "id") for p in all_patterns)


def test_cross_agent_signal_without_agent():
    """Signals without agent metadata should be skipped in cross-agent detection."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        _make_signal("1", "A", tags=["validation"]),
        _make_signal("2", "B", tags=["validation"]),
    ]

    patterns = detector.ingest(signals)
    cross = [p for p in patterns if p.id.startswith("cross:")]
    assert len(cross) == 0


def test_escalation_not_triggered_small_delta():
    """Agent with 3+ signals but small severity delta should not trigger escalation."""
    detector = PatternDetector(min_frequency=1)

    signals = [
        Signal(
            id="1",
            type=SignalType.GITHUB_ISSUE,
            source="t:1",
            title="A",
            body="",
            severity=Severity.MEDIUM,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="2",
            type=SignalType.GITHUB_ISSUE,
            source="t:2",
            title="B",
            body="",
            severity=Severity.MEDIUM,
            metadata={"agent": "coder"},
            tags=[],
        ),
        Signal(
            id="3",
            type=SignalType.GITHUB_ISSUE,
            source="t:3",
            title="C",
            body="",
            severity=Severity.HIGH,
            metadata={"agent": "coder"},
            tags=[],
        ),
    ]

    patterns = detector.ingest(signals)
    escalation = [p for p in patterns if p.id.startswith("escalation:")]
    # Delta is only 1 (MEDIUM=2 to HIGH=3), needs >= 2
    assert len(escalation) == 0
