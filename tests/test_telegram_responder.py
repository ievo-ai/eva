"""Tests for Eva's community responder."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.telegram.responder import (
    COMMUNITY_SYSTEM,
    EvaResponder,
)


def _make_responder(
    tmp_path: Path,
    *,
    cli: str | None = None,
    api_key: str | None = "sk-test",
    role_text: str = "",
) -> EvaResponder:
    """Helper to create a responder with tmp_path-based paths."""
    role = tmp_path / "ROLE.md"
    role.write_text(role_text)
    marker = tmp_path / ".eva-session"
    with patch("eva.telegram.responder.shutil.which", return_value=cli):
        return EvaResponder(
            anthropic_key=api_key,
            role_path=role,
            session_marker=marker,
        )


# ── Init ──────────────────────────────────────────────────


class TestResponderInit:
    def test_raises_without_cli_or_api_key(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("eva.telegram.responder.shutil.which", return_value=None),
            pytest.raises(ValueError, match="No Claude CLI or Anthropic API key"),
        ):
            EvaResponder(anthropic_key=None)

    def test_accepts_api_key_without_cli(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli=None, api_key="sk-test", role_text="# Eva")
        assert r._api_key == "sk-test"
        assert r._claude_cli is None
        assert "Eva" in r._role_context

    def test_accepts_cli_without_api_key(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva")
        with (
            patch.dict("os.environ", {}, clear=True),
            patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"),
        ):
            r = EvaResponder(anthropic_key=None, role_path=role)
        assert r._claude_cli == "/usr/bin/claude"

    def test_reads_env_var(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Identity")
        with (
            patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-env"}),
            patch("eva.telegram.responder.shutil.which", return_value=None),
        ):
            r = EvaResponder(role_path=role)
        assert r._api_key == "sk-env"

    def test_missing_role_file(self, tmp_path: Path):
        role = tmp_path / "nonexistent" / "ROLE.md"
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)
        assert r._role_context == ""

    def test_custom_model(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        assert r._model == "claude-haiku-4-5-20251001"
        role = tmp_path / "ROLE2.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r2 = EvaResponder(anthropic_key="sk-test", role_path=role, model="claude-opus-4-6")
        assert r2._model == "claude-opus-4-6"


# ── _call_claude dispatch ────────────────────────────────


class TestCallClaudeDispatch:
    @pytest.mark.asyncio
    async def test_prefers_cli(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli="/usr/bin/claude")
        r._call_claude_cli = AsyncMock(return_value="cli result")
        r._call_claude_api = AsyncMock(return_value="api result")

        result = await r._call_claude("system", "user")
        assert result == "cli result"
        r._call_claude_cli.assert_called_once_with("system", "user", continue_session=False)
        r._call_claude_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_falls_back_to_api(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli=None)
        r._call_claude_api = AsyncMock(return_value="api result")

        result = await r._call_claude("system", "user")
        assert result == "api result"
        r._call_claude_api.assert_called_once()


# ── _call_claude_cli ─────────────────────────────────────


class TestCallClaudeCli:
    @pytest.mark.asyncio
    async def test_first_call_sends_full_prompt(self, tmp_path: Path):
        """Without existing session, sends system+user as single prompt."""
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Hello", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await r._call_claude_cli("system prompt", "user text")

        assert result == "Hello"
        args = mock_exec.call_args[0]
        assert args[0] == "/usr/bin/claude"
        assert "-p" in args
        assert "--continue" not in args
        prompt_arg = args[-1]
        assert "system prompt" in prompt_arg
        assert "user text" in prompt_arg

    @pytest.mark.asyncio
    async def test_continue_sends_only_user_text(self, tmp_path: Path):
        """With existing session marker, sends only user text with --continue."""
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)
        # Create session marker
        r._session_marker.touch()

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"I remember", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            result = await r._call_claude_cli("system", "what code?", continue_session=True)

        assert result == "I remember"
        args = mock_exec.call_args[0]
        assert "--continue" in args
        # Only user text, no system prompt
        assert args[-1] == "what code?"
        assert "system" not in " ".join(args[:-1])

    @pytest.mark.asyncio
    async def test_creates_marker_after_first_continue(self, tmp_path: Path):
        """First call with continue_session=True creates session marker."""
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)
        assert not r._session_marker.exists()

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Hello", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            await r._call_claude_cli("system", "hi", continue_session=True)

        assert r._session_marker.exists()

    @pytest.mark.asyncio
    async def test_no_marker_without_continue_session(self, tmp_path: Path):
        """Calls without continue_session=True don't create marker."""
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"result", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            await r._call_claude_cli("system", "hi", continue_session=False)

        assert not r._session_marker.exists()

    @pytest.mark.asyncio
    async def test_stale_session_retries_fresh(self, tmp_path: Path):
        """If --continue fails, resets marker and retries with full prompt."""
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)
        r._session_marker.touch()

        fail_proc = AsyncMock()
        fail_proc.communicate.return_value = (b"", b"error")
        fail_proc.returncode = 1

        ok_proc = AsyncMock()
        ok_proc.communicate.return_value = (b"fresh start", b"")
        ok_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", side_effect=[fail_proc, ok_proc]) as mock_exec:
            result = await r._call_claude_cli("system", "hello", continue_session=True)

        assert result == "fresh start"
        assert mock_exec.call_count == 2
        # First call: --continue with user text only
        first_args = mock_exec.call_args_list[0][0]
        assert "--continue" in first_args
        # Second call: full prompt without --continue
        second_args = mock_exec.call_args_list[1][0]
        assert "--continue" not in second_args
        assert "system" in second_args[-1]

    @pytest.mark.asyncio
    async def test_error_returns_empty(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli="/usr/bin/claude", api_key=None)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"error")
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await r._call_claude_cli("system", "user")

        assert result == ""


