from stalcraft.asyncio import AsyncUserClient
from stalcraft import BaseUrl, Region
import asyncio


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"

NICKNAME = "Test-1"
CLAN_ID = "647d6c53-b3d7-4d30-8d08-de874eb1d845"


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
