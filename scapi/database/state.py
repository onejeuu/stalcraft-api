from cachetools import TTLCache


class CommitsState:
    """Commit state tracker with TTL cache for remote commit."""

    def __init__(self, ttl: float):
        self.local = ""
        self._cache = TTLCache(maxsize=1, ttl=ttl)

    @property
    def remote(self) -> str:
        """Cached remote commit hash."""
        return self._cache.get("remote", "")

    @remote.setter
    def remote(self, value: str) -> None:
        self._cache["remote"] = value

    @property
    def uptodate(self) -> bool:
        """Local and remote commit equality."""
        return bool(self.local and self.local == self.remote)

    def __repr__(self):
        return f"{self.__class__.__name__}(local='{self.local}', remote='{self.remote}', uptodate={self.uptodate})"
