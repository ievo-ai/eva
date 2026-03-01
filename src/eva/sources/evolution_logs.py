"""Evolution logs source — reads EVO entries from marketplace agents."""

import re
from pathlib import Path

from eva.core.config import SourceConfig
from eva.core.models import Severity, Signal, SignalType
from eva.sources.base import BaseSource

# Regex for parsing EVO entries
_EVO_PATTERN = re.compile(
    r"## (EVO-\d+)\s*—\s*(.+?)\n"
    r".*?Type:\s*(.+?)\n"
    r".*?Trigger:\s*(.+?)\n"
    r".*?Root cause:\s*(.+?)\n"
    r".*?Mutation:\s*(.+?)\n"
    r".*?Confidence:\s*(\w+)",
    re.DOTALL,
)

_TYPE_SEVERITY = {
    "bug": Severity.HIGH,
    "misunderstanding": Severity.MEDIUM,
    "gap": Severity.MEDIUM,
    "drift": Severity.LOW,
    "regression": Severity.CRITICAL,
}


class EvolutionLogsSource(BaseSource):
    """Scans EVOLUTION_LOG.md files from marketplace agents."""

    name = "evolution_logs"

    def __init__(
        self,
        config: SourceConfig,
        marketplace_dir: Path | None = None,
    ) -> None:
        super().__init__(config)
        self._marketplace_dir = marketplace_dir
        self._seen_ids: set[str] = set()

    async def poll(self) -> list[Signal]:
        if not self._marketplace_dir or not self._marketplace_dir.exists():
            return []

        signals: list[Signal] = []
        agents_dir = self._marketplace_dir / "agents"
        if not agents_dir.exists():
            return []

        for agent_dir in agents_dir.iterdir():
            if not agent_dir.is_dir():
                continue

            evo_log = agent_dir / "EVOLUTION_LOG.md"
            if not evo_log.exists():
                continue

            content = evo_log.read_text()
            for match in _EVO_PATTERN.finditer(content):
                evo_id = match.group(1)
                full_id = f"{agent_dir.name}:{evo_id}"

                if full_id in self._seen_ids:
                    continue
                self._seen_ids.add(full_id)

                evo_type = match.group(3).strip().lower()
                severity = _TYPE_SEVERITY.get(evo_type, Severity.MEDIUM)

                signal = Signal(
                    id=full_id,
                    type=SignalType.EVOLUTION_LOG,
                    source=f"evo:{agent_dir.name}",
                    title=f"[{agent_dir.name}] {match.group(2).strip()}",
                    body=(
                        f"Type: {match.group(3).strip()}\n"
                        f"Trigger: {match.group(4).strip()}\n"
                        f"Root cause: {match.group(5).strip()}\n"
                        f"Mutation: {match.group(6).strip()}"
                    ),
                    severity=severity,
                    metadata={
                        "agent": agent_dir.name,
                        "evo_id": evo_id,
                        "evo_type": evo_type,
                        "confidence": match.group(7).strip(),
                    },
                    tags=[agent_dir.name, evo_type, "evo"],
                )
                signals.append(signal)

        return signals

    async def healthcheck(self) -> bool:
        return self._marketplace_dir is not None and self._marketplace_dir.exists()
