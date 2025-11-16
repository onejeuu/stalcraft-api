import asyncio
import zipfile
from datetime import datetime
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Any, Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.defaults import Default
from scapi.enums import RepoSyncMode

from . import models
from .enums import MetadataKey
from .github import GitHubClient


VERSION = "1.0"


class StalcraftDatabase:
    def __init__(
        self,
        path: PathLike[str] = Default.DATABASE_PATH,
        mode: RepoSyncMode = Default.SYNC_MODE,
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
        mode: Optional[RepoSyncMode] = None,
        force: bool = False,
    ) -> bool:
        mode = mode or self._mode
        await self._create_tables()

        # Compare commit hashes
        local_commit = await self._get_local_commit()
        remote_commit = await self._github.latest_commit()

        # Stop if up to date
        if local_commit == remote_commit and not force:
            await self._update_metadata(MetadataKey.STATUS, "up to date")
            await self._update_metadata(MetadataKey.CHEKED, datetime.now().isoformat())
            return False

        # Create database
        if not local_commit or force:
            match mode:
                case RepoSyncMode.ARCHIVE:
                    await self._download_archive()

                case RepoSyncMode.FILES | _:
                    await self._download_files()

            await self._update_metadata_completed(remote_commit)
            return True

        # Update diff
        await self._download_diff(local_commit, remote_commit)
        await self._update_metadata_completed(remote_commit)
        return True

    async def _create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(models.ScDatabaseModel.metadata.create_all)

    async def _get_local_commit(self) -> str:
        async with self._sessionmaker() as session:
            query = select(models.Metadata.value).where(models.Metadata.key == MetadataKey.COMMIT)
            local_commit = (await session.exec(query)).first()
        return local_commit or ""

    async def _update_metadata(self, key: str, value: Any):
        async with self._sessionmaker() as session:
            async with session.begin():
                await session.merge(models.Metadata(key=key, value=str(value)))

    async def _update_metadata_completed(self, commit: str):
        now = datetime.now().isoformat()
        await self._update_metadata(MetadataKey.COMMIT, commit)
        await self._update_metadata(MetadataKey.UPDATED, now)
        await self._update_metadata(MetadataKey.CHEKED, now)
        await self._update_metadata(MetadataKey.STATUS, "updated")

    async def _download_files(self):
        contents = await self._github.contents()

        # Load subdirs files
        dirs = [item for item in contents if item["type"] == "dir"]
        subcontents = await asyncio.gather(*[self._github.GET(dir["url"]) for dir in dirs])

        # Create targets list
        files = [item for item in contents if item["type"] == "file"]
        files.extend(item for sublist in subcontents for item in sublist if item["type"] == "file")

        # Download file and create blob model
        async def download_file(item: dict[str, Any]):
            data = await self._github.GET(item["download_url"])
            content = data.encode()
            return models.FileBlob(
                path=item["path"],
                content=content,
                size=len(content),
            )

        # Download files and merge to database
        async with self._sessionmaker() as session:
            async with session.begin():
                blobs = await asyncio.gather(*[download_file(item) for item in files])

                for blob in blobs:
                    await session.merge(blob)

    async def _download_archive(self):
        content = await self._github.archive()

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
