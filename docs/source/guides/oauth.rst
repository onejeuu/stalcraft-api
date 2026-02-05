Authentication
==================================================

| This guide explains how to obtain authentication tokens for the STALCRAFT API.
| You'll learn about ``App Tokens`` for **public** data and ``User Tokens`` (via OAuth 2.0) for **private** player data.

.. note::

  | **Production access requires application registration and moderation approval**.
  | Use the **Demo API** for immediate testing without waiting.


----------------------------------------
🧪 Demo API for Testing
----------------------------------------

You can test the library immediately using pre-generated demo tokens from the `official documentation <https://eapi.stalcraft.net/overview.html#demo-api>`_.
These work only with the **Demo API** endpoint (``https://dapi.stalcraft.net``).

.. code-block:: python

  from scapi import AppClient, UserClient, BaseUrl

  # Test public endpoints with demo app token
  client = AppClient(token="...", base_url=BaseUrl.DEMO)

  # Test private endpoints with demo user token
  user = UserClient(token="...", base_url=BaseUrl.DEMO)


.. admonition:: Limitations
  :class: important

  **Demo tokens cannot be used in OAuth flows, be refreshed, and may not work with all endpoints.** For full functionality, you'll need to register your application.


----------------------------------------
🪪 Application Registration
----------------------------------------

Production API access requires registering an application through the **official Telegram bot**.

Registration Process
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. **Access the bot**: `@stalcraft_api_bot <https://t.me/stalcraft_api_bot>`_ in Telegram
2. **Authenticate with your EXBO account**
3. **Create application**: Use the ``/newapp`` command
4. Provide details:
    - **Application name**
    - **Redirect URI:** Must match your OAuth callback URL (e.g., ``http://localhost:8080/callback``)
    - **Purpose:** Be specific (e.g., ``"Clan statistics service"``, not just ``"Testing"``)
5. **Submit and wait for manual approval**: Processing time varies (days to weeks)

| Upon approval, you'll receive credentials: ``client_id`` and ``client_secret``.
| Use ``/myapps`` to view or edit your applications.


----------------------------------------
🔑 Working with OAuthClient
----------------------------------------

The ``OAuthClient`` handles all authentication flows. Initialize it with your credentials.

.. code-block:: python
  :caption: Create OAuth Client

  from scapi import OAuthClient
  import os

  oauth = OAuthClient(
    client_id=os.getenv("CLIENT_ID"),
    client_secret=os.getenv("CLIENT_SECRET"),
    redirect_uri="http://localhost:8080/callback", # MUST match application URI
  )


----------------------------------------
📡 App Token
----------------------------------------


.. admonition:: Token Replacement
  :class: caution

  Each successful call to ``get_app_token()`` or ``get_user_token()`` **invalidates all previously issued tokens** for that same application (or user).
  Avoid unnecessary token regeneration. Store tokens securely and reuse them until they expire or are revoked.


App tokens authenticate your application for **public data** (auctions, emissions, public profiles).

.. code-block:: python
  :caption: Get App Token

  token = await oauth.get_app_token()
  print(f"Token: {token.access_token}")
  print(f"Expires: {token.expires_in}")


Use this token with ``AppClient`` to access public endpoints.


----------------------------------------
🔐 User Token Flow
----------------------------------------

| User tokens provide access to both **public and private data** (characters, friends, clan membership).
| They require user authorization via **OAuth 2.0**.

**Flow steps:**

1. **Generate Authorization URL**

   .. code-block:: python

    import secrets

    # Optional (Recommended): Generate state for CSRF protection
    # Store state securely for later verification
    state = secrets.token_urlsafe(16)

    auth_url = oauth.get_authorize_url(state=state)
    print(f"Open in browser: {auth_url}")

   The ``state`` parameter prevents `CSRF attacks <https://en.wikipedia.org/wiki/Cross-site_request_forgery>`_. Verify it matches when handling user callback.

2. **Handle Callback and Exchange Code**

   | After authorization, users are redirected to your ``redirect_uri`` with ``code`` (and ``state`` if you provided it).
   | If the returned ``state`` doesn't match your original -- **ignore the request**.

   .. code-block:: python

    # For demonstration: Manually paste the code
    # In production extract code automatically from callback URL
    code = input("Enter authorization code from URL: ")

    # Exchange code to token (immediately)
    user_token = await oauth.get_user_token(code=code)

    print(f"Access Token: {user_token.access_token}")
    print(f"Refresh Token: {user_token.refresh_token}")
    print(f"Expires In: {user_token.expires_in}")


Use this token with ``UserClient`` to access public and player-specific endpoints.


----------------------------------------
🔄 User Token Refresh
----------------------------------------

User tokens expire after *approximately* **12 months**. Refresh them before expiration using the ``refresh_token``.

.. code-block:: python
  :caption: Refresh User Token

  new_token = await oauth.refresh_user_token(refresh_token=user_token.refresh_token)

  print(f"New Access Token: {new_token.access_token}")
  print(f"New Refresh Token: {new_token.refresh_token}")


.. note::

  The refresh token itself is also updated. Store the new refresh token for future use.


----------------------------------------
✅ User Token Validation
----------------------------------------

You can validate user tokens and retrieve basic account information.

.. code-block:: python
  :caption: Validate User Token

  user = await oauth.validate_user_token(token=user_token.access_token)

  print(f"User ID: {user.id}")
  print(f"User Login: {user.login}")
  print(f"Distributor: {user.distributor}")

Use this to verify token validity and identify the authenticated user.


----------------------------------------
🚨 Common Issues
----------------------------------------

.. list-table::
  :header-rows: 1

  * - Problem
    - Solution
  * - **No callback redirect after user authorization**
    - Ensure ``redirect_uri`` exactly matches your registered application URI.
  * - **Authorization code expired**
    - Use authorization codes immediately. They expire quickly.
  * - **Application not approved**
    - Production access requires manual approval. Use Demo API while waiting.
  * - **Token stops working**
    - New created tokens invalidate previous ones. Ensure you not published your application credentials.


----------------------------------------
⏩ What's Next
----------------------------------------

Continue with:

- :doc:`API Clients Guide <client>` – Use tokens with AppClient and UserClient.
- :doc:`Database Lookup <database>` – Find items IDs by name
