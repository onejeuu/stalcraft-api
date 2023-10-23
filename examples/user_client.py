from stalcraft import UserClient, Region


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"

NICKNAME = "Test-1"
CLAN_ID = "647d6c53-b3d7-4d30-8d08-de874eb1d845"


client = UserClient(token=TOKEN)


# + All methods from AppClient

print("List of characters created by the user on EU server by which used access token was provided")
print(client.characters(Region.EU))

print()
print(f"List of friends character names who are friend with '{NICKNAME}'")
print(client.friends(NICKNAME))

# ! Can be used only when using user access token
# ! And that user has at least one character in that clan
print(f"Members in clan with id '{CLAN_ID}'")
print(client.clan(CLAN_ID).members())

# ! Not working in DEMO API
print("Information about player's profile")
print("Includes alliance, profile description, last login time, stats, etc.")
print(client.character_profile("ZIV"))
