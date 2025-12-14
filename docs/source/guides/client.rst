Working with API Clients
==================================================

This guide covers practical usage of the API clients. You'll learn how to access **public** game data with ``AppClient`` and **private** player data with ``UserClient``.


----------------------------------------
Basic Concepts
----------------------------------------

| STALCRAFT API organizes data by regions (``RU``, ``EU``, ``NA``, ``SEA``).
| Most endpoints require specifying a region.

**Authentication Types:**

-  ``Application Credentials``, ``App Token`` - **For public data** (auction, emissions, profiles)
- ``User Token`` - **For public and private data** (characters, friends, clan membership)

**Response Formats:**

- ``Pydantic Models`` (default) - Typed Python objects with IDE hints
- ``Raw JSON`` - Original API response


.. hint::

  For application register and token creation, refer to the :doc:`OAuth Guide <oauth>`.


----------------------------------------
Getting Started
----------------------------------------

Initializing AppClient
^^^^^^^^^^^^^^^^^^^^^^^


.. warning::

  | **NEVER** include credentials in source code. Examples show strings for clarity.
  | Production code **SHOULD** use `environment variables <https://12factor.net/config>`_.


Start by creating an ``AppClient``. You can authenticate either with **Application Credentials** OR with **App Token**.

.. code-block:: python
  :caption: App Client Initialization

  from scapi import AppClient, Region

  # Option 1: Using application credentials
  client = AppClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
  )

  # Option 2: Using created app token
  client = AppClient(token="YOUR_APP_TOKEN")

  # And you can set defaults for this client instance
  client = AppClient(
    token="YOUR_APP_TOKEN",
    region=Region.EU,  # Default region in requests
    json=True          # Return raw json instead of typed models
  )


Making First Requests
^^^^^^^^^^^^^^^^^^^^^^

Once client initialized, you can call endpoints directly.

API calls are asynchronous (``async``/``await``). You need to run them inside an `event loop <https://docs.python.org/3/library/asyncio-eventloop.html>`_.

For simplicity, examples in this guide show only the relevant ``await`` calls. Assume they're inside an ``async`` function, typically called from ``asyncio.run()``.


.. tip::

  If you're new to async Python, check the `official asyncio documentation <https://docs.python.org/3/library/asyncio.html>`_.


.. code-block:: python
  :caption: Basic Example

  import asyncio
  from scapi import AppClient

  client = AppClient(token="YOUR_APP_TOKEN")

  async def main():
    # List available api regions
    regions = await client.regions()
    for region in regions:
      print(f"{region.id}: {region.name}")

    # Get emission status
    emission = await client.emission()
    print(f"Current emission: {emission.current_start}")
    print(f"Previous: {emission.previous_start} - {emission.previous_end}")

    # Get public character profile
    profile = await client.profile("ZIV")
    print(f"Character alliance: {profile.alliance}")
    print(f"Clan: {profile.clan.info.name if profile.clan else 'No clan'}")

  asyncio.run(main())


Use Different Regions
^^^^^^^^^^^^^^^^^^^^^^

| Region selection follows a priority chain:
| ``explicit call parameter`` → ``client instance default`` → ``global Config.REGION``.

| When you specify a region in a method call, it overrides all defaults.
| If omitted, the client checks its own ``region`` parameter.
| If that's also unset, it falls back to ``Config.REGION`` (which defaults to ``"ru"``).

This allows flexible configuration.

.. code-block:: python
  :caption: Different Regions Usage

  from scapi import AppClient, Region, Config

  # Client with default region (EU)
  client = AppClient(token="YOUR_APP_TOKEN", region=Region.EU)

  # Uses client default (EU)
  emission = await client.emission()

  # Explicit parameter overrides default (SEA)
  emission = await client.emission(region=Region.SEA)

  # Change config default from (RU) to (NA)
  Config.REGION = Region.NA

  # Create client with no default region
  client = AppClient(token="YOUR_APP_TOKEN")

  # No client region default → uses Config.REGION (NA)
  emission = await client.emission()


Operations Sessions
^^^^^^^^^^^^^^^^^^^^

The ``operations_sessions()`` method returns listing including participants, weapons, stats, and other information.

