from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest
from pydantic import ValidationError

from scapi.oauth.client import OAuthClient
from scapi.oauth.models import AppToken, TokenResponse, UserToken


def test_oauth_client_init():
    client = OAuthClient(
        client_id="test_client_id",
        client_secret="test_client_secret",
        redirect_uri="http://localhost:8080",
    )

    assert client._client_id == "test_client_id"
    assert client._client_secret == "test_client_secret"
    assert client._redirect_uri == "http://localhost:8080"
    assert client._http is not None


def test_oauth_client_get_authorize_url():
    client = OAuthClient(client_id="test_id", client_secret="test_secret")

    url = client.get_authorize_url(state="random_state")

    assert client._base_url in url
    assert "test_id" in url
    assert "random_state" in url
    assert "response_type=code" in url

    url2 = client.get_authorize_url(state="state2", redirect_uri="http://custom.com", scope="custom_scope")
    assert "custom.com" in url2
    assert "custom_scope" in url2


@pytest.mark.asyncio
async def test_oauth_client_get_app_token():
    client = OAuthClient(client_id="test_id", client_secret="test_secret")

    mock_response = {"access_token": "app_token", "expires_in": 3600}
    client._http.POST = AsyncMock(return_value=mock_response)
    client._parse = Mock(return_value="parsed_token")

    result = await client.get_app_token()

    client._http.POST.assert_called_once()
    call_data = client._http.POST.call_args[1]["data"]
    assert call_data["client_id"] == "test_id"
    assert call_data["grant_type"] == "client_credentials"
    assert result == "parsed_token"


@pytest.mark.asyncio
async def test_oauth_client_get_user_token():
    client = OAuthClient(client_id="test_id", client_secret="test_secret")

    mock_response = {"access_token": "user_token", "refresh_token": "refresh"}
    client._http.POST = AsyncMock(return_value=mock_response)
    client._parse = Mock(return_value="parsed_user_token")

    result = await client.get_user_token(code="auth_code_123")

    client._http.POST.assert_called_once()
    call_data = client._http.POST.call_args[1]["data"]
    assert call_data["code"] == "auth_code_123"
    assert call_data["grant_type"] == "authorization_code"
    assert result == "parsed_user_token"


@pytest.mark.asyncio
async def test_oauth_client_refresh_user_token():
    client = OAuthClient(client_id="test_id", client_secret="test_secret")

    mock_response = {"access_token": "new_token", "refresh_token": "new_refresh"}
    client._http.POST = AsyncMock(return_value=mock_response)
    client._parse = Mock(return_value="parsed_refreshed_token")

    result = await client.refresh_user_token(refresh_token="old_refresh_token", scope="new_scope")

    client._http.POST.assert_called_once()
    call_data = client._http.POST.call_args[1]["data"]
    assert call_data["refresh_token"] == "old_refresh_token"
    assert call_data["grant_type"] == "refresh_token"
    assert call_data["scope"] == "new_scope"
    assert result == "parsed_refreshed_token"


@pytest.mark.asyncio
async def test_oauth_client_validate_user_token():
    client = OAuthClient(client_id="test_id", client_secret="test_secret")

    mock_response = {"id": "user_123", "username": "test_user"}
    client._http.GET = AsyncMock(return_value=mock_response)
    client._parse = Mock(return_value="parsed_user_info")

    result = await client.validate_user_token(token="user_access_token")

    client._http.GET.assert_called_once()
    call_headers = client._http.GET.call_args[1]["headers"]
    assert call_headers["Authorization"] == "Bearer user_access_token"
    assert result == "parsed_user_info"


def test_token_response_parse_expires_in():
    data = {
        "token_type": "Bearer",
        "access_token": "test_token",
        "expires_in": "3600",
    }

    token = TokenResponse.model_validate(data)
    assert isinstance(token.expires_in, datetime)

    # Проверяем что время в будущем
    time_diff = token.expires_in - datetime.now()
    assert timedelta(hours=0.9) < time_diff < timedelta(hours=1.1)

    data2 = {"token_type": "Bearer", "access_token": "test_token", "expires_in": "not_a_number"}

    with pytest.raises(ValidationError):
        TokenResponse.model_validate(data2)

    app_data = {"token_type": "Bearer", "access_token": "app_token", "expires_in": "7200"}

    app_token = AppToken.model_validate(app_data)
    assert isinstance(app_token.expires_in, datetime)

    user_data = {
        "token_type": "Bearer",
        "access_token": "user_token",
        "expires_in": "1800",
        "refresh_token": "refresh_token_123",
    }

    user_token = UserToken.model_validate(user_data)
    assert isinstance(user_token.expires_in, datetime)
    assert user_token.refresh_token == "refresh_token_123"
