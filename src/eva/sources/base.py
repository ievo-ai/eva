"""Base class for all signal sources."""

from abc import ABC, abstractmethod

from eva.core.config import SourceConfig
from eva.core.models import Signal


class BaseSource(ABC):
    """Abstract base for signal sources.

    Each source connects to an external system, polls for new data,
    and converts it into normalized Signal objects.
    """

    name: str = "base"

    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    @abstractmethod
    async def poll(self) -> list[Signal]:
        """Fetch new signals from the source.

        Returns:
            List of new Signal objects since last poll.
        """
        ...

    @abstractmethod
    async def healthcheck(self) -> bool:
        """Check if the source is reachable.

        Returns:
            True if the source is available.
        """
        ...

    def is_enabled(self) -> bool:
        return self.config.enabled
