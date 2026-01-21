Database Lookup
==================================================

The **STALCRAFT API** uses internal identifiers like ``"zyv9"``, but applications typically need to **search by item names**.
``DatabaseLookup`` solves this by maintaining a **local**, **synchronized copy** of the official game database with **fuzzy search** capabilities.


✨ Key Features
^^^^^^^^^^^^^^^^

- ``🔗`` **Synchronization:** with the official `stalcraft-database repository <https://github.com/EXBO-Studio/stalcraft-database/>`_
- ``🔍`` **Fuzzy search:** handling typos and partial matches
- ``⚡`` **In-memory caching:** for instant queries (~0.0001 seconds after sync)
- ``📦`` **Multiple data types**: items, achievements, and character stats
- ``🔄`` **Lazy updates:** checks for changes when requested (configurable interval)


🛠️ How It Works
^^^^^^^^^^^^^^^^

``DatabaseLookup`` **downloads compressed JSON indexes** on first use and caches them in memory.
Searches use **fuzzy matching** for typos and partial names. When the configured TTL expires, the next request **automatically updates the cache** if the remote database has changed.


📌 When to Use
^^^^^^^^^^^^^^^

Use ``DatabaseLookup`` to convert names to API internal IDs, build search functionality, or retrieve detailed item information and icons.