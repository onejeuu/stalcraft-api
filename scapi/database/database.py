from os import PathLike
from pathlib import Path
from typing import Any, NamedTuple, Optional, Sequence

from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import MetaData, col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default
from scapi.enums import EntityType

from . import metadata, models, parsing
from .enums import MetaKey, StatusNormalize, SyncMode
from .github import GitHubClient
from .models import Translation
from .repository import DatabaseRepository


class CommitsPair(NamedTuple):
    local: str
    remote: str


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
        self._repo = DatabaseRepository(self._github)

        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self._path}")
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

    async def get_commits(
        self,
    ) -> CommitsPair:
        await self._validate_database()

        async with self._sessionmaker.begin() as session:
            local = await metadata.get(session, MetaKey.CURRENT_COMMIT)

        remote = await self._github.latest_commit()
        return CommitsPair(local, remote)

    async def is_uptodate(
        self,
    ) -> bool:
        commits = await self.get_commits()
        return commits.local == commits.remote

    async def is_ready(
        self,
    ) -> bool:
        await self._validate_database()

        async with self._sessionmaker.begin() as session:
            status = await metadata.get(session, MetaKey.NORMALIZE_STATUS)

        return status == StatusNormalize.READY

    async def sync(
        self,
        mode: Optional[SyncMode] = None,
        normalize: bool = True,
        force: bool = False,
    ) -> bool:
        await self._validate_database()

        mode = mode or self._mode

        # Get local and remote commit hashes
        commits = await self.get_commits()

        # Stop sync if database is up to date
        if commits.local == commits.remote and not force:
            async with self._sessionmaker.begin() as session:
                await metadata.set_unchanged(session, mode)
            return False

        # Create clean database
        if not commits.local or force:
            async with self._sessionmaker.begin() as session:
                await self._rebuild_database(session, mode)
                await metadata.set_synced(session, mode, commits.remote)

            if normalize:
                await self.normalize()
            return True

        # Update database by diff
        async with self._sessionmaker.begin() as session:
            await self._repo.sync_diff(session, mode, commits.local, commits.remote)
            await metadata.set_synced(session, mode, commits.remote)

        if normalize:
            await self.normalize()
        return True

    async def normalize(
        self,
    ) -> None:
        await self._validate_database()

        async with self._sessionmaker.begin() as session:
            await self._clear_tables(session, models.BaseParsed.metadata)

            rows = await parsing.normalize(session)
            session.add_all(rows.values())

            await metadata.set_normalized(session)

    async def search(
        self,
        text: str,
        language: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> Sequence[Translation]:
        await self._validate_database()

        model = models.Translation

        if not await self.is_ready():
            await self.sync(normalize=True)

        async with self._sessionmaker.begin() as session:
            query = parsing.query(text)
            conds: list[Any] = [col(model.search).ilike(f"%{query}%")]

            if language is not None:
                conds.append(col(model.language) == language.lower())

            if entity_type is not None:
                conds.append(col(model.entity_type) == entity_type.lower())

            query = select(model).where(*conds)
            return (await session.exec(query)).all()

    async def get_id(
        self,
        text: str,
        language: Optional[str] = None,
        entity_type: Optional[str] = EntityType.LISTING,
    ) -> str | None:
        results = await self.search(
            text=text,
            language=language,
            entity_type=entity_type,
        )

        return results[0].entity_id if results else None

    async def _rebuild_database(self, session: AsyncSession, mode: SyncMode):
        # Drop repository table
        await session.exec(delete(models.FileBlob))

        # Download repository by mode
        match mode:
            case SyncMode.ARCHIVE:
                await self._repo.sync_archive(session)

            case SyncMode.INDEX | _:
                await self._repo.sync_index(session)

    async def _validate_database(self):
        try:
            async with self._sessionmaker.begin() as session:
                incompatible = await metadata.incompatible(session)

            if incompatible:
                await self._drop_tables()
                await self._create_database()

        except DatabaseError:
            await self._create_database()

    async def _create_database(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)

        await self._create_tables()

        async with self._sessionmaker.begin() as session:
            await metadata.set_versions(session)

    async def _create_tables(self):
        async with self._engine.begin() as conn:
            for base in models.BASES:
                await conn.run_sync(base.metadata.create_all)

    async def _drop_tables(self):
        async with self._engine.begin() as conn:
            for base in models.BASES:
                await conn.run_sync(base.metadata.drop_all)

    async def _clear_tables(self, session: AsyncSession, metadata: MetaData):
        for table in reversed(metadata.sorted_tables):
            await session.exec(table.delete())

    def __str__(self):
        return f"<{self.__class__.__name__} mode='{self._mode}' path='{self._path.as_posix()}'>"
