from typing import Any, Optional

from scapi.consts import DatabaseRepository as Repo
from scapi.http.api import APIClient
from scapi.http.auth.token import TokenHTTPClient
from scapi.http.client import Headers


TIMEOUT = 300

# TODO: update headers
HEADERS = {
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}


class GitHubClient(APIClient):
    """API Client for GitHub repository operations."""

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        owner: str = Repo.OWNER,
        repository: str = Repo.REPOSITORY,
        branch: str = Repo.BRANCH,
        timeout: int = TIMEOUT,
        headers: Optional[Headers] = None,
    ):
        """
        Initialize GitHub client.

        Args:
            token (optional): GitHub API token for authenticated requests.
            owner (optional): Repository owner. Defaults to `EXBO-Studio`.
            repository (optional): Repository name. Defaults to `stalcraft-database`.
            branch (optional): Repository branch. Defaults to `main`.
            timeout (optional): Request timeout in seconds. Defaults to `300s`.
            headers (optional): Custom HTTP headers.
        """

        self._token = token
        self._owner = owner
        self._repository = repository
        self._branch = branch
        self._slug = f"{owner}/{repository}"

        self._http = TokenHTTPClient(token=token, timeout=timeout, headers=headers or HEADERS.copy())

    @property
    def has_token(self) -> bool:
        return bool(self._token)

    async def latest_commit(self) -> str:
        """
        Get latest commit hash.

        Returns:
            Commit SHA hash.
        """

        data = await self._http.GET(f"https://api.github.com/repos/{self._slug}/commits/{self._branch}")
        return data["sha"]

    async def diff(self, base: str, head: str) -> dict[str, Any]:
        """
        Compare commits or branches.

        Args:
            base: Base commit or branch.
            head: Head commit or branch.

        Returns:
            Comparison data.
        """

        return await self._http.GET(f"https://api.github.com/repos/{self._slug}/compare/{base}...{head}")

    async def contents(self, path: str = ""):
        """
        List repository contents at specified path.

        Args:
            path (optional): Directory path. Defaults to repository root.

        Returns:
            Repository contents listing.
        """

        return await self._http.GET(f"https://api.github.com/repos/{self._slug}/contents/{path}")

    async def rawfile(self, path: str, ref: Optional[str] = None, output: Optional[str] = None):
        """
        Download raw file from repository.

        Args:
            path: File path within repository.
            ref (optional): Git reference. Defaults to configured branch.
            output (optional): Local filename for file streaming.

        Returns:
            File content bytes.
        """

        ref = ref or self._branch
        return await self._http.GET(
            f"https://raw.githubusercontent.com/{self._slug}/{ref}/{path}",
            filename=output,
            raw=True,
        )

    async def archive(self, output: Optional[str] = None):
        """
        Download repository as ZIP archive.

        Args:
            output (optional): Local filename for file streaming.

        Returns:
            Archive content bytes.
        """

        return await self._http.GET(
            f"https://github.com/{self._slug}/archive/refs/heads/{self._branch}.zip",
            filename=output,
        )

    def __repr__(self):
        return f"{self.__class__.__name__}(token={self.has_token}, repo='{self._slug}', branch='{self._branch}', http={self._http})"
