from aiohttp import web


MOCK_CHARACTERS = [
    {
        "information": {
            "id": "11111111-1111-1111-1111-111111111111",
            "name": "CharacterOne",
            "creationTime": "2023-01-01T12:00:00Z",
        }
    },
    {
        "information": {
            "id": "22222222-2222-2222-2222-222222222222",
            "name": "CharacterTwo",
            "creationTime": "2024-02-01T12:00:00Z",
        }
    },
    {
        "information": {
            "id": "33333333-3333-3333-3333-333333333333",
            "name": "CharacterThree",
            "creationTime": "2025-03-01T12:00:00Z",
        }
    },
    {
        "information": {
            "id": "44444444-4444-4444-4444-444444444444",
            "name": "CharacterFour",
            "creationTime": "2026-04-01T12:00:00Z",
        }
    },
]


async def characters(request: web.Request) -> web.Response:
    return web.json_response(MOCK_CHARACTERS)
