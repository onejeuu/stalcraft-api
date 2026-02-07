import os
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import ClientResponse, ClientSession

from scapi.exceptions import RequestError
from scapi.http.api import APIClient
from scapi.http.auth.creds import CredentialsHTTPClient
from scapi.http.auth.token import TokenHTTPClient
from scapi.http.client import HTTPClient
from scapi.http.ratelimit import RateLimit


def test_api_client_ratelimit():
    mock_http = Mock(spec=HTTPClient)
    mock_ratelimit = Mock()
    mock_http.ratelimit = mock_ratelimit

    client = APIClient()
    client._http = mock_http

    assert client.ratelimit == mock_ratelimit


@pytest.mark.asyncio
async def test_api_client_async_context():
    class TestClient(APIClient):
        closed = False

        async def close(self):
            self.closed = True

    async with TestClient() as client:
        assert isinstance(client, TestClient)
        assert not client.closed

    assert client.closed


def test_credentials_http_client_with_headers():
    custom_headers = {"X-Custom": "value"}

    client = CredentialsHTTPClient(client_id="test_id", client_secret="test_secret", headers=custom_headers)

    assert client._headers["Client-Id"] == "test_id"
    assert client._headers["Client-Secret"] == "test_secret"
    assert client._headers["X-Custom"] == "value"


def test_token_http_client_token_part():
    client = TokenHTTPClient(token="very_long_token_string_12345")

    masked = client.token_part
    assert isinstance(masked, str)
    assert len(masked) > 0
    assert "..." in masked

    client2 = TokenHTTPClient()
    assert client2.token_part == "None"


def test_token_http_client_update_token():
    client = TokenHTTPClient(token="old_token")

    client.update_token("new_token")

    assert client._token == "new_token"
    assert client._headers["Authorization"] == "Bearer new_token"


@pytest.mark.asyncio
async def test_http_client_methods():
    client = HTTPClient()
    client.request = AsyncMock(return_value={"result": "ok"})

    await client.GET("test_url")
    client.request.assert_called_with(method="GET", url="test_url", params=None, headers=None, filename=None, raw=False)

    await client.HEAD("test_url")
    client.request.assert_called_with(method="HEAD", url="test_url", params=None, headers=None, raw=False)

    data = {"key": "value"}
    await client.POST("test_url", data=data)
    client.request.assert_called_with(method="POST", url="test_url", params=None, data=data, headers=None, raw=False)

    await client.PUT("test_url", data={"update": "data"})
    client.request.assert_called_with(
        method="PUT", url="test_url", params=None, data={"update": "data"}, headers=None, raw=False
    )

    await client.DELETE("test_url")
    client.request.assert_called_with(method="DELETE", url="test_url", params=None, headers=None, raw=False)

    await client.PATCH("test_url", data={"patch": "data"})
    client.request.assert_called_with(
        method="PATCH", url="test_url", params=None, data={"patch": "data"}, headers=None, raw=False
    )


@pytest.mark.asyncio
async def test_http_client_use_session_creation():
    client = HTTPClient()

    session = await client._use_session()
    assert session is not None
    assert client._session is session
    assert isinstance(session, ClientSession)

    same_session = await client._use_session()
    assert same_session is session

    await client.close()


@pytest.mark.asyncio
async def test_http_client_parse_text():
    client = HTTPClient()

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.headers.get.return_value = "text/html"
    mock_response.text = AsyncMock(return_value="<html>test</html>")

    result = await client._parse(mock_response, raw=False)
    assert result == "<html>test</html>"


@pytest.mark.asyncio
async def test_http_client_stream_to_file():
    client = HTTPClient()

    mock_session = AsyncMock(spec=ClientSession)
    client._use_session = AsyncMock(return_value=mock_session)

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200

    mock_iterator = AsyncMock()
    mock_iterator.__aiter__.return_value = mock_iterator
    mock_iterator.__anext__.side_effect = [b"data", StopAsyncIteration()]
    mock_response.content.iter_chunked.return_value = mock_iterator

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None

    mock_session.request.return_value = mock_context

    with tempfile.NamedTemporaryFile(delete=False) as f:
        filename = f.name

    try:
        result = await client.request("GET", "test", filename=filename)
        assert result == filename

    finally:
        if os.path.exists(filename):
            os.unlink(filename)


@pytest.mark.asyncio
async def test_http_client_update_ratelimit_with_error():
    client = HTTPClient()

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.headers = {"X-RateLimit-Remaining": "invalid"}

    await client._update_ratelimit(mock_response)


