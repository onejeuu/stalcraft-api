from aiohttp import web


async def profile(request: web.Request) -> web.Response:
    character = request.match_info.get("character", "TestPlayer")

    return web.json_response(
        {
            "username": character,
            "uuid": "550e8400-e29b-41d4-a716-446655440000",
            "status": "§4ProfileAbout",
            "alliance": "bandits",
            "lastLogin": "2026-01-01T12:00:00.000Z",
            "displayedAchievements": ["svinomatka"],
            "stats": [
                {"id": "kil", "type": "INTEGER", "value": 15000},
                {"id": "dea", "type": "INTEGER", "value": 5000},
                {"id": "par-tim", "type": "DURATION", "value": 1000000000},
                {"id": "pla-tim", "type": "DURATION", "value": 2000000000},
                {"id": "ach-points", "type": "INTEGER", "value": 1000},
                {"id": "exp-kil", "type": "INTEGER", "value": 100},
                {"id": "mut-kil", "type": "INTEGER", "value": 5000},
                {"id": "npc-kil", "type": "INTEGER", "value": 3000},
                {"id": "sho-fir", "type": "INTEGER", "value": 100000},
                {"id": "sho-hit", "type": "INTEGER", "value": 25000},
                {"id": "dam-dea-pla", "type": "DECIMAL", "value": 5000000.5},
                {"id": "dam-rec-pla", "type": "DECIMAL", "value": 2000000.75},
                {"id": "reg-tim", "type": "DATE", "value": "2018-01-01T12:00:00.000Z"},
                {"id": "joined-guild", "type": "DATE", "value": "2020-01-01T12:00:00.000Z"},
            ],
        }
    )
