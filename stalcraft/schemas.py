from datetime import datetime
import json
import os

from . import Rank


class BaseSchema:
    def datetime(self, string: str, default=None):
        try:
            return datetime.fromisoformat(string)

        except Exception:
            return default

    def _compare(self, other, method):
        if isinstance(other, self.__class__):
            return method(self, other)
        return False

    @property
    def key(self):
        return list(self.__dict__.keys())[0]

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s.__dict__ == o.__dict__)

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s.key < o.key)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s.key <= o.key)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s.key > o.key)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s.key >= o.key)

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return f"{self.__class__.__name__}({', '.join(kws)})"

    def __rich_repr__(self):
        for key, value in self.__dict__.items():
            yield key, value


class RateLimit:
    def __init__(self, response):
        self.limit = response.headers.get("X-RateLimit-Limit")
        self.remaining = response.headers.get("X-RateLimit-Remaining")
        self.reset = datetime.fromtimestamp(response.headers.get("X-RateLimit-Reset"))


class RegionInfo(BaseSchema):
    def __init__(self, region):
        self.id = region.get("id")
        self.name = region.get("name")


class Emission(BaseSchema):
    def __init__(self, response):
        self.current_start = self.datetime(response.get("currentStart"))
        self.previous_start = self.datetime(response.get("previousStart"))
        self.previous_end = self.datetime(response.get("previousEnd"))


class ClanInfo(BaseSchema):
    def __init__(self, clan):
        self.id = clan.get("id")
        self.name = clan.get("name")
        self.tag = clan.get("tag")
        self.level = clan.get("level")
        self.level_points = clan.get("levelPoints")
        self.registration_time = self.datetime(clan.get("registrationTime"))
        self.alliance = clan.get("alliance")
        self.description = clan.get("description")
        self.leader = clan.get("leader")
        self.member_count = clan.get("memberCount")

    @property
    def key(self):
        return self.name


class CharacterInfo(BaseSchema):
    def __init__(self, info):
        self.id = info.get("id")
        self.name = info.get("name")
        self.creation_time = self.datetime(info.get("creationTime"))

    @property
    def key(self):
        return self.name


class ClanMember(BaseSchema):
    def __init__(self, member):
        self.name = member.get("name")
        self.rank = Rank[member.get("rank")]
        self.join_time = self.datetime(member.get("joinTime"))

    @property
    def key(self):
        return self.name


class CharacterClan(BaseSchema):
    def __init__(self, clan):
        clan_info = clan.get("info", {})
        clan_member = clan.get("member", {})

        self.info = ClanInfo(clan_info)
        self.member = ClanMember(clan_member)


class Character(BaseSchema):
    def __init__(self, character):
        info = character.get("information", {})
        self.info = CharacterInfo(info)

        clan = character.get("clan", {})
        self.clan = CharacterClan(clan) if clan else None


class CharacterStatistic(BaseSchema):
    def __init__(self, stat):
        self.id = stat.get("id")
        self.type = stat.get("type")
        self.value = stat.get("value")



class CharacterProfile(BaseSchema):
    def __init__(self, response):
        self.username = response.get("username")
        self.uuid = response.get("uuid")
        self.status = response.get("status")
        self.alliance = response.get("alliance")
        self.last_login = self.datetime(response.get("lastLogin"))
        self.displayed_achievements = response.get("displayedAchievements")

        clan = response.get("clan", {})
        self.clan = CharacterClan(clan) if clan else None

        self.stats = [
            CharacterStatistic(stat)
            for stat in response.get("stats", [])
        ]


class Price(BaseSchema):
    def __init__(self, price):
        self.amount = price.get("amount")
        self.price = price.get("price")
        self.time = self.datetime(price.get("time"))
        self.additional = price.get("additional")

    @property
    def key(self):
        return self.price


class Lot(BaseSchema):
    def __init__(self, lot):
        self.item_id = lot.get("itemId")
        self.amount = lot.get("amount")
        self.start_price = lot.get("startPrice")
        self.current_price = lot.get("currentPrice", self.start_price)
        self.buyout_price = lot.get("buyoutPrice")
        self.start_time = self.datetime(lot.get("startTime"))
        self.end_time = self.datetime(lot.get("endTime"))
        self.additional = lot.get("additional")

    @property
    def key(self):
        return self.buyout_price
