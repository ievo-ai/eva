"""Tests for the low-level GitHub REST API client."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from eva.github.client import GitHubClient, PRResult


class TestGitHubClientMethods:
    @pytest.mark.asyncio
    async def test_get_default_branch(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"default_branch": "main"}

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_default_branch("ievo-ai/eva")

        assert result == "main"

    @pytest.mark.asyncio
    async def test_get_ref_sha(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"object": {"sha": "abc123"}}

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_ref_sha("ievo-ai/eva", "main")

        assert result == "abc123"

    @pytest.mark.asyncio
    async def test_create_branch(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.raise_for_status = MagicMock()

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            await client.create_branch("ievo-ai/eva", "eva/mut-001", "abc123")

        mock_http.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_branch_already_exists(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 422

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            await client.create_branch("ievo-ai/eva", "eva/mut-001", "abc123")

        # Should not raise

    @pytest.mark.asyncio
    async def test_get_file_content(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"content": "dGVzdA==", "sha": "file-sha"}

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_file_content("ievo-ai/eva", "README.md", "main")

        assert result is not None
        assert result["sha"] == "file-sha"

    @pytest.mark.asyncio
    async def test_get_file_content_not_found(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 404

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.get_file_content("ievo-ai/eva", "nonexistent.md", "main")

        assert result is None

    @pytest.mark.asyncio
    async def test_create_or_update_file_new(self):
        client = GitHubClient("test-token")

        # get_file_content returns None (new file)
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 404

        mock_put_resp = MagicMock()
        mock_put_resp.status_code = 201
        mock_put_resp.raise_for_status = MagicMock()
        mock_put_resp.json.return_value = {"commit": {"sha": "new-sha"}}

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_get_resp
        mock_http.put.return_value = mock_put_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.create_or_update_file(
                repo="ievo-ai/eva",
                path="test.md",
                content="# Test",
                message="add test",
                branch="main",
            )

        assert result == "new-sha"

    @pytest.mark.asyncio
    async def test_create_or_update_file_existing(self):
        client = GitHubClient("test-token")

        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.raise_for_status = MagicMock()
        mock_get_resp.json.return_value = {"content": "b2xk", "sha": "old-sha"}

        mock_put_resp = MagicMock()
        mock_put_resp.status_code = 200
        mock_put_resp.raise_for_status = MagicMock()
        mock_put_resp.json.return_value = {"commit": {"sha": "updated-sha"}}

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_get_resp
        mock_http.put.return_value = mock_put_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.create_or_update_file(
                repo="ievo-ai/eva",
                path="test.md",
                content="# Updated",
                message="update test",
                branch="main",
            )

        assert result == "updated-sha"
        # Verify SHA was included in payload
        put_call = mock_http.put.call_args
        assert put_call[1]["json"]["sha"] == "old-sha"

    @pytest.mark.asyncio
    async def test_create_pull_request(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 201
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {
            "html_url": "https://github.com/ievo-ai/eva/pull/1",
            "number": 1,
        }

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.create_pull_request(
                repo="ievo-ai/eva",
                title="Test PR",
                body="Body",
                head="feature",
                base="main",
            )

        assert isinstance(result, PRResult)
        assert result.pr_url == "https://github.com/ievo-ai/eva/pull/1"
        assert result.pr_number == 1

    @pytest.mark.asyncio
    async def test_create_pull_request_auto_base(self):
        client = GitHubClient("test-token")

        # First call: get_default_branch
        mock_branch_resp = MagicMock()
        mock_branch_resp.status_code = 200
        mock_branch_resp.raise_for_status = MagicMock()
        mock_branch_resp.json.return_value = {"default_branch": "main"}

        # Second call: create PR
        mock_pr_resp = MagicMock()
        mock_pr_resp.status_code = 201
        mock_pr_resp.raise_for_status = MagicMock()
        mock_pr_resp.json.return_value = {
            "html_url": "https://github.com/ievo-ai/eva/pull/2",
            "number": 2,
        }

        mock_http = AsyncMock()
        mock_http.get.return_value = mock_branch_resp
        mock_http.post.return_value = mock_pr_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            result = await client.create_pull_request(
                repo="ievo-ai/eva",
                title="Test PR",
                body="Body",
                head="feature",
                base=None,  # auto-detect
            )

        assert result.pr_number == 2

    @pytest.mark.asyncio
    async def test_add_labels(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 200

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            await client.add_labels("ievo-ai/eva", 1, ["eva", "automated"])

    @pytest.mark.asyncio
    async def test_add_labels_error_ignored(self):
        client = GitHubClient("test-token")

        mock_resp = MagicMock()
        mock_resp.status_code = 404  # Label doesn't exist

        mock_http = AsyncMock()
        mock_http.post.return_value = mock_resp
        mock_http.__aenter__ = AsyncMock(return_value=mock_http)
        mock_http.__aexit__ = AsyncMock(return_value=False)

        with patch("eva.github.client.httpx.AsyncClient", return_value=mock_http):
            await client.add_labels("ievo-ai/eva", 1, ["nonexistent"])

        # Should not raise
