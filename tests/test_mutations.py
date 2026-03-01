"""Tests for mutation engine."""

from eva.core.models import MutationType, Pattern, Severity
from eva.mutations.engine import MutationEngine


def test_generates_role_patch_for_frequency():
    engine = MutationEngine(max_per_run=5)
    patterns = [
        Pattern(
            id="freq:spec-writer-fails",
            title="Recurring: spec-writer fails on empty input",
            description="Seen 3 times",
            signal_ids=["1", "2", "3"],
            frequency=3,
            severity=Severity.HIGH,
            affected_agents=["spec-writer"],
            confidence=0.7,
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 1
    assert mutations[0].type == MutationType.ROLE_PATCH
    assert "spec-writer" in mutations[0].target_path


def test_generates_skill_patch_for_cross_agent():
    engine = MutationEngine(max_per_run=5)
    patterns = [
        Pattern(
            id="cross:validation",
            title="Cross-agent issue: validation",
            description="Tag 'validation' appears in 2 agents",
            signal_ids=["1", "2"],
            frequency=2,
            severity=Severity.HIGH,
            affected_agents=["spec-writer", "coder"],
            confidence=0.6,
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 1
    assert mutations[0].type == MutationType.SKILL_PATCH


def test_respects_max_per_run():
    engine = MutationEngine(max_per_run=2)
    patterns = [
        Pattern(
            id=f"freq:issue-{i}",
            title=f"Issue {i}",
            description="",
            signal_ids=[str(i)],
            frequency=2,
            severity=Severity.MEDIUM,
            affected_agents=[f"agent-{i}"],
            confidence=0.5,
        )
        for i in range(10)
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) <= 2


def test_skips_low_confidence():
    engine = MutationEngine(min_confidence=0.5)
    patterns = [
        Pattern(
            id="freq:low-conf",
            title="Low confidence",
            description="",
            signal_ids=["1", "2"],
            frequency=2,
            severity=Severity.LOW,
            affected_agents=["test"],
            confidence=0.2,  # Below threshold
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 0


def test_generates_memory_update_for_escalation():
    engine = MutationEngine(max_per_run=5)
    patterns = [
        Pattern(
            id="escalation:coder",
            title="Escalating issues in coder",
            description="Severity trending up",
            signal_ids=["1", "2", "3"],
            frequency=3,
            severity=Severity.CRITICAL,
            affected_agents=["coder"],
            confidence=0.7,
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 1
    assert mutations[0].type == MutationType.MEMORY_UPDATE
    assert "coder" in mutations[0].title
    assert "CONTEXT.md" in mutations[0].target_path


def test_escalation_without_agents():
    engine = MutationEngine(max_per_run=5)
    patterns = [
        Pattern(
            id="escalation:unknown",
            title="Escalating issues",
            description="Severity trending up",
            signal_ids=["1", "2", "3"],
            frequency=3,
            severity=Severity.CRITICAL,
            affected_agents=[],
            confidence=0.7,
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 1
    assert "unknown" in mutations[0].title


def test_mutations_property():
    engine = MutationEngine(max_per_run=5)
    assert engine.mutations == []

    patterns = [
        Pattern(
            id="freq:test",
            title="Test",
            description="",
            signal_ids=["1", "2"],
            frequency=2,
            severity=Severity.HIGH,
            affected_agents=["spec-writer"],
            confidence=0.7,
        ),
    ]

    engine.generate(patterns)
    assert len(engine.mutations) >= 1


def test_unknown_pattern_type_produces_no_mutations():
    """Pattern with unrecognized prefix should produce no mutations."""
    engine = MutationEngine(max_per_run=5)
    patterns = [
        Pattern(
            id="unknown:something",
            title="Unknown type",
            description="",
            signal_ids=["1", "2"],
            frequency=2,
            severity=Severity.HIGH,
            affected_agents=["spec-writer"],
            confidence=0.7,
        ),
    ]

    mutations = engine.generate(patterns)
    assert len(mutations) == 0
