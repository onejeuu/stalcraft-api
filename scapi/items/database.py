import asyncio
import os
import tempfile
import zipfile
from datetime import datetime
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

        # Get local and remote commit hashes
        local_commit = await self._get_local_commit()
        remote_commit = await self._github.latest_commit()

        # Stop if database is up to date
        if local_commit == remote_commit and not force:
            await self._set_metadata(MetadataKey.STATUS, "up to date")
            await self._set_metadata(MetadataKey.CHEKED, datetime.now().isoformat())
            return False

        # Create clear database
        if not local_commit or force:
            await self._rebuild_database(mode)
            await self._set_metadata_completed(remote_commit)
            return True

        # Update database by diff
        await self._update_diff(local_commit, remote_commit)
        await self._set_metadata_completed(remote_commit)
        return True

    async def _create_tables(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(models.meta.create_all)

    async def _rebuild_database(self, mode: RepoSyncMode):
        async with self._sessionmaker() as session:
            async with session.begin():
                for table in reversed(models.meta.sorted_tables):
                    await session.exec(table.delete())

                match mode:
                    case RepoSyncMode.ARCHIVE:
                        await self._download_archive(session)

                    case RepoSyncMode.FILES | _:
                        await self._download_files(session)

    async def _get_local_commit(self) -> str:
        async with self._sessionmaker() as session:
            query = select(models.Metadata.value).where(models.Metadata.key == MetadataKey.COMMIT)
            local_commit = (await session.exec(query)).first()
        return local_commit or ""

    async def _set_metadata(self, key: str, value: Any):
        async with self._sessionmaker() as session:
            async with session.begin():
                await session.merge(models.Metadata(key=key, value=str(value)))

    async def _set_metadata_completed(self, commit: str):
        now = datetime.now().isoformat()
        await self._set_metadata(MetadataKey.COMMIT, commit)
        await self._set_metadata(MetadataKey.UPDATED, now)
        await self._set_metadata(MetadataKey.CHEKED, now)
        await self._set_metadata(MetadataKey.STATUS, "updated")

    async def _download_files(self, session: AsyncSession):
        # Get root files
        contents = await self._github.contents()

        # Get subdirs files
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

        # Download files and add to database
        blobs = await asyncio.gather(*[download_file(item) for item in files])
        session.add_all(blobs)

    async def _download_archive(self, session: AsyncSession):
        # Create temp archive file
        with tempfile.NamedTemporaryFile(delete=False, prefix="scapi-db-", suffix=".zip") as tmp:
            filename = tmp.name

        try:
            # Download archive to temp
            await self._github.archive(output=filename)

            # Open downloaded repository archive
            with zipfile.ZipFile(filename) as zip:
                root = zip.namelist()[0]  # Root directory name

                # Add all files to database session
                for name in zip.namelist():
                    if name.endswith("/"):
                        continue

                    # Get relative path and file content
                    path = name.replace(root, "", 1)
                    content = zip.read(name)

                    # Add file blob to session
                    session.add(models.FileBlob(path=path, content=content, size=len(content)))

        finally:
            os.unlink(filename)

    async def _update_diff(self, base: str, head: str):
        # TODO: update me! asyncio download!
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