@pytest.mark.asyncio
async def test_http_client_close():
    client = HTTPClient()
    client._session = AsyncMock(spec=ClientSession)
    client._session.closed = False
    client._session.close = AsyncMock()

    await client.close()
    client._session.close.assert_called_once()


def test_http_client_ratelimit_property():
    client = HTTPClient()
    ratelimit = client.ratelimit
    assert ratelimit is client._ratelimit


@pytest.mark.asyncio
async def test_http_client_request_error():
    client = HTTPClient()

    mock_session = AsyncMock(spec=ClientSession)
    client._use_session = AsyncMock(return_value=mock_session)

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 404
    mock_response.method = "GET"
    mock_response.url = "http://test.com/404"
    mock_response.json = AsyncMock(return_value={"error": "Not found"})

    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None

    mock_session.request.return_value = mock_context

    with pytest.raises(RequestError):
        await client.request("GET", "test")


@pytest.mark.asyncio
async def test_http_client_on_error_with_json_exception():
    client = HTTPClient()

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 500
    mock_response.method = "GET"
    mock_response.url = "http://test.com/error"

    mock_response.json = AsyncMock(side_effect=Exception("Invalid JSON"))
    mock_response.text = AsyncMock(return_value="Error text")

    with pytest.raises(Exception):
        await client._on_error(mock_response)

    mock_response.text.assert_called_once_with(errors="replace")


@pytest.mark.asyncio
async def test_http_client_parse_raw():
    client = HTTPClient()

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.read = AsyncMock(return_value=b"rawbytes")

    result = await client._parse(mock_response, raw=True)
    assert result == b"rawbytes"


@pytest.mark.asyncio
async def test_http_client_update_ratelimit_exception():
    client = HTTPClient()

    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.headers = {}

    await client._update_ratelimit(mock_response)


@pytest.mark.asyncio
async def test_http_client_async_context_manager():
    client = HTTPClient()
    client.close = AsyncMock()

    async with client as entered_client:
        assert entered_client is client

    client.close.assert_called_once()


@pytest.mark.asyncio
async def test_http_client_async_context_with_exception():
    client = HTTPClient()
    client.close = AsyncMock()

    with pytest.raises(ValueError):
        async with client:
            raise ValueError("test")

    client.close.assert_called_once()


def test_ratelimit_estimated_used():
    ratelimit = RateLimit.model_construct(limit=100, remaining=75)

    assert ratelimit.estimated_used == 25

    ratelimit2 = RateLimit.model_construct(remaining=75)
    assert ratelimit2.estimated_used is None

    ratelimit3 = RateLimit.model_construct(limit=100)
    assert ratelimit3.estimated_used is None

    ratelimit4 = RateLimit.model_construct()
    assert ratelimit4.estimated_used is None

    ratelimit5 = RateLimit.model_construct(limit=100, remaining=150)
    assert ratelimit5.estimated_used == 0


def test_ratelimit_parse_reset():
    result = RateLimit.parse_reset("1672531199")
    assert isinstance(result, datetime)
    assert result.year == 2023

    result = RateLimit.parse_reset("1672531199000")
    assert isinstance(result, datetime)
    assert result.year == 2023

    result = RateLimit.parse_reset("1672531199000000")
    assert isinstance(result, datetime)
    assert result.year == 2023

    result = RateLimit.parse_reset("not-a-timestamp")
    assert result is None

    result = RateLimit.parse_reset("")
    assert result is None

    result = RateLimit.parse_reset(None)
    assert result is None


def test_ratelimit_from_headers():
    headers = {
        "x-ratelimit-limit": "100",
        "x-ratelimit-remaining": "75",
        "x-ratelimit-used": "25",
        "x-ratelimit-reset": "1672531199",
    }

    ratelimit = RateLimit.model_validate(headers)

    assert ratelimit.limit == 100
    assert ratelimit.remaining == 75
    assert ratelimit.used == 25
    assert isinstance(ratelimit.reset, datetime)
    assert ratelimit.estimated_used == 25


def test_http_client_cleanup():
    client = HTTPClient()

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.close = AsyncMock()

    client._session = mock_session

    client._cleanup()

    mock_session.close.assert_called_once()


def test_http_client_cleanup_with_exception():
    client = HTTPClient()

    mock_session = AsyncMock()
    mock_session.closed = False
    mock_session.close.side_effect = Exception("test")

    client._session = mock_session

    client._cleanup()
