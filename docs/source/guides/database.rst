Database Lookup
==================================================

--------------------------------------------------
📋 Overview
--------------------------------------------------

The **STALCRAFT API** uses internal identifiers like ``"zyv9"``, but applications typically need to **search by item names**.
``DatabaseLookup`` solves this by maintaining a **local**, **synchronized copy** of the official game database with **fuzzy search** capabilities.

Key Features
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- ``🔗`` **Synchronization:** with the official `stalcraft-database <https://github.com/EXBO-Studio/stalcraft-database/>`_ repository
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


--------------------------------------------------
📖 Core Concepts
--------------------------------------------------

Realms
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Game data exists in two separate versions: ``ru`` and ``global``.
Most items are the same, but some are realm‑specific.
Defaults to ``ru``.


Data Source
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The library synchronizes with the official `stalcraft-database <https://github.com/EXBO-Studio/stalcraft-database/>`_ GitHub repository. Index files are used: ``listing.json`` (items), ``achievements.json``, and ``stats.json``.


Fuzzy Search
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Search uses N‑gram tokenization to handle typos, partial names, and different languages.
The ``threshold`` parameter (``0.0`` -- ``1.0``) controls match strictness lower values return more results, higher values only close matches.
Defaults to ``0.1``.


Caching & Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Commit freshness**: The remote commit hash is cached for ``stale_time`` seconds. If this time expires, the next method call will check GitHub for changes.

**Asset cache**: Downloaded item details (JSON) and icons (PNG) are stored in memory for ``asset_ttl`` seconds.

**Update behavior** (If a newer commit is found):

- ``sync_on_update=True`` (default) -- All indexes reload.
- ``sync_on_update=False`` -- Only the accessed index reloads.

.. tip::

  | Set ``stale_time=0`` to disable checks.
  | The lookup will never contact GitHub unless you call ``sync(force=True)``.


State Monitoring
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use lookup.state to determine if the local database is current or needs synchronization.


--------------------------------------------------
⚙️ Initial Setup
--------------------------------------------------

Create a ``DatabaseLookup`` with default settings.
It will be configured for the ``ru`` realm, indexes considered stale after **15 minutes** (``stale_time=900``) and caching assets for **24 hours** (``asset_ttl=86400``).

.. code-block:: python

  from scapi import DatabaseLookup

  lookup = DatabaseLookup()


First Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

| Execute ``sync()`` when your application initializes.
| This downloads the index files from GitHub and caches them locally.

| Synchronization takes **1–10 seconds**, depending on your connection.
| Data is then cached in memory for subsequent requests.

.. code-block:: python

  await lookup.sync()


Sync Strategy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Choose settings based on how your application runs.

**Long‑running service** (web app, bot):

.. code-block:: python

  lookup = DatabaseLookup(
    stale_time=300,          # Indexes considered stale after 5 minutes
    sync_on_update=True,     # Reload all indexes if an update is found
  )

**Script or CLI tool**:

.. code-block:: python

  lookup = DatabaseLookup(
    stale_time=0,            # Indexes never considered stale
    sync_on_update=False,    # Update only accessed indexes
  )

  # Sync manually if you need fresh data
  await lookup.sync(force=True)


.. admonition:: Partial Index Updates
  :class: note

  Use ``sync_on_update=False`` if your application only accesses a specific index file (e.g., only ``listing.json``).
  When an update is detected, only that file will be refreshed, avoiding unnecessary downloads of other indexes like ``achievements.json``.


--------------------------------------------------
🔍 Search Workflow
--------------------------------------------------

Most operations follow this pattern: **search** → **extract ID/paths** → **fetch details or call API**.

.. code-block:: python

  # Search for an item
  result = await lookup.find_one("AK-105")
  if not result:
    print("Item not found")
    return

  # Extract the internal ID
  item_id = result.id              # "zz2rn"
  item_path = result.data["data"]  # "/items/weapon/assault_rifle/zz2rn.json"

  # Use the ID with an API client
  client = AppClient(token=os.getenv("APP_TOKEN"))
  lots = await client.auction(item_id).lots(limit=5)

  # Or fetch detailed item information
  details = await lookup.item_info(item_path)


Object ``Lookup`` object contains ``id``, ``data``, and ``score``. The ``data`` field varies by index type but always includes the relevant paths and metadata for that entity type.


Getting Entity Data by ID
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``get_entity()`` when you already have an internal ID (e.g., from an API response) and need its display information.

.. code-block:: python

  # Get achievement data by ID
  achievement = await lookup.get_entity("operations_naked_crew", filename="achievements.json")

  if achievement:
    title = achievement.get("title", {}).get("lines", {}).get("en")
    print(f"Achievement: {title}")  # "Wretch"

  # Get stat name by ID
  stat = await lookup.get_entity("reg-tim", filename="stats.json")

  if stat:
    name = stat.get("name", {}).get("lines", {}).get("en")
    print(f"Stat: {name}")  # Arrived in the Zone


Item Detailed Information
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Method ``item_info()`` fetches the complete JSON of an item, including stats, descriptions, and upgrade variants.

.. code-block:: python

  # Get base item data
  info = await lookup.item_info("/items/weapon/assault_rifle/zz2rn.json")

  # Get an upgraded item version (levels 0–15)
  info = await lookup.item_info(
    "/items/weapon/assault_rifle/zz2rn.json",
    upgrade_level=10
  )

Method ``item_icon()`` downloads the item icon as PNG bytes.

.. code-block:: python

  icon = await lookup.item_icon("/icons/weapon/assault_rifle/zz2rn.png")

  with open("ak105.png", "wb") as fp:
    fp.write(icon)


.. admonition:: Network Requests
  :class: caution

  Both ``item_info()`` and ``item_icon()`` perform **HTTP requests to GitHub** (unless file is already cached).
  For frequent use, provide a **GitHub token** to your ``GitHubClient``.

  See `GitHub documentation <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_ for personal access token creation.


Different Data Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify the filename ``parameter`` to search achievements or stats instead of items.

.. code-block:: python

  from scapi import IndexFile

  # Search achievement
  achievement = await lookup.find_one(
    "Wretch",
    filename="achievements.json" # or IndexFile.ACHIEVEMENTS
  )

  # Search character stats
  stats = await lookup.find_one(
    "Piggies",
    filename=IndexFile.STATS,
  )

