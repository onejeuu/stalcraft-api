from . import BaseApi, Region, Sort, Order


class Auction(BaseApi):
    def __init__(self, token, api_link, item_id: str = "", region: Region = Region.RU):
        super().__init__(token, api_link)

        if not item_id:
            raise ValueError(f"Invalid item '{item_id}'")

        else:
            self.item_id = item_id

        self.region = region

    def history(self, offset: int=0, limit: int=20):
        """
        offset: Количество цен в списке, которое нужно пропустить, по умолчанию 0 \n
        limit: Количество возвращаемых цен, начиная со смещения, минимум 0, максимум 100, по умолчанию 20 \n
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/history?offset={offset}&limit={limit}"
        return self._request(method)

    def lots(self, offset: int=0, limit: int=20, sort: Sort = Sort.TIME_CREATED, order: Order = Order.ASCENDING):
        """
        offset: Количество цен в списке, которое нужно пропустить, по умолчанию 0 \n
        limit: Количество возвращаемых цен, начиная со смещения, минимум 0, максимум 100, по умолчанию 20 \n
        sort: Параметр для сортировки по одному из: TIME_CREATED, TIME_LEFT, CURRENT_PRICE, BUYOUT_PRICE \n
        order: Параметр для порядка: ASCENDING (возрастания), DESCENDING (убывания) \n
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/lots?offset={offset}&limit={limit}&sort={sort.value}&order={order.value}"
        return self._request(method)

    def __repr__(self):
        return f"<Clan> item='{self.item_id}' region='{self.region}'"
