import asyncio
import json
from typing import Optional

from cachetools import TTLCache

from scapi.enums import Realm

from .enums import IndexFile
from .github import GitHubClient
from .index import Lookup, SearchIndex, Translations


SYNC_FILES: list[str] = [f"{realm}/{file}" for realm in Realm for file in IndexFile]


class CommitsState:
    def __init__(self, ttl: float):
        self.local = ""
        self._cache = TTLCache(maxsize=1, ttl=ttl)

    @property
    def remote(self) -> str:
        return self._cache.get("remote", "")

    @remote.setter
    def remote(self, value: str) -> None:
        self._cache["remote"] = value

    @property
    def uptodate(self) -> bool:
        return bool(self.local and self.local == self.remote)

    def __repr__(self):
        return f"{self.__class__.__name__}(local='{self.local}', remote='{self.remote}', uptodate={self.uptodate})"


class DatabaseLookup:
    def __init__(
        self,
        github: Optional[GitHubClient] = None,
        realm: str | Realm = Realm.RU,
        threshold: float = 0.1,
        commit_ttl: float = 300,
        cache_ttl: float = 86400,
    ):
        self._github = github or GitHubClient()
        self._realm = realm
        self._threshold = threshold

        self._commits = CommitsState(ttl=commit_ttl)

        # TODO: single cache for every IndexFile
        self._cache = TTLCache(maxsize=32, ttl=cache_ttl)

    async def get(
        self,
        entity_id: str,
        realm: Optional[str | Realm] = None,
        filename: str | IndexFile = IndexFile.LISTING,
    ) -> Optional[Translations]:
        realm = realm or self._realm
        path = f"{realm}/{filename}"

        index = await self._index(path)
        return index.get(entity_id)

    async def search(
        self,
        query: str,
        filename: str | IndexFile = IndexFile.LISTING,
        realm: Optional[str | Realm] = None,
        threshold: Optional[float] = None,
    ) -> list[Lookup]:
        realm = realm or self._realm
        path = f"{realm}/{filename}"

        threshold = threshold if threshold is not None else self._threshold

        index = await self._index(path)
        return index.search(query, threshold)

    async def sync(
        self,
        force: bool = False,
    ) -> bool:
        await self._validate_remote_commit()

        if self._commits.uptodate and not force:
            return False

        self._update_commit()

        await asyncio.gather(*[self._download(file) for file in SYNC_FILES])
        return True

    async def _index(self, path: str):
        await self._validate_remote_commit()

        if self._commits.uptodate and path in self._cache:
            return self._cache[path]

        self._update_commit()

        return await self._download(path)

    async def _download(self, path: str) -> SearchIndex:
        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        index = SearchIndex()
        index.build(path, data)

        self._cache[path] = index
        return index

    async def _validate_remote_commit(self) -> None:
        if not self._commits.remote:
            self._commits.remote = await self._github.latest_commit()

    def _update_commit(self) -> None:
        if not self._commits.uptodate:
            self._commits.local = self._commits.remote
            self._cache.clear()
