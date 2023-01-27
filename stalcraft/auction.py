from . import BaseApi, BaseUrl, Order, Region, Sort, LocalItem, WebItem
from . import schemas


class Auction(BaseApi):
    def __init__(self, token: str, base_url: BaseUrl | str, json: bool, item_id: str | LocalItem | WebItem, region: Region):
        super().__init__(token, base_url)

        self.json = json

        if isinstance(item_id, (LocalItem, WebItem)):
            item_id = item_id.item_id

        self.item_id = item_id
        self.region = region

    def price_history(self, offset=0, limit=20, additional=False):
        """
        Returns history of prices for lots which were bought from auction for the given item.
        Prices are sorted in descending order by recorded time of purchase.

        Args:
            offset: Amount of prices in list to skip, default 0
            limit: Amount of prices to return, starting from offset, minimum 0, maximum 100, default 20
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/history"
        payload = {"offset": offset, "limit": limit, "additional": additional}
        response = self._request(method, payload)

        if self.json is True:
            return response

        return [
            schemas.Price(price)
            for price in response['prices']
        ]

    def lots(self, offset=0, limit=20, sort=Sort.TIME_CREATED, order=Order.ASCENDING, additional=False):
        """
        Returns list of currently active lots on the auction for the given item.
        Lots are sorted based on given parameter.

        Args:
            offset: Amount of lots in list to skip, default 0
            limit: Amount of lots to return, starting from offset, minimum 0, maximum 100, default 20
            sort: Property to sort by, one of: TIME_CREATED, TIME_LEFT, CURRENT_PRICE, BUYOUT_PRICE
            order: Either ASCENDING or DESCENDING
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/lots"
        payload = {"offset": offset, "limit": limit, "sort": sort.value, "order": order.value, "additional": additional}
        response = self._request(method, payload)

        if self.json is True:
            return response

        return [
            schemas.Lot(lots)
            for lots in response['lots']
        ]

    def __repr__(self):
        return f"{super().__repr__()} item_id='{self.item_id}' region='{self.region}'"
