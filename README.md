# scapi: Python Client for STALCRAFT API

<!-- Links -->

[pypi]: https://pypi.org/project/stalcraft-api
[license]: https://opensource.org/licenses/MIT
[tests]: https://github.com/onejeuu/stalcraft-api/actions/workflows/tests.yml
[issues]: https://github.com/onejeuu/stalcraft-api/issues
[codecov]: https://codecov.io/github/onejeuu/stalcraft-api
[docs]: https://sc-api.readthedocs.io
[docs-guides]: https://sc-api.readthedocs.io/en/latest/guides/
[docs-guides-client]: https://sc-api.readthedocs.io/en/latest/guides/client.html
[docs-guides-database]: https://sc-api.readthedocs.io/en/latest/guides/database.html
[docs-guides-oauth]: https://sc-api.readthedocs.io/en/latest/guides/oauth.html
[docs-api]: https://sc-api.readthedocs.io/en/latest/lib/scapi.html
[stalcraft-docs]: https://eapi.stalcraft.net
[stalcraft-app]: https://eapi.stalcraft.net/registration.html

<!-- Badges -->

[badge-pypi]: https://img.shields.io/pypi/v/stalcraft-api.svg
[badge-license]: https://img.shields.io/github/license/onejeuu/stalcraft-api
[badge-python]: https://img.shields.io/pypi/pyversions/stalcraft-api.svg
[badge-docs]: https://img.shields.io/readthedocs/sc-api
[badge-tests]: https://img.shields.io/github/actions/workflow/status/onejeuu/stalcraft-api/tests.yml?label=tests
[badge-issues]: https://img.shields.io/github/issues/onejeuu/stalcraft-api
[badge-codecov]: https://codecov.io/github/onejeuu/stalcraft-api/graph/badge.svg?token=QZQSMOHL6G

[![Python][badge-python]][pypi] [![PyPI][badge-pypi]][pypi] [![License][badge-license]][license] [![codecov][badge-codecov]][codecov] [![Issues][badge-issues]][issues] [![Docs][badge-docs]][docs] [![Tests][badge-tests]][tests]

**scapi** is an unofficial asynchronous wrapper for **external [STALCRAFT API][stalcraft-docs]**.\
It provides access to read-only game endpoints including auction, emissions, clans, profiles, and etc.

## ✨ Features

- `AppClient` and `UserClient` for API requests
- `OAuthClient` for OAuth 2.0 authorization flows
- `DatabaseLookup` for items search
- Typed Pydantic model responses
- Configurable default parameters
- Rate limit information access

## 📌 Before You Start

To use the API, you must **[register an application][stalcraft-app]** and receive approval. Use **App tokens** for public resources or **User tokens** (via OAuth) for player-specific resources like character friends. Demo API is available at `https://dapi.stalcraft.net` for testing without registration.

## 🛠️ Installation

```bash
pip install stalcraft-api -U
```

## 🚀 Quick Start

```python
from scapi import AppClient, Region
import asyncio
import os

# Initialize app client with your credentials
client = AppClient(client_id=os.getenv("CLIENT_ID"), client_secret=os.getenv("CLIENT_SECRET"))

# OR use generated token from OAuthClient
client = AppClient(token=os.getenv("APP_TOKEN"))

async def main():
    # Get emission status for current region
    emission = await client.emission()
    print(f"Last emission ended at: {emission.previous_end}")

    # Get public character information
    profile = await client.profile("ZIV")
    print("Character profile:", profile)

    # Fetch last 3 auction lots for item with id "zyv9"
    lots = await client.auction("zyv9").lots(limit=3)
    print("Actual lots:", lots)

    # Other methods can be know in docs:
    # https://sc-api.rtfd.io

asyncio.run(main())
```

## 📚 Documentation

Complete documentation is available at **[sc-api.readthedocs.io][docs]**, including:

- [Guides][docs-guides]
  - [API Clients][docs-guides-client]
  - [Database Lookup][docs-guides-database]
  - [Authentication][docs-guides-oauth]
- [Library API Reference][docs-api]
