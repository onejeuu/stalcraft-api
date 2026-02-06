from aiohttp import web


MOCK_LOTS = [
    {
        "itemId": "9nd0",
        "amount": 1,
        "startPrice": 34999,
        "currentPrice": None,
        "buyoutPrice": 0,
        "startTime": "2026-02-01T12:00:00Z",
        "endTime": "2026-02-03T12:00:00Z",
        "additional": {},
    },
    {
        "itemId": "9nd0",
        "amount": 1,
        "startPrice": 1,
        "currentPrice": 11,
        "buyoutPrice": 90000,
        "startTime": "2026-02-02T12:00:00Z",
        "endTime": "2026-02-04T12:00:00Z",
        "additional": {},
    },
    {
        "itemId": "9nd0",
        "amount": 1,
        "startPrice": 29999,
        "currentPrice": None,
        "buyoutPrice": 30000,
        "startTime": "2026-02-03T12:00:00Z",
        "endTime": "2026-02-05T12:00:00Z",
        "additional": {},
    },
]


async def auction_lots(request: web.Request) -> web.Response:
    query = request.query
    limit = int(query.get("limit", 20))
    offset = int(query.get("offset", 0))

    total = len(MOCK_LOTS)
    paginated_lots = MOCK_LOTS[offset : offset + limit]

    return web.json_response({"total": total, "lots": paginated_lots})
