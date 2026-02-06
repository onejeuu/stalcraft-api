from aiohttp import web


async def regions(request: web.Request) -> web.Response:
    return web.json_response(
        [
            {"id": "RU", "name": "RUSSIA"},
            {"id": "EU", "name": "EUROPE"},
            {"id": "NA", "name": "NORTH AMERICA"},
            {"id": "SEA", "name": "SOUTHEAST ASIA"},
            {"id": "NEA", "name": "NORTHEAST ASIA"},
        ]
    )
