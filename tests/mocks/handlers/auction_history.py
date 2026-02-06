from aiohttp import web


MOCK_PRICES = [
    {"amount": 1, "price": 1500, "time": "2026-02-01T12:00:00Z", "additional": {}},
    {"amount": 1, "price": 6900, "time": "2026-02-01T12:00:00Z", "additional": {}},
    {"amount": 1, "price": 6900, "time": "2026-02-01T12:00:00Z", "additional": {}},
    {"amount": 2, "price": 3000, "time": "2026-02-02T12:00:00Z", "additional": {}},
    {"amount": 5, "price": 1000, "time": "2026-02-03T12:00:00Z", "additional": {}},
]


async def auction_history(request: web.Request) -> web.Response:
    query = request.query
    limit = int(query.get("limit", 20))
    offset = int(query.get("offset", 0))

    total = len(MOCK_PRICES)
    paginated_prices = MOCK_PRICES[offset : offset + limit]

    return web.json_response({"total": total, "prices": paginated_prices})
