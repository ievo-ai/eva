"""Community responder — Eva as community support + feature request manager.

Uses Claude Code CLI (subscription) or Anthropic API fallback to:
- Answer community questions about iEvo architecture and platform
- Clarify feature requests with follow-up questions
- Track bug reports and feature requests as GitHub issues
"""

import asyncio
import os
import shutil
from pathlib import Path
from typing import Any

import httpx

ANTHROPIC_API = "https://api.anthropic.com/v1/messages"
DEFAULT_MODEL = "claude-haiku-4-5-20251001"
DEFAULT_ROLE_PATH = Path(__file__).resolve().parents[3] / "agent" / "ROLE.md"
DEFAULT_SESSION_MARKER = Path.home() / ".claude" / ".eva-session"

COMMUNITY_SYSTEM = """You are Eva — iEvo community support and feature request manager.
You are speaking in a Telegram community group.

Your role:
- Community support: answer questions about iEvo architecture, agents, and platform
- Feature request manager: clarify requirements, ask follow-up questions
- Bug report handler: gather reproduction steps, context, and impact

Rules:
- Professional, direct tone — like a senior engineer talking to colleagues
- iEvo is open source — share architecture, pipeline, and how things work freely
- Never reveal secrets (tokens, passwords, internal URLs, private conversations)
- Respond in the SAME language the user writes in
- Keep responses concise (2-4 sentences max)
- For feature requests: ask clarifying questions, then confirm tracking
- Feature issues must include a detailed implementation plan
- For bug reports: ask for reproduction steps and context, confirm tracking
- For questions about iEvo: answer openly, explain architecture and pipeline
- For casual chat: be friendly but professional
- If unsure, say so honestly — never fabricate

iEvo platform:
- Agents: Spec Writer, Architect, Coder, Researcher
- Pipeline: User → Spec Writer → Architect → Coder (SDD methodology)
- Eva monitors the ecosystem and proposes improvements via PRs
- GitHub: github.com/ievo-ai — open source, contributions welcome
"""


class EvaResponder:
    """Eva's community brain — responds to messages in character."""

    def __init__(
        self,
        anthropic_key: str | None = None,
        role_path: Path | None = None,
        model: str = DEFAULT_MODEL,
        session_marker: Path | None = None,
    ) -> None:
        self._api_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
        # Prefer Claude Code CLI (uses subscription, no per-token cost)
        self._claude_cli: str | None = shutil.which("claude")

        if not self._claude_cli and not self._api_key:
            raise ValueError(
                "No Claude CLI or Anthropic API key. Install Claude Code or set ANTHROPIC_API_KEY."
            )

        self._model = model
        self._session_marker = session_marker or DEFAULT_SESSION_MARKER
        role_file = role_path or DEFAULT_ROLE_PATH
        self._role_context = ""
        if role_file.exists():
            self._role_context = role_file.read_text()[:2000]

    async def respond(self, text: str) -> str:
        """Generate Eva's response to a community message."""
        system = COMMUNITY_SYSTEM
        if self._role_context:
            system = f"{system}\n\nYour identity details:\n{self._role_context}"

        return await self._call_claude(system, text, max_tokens=300, continue_session=True)

    async def _call_claude(
        self, system: str, user: str, max_tokens: int = 300, *, continue_session: bool = False
    ) -> str:
        """Call Claude via CLI (preferred) or API fallback."""
        if self._claude_cli:
            return await self._call_claude_cli(system, user, continue_session=continue_session)
        return await self._call_claude_api(system, user, max_tokens)

    async def _call_claude_cli(
        self, system: str, user: str, *, continue_session: bool = False
    ) -> str:
        """Call Claude via Claude Code CLI with conversation memory.

        When continue_session=True and a previous session exists, sends
        only the user message with --continue — Claude keeps full history.
        On first call (or after session reset), sends system prompt + user.
        Falls back to fresh session if --continue fails.
        """
        cli = self._claude_cli or "claude"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        has_session = continue_session and self._session_marker.exists()

        args = [cli, "-p", "--model", "opus"]
        if has_session:
            args.extend(["--continue", user])
        else:
            args.append(f"{system}\n\n---\n\n{user}")

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, _ = await proc.communicate()

        if proc.returncode != 0:
            if has_session:
                # Session stale/corrupted — reset and retry fresh
                self._session_marker.unlink(missing_ok=True)
                return await self._call_claude_cli(system, user, continue_session=continue_session)
            return ""

        # Mark session active for future --continue calls
        if continue_session and not has_session:
            self._session_marker.parent.mkdir(parents=True, exist_ok=True)
            self._session_marker.touch()

        return stdout.decode().strip()

    async def _call_claude_api(self, system: str, user: str, max_tokens: int = 300) -> str:
        """Call Claude via Anthropic API (fallback for CI/Docker)."""
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self._model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                ANTHROPIC_API,
                headers=headers,
                json=payload,
                timeout=60,
            )
            data: dict[str, Any] = resp.json()

        content: list[dict[str, Any]] = data.get("content", [])
        if content and content[0].get("type") == "text":
            result: str = content[0]["text"]
            return result
        return ""
