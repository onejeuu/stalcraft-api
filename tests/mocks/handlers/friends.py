from aiohttp import web


async def friends(request: web.Request) -> web.Response:
    return web.json_response(["Friend1", "Friend2", "Friend3"])
