Index
==================================================

.. include:: _links.rst

.. toctree::
  :maxdepth: 1

  guides/index
  lib/scapi

----------------------------------------
Overview
----------------------------------------

| **scapi** is an unofficial asynchronous wrapper for external `STALCRAFT API <https://eapi.stalcraft.net>`_.
| It provides access to read-only game endpoints including auction, emissions, clans, profiles, and etc.


----------------------------------------
✨ Features
----------------------------------------

- ``AppClient`` and ``UserClient`` for API requests
- ``OAuthClient`` for OAuth 2.0 authorization flows
- ``DatabaseLookup`` for items search
- Typed Pydantic model responses
- Configurable default parameters
- Rate limit information access


----------------------------------------
🛠️ Installation
----------------------------------------

.. code-block:: bash

  pip install stalcraft-api -U


----------------------------------------
🚀 Quick Start
----------------------------------------

.. code-block:: python

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
