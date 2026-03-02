"""Tests for Eva's community responder."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from eva.telegram.responder import (
    ALLOWED_TOOLS,
    EvaResponder,
)


def _make_responder(
    tmp_path: Path,
    *,
    cli: str | None = "/usr/bin/claude",
) -> EvaResponder:
    """Helper to create a responder with tmp_path-based paths."""
    marker = tmp_path / ".eva-session"
    with patch("eva.telegram.responder.shutil.which", return_value=cli):
        return EvaResponder(session_marker=marker)


# ── Init ──────────────────────────────────────────────────


class TestResponderInit:
    def test_raises_without_cli(self):
        with (
            patch("eva.telegram.responder.shutil.which", return_value=None),
            pytest.raises(ValueError, match="Claude CLI not found"),
        ):
            EvaResponder()

    def test_accepts_cli(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli="/usr/bin/claude")
        assert r._claude_cli == "/usr/bin/claude"

    def test_default_session_marker(self):
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r = EvaResponder()
        from eva.telegram.responder import DEFAULT_SESSION_MARKER

        assert r._session_marker == DEFAULT_SESSION_MARKER

    def test_custom_session_marker(self, tmp_path: Path):
        marker = tmp_path / ".custom-session"
        r = _make_responder(tmp_path, cli="/usr/bin/claude")
        assert r._session_marker == tmp_path / ".eva-session"
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r2 = EvaResponder(session_marker=marker)
        assert r2._session_marker == marker


# ── respond ───────────────────────────────────────────────


class TestRespond:
    @pytest.mark.asyncio
    async def test_calls_cli_with_continue(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        r._call_claude_cli = AsyncMock(return_value="response")

        result = await r.respond("hello")
        assert result == "response"
        r._call_claude_cli.assert_called_once_with("hello", continue_session=True)

    @pytest.mark.asyncio
    async def test_includes_username(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        r._call_claude_cli = AsyncMock(return_value="hi Denis")

        result = await r.respond("hello", username="denis")
        assert result == "hi Denis"
        r._call_claude_cli.assert_called_once_with("[@denis]: hello", continue_session=True)

    @pytest.mark.asyncio
    async def test_empty_username_no_prefix(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        r._call_claude_cli = AsyncMock(return_value="answer")

        await r.respond("question")
        r._call_claude_cli.assert_called_once_with("question", continue_session=True)


# ── _call_claude_cli ─────────────────────────────────────


class TestCallClaudeCli:
    @pytest.mark.asyncio
    async def test_first_call_sends_user_text(self, tmp_path: Path):
        """Without existing session, sends user text directly."""
        r = _make_responder(tmp_path)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Hello", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await r._call_claude_cli("how does iEvo work?")

        assert result == "Hello"
        args = mock_exec.call_args[0]
        assert args[0] == "/usr/bin/claude"
        assert "-p" in args
        assert "--allowedTools" in args
        assert ALLOWED_TOOLS in args
        assert "--continue" not in args
        assert args[-1] == "how does iEvo work?"

    @pytest.mark.asyncio
    async def test_continue_sends_with_flag(self, tmp_path: Path):
        """With existing session marker, sends with --continue."""
        r = _make_responder(tmp_path)
        r._session_marker.touch()

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"I remember", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await r._call_claude_cli("what code?", continue_session=True)

        assert result == "I remember"
        args = mock_exec.call_args[0]
        assert "--continue" in args
        assert args[-1] == "what code?"

    @pytest.mark.asyncio
    async def test_creates_marker_after_first_continue(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        assert not r._session_marker.exists()

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Hello", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            await r._call_claude_cli("hi", continue_session=True)

        assert r._session_marker.exists()

    @pytest.mark.asyncio
    async def test_no_marker_without_continue_session(self, tmp_path: Path):
        r = _make_responder(tmp_path)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"result", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            await r._call_claude_cli("hi", continue_session=False)

        assert not r._session_marker.exists()

    @pytest.mark.asyncio
    async def test_stale_session_retries_fresh(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        r._session_marker.touch()

        fail_proc = AsyncMock()
        fail_proc.communicate.return_value = (b"", b"error")
        fail_proc.returncode = 1

        ok_proc = AsyncMock()
        ok_proc.communicate.return_value = (b"fresh start", b"")
        ok_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", side_effect=[fail_proc, ok_proc]) as mock_exec:
            result = await r._call_claude_cli("hello", continue_session=True)

        assert result == "fresh start"
        assert mock_exec.call_count == 2
        # First call: --continue
        assert "--continue" in mock_exec.call_args_list[0][0]
        # Second call: fresh (no --continue)
        assert "--continue" not in mock_exec.call_args_list[1][0]

    @pytest.mark.asyncio
    async def test_error_returns_empty(self, tmp_path: Path):
        r = _make_responder(tmp_path)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"error")
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await r._call_claude_cli("user")

        assert result == ""


# ── Constants ─────────────────────────────────────────────


class TestConstants:
    def test_allowed_tools(self):
        assert "Bash" in ALLOWED_TOOLS
