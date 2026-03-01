"""Publish evolution entries to ievo.ai evolutions.json via GitHub API.

After Eva creates PRs, it records each successful mutation as an evolution
entry on the ievo.ai site so the public can see the platform evolving.
"""

import base64
import json
import os
from datetime import UTC, datetime

from rich.console import Console

from eva.core.models import Mutation
from eva.github.client import GitHubClient

console = Console()

# Target: ievo-ai/ievo.ai repo, docs/evolutions.json
SITE_REPO = "ievo-ai/ievo.ai"
EVOLUTIONS_PATH = "docs/evolutions.json"


class EvolutionPublisher:
    """Publishes evolution entries to ievo.ai."""

    def __init__(self, token: str | None = None) -> None:
        self._token = token or os.environ.get("EVA_GITHUB_TOKEN", "")
        if not self._token:
            raise ValueError("No token for evolution publishing. Set EVA_GITHUB_TOKEN.")
        self._client = GitHubClient(self._token)

    async def publish(self, mutations: list[Mutation]) -> int:
        """Publish successful mutations as evolution entries.

        Only publishes mutations that have a pr_url (= successfully created PR).
        Returns number of entries published.
        """
        successful = [m for m in mutations if m.pr_url]
        if not successful:
            return 0

        try:
            # Read current evolutions.json
            existing = await self._client.get_file_content(SITE_REPO, EVOLUTIONS_PATH, "main")

            if existing and "content" in existing:
                raw = base64.b64decode(existing["content"]).decode()
                evolutions = json.loads(raw)
            else:
                evolutions = []

            # Find next ID
            max_id = 0
            for e in evolutions:
                eid = e.get("id", "")
                if eid.startswith("EVO-"):
                    try:
                        num = int(eid.split("-")[1])
                        max_id = max(max_id, num)
                    except (IndexError, ValueError):
                        pass

            # Add new entries
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            for mutation in successful:
                max_id += 1
                entry = {
                    "id": f"EVO-{max_id:03d}",
                    "date": today,
                    "title": mutation.title,
                    "agent": "eva",
                    "type": mutation.type.value,
                    "target": mutation.target_path,
                    "description": mutation.description[:200],
                    "confidence": round(mutation.confidence, 2),
                    "pr": mutation.pr_url,
                }
                evolutions.append(entry)

            # Write back
            new_content = json.dumps(evolutions, indent=2, ensure_ascii=False) + "\n"
            await self._client.create_or_update_file(
                repo=SITE_REPO,
                path=EVOLUTIONS_PATH,
                content=new_content,
                message=f"eva: publish {len(successful)} evolution(s)",
                branch="main",
            )

            console.print(f"  [green]✓[/green] Published {len(successful)} evolution(s) to ievo.ai")
            return len(successful)

        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Evolution publish failed: {e}")
            return 0
