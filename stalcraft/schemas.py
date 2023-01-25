from datetime import datetime

from . import Rank


class BaseSchema:
    def datetime(self, string: str):
        try:
            return datetime.fromisoformat(string)

        except Exception:
            return None

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        kws = [f"{key}={value!r}" for key, value in self.__dict__.items()]
        return "{}({})".format(type(self).__name__, ", ".join(kws))

    def __rich_repr__(self):
        for key, value in self.__dict__.items():
            yield key, value


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


class Clans(BaseSchema):
    def __init__(self, response):
        self.total = response.get("total", 0)

        self.clans = [
            ClanInfo(clan) for clan in response.get("data", [{}])
        ]


class CharacterInfo(BaseSchema):
    def __init__(self, info):
        self.id = info.get("id")
        self.name = info.get("name")
        self.creation_time = self.datetime(info.get("creationTime"))


class ClanMember(BaseSchema):
    def __init__(self, member):
        self.name = member.get("name")
        self.rank = Rank[member.get("rank")]
        self.join_time = self.datetime(member.get("joinTime"))


class CharacterClan(BaseSchema):
    def __init__(self, clan):
        clan_info = clan.get("info", {})
        clan_member = clan.get("member", {})

        self.info = ClanInfo(clan_info)
        self.member = ClanMember(clan_member)


class Character(BaseSchema):
    def __init__(self, character):
        info = character.get("information", {})
        clan = character.get("clan", {})

        self.info = CharacterInfo(info)
        self.clan = CharacterClan(clan)


class Price(BaseSchema):
    def __init__(self, price):
        self.amount = price.get("amount")
        self.price = price.get("price")
        self.time = self.datetime(price.get("time"))
        self.additional = price.get("additional")


class Prices(BaseSchema):
    def __init__(self, response):
        self.total = response.get("total", 0)

        self.prices = [
            Price(price) for price in response.get("prices", [{}])
        ]


class Lot(BaseSchema):
    def __init__(self, lot):
        self.item_id = lot.get("itemId")
        self.start_price = lot.get("startPrice")
        self.current_price = lot.get('currentPrice')
        self.buyout_price = lot.get("buyoutPrice")
        self.start_time = self.datetime(lot.get("startTime"))
        self.end_time = self.datetime(lot.get("endTime"))
        self.additional = lot.get("additional")


class Lots(BaseSchema):
    def __init__(self, response):
        self.total = response.get("total", 0)

        self.lots = [
            Lot(lots) for lots in response.get("lots", [{}])
        ]
