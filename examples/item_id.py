from stalcraft import AppClient, LocalItem, WebItem, ItemFolder


TOKEN = "YOUR_TOKEN"


client = AppClient(token=TOKEN)


ITEM_ID = LocalItem("Snowflake")

print()
print("Search by local file")
print(client.auction(ITEM_ID).lots())


ITEM_ID = WebItem("Snowflake", folder=ItemFolder.GLOBAL)

print()
print("(Not reliable)")
print("Search by listing.json in stalcraft-database github repository")
print(client.auction(ITEM_ID).lots())
