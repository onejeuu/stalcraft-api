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
<br>

# ⚡ Quick Start

```python
from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)
```

<br>
<br>

# 🚫 Exceptions

```
Exception
├── InvalidToken
├── StalcraftApiException
│   ├── Unauthorised
│   ├── InvalidParameter
│   ├── NotFound
│   └── RateLimitException
└── ItemException
    ├── ListingJsonNotFound
    └── ItemIdNotFound
```

<br>
<br>

# 🔑 Tokens

```python
from stalcraft import Authorization

CLIENT_ID = "YOUR_CLIENT_ID"
CLIENT_SECRET = "YOUR_CLIENT_SECRET"

auth = Authorization(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
```

<details>
<summary>Get App Token</summary>

```python
print()
print("Get App Token")
print(auth.get_app_token())
```

</details>

<br>

<details>
<summary>Get User Token</summary>

```python
print()
print("Get User Code")
print(auth.user_code_url)

auth.input_code()

# or
# auth.code = "USER_CODE"

print()
print("Get User Token")
print(auth.get_user_token())
```

</details>

<br>

<details>
<summary>Refresh User Token</summary>

```python
REFRESH_TOKEN = "USER_REFRESH_TOKEN"

print()
print("Refresh User Token")
print(auth.update_token(REFRESH_TOKEN))
```

</details>


<br>
<br>

# 📋 Output Formats

```python
from stalcraft import AppClient

TOKEN = "YOUR_TOKEN"

client = AppClient(token=TOKEN)

print()
print("Object:")
print(client.emission())

client.json = True

# or
# client = AppClient(TOKEN, json=True)

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
    'previousStart': '2023-01-30T05:16:52Z',
    'previousEnd': '2023-01-30T05:21:52Z'
}
```