# ── _call_claude_api ─────────────────────────────────────


def _mock_claude_response(text: str) -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {
        "content": [{"type": "text", "text": text}],
    }
    return resp


def _mock_empty_response() -> MagicMock:
    resp = MagicMock()
    resp.json.return_value = {"content": []}
    return resp


class TestCallClaudeApi:
    @pytest.mark.asyncio
    async def test_returns_text(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli=None)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("Hello world")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.responder.httpx.AsyncClient", return_value=mock_httpx):
            result = await r._call_claude_api("system", "user")

        assert result == "Hello world"
        call_kwargs = mock_httpx.post.call_args[1]["json"]
        assert call_kwargs["system"] == "system"
        assert call_kwargs["messages"] == [{"role": "user", "content": "user"}]

    @pytest.mark.asyncio
    async def test_empty_content(self, tmp_path: Path):
        r = _make_responder(tmp_path, cli=None)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_empty_response()
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.responder.httpx.AsyncClient", return_value=mock_httpx):
            result = await r._call_claude_api("system", "user")

        assert result == ""


# ── respond ───────────────────────────────────────────────


class TestRespond:
    @pytest.mark.asyncio
    async def test_returns_response(self, tmp_path: Path):
        r = _make_responder(tmp_path, role_text="# Eva\nCommunity support agent.")
        r._call_claude = AsyncMock(return_value="The agents collaborate.")
        result = await r.respond("How does iEvo work?")

        assert result == "The agents collaborate."
        call_args = r._call_claude.call_args[0]
        assert "Eva" in call_args[0]

    @pytest.mark.asyncio
    async def test_includes_role_context(self, tmp_path: Path):
        r = _make_responder(tmp_path, role_text="# Eva\nMeta-evolution agent.")
        r._call_claude = AsyncMock(return_value="Noted.")
        await r.respond("Add dark mode")

        system = r._call_claude.call_args[0][0]
        assert "Meta-evolution agent" in system

    @pytest.mark.asyncio
    async def test_uses_continue_session(self, tmp_path: Path):
        r = _make_responder(tmp_path)
        r._call_claude = AsyncMock(return_value="Response.")
        await r.respond("Hello")

        r._call_claude.assert_called_once()
        assert r._call_claude.call_args[1]["continue_session"] is True

    @pytest.mark.asyncio
    async def test_without_role_context(self, tmp_path: Path):
        role = tmp_path / "nonexistent" / "ROLE.md"
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="Welcome.")
        result = await r.respond("Hello!")

        assert result == "Welcome."
        system = r._call_claude.call_args[0][0]
        assert "identity details" not in system


# ── Constants ─────────────────────────────────────────────


class TestConstants:
    def test_community_system_has_rules(self):
        assert "Eva" in COMMUNITY_SYSTEM
        assert "open source" in COMMUNITY_SYSTEM
        assert "community support" in COMMUNITY_SYSTEM
        assert "feature request" in COMMUNITY_SYSTEM
