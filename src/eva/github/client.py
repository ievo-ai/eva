"""Low-level GitHub REST API client for Eva.

Handles: branch creation, file commits, and pull request management.
Uses httpx (async) — same as the rest of Eva's sources.
"""

import base64
from dataclasses import dataclass
from typing import Any

import httpx

API_BASE = "https://api.github.com"


@dataclass
class PRResult:
    """Result of creating a pull request."""

    pr_url: str
    pr_number: int
    branch: str
    repo: str


class GitHubClient:
    """Async GitHub REST API client.

    Supports both GitHub App tokens and PATs via Authorization header.
    """

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("GitHub token is required for live mode.")
        self._token = token
        self._headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    async def get_default_branch(self, repo: str) -> str:
        """Get the default branch name for a repo."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE}/repos/{repo}",
                headers=self._headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["default_branch"]

    async def get_ref_sha(self, repo: str, ref: str) -> str:
        """Get the SHA of a git ref (branch/tag)."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE}/repos/{repo}/git/ref/heads/{ref}",
                headers=self._headers,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["object"]["sha"]

    async def create_branch(self, repo: str, branch: str, from_sha: str) -> None:
        """Create a new branch from a SHA."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_BASE}/repos/{repo}/git/refs",
                headers=self._headers,
                json={"ref": f"refs/heads/{branch}", "sha": from_sha},
                timeout=30,
            )
            # 422 = branch already exists — that's okay, we'll update it
            if resp.status_code == 422:
                return
            resp.raise_for_status()

    async def get_file_content(self, repo: str, path: str, branch: str) -> dict[str, Any] | None:
        """Get file content + SHA (needed for updates). Returns None if file doesn't exist."""
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{API_BASE}/repos/{repo}/contents/{path}",
                headers=self._headers,
                params={"ref": branch},
                timeout=30,
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.json()

    async def create_or_update_file(
        self,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
    ) -> str:
        """Create or update a file on a branch. Returns the commit SHA."""
        encoded = base64.b64encode(content.encode()).decode()

        payload: dict[str, Any] = {
            "message": message,
            "content": encoded,
            "branch": branch,
        }

        # If file exists, we need the SHA for update
        existing = await self.get_file_content(repo, path, branch)
        if existing and "sha" in existing:
            payload["sha"] = existing["sha"]

        async with httpx.AsyncClient() as client:
            resp = await client.put(
                f"{API_BASE}/repos/{repo}/contents/{path}",
                headers=self._headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            return resp.json()["commit"]["sha"]

    async def create_pull_request(
        self,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str | None = None,
    ) -> PRResult:
        """Create a pull request. Returns PRResult with URL and number."""
        if base is None:
            base = await self.get_default_branch(repo)

        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_BASE}/repos/{repo}/pulls",
                headers=self._headers,
                json={
                    "title": title,
                    "body": body,
                    "head": head,
                    "base": base,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()

        return PRResult(
            pr_url=data["html_url"],
            pr_number=data["number"],
            branch=head,
            repo=repo,
        )

    async def add_labels(self, repo: str, issue_number: int, labels: list[str]) -> None:
        """Add labels to an issue/PR."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{API_BASE}/repos/{repo}/issues/{issue_number}/labels",
                headers=self._headers,
                json={"labels": labels},
                timeout=30,
            )
            # Ignore errors for labels — non-critical
            if resp.status_code >= 400:
                pass
