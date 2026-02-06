from aiohttp import web


async def emission(request: web.Request) -> web.Response:
    return web.json_response(
        {
            "previousStart": "2026-01-01T12:00:00Z",
            "previousEnd": "2026-01-01T12:04:00Z",
        }
    )
