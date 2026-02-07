import warnings
from datetime import datetime

import pytest
from aiohttp.test_utils import TestServer
from pydantic_core import TzInfo

from scapi.client.app import AppClient
from scapi.client.user import UserClient
from scapi.enums import Alliance, ClanRank
from scapi.exceptions import CredentialsError


@pytest.mark.asyncio
async def test_app_client_with_token(server: TestServer):
    base_url = f"http://{server.host}:{server.port}"
    client = AppClient(token="test_token", base_url=base_url)
    assert client is not None
    await client.close()


@pytest.mark.asyncio
async def test_app_client_with_credentials(server: TestServer):
    base_url = f"http://{server.host}:{server.port}"
    client = AppClient(client_id="test_client_id", client_secret="test_client_secret", base_url=base_url)
    assert client is not None
    await client.close()


@pytest.mark.asyncio
async def test_app_client_redundant_auth():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        AppClient(
            token="test_token",
            client_id="test_client_id",
            client_secret="test_client_secret",
            base_url="http://test.com",
        )

        assert len(w) == 1
        assert issubclass(w[0].category, UserWarning)


@pytest.mark.asyncio
async def test_app_client_no_auth_error():
    with pytest.raises(CredentialsError):
        AppClient(base_url="http://test.com")


@pytest.mark.asyncio
async def test_user_client_no_token_error():
    with pytest.raises(CredentialsError):
        UserClient(token="", base_url="http://test.com")


@pytest.mark.asyncio
async def test_regions(client: AppClient):
    regions = await client.regions()

    region_ids = {r.id for r in regions}
    region_names = {r.name for r in regions}

    assert len(regions) == 5
    assert region_ids == {"RU", "EU", "NA", "SEA", "NEA"}
    assert region_names == {"RUSSIA", "EUROPE", "NORTH AMERICA", "SOUTHEAST ASIA", "NORTHEAST ASIA"}


@pytest.mark.asyncio
async def test_emission(client: AppClient):
    emission = await client.emission()

    assert emission.current_start is None
    assert emission.previous_start == datetime(2026, 1, 1, 12, 0, 0, tzinfo=TzInfo(0))
    assert emission.previous_end == datetime(2026, 1, 1, 12, 4, 0, tzinfo=TzInfo(0))


@pytest.mark.asyncio
async def test_profile(client: AppClient):
    profile = await client.profile(username="TestPlayer", region="EU")

    assert profile.name == "TestPlayer"
    assert profile.uuid == "550e8400-e29b-41d4-a716-446655440000"
    assert profile.status == "§4ProfileAbout"
    assert profile.alliance == Alliance.BANDITS
    assert profile.last_login == datetime(2026, 1, 1, 12, 0, 0, tzinfo=TzInfo(0))

    assert len(profile.displayed_achievements) == 1
    assert "svinomatka" in profile.displayed_achievements

    assert profile.clan is None

    assert len(profile.stats) == 14


@pytest.mark.asyncio
async def test_operations_sessions(client: AppClient):
    result = await client.operations_sessions()

    assert result.total == 3
    assert len(result) == 3

    session = result[0]
    assert session.id == 1472603904834535425
    assert session.map == "big_cleanup"
    assert session.difficulty == 1

    assert len(session.participants) == 2
    assert session.participants[0].username == "Player1"
    assert session.participants[0].death == 0


@pytest.mark.asyncio
async def test_operations_sessions_pagination(client: AppClient):
    result1 = await client.operations_sessions(limit=2)
    assert result1.total == 3
    assert len(result1) == 2
    assert result1[0].id == 1472603904834535425
    assert result1[1].id == 1472603904834535426

    result2 = await client.operations_sessions(limit=2, offset=2)
    assert len(result2) == 1
    assert result2[0].id == 1472603904834535427


@pytest.mark.asyncio
async def test_operations_sessions_filter_by_map(client: AppClient):
    result = await client.operations_sessions(map="shock_therapy")

    assert result.total == 1
    assert len(result) == 1
    assert result[0].map == "shock_therapy"
    assert result[0].id == 1472603904834535426


@pytest.mark.asyncio
async def test_operations_sessions_filter_by_username(client: AppClient):
    result = await client.operations_sessions(username="Player1")

    assert result.total == 2
    assert len(result) == 2

    session_ids = {s.id for s in result}
    assert 1472603904834535425 in session_ids
    assert 1472603904834535427 in session_ids
    assert 1472603904834535426 not in session_ids


@pytest.mark.asyncio
async def test_operations_sessions_sorting(client: AppClient):
    result_asc = await client.operations_sessions(sort="date_finish", order="ascending")
    assert result_asc[0].end_time.year == 2025
    assert result_asc[0].end_time.month == 11
    assert result_asc[0].end_time.day == 12

    result_desc = await client.operations_sessions(sort="date_finish", order="descending")
    assert result_desc[0].end_time.day == 14


@pytest.mark.asyncio
async def test_operations_sessions_before_datetime(client: AppClient):
    before_date = datetime(2025, 11, 13, 0, 0, 0)
    result = await client.operations_sessions(before=before_date)

    assert result.total == 1
    assert result[0].id == 1472603904834535425
    assert result[0].end_time.day == 12


@pytest.mark.asyncio
async def test_operations_sessions_after_datetime(client: AppClient):
    after_date = datetime(2025, 11, 13, 0, 0, 0)
    result = await client.operations_sessions(after=after_date)

    assert result.total == 2
    session_ids = {s.id for s in result}
    assert 1472603904834535426 in session_ids
    assert 1472603904834535427 in session_ids
    assert 1472603904834535425 not in session_ids


