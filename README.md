# stalcraft-api unofficial python library

📄 **Официальная документация API:** https://eapi.stalcraft.net

ℹ️ **Для использования полноценной версии API вы должны пройти верификацию от EXBO**

[`подробнее`](https://eapi.stalcraft.net/registration.html)


<br>

# Установка

```console
pip install stalcraft-api --upgrade
```


<br>

# Quick Start

```python
from stalcraft import Client, ApiLink

TOKEN = "YOUR_TOKEN"

client = Client(TOKEN, ApiLink.PRODUCTION)
```

<br>

# Примеры использования


```python
from stalcraft import Client, Region, Sort, Order

TOKEN = "YOUR_TOKEN"

client = Client(TOKEN)

print()
print("List of regions")
print(client.regions())

print()
print("List of characters on EU server")
print(client.characters(Region.EU))

print()
print("List of clans with offset 1 and limit 2")
print(client.clans(offset=1, limit=2))

print()
print("Information about emission")
print(client.emission())

print()
print("List of friends character Test-1")
print(client.friends("Test-1"))

item = client.auction("y1q9")

print()
print("List of lots item with id y1q9 with offset 5 and limit 2 and sort by buyout price")
print(item.lots(offset=5, limit=2, sort=Sort.BUYOUT_PRICE))

print()
print("List of history item with id y1q9")
print(client.auction("y1q9").history())

clan = client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845")

print()
print("Information about clan with id 647d6c53-b3d7-4d30-8d08-de874eb1d845")
print(clan.info())

print()
print("Members in clan with id 647d6c53-b3d7-4d30-8d08-de874eb1d845")
print(client.clan("647d6c53-b3d7-4d30-8d08-de874eb1d845").members())
```

<br>

# Поиск ID предмета

```python
from stalcraft import Client, Item

TOKEN = "YOUR_TOKEN"

client = Client(TOKEN)

print(client.auction(Item("Гадюка").item_id).lots())
```
