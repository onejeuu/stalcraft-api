from stalcraft import AppClient


# Only as example.
# Do not store your credentials in code.
TOKEN = "YOUR_TOKEN"


client = AppClient(token=TOKEN)


# ? To obtain information about the current rate limit values
# ? You can use client.ratelimit

print(client.ratelimit)
# Output: RateLimit(limit=None, remaining=None, reset=None)


# ! Warning: by default client.ratelimit is empty.
# ! Until first request is made (except for client.regions).
# ! So use caution.

client.regions()
print(client.ratelimit)
# Output: RateLimit(limit=None, remaining=None, reset=None)


client.emission()
print(client.ratelimit)
# Output: RateLimit(limit=200, remaining=199, reset=datetime.datetime(2023, 1, 1, 12, 0, 0, tzinfo=...))
