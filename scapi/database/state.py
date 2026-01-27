import time
from datetime import datetime
from typing import Optional


class CommitState:
    """Commit state tracker with TTL cache for remote commit."""

    _time_offset = time.time() - time.monotonic()

    def __init__(self, ttl: float, local: str = ""):
        self.local = local

        self._ttl = ttl
        self._remote = ""
        self._until = 0.0

    @property
    def remote(self) -> str:
        """Cached remote commit hash."""
        if time.monotonic() > self._until:
            return ""
        return self._remote

    @remote.setter
    def remote(self, value: str) -> None:
        self._remote = value
        self._until = time.monotonic() + self._ttl if self._ttl > 0 else float("inf")

    @property
    def uptodate(self) -> bool:
        """Local and remote commit equality."""
        if not self.local or time.monotonic() > self._until:
            return False

        return self.local == self._remote

    @property
    def until(self) -> Optional[datetime]:
        """Expiration time as datetime or None if infinite."""
        if self._until == float("inf") or self._until == 0.0:
            return None
        timestamp = self._until + self._time_offset
        return datetime.fromtimestamp(timestamp)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(local='{self.local}', remote='{self.remote}', uptodate={self.uptodate}, until={self.until})"
