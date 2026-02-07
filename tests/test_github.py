from unittest.mock import AsyncMock

import pytest

from scapi.database.github import GitHubClient


@pytest.fixture
def github_client():
    return GitHubClient(token="test_token")


@pytest.fixture
def mock_http_client():
    mock = AsyncMock()
    mock.GET = AsyncMock(return_value={"sha": "test_sha"})
    return mock


@pytest.mark.asyncio
async def test_github_client_init():
    client = GitHubClient()
    assert client._token is None
    assert client.has_token is False

    client = GitHubClient(token="token")
    assert client._token == "token"
    assert client.has_token is True


@pytest.mark.asyncio
async def test_github_client_methods(mock_http_client):
    client = GitHubClient(token="test", owner="test_owner", repository="test_repo", branch="test_branch")
    client._http = mock_http_client

    await client.latest_commit()
    mock_http_client.GET.assert_called_with(f"https://api.github.com/repos/{client._slug}/commits/{client._branch}")

    await client.diff("base", "head")
    mock_http_client.GET.assert_called_with(f"https://api.github.com/repos/{client._slug}/compare/base...head")

    await client.contents("path/to/dir")
    mock_http_client.GET.assert_called_with(f"https://api.github.com/repos/{client._slug}/contents/path/to/dir")

    await client.rawfile("some/file.json", ref="some_ref")
    mock_http_client.GET.assert_called_with(
        f"https://raw.githubusercontent.com/{client._slug}/some_ref/some/file.json", filename=None, raw=True
    )

    await client.archive()
    mock_http_client.GET.assert_called_with(
        f"https://github.com/{client._slug}/archive/refs/heads/{client._branch}.zip", filename=None
    )
