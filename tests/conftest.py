from typing import AsyncGenerator, Awaitable, Callable, TypeAlias

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from scapi.client.app import AppClient
from scapi.client.user import UserClient


AioHTTPServer: TypeAlias = Callable[[web.Application], Awaitable[TestServer]]


@pytest.fixture
async def server(aiohttp_server: AioHTTPServer) -> TestServer:
    from tests.mocks import handlers

    # Create app
    app = web.Application()
    app.router.add_get("/regions", handlers.regions)
    app.router.add_get("/{region}/emission", handlers.emission)
    app.router.add_get("/{region}/character/by-name/{character}/profile", handlers.profile)
    app.router.add_get("/{region}/operations/sessions", handlers.operations_sessions)
    app.router.add_get("/{region}/auction/{item}/lots", handlers.auction_lots)
    app.router.add_get("/{region}/auction/{item}/history", handlers.auction_history)
    app.router.add_get("/{region}/clans", handlers.clans)
    app.router.add_get("/{region}/clan/{clanid}/info", handlers.clan_info)
    app.router.add_get("/{region}/clan/{clanid}/members", handlers.clan_members)
    app.router.add_get("/{region}/friends/{character}", handlers.friends)
    app.router.add_get("/{region}/characters", handlers.characters)

    # Run server on random port
    server = await aiohttp_server(app)
    return server


@pytest.fixture
async def client(server: TestServer) -> AsyncGenerator[AppClient, None]:
    base_url = f"http://{server.host}:{server.port}"
    client = AppClient(token="6f776c7320617265206e6f7420776861742074686579207365656d", base_url=base_url)

    yield client
    await client.close()


@pytest.fixture
async def userclient(server: TestServer) -> AsyncGenerator[UserClient, None]:
    base_url = f"http://{server.host}:{server.port}"
    client = UserClient(token="6f776c7320617265206e6f7420776861742074686579207365656d", base_url=base_url)

    yield client
    await client.close()
