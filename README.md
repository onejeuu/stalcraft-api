# stalcraft-api unofficial python library

[![PyPi Package Version](https://img.shields.io/pypi/v/stalcraft-api.svg?style=flat-square)](https://pypi.org/project/stalcraft-api)
[![Supported python versions](https://img.shields.io/pypi/pyversions/stalcraft-api.svg?style=flat-square)](https://pypi.org/project/stalcraft-api)
[![MIT License](https://img.shields.io/pypi/l/aiogram.svg?style=flat-square)](https://opensource.org/licenses/MIT)


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

# Usage Examples

<details>
<summary>AppClient</summary>

```python
from stalcraft import AppClient, Region, Sort, Order

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN)

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
print("List of lots for item with id 'y1q9'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction("y1q9").lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

print()
print("List of price history for item with id 'y1q9'")
print(client.auction("y1q9").price_history())

print()
print("Information about clan with id '647d6c53-b3d7-4d30-8d08-de874eb1d845'")
print(client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845").info())
```

</details>


<br>

<details>
<summary>UserClient</summary>

```python
from stalcraft import UserClient, Region

TOKEN = "YOUR_TOKEN"

client = UserClient(TOKEN)

# + all methods from AppClient

print("List of characters created on EU server by the user by which used access token was provided")
print(client.characters(Region.EU))

print()
print("List of friends character names who are friend with 'Test-1'")
print(client.friends("Test-1"))

print()
print("Members in clan with id '647d6c53-b3d7-4d30-8d08-de874eb1d845'")
print("Can be used only when using user access token and that user has at least one character in that clan.")
print(client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845").members())
```

</details>


<br>

<details>
<summary>Find Item ID by name</summary>

```python
from stalcraft import AppClient, LocalItem, WebItem

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN)

print()
print("Search by local file")
print(client.auction(LocalItem("Snowflake")).lots())

print()
print("(Not reliable)")
print("Search by listing.json in stalcraft-database github repository")
print(client.auction(WebItem("Snowflake", folder="ru")).lots())
```

</details>


<br>

<details>
<summary>Exceptions</summary>

```python
from stalcraft import (
    UserClient, LocalItem,
    InvalidToken, StalcraftApiException, ItemException
)

TOKEN = "YOUR_TOKEN"

client = UserClient(TOKEN)

print()
print("If token is invalid")
try:
    client = UserClient("test1234567890")
except InvalidToken as e:
    print("Error:", e)

print()
print("If an item with that name does not exist")
try:
    print(LocalItem("test"))
except ItemException as e:
    print("Error:", e)

print()
print("If one of parameters is invalid")
try:
    print(client.auction("test").price_history())
except StalcraftApiException as e:
    print("Error:", e)
```

</details>


<br>

# Output Formats

```python
from stalcraft import AppClient

# Optional
from rich import print

TOKEN = "YOUR_TOKEN"

client = AppClient(TOKEN)

print()
print("Object:")
print(client.emission())

# or client = AppClient(TOKEN, json=True)
client.json = True

print()
print("Json:")
print(client.emission())
```

## Output:

```python
Object:
Emission(
    current_start=datetime.datetime(2023, 1, 27, 9, 28, 16, 656875, tzinfo=datetime.timezone.utc),
    previous_start=datetime.datetime(2023, 1, 27, 7, 26, 16, 656875, tzinfo=datetime.timezone.utc),
    previous_end=datetime.datetime(2023, 1, 27, 7, 31, 16, 656875, tzinfo=datetime.timezone.utc)
)

Json:
{
    'currentStart': '2023-01-27T09:28:16.829929Z',
    'previousStart': '2023-01-27T07:26:16.829929Z',
    'previousEnd': '2023-01-27T07:31:16.829929Z'
}
```
