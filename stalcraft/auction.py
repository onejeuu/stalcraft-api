from . import BaseApi, BaseUrl, Order, Region, Sort


class Auction(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl = "", item_id="", region=Region.RU):
        super().__init__(token, base_url)

        if not item_id:
            raise ValueError(f"Invalid item '{item_id}'")

        self.item_id = item_id
        self.region = region

    def price_history(self, offset=0, limit=20):
        """
        offset: Amount of prices in list to skip, default 0
        limit: Amount of prices to return, starting from offset, minimum 0, maximum 100, default 20
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/history?offset={offset}&limit={limit}"
        return self._request(method)

    def lots(self, offset=0, limit=20, sort=Sort.TIME_CREATED, order=Order.ASCENDING):
        """
        offset: Amount of lots in list to skip, default 0
        limit: Amount of lots to return, starting from offset, minimum 0, maximum 100, default 20
        sort: Property to sort by, one of: TIME_CREATED, TIME_LEFT, CURRENT_PRICE, BUYOUT_PRICE
        order: Either ASCENDING or DESCENDING
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/lots?offset={offset}&limit={limit}&sort={sort.value}&order={order.value}"
        return self._request(method)

    def __repr__(self):
        return f"<Clan> item='{self.item_id}' region='{self.region}'"
