from datetime import datetime

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from . import schema
from .enums import MetaKey, MetaStatus, SyncMode
from .models import Metadata


VERSION = "1"
SCHEMA = schema.checksum()


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

    async def needs_reset(self) -> bool:
        version = await self.get(MetaKey._VERSION)
        schema = await self.get(MetaKey._SCHEMA)
        return bool(version and version != VERSION) or bool(schema and schema != SCHEMA)

    async def set_synced(self, session: AsyncSession, mode: SyncMode, commit: str):
        now = datetime.now().isoformat()
        await session.merge(Metadata(key=MetaKey.CURRENT_COMMIT, value=commit))
        await session.merge(Metadata(key=MetaKey.LAST_SYNC_MODE, value=mode))
        await session.merge(Metadata(key=MetaKey.LAST_CHECK, value=now))
        await session.merge(Metadata(key=MetaKey.LAST_UPDATE, value=now))
        await session.merge(Metadata(key=MetaKey.LAST_STATUS, value=MetaStatus.SYNCED))

    async def set_unchanged(self, session: AsyncSession, mode: SyncMode):
        now = datetime.now().isoformat()
        await session.merge(Metadata(key=MetaKey.LAST_SYNC_MODE, value=mode))
        await session.merge(Metadata(key=MetaKey.LAST_CHECK, value=now))
        await session.merge(Metadata(key=MetaKey.LAST_STATUS, value=MetaStatus.UNCHANGED))

    async def set_versions(self, session: AsyncSession):
        await session.merge(Metadata(key=MetaKey._VERSION, value=VERSION))
        await session.merge(Metadata(key=MetaKey._SCHEMA, value=SCHEMA))
