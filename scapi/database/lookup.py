import asyncio
import json
from pathlib import Path
from typing import Any, Optional

from cachetools import TTLCache

from scapi.config import Config
from scapi.enums import Realm

from .enums import IndexFile
from .github import GitHubClient
from .index import Data, Lookup, SearchIndex
from .state import CommitsState


SYNC_FILES: list[str] = [f"{realm}/{file}" for realm in Realm for file in IndexFile]


class DatabaseLookup:
    """Entity lookup and search interface for game database."""

    def __init__(
        self,
        github: Optional[GitHubClient] = None,
        realm: Optional[str | Realm] = None,
        threshold: float = 0.1,
        commit_ttl: float = 300,
        cache_ttl: float = 86400,
        cache_size: int = 128,
    ):
        """
        Initialize database lookup.

        Args:
            github (optional): GitHub client instance.
            realm (optional): Default game version realm. Defaults to `ru`.
            threshold (optional): Default search similarity threshold (`0.0`-`1.0`). Defaults to `0.1`.
            commit_ttl (optional): Remote commit cache TTL seconds. Defaults to `300s` (`5 minute`).
            cache_ttl (optional): Cache TTL seconds. Defaults to `86400s` (`1 day`).
            cache_size (optional): Cache size limit. Defaults to `128`.
        """

        self._github = github or GitHubClient()
        self._realm = realm
        self._threshold = threshold
        self._commit_ttl = commit_ttl
        self._cache_ttl = cache_ttl
        self._cache_size = cache_size

        self._commits = CommitsState(ttl=commit_ttl)
        self._cache = TTLCache(maxsize=cache_size, ttl=cache_ttl)

    @property
    def state(self) -> CommitsState:
        """Current commit synchronization state."""
        return self._commits

    async def get(
        self,
        entity_id: str,
        filename: str | IndexFile = IndexFile.LISTING,
        realm: Optional[str | Realm] = None,
    ) -> Optional[Data]:
        """
        Retrieve entity data by ID.

        Args:
            entity_id: Entity identifier.
            filename (optional): Index file name. Defaults to `listing.json`.
            realm (optional): Game version realm. Defaults to `ru`.

        Returns:
            Entity json data or None.
        """

        realm = (realm or self._realm or Config.REALM).lower()
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
        """
        Search entities by text query.

        Args:
            query: Search text.
            filename (optional): Index file name. Defaults to `listing.json`.
            realm (optional): Game version realm. Defaults to `ru`.
            threshold (optional): Override similarity threshold (`0.0`-`1.0`). Defaults to `0.1`.

        Returns:
            List of search results sorted by relevance.
        """

        realm = (realm or self._realm or Config.REALM).lower()
        path = f"{realm}/{filename}"

        threshold = threshold if threshold is not None else self._threshold

        index = await self._index(path)
        return index.search(query, threshold)

    async def find(
        self,
        query: str,
        filename: str | IndexFile = IndexFile.LISTING,
        realm: Optional[str | Realm] = None,
        threshold: Optional[float] = None,
    ) -> Optional[Lookup]:
        """
        Find single best match for text query.

        Args:
            query: Search text.
            filename (optional): Index file name. Defaults to `listing.json`.
            realm (optional): Game version realm. Defaults to `ru`.
            threshold (optional): Override similarity threshold (`0.0`-`1.0`). Defaults to `0.1`.

        Returns:
            Best match result or None.
        """

        results = await self.search(
            query=query,
            filename=filename,
            realm=realm,
            threshold=threshold,
        )

        return results[0] if results else None

    async def item_info(
        self,
        path: str,
        upgrade_level: int = 0,
        realm: Optional[str | Realm] = None,
    ) -> Any:
        """
        Retrieve item information.

        Args:
            path: Item data path.
            upgrade_level (optional): Item upgrade level (`0`-`15`). Defaults to `0`.
            realm (optional): Game version realm. Defaults to `ru`.

        Returns:
            Item json data.
        """

        realm = (realm or self._realm or Config.REALM).lower()
        path = f"{realm}/{path}"
        lvl = max(0, min(15, upgrade_level))

        if lvl > 0:
            tmp = Path(path)
            path = (tmp.parent / f"_variants/{tmp.stem}/{lvl}.json").as_posix()

        if path in self._cache:
            return self._cache[path]

        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        self._cache[path] = data
        return data

    async def item_icon(
        self,
        path: str,
        realm: Optional[str | Realm] = None,
    ) -> bytes:
        """
        Download item icon image.

        Args:
            path: Icon file path.
            realm (optional): Game version realm. Defaults to `ru`.

        Returns:
            Icon binary data.
        """

        realm = (realm or self._realm or Config.REALM).lower()
        path = f"{realm}/{path}"

        if path in self._cache:
            return self._cache[path]

        data: bytes = await self._github.rawfile(path=path)

        self._cache[path] = data
        return data

    async def sync(
        self,
        force: bool = False,
    ) -> bool:
        """
        Synchronize local database with remote.

        Args:
            force (optional): Force sync regardless of commit state.

        Returns:
            True if sync was performed, False if already up-to-date.
        """

        await self._validate_remote_commit()

        if self._commits.uptodate and not force:
            return False

        self._update_commit()

        await asyncio.gather(*[self._download(file) for file in SYNC_FILES])
        return True

    async def _index(self, path: str) -> SearchIndex:
        """Retrieve or build search index for path with commit validation."""

        await self._validate_remote_commit()

        if self._commits.uptodate and path in self._cache:
            return self._cache[path]

        self._update_commit()

        return await self._download(path)

    async def _download(self, path: str) -> SearchIndex:
        """Download and build search index from json file."""

        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        index = SearchIndex()
        index.build(path, data)

        self._cache[path] = index
        return index

    async def _validate_remote_commit(self) -> None:
        """Fetch latest remote commit if not cached."""

        if not self._commits.remote:
            self._commits.remote = await self._github.latest_commit()

    def _update_commit(self) -> None:
        """Update local commit and clear cache on change."""

        if not self._commits.uptodate:
            self._commits.local = self._commits.remote
            self._cache.clear()

    def __repr__(self):
        return f"{self.__class__.__name__}(realm='{self._realm}', threshold={self._threshold}, uptodate={self._commits.uptodate}, commit_ttl={self._commit_ttl}, cache_ttl={self._cache_ttl})"
