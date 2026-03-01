"""Tests for core domain models."""

from eva.core.models import Mutation, MutationType, Severity, Signal, SignalType


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
