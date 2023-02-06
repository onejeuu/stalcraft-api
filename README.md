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

```console
pip install -r requirements.txt
```


<br>

# Quick Start

```python
from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)
```

<br>

# Usage Examples

<details>
<summary>AppClient</summary>

```python
from stalcraft import AppClient, Region, Sort, Order

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

TOKEN = "YOUR_TOKEN"

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
print("List of lots for item with id 'y1q9'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction("y1q9").lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

print()
print("List of price history for item with id 'y1q9'")
print(client.auction("y1q9").price_history())

print()
print("Information about clan with id '562968e7-4282-4ac6-900f-f7f1581495e8'")
print(client.clan("562968e7-4282-4ac6-900f-f7f1581495e8").info())
```

</details>


<br>

<details>
<summary>UserClient</summary>

```python
from stalcraft import UserClient, BaseUrl, Region

TOKEN = "YOUR_TOKEN"

client = UserClient(token=TOKEN, base_url=BaseUrl.DEMO)

# + all methods from AppClient

print("List of characters created by the user on EU server by which used access token was provided")
print(client.characters(Region.EU))

print()
print("List of friends character names who are friend with 'Test-1'")
print(client.friends("Test-1"))


# Members in clan with id '562968e7-4282-4ac6-900f-f7f1581495e8'
# (Can be used only when using user access token and that user has at least one character in that clan)
# client.clan("562968e7-4282-4ac6-900f-f7f1581495e8").members()

#
# Information about player's profile. Includes alliance, profile description, last login time, stats, etc.
# (Not working in DEMO API)
# client.character_profile("ZIV")
```

</details>


<br>

<details>
<summary>Find Item ID by name</summary>

```python
from stalcraft import AppClient, LocalItem, WebItem

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

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
from stalcraft import UserClient, LocalItem

from stalcraft.exceptions import (
    InvalidToken, StalcraftApiException, ItemException
)

TOKEN = "YOUR_TOKEN"

client = UserClient(token=TOKEN)

def handle_exception(func, exception):
    try:
        func()
    except exception as e:
        print("Error:", e)

print()
print("If token is invalid")
handle_exception(lambda: UserClient("test1234567890"), InvalidToken)

print()
print("If an item with that name does not exist")
handle_exception(lambda: LocalItem("test"), ItemException)

print()
print("If one of parameters is invalid")
handle_exception(lambda: client.auction("test").price_history(), StalcraftApiException)
```

</details>


<br>

# About Tokens

```python
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

auth = Authorization(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

print()
print("Get App Token")
print(auth.get_app_token())

print()
print("Get User Code")
print(auth.get_user_code())

auth.input_code()

# or
# auth.code = "USER_CODE"

print()
print("Get User Token")
print(auth.get_user_token())
```

## Refresh User Token

```python
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"
REDIRECT_URI = "YOUR_REDIRECT_URI"

auth = Authorization(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI)

REFRESH_TOKEN = "USER_REFRESH_TOKEN"

print()
print("Refresh User Token")
print(auth.update_token(REFRESH_TOKEN))
```


<br>

# Output Formats

```python
from stalcraft import AppClient

# Optional
from rich import print

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print()
print("Object:")
print(client.emission())

# or client = AppClient(TOKEN, json=True)
client.json = True

print()
print("Json:")
print(client.emission())
```

### Output:

```python
Object:
Emission(
    current_start=None,
    previous_start=datetime.datetime(2023, 1, 30, 5, 16, 52, tzinfo=datetime.timezone.utc),
    previous_end=datetime.datetime(2023, 1, 30, 5, 21, 52, tzinfo=datetime.timezone.utc)
)

Json:
{
    'previousStart': '2023-01-30T05:16:52Z',
    'previousEnd': '2023-01-30T05:21:52Z'
}
```
