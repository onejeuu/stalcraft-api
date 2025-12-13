Working with API Clients
==================================================

This guide covers practical usage of api clients: ``AppClient`` for **public** data and ``UserClient`` for **private** data.


----------------------------------------
Basic Concepts
----------------------------------------

STALCRAFT API organizes data by regions (``RU``, ``EU``, ``NA``, ``SEA``). Most endpoints require specifying a region, either per-call or through default client configuration.

Clients return **Pydantic models** by default, providing type safety and IDE autocompletion. You can optionally request raw JSON responses.


----------------------------------------
Getting Started
----------------------------------------

Initialization
^^^^^^^^^^^^^^^

.. warning::

  Never hardcode API credentials in source code. Examples show strings for
  clarity, but production code **SHOULD** use environment variables.

Start by creating an ``AppClient``. You can authenticate either with a created token or with client credentials:

.. code-block:: python

  from scapi import AppClient, Region

  # Option 1: Using existing app token (simplest)
  client = AppClient(token="YOUR_APP_TOKEN")

  # Option 2: Using application credentials
  client = AppClient(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
  )

  # Option 3: With custom client defaults
  client = AppClient(
    token="YOUR_APP_TOKEN",
    region=Region.EU,  # Default region in requests
    json=True          # Return raw json
  )


Making Requests
^^^^^^^^^^^^^^^^

Once initialized, call endpoints directly:

.. code-block:: python

  # List available regions
  regions = await client.regions()
  for region in regions:
    print(f"{region.id}: {region.name}")

  # Get emission status for current region
  # Region in request uses specified, or client default, or config default
  emission = await client.emission()
  print(f"Current emission: {emission.current_start}")
  print(f"Previous: {emission.previous_start} - {emission.previous_end}")

  # Get public character profile
  profile = await client.profile("ZIV")
  print(f"Character alliance: {profile.alliance}")
  print(f"Clan: {profile.clan.info.name if profile.clan else 'No clan'}")


Different Regions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify regions per-call or change the default:

.. code-block:: python

  from scapi import AppClient, Region, Config

  # Client with default region
  client = AppClient(token="YOUR_APP_TOKEN", region=Region.EU)

  # Uses client default (EU)
  emission = await client.emission()

  # Explicit parameter overrides default (SEA)
  emission = await client.emission(region=Region.SEA)

  # Change config default from (RU) to (NA)
  Config.REGION = Region.NA

  # No client default → uses Config.REGION (NA)
  client = AppClient(token="YOUR_APP_TOKEN")
  emission = await client.emission()


Operations Sessions
^^^^^^^^^^^^^^^^^^^^

The ``operations_sessions()`` method retrieves operation history with filtering options.

.. code-block:: python

  # Get recent operation sessions
  sessions = await client.operations_sessions(limit=3)
  for session in sessions:
    print(f"Map: {session.map}, Duration: {session.duration_seconds // 60} minutes")

  # Filter by map and date
  sessions = await client.operations_sessions(map=OperationsMap.SHOCK_THERAPY, after="2025-12-01T00:00:00Z", limit=3)
  users = [user.username for session in sessions for user in session.participants]
  print(f"Shock Therapy sessions since Dec 2025: {users}")


Auction Methods
^^^^^^^^^^^^^^^^

The ``auction()`` factory method returns a dedicated endpoint for a specific item. Chain async methods like ``lots()`` or ``price_history()`` directly.

.. code-block:: python

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


Clan Methods
^^^^^^^^^^^^^

.. code-block:: python

  CLAN_ID = "a552092f-e7c9-4cc3-a256-1e3f525770bf"

  # Get public clan information
  clan = await client.clan(CLAN_ID).info()
  print(f"Clan {clan.name}: Level {clan.level}")
  print(f"Members: {clan.member_count}")
  print(f"Created: {clan.registration_time}")


----------------------------------------
User Client
----------------------------------------

``UserClient`` extends public API access with owner-specific endpoints. Each user token has independent rate limits.

.. important::

  | User-specific endpoints only return data for the account that owns the token.
  | You cannot access other players private information.

.. code-block:: python

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