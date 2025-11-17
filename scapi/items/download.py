import asyncio
import os
import tempfile
import zipfile
from typing import Optional

from sqlmodel import col, delete
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.enums import RepoSyncMode
from scapi.items.github import GitHubClient

from .models import FileBlob


TEMP_PREFIX = "scapi-db-"

CONCURRENT_DOWNLOAD_LIMIT = 20
BUFFER_FLUSH_LIMIT = 1024 * 1024 * 4  # 4 MB


class RepoSyncer:
    def __init__(
        self,
        github: GitHubClient,
    ):
        self._github = github
        self._semaphore = asyncio.Semaphore(CONCURRENT_DOWNLOAD_LIMIT)

    async def archive(self, session: AsyncSession):
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

    async def files(self, session: AsyncSession):
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

    async def diff(self, session: AsyncSession, mode: RepoSyncMode, base: str, head: str):
        # Get repository diff from base commit to head commit
        diff = await self._github.diff(base=base, head=head)

        # Create targets files list
        to_download: list[str] = [file["filename"] for file in diff["files"] if file["status"] in ("added", "modified")]
        to_delete: list[str] = [file["filename"] for file in diff["files"] if file["status"] in ("deleted",)]

        # Filter targets files by mode
        if mode == RepoSyncMode.DEFAULT:
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

    async def _download_file(self, path: str, ref: Optional[str] = None):
        async with self._semaphore:
            content = await self._github.rawfile(path=path, ref=ref)
            return FileBlob(path=path, content=content, size=len(content))
