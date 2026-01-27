import asyncio
import json
from pathlib import Path
from typing import Any, Optional

from cachetools import TTLCache

from scapi.config import Config
from scapi.enums import IndexFile, Realm

from .github import GitHubClient
from .index.search import Entity, Lookup, SearchIndex
from .state import CommitState


INDEX_FILES: list[str] = [f"{realm}/{file}" for realm in Realm for file in IndexFile]


class DatabaseLookup:
    """Entity lookup and search interface for game database."""

    def __init__(
        self,
        github: Optional[GitHubClient] = None,
        realm: Optional[Realm | str] = None,
        threshold: float = 0.1,
        stale_time: float = 900,
        asset_ttl: float = 86400,
        asset_capacity: int = 128,
        sync_on_update: bool = True,
    ):
        """
        Initialize database lookup.

        Args:
            github (optional): GitHub client instance.
            realm (optional): Default game version realm. Defaults to `ru`.
            threshold (optional): Default search similarity threshold (`0.0`-`1.0`). Defaults to `0.1`.
            stale_time (optional): Remote commit cache TTL seconds (`0` to disable). Defaults to `900s` (`15 minute`).
            asset_ttl (optional): Files cache TTL seconds. Defaults to `86400s` (`1 day`).
            asset_capacity (optional): Files cache size limit. Defaults to `128`.
            sync_on_update (optional): Sync all indexes on commit update, otherwise lazy load. Defaults to `True`.
        """

        self._github = github or GitHubClient()
        self._realm = realm
        self._threshold = threshold
        self._stale_time = stale_time
        self._asset_ttl = asset_ttl
        self._asset_cap = asset_capacity
        self._sync_on_update = sync_on_update

        self._state = CommitState(ttl=self._stale_time)
        self._assets = TTLCache(maxsize=self._asset_cap, ttl=self._asset_ttl)
        self._indexes: dict[str, SearchIndex] = {}

    @property
    def state(self) -> CommitState:
        return self._state

    async def get_entity(
        self,
        entity_id: str,
        filename: IndexFile | str = IndexFile.LISTING,
        realm: Optional[Realm | str] = None,
    ) -> Optional[Entity]:
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

        index = await self._get_index(path)
        return index.get(entity_id)

    async def search(
        self,
        query: str,
        filename: IndexFile | str = IndexFile.LISTING,
        realm: Optional[Realm | str] = None,
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

        index = await self._get_index(path)
        return index.search(query, threshold)

    async def find_one(
        self,
        query: str,
        filename: IndexFile | str = IndexFile.LISTING,
        realm: Optional[Realm | str] = None,
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
        realm: Optional[Realm | str] = None,
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

        if path in self._assets:
            return self._assets[path]

        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        self._assets[path] = data
        return data

    async def item_icon(
        self,
        path: str,
        realm: Optional[Realm | str] = None,
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

        if path in self._assets:
            return self._assets[path]

        data: bytes = await self._github.rawfile(path=path)

        self._assets[path] = data
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

        if not force and self._state.uptodate:
            return False

        self._update_commit()

        await asyncio.gather(*[self._download_index(path) for path in INDEX_FILES])
        return True

    async def _get_index(self, path: str) -> SearchIndex:
        """Retrieve or build search index for path with commit validation."""

        await self._validate_remote_commit()

        if self._state.uptodate and path in self._indexes:
            return self._indexes[path]

        if self._sync_on_update:
            await self.sync(force=True)
            return self._indexes[path]

        self._update_commit()
        return await self._download_index(path)

    async def _download_index(self, path: str) -> SearchIndex:
        """Download and build search index from json file."""

        content: bytes = await self._github.rawfile(path=path)
        data = json.loads(content)

        index = SearchIndex()
        index.build(path, data)

        self._indexes[path] = index
        return index

    async def _validate_remote_commit(self) -> None:
        """Fetch latest remote commit if not cached."""

        if not self._state.remote:
            self._state.remote = await self._github.latest_commit()

    def _update_commit(self) -> None:
        """Update local commit and clear cache on change."""

        if not self._state.uptodate:
            self._state.local = self._state.remote
            self._indexes.clear()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(realm='{self._realm}', threshold={self._threshold}, uptodate={self._state.uptodate}, sync_on_update={self._sync_on_update}, "
            f"stale_time={self._stale_time}, asset_ttl={self._asset_ttl})"
        )
