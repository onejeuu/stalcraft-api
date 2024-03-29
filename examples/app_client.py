from stalcraft import AppClient, LocalItem, Order, Region, Sort


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

ITEM_ID = LocalItem("Viper")
CLAN_ID = "5ea2c08c-23f7-4366-98b8-40292267a03f"


# Method 1:
client = AppClient(token=TOKEN)

# Method 2:
client = AppClient(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


print()
print("List of regions")
print(client.regions())

print()
print("List of clans with limit 2")
print(client.clans(limit=2))

print()
print("Information about emission on EU server")
print(client.emission(Region.EUROPE))

print()
print(f"List of lots for item with id '{ITEM_ID}'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction(ITEM_ID).lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

print()
print(f"List of price history for item with id '{ITEM_ID}'")
print(client.auction(ITEM_ID).price_history())

print()
print(f"Information about clan with id '{CLAN_ID}'")
print(client.clan(CLAN_ID).info())
