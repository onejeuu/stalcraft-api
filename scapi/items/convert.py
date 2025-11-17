import asyncio
import json
from typing import Any, NamedTuple, TypeAlias

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.enums import Realm

from . import models


JSON: TypeAlias = dict[str, Any]

Rows: TypeAlias = dict[tuple, models.ScDatabaseModel]


class DatabaseFile(NamedTuple):
    realm: str
    data: Any


class DatabaseNormalizer:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._rows: Rows = {}

    async def convert(self):
        await asyncio.gather(
            *[
                self._parse_listing(),
                self._parse_stats(),
                self._parse_achievements(),
                self._parse_barter(),
            ]
        )

        self._session.add_all(self._rows.values())

    async def _parse_listing(self):
        KEY = str(models.ItemListing.__tablename__)

        async for realm, data in self._load("listing.json"):
            for item in data:
                entity_id = item["data"].split("/")[-1].replace(".json", "")

                key = (KEY, realm, entity_id)
                self._rows[key] = models.ItemListing(
                    id=entity_id,
                    realm=realm,
                    color=item["color"],
                    state=item["status"]["state"],
                )

                self._parse_translation(item, KEY, entity_id, field="name")

    async def _parse_stats(self):
        KEY = str(models.ItemStatistic.__tablename__)

        async for realm, data in self._load("stats.json"):
            for item in data:
                entity_id = item["id"]

                key = (KEY, realm, entity_id)
                self._rows[key] = models.ItemStatistic(
                    id=entity_id,
                    realm=realm,
                    category=item["category"],
                    type=item["type"],
                )

                self._parse_translation(item, KEY, entity_id, field="name")

    async def _parse_achievements(self):
        KEY = str(models.ItemAchievement.__tablename__)

        async for realm, data in self._load("achievements.json"):
            for item in data:
                entity_id = item["id"]

                key = (KEY, realm, entity_id)
                self._rows[key] = models.ItemAchievement(
                    id=entity_id,
                    realm=realm,
                    points=item["points"],
                )

                self._parse_translation(item, KEY, entity_id, field="title")
                self._parse_translation(item, KEY, entity_id, field="description")

    async def _parse_barter(self):
        KEY = str(models.Settlement.__tablename__)

        async for realm, data in self._load("barter_recipes.json"):
            for item in data:
                entity_id = item["settlementTitle"]["key"].split(".")[2]

                key = (KEY, realm, entity_id)
                self._rows[key] = models.Settlement(
                    id=entity_id,
                    realm=realm,
                )

                self._parse_translation(item, KEY, entity_id, field="settlementTitle")

                await self._parse_barter_recipes(item["recipes"], realm, entity_id)

    async def _parse_barter_recipes(self, recipes: list[JSON], realm: str, settlement_id: str):
        KEY = str(models.BarterRecipe.__tablename__)

        for item in recipes:
            item_id = item["item"]
            key = (KEY, realm, settlement_id, item_id)
            self._rows[key] = models.BarterRecipe(
                item_id=item_id,
                realm=realm,
                settlement_id=settlement_id,
                required_level=item["settlementRequiredLevel"],
            )

            await self._parse_barter_offers(item["offers"], realm, item_id, settlement_id)

    async def _parse_barter_offers(self, offers: list[JSON], realm: str, item_id: str, settlement_id: str):
        KEY = str(models.BarterOffer.__tablename__)

        for index, item in enumerate(offers, start=1):
            key = (KEY, realm, settlement_id, item_id, index)
            self._rows[key] = models.BarterOffer(
                item_id=item_id,
                realm=realm,
                settlement_id=settlement_id,
                index=index,
                cost=item["cost"],
                currency=item["currency"],
            )

            await self._parse_barter_requirements(item["requiredItems"], realm, item_id, settlement_id)

    async def _parse_barter_requirements(self, requirements: list[JSON], realm: str, item_id: str, settlement_id: str):
        KEY = str(models.BarterRequirement.__tablename__)

        for item in requirements:
            required_item_id = item["item"]
            key = (KEY, realm, item_id, required_item_id)
            self._rows[key] = models.BarterRequirement(
                item_id=item_id,
                realm=realm,
                settlement_id=settlement_id,
                required_item_id=required_item_id,
                amount=item["amount"],
            )

    def _parse_translation(self, item: JSON, entity_type: str, entity_id: str, field: str):
        if item[field]["type"] == "translation":
            for lang, text in item[field]["lines"].items():
                key = ("translation", lang, entity_id)
                self._rows[key] = models.Translation(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    field=field,
                    language=lang,
                    text=text,
                )

    async def _load(self, filename: str):
        files = {f"{r.value}/{filename}": r.lower() for r in Realm}

        query = select(models.FileBlob).where(col(models.FileBlob.path).in_(files.keys()))
        blobs = await self._session.exec(query)

        for blob in blobs:
            yield DatabaseFile(files[blob.path], json.loads(blob.content))
