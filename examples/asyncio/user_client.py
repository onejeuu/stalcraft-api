import asyncio

from stalcraft import BaseUrl, Region
from stalcraft.asyncio import AsyncUserClient


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"

NICKNAME = "REPLACE_ME"
CLAN_ID = "5ea2c08c-23f7-4366-98b8-40292267a03f"


async def main():
    client = AsyncUserClient(token=TOKEN, base_url=BaseUrl.DEMO)

    # + All methods from AsyncAppClient

    print("List of characters created by the user on EU server by which used access token was provided")
    print(await client.characters(Region.EU))

    print()
    print(f"List of friends character names who are friend with '{NICKNAME}'")
    print(await client.friends(NICKNAME))

    # ! Can be used only when using user access token
    # ! And that user has at least one character in that clan
    print(f"Members in clan with id '{CLAN_ID}'")
    print(await client.clan(CLAN_ID).members())

    # ! Not working in DEMO API
    print("Information about player's profile")
    print("Includes alliance, profile description, last login time, stats, etc.")
    print(await client.character_profile("ZIV"))


asyncio.run(main())
