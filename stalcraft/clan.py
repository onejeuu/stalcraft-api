from . import BaseApi, Region


class Clan(BaseApi):
    def __init__(self, token, api_link, clan_id: str = "", region: Region = Region.RU):
        super().__init__(token, api_link)

        if not clan_id:
            raise ValueError(f"Invalid clan_id: {clan_id}")

        else:
            self.clan_id = clan_id

        self.region = region

    def info(self):
        """
        Возвращает информацию о клане
        """

        method = f"{self.region.value}/clan/{self.clan_id}/info"
        return self._request(method)

    def members(self):
        """
        Возвращает участников клана
        """

        method = f"{self.region.value}/clan/{self.clan_id}/members"
        return self._request(method)

    def __repr__(self):
        return f"<Clan> clan_id='{self.clan_id}' region='{self.region}'"
