import zipfile
from io import BytesIO
from os import PathLike
from pathlib import Path
from typing import Optional

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel, delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.consts import ItemsRepository
from scapi.defaults import Default
from scapi.enums import DatabaseMode
from scapi.http.client import HTTPClient

from .models import FileBlob, Metadata


VERSION = "1.0"

HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}


class StalcraftDatabase:
    def __init__(
        self,
        path: PathLike[str] = Default.DATABASE_PATH,
        mode: DatabaseMode = Default.DATABASE_MODE,
        owner: str = ItemsRepository.OWNER,
        repository: str = ItemsRepository.REPOSITORY,
        branch: str = ItemsRepository.BRANCH,
        download_timeout: int = 300,
    ):
        self._path = Path(path)
        self._mode = mode

        self._owner = owner
        self._repository = repository
        self._branch = branch
        self._slug = f"{owner}/{repository}"

        self._timeout = download_timeout

        self._http = HTTPClient()
        self._engine = create_async_engine(f"sqlite+aiosqlite:///{self._path}")
        self._sessionmaker = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)

        self._path.parent.mkdir(parents=True, exist_ok=True)

    async def sync(
        self,
        mode: Optional[DatabaseMode] = None,
        force: bool = False,
    ) -> bool:
        mode = mode or self._mode
        await self._create()

        # Compare commit hashes
        local_commit = await self._get_local_commit()
        remote_commit = await self._get_remote_commit()

        # Stop if up to date
        if local_commit == remote_commit and not force:
            return False

        # Create database
        if not self._path.exists() or force:
            match mode:
                case DatabaseMode.FULL:
                    await self._download_archive()

                case _:
                    await self._download_files()

            await self._update_metadata(remote_commit)
            return True

        # Impossible state
        if local_commit:
            return False

        # Update diff
        await self._download_diff(local_commit, remote_commit)
        await self._update_metadata(remote_commit)
        return True

    async def _create(self):
        async with self._engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        async with self._sessionmaker() as session:
            async with session.begin():
                await session.merge(Metadata(key="version", value=VERSION))

    async def _get_local_commit(self) -> str:
        async with self._sessionmaker() as session:
            query = select(Metadata.value).where(Metadata.key == "last_commit")
            local_commit = (await session.exec(query)).first()

        return local_commit or ""

    async def _update_metadata(self, last_commit: str):
        async with self._sessionmaker() as session:
            metadata = Metadata(key="last_commit", value=last_commit)
            await session.merge(metadata)
            await session.commit()

    async def _download_files(self):
        root = await self._http.GET(f"https://api.github.com/repos/{self._slug}/contents/")

        async with self._sessionmaker() as session:
            async with session.begin():
                for item in root:
                    if item["type"] == "dir":
                        files = await self._http.GET(item["url"])
                        for file in files:
                            if file["type"] == "file":
                                content = await self._http.GET(file["download_url"])
                                content = content.encode()
                                await session.merge(
                                    FileBlob(
                                        path=file["path"],
                                        content=content,
                                        size=len(content),
                                    )
                                )

    async def _download_archive(self):
        url = f"https://github.com/{self._slug}/archive/refs/heads/{self._branch}.zip"
        timeout = aiohttp.ClientTimeout(self._timeout)

        # Download repository archive
        async with aiohttp.ClientSession(timeout=timeout, headers=HEADERS) as session:
            async with session.get(url=url) as response:
                content = await response.read()

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

                        session.add(FileBlob(path=rel, content=content, size=len(content)))

    async def _download_diff(self, base: str, head: str):
        diff = await self._get_diff(base, head)

        async with self._sessionmaker() as session:
            async with session.begin():
                for file in diff.get("files", []):
                    filename = file.get("filename")
                    status = file.get("status")
                    url = file.get("raw_url")

                    if url and filename and status in ("added", "modified"):
                        content = await self._http.GET(url)
                        await session.merge(
                            FileBlob(
                                path=filename,
                                content=content,
                                size=len(content),
                            )
                        )

                    if filename and status == "deleted":
                        await session.exec(delete(FileBlob).where(FileBlob.path == filename))

    # TODO: http clients?
    async def _get_remote_commit(self) -> str:
        data = await self._http.GET(f"https://api.github.com/repos/{self._slug}/commits/{self._branch}")
        return data["sha"]

    async def _get_diff(self, base: str, head: str):
        data = await self._http.GET(f"https://api.github.com/repos/{self._slug}/compare/{base}...{head}")
        return data.get("files", [])
