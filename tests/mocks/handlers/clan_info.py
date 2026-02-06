from aiohttp import web


async def clan_info(request: web.Request) -> web.Response:
    clan_id = request.match_info.get("clanid")

    return web.json_response(
        {
            "id": clan_id,
            "name": "TestClan",
            "tag": "TEST",
            "level": 2,
            "levelPoints": 6500000,
            "registrationTime": "2024-01-01T12:00:00Z",
            "alliance": "merc",
            "description": "Test description",
            "leader": "TestLeader",
            "memberCount": 35,
        }
    )
