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
    def test_raises_without_api_key(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            pytest.raises(ValueError, match="No Anthropic API key"),
        ):
            EvaResponder(anthropic_key=None)

    def test_accepts_explicit_key(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)
        assert r._api_key == "sk-test"
        assert "Eva" in r._role_context

    def test_reads_env_var(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Identity")
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "sk-env"}):
            r = EvaResponder(role_path=role)
        assert r._api_key == "sk-env"

    def test_missing_role_file(self, tmp_path: Path):
        role = tmp_path / "nonexistent" / "ROLE.md"
        r = EvaResponder(anthropic_key="sk-test", role_path=role)
        assert r._role_context == ""

    def test_custom_model(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role, model="claude-opus-4-6")
        assert r._model == "claude-opus-4-6"


# ── _call_claude ──────────────────────────────────────────


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


class TestCallClaude:
    @pytest.mark.asyncio
    async def test_returns_text(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("Hello world")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r._call_claude("system", "user")

        assert result == "Hello world"
        call_kwargs = mock_httpx.post.call_args[1]["json"]
        assert call_kwargs["system"] == "system"
        assert call_kwargs["messages"] == [{"role": "user", "content": "user"}]

    @pytest.mark.asyncio
    async def test_empty_content(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_empty_response()
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r._call_claude("system", "user")

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
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response(response)
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r.classify("Test message")

        assert result == expected

    @pytest.mark.asyncio
    async def test_invalid_category_defaults_to_noise(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("gibberish")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r.classify("Test")

        assert result == "noise"


# ── respond ───────────────────────────────────────────────


class TestRespond:
    @pytest.mark.asyncio
    async def test_noise_returns_none(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)
        result = await r.respond("spam", "noise")
        assert result is None

    @pytest.mark.asyncio
    async def test_question_returns_response(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva\nI am the mother.")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response(
            "My children work together in harmony."
        )
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r.respond("How does iEvo work?", "question")

        assert result == "My children work together in harmony."
        call_kwargs = mock_httpx.post.call_args[1]["json"]
        assert "Eva" in call_kwargs["system"]
        assert "[Category: question]" in call_kwargs["messages"][0]["content"]

    @pytest.mark.asyncio
    async def test_feature_request_includes_role_context(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("# Eva\nMeta-evolution agent.")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("Noted.")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r.respond("Add dark mode", "feature_request")

        assert result == "Noted."
        system = mock_httpx.post.call_args[1]["json"]["system"]
        assert "Meta-evolution agent" in system

    @pytest.mark.asyncio
    async def test_respond_without_role_context(self, tmp_path: Path):
        role = tmp_path / "nonexistent" / "ROLE.md"
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("Welcome.")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            result = await r.respond("Hello!", "chat")

        assert result == "Welcome."
        system = mock_httpx.post.call_args[1]["json"]["system"]
        assert "identity details" not in system


# ── process_message ───────────────────────────────────────


class TestProcessMessage:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        call_count = 0
        responses = ["question", "The agents collaborate."]

        def make_response(*args: object, **kwargs: object) -> MagicMock:
            nonlocal call_count
            resp = _mock_claude_response(responses[call_count])
            call_count += 1
            return resp

        mock_httpx = AsyncMock()
        mock_httpx.post.side_effect = make_response
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
            response, category = await r.process_message("How do agents work?")

        assert category == "question"
        assert response == "The agents collaborate."

    @pytest.mark.asyncio
    async def test_noise_skips_response(self, tmp_path: Path):
        role = tmp_path / "ROLE.md"
        role.write_text("")
        r = EvaResponder(anthropic_key="sk-test", role_path=role)

        mock_httpx = AsyncMock()
        mock_httpx.post.return_value = _mock_claude_response("noise")
        mock_httpx.__aenter__ = AsyncMock(return_value=mock_httpx)
        mock_httpx.__aexit__ = AsyncMock(return_value=False)

        with patch(
            "eva.telegram.responder.httpx.AsyncClient",
            return_value=mock_httpx,
        ):
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
        assert "NEVER reveal" in COMMUNITY_SYSTEM
