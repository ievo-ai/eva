"""Tests for ResearchSource — reads researcher agent proposals."""

from __future__ import annotations

from pathlib import Path

import pytest

from eva.core.config import SourceConfig
from eva.core.models import Severity, SignalType
from eva.sources.research import ResearchSource, _extract_title


SAMPLE_PROPOSAL = """\
# PROP: Add vector search to agent memory

## Source
- **URL**: https://arxiv.org/abs/2026.12345
- **Author**: Test Author
- **Date**: 2026-03-01

## Summary
Vector similarity search over agent memory files using sqlite-vec MCP server.

## Relevance to iEvo
Agents currently read full memory files. Vector search enables selective recall.

## Proposed Change
Add sqlite-vec MCP server dependency to all agents. Index memory files on save.

## Affected Components
- cli/src/ievo/commands/run.py
- marketplace/agents/*/agent.yaml

## Scores
- Applicability: 4/5
- Effort: medium
- Impact: quality
"""


@pytest.fixture
def research_dir(tmp_path: Path) -> Path:
    d = tmp_path / "spec" / "research"
    d.mkdir(parents=True)
    return d


@pytest.fixture
def source(research_dir: Path) -> ResearchSource:
    return ResearchSource(
        config=SourceConfig(enabled=True),
        research_dir=research_dir,
    )


@pytest.mark.asyncio
async def test_poll_empty(source: ResearchSource) -> None:
    signals = await source.poll()
    assert signals == []


@pytest.mark.asyncio
async def test_poll_reads_proposal(
    source: ResearchSource, research_dir: Path,
) -> None:
    (research_dir / "PROP-2026-03-01-vector-search.md").write_text(SAMPLE_PROPOSAL)

    signals = await source.poll()
    assert len(signals) == 1

    s = signals[0]
    assert s.type == SignalType.RESEARCH_PROPOSAL
    assert s.id == "PROP-2026-03-01-vector-search"
    assert "vector search" in s.title.lower()
    assert s.metadata["applicability"] == 4
    assert s.metadata["effort"] == "medium"
    assert s.severity == Severity.HIGH  # applicability 4 boosts to HIGH


@pytest.mark.asyncio
async def test_poll_deduplicates(
    source: ResearchSource, research_dir: Path,
) -> None:
    (research_dir / "PROP-2026-03-01-test.md").write_text(SAMPLE_PROPOSAL)

    signals1 = await source.poll()
    signals2 = await source.poll()
    assert len(signals1) == 1
    assert len(signals2) == 0  # already seen


@pytest.mark.asyncio
async def test_poll_multiple_proposals(
    source: ResearchSource, research_dir: Path,
) -> None:
    (research_dir / "PROP-2026-03-01-a.md").write_text(SAMPLE_PROPOSAL)
    (research_dir / "PROP-2026-03-02-b.md").write_text(
        "# PROP: Better TDD\n\n## Scores\n- Applicability: 3/5\n- Effort: low\n- Impact: speed\n"
    )

    signals = await source.poll()
    assert len(signals) == 2


@pytest.mark.asyncio
async def test_poll_low_effort_high_severity(
    source: ResearchSource, research_dir: Path,
) -> None:
    content = "# PROP: Quick fix\n\n## Scores\n- Applicability: 3/5\n- Effort: low\n- Impact: speed\n"
    (research_dir / "PROP-2026-03-01-quick.md").write_text(content)

    signals = await source.poll()
    assert signals[0].severity == Severity.HIGH  # low effort = high priority


@pytest.mark.asyncio
async def test_poll_no_dir() -> None:
    source = ResearchSource(
        config=SourceConfig(enabled=True),
        research_dir=Path("/nonexistent"),
    )
    signals = await source.poll()
    assert signals == []


@pytest.mark.asyncio
async def test_healthcheck_with_dir(source: ResearchSource) -> None:
    assert await source.healthcheck() is True


@pytest.mark.asyncio
async def test_healthcheck_no_dir() -> None:
    source = ResearchSource(
        config=SourceConfig(enabled=True),
        research_dir=None,
    )
    assert await source.healthcheck() is False


def test_extract_title_prop_format() -> None:
    assert _extract_title("# PROP: My Title\n\nBody", "fallback") == "My Title"


def test_extract_title_h1_format() -> None:
    assert _extract_title("# Just a Title\n\nBody", "fallback") == "Just a Title"


def test_extract_title_fallback() -> None:
    assert _extract_title("No header here", "fallback") == "fallback"
