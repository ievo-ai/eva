"""Publish evolution entries to ievo.ai evolutions.json via GitHub API.

After Eva creates PRs, it records each successful mutation as an evolution
entry on the ievo.ai site so the public can see the platform evolving.
Optionally also sends formatted messages to Telegram.
"""

import base64
import json
import os
from datetime import UTC, datetime
from typing import Any

from rich.console import Console

from eva.core.models import EvolutionEntry, Mutation
from eva.github.client import GitHubClient
from eva.telegram.client import TelegramClient
from eva.telegram.formatter import format_telegram_message

console = Console()

# Target: ievo-ai/ievo.ai repo, docs/evolutions.json
SITE_REPO = "ievo-ai/ievo.ai"
EVOLUTIONS_PATH = "docs/evolutions.json"


class EvolutionPublishError(Exception):
    """At least one publish channel (GitHub feed, Telegram) failed.

    Both channels are always attempted before this is raised; the message
    aggregates every failure so callers can fail loudly (eva#160 — a swallowed
    409 hid a production outage for 8+ hours).
    """


class EvolutionPublisher:
    """Publishes evolution entries to ievo.ai and optionally Telegram."""

    def __init__(
        self,
        token: str | None = None,
        telegram: TelegramClient | None = None,
    ) -> None:
        self._token = token or os.environ.get("EVA_GITHUB_TOKEN", "")
        if not self._token:
            raise ValueError("No token for evolution publishing. Set EVA_GITHUB_TOKEN.")
        self._client = GitHubClient(self._token)
        self._telegram = telegram
        topic_env = os.environ.get("TELEGRAM_EVOLUTIONS_TOPIC", "")
        self._evolutions_topic: int | None = int(topic_env) if topic_env else None

    async def publish(self, mutations: list[Mutation]) -> int:
        """Publish successful mutations as evolution entries.

        Only publishes mutations that have a pr_url (= successfully created PR).
        Converts Mutations to EvolutionEntry objects and delegates to publish_entries,
        so it raises EvolutionPublishError if either channel failed.
        Returns number of entries published.
        """
        successful = [m for m in mutations if m.pr_url]
        if not successful:
            return 0

        entries = [EvolutionEntry.from_mutation(m) for m in successful]
        return await self.publish_entries(entries)

    async def publish_entries(self, entries: list[EvolutionEntry]) -> int:
        """Publish EvolutionEntry objects to GitHub and optionally Telegram.

        Auto-assigns id and date to entries that don't have them.
        Both channels are attempted independently: a feed failure does not
        silence Telegram (nor vice versa). Raises EvolutionPublishError if
        either channel failed. Returns number of entries published.
        """
        if not entries:
            return 0

        feed_error: str | None = None
        try:
            # Read current evolutions.json
            existing = await self._client.get_file_content(SITE_REPO, EVOLUTIONS_PATH, "main")

            if existing and "content" in existing:
                raw = base64.b64decode(existing["content"]).decode()
                evolutions: list[dict[str, Any]] = json.loads(raw)
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

            # Assign IDs and dates, then append
            today = datetime.now(UTC).strftime("%Y-%m-%d")
            for entry in entries:
                if not entry.id:
                    max_id += 1
                    entry.id = f"EVO-{max_id:03d}"
                if not entry.date:
                    entry.date = today
                evolutions.append(entry.to_dict())

            # Write back
            new_content = json.dumps(evolutions, indent=2, ensure_ascii=False) + "\n"
            await self._client.create_or_update_file(
                repo=SITE_REPO,
                path=EVOLUTIONS_PATH,
                content=new_content,
                message=f"eva: publish {len(entries)} evolution(s)",
                branch="main",
            )

            console.print(
                f"  [green]\u2713[/green] Published {len(entries)} evolution(s) to ievo.ai"
            )

        except Exception as e:
            feed_error = str(e)
            console.print(f"  [yellow]\u26a0[/yellow] Evolution publish failed: {e}")

        # Notify Telegram \u2014 always attempted, even when the feed write failed
        # (entries keep their default id/date if the feed read never ran).
        telegram_errors = await self._notify_telegram(entries)

        if feed_error or telegram_errors:
            failures = []
            if feed_error:
                failures.append(f"feed: {feed_error}")
            failures.extend(f"telegram: {err}" for err in telegram_errors)
            raise EvolutionPublishError("; ".join(failures))

        return len(entries)

    async def _notify_telegram(self, entries: list[EvolutionEntry]) -> list[str]:
        """Send evolution notifications to Telegram community chat.

        Returns error descriptions for failed sends (empty list when all
        sends succeeded or no Telegram client is configured).
        """
        if not self._telegram:
            return []

        topic_id = self._evolutions_topic
        errors: list[str] = []

        for entry in entries:
            # id is blank when the feed read failed before assignment \u2014 fall
            # back to the title so failure messages still identify the entry.
            label = entry.id or entry.title
            msg = format_telegram_message(entry)
            try:
                result = await self._telegram.send_message(msg, message_thread_id=topic_id)
            except Exception as e:
                console.print(f"  [yellow]\u26a0[/yellow] Telegram {label}: {e}")
                errors.append(f"{label}: {e}")
                continue
            if result.success:
                console.print(f"  [green]\u2713[/green] Telegram: {label}")
            else:
                console.print(f"  [yellow]\u26a0[/yellow] Telegram {label}: {result.error}")
                errors.append(f"{label}: {result.error}")

        return errors
