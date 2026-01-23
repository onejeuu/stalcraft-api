Database Lookup
==================================================

--------------------------------------------------
📋 Overview
--------------------------------------------------

The **STALCRAFT API** uses internal identifiers like ``"zyv9"``, but applications typically need to **search by item names**.
``DatabaseLookup`` solves this by maintaining a **local**, **synchronized copy** of the official game database with **fuzzy search** capabilities.

Key Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``🔗`` **Synchronization:** with the official `stalcraft-database repository <https://github.com/EXBO-Studio/stalcraft-database/>`_
- ``🔍`` **Fuzzy search:** handling typos and partial matches
- ``⚡`` **In-memory caching:** for instant queries (~0.0001 seconds after sync)
- ``📦`` **Multiple data types**: items, achievements, and character stats
- ``🔄`` **Lazy updates:** checks for changes when requested (configurable interval)


How It Works
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``DatabaseLookup`` **downloads compressed JSON indexes** on first use and caches them in memory.
Searches use **fuzzy matching** for typos and partial names. When the configured TTL expires, the next request **automatically updates the cache** if the remote database has changed.


When to Use
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``DatabaseLookup`` to convert names to API internal IDs, build search functionality, or retrieve detailed item information and icons.


----------------------------------------
🚀 Quick Start
----------------------------------------

Minimal setup to start searching for item IDs.

.. code-block:: python

  from scapi import DatabaseLookup, AppClient
  import asyncio
  import os

  async def main():
    # Create api client
    client = AppClient(token=os.getenv("YOUR_APP_TOKEN"))

    # Create lookup instance
    lookup = DatabaseLookup()

    # Initial sync (downloads database, ~1-15 seconds)
    await lookup.sync()

    # Search for items by name
    results = await lookup.search("AK-105")
    for result in results[:3]:
      print(f"{result.id}: {result.data.get('name', {}).get('lines', {})}")

    # Get the best match
    item = await lookup.find_one("AK-105")
    if item:
      print(f"Item ID: {item.id}")

      # Use with API client
      lots = await client.auction(item.id).lots(limit=5)
      print(f"Found {len(lots)} auction lots")

  asyncio.run(main())


----------------------------------------
⚙️ Lookup Initialization
----------------------------------------

Creating a Lookup Instance.

.. code-block:: python

  from scapi import DatabaseLookup

  # Default settings (RU realm, 15‑minute stale check, 24‑hour cache)
  lookup = DatabaseLookup()

  # With custom configuration
  lookup = DatabaseLookup(
    realm="global",         # Game version: "ru" or "global"
    threshold=0.25,         # Similarity threshold (0.0‑1.0)
    stale_time=300,         # Check for updates every 5 minutes
    cache_ttl=7200,         # Files cache for 2 hours
    cache_capacity=256,     # Keep up to 256 cached files
  )


Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| The first search or explicit ``sync()`` downloads the database.
| Subsequent requests use the cached version.

.. code-block:: python

  # Explicit sync (recommended on application start)
  await lookup.sync()

  # Force re‑download even if up‑to‑date
  await lookup.sync(force=True)


Lazy Sync
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you don't call ``sync()`` explicitly, the first request will trigger synchronization automatically.

.. code-block:: python

  # This will sync if needed, then search
  results = await lookup.search("AK-105")


----------------------------------------
🔍 Searching Entities
----------------------------------------

Basic Search
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  # Get all matches with relevance scores
  results = await lookup.search("AK-105")

  for item in results:
    # item.data contains the full entity data
    print(f"ID: {item.id}, Score: {item.score:.2f}")


Finding the Best Match
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  # Get single best result (returns None if no matches)
  item = await lookup.find_one("KA-105") # Handles typos
  if item:
    print(f"Found: {item.id}")


Finding the Best Match
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  # Lower threshold = more results (including poor matches)
  results = await lookup.search("FN F2000", threshold=0.05)
  print([item.data.get("name", {}).get("lines", {}).get("en") for item in results])
  print(f"Found {len(results)} results")
  print()

  # Higher threshold = only close matches
  results = await lookup.search("FN F2000", threshold=0.25)
  print([item.data.get("name", {}).get("lines", {}).get("en") for item in results])
  print(f"Found {len(results)} results")


Searching Different Data Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from scapi import IndexFile

  # Items (default)
  items = await lookup.search("AK-105")

  # Achievements
  achievements = await lookup.search(
    "Wretch",
    filename="achievements.json"  # or IndexFile.ACHIEVEMENTS
  )
  print(achievements)

  # Character stats
  stats = await lookup.search(
    "Piggies",
    filename=IndexFile.STATS  # Using enum prevents typos
  )
  print(stats)


----------------------------------------
📄 Retrieving Information
----------------------------------------

Direct Access by ID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  # Get entity data directly
  entity = await lookup.get_entity("zyv9")
  if entity:
    print("Item name:", entity.get("name", {}).get("lines", {}).get("en"))


Search Item Details
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO WARN
This makes web reqests every time. If you call item_info you NEED to use github token

.. code-block:: python

  # Search for item
  item = await lookup.find_one("AK-105")
  if not item:
    print("Item not found")
    return

  # Extract paths from search resul
  path = item.data["data"]

  # Get detailed item information
  details = await lookup.item_info(path)
  print("Category:", details["category"])
  print("Color:", details["color"])

  damage = next(
      e["value"]
      for block in details["infoBlocks"]
      for e in block["elements"]
      if e.get("name", {}).get("key") == "core.tooltip.stat_name.damage_type.direct"
  )
  print(f"Damage: {damage}")


Upgraded Items
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  item = await lookup.find_one("AK-105")
  if item:
    path = item.data["data"]
    details = await lookup.item_info(path, upgrade_level=10)

