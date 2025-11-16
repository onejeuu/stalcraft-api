import zipfile
from datetime import datetime
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Optional, TypeAlias

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default
from scapi.enums import DatabaseMode

from . import models
from .enums import MetadataKey
from .github import GitHubClient


VERSION = "1.0"

JSON: TypeAlias = dict[str, Any]


class StalcraftDatabase:
    def __init__(
        self,
        path: PathLike[str] = Default.DATABASE_PATH,
        mode: DatabaseMode = Default.DATABASE_MODE,
        github: Optional[GitHubClient] = None,
    ):
        self._path = Path(path)
        self._mode = mode
        self._github = github or GitHubClient()

        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self._path}")
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def sync(
        self,
        mode: Optional[DatabaseMode] = None,
        force: bool = False,
    ) -> bool:
        mode = mode or self._mode
        await self._create_tables()

        # Compare commit hashes
        local_commit = await self._get_local_commit()
        remote_commit = await self._github.latest_commit()

        # Stop if up to date
        if local_commit == remote_commit and not force:
            await self._update_metadata(MetadataKey.LAST_CHEKED, datetime.now().isoformat())
            return False

        # Create database
        if not local_commit or force:
            match mode:
                case DatabaseMode.FULL:
                    await self._download_archive()

                case _:
                    await self._download_files()

            await self._update_metadata_success(remote_commit)
            return True

        # Update diff
        await self._download_diff(local_commit, remote_commit)
        await self._update_metadata_success(remote_commit)
        return True

    async def _create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(models.ScDatabaseModel.metadata.create_all)

    async def _get_local_commit(self) -> str:
        async with self._sessionmaker() as session:
            query = select(models.Metadata.value).where(models.Metadata.key == MetadataKey.LAST_COMMIT)
            local_commit = (await session.exec(query)).first()
        return local_commit or ""

    async def _update_metadata(self, key: str, value: str):
        async with self._sessionmaker() as session:
            async with session.begin():
                await session.merge(models.Metadata(key=key, value=value))

    async def _update_metadata_success(self, last_commit: str):
        dt = datetime.now().isoformat()
        await self._update_metadata(MetadataKey.LAST_COMMIT, last_commit)
        await self._update_metadata(MetadataKey.LAST_UPDATED, dt)
        await self._update_metadata(MetadataKey.LAST_CHEKED, dt)

    async def _download_files(self):
        root = await self._github.contents()

        async with self._sessionmaker() as session:
            async with session.begin():
                for item in root:
                    if item["type"] == "dir":
                        files = await self._github.GET(item["url"])
                        for file in files:
                            if file["type"] == "file":
                                content = await self._github.GET(file["download_url"])
                                content = content.encode()
                                await session.merge(
                                    models.FileBlob(
                                        path=file["path"],
                                        content=content,
                                        size=len(content),
                                    )
                                )

    async def _download_archive(self):
        content = await self._github.archive()

        # TODO: delete old files
        # Add files to database
        with zipfile.ZipFile(BytesIO(content)) as zip:
            async with self._sessionmaker() as session:
                async with session.begin():
                    root = zip.namelist()[0]

                    for name in zip.namelist():
                        if name.endswith("/"):
                            continue

                        rel = name.replace(root, "", 1)
                        content = zip.read(name)

                        session.add(models.FileBlob(path=rel, content=content, size=len(content)))

    async def _download_diff(self, base: str, head: str):
        diff = await self._github.diff(base=base, head=head)

        async with self._sessionmaker() as session:
            async with session.begin():
                for file in diff.get("files", []):
                    filename = file.get("filename")
                    status = file.get("status")
                    url = file.get("raw_url")

                    if url and filename and status in ("added", "modified"):
                        content = await self._github.GET(url)
                        await session.merge(
                            models.FileBlob(
                                path=filename,
                                content=content,
                                size=len(content),
                            )
                        )

                    if filename and status == "deleted":
                        await session.exec(delete(models.FileBlob).where(models.FileBlob.path == filename))
