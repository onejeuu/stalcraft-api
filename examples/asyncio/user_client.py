import asyncio

from stalcraft.asyncio import AsyncUserClient


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"

CHARACTER = "REPLACE_ME"
CLAN_ID = "5ea2c08c-23f7-4366-98b8-40292267a03f"


async def main():
    client = AsyncUserClient(token=TOKEN)

    print("+ All methods from App Client")
    print("List of clans with limit 2")
    print(await client.clans(limit=2))

    print("List of characters created by the user on RU server by which used access token was provided")
    print(await client.characters())

    # ! CHARACTER must be one of characters whose token is provided
    print()
    print(f"List of friends character names who are friend with '{CHARACTER}'")
    print(client.friends(CHARACTER))

    # ! Not working in DEMO API
    print("Information about player's profile")
    print("Includes alliance, profile description, last login time, stats, etc.")
    print(await client.character_profile("ZIV"))

    # ! Can be used only when using user access token
    # ! And that user has at least one character in that clan
    print(f"Members in clan with id '{CLAN_ID}'")
    print(await client.clan(CLAN_ID).members())


asyncio.run(main())
