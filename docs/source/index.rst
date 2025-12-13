Index
==================================================

.. include:: _links.rst

.. toctree::
  :maxdepth: 1

  guides/index
  examples/index
  api/index

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
