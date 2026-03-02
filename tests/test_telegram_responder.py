"""Tests for Eva's community responder."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.telegram.responder import (
    CLASSIFY_SYSTEM,
    COMMUNITY_SYSTEM,
    EvaResponder,
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
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)
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
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role, model="claude-opus-4-6")
        assert r._model == "claude-opus-4-6"


# ── _call_claude dispatch ────────────────────────────────


class TestCallClaudeDispatch:
    @pytest.mark.asyncio
    async def test_prefers_cli(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude_cli = AsyncMock(return_value="cli result")
        r._call_claude_api = AsyncMock(return_value="api result")

        result = await r._call_claude("system", "user")
        assert result == "cli result"
        r._call_claude_cli.assert_called_once_with("system", "user")
        r._call_claude_api.assert_not_called()

    @pytest.mark.asyncio
    async def test_falls_back_to_api(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude_api = AsyncMock(return_value="api result")

        result = await r._call_claude("system", "user")
        assert result == "api result"
        r._call_claude_api.assert_called_once()


# ── _call_claude_cli ─────────────────────────────────────


class TestCallClaudeCli:
    @pytest.mark.asyncio
    async def test_returns_stdout(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r = EvaResponder(anthropic_key=None, role_path=role)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"Hello world", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await r._call_claude_cli("system", "user")

        assert result == "Hello world"

    @pytest.mark.asyncio
    async def test_error_returns_empty(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r = EvaResponder(anthropic_key=None, role_path=role)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"", b"error")
        mock_proc.returncode = 1

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc):
            result = await r._call_claude_cli("system", "user")

        assert result == ""

    @pytest.mark.asyncio
    async def test_passes_correct_args(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value="/usr/bin/claude"):
            r = EvaResponder(anthropic_key=None, role_path=role)

        mock_proc = AsyncMock()
        mock_proc.communicate.return_value = (b"result", b"")
        mock_proc.returncode = 0

        with patch("asyncio.create_subprocess_exec", return_value=mock_proc) as mock_exec:
            await r._call_claude_cli("system prompt", "user text")

        args = mock_exec.call_args[0]
        assert args[0] == "/usr/bin/claude"
        assert "-p" in args
        assert "--continue" in args
        assert "--model" in args
        assert "haiku" in args
        # Prompt contains both system and user text
        prompt_arg = args[-1]
        assert "system prompt" in prompt_arg
        assert "user text" in prompt_arg


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
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

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
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_empty_response()
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.telegram.responder.httpx.AsyncClient", return_value=mock_httpx):
            result = await r._call_claude_api("system", "user")

        assert result == ""


# ── classify ──────────────────────────────────────────────


class TestClassify:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "response,expected",
        [
            ("feature_request", "feature_request"),
            ("bug_report", "bug_report"),
            ("question", "question"),
            ("chat", "chat"),
            ("noise", "noise"),
            ("  Feature_Request  ", "feature_request"),
        ],
    )
    async def test_valid_categories(self, tmp_path: Path, response: str, expected: str):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value=response)
        result = await r.classify("Test message")
        assert result == expected

    @pytest.mark.asyncio
    async def test_invalid_category_defaults_to_noise(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="gibberish")
        result = await r.classify("Test")
        assert result == "noise"


# ── respond ───────────────────────────────────────────────


class TestRespond:
    @pytest.mark.asyncio
    async def test_noise_returns_none(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)
        result = await r.respond("spam", "noise")
        assert result is None

    @pytest.mark.asyncio
    async def test_question_returns_response(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva\nI am the mother.")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="My children work together in harmony.")
        result = await r.respond("How does iEvo work?", "question")

        assert result == "My children work together in harmony."
        call_args = r._call_claude.call_args[0]
        assert "Eva" in call_args[0]  # system prompt
        assert "[Category: question]" in call_args[1]  # user prompt

    @pytest.mark.asyncio
    async def test_feature_request_includes_role_context(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva\nMeta-evolution agent.")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="Noted.")
        result = await r.respond("Add dark mode", "feature_request")

        assert result == "Noted."
        system = r._call_claude.call_args[0][0]
        assert "Meta-evolution agent" in system

    @pytest.mark.asyncio
    async def test_respond_without_role_context(self, tmp_path: Path):
        role = tmp_path / "nonexistent" / "ROLE.md"
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="Welcome.")
        result = await r.respond("Hello!", "chat")

        assert result == "Welcome."
        system = r._call_claude.call_args[0][0]
        assert "identity details" not in system


# ── process_message ───────────────────────────────────────


class TestProcessMessage:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(side_effect=["question", "The agents collaborate."])
        response, category = await r.process_message("How do agents work?")

        assert category == "question"
        assert response == "The agents collaborate."

    @pytest.mark.asyncio
    async def test_noise_skips_response(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        with patch("eva.telegram.responder.shutil.which", return_value=None):
            r = EvaResponder(anthropic_key="sk-test", role_path=role)

        r._call_claude = AsyncMock(return_value="noise")
        response, category = await r.process_message("random gibberish")

        assert category == "noise"
        assert response is None


# ── Constants ─────────────────────────────────────────────


class TestConstants:
    def test_classify_system_has_categories(self):
        for cat in ["feature_request", "bug_report", "question", "chat", "noise"]:
            assert cat in CLASSIFY_SYSTEM

    def test_community_system_has_rules(self):
        assert "Eva" in COMMUNITY_SYSTEM
        assert "children" in COMMUNITY_SYSTEM
        assert "open source" in COMMUNITY_SYSTEM
