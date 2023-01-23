# stalcraft-api unofficial python library

📄 **Official API documentation:** https://eapi.stalcraft.net

ℹ️ **Before you can use the API, you must register your application and receive approval**

ℹ️ **For testing Demo API is available**

[`more about applications`](https://eapi.stalcraft.net/registration.html)


<br>

# Setup

```console
pip install stalcraft-api --upgrade
```


<br>

# Quick Start

```python
from stalcraft import AppClient, BaseUrl

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN, BaseUrl.PRODUCTION)
```

<br>

# Usage

## AppClient Examples

```python
from stalcraft import AppClient, Region, Sort, Order

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN)

print()
print("List of regions")
print(client.regions())

print()
print("List of clans with offset 1 and limit 2")
print(client.clans(offset=1, limit=2))

print()
print("Information about emission on NA server")
print(client.emission(Region.NA))

print()
print("List of lots for item with id 'y1q9'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction("y1q9").lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESCENDING))

print()
print("List of price history for item with id 'y1q9'")
print(client.auction("y1q9").price_history())

print()
print("Information about clan with id '647d6c53-b3d7-4d30-8d08-de874eb1d845'")
print(client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845").info())
```


<br>

## UserClient Examples

```python
from stalcraft import UserClient, Region

TOKEN = "YOUR_TOKEN"

client = UserClient(TOKEN)

# + all methods from AppClient

print()
print("List of characters on EU server")
print(client.characters(Region.EU))

print()
print("List of friends character 'Test-1'")
print(client.friends("Test-1"))

print()
print("Members in clan with id '647d6c53-b3d7-4d30-8d08-de874eb1d845'")
print(client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845").members())
```


<br>

## Find Item ID by name

```python
from stalcraft import AppClient, LocalItem, WebItem, ItemIdException

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN)

print()
print("Search by local file")
print(client.auction(LocalItem("Snowflake").item_id).lots())

print()
print("(Not reliable)")
print("Search by stalcraft-database github repository")
print(client.auction(WebItem("Snowflake").item_id).lots())

print()
print("If an item with that name does not exist")
try:
    print(LocalItem("test123").item_id)
except ItemIdException as e:
    print("Error:", e)
```
