# scapi: Python Client for STALCRAFT API

[![PyPI](https://img.shields.io/pypi/v/stalcraft-api?color=blue)](https://pypi.org/project/scapi/) [![Python](https://img.shields.io/pypi/pyversions/stalcraft-api)](https://pypi.org/project/scapi/) [![Documentation](https://img.shields.io/badge/docs-readthedocs.io-informational)](https://sc-api.readthedocs.io/)

**scapi** is an unofficial asynchronous wrapper for **external [STALCRAFT API](https://eapi.stalcraft.net)**.\
It provides access to read-only game endpoints including auction, emissions, clans, profiles, and etc.

## ✨ Features

- `AppClient` and `UserClient` for API requests
- `OAuthClient` for OAuth 2.0 authorization flows
- `DatabaseLookup` for items search
- Typed Pydantic model responses
- Configurable default parameters
- Rate limit information access

## 📌 Before You Start

To use the API, you must **[register an application](https://eapi.stalcraft.net/registration.html)** and receive approval. Use **App tokens** for public resources or **User tokens** (via OAuth) for player-specific resources like character friends. Demo API is available at `https://dapi.stalcraft.net` for testing without registration.

## 🛠️ Installation

```bash
pip install stalcraft-api -U
```

## 🚀 Quick Start

```python
import asyncio
from scapi import AppClient, Region

# Initialize app client
# WARN: Store credentials in environment variables, NOT in source code
client = AppClient(client_id="YOUR_CLIENT_ID", client_secret="YOUR_CLIENT_SECRET")
# OR
client = AppClient(token="YOUR_APP_TOKEN")

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
    # https://sc-api.readthedocs.io/api

asyncio.run(main())
```

## 📚 Documentation

Complete documentation is available at **[sc-api.readthedocs.io](https://sc-api.readthedocs.io)**, including:

- [Library API Reference](https://sc-api.readthedocs.io/api)
- [Guides](https://sc-api.readthedocs.io/guides) – Clients, authentication, database lookup, error handling
- [Examples](https://sc-api.readthedocs.io/examples) – Practical use cases and patterns
