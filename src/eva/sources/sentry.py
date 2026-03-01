"""Sentry error tracking source.

Polls Sentry.io (or self-hosted) for unresolved issues across multiple projects.
Maps Sentry severity levels to Eva's severity model.

Config in eva.yaml:
    sources:
      sentry:
        enabled: true
        token_env: EVA_SENTRY_TOKEN
        extra:
          org: ievo
          projects:
            cli: ievo-cli
            marketplace: ievo-marketplace
            sdk: ievo-sdk
"""

import os
from datetime import UTC, datetime

import httpx

from eva.core.config import SourceConfig
from eva.core.models import Severity, Signal, SignalType
from eva.sources.base import BaseSource

# Sentry level → Eva severity
_SEVERITY_MAP = {
    "fatal": Severity.CRITICAL,
    "error": Severity.HIGH,
    "warning": Severity.MEDIUM,
    "info": Severity.LOW,
    "debug": Severity.INFO,
}


class SentrySource(BaseSource):
    """Polls Sentry for unresolved issues across multiple projects.

    Supports both sentry.io and self-hosted instances.
    """

    name = "sentry"

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)
        self._token = os.environ.get(config.token_env, "")
        self._base_url = (config.endpoint or "https://sentry.io/api/0").rstrip("/")
        self._org = config.extra.get("org", "")
        # Multi-project: {"label": "sentry-project-slug"}
        self._projects: dict[str, str] = config.extra.get("projects", {})
        # Legacy: single project via "project" key
        if not self._projects and "project" in config.extra:
            self._projects = {"default": config.extra["project"]}
        self._last_seen: str | None = None

    async def poll(self) -> list[Signal]:
        if not self._token or not self._org:
            return []

        signals: list[Signal] = []
        headers = {"Authorization": f"Bearer {self._token}"}

        async with httpx.AsyncClient() as client:
            for label, project_slug in self._projects.items():
                params: dict[str, str] = {
                    "query": "is:unresolved",
                    "sort": "date",
                    "limit": "25",
                }
                if self._last_seen:
                    params["start"] = self._last_seen

                url = f"{self._base_url}/projects/{self._org}/{project_slug}/issues/"
                try:
                    resp = await client.get(
                        url,
                        headers=headers,
                        params=params,
                        timeout=30,
                    )
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for issue in resp.json():
                    severity = _SEVERITY_MAP.get(
                        issue.get("level", "error"),
                        Severity.MEDIUM,
                    )

                    # Build readable body from Sentry metadata
                    culprit = issue.get("culprit", "")
                    metadata_value = issue.get("metadata", {}).get("value", "")
                    count = issue.get("count", 0)
                    body_parts = []
                    if culprit:
                        body_parts.append(f"Culprit: {culprit}")
                    if metadata_value:
                        body_parts.append(metadata_value)
                    if count > 1:
                        body_parts.append(f"Seen {count} times")

                    platform = issue.get("platform", "")
                    tags = [label, "sentry"]
                    if platform:
                        tags.insert(0, platform)

                    signal = Signal(
                        id=str(issue["id"]),
                        type=SignalType.SENTRY_ERROR,
                        source=f"sentry:{self._org}/{project_slug}#{issue['id']}",
                        title=issue.get("title", "Unknown error"),
                        body="\n".join(body_parts),
                        severity=severity,
                        timestamp=_parse_timestamp(issue.get("lastSeen", "")),
                        metadata={
                            "org": self._org,
                            "project": project_slug,
                            "project_label": label,
                            "count": count,
                            "culprit": culprit,
                            "platform": platform,
                            "first_seen": issue.get("firstSeen", ""),
                            "permalink": issue.get("permalink", ""),
                        },
                        tags=tags,
                    )
                    signals.append(signal)

        if signals:
            self._last_seen = datetime.now(UTC).isoformat()

        return signals

    async def healthcheck(self) -> bool:
        if not self._token:
            return False
        headers = {"Authorization": f"Bearer {self._token}"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self._base_url}/",
                    headers=headers,
                    timeout=10,
                )
                return resp.status_code == 200
            except httpx.HTTPError:
                return False


def _parse_timestamp(value: str) -> datetime:
    """Parse Sentry ISO 8601 timestamp."""
    if not value:
        return datetime.now(UTC)
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return datetime.now(UTC)
