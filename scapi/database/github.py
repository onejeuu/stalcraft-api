from typing import Any, Optional

from scapi.consts import ItemsRepository
from scapi.http.api import APIClient
from scapi.http.auth.token import TokenHTTPClient
from scapi.http.client import Headers


HEADERS = {
    "Connection": "keep-alive",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept": "*/*",
}


class GitHubClient(APIClient):
    def __init__(
        self,
        token: Optional[str] = None,
        owner: str = ItemsRepository.OWNER,
        repository: str = ItemsRepository.REPOSITORY,
        branch: str = ItemsRepository.BRANCH,
        timeout: int = ItemsRepository.TIMEOUT,
        headers: Optional[Headers] = None,
    ):
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
        data = await self._http.GET(f"https://api.github.com/repos/{self._slug}/commits/{self._branch}")
        return data["sha"]

    async def diff(self, base: str, head: str) -> dict[str, Any]:
        return await self._http.GET(f"https://api.github.com/repos/{self._slug}/compare/{base}...{head}")

    async def contents(self, path: str = ""):
        return await self._http.GET(f"https://api.github.com/repos/{self._slug}/contents/{path}")

    async def rawfile(self, path: str, ref: Optional[str] = None, output: Optional[str] = None):
        ref = ref or self._branch
        return await self._http.GET(
            f"https://raw.githubusercontent.com/{self._slug}/{ref}/{path}",
            filename=output,
            raw=True,
        )

    async def archive(self, output: Optional[str] = None):
        return await self._http.GET(
            f"https://github.com/{self._slug}/archive/refs/heads/{self._branch}.zip",
            filename=output,
        )

    def __str__(self):
        return f"<{self.__class__.__name__} token={bool(self._token)} repo='{self._slug}' branch='{self._branch}' http={self._http}>"
