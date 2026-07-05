"""Community responder — Eva as community support + feature request manager.

Uses Claude Code CLI (subscription) with full tool access.
Claude reads CLAUDE.md from the project directory for identity context.
"""

import asyncio
import os
import shutil
from pathlib import Path

DEFAULT_SESSION_MARKER = Path.home() / ".claude" / ".eva-session"

# Tools Eva can use via Claude Code CLI
ALLOWED_TOOLS = "Bash,Read,Glob,Grep,WebFetch"


class EvaResponder:
    """Eva's community brain — responds to messages with full tool access."""

    def __init__(
        self,
        session_marker: Path | None = None,
    ) -> None:
        self._claude_cli: str | None = shutil.which("claude")
        if not self._claude_cli:
            raise ValueError(
                "Claude CLI not found. "
                "Install Claude Code: npm install -g @anthropic-ai/claude-code"
            )
        self._session_marker = session_marker or DEFAULT_SESSION_MARKER

    async def respond(self, text: str, *, username: str = "") -> str:
        """Generate Eva's response to a community message."""
        prompt = f"[@{username}]: {text}" if username else text
        return await self._call_claude_cli(prompt, continue_session=True)

    async def _call_claude_cli(self, user: str, *, continue_session: bool = False) -> str:
        """Call Claude Code CLI with conversation memory and tool access.

        Claude reads CLAUDE.md from /app for identity context.
        No system prompt needed — project context provides everything.
        """
        cli = self._claude_cli or "claude"
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        has_session = continue_session and self._session_marker.exists()

        args = [cli, "-p", "--model", "sonnet", "--effort", "high", "--allowedTools", ALLOWED_TOOLS]
        if has_session:
            args.extend(["--continue", user])
        else:
            args.append(user)

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
                return await self._call_claude_cli(user, continue_session=continue_session)
            return ""

        # Mark session active for future --continue calls
        if continue_session and not has_session:
            self._session_marker.parent.mkdir(parents=True, exist_ok=True)
            self._session_marker.touch()

        return stdout.decode().strip()
