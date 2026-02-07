from datetime import datetime

from aiohttp import web


MOCK_SESSIONS = [
    {
        "id": 1472603904834535425,
        "map": "big_cleanup",
        "startTime": "2025-11-12T08:55:04Z",
        "endTime": "2025-11-12T09:07:28Z",
        "difficulty": 1,
        "sessionDurationSeconds": 718.10004,
        "difficultyReward": 3,
        "participants": [
            {
                "username": "Player1",
                "death": 0,
                "mobKills": 202,
                "damageReceived": 739.62,
                "damageDealt": 185850.23,
                "armorClass": "combined",
                "armorItemId": "item1",
                "armorLevel": 0,
                "primaryWeaponItemId": "weapon1",
                "primaryWeaponLevel": 8,
                "secondaryWeaponItemId": "weapon2",
                "secondaryWeaponLevel": 0,
            },
            {
                "username": "Player2",
                "death": 0,
                "mobKills": 291,
                "damageReceived": 482.0,
                "damageDealt": 312414.06,
                "armorClass": "combined",
                "armorItemId": "item2",
                "armorLevel": 15,
                "primaryWeaponItemId": "weapon3",
                "primaryWeaponLevel": 15,
                "secondaryWeaponItemId": "weapon4",
                "secondaryWeaponLevel": 5,
            },
        ],
    },
    {
        "id": 1472603904834535426,
        "map": "shock_therapy",
        "startTime": "2025-11-13T10:00:00Z",
        "endTime": "2025-11-13T10:15:00Z",
        "difficulty": 2,
        "sessionDurationSeconds": 900.0,
        "difficultyReward": 5,
        "participants": [
            {
                "username": "Player3",
                "death": 1,
                "mobKills": 150,
                "damageReceived": 1000.0,
                "damageDealt": 150000.0,
                "armorClass": "light",
                "armorItemId": "item3",
                "armorLevel": 10,
                "primaryWeaponItemId": "weapon5",
                "primaryWeaponLevel": 10,
                "secondaryWeaponItemId": "weapon6",
                "secondaryWeaponLevel": 10,
            }
        ],
    },
    {
        "id": 1472603904834535427,
        "map": "big_cleanup",
        "startTime": "2025-11-14T12:00:00Z",
        "endTime": "2025-11-14T12:20:00Z",
        "difficulty": 1,
        "sessionDurationSeconds": 1200.0,
        "difficultyReward": 4,
        "participants": [
            {
                "username": "Player1",
                "death": 0,
                "mobKills": 300,
                "damageReceived": 500.0,
                "damageDealt": 250000.0,
                "armorClass": "heavy",
                "armorItemId": "item4",
                "armorLevel": 15,
                "primaryWeaponItemId": "weapon7",
                "primaryWeaponLevel": 15,
                "secondaryWeaponItemId": "weapon8",
                "secondaryWeaponLevel": 0,
            }
        ],
    },
]


async def operations_sessions(request: web.Request) -> web.Response:
    query = request.query

    sessions = MOCK_SESSIONS.copy()

    # filter maps
    map_filter = query.get("map")
    if map_filter:
        sessions = [s for s in sessions if s["map"] == map_filter]

    # filter username
    username_filter = query.get("username")
    if username_filter:
        filtered_sessions = []
        for session in sessions:
            if any(p["username"] == username_filter for p in session["participants"]):
                filtered_sessions.append(session)
        sessions = filtered_sessions

    # filter dt before
    before_filter = query.get("before")
    if before_filter:
        sessions = [s for s in sessions if _parse_date(s["endTime"]) < _parse_date(before_filter)]

    # filter dt after
    after_filter = query.get("after")
    if after_filter:
        sessions = [s for s in sessions if _parse_date(s["endTime"]) > _parse_date(after_filter)]

    # sorting
    sort = query.get("sort", "date_finish")
    order = query.get("order", "ascending")

    if sort in ["date_finish", "endTime"]:
        sessions.sort(key=lambda x: x["endTime"], reverse=(order == "descending"))

    # pagination
    limit = int(query.get("limit", 20))
    offset = int(query.get("offset", 0))

    # offset and limit
    total = len(sessions)
    paginated_sessions = sessions[offset : offset + limit]

    return web.json_response({"total": total, "sessions": paginated_sessions})


def _parse_date(date_str: str) -> datetime:
    if date_str.endswith("Z"):
        date_str = date_str[:-1] + "+00:00"

    return datetime.fromisoformat(date_str)
