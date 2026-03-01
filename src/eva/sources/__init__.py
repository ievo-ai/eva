"""Signal sources — connectors that feed Eva with observations."""

from eva.sources.base import BaseSource
from eva.sources.evolution_logs import EvolutionLogsSource
from eva.sources.github_issues import GitHubIssuesSource
from eva.sources.reviews import ReviewsSource
from eva.sources.sentry import SentrySource

__all__ = [
    "BaseSource",
    "GitHubIssuesSource",
    "SentrySource",
    "EvolutionLogsSource",
    "ReviewsSource",
]
