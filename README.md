<h1 align="center">stalcraft-api unofficial python library</h1>

<p align="center">
    <a href="https://pypi.org/project/stalcraft-api" alt="PyPi Package Version">
        <img src="https://img.shields.io/pypi/v/stalcraft-api.svg?style=flat-square"/>
    </a>
    <a href="https://pypi.org/project/stalcraft-api" alt="Supported python versions">
        <img src="https://img.shields.io/pypi/pyversions/stalcraft-api.svg?style=flat-square"/>
    </a>
    <a href="https://opensource.org/licenses/MIT" alt="MIT License">
        <img src="https://img.shields.io/pypi/l/aiogram.svg?style=flat-squar"/>
    </a>
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
pip install stalcraft-api -U
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
poetry install
```
</details>


<br>

# ⚡ Quick Start

```python
from stalcraft import AppClient, Region

# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print(client.emission(Region.EU))
```

<details>
<summary>🐇 Asyncio</summary>

```python
from stalcraft.asyncio import AsyncAppClient
from stalcraft import Region
import asyncio

TOKEN = "YOUR_TOKEN"

async def main():
    client = AsyncAppClient(token=TOKEN)

    print(await client.emission(Region.EU))

asyncio.run(main())
```

</details>

<br>


# 🚫 Exceptions

```
StalcraftApiException
├── InvalidToken
├── MissingCredentials
├── ApiRequestError
│   ├── RequestUnauthorised
│   ├── RequestInvalidParameter
│   ├── RequestNotFound
│   └── RateLimitReached
└── ItemIdError
    ├── ListingJsonNotFound
    └── ItemIdNotFound
```

<br>

# 🔑 Authorization

```python
from stalcraft import AppAuth, UserAuth

# Only as example.
# Do not store your credentials in code.
CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

app_auth = AppAuth(CLIENT_ID, CLIENT_SECRET)
user_auth = UserAuth(CLIENT_ID, CLIENT_SECRET)
```

<details>
<summary>Get App Token</summary>

```python
print(app_auth.get_token())
```

</details>

<br>

<details>
<summary>Get User Token</summary>

```python
print(user_auth.code_url)

code = input("Enter code:")

print()
print(user_auth.get_token(code))
```

</details>

<br>

<details>
<summary>Refresh User Token</summary>

```python
REFRESH_TOKEN = "USER_REFRESH_TOKEN"

print(user_auth.refresh_token(REFRESH_TOKEN))
```

</details>


<br>

# 📋 Output Formats

```python
from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print("Object:")
print(client.emission())

client = AppClient(TOKEN, json=True)

# or
# client.json = True

print()
print("Json:")
print(client.emission())
```

### Output:

```python
Object:
Emission(
    current_start=None,
    previous_start=datetime.datetime(2023, 1, 30, 12, 0, 0, tzinfo=datetime.timezone.utc),
    previous_end=datetime.datetime(2023, 1, 30, 12, 5, 0, tzinfo=datetime.timezone.utc)
)

Json:
{
    'previousStart': '2023-01-30T12:00:00Z',
    'previousEnd': '2023-01-30T12:05:00Z'
}
```
