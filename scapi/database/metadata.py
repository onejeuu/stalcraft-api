from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import schema
from .enums import MetaKey, MetaStatus, SyncMode
from .models import Metadata


VERSION = "1"
SCHEMA = schema.checksum()


Updates = list[tuple[str, str]]


class DatabaseMetadata:
    def __init__(
        self,
        sessionmaker: async_sessionmaker[AsyncSession],
    ):
        self._sessionmaker = sessionmaker

    async def get(self, key: MetaKey) -> str:
        async with self._sessionmaker.begin() as session:
            query = select(Metadata.value).where(Metadata.key == key)
            value = (await session.exec(query)).first()
        return value or ""

    async def set(self, key: MetaKey, value: str):
        async with self._sessionmaker.begin() as session:
            await session.merge(Metadata(key=key, value=value))

    async def set_bulk(self, session: AsyncSession, updates: Updates):
        for key, value in updates:
            await session.merge(Metadata(key=key, value=value))

    async def needs_reset(self) -> bool:
        version = await self.get(MetaKey._VERSION)
        schema = await self.get(MetaKey._SCHEMA)
        return bool(version and version != VERSION) or bool(schema and schema != SCHEMA)

    async def set_synced(self, session: AsyncSession, mode: SyncMode, commit: str):
        now = datetime.now().isoformat()
        updates: Updates = [
            (MetaKey.CURRENT_COMMIT, commit),
            (MetaKey.LAST_SYNC_MODE, mode),
            (MetaKey.LAST_CHECK, now),
            (MetaKey.LAST_UPDATE, now),
            (MetaKey.LAST_STATUS, MetaStatus.SYNCED),
        ]
        await self.set_bulk(session, updates)

    async def set_unchanged(self, session: AsyncSession, mode: SyncMode):
        now = datetime.now().isoformat()
        updates: Updates = [
            (MetaKey.LAST_SYNC_MODE, mode),
            (MetaKey.LAST_CHECK, now),
            (MetaKey.LAST_STATUS, MetaStatus.UNCHANGED),
        ]
        await self.set_bulk(session, updates)

    async def set_versions(self, session: AsyncSession):
        updates: Updates = [
            (MetaKey._VERSION, VERSION),
            (MetaKey._SCHEMA, SCHEMA),
        ]
        await self.set_bulk(session, updates)
