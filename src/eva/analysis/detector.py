"""Pattern detection — finds recurring themes across signals."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

from eva.core.models import Pattern, Signal, Severity


@dataclass
class PatternDetector:
    """Detects patterns from a stream of signals.

    Pattern detection strategies:
    1. Frequency — same error/issue appearing repeatedly
    2. Clustering — related signals from same agent/repo
    3. Escalation — severity increasing over time
    4. Cross-agent — same issue affecting multiple agents
    """

    # Minimum signals to form a pattern
    min_frequency: int = 2

    # Existing patterns (persisted between runs)
    _patterns: dict[str, Pattern] = field(default_factory=dict)

    # Signal index
    _by_agent: dict[str, list[Signal]] = field(default_factory=lambda: defaultdict(list))
    _by_type: dict[str, list[Signal]] = field(default_factory=lambda: defaultdict(list))
    _by_tag: dict[str, list[Signal]] = field(default_factory=lambda: defaultdict(list))

    def ingest(self, signals: list[Signal]) -> list[Pattern]:
        """Process new signals and return newly detected patterns.

        Args:
            signals: New signals to analyze.

        Returns:
            List of newly detected or updated patterns.
        """
        # Index signals
        for s in signals:
            self._by_type[s.type.value].append(s)
            for tag in s.tags:
                self._by_tag[tag].append(s)
            # Extract agent name from metadata or tags
            agent = s.metadata.get("agent", "")
            if agent:
                self._by_agent[agent].append(s)
            repo_label = s.metadata.get("repo_label", "")
            if repo_label:
                self._by_agent[repo_label].append(s)

        new_patterns: list[Pattern] = []

        # Strategy 1: Frequency — group similar signals by title keywords
        new_patterns.extend(self._detect_frequency(signals))

        # Strategy 2: Cross-agent — same tags across different agents
        new_patterns.extend(self._detect_cross_agent(signals))

        # Strategy 3: Escalation — severity trending up
        new_patterns.extend(self._detect_escalation(signals))

        return new_patterns

    def _detect_frequency(self, signals: list[Signal]) -> list[Pattern]:
        """Find signals with similar titles appearing repeatedly."""
        patterns: list[Pattern] = []

        # Group by simplified title (lowercase, first 5 words)
        title_groups: dict[str, list[Signal]] = defaultdict(list)
        for s in signals:
            key = " ".join(s.title.lower().split()[:5])
            title_groups[key].append(s)

        for key, group in title_groups.items():
            if len(group) < self.min_frequency:
                continue

            pid = f"freq:{key[:40]}"
            if pid in self._patterns:
                # Update existing
                p = self._patterns[pid]
                p.signal_ids.extend(s.id for s in group)
                p.frequency = len(p.signal_ids)
                patterns.append(p)
            else:
                # New pattern
                p = Pattern(
                    id=pid,
                    title=f"Recurring: {group[0].title[:60]}",
                    description=f"Seen {len(group)} times across signals",
                    signal_ids=[s.id for s in group],
                    frequency=len(group),
                    severity=max(s.severity for s in group),
                    affected_agents=list({s.metadata.get("agent", "") for s in group} - {""}),
                    affected_repos=list({s.metadata.get("repo", "") for s in group} - {""}),
                    confidence=min(0.3 + len(group) * 0.1, 0.9),
                )
                self._patterns[pid] = p
                patterns.append(p)

        return patterns

    def _detect_cross_agent(self, signals: list[Signal]) -> list[Pattern]:
        """Find same issue affecting multiple agents."""
        patterns: list[Pattern] = []

        # Check tags shared by multiple agents
        tag_agents: dict[str, set[str]] = defaultdict(set)
        tag_signals: dict[str, list[Signal]] = defaultdict(list)

        for s in signals:
            agent = s.metadata.get("agent", s.metadata.get("repo_label", ""))
            if not agent:
                continue
            for tag in s.tags:
                if tag in ("github", "sentry", "evo", "review"):
                    continue  # Skip generic tags
                tag_agents[tag].add(agent)
                tag_signals[tag].append(s)

        for tag, agents in tag_agents.items():
            if len(agents) < 2:
                continue

            pid = f"cross:{tag}"
            if pid in self._patterns:
                continue

            group = tag_signals[tag]
            p = Pattern(
                id=pid,
                title=f"Cross-agent issue: {tag}",
                description=f"Tag '{tag}' appears in {len(agents)} agents: {', '.join(sorted(agents))}",
                signal_ids=[s.id for s in group],
                frequency=len(group),
                severity=Severity.HIGH,
                affected_agents=sorted(agents),
                confidence=min(0.4 + len(agents) * 0.15, 0.85),
            )
            self._patterns[pid] = p
            patterns.append(p)

        return patterns

    def _detect_escalation(self, signals: list[Signal]) -> list[Pattern]:
        """Detect severity escalation over time."""
        patterns: list[Pattern] = []

        # Check per-agent severity trends
        for agent, agent_signals in self._by_agent.items():
            if len(agent_signals) < 3:
                continue

            recent = sorted(agent_signals, key=lambda s: s.timestamp)[-5:]
            severities = [_severity_rank(s.severity) for s in recent]

            # Check if trending up
            if len(severities) >= 3 and severities[-1] > severities[0]:
                trend_delta = severities[-1] - severities[0]
                if trend_delta >= 2:  # Jumped at least 2 levels
                    pid = f"escalation:{agent}"
                    if pid in self._patterns:
                        continue

                    p = Pattern(
                        id=pid,
                        title=f"Escalating issues in {agent}",
                        description=f"Severity trending up: {' → '.join(s.severity.value for s in recent)}",
                        signal_ids=[s.id for s in recent],
                        frequency=len(recent),
                        severity=Severity.CRITICAL,
                        affected_agents=[agent],
                        confidence=min(0.5 + trend_delta * 0.1, 0.9),
                        suggested_action=f"Investigate root cause in {agent} — issues getting worse",
                    )
                    self._patterns[pid] = p
                    patterns.append(p)

        return patterns

    @property
    def patterns(self) -> list[Pattern]:
        """All detected patterns."""
        return list(self._patterns.values())


def _severity_rank(s: Severity) -> int:
    """Numeric rank for severity comparison."""
    return {
        Severity.INFO: 0,
        Severity.LOW: 1,
        Severity.MEDIUM: 2,
        Severity.HIGH: 3,
        Severity.CRITICAL: 4,
    }.get(s, 2)