.. code-block:: python
  :caption: Operations Sessions Usage

  # Get recent operation sessions
  sessions = await client.operations_sessions(limit=3)
  for session in sessions:
    print(f"Map: {session.map}, Duration: {session.duration_seconds // 60} minutes")

  # Filter by map and date
  sessions = await client.operations_sessions(
    map=OperationsMap.SHOCK_THERAPY,
    after="2025-12-01T00:00:00Z",
    limit=3
  )
  users = [user.username for session in sessions for user in session.participants]
  print(f"Shock Therapy users since Dec 2025: {users}")


Auction Methods
^^^^^^^^^^^^^^^^

| The ``auction()`` **factory method** returns a dedicated endpoint for a specific item.
| Chain async methods like ``lots()`` or ``price_history()`` directly.

| Use ``sort`` and ``order`` parameters to control listing order.
| The ``limit`` parameter caps results per request (max ``200``).

.. code-block:: python
  :caption: Auction Methods Usage

  # Target Item ID
  ITEM_ID = "zyv9"

  # Get active lots
  lots = await client.auction(ITEM_ID).lots(limit=3)
  print(f"Active latest lots: {lots}")

  # With sorting cheapest first
  cheapest = await client.auction(ITEM_ID).lots(
    limit=3,
    sort=SortAuction.BUYOUT_PRICE,
    order=Order.ASCENDING,
  )
  print(f"Cheapest lots: {cheapest}")

  # Price history
  history = await client.auction(ITEM_ID).price_history(limit=3)
  print(f"Historical prices: {history}")


.. admonition:: Finding Item IDs
  :class: tip

  Use ``DatabaseLookup`` (see :doc:`Database Guide <database>`) or reference the `official Stalcraft Database <https://github.com/EXBO-Studio/stalcraft-database>`_.


Clan Methods
^^^^^^^^^^^^^

| The ``clan()`` **factory method** returns a dedicated endpoint for a specific clan.

.. code-block:: python
  :caption: Clan Methods Usage

  CLAN_ID = "a552092f-e7c9-4cc3-a256-1e3f525770bf"

  # Get public clan information
  clan = await client.clan(CLAN_ID).info()
  print(f"Clan {clan.name}: Level {clan.level}")
  print(f"Members: {clan.member_count}")
  print(f"Created: {clan.registration_time}")


----------------------------------------
UserClient for Private Data
----------------------------------------

``UserClient`` requires an OAuth user token and provides access to player-specific endpoints while maintaining all ``AppClient`` functionality.


.. important::

  | User-specific endpoints only return data for the account that owns the token.
  | You cannot access other players private information.


.. code-block:: python
  :caption: User Client Usage

  from scapi import UserClient

  # Initialize with OAuth user token
  client = UserClient(token="USER_OAUTH_TOKEN")

  # Public data works identically to AppClient
  emission = await client.emission()
  lots = await client.auction("zyv9").lots(limit=3)

  # User-specific endpoints
  characters = await client.characters()
  print(f"Characters for this account: {[char.info.name for char in characters]}")

  # Friends list for a specific character
  friends = await client.friends("YourCharacterName")
  print(f"Friends: {friends}")


Clan Methods
^^^^^^^^^^^^^


.. important::

  This endpoint will fail with a 401 error if the token owner is not a member of the specified clan.


.. code-block:: python

  try:
    members = await client.clan("a552092f-e7c9-4cc3-a256-1e3f525770bf").members()
    print(f"Clan members: {len(members)}")
    for member in members:
      print(f"  {member.name} - {member.rank}")

  except Exception as err:
    print(f"Cannot access members: {err}")


----------------------------------------
Error Handling and Rate Limits
----------------------------------------

| API errors raise specific exceptions.
| Rate limit information is available through the client.

.. code-block:: python

  from scapi import AppClient, exceptions

  client = AppClient(token="YOUR_APP_TOKEN")

  for offset in range(99):
    try:
      lots = await client.auction("zyv9").lots(limit=1, offset=offset)
      print(f"Lot {lots}")

    except exceptions.RateLimitError:
      print(f"Rate limit exceeded {client.ratelimit}")
      break

    except exceptions.ScApiException as err:
      print(f"Error {err}")
      break

    except Exception as err:
      print(f"Unexcepted error {err}")
      break
