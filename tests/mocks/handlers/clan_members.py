from aiohttp import web


MOCK_MEMBERS = [
    {"name": "MemberOne", "rank": "LEADER", "joinTime": "2024-01-01T12:00:00Z"},
    {"name": "MemberTwo", "rank": "OFFICER", "joinTime": "2024-02-01T12:00:00Z"},
    {"name": "MemberThree", "rank": "SOLDIER", "joinTime": "2024-03-01T12:00:00Z"},
    {"name": "MemberFour", "rank": "RECRUIT", "joinTime": "2024-04-01T12:00:00Z"},
]


async def clan_members(request: web.Request) -> web.Response:
    return web.json_response(MOCK_MEMBERS)
