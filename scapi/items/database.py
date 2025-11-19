from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import MetaData, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default

from . import models, parsing
from .enums import MetadataKey, SyncMode
from .github import GitHubClient
from .models import Metadata
from .repository import Repository


VERSION = "1.0"




class StalcraftDatabase:
    def __init__(
        self,
        path: PathLike[str] = Default.DATABASE_PATH,
        mode: SyncMode = SyncMode.DEFAULT,
        github: Optional[GitHubClient] = None,
    ):
        self._path = Path(path)
        self._mode = mode

        self._github = github or GitHubClient()
        self._repo = Repository(self._github)

        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self._path}")
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

    async def sync(
        self,
        mode: Optional[SyncMode] = None,
        force: bool = False,
    ) -> bool:
        mode = mode or self._mode
        await self._create_tables()

        # Get local and remote commit hashes
        local_commit = await self._get_local_commit()
        remote_commit = await self._github.latest_commit()

        # Stop sync if database is up to date
        if local_commit == remote_commit and not force:
            async with self._sessionmaker.begin() as session:
                await self._set_metadata_uptodate(session, mode)
            return False

        # Create clear database
        if not local_commit or force:
            async with self._sessionmaker.begin() as session:
                await self._rebuild_database(session, mode)
                await self._set_metadata_completed(session, mode, remote_commit)
            return True

        # Update database by diff
        async with self._sessionmaker.begin() as session:
            await self._repo.sync_diff(session, mode, local_commit, remote_commit)
            await self._set_metadata_completed(session, mode, remote_commit)
        return True

    async def normalize(self):
        async with self._sessionmaker.begin() as session:
            await self._drop_tables(session, models.ScDatabaseParsed.metadata)

            rows = await parsing.normalize(session)
            session.add_all(rows.values())

    async def _create_tables(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)

        async with self._engine.begin() as conn:
            await conn.run_sync(models.ScDatabaseModel.metadata.create_all)
            await conn.run_sync(models.ScDatabaseParsed.metadata.create_all)

    async def _drop_tables(self, session: AsyncSession, metadata: MetaData):
        for table in reversed(metadata.sorted_tables):
            await session.exec(table.delete())

    async def _rebuild_database(self, session: AsyncSession, mode: SyncMode):
        # Drop tables
        await self._drop_tables(session, models.ScDatabaseModel.metadata)

        # Download repository by mode
        match mode:
            case SyncMode.ARCHIVE:
                await self._repo.sync_archive(session)

            case SyncMode.INDEX | _:
                await self._repo.sync_index(session)

    async def _get_local_commit(self) -> str:
        async with self._sessionmaker() as session:
            query = select(Metadata.value).where(Metadata.key == MetadataKey.COMMIT)
            local_commit = (await session.exec(query)).first()
        return local_commit or ""

    async def _set_metadata_completed(self, session: AsyncSession, mode: SyncMode, commit: str):
        now = datetime.now().isoformat()
        await session.merge(Metadata(key=MetadataKey.MODE, value=mode))
        await session.merge(Metadata(key=MetadataKey.COMMIT, value=commit))
        await session.merge(Metadata(key=MetadataKey.CHEKED, value=now))
        await session.merge(Metadata(key=MetadataKey.UPDATED, value=now))
        await session.merge(Metadata(key=MetadataKey.STATUS, value="updated"))

    async def _set_metadata_uptodate(self, session: AsyncSession, mode: SyncMode):
        now = datetime.now().isoformat()
        await session.merge(Metadata(key=MetadataKey.MODE, value=mode))
        await session.merge(Metadata(key=MetadataKey.CHEKED, value=now))
        await session.merge(Metadata(key=MetadataKey.STATUS, value="up to date"))
