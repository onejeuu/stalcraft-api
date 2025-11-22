from os import PathLike
from pathlib import Path
from typing import Any, NamedTuple, Optional, Sequence

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import MetaData, col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default
from scapi.enums import EntityType

from . import models, parsing
from .enums import MetaKey, SyncMode
from .github import GitHubClient
from .metadata import DatabaseMetadata
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

        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self._path}")
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

        self._github = github or GitHubClient()
        self._repo = DatabaseRepository(self._github)
        self._meta = DatabaseMetadata(self._sessionmaker)

    async def get_commits_pair(
        self,
    ) -> CommitsPair:
        local = await self._meta.get(MetaKey.CURRENT_COMMIT)
        remote = await self._github.latest_commit()
        return CommitsPair(local, remote)

    async def is_uptodate(
        self,
    ) -> bool:
        commits = await self.get_commits_pair()
        return commits.local == commits.remote

    async def sync(
        self,
        mode: Optional[SyncMode] = None,
        normalize: bool = True,
        force: bool = False,
    ) -> bool:
        mode = mode or self._mode
        await self._validate_database()

        # Get local and remote commit hashes
        commits = await self.get_commits_pair()

        # Stop sync if database is up to date
        if commits.local == commits.remote and not force:
            async with self._sessionmaker.begin() as session:
                await self._meta.set_unchanged(session, mode)
            return False

        # Create clear database
        if not commits.local or force:
            async with self._sessionmaker.begin() as session:
                await self._rebuild_database(session, mode)
                await self._meta.set_synced(session, mode, commits.remote)

            if normalize:
                await self.normalize()
            return True

        # Update database by diff
        async with self._sessionmaker.begin() as session:
            await self._repo.sync_diff(session, mode, commits.local, commits.remote)
            await self._meta.set_synced(session, mode, commits.remote)

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

            await self._meta.set_normalized(session)

    async def search(
        self,
        text: str,
        language: Optional[str] = None,
        entity_type: Optional[str] = None,
    ) -> Sequence[Translation]:
        async with self._sessionmaker.begin() as session:
            conds: list[Any] = [col(models.Translation.text).ilike(f"%{text}%")]

            if language is not None:
                conds.append(col(models.Translation.language) == language.lower())

            if entity_type is not None:
                conds.append(col(models.Translation.entity_type) == entity_type.lower())

            query = select(models.Translation).where(*conds)
            return (await session.exec(query)).all()

    async def listing(
        self,
        text: str,
        language: Optional[str] = None,
    ) -> str | None:
        results = await self.search(
            text=text,
            language=language,
            entity_type=EntityType.LISTING,
        )

        if results and len(results) > 0:
            return results[0].entity_id

    async def _rebuild_database(self, session: AsyncSession, mode: SyncMode):
        # Drop tables
        await self._clear_tables(session, models.BaseModel.metadata)

        # Download repository by mode
        match mode:
            case SyncMode.ARCHIVE:
                await self._repo.sync_archive(session)

            case SyncMode.INDEX | _:
                await self._repo.sync_index(session)

    async def _validate_database(self):
        await self._create_tables()

        if await self._meta.needs_reset():
            await self._drop_tables()
            await self._create_tables()

        async with self._sessionmaker.begin() as session:
            await self._meta.set_versions(session)

    async def _create_tables(self):
        self._path.parent.mkdir(parents=True, exist_ok=True)

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
