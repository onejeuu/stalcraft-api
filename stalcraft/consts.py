from typing import NamedTuple


class BaseUrl(NamedTuple):
    DEMO = "http://dapi.stalcraft.net"
    PRODUCTION = "http://eapi.stalcraft.net"


class AuthUrl(NamedTuple):
    AUTHORIZE = "https://exbo.net/oauth/authorize"
    TOKEN = "https://exbo.net/oauth/token"
    USER = "https://exbo.net/oauth/user"


class ItemsDatabase(NamedTuple):
    GITHUB_RAW = "raw.githubusercontent.com"
    REPOS = "EXBO-Studio/stalcraft-database"
    BRANCH = "main"


class StatusCode(NamedTuple):
    OK = 200
    INVALID_PARAMETER = 400
    UNAUTHORISED = 401
    NOT_FOUND = 404
    RATE_LIMIT = 429
