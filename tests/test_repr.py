from yarl import URL

from scapi.client.auction.shared import AuctionEndpoint
from scapi.client.clan.shared import ClanEndpoint
from scapi.client.clan.user import UserClanEndpoint
from scapi.database.github import GitHubClient
from scapi.database.index.search import SearchIndex
from scapi.database.lookup import DatabaseLookup
from scapi.database.state import CommitState
from scapi.exceptions import RequestError
from scapi.http.api import APIClient
from scapi.http.auth.creds import CredentialsHTTPClient
from scapi.http.auth.token import TokenHTTPClient
from scapi.http.client import HTTPClient
from scapi.oauth.client import OAuthClient


def test_repr():
    http_client = HTTPClient(base_url="https://test.com")
    repr(http_client)
    str(http_client)

    token_client = TokenHTTPClient(token="fake_token")
    repr(token_client)
    str(token_client)

    creds_client = CredentialsHTTPClient(client_id="id", client_secret="secret")
    repr(creds_client)
    str(creds_client)

    api_client = APIClient()
    api_client._http = http_client
    repr(api_client)
    str(api_client)

    oauth_client = OAuthClient(client_id="id", client_secret="secret")
    repr(oauth_client)
    str(oauth_client)

    auction_client = AuctionEndpoint(item_id="test_item", http=http_client)
    repr(auction_client)
    str(auction_client)

    clan_client = ClanEndpoint(clan_id="test_clan", http=http_client)
    repr(clan_client)
    str(clan_client)

    user_clan_client = UserClanEndpoint(clan_id="test_clan", http=http_client)
    repr(user_clan_client)
    str(user_clan_client)

    github_client = GitHubClient()
    repr(github_client)
    str(github_client)

    search_index = SearchIndex()
    repr(search_index)
    str(search_index)

    lookup = DatabaseLookup()
    repr(lookup)
    str(lookup)

    commit_state = CommitState(ttl=300)
    repr(commit_state)
    str(commit_state)

    request_error = RequestError(data={"error": "test"}, status=404, method="GET", url=URL("https://test.com"))
    repr(request_error)
    str(request_error)
    request_error.message
