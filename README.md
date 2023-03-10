<h1 align="center">stalcraft-api unofficial python library</h1>

<p align="center">
    <a href="https://pypi.org/project/stalcraft-api" alt="PyPi Package Version">
        <img src="https://img.shields.io/pypi/v/stalcraft-api.svg?style=flat-square"/></a>
    <a href="https://pypi.org/project/stalcraft-api" alt="Supported python versions">
        <img src="https://img.shields.io/pypi/pyversions/stalcraft-api.svg?style=flat-square"/></a>
    <a href="https://opensource.org/licenses/MIT" alt="MIT License">
        <img src="https://img.shields.io/pypi/l/aiogram.svg?style=flat-squar"/></a>
</p>


<br>

<p align="center">
    <b>Official API documentation:</b> https://eapi.stalcraft.net
</p>
<p align="center">
    <b>Before you can use the API, you must register your application and receive approval<b>
</p>
<p align="center">
    <b>For testing Demo API is available<b>
</p>
<p align="center">
    <a href="https://eapi.stalcraft.net/registration.html">more about applications</a>
</p>


<br>

# 🔧 Install

### Pip

```console
pip install stalcraft-api --upgrade
```

<details>
<summary>Manual</summary>

```console
git clone git@github.com:onejeuu/stalcraft-api.git
```

```console
cd stalcraft-api
```

```console
pip install -r requirements.txt
```
</details>


<br>

# ⚡ Quick Start

```python
from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)
```


<br>

# 📎 Usage Examples

<details>
<summary>App Client</summary>

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
print("List of lots for item with id '1r756'")
print("With offset 5, limit 2, sort by buyout price and order by descending")
print(client.auction("1r756").lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE, order=Order.DESC))

print()
print("List of price history for item with id '1r756'")
print(client.auction("1r756").price_history())

print()
print("Information about clan with id '562968e7-4282-4ac6-900f-f7f1581495e8'")
print(client.clan("562968e7-4282-4ac6-900f-f7f1581495e8").info())
```

</details>


<br>

<details>
<summary>User Client</summary>

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
from stalcraft import AppClient, LocalItem, WebItem, ItemFolder

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print()
print("Search by local file")
print(client.auction(LocalItem("Snowflake")).lots())

print()
print("(Not reliable)")
print("Search by listing.json in stalcraft-database github repository")
print(client.auction(WebItem("Snowflake", folder=ItemFolder.GLOBAL)).lots())
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

# 🚫 Rate Limits

```python
# To obtain information about the current rate limit values, you can use client.ratelimit
# Warning: by default client.ratelimit is None until the first request is made (except for regions), so use caution

from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print(client.ratelimit)
# Output: None

client.emission()

print(client.ratelimit)
# Output: RateLimit(limit=200, remaining=199, reset=datetime.datetime(2023, 2, 23, 12, 0, 0, tzinfo=...))
```


<br>

# 🔑 About Tokens

### Get User and App Token

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

### Refresh User Token

```python
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

auth = Authorization(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

REFRESH_TOKEN = "USER_REFRESH_TOKEN"

print()
print("Refresh User Token")
print(auth.update_token(REFRESH_TOKEN))
```


<br>

# 📋 Output Formats

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
