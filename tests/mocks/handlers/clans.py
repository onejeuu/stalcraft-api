from aiohttp import web


MOCK_CLANS = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "ClanOne",
        "tag": "ONE",
        "level": 0,
        "levelPoints": 100000,
        "registrationTime": "2025-01-01T12:00:00Z",
        "alliance": "merc",
        "description": "Description one",
        "leader": "LeaderOne",
        "memberCount": 5,
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "ClanTwo",
        "tag": "TWO",
        "level": 1,
        "levelPoints": 500000,
        "registrationTime": "2024-01-01T12:00:00Z",
        "alliance": "duty",
        "description": "Description two",
        "leader": "LeaderTwo",
        "memberCount": 10,
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "name": "ClanThree",
        "tag": "THREE",
        "level": 2,
        "levelPoints": 1000000,
        "registrationTime": "2023-01-01T12:00:00Z",
        "alliance": "freedom",
        "description": "Description three",
        "leader": "LeaderThree",
        "memberCount": 15,
    },
]


async def clans(request: web.Request) -> web.Response:
    query = request.query
    limit = int(query.get("limit", 20))
    offset = int(query.get("offset", 0))

    total = len(MOCK_CLANS)
    paginated_clans = MOCK_CLANS[offset : offset + limit]

    return web.json_response({"totalClans": total, "data": paginated_clans})
