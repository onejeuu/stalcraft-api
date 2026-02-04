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
Defaults to ``0.2``.


Caching & Synchronization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Commit freshness**: The remote commit hash is cached for ``stale_time`` seconds. If this time expires, the next method call will check GitHub for changes.

**Asset cache**: Downloaded item details (JSON) and icons (PNG) are stored in memory for ``asset_ttl`` seconds.

**Update behavior** (If a newer commit is found):

- ``sync_on_update=True`` (default) -- All indexes reload.
- ``sync_on_update=False`` -- Only the accessed index reloads.


.. tip::

  | Setting ``stale_time=0`` disables automatic update checks.
  | Missing files are still downloaded when needed, but outdated files are not detected automatically.


--------------------------------------------------
🚀 Initial Setup
--------------------------------------------------

Create a ``DatabaseLookup`` with default settings.
It will be configured for the ``ru`` realm, indexes considered stale after **15 minutes** (``stale_time=900``) and caching assets for **24 hours** (``asset_ttl=86400``).

.. code-block:: python

  from scapi import DatabaseLookup, GitHubClient
  import asyncio
  import os

  # Production use REQUIRES a GitHub token
  github = GitHubClient(token=os.getenv("GITHUB_TOKEN"))
  lookup = DatabaseLookup(github=github)

  async def main():
    # Initial sync downloads and caches indexes
    await lookup.sync()

    # Now ready for instant searches
    results = await lookup.search("AK-105")
    print(f"Found {len(results)} items")

  asyncio.run(main())


.. tip::

  Call ``sync()`` once when your application starts.
  It downloads JSON files from GitHub, caches them locally, and builds an in‑memory search index.


Sync Realm
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, ``sync()`` updates only the **default realm** (instance ``realm`` parameter or ``Config.REALM``).

To synchronize both realms, pass a keyword from ``ALL_REALMS_KEYWORDS`` (e.g., ``"all"``).

.. code-block:: python

  # Sync only the default realm ("ru")
  await lookup.sync()

  # Sync both realms ("ru" + "global")
  await lookup.sync(realm="all")

  # Sync a specific realm
  await lookup.sync(realm="global")

The ``ALL_REALMS_KEYWORDS`` includes ``("all", "any", "*")`` for convenience.


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

  | With ``sync_on_update=False``, indexes are loaded on‑demand when first accessed.
  | When an update is detected, **only the currently loaded indexes** are refreshed.
  | This avoids downloading unused files (like ``achievements.json``) when you only need ``listing.json``.
  |
  | With ``sync_on_update=True`` (default), **all indexes** are refreshed when any update is detected


--------------------------------------------------
🔍 Search Workflow
--------------------------------------------------

Standard Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

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


Different Data Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specify the ``filename`` parameter to search achievements or stats instead of items.

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
    filename=IndexFile.STATS, # you can use enum to avoid mistypes
  )


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


Retrieving All Entities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``get_all()`` to fetch the complete dictionary of entities for batch processing or analysis.

.. code-block:: python

  # Get all stats entities
  stats = await lookup.get_all(filename="stats.json")

  grouped = {}
  for stat in stats.values():
    category = stat.get("category", "UNCATEGORIZED")
    grouped.setdefault(category, []).append(stat)

  for category in sorted(grouped):
    names = sorted([stat["name"]["lines"]["ru"] for stat in grouped[category]])
    print(f"{category}: {', '.join(names)}")


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


--------------------------------------------------
⚙️ Advanced Configuration
--------------------------------------------------

Custom GitHub Client
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


.. important::

  | Production use requires a `GitHub personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_.
  | **Without one, you will hit rate limits quickly**. ``DatabaseLookup`` without a token is for testing only.


.. code-block:: python

  from scapi import DatabaseLookup, GitHubClient

  # Create GitHub client with token
  github = GitHubClient(token=os.getenv("GHP_ACCESS_TOKEN"))

  # Pass it to the lookup
  lookup = DatabaseLookup(github=github)


Optimizing Parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Settings should match your applications access pattern. Consider three dimensions:

``📡`` **Update frequency**: How often you need fresh data.

- **Frequent updates** (price monitor, live dashboard): Set ``stale_time=300–900`` (5–15 minutes). The lookup will check GitHub regularly and reload data when changes are detected.
- **Infrequent updates** (static analysis, occasional reports): Set ``stale_time=3600+`` (1+ hour) or ``stale_time=0`` and call ``sync(force=True)`` manually.

``📊`` **Index usage**: Which parts of the database you actually use.

- **Multiple index types**: ``sync_on_update=True`` ensures all indexes stay in sync when any one updates.
- **Single index type**: ``sync_on_update=False`` prevents downloading unused indexes like ``achievements.json``.

``💾`` **Asset cache lifetime**: How long you can tolerate cached data.

- **Long cache** (24+ hours): Suitable for background jobs where momentary staleness is acceptable. Increase ``asset_ttl``.
- **Short cache** (minutes): For real‑time applications where data must be recent. Decrease ``asset_ttl``.
- **Memory trade‑off**: Higher ``asset_ttl`` and ``asset_capacity`` keep more data in **RAM**, improving speed at the cost of memory usage.

.. tip::

  There is no universal “best” setting.
  Adjust parameters based on **how often your data changes, which indexes you query, and how fresh the results need to be**.


--------------------------------------------------
🚨 Common Issues
--------------------------------------------------

.. list-table::
  :header-rows: 1

  * - Problem
    - Solution
  * - **GitHub rate limit errors**
    - Provide `GitHub personal access token <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens>`_ to ``GitHubClient``. Authenticated requests have higher limits.
  * - **Item not found in search**
    - Lower the threshold parameter (e.g., to ``0.05``). The default ``0.1`` may be too strict for some names.
  * - **Search returns irrelevant matches**
    - Increase the threshold (e.g., to ``0.25``). Check if the query matches the item’s name in the language you expect.
  * - **Data seems stale / not updating**
    - Reduce stale_time or call ``sync(force=True)``. Verify ``lookup.state.uptodate`` is True.
  * - **High memory usage**
    - Decrease ``asset_capacity`` and ``asset_ttl``. The cache stores JSON and PNG in RAM.
  * - **Sync is slow on startup**
    - Expected for first sync (1‑10 seconds). Provide a GitHub token to increase download speed by reducing authentication checks and lift rate limits.
  * - **Methods** ``item_info()`` / ``item_icon()`` **are slow**
    - These methods download files from GitHub. Ensure a token is provided and consider caching results in your application.


----------------------------------------
⏩ What's Next
----------------------------------------

Continue with:

- :doc:`API Clients Guide <client>` – Use tokens with AppClient and UserClient.
- :doc:`Authentication Guide <oauth>` – Register application and get tokens
- :doc:`Error Handling <errors>` – Handle exceptions and rate limits
- :doc:`Examples <../examples/index>` – Complete usage examples
