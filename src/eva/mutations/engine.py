"""Mutation engine — converts patterns into concrete platform changes."""

from dataclasses import dataclass, field
from datetime import datetime

from eva.core.models import Mutation, MutationType, Pattern, Severity


@dataclass
class MutationEngine:
    """Generates mutations (proposed changes) from detected patterns.

    Each mutation is a concrete change to a specific file in a specific repo,
    ready to be turned into a Pull Request.

    Safety rules:
    - Never auto-merge (requires human approval)
    - Max mutations per run is capped
    - Low-confidence mutations are flagged for manual review
    - Mutations include full context for reviewer
    """

    max_per_run: int = 5
    min_confidence: float = 0.3
    _counter: int = 0

    # Generated mutations
    _mutations: list[Mutation] = field(default_factory=list)

    def generate(self, patterns: list[Pattern]) -> list[Mutation]:
        """Generate mutations from patterns.

        Args:
            patterns: Detected patterns to act on.

        Returns:
            List of proposed mutations (capped at max_per_run).
        """
        mutations: list[Mutation] = []

        # Sort patterns by severity × confidence (highest priority first)
        ranked = sorted(
            patterns,
            key=lambda p: (_severity_weight(p.severity) * p.confidence),
            reverse=True,
        )

        for pattern in ranked:
            if len(mutations) >= self.max_per_run:
                break

            if pattern.confidence < self.min_confidence:
                continue

            new_mutations = self._pattern_to_mutations(pattern)
            mutations.extend(new_mutations)

        self._mutations.extend(mutations)
        return mutations[: self.max_per_run]

    def _pattern_to_mutations(self, pattern: Pattern) -> list[Mutation]:
        """Convert a single pattern into one or more mutations."""
        mutations: list[Mutation] = []

        # Strategy: based on pattern type and affected components
        if pattern.id.startswith("freq:") and pattern.affected_agents:
            # Recurring issue in specific agent → patch ROLE.md
            for agent in pattern.affected_agents:
                self._counter += 1
                mutations.append(
                    Mutation(
                        id=f"mut-{self._counter:04d}",
                        type=MutationType.ROLE_PATCH,
                        title=f"Fix recurring issue in {agent}: {pattern.title[:50]}",
                        description=(
                            f"Pattern detected: {pattern.description}\n\n"
                            f"Suggested action: Add a rule to {agent}/ROLE.md "
                            f"to prevent this recurring issue.\n\n"
                            f"Signals: {len(pattern.signal_ids)} occurrences"
                        ),
                        target_repo=_agent_to_repo(agent),
                        target_path=f"agents/{agent}/ROLE.md",
                        diff=_generate_role_patch(agent, pattern),
                        pattern_id=pattern.id,
                        confidence=pattern.confidence,
                    )
                )

        elif pattern.id.startswith("cross:"):
            # Cross-agent issue → update shared skill or create new one
            self._counter += 1
            mutations.append(
                Mutation(
                    id=f"mut-{self._counter:04d}",
                    type=MutationType.SKILL_PATCH,
                    title=f"Cross-agent fix: {pattern.title[:50]}",
                    description=(
                        f"Issue affects {len(pattern.affected_agents)} agents: "
                        f"{', '.join(pattern.affected_agents)}\n\n"
                        f"{pattern.description}\n\n"
                        f"Suggested: Update shared EVO skill to handle this pattern."
                    ),
                    target_repo="ievo-ai/marketplace",
                    target_path="shared/skills/evo/SKILL.md",
                    diff=_generate_skill_patch(pattern),
                    pattern_id=pattern.id,
                    confidence=pattern.confidence * 0.8,  # Lower confidence for cross-agent
                )
            )

        elif pattern.id.startswith("escalation:"):
            # Escalating severity → urgent review + memory update
            agent = pattern.affected_agents[0] if pattern.affected_agents else "unknown"
            self._counter += 1
            mutations.append(
                Mutation(
                    id=f"mut-{self._counter:04d}",
                    type=MutationType.MEMORY_UPDATE,
                    title=f"Urgent: escalating issues in {agent}",
                    description=(
                        f"Severity trending up in {agent}.\n\n"
                        f"{pattern.description}\n\n"
                        f"Action: Update memory/CONTEXT.md with known issues "
                        f"and add guardrails to ROLE.md."
                    ),
                    target_repo=_agent_to_repo(agent),
                    target_path=f"agents/{agent}/memory/CONTEXT.md",
                    diff=_generate_context_update(agent, pattern),
                    pattern_id=pattern.id,
                    confidence=pattern.confidence,
                )
            )

        return mutations

    @property
    def mutations(self) -> list[Mutation]:
        """All generated mutations."""
        return self._mutations


def _severity_weight(s: Severity) -> float:
    return {
        Severity.INFO: 0.1,
        Severity.LOW: 0.3,
        Severity.MEDIUM: 0.5,
        Severity.HIGH: 0.8,
        Severity.CRITICAL: 1.0,
    }.get(s, 0.5)


def _agent_to_repo(agent: str) -> str:
    """Map agent name to marketplace repo."""
    return "ievo-ai/marketplace"


def _generate_role_patch(agent: str, pattern: Pattern) -> str:
    """Generate a ROLE.md patch suggestion."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    return (
        f"# Eva-generated patch for {agent}/ROLE.md\n"
        f"# Date: {date}\n"
        f"# Pattern: {pattern.id}\n"
        f"# Confidence: {pattern.confidence:.0%}\n"
        f"#\n"
        f"# Add to Rules section:\n"
        f"#\n"
        f"# ## Eva Rule (auto-generated)\n"
        f"# \n"
        f"# Based on {pattern.frequency} occurrences of: {pattern.title}\n"
        f"# {pattern.suggested_action or 'Review and add appropriate guardrail.'}\n"
    )


def _generate_skill_patch(pattern: Pattern) -> str:
    """Generate a shared skill patch suggestion."""
    return (
        f"# Eva-generated skill update\n"
        f"# Pattern: {pattern.id}\n"
        f"# Affects: {', '.join(pattern.affected_agents)}\n"
        f"#\n"
        f"# Suggested addition to EVO SKILL.md:\n"
        f"#\n"
        f"# ## Known Pattern: {pattern.title}\n"
        f"# When encountering this pattern, apply the following:\n"
        f"# 1. Check if the issue is in your ROLE.md rules\n"
        f"# 2. If not, classify and add via EVO workflow\n"
        f"# 3. Cross-reference with other agents' evolution logs\n"
    )


def _generate_context_update(agent: str, pattern: Pattern) -> str:
    """Generate a memory/CONTEXT.md update."""
    date = datetime.utcnow().strftime("%Y-%m-%d")
    return (
        f"# Eva-generated context update for {agent}\n"
        f"# Date: {date}\n"
        f"#\n"
        f"# Add to Notes section:\n"
        f"#\n"
        f"# ⚠️ Eva Alert ({date}): Escalating issues detected.\n"
        f"# {pattern.description}\n"
        f"# Action needed: Review recent evolution log and address root causes.\n"
    )
