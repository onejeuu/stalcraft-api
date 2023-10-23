from stalcraft.api.base import BaseApi, RequestHeaders


class SecretApi(BaseApi):
    def __init__(self, client_id: str, client_secret: str, base_url: str):
        super().__init__(base_url)

        self._client_id = client_id
        self._client_secret = client_secret

    @property
    def part_of_secret(self) -> str:
        return f"{self._client_secret[:5]}...{self._client_secret[-3:]}"

    @property
    def headers(self) -> RequestHeaders:
        return {
            "Client-Id": self._client_id,
            "Client-Secret": self._client_secret,
            "Content-Type": "application/json"
        }

    def __str__(self):
        return f"{super().__str__()} client_id='{self._client_id}' client_secret='{self.part_of_secret}'"
