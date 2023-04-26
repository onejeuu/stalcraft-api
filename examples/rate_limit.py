from stalcraft import AppClient


TOKEN = "YOUR_TOKEN"


client = AppClient(token=TOKEN)


# ? To obtain information about the current rate limit values, you can use client.ratelimit
# ! Warning: by default client.ratelimit is None until the first request is made (except for regions), so use caution

print(client.ratelimit)
# Output: None

client.emission()

print(client.ratelimit)
# Output: RateLimit(limit=200, remaining=199, reset=datetime.datetime(2023, 2, 23, 12, 0, 0, tzinfo=...))
