"""User reviews and PR comment source."""

import os
from datetime import datetime

import httpx

from eva.core.config import SourceConfig
from eva.core.models import Severity, Signal, SignalType
from eva.sources.base import BaseSource


class ReviewsSource(BaseSource):
    """Polls GitHub discussions and PR review comments for feedback."""

    name = "reviews"

    def __init__(self, config: SourceConfig, repos: dict[str, str] | None = None) -> None:
        super().__init__(config)
        self._token = os.environ.get(config.token_env, "")
        self._repos = repos or {}
        self._seen_ids: set[str] = set()

    async def poll(self) -> list[Signal]:
        signals: list[Signal] = []
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"

        async with httpx.AsyncClient() as client:
            for label, repo in self._repos.items():
                # Fetch recent PR comments
                url = f"https://api.github.com/repos/{repo}/pulls/comments"
                params = {"sort": "updated", "direction": "desc", "per_page": "20"}

                try:
                    resp = await client.get(url, headers=headers, params=params, timeout=30)
                    resp.raise_for_status()
                except httpx.HTTPError:
                    continue

                for comment in resp.json():
                    cid = f"pr-comment:{repo}:{comment['id']}"
                    if cid in self._seen_ids:
                        continue
                    self._seen_ids.add(cid)

                    body = comment.get("body", "") or ""
                    severity = _classify_comment(body)

                    signal = Signal(
                        id=str(comment["id"]),
                        type=SignalType.PR_COMMENT,
                        source=f"github:{repo}:pr-comment",
                        title=f"PR comment on {repo}",
                        body=body,
                        severity=severity,
                        timestamp=datetime.fromisoformat(
                            comment["updated_at"].replace("Z", "+00:00")
                        ),
                        metadata={
                            "repo": repo,
                            "author": comment.get("user", {}).get("login", ""),
                            "url": comment.get("html_url", ""),
                            "pr_url": comment.get("pull_request_url", ""),
                        },
                        tags=[label, "review", "github"],
                    )
                    signals.append(signal)

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


def _classify_comment(body: str) -> Severity:
    """Heuristic severity from comment content."""
    lower = body.lower()
    if any(w in lower for w in ("broken", "crash", "fatal", "critical", "blocker")):
        return Severity.CRITICAL
    if any(w in lower for w in ("bug", "error", "wrong", "incorrect", "fail")):
        return Severity.HIGH
    if any(w in lower for w in ("should", "could", "improve", "suggest", "nitpick")):
        return Severity.LOW
    return Severity.MEDIUM
