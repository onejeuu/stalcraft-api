from stalcraft import AppClient, Region, Sort, Order


TOKEN = "YOUR_TOKEN"

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"


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
print("Information about emission on NA server")
print(client.emission(Region.NA))

print()
print("List of lots for item with id '1r756'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction("1r756").lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

print()
print("List of price history for item with id '1r756'")
print(client.auction("1r756").price_history())

print()
print("Information about clan with id '562968e7-4282-4ac6-900f-f7f1581495e8'")
print(client.clan("562968e7-4282-4ac6-900f-f7f1581495e8").info())
