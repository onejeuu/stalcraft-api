from os import PathLike
from pathlib import Path
from typing import Any, NamedTuple, Optional, TypeVar

from sqlalchemy.exc import DatabaseError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import MetaData, col, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default
from scapi.enums import EntityType

from . import metadata, models, parsing
from .enums import MetaKey, StatusNormalize, SyncMode
from .github import GitHubClient
from .repository import DatabaseRepository


M = TypeVar("M", bound=models.BaseModel)


class CommitsPair(NamedTuple):
    local: str
    remote: str


class StalcraftDatabase:
    def __init__(
        self,
        path: PathLike[str] = Default.DATABASE_PATH,
        mode: SyncMode = SyncMode.DEFAULT,
        normalize: bool = True,
        github: Optional[GitHubClient] = None,
    ):
        self._path = Path(path)
        self._mode = mode
        self._normalize = normalize

        self._github = github or GitHubClient()
        self._repo = DatabaseRepository(self._github)

        self._engine = create_async_engine(self.url)
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self._path}"

    async def commits(
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
        commits = await self.commits()
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
        normalize: Optional[bool] = None,
        force: bool = False,
    ) -> bool:
        await self._validate_database()

        mode = mode or self._mode
        normalize = normalize if normalize is not None else self._normalize

        # Get local and remote commit hashes
        commits = await self.commits()

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

    async def get(
        self,
        model: type[M] = models.Translation,
        **filters: Any,
    ) -> tuple[M, ...]:
        await self._validate_database()

        if not await self.is_ready():
            await self.sync(normalize=True)

        async with self._sessionmaker.begin() as session:
            conds: list[Any] = []

            for field, value in filters.items():
                if value is not None:
                    column = col(getattr(model, field))
                    condition = column.ilike(f"%{parsing.query(value)}%") if field == "search" else column == value
                    conds.append(condition)

            query = select(model).where(*conds)
            return tuple((await session.exec(query)).all())

    async def get_id(
        self,
        query: str,
        language: Optional[str] = None,
        entity_type: Optional[str] = EntityType.LISTING,
    ) -> str | None:
        results = await self.get(
            model=models.Translation,
            search=query,
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
