from . import BaseApi, ApiLink, Auction, Clan, Region


class Client(BaseApi):
    def __init__(self, token: str, api_link: str | ApiLink = ""):
        """
        token: Токен для авторизации
        api_link: Опциональный параметр, ссылка на API
        warn_demo: Предупреждать о том что используется demo версия API
        """

        super().__init__(token, api_link)

    def regions(self):
        """
        Возвращает список регионов
        """

        method = "regions"
        return self._request(method)

    def characters(self, region: Region = Region.RU):
        """
        Возвращает список персонажей

        region: Регион сталкрафта, по умолчанию Region.RU
        """

        method = f"{region.value}/characters"
        return self._request(method)

    def clans(self, offset: int=0, limit: int=20, region: Region = Region.RU):
        """
        Возвращает список кланов

        offset: Количество цен в списке, которое нужно пропустить, по умолчанию 0 \n
        limit: Количество возвращаемых цен, начиная со смещения, минимум 0, максимум 100, по умолчанию 20 \n
        region: Регион сталкрафта, по умолчанию Region.RU
        """

        self._offset_and_limit(offset, limit)

        method = f"{region.value}/clans?offset={offset}&limit={limit}"
        return self._request(method)

    def emission(self, region: Region = Region.RU):
        """
        Возвращает информацию о выбросе

        region: Регион сталкрафта, по умолчанию Region.RU
        """

        method = f"{region.value}/emission"
        return self._request(method)

    def friends(self, character: str = "", region: Region = Region.RU):
        """
        Возвращает список друзей

        character: Имя персонажа
        region: Регион сталкрафта, по умолчанию Region.RU
        """

        if not character:
            raise ValueError(f"Invalid character '{character}'")

        method = f"{region.value}/friends/{character}"
        return self._request(method)

    def auction(self, item_id: str = "", region: Region = Region.RU):
        """
        Интерфейс для работы с аукционом

        item: ID предмета, к примеру "y1q9"
        region: Регион сталкрафта, по умолчанию Region.RU
        """

        return Auction(self.token, self.api_link, item_id, region)

    def clan(self, clan_id: str = "", region: Region = Region.RU):
        """
        Интерфейс для работы с кланами

        clan_id: ID клана, к примеру "647d6c53-b3d7-4d30-8d08-de874eb1d845"
        region: Регион сталкрафта, по умолчанию Region.RU
        """

        return Clan(self.token, self.api_link, clan_id, region)

    def __repr__(self):
        return f"<Client> api_link='{self.api_link}' token='{self.token_part}'"
