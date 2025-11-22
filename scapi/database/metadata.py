from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import schema
from .enums import MetaKey, MetaStatus, SyncMode
from .models import Metadata


VERSION = "1"
SCHEMA = schema.checksum()


Updates = list[tuple[str, str]]


async def get(session: AsyncSession, key: MetaKey) -> str:
    query = select(Metadata.value).where(Metadata.key == key)
    value = (await session.exec(query)).first()
    return value or ""


async def set(session: AsyncSession, key: MetaKey, value: str):
    await session.merge(Metadata(key=key, value=value))


async def bulkset(session: AsyncSession, updates: Updates):
    for key, value in updates:
        await session.merge(Metadata(key=key, value=value))


async def incompatible(session: AsyncSession) -> bool:
    version = await get(session, MetaKey._VERSION)
    schema = await get(session, MetaKey._SCHEMA)
    return bool(version and version != VERSION) or bool(schema and schema != SCHEMA)


async def set_synced(session: AsyncSession, mode: SyncMode, commit: str):
    now = datetime.now().isoformat()
    updates: Updates = [
        (MetaKey.CURRENT_COMMIT, commit),
        (MetaKey.LAST_SYNC_MODE, mode),
        (MetaKey.LAST_CHECK, now),
        (MetaKey.LAST_UPDATE, now),
        (MetaKey.LAST_STATUS, MetaStatus.SYNCED),
    ]
    await bulkset(session, updates)


async def set_unchanged(session: AsyncSession, mode: SyncMode):
    now = datetime.now().isoformat()
    updates: Updates = [
        (MetaKey.LAST_SYNC_MODE, mode),
        (MetaKey.LAST_CHECK, now),
        (MetaKey.LAST_STATUS, MetaStatus.UNCHANGED),
    ]
    await bulkset(session, updates)


async def set_normalized(session: AsyncSession):
    now = datetime.now().isoformat()
    updates: Updates = [
        (MetaKey.LAST_NORMALIZE, now),
        (MetaKey.LAST_STATUS, MetaStatus.NORMALIZED),
    ]
    await bulkset(session, updates)


async def set_versions(session: AsyncSession):
    updates: Updates = [
        (MetaKey._VERSION, VERSION),
        (MetaKey._SCHEMA, SCHEMA),
    ]
    await bulkset(session, updates)
