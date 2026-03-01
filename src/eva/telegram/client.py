"""Telegram Bot API client for Eva notifications and community interaction."""

import os
from dataclasses import dataclass
from typing import Any

import httpx

API_BASE = "https://api.telegram.org"


@dataclass
class TelegramResult:
    """Result of a Telegram API call."""

    success: bool
    message_id: int = 0
    error: str = ""


class TelegramClient:
    """Async Telegram Bot API client.

    Uses the same async httpx pattern as GitHubClient.
    """

    def __init__(self, token: str | None = None, chat_id: str | None = None) -> None:
        self._token = token or os.environ.get("TELEGRAM_BOT_TOKEN", "")
        if not self._token:
            raise ValueError("No Telegram token. Set TELEGRAM_BOT_TOKEN.")
        self._chat_id = chat_id or os.environ.get("TELEGRAM_COMMUNITY_CHAT", "")
        if not self._chat_id:
            raise ValueError("No Telegram chat ID. Set TELEGRAM_COMMUNITY_CHAT.")
        self._base = f"{API_BASE}/bot{self._token}"

    async def send_message(
        self,
        text: str,
        parse_mode: str = "HTML",
        message_thread_id: int | None = None,
        reply_to_message_id: int | None = None,
    ) -> TelegramResult:
        """Send a message to the configured chat.

        For forum groups (Threaded Mode), automatically retries with
        message_thread_id=0 (General topic) if the first attempt fails.
        """
        payload: dict[str, Any] = {
            "chat_id": self._chat_id,
            "text": text,
            "parse_mode": parse_mode,
        }
        if message_thread_id is not None:
            payload["message_thread_id"] = message_thread_id
        if reply_to_message_id is not None:
            payload["reply_to_message_id"] = reply_to_message_id

        data = await self._post("sendMessage", payload)

        # Forum groups require message_thread_id — retry with General topic
        if not data.get("ok") and message_thread_id is None:
            payload["message_thread_id"] = 0
            data = await self._post("sendMessage", payload)

        if not data.get("ok"):
            return TelegramResult(
                success=False,
                error=data.get("description", "Unknown Telegram error"),
            )
        return TelegramResult(
            success=True,
            message_id=data["result"]["message_id"],
        )

    async def _post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        """Send a POST request to the Telegram API."""
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self._base}/{method}",
                json=payload,
                timeout=30,
            )
            result: dict[str, Any] = resp.json()
        return result

    async def create_forum_topic(self, name: str) -> int | None:
        """Create a forum topic in the group. Returns topic ID or None on failure."""
        data = await self._post(
            "createForumTopic",
            {"chat_id": self._chat_id, "name": name},
        )
        if data.get("ok"):
            result: dict[str, Any] = data["result"]
            return int(result["message_thread_id"])
        return None

    async def get_updates(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Get new messages via long polling. Returns list of Update dicts."""
        params: dict[str, Any] = {"limit": limit, "timeout": 5}
        if offset:
            params["offset"] = offset

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self._base}/getUpdates",
                    params=params,
                    timeout=30,
                )
                data: dict[str, Any] = resp.json()
            except httpx.HTTPError:
                return []

        if not data.get("ok"):
            return []
        result: list[dict[str, Any]] = data.get("result", [])
        return result
