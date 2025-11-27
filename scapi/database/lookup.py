import json
from typing import Optional

from cachetools import TTLCache

from scapi.enums import Realm

from .enums import IndexFile
from .github import GitHubClient
from .index import SearchIndex


class CommitsState:
    def __init__(self, ttl: float):
        self.local = ""
        self._cache = TTLCache(maxsize=128, ttl=ttl)

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
        commit_ttl: float = 300,
        cache_ttl: float = 86400,
    ):
        self._github = github or GitHubClient()
        self._realm = realm

        self._commits = CommitsState(ttl=commit_ttl)
        self._cache = TTLCache(maxsize=256, ttl=cache_ttl)

    async def get(
        self,
        query: str,
        realm: Optional[str | Realm] = None,
        filename: str | IndexFile = IndexFile.LISTING,
    ):
        realm = realm or self._realm
        path = f"{realm}/{filename}"

        index = await self._download(path)
        return index.search(query)

    async def _download(self, path: str) -> SearchIndex:
        index = SearchIndex()

        if not self._commits.remote:
            self._commits.remote = await self._github.latest_commit()

        if self._commits.uptodate and path in self._cache:
            return self._cache[path]

        if not self._commits.uptodate:
            self._commits.local = self._commits.remote
            self._cache.clear()

        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        index.build(path, data)

        self._cache[path] = index
        return index