@pytest.mark.asyncio
async def test_operations_sessions_after_string(client: AppClient):
    result = await client.operations_sessions(after="2025-11-13T10:00:00Z")

    assert result.total == 2
    session_ids = {s.id for s in result}
    assert 1472603904834535426 in session_ids
    assert 1472603904834535427 in session_ids
    assert 1472603904834535425 not in session_ids


@pytest.mark.asyncio
async def test_operations_sessions_before_string(client: AppClient):
    result = await client.operations_sessions(before="2025-11-13T10:15:00Z")

    assert result.total == 1
    assert result[0].id == 1472603904834535425


@pytest.mark.asyncio
async def test_operations_sessions_before_after_combined(client: AppClient):
    before_date = datetime(2025, 11, 14, 0, 0, 0)
    after_date = datetime(2025, 11, 12, 12, 0, 0)

    result = await client.operations_sessions(before=before_date, after=after_date)

    assert result.total == 1
    assert result[0].id == 1472603904834535426
    assert result[0].end_time.day == 13


@pytest.mark.asyncio
async def test_auction_lots(client: AppClient):
    auction = client.auction("9nd0")
    result = await auction.lots()

    assert result.total == 3
    assert len(result) == 3

    lot = result[0]
    assert lot.item_id == "9nd0"
    assert lot.amount == 1
    assert lot.start_price == 34999
    assert lot.current_price is None
    assert lot.buyout_price == 0
    assert lot.start_time.year == 2026
    assert lot.start_time.month == 2
    assert lot.start_time.day == 1
    assert lot.additional == {}


@pytest.mark.asyncio
async def test_auction_lots_pagination(client: AppClient):
    auction = client.auction("9nd0")

    result1 = await auction.lots(limit=2)
    assert len(result1) == 2
    assert result1[0].start_price == 34999
    assert result1[1].start_price == 1

    result2 = await auction.lots(limit=2, offset=2)
    assert len(result2) == 1
    assert result2[0].start_price == 29999


@pytest.mark.asyncio
async def test_auction_price_history(client: AppClient):
    auction = client.auction("9nd0")
    result = await auction.price_history()

    assert result.total == 5
    assert len(result) == 5

    price = result[0]
    assert price.amount == 1
    assert price.price == 1500
    assert price.time.year == 2026
    assert price.time.month == 2
    assert price.additional == {}


@pytest.mark.asyncio
async def test_auction_price_history_pagination(client: AppClient):
    auction = client.auction("9nd0")

    result1 = await auction.price_history(limit=3)
    assert len(result1) == 3
    assert result1[0].price == 1500
    assert result1[1].price == 6900

    result2 = await auction.price_history(limit=2, offset=3)
    assert len(result2) == 2
    assert result2[0].price == 3000
    assert result2[0].amount == 2
    assert result2[1].price == 1000


@pytest.mark.asyncio
async def test_clans(client: AppClient):
    result = await client.clans()

    assert result.total == 3
    assert len(result) == 3

    clan = result[0]
    assert clan.name == "ClanOne"
    assert clan.tag == "ONE"
    assert clan.level == 0
    assert clan.level_points == 100000
    assert clan.alliance == Alliance.MERC
    assert clan.leader == "LeaderOne"
    assert clan.member_count == 5
    assert clan.registration_time.year == 2025


@pytest.mark.asyncio
async def test_clans_pagination(client: AppClient):
    result1 = await client.clans(limit=2)
    assert len(result1) == 2
    assert result1[0].name == "ClanOne"
    assert result1[1].name == "ClanTwo"

    result2 = await client.clans(limit=2, offset=2)
    assert len(result2) == 1
    assert result2[0].name == "ClanThree"


@pytest.mark.asyncio
async def test_clan_info(client: AppClient):
    result = await client.clan(clan_id="11111111-1111-1111-1111-111111111111").info()

    assert result.name == "TestClan"
    assert result.tag == "TEST"
    assert result.level == 2
    assert result.level_points == 6500000
    assert result.alliance == Alliance.MERC
    assert result.leader == "TestLeader"
    assert result.member_count == 35
    assert result.registration_time.year == 2024


@pytest.mark.asyncio
async def test_friends(userclient: UserClient):
    friends = await userclient.friends("testplayer")

    assert len(friends) == 3
    assert friends[0] == "Friend1"
    assert friends[1] == "Friend2"
    assert friends[2] == "Friend3"


@pytest.mark.asyncio
async def test_characters(userclient: UserClient):
    characters = await userclient.characters()

    assert len(characters) == 4

    char1 = characters[0]
    assert char1.info.name == "CharacterOne"
    assert char1.info.uuid == "11111111-1111-1111-1111-111111111111"
    assert char1.info.creation_time.year == 2023
    assert char1.info.creation_time.month == 1
    assert char1.clan is None

    char3 = characters[2]
    assert char3.info.name == "CharacterThree"
    assert char3.info.uuid == "33333333-3333-3333-3333-333333333333"
    assert char3.clan is None

    char5 = characters[3]
    assert char5.info.name == "CharacterFour"
    assert char5.info.uuid == "44444444-4444-4444-4444-444444444444"


@pytest.mark.asyncio
async def test_clan_members(userclient: UserClient):
    members = await userclient.clan("test-clan").members()

    assert len(members) == 4

    member1 = members[0]
    assert member1.name == "MemberOne"
    assert member1.rank == ClanRank.LEADER
    assert member1.join_time.year == 2024
    assert member1.join_time.month == 1

    member2 = members[1]
    assert member2.name == "MemberTwo"
    assert member2.rank == ClanRank.OFFICER

    member3 = members[2]
    assert member3.name == "MemberThree"
    assert member3.rank == ClanRank.SOLDIER

    member4 = members[3]
    assert member4.name == "MemberFour"
    assert member4.rank == ClanRank.RECRUIT
