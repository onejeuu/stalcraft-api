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