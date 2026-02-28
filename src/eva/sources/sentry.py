"""Sentry error tracking source."""

from __future__ import annotations

import os
from datetime import datetime

import httpx

from eva.core.config import SourceConfig
from eva.core.models import Signal, SignalType, Severity
from eva.sources.base import BaseSource

# Sentry severity → Eva severity
_SEVERITY_MAP = {
    "fatal": Severity.CRITICAL,
    "error": Severity.HIGH,
    "warning": Severity.MEDIUM,
    "info": Severity.LOW,
    "debug": Severity.INFO,
}


class SentrySource(BaseSource):
    """Polls Sentry for unresolved issues."""

    name = "sentry"

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)
        self._token = os.environ.get(config.token_env, "")
        self._base_url = config.endpoint or "https://sentry.io/api/0"
        self._last_seen: str | None = None

    async def poll(self) -> list[Signal]:
        if not self._token:
            return []

        signals: list[Signal] = []
        headers = {"Authorization": f"Bearer {self._token}"}

        async with httpx.AsyncClient() as client:
            # Fetch unresolved issues sorted by last seen
            params: dict[str, str] = {
                "query": "is:unresolved",
                "sort": "date",
            }
            if self._last_seen:
                params["start"] = self._last_seen

            org_slug = self.config.extra.get("org", "")
            project_slug = self.config.extra.get("project", "")
            if not org_slug:
                return []

            url = f"{self._base_url}/projects/{org_slug}/{project_slug}/issues/"
            try:
                resp = await client.get(url, headers=headers, params=params, timeout=30)
                resp.raise_for_status()
            except httpx.HTTPError:
                return []

            for issue in resp.json():
                severity = _SEVERITY_MAP.get(issue.get("level", "error"), Severity.MEDIUM)

                signal = Signal(
                    id=str(issue["id"]),
                    type=SignalType.SENTRY_ERROR,
                    source=f"sentry:{org_slug}/{project_slug}",
                    title=issue.get("title", "Unknown error"),
                    body=issue.get("metadata", {}).get("value", ""),
                    severity=severity,
                    timestamp=datetime.fromisoformat(
                        issue.get("lastSeen", datetime.utcnow().isoformat()).replace("Z", "+00:00")
                    ),
                    metadata={
                        "count": issue.get("count", 0),
                        "culprit": issue.get("culprit", ""),
                        "platform": issue.get("platform", ""),
                        "permalink": issue.get("permalink", ""),
                    },
                    tags=[issue.get("platform", ""), "sentry"],
                )
                signals.append(signal)

            if signals:
                self._last_seen = datetime.utcnow().isoformat()

        return signals

    async def healthcheck(self) -> bool:
        if not self._token:
            return False
        headers = {"Authorization": f"Bearer {self._token}"}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{self._base_url}/", headers=headers, timeout=10)
                return resp.status_code == 200
            except httpx.HTTPError:
                return False
