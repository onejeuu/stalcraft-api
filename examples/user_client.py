from stalcraft import UserClient, BaseUrl, Region


TOKEN = "YOUR_TOKEN"


client = UserClient(token=TOKEN, base_url=BaseUrl.DEMO)


# + All Methods From AppClient

print("List of characters created by the user on EU server by which used access token was provided")
print(client.characters(Region.EU))

print()
print("List of friends character names who are friend with 'Test-1'")
print(client.friends("Test-1"))

# ! Can be used only when using user access token and that user has at least one character in that clan
print("Members in clan with id '562968e7-4282-4ac6-900f-f7f1581495e8'")
print(client.clan("562968e7-4282-4ac6-900f-f7f1581495e8").members())

# ! Not working in DEMO API
print("Information about player's profile")
print("Includes alliance, profile description, last login time, stats, etc.")
print(client.character_profile("ZIV"))
