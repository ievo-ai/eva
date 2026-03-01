"""Tests for core domain models."""

from eva.core.models import (
    EvolutionEntry,
    EvolutionType,
    Mutation,
    MutationType,
    Severity,
    Signal,
    SignalType,
)


def test_signal_key():
    s = Signal(
        id="42",
        type=SignalType.GITHUB_ISSUE,
        source="github:ievo-ai/cli#42",
        title="Test",
        body="",
    )
    assert s.key == "github_issue:github:ievo-ai/cli#42:42"


def test_signal_default_severity():
    s = Signal(id="1", type=SignalType.SENTRY_ERROR, source="sentry", title="T", body="")
    assert s.severity == Severity.MEDIUM


def test_mutation_branch_name():
    m = Mutation(
        id="mut-0001",
        type=MutationType.ROLE_PATCH,
        title="Fix",
        description="",
        target_repo="ievo-ai/marketplace",
        target_path="agents/spec-writer/ROLE.md",
        diff="",
    )
    assert m.branch_name == "eva/mut-0001"


# --- EvolutionType ---


def test_evolution_type_values():
    assert EvolutionType.ROLE_PATCH == "role_patch"
    assert EvolutionType.MILESTONE == "milestone"
    assert EvolutionType.BEST_PRACTICE == "best_practice"
    assert EvolutionType.SKILL_PATCH == "skill_patch"
    assert EvolutionType.MEMORY_UPDATE == "memory_update"
    assert EvolutionType.CONFIG_PATCH == "config_patch"


# --- EvolutionEntry ---


def test_evolution_entry_defaults():
    e = EvolutionEntry(
        title="Test",
        agent="eva",
        type=EvolutionType.MILESTONE,
        target="ievo-ai/*",
        description="A milestone.",
    )
    assert e.confidence == 0.0
    assert e.pr_url == ""
    assert e.id == ""
    assert e.date == ""


def test_evolution_entry_from_mutation():
    m = Mutation(
        id="mut-0001",
        type=MutationType.ROLE_PATCH,
        title="Fix format validation",
        description="Added rule to prevent format errors across all agents",
        target_repo="ievo-ai/marketplace",
        target_path="agents/spec-writer/ROLE.md",
        diff="# patch",
        confidence=0.75,
        pr_url="https://github.com/ievo-ai/marketplace/pull/1",
    )
    e = EvolutionEntry.from_mutation(m)
    assert e.title == "Fix format validation"
    assert e.agent == "eva"
    assert e.type == EvolutionType.ROLE_PATCH
    assert e.target == "agents/spec-writer/ROLE.md"
    assert e.confidence == 0.75
    assert e.pr_url == "https://github.com/ievo-ai/marketplace/pull/1"


def test_evolution_entry_from_mutation_unmapped_type():
    m = Mutation(
        id="mut-0002",
        type=MutationType.NEW_AGENT,
        title="New agent",
        description="Propose new agent",
        target_repo="ievo-ai/marketplace",
        target_path="agents/new-agent/ROLE.md",
        diff="",
    )
    e = EvolutionEntry.from_mutation(m)
    assert e.type == EvolutionType.ROLE_PATCH  # fallback


def test_evolution_entry_from_mutation_truncates_description():
    m = Mutation(
        id="mut-0003",
        type=MutationType.SKILL_PATCH,
        title="Long desc",
        description="x" * 300,
        target_repo="ievo-ai/marketplace",
        target_path="agents/coder/ROLE.md",
        diff="",
    )
    e = EvolutionEntry.from_mutation(m)
    assert len(e.description) == 200


def test_evolution_entry_to_dict():
    e = EvolutionEntry(
        title="Test evolution",
        agent="spec-writer",
        type=EvolutionType.BEST_PRACTICE,
        target="agents/spec-writer/ROLE.md",
        description="A best practice.",
        confidence=0.8567,
        pr_url="https://github.com/ievo-ai/marketplace/pull/5",
        id="EVO-042",
        date="2026-03-01",
    )
    d = e.to_dict()
    assert d["id"] == "EVO-042"
    assert d["date"] == "2026-03-01"
    assert d["title"] == "Test evolution"
    assert d["agent"] == "spec-writer"
    assert d["type"] == "best_practice"
    assert d["target"] == "agents/spec-writer/ROLE.md"
    assert d["description"] == "A best practice."
    assert d["confidence"] == 0.86  # rounded
    assert d["pr"] == "https://github.com/ievo-ai/marketplace/pull/5"


def test_evolution_entry_to_dict_no_pr():
    e = EvolutionEntry(
        title="No PR",
        agent="eva",
        type=EvolutionType.MILESTONE,
        target="ievo-ai/*",
        description="Milestone without PR.",
    )
    d = e.to_dict()
    assert d["pr"] is None
