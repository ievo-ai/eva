"""Telegram community source — polls group messages as signals."""

import os
from datetime import UTC, datetime

import httpx

from eva.core.config import SourceConfig
from eva.core.models import Severity, Signal, SignalType
from eva.sources.base import BaseSource

# Keyword-based severity mapping for community messages
_KEYWORD_SEVERITY = {
    "bug": Severity.HIGH,
    "error": Severity.HIGH,
    "crash": Severity.CRITICAL,
    "broken": Severity.HIGH,
    "feature": Severity.LOW,
    "request": Severity.LOW,
    "help": Severity.MEDIUM,
    "question": Severity.MEDIUM,
}

API_BASE = "https://api.telegram.org"


class TelegramSource(BaseSource):
    """Polls Telegram community group for messages as signals."""

    name = "telegram"

    def __init__(self, config: SourceConfig) -> None:
        super().__init__(config)
        self._token = os.environ.get(config.token_env, "")
        self._chat_id = os.environ.get("TELEGRAM_COMMUNITY_CHAT", "")
        self._offset: int = config.extra.get("offset", 0)
        self._seen: set[int] = set()

    async def poll(self) -> list[Signal]:
        """Fetch new messages from Telegram group and convert to signals."""
        if not self._token:
            return []

        base = f"{API_BASE}/bot{self._token}"
        params: dict[str, int] = {"limit": 100, "timeout": 5}
        if self._offset:
            params["offset"] = self._offset

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{base}/getUpdates",
                    params=params,
                    timeout=30,
                )
                data = resp.json()
            except httpx.HTTPError:
                return []

        if not data.get("ok"):
            return []

        signals: list[Signal] = []
        for update in data.get("result", []):
            update_id = update.get("update_id", 0)

            # Track offset for next poll
            self._offset = max(self._offset, update_id + 1)

            msg = update.get("message", {})
            text = msg.get("text", "")
            if not text:
                continue

            # Filter: only messages from the community chat
            chat = msg.get("chat", {})
            chat_id = str(chat.get("id", ""))
            if self._chat_id and chat_id != self._chat_id:
                continue

            # Deduplicate
            msg_id = msg.get("message_id", 0)
            if msg_id in self._seen:
                continue
            self._seen.add(msg_id)

            severity = _classify_severity(text)
            user = msg.get("from", {})
            username = user.get("username", user.get("first_name", "anonymous"))

            signal = Signal(
                id=str(msg_id),
                type=SignalType.TELEGRAM_MESSAGE,
                source=f"telegram:{chat_id}#{msg_id}",
                title=text[:100],
                body=text,
                severity=severity,
                timestamp=datetime.fromtimestamp(msg.get("date", 0), tz=UTC),
                metadata={
                    "chat_id": chat_id,
                    "message_id": msg_id,
                    "username": username,
                    "update_id": update_id,
                },
                tags=["telegram", "community"],
            )
            signals.append(signal)

        # Store offset for persistence
        self.config.extra["offset"] = self._offset

        return signals

    async def healthcheck(self) -> bool:
        """Check if the Telegram bot is reachable."""
        if not self._token:
            return False

        base = f"{API_BASE}/bot{self._token}"
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(f"{base}/getMe", timeout=10)
                data = resp.json()
                return bool(data.get("ok"))
            except httpx.HTTPError:
                return False


def _classify_severity(text: str) -> Severity:
    """Classify message severity from keywords."""
    lower = text.lower()
    for keyword, severity in _KEYWORD_SEVERITY.items():
        if keyword in lower:
            return severity
    return Severity.LOW
