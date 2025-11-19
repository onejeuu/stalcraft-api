from .. import models
from .base import JSON, BaseParser, ItemContext


class ListingParser(BaseParser):
    filename = "listing.json"
    model = models.ItemListing

    translation_fields = ["name"]

    def extract_id(self, item: JSON) -> str:
        return item["data"].split("/")[-1].replace(".json", "")

    def create_entity(self, ctx: ItemContext):
        return models.ItemListing(
            id=ctx.entity_id,
            realm=ctx.realm,
            color=ctx.item["color"],
            state=ctx.item["status"]["state"],
        )


class StatsParser(BaseParser):
    filename = "stats.json"
    model = models.ItemStatistic

    translation_fields = ["name"]

    def create_entity(self, ctx: ItemContext):
        return models.ItemStatistic(
            id=ctx.entity_id,
            realm=ctx.realm,
            category=ctx.item["category"],
            type=ctx.item["type"],
        )


class AchievementsParser(BaseParser):
    filename = "achievements.json"
    model = models.ItemAchievement

    translation_fields = ["title", "description"]

    def create_entity(self, ctx: ItemContext):
        return models.ItemAchievement(
            id=ctx.entity_id,
            realm=ctx.realm,
            points=ctx.item["points"],
        )


class BarterParser(BaseParser):
    filename = "barter_recipes.json"
    model = models.Settlement

    translation_fields = ["settlementTitle"]

    def extract_id(self, item: JSON) -> str:
        return item["settlementTitle"]["key"].split(".")[2]

    def create_entity(self, ctx: ItemContext):
        return models.Settlement(
            id=ctx.entity_id,
            realm=ctx.realm,
        )
