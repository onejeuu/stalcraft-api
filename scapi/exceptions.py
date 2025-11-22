from dataclasses import dataclass

from yarl import URL


class ScApiException(Exception):
    pass


class ClientError(ScApiException):
    pass


class CredentialsError(ClientError):
    pass


@dataclass
class RequestError(ClientError):
    error: dict[str, str]
    status_code: int
    method: str
    url: URL

    def __str__(self):
        return f"HTTP {self.status_code}: {self.error}"
