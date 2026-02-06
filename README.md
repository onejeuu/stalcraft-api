# scapi: Python Client for STALCRAFT API

<!-- Links -->

[pypi]: https://pypi.org/project/stalcraft-api/
[docs]: https://sc-api.readthedocs.io/
[docs-api]: https://sc-api.readthedocs.io/lib
[docs-guides]: https://sc-api.readthedocs.io/guides
[docs-examples]: https://sc-api.readthedocs.io/examples
[stalcraft-docs]: https://eapi.stalcraft.net
[stalcraft-app]: https://eapi.stalcraft.net/registration.html

<!-- Badges -->

[badge-pypi]: https://img.shields.io/pypi/v/stalcraft-api
[badge-python]: https://img.shields.io/pypi/pyversions/stalcraft-api
[badge-docs]: https://img.shields.io/badge/docs-readthedocs.io-informational

[![PyPI][badge-pypi]][pypi] [![Python][badge-python]][pypi] [![Documentation][badge-docs]][docs]

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
    # https://sc-api.readthedocs.io

asyncio.run(main())
```

## 📚 Documentation

Complete documentation is available at **[sc-api.readthedocs.io][docs]**, including:

- [Library API Reference][docs-api]
- [Guides][docs-guides] – Clients, authentication, database lookup, error handling
- [Examples][docs-examples] – Practical use cases and patterns
