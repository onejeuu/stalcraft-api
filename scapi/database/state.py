import time


class CommitState:
    """Commit state tracker with TTL cache for remote commit."""

    def __init__(self, ttl: float, local: str = ""):
        self.local = local

        self._ttl = ttl
        self._remote = ""
        self._until = 0.0

    @property
    def remote(self) -> str:
        """Cached remote commit hash."""
        if time.time() > self._until:
            return ""
        return self._remote

    @remote.setter
    def remote(self, value: str) -> None:
        self._remote = value
        self._until = time.time() + self._ttl if self._ttl > 0 else float("inf")

    @property
    def uptodate(self) -> bool:
        """Local and remote commit equality."""
        if not self.local or time.time() > self._until:
            return False

        return self.local == self._remote

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(local='{self.local}', remote='{self.remote}', uptodate={self.uptodate})"
