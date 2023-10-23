from stalcraft.exceptions import ItemIdError
from stalcraft import AppClient, LocalItem, WebItem, ItemFolder


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"


client = AppClient(token=TOKEN)


print()
print("By item id")
item_id = "5r5g"
print(client.auction(item_id).lots(limit=1))


print()
print("Find item id by local file")

item_id = LocalItem("Snowflake")

print(client.auction(item_id).lots(limit=1))


print()
print("(Not reliable)")
print("Find item id by listing.json in stalcraft-database github repository")

item_id = WebItem("Snowflake", folder=ItemFolder.GLOBAL)

print(client.auction(item_id).lots(limit=1))


print()
print("Exception handling")
try:
    item_id = LocalItem("42")
    print(client.auction(item_id).lots(limit=1))

except ItemIdError as e:
    print("ItemIdError:", e)
