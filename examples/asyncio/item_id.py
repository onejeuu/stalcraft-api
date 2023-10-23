import asyncio

from stalcraft import ItemFolder, LocalItem, WebItem
from stalcraft.asyncio import AsyncAppClient
from stalcraft.exceptions import ItemIdError


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"


async def main():
    client = AsyncAppClient(token=TOKEN)

    print()
    print("By item id")
    item_id = "5r5g"
    print(await client.auction(item_id).lots(limit=1))

    print()
    print("Find item id by local file")
    item_id = LocalItem("Snowflake")
    print(await client.auction(item_id).lots(limit=1))

    print()
    print("(Not reliable)")
    print("Find item id by listing.json in stalcraft-database github repository")
    item_id = WebItem("Snowflake", folder=ItemFolder.GLOBAL)
    print(await client.auction(item_id).lots(limit=1))

    print()
    print("Exception handling")
    try:
        item_id = LocalItem("42")

    except ItemIdError as e:
        print("ItemIdError:", e)


asyncio.run(main())
