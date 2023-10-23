from stalcraft.asyncio import AsyncAppClient
from stalcraft import Region, Sort, Order
import asyncio


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

ITEM_ID = "1r756"
CLAN_ID = "647d6c53-b3d7-4d30-8d08-de874eb1d845"


async def main():
    # Method 1:
    client = AsyncAppClient(token=TOKEN)

    # Method 2:
    client = AsyncAppClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

    print()
    print("List of regions")
    print(await client.regions())

    print()
    print("List of clans with limit 2")
    print(await client.clans(limit=2))

    print()
    print("Information about emission on NA server")
    print(await client.emission(Region.NA))

    print()
    print(f"List of lots for item with id '{ITEM_ID}'")
    print("With offset 5, limit 2, sort by buyout price and order by descending")
    print(await client.auction(ITEM_ID).lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

    print()
    print(f"List of price history for item with id '{ITEM_ID}'")
    print(await client.auction(ITEM_ID).price_history())

    print()
    print(f"Information about clan with id '{CLAN_ID}'")
    print(await client.clan(CLAN_ID).info())


asyncio.run(main())
