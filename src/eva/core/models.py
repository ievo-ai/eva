"""Core domain models for Eva."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class SignalType(StrEnum):
    """Type of incoming signal."""

    SENTRY_ERROR = "sentry_error"
    GITHUB_ISSUE = "github_issue"
    USER_REVIEW = "user_review"
    EVOLUTION_LOG = "evolution_log"
    PR_COMMENT = "pr_comment"
    RESEARCH_PROPOSAL = "research_proposal"
    TELEGRAM_MESSAGE = "telegram_message"


class Severity(StrEnum):
    """Signal severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MutationType(StrEnum):
    """Type of mutation Eva can propose."""

    ROLE_PATCH = "role_patch"  # Update agent ROLE.md
    SKILL_PATCH = "skill_patch"  # Update agent skill
    MEMORY_UPDATE = "memory_update"  # Update agent memory files
    REGISTRY_UPDATE = "registry_update"  # Update marketplace registry
    CONFIG_PATCH = "config_patch"  # Update platform config
    NEW_AGENT = "new_agent"  # Propose a new agent
    DEPRECATE = "deprecate"  # Deprecate an agent/skill


@dataclass
class Signal:
    """An incoming signal from any source.

    Signals are the raw observations Eva collects from the ecosystem.
    """

    id: str
    type: SignalType
    source: str  # e.g. "sentry", "github:ievo-ai/cli#42"
    title: str
    body: str
    severity: Severity = Severity.MEDIUM
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        """Dedup key."""
        return f"{self.type.value}:{self.source}:{self.id}"


@dataclass
class Pattern:
    """A pattern detected across multiple signals.

    Patterns emerge when Eva sees recurring themes.
    """

    id: str
    title: str
    description: str
    signal_ids: list[str] = field(default_factory=list)
    frequency: int = 1
    severity: Severity = Severity.MEDIUM
    affected_agents: list[str] = field(default_factory=list)
    affected_repos: list[str] = field(default_factory=list)
    suggested_action: str = ""
    confidence: float = 0.0  # 0.0–1.0


@dataclass
class Mutation:
    """A proposed change to the platform.

    Mutations are Eva's output — concrete changes ready to become PRs.
    """

    id: str
    type: MutationType
    title: str
    description: str
    target_repo: str  # e.g. "ievo-ai/marketplace"
    target_path: str  # e.g. "agents/spec-writer/ROLE.md"
    diff: str  # unified diff or full new content
    pattern_id: str = ""  # pattern that triggered this
    confidence: float = 0.0
    approved: bool = False
    pr_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def branch_name(self) -> str:
        """Generate branch name for PR."""
        safe_id = self.id.replace(":", "-").replace("/", "-")
        return f"eva/{safe_id}"


class EvolutionType(StrEnum):
    """Type of evolution entry — superset of pipeline mutations."""

    ROLE_PATCH = "role_patch"
    SKILL_PATCH = "skill_patch"
    MEMORY_UPDATE = "memory_update"
    CONFIG_PATCH = "config_patch"
    MILESTONE = "milestone"
    BEST_PRACTICE = "best_practice"


@dataclass
class EvolutionEntry:
    """A published evolution entry for the ievo.ai feed and Telegram."""

    title: str
    agent: str
    type: EvolutionType
    target: str
    description: str
    confidence: float = 0.0
    pr_url: str = ""
    id: str = ""  # EVO-NNN, auto-assigned by publisher
    date: str = ""  # YYYY-MM-DD, auto-assigned by publisher

    @classmethod
    def from_mutation(cls, mutation: "Mutation") -> "EvolutionEntry":
        """Create an evolution entry from a pipeline mutation."""
        type_map: dict[str, EvolutionType] = {
            t.value: EvolutionType(t.value)
            for t in EvolutionType
            if t.value in {mt.value for mt in MutationType}
        }
        evo_type = type_map.get(mutation.type.value, EvolutionType.ROLE_PATCH)
        return cls(
            title=mutation.title,
            agent="eva",
            type=evo_type,
            target=mutation.target_path,
            description=mutation.description[:200],
            confidence=mutation.confidence,
            pr_url=mutation.pr_url,
        )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to evolutions.json format."""
        return {
            "id": self.id,
            "date": self.date,
            "title": self.title,
            "agent": self.agent,
            "type": self.type.value,
            "target": self.target,
            "description": self.description,
            "confidence": round(self.confidence, 2),
            "pr": self.pr_url or None,
        }
