import asyncio
import os
import tempfile
import zipfile
from typing import Optional

from sqlmodel import col, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from .enums import SyncMode
from .github import GitHubClient
from .models import FileBlob


TEMP_PREFIX = "scapi-db-"

BUFFER_FLUSH_LIMIT = 1024 * 1024 * 4  # 4 MB

SEMAPHORE_DEFAULT = 5
SEMAPHORE_TOKEN = 20


class DatabaseRepository:
    def __init__(
        self,
        github: GitHubClient,
    ):
        self._github = github

        value = SEMAPHORE_TOKEN if self._github.has_token else SEMAPHORE_DEFAULT
        self._semaphore = asyncio.Semaphore(value)

    async def sync_index(self, session: AsyncSession) -> None:
        # Get repository root files
        contents = await self._github.contents()

        # Get subdirs
        subdirs = [item for item in contents if item["type"] == "dir"]
        subcontents = await asyncio.gather(*[self._github.contents(dir["path"]) for dir in subdirs])

        # Create targets files list
        files = [item for item in contents if item["type"] == "file"]
        files.extend(item for sublist in subcontents for item in sublist if item["type"] == "file")

        # Download files
        blobs = await asyncio.gather(*[self._download_file(item["path"]) for item in files])
        session.add_all(blobs)

    async def sync_diff(self, session: AsyncSession, mode: SyncMode, base: str, head: str) -> None:
        # Get repository diff from base commit to head commit
        diff = await self._github.diff(base=base, head=head)

        # Create targets files list
        to_download: list[str] = [file["filename"] for file in diff["files"] if file["status"] in ("added", "modified")]
        to_delete: list[str] = [file["filename"] for file in diff["files"] if file["status"] in ("deleted",)]

        # Filter targets files by mode
        if mode == SyncMode.INDEX:
            to_download = [filename for filename in to_download if filename.count("/") <= 1]
            to_delete = [filename for filename in to_delete if filename.count("/") <= 1]

        # Download files
        blobs = await asyncio.gather(*[self._download_file(filename) for filename in to_download])

        # Merge new and changed files
        for blob in blobs:
            await session.merge(blob)

        # Delete outdated files
        for filename in to_delete:
            await session.exec(delete(FileBlob).where(col(FileBlob.path) == filename))

    async def sync_archive(self, session: AsyncSession) -> None:
        # Create temp archive file
        with tempfile.NamedTemporaryFile(prefix=TEMP_PREFIX, suffix=".zip", delete=False) as tmp:
            filename = tmp.name

        try:
            # Download archive to temp file
            await self._github.archive(output=filename)

            # Open downloaded repository archive
            with zipfile.ZipFile(filename) as zip:
                root = zip.namelist()[0]  # Root directory name
                counter = 0

                for name in zip.namelist():
                    if not name.endswith("/"):  # Filter dirs
                        path = name.replace(root, "", 1)  # Relative path
                        content = zip.read(name)
                        size = len(content)
                        session.add(FileBlob(path=path, content=content, size=size))

                        # Flush every limit to not overflow memory
                        counter += size
                        if counter >= BUFFER_FLUSH_LIMIT:
                            counter = 0
                            await session.flush()

        # Always delete temp archive file
        finally:
            os.unlink(filename)

    async def _download_file(self, path: str, ref: Optional[str] = None) -> FileBlob:
        async with self._semaphore:
            content = await self._github.rawfile(path=path, ref=ref)
            return FileBlob(path=path, content=content, size=len(content))

    def __str__(self):
        return f"<{self.__class__.__name__} github={self._github} semaphore={self._semaphore._value}>"
