import json
import time
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

from scapi.database.github import GitHubClient
from scapi.database.lookup import DatabaseLookup
from scapi.database.state import CommitState


def test_commit_state_remote_ttl():
    state = CommitState(ttl=0.1)

    assert state.remote == ""

    state.remote = "abc123"
    assert state.remote == "abc123"

    time.sleep(0.15)
    assert state.remote == ""


def test_commit_state_infinite_ttl():
    state = CommitState(ttl=0)
    state.remote = "abc123"

    time.sleep(0.1)
    assert state.remote == "abc123"


def test_commit_state_uptodate_logic():
    state = CommitState(ttl=10)
    state.remote = "abc123"
    assert not state.uptodate

    state.local = "abc123"
    assert state.uptodate

    state.remote = "def456"
    assert not state.uptodate

    state = CommitState(ttl=0.01)
    state.local = "abc123"
    state.remote = "abc123"
    time.sleep(0.02)
    assert not state.uptodate


def test_commit_state_until_property():
    state = CommitState(ttl=3600)

    assert state.until is None

    state.remote = "abc123"
    until = state.until

    assert until is not None
    assert isinstance(until, datetime)

    expected_min = datetime.now() + timedelta(seconds=3500)
    expected_max = datetime.now() + timedelta(seconds=3700)
    assert expected_min < until < expected_max


@pytest.fixture
def mock_github():
    github = Mock(spec=GitHubClient)
    github.latest_commit = AsyncMock(return_value="commit123")
    github.rawfile = AsyncMock(return_value=b"[]")
    return github


@pytest.mark.asyncio
async def test_lookup_init():
    lookup = DatabaseLookup()
    assert lookup is not None
    assert lookup._github is not None

    github = Mock()
    lookup = DatabaseLookup(github=github)
    assert lookup._github == github


@pytest.mark.asyncio
async def test_lookup_get_entity(mock_github):
    mock_data = """[
        {
            "data": "/items/attachment/other/1r1j6.json",
            "icon": "/icons/attachment/other/1r1j6.png",
            "name": {"type": "translation", "lines": {"ru": "M203", "en": "M203"}}
        }
    ]""".encode()

    mock_github.rawfile.return_value = mock_data
    lookup = DatabaseLookup(github=mock_github, sync_on_update=False)

    entity = await lookup.get_entity("1r1j6")
    assert entity is not None
    assert entity["data"] == "/items/attachment/other/1r1j6.json"
    mock_github.rawfile.assert_called_with(path="ru/listing.json")


@pytest.mark.asyncio
async def test_lookup_search(mock_github):
    mock_data = """[
        {
            "data": "/items/drink/6w5jj.json",
            "icon": "/icons/drink/6w5jj.png",
            "name": {"type": "translation", "lines": {"ru": "Брусничная водка", "en": "Lingonberry Vodka"}}
        },
        {
            "data": "/items/misc/npr6.json",
            "icon": "/icons/misc/npr6.png",
            "name": {"type": "translation", "lines": {"ru": "Цинк", "en": "Zinc"}}
        }
    ]""".encode()

    mock_github.rawfile.return_value = mock_data
    lookup = DatabaseLookup(github=mock_github, sync_on_update=False)

    results = await lookup.search("водка")
    assert len(results) >= 1
    assert results[0].id == "6w5jj"

    results = await lookup.search("zinc")
    assert len(results) >= 1
    assert results[0].id == "npr6"

    results = await lookup.search("???")
    assert len(results) == 0

    results = await lookup.search("")
    assert len(results) == 0


@pytest.mark.asyncio
async def test_lookup_sync(mock_github):
    lookup = DatabaseLookup(github=mock_github, sync_on_update=True)

    result = await lookup.sync()
    assert result is True

    result = await lookup.sync(force=False)
    assert result is False

    result = await lookup.sync(force=True)
    assert result is True


@pytest.mark.asyncio
async def test_lookup_state_property(mock_github):
    lookup = DatabaseLookup(github=mock_github)
    state = lookup.state
    assert state is not None
    assert state.local == ""


@pytest.mark.asyncio
async def test_lookup_get_all(mock_github):
    mock_data = (
        b'[{"data": "/items/attachment/other/1r1j6.json", "name": {"type": "translation", "lines": {"ru": "M203"}}}]'
    )
    mock_github.rawfile.return_value = mock_data

    lookup = DatabaseLookup(github=mock_github, sync_on_update=False)

    all_items = await lookup.get_all()
    assert isinstance(all_items, dict)
    assert len(all_items) == 1
    assert "1r1j6" in all_items


@pytest.mark.asyncio
async def test_lookup_find_one(mock_github):
    mock_data = b'[{"data": "/items/attachment/other/1r1j6.json", "name": {"type": "text", "text": "M203"}}]'
    mock_github.rawfile.return_value = mock_data

    lookup = DatabaseLookup(github=mock_github, sync_on_update=False)

    result = await lookup.find_one("M203")
    assert result is not None
    assert result.id == "1r1j6"

    result = await lookup.find_one("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_lookup_item_info(mock_github):
    item_data = {"name": "M203", "type": "attachment"}
    mock_github.rawfile.return_value = json.dumps(item_data).encode()

    lookup = DatabaseLookup(github=mock_github)

    result = await lookup.item_info("items/attachment/other/1r1j6.json")
    assert result == item_data

    result = await lookup.item_info("items/attachment/other/1r1j6.json")
    assert result == item_data

    result = await lookup.item_info("items/weapon/5ln40.json", upgrade_level=8)
    expected_path = "ru/items/weapon/_variants/5ln40/8.json"
    mock_github.rawfile.assert_called_with(path=expected_path)


@pytest.mark.asyncio
async def test_lookup_item_icon(mock_github):
    icon_data = b"\x89PNG\r\n\x1a\n"
    mock_github.rawfile.return_value = icon_data

    lookup = DatabaseLookup(github=mock_github)

    result = await lookup.item_icon("icons/items/1r1j6.png")
    assert result == icon_data

    result = await lookup.item_icon("icons/items/1r1j6.png")
    assert result == icon_data
    assert mock_github.rawfile.call_count == 1


@pytest.mark.asyncio
async def test_lookup_sync_with_all_realms(mock_github):
    mock_github.latest_commit = AsyncMock(return_value="commit123")
    mock_github.rawfile = AsyncMock(return_value=b"[]")

    lookup = DatabaseLookup(github=mock_github, sync_on_update=True)

    result = await lookup.sync(realm="*")
    assert result is True

    assert mock_github.rawfile.call_count > 0


@pytest.mark.asyncio
async def test_lookup_get_index_with_sync_on_update(mock_github):
    mock_github.latest_commit = AsyncMock(return_value="commit123")
    mock_github.rawfile = AsyncMock(return_value=b"[]")

    lookup = DatabaseLookup(github=mock_github, sync_on_update=True)

    entity = await lookup.get_entity("1r1j6")
    assert entity is None
    assert mock_github.rawfile.called
    assert mock_github.latest_commit.called
