from datetime import datetime

from . import BaseApi, BaseUrl, Order, Region, Sort
from . import schemas


class Auction(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl = "", item_id="", region=Region.RU):
        super().__init__(token, base_url)

        if not item_id:
            raise ValueError(f"Invalid item '{item_id}'")

        self.item_id = item_id
        self.region = region

    def price_history(self, offset=0, limit=20):
        """
        Returns history of prices for lots which were bought from auction for the given item.
        Prices are sorted in descending order by recorded time of purchase.

        Args:
            offset: Amount of prices in list to skip, default 0
            limit: Amount of prices to return, starting from offset, minimum 0, maximum 100, default 20
        """

        self._offset_and_limit(offset, limit)

        method = f"{self.region.value}/auction/{self.item_id}/history"
        params = {"offset": offset, "limit": limit}
        response = self._request(method, params)

        return schemas.Prices(
            total=response.get("total"),
            prices=[
                schemas.Price(
                    amount=price.get("amount"),
                    price=price.get("price"),
                    time=datetime.fromisoformat(price.get("time")),
                    additional=price.get("additional")
                )
                for price in response.get("prices")
            ]
        )

    def lots(self, offset=0, limit=20, sort=Sort.TIME_CREATED, order=Order.ASCENDING):
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
        params = {"offset": offset, "limit": limit, "sort": sort.value, "order": order.value}
        response = self._request(method, params)

        return schemas.Lots(
            total=response.get("total"),
            lots=[
                schemas.Lot(
                    item_id=lot.get("itemId"),
                    start_price=lot.get("startPrice"),
                    current_price=lot.get('currentPrice'),
                    buyout_price=lot.get("buyoutPrice"),
                    start_time=datetime.fromisoformat(lot.get("startTime")),
                    end_time=datetime.fromisoformat(lot.get("endTime")),
                    additional=lot.get("additional"),
                )
                for lot in response.get("lots")
            ]
        )

    def __repr__(self):
        return f"<Clan> item='{self.item_id}' region='{self.region}'"
