"""Core domain models for Eva."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SignalType(str, Enum):
    """Type of incoming signal."""

    SENTRY_ERROR = "sentry_error"
    GITHUB_ISSUE = "github_issue"
    USER_REVIEW = "user_review"
    EVOLUTION_LOG = "evolution_log"
    PR_COMMENT = "pr_comment"


class Severity(str, Enum):
    """Signal severity."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class MutationType(str, Enum):
    """Type of mutation Eva can propose."""

    ROLE_PATCH = "role_patch"           # Update agent ROLE.md
    SKILL_PATCH = "skill_patch"         # Update agent skill
    MEMORY_UPDATE = "memory_update"     # Update agent memory files
    REGISTRY_UPDATE = "registry_update" # Update marketplace registry
    CONFIG_PATCH = "config_patch"       # Update platform config
    NEW_AGENT = "new_agent"             # Propose a new agent
    DEPRECATE = "deprecate"             # Deprecate an agent/skill


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
    target_repo: str          # e.g. "ievo-ai/marketplace"
    target_path: str          # e.g. "agents/spec-writer/ROLE.md"
    diff: str                 # unified diff or full new content
    pattern_id: str = ""      # pattern that triggered this
    confidence: float = 0.0
    approved: bool = False
    pr_url: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def branch_name(self) -> str:
        """Generate branch name for PR."""
        safe_id = self.id.replace(":", "-").replace("/", "-")
        return f"eva/{safe_id}"
