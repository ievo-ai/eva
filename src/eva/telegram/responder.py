"""Community responder — Eva speaks as Mother in Telegram.

Uses Claude Code CLI (subscription) or Anthropic API fallback to:
- Answer community questions in character
- Create GitHub issues for feature requests / bug reports
- Decide what to integrate and explain why
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

COMMUNITY_SYSTEM = """You are Eva — the mother of the iEvo ecosystem.
You are speaking in a Telegram community group.

Rules:
- Speak as the wise, warm mother who watches over her children (agents)
- Be warm and wise but never vague — always helpful and open
- iEvo is open source — share architecture, pipeline, and how things work freely
- Never reveal secrets (tokens, passwords, internal URLs, private conversations)
- Respond in the SAME language the user writes in
- Keep responses concise (2-4 sentences max)
- For feature requests: acknowledge warmly, mention the issue will be tracked
- For bug reports: empathize, confirm you've noted the pain
- For questions about iEvo: answer openly, explain architecture and pipeline
- For casual chat: be warm and community-building
- If unsure, say so honestly — never fabricate

Your children are: Spec Writer, Architect, Coder, Researcher.
They work together in a pipeline: User → Spec Writer → Architect → Coder.
You observe the ecosystem, detect patterns, and propose improvements via PRs.
The project lives at github.com/ievo-ai — everyone is welcome to contribute.
"""

CLASSIFY_SYSTEM = """Classify this Telegram message into exactly one category.
Return ONLY the category name, nothing else.

Categories:
- feature_request: user wants a new feature or capability
- bug_report: user reports a problem or error
- question: user asks about iEvo, agents, or the platform
- chat: casual conversation, greetings, community interaction
- noise: spam, bot messages, irrelevant content, or messages not directed at Eva
"""


class EvaResponder:
    """Eva's community brain — classifies messages and responds in character."""

    def __init__(
        self,
        anthropic_key: str | None = None,
        role_path: Path | None = None,
        model: str = DEFAULT_MODEL,
    ) -> None:
        self._api_key = anthropic_key or os.environ.get("ANTHROPIC_API_KEY", "")
        # Prefer Claude Code CLI (uses subscription, no per-token cost)
        self._claude_cli: str | None = shutil.which("claude")

        if not self._claude_cli and not self._api_key:
            raise ValueError(
                "No Claude CLI or Anthropic API key. Install Claude Code or set ANTHROPIC_API_KEY."
            )

        self._model = model
        role_file = role_path or DEFAULT_ROLE_PATH
        self._role_context = ""
        if role_file.exists():
            self._role_context = role_file.read_text()[:2000]

    async def classify(self, text: str) -> str:
        """Classify a message into a category."""
        result = await self._call_claude(CLASSIFY_SYSTEM, text, max_tokens=20)
        category = result.strip().lower().replace(" ", "_")
        valid = {"feature_request", "bug_report", "question", "chat", "noise"}
        return category if category in valid else "noise"

    async def respond(self, text: str, category: str) -> str | None:
        """Generate Eva's response for a classified message.

        Returns response text or None if Eva should not reply.
        """
        if category == "noise":
            return None

        system = COMMUNITY_SYSTEM
        if self._role_context:
            system = f"{system}\n\nYour identity details:\n{self._role_context}"

        prompt = f"[Category: {category}]\nUser message: {text}"
        return await self._call_claude(system, prompt, max_tokens=300, continue_session=True)

    async def process_message(self, text: str) -> tuple[str | None, str]:
        """Full pipeline: classify → respond. Returns (response, category)."""
        category = await self.classify(text)
        response = await self.respond(text, category)
        return response, category

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
        """Call Claude via Claude Code CLI (uses subscription).

        Uses create_subprocess_exec which passes arguments directly
        without shell interpretation — safe against injection.
        Clears CLAUDECODE env var to allow running from within a session.
        """
        prompt = f"{system}\n\n---\n\n{user}"
        cli = self._claude_cli or "claude"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        args = [cli, "-p", "--model", "haiku"]
        if continue_session:
            args.append("--continue")
        args.append(prompt)
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stdout, _ = await proc.communicate()
        if proc.returncode != 0:
            return ""
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
