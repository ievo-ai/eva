"""GitHub Issues source."""

import os
from datetime import datetime

import httpx

from eva.core.config import SourceConfig
from eva.core.models import Severity, Signal, SignalType
from eva.sources.base import BaseSource

# Label-based severity mapping
_LABEL_SEVERITY = {
    "bug": Severity.HIGH,
    "critical": Severity.CRITICAL,
    "enhancement": Severity.LOW,
    "feature": Severity.LOW,
    "documentation": Severity.INFO,
    "help wanted": Severity.MEDIUM,
}


class GitHubIssuesSource(BaseSource):
    """Polls GitHub repos for open issues and bug reports."""

    name = "github_issues"

    def __init__(self, config: SourceConfig, repos: dict[str, str] | None = None) -> None:
        super().__init__(config)
        self._token = os.environ.get(config.token_env, "")
        self._repos = repos or {}
        self._since: str | None = None

    async def poll(self) -> list[Signal]:
        signals: list[Signal] = []
        headers = {}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        headers["Accept"] = "application/vnd.github.v3+json"

        async with httpx.AsyncClient() as client:
            for label, repo in self._repos.items():
                params: dict[str, str] = {
                    "state": "open",
                    "sort": "updated",
                    "direction": "desc",
                    "per_page": "20",
                }
                if self._since:
                    params["since"] = self._since

                url = f"https://api.github.com/repos/{repo}/issues"
                try:
                    resp = await client.get(url, headers=headers, params=params, timeout=30)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for issue in resp.json():
                    # Skip pull requests (GitHub returns them in issues endpoint)
                    if "pull_request" in issue:
                        continue

                    labels = [label["name"] for label in issue.get("labels", [])]
                    severity = _classify_severity(labels)

                    signal = Signal(
                        id=str(issue["number"]),
                        type=SignalType.GITHUB_ISSUE,
                        source=f"github:{repo}#{issue['number']}",
                        title=issue.get("title", ""),
                        body=issue.get("body", "") or "",
                        severity=severity,
                        timestamp=datetime.fromisoformat(
                            issue["updated_at"].replace("Z", "+00:00")
                        ),
                        metadata={
                            "repo": repo,
                            "repo_label": label,
                            "labels": labels,
                            "author": issue.get("user", {}).get("login", ""),
                            "comments": issue.get("comments", 0),
                            "url": issue.get("html_url", ""),
                        },
                        tags=labels + [label, "github"],
                    )
                    signals.append(signal)

        if signals:
            self._since = datetime.utcnow().isoformat() + "Z"

        return signals

    async def healthcheck(self) -> bool:
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    "https://api.github.com/rate_limit",
                    headers=headers,
                    timeout=10,
                )
                return resp.status_code == 200
            except httpx.HTTPError:
                return False


def _classify_severity(labels: list[str]) -> Severity:
    """Determine severity from issue labels."""
    for label in labels:
        lower = label.lower()
        for keyword, severity in _LABEL_SEVERITY.items():
            if keyword in lower:
                return severity
    return Severity.MEDIUM
