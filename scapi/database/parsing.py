import asyncio
import json
from typing import Any, AsyncIterator, TypeAlias

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.enums import Realm

from . import models


BaseModel = models.ScDatabaseModel
Rows: TypeAlias = dict[tuple, BaseModel]


async def normalize(session: AsyncSession) -> Rows:
    rows: Rows = {}

    await asyncio.gather(
        _parse_listings(session, rows),
        _parse_stats(session, rows),
        _parse_achievements(session, rows),
        _parse_barter(session, rows),
    )

    return rows


def _tablename(model: type[BaseModel]) -> str:
    return str(model.__tablename__)


async def _load_file(session: AsyncSession, filename: str) -> AsyncIterator[tuple[str, Any]]:
    realms = {f"{r}/{filename}": str(r) for r in Realm}
    query = select(models.FileBlob).where(col(models.FileBlob.path).in_(realms.keys()))

    for blob in await session.exec(query):
        yield realms[blob.path], json.loads(blob.content)


async def _parse_listings(session: AsyncSession, rows: Rows):
    model = models.ItemListing
    tablename = _tablename(model)

    async for realm, items in _load_file(session, "listing.json"):
        for data in items:
            entity_id = data["data"].split("/")[-1].replace(".json", "")

            rows[(tablename, realm, entity_id)] = model(
                realm=realm,
                id=entity_id,
                color=data["color"],
                state=data["status"]["state"],
            )

            await _parse_translation(rows, tablename, entity_id, data, "name")


async def _parse_stats(session: AsyncSession, rows: Rows):
    model = models.ItemStatistic
    tablename = _tablename(model)

    async for realm, items in _load_file(session, "stats.json"):
        for data in items:
            entity_id = data["id"]

            rows[(tablename, realm, entity_id)] = model(
                realm=realm,
                id=entity_id,
                category=data["category"],
                type=data["type"],
            )

            await _parse_translation(rows, tablename, entity_id, data, "name")


async def _parse_achievements(session: AsyncSession, rows: Rows):
    model = models.ItemAchievement
    tablename = _tablename(model)

    async for realm, items in _load_file(session, "achievements.json"):
        for data in items:
            entity_id = data["id"]

            rows[(tablename, realm, entity_id)] = model(
                realm=realm,
                id=entity_id,
                points=data["points"],
            )

            await _parse_translation(rows, tablename, entity_id, data, "title")
            await _parse_translation(rows, tablename, entity_id, data, "description")


async def _parse_barter(session: AsyncSession, rows: Rows):
    async for realm, items in _load_file(session, "barter_recipes.json"):
        for data in items:
            await _parse_settlement(rows, realm, data)


async def _parse_settlement(rows: Rows, realm: str, data: Any):
    model = models.Settlement
    tablename = _tablename(model)

    settlement_id = data["settlementTitle"]["key"].split(".")[2]

    rows[(tablename, realm, settlement_id)] = model(
        realm=realm,
        id=settlement_id,
    )

    await _parse_translation(rows, tablename, settlement_id, data, "settlementTitle")
    await _parse_recipes(rows, realm, data["recipes"], settlement_id)


async def _parse_recipes(rows: Rows, realm: str, recipes: list[Any], settlement_id: str):
    model = models.BarterRecipe
    tablename = _tablename(model)

    for data in recipes:
        item_id = data["item"]

        rows[(tablename, realm, settlement_id, item_id)] = model(
            realm=realm,
            item_id=item_id,
            settlement_id=settlement_id,
            required_level=data["settlementRequiredLevel"],
        )

        await _parse_offers(rows, realm, data["offers"], settlement_id, item_id)


async def _parse_offers(rows: Rows, realm: str, offers: list[Any], settlement_id: str, item_id: str):
    model = models.BarterOffer
    tablename = _tablename(model)

    for index, data in enumerate(offers, start=1):
        rows[(tablename, realm, settlement_id, item_id, str(index))] = model(
            realm=realm,
            item_id=item_id,
            settlement_id=settlement_id,
            index=index,
            cost=data["cost"],
            currency=data["currency"],
        )

        await _parse_requirements(rows, realm, data["requiredItems"], settlement_id, item_id)


async def _parse_requirements(rows: Rows, realm: str, requirements: list[Any], settlement_id: str, recipe_id: str):
    model = models.BarterRequirement
    tablename = _tablename(model)

    for data in requirements:
        required_item_id = data["item"]

        rows[(tablename, realm, recipe_id, required_item_id)] = model(
            realm=realm,
            item_id=recipe_id,
            settlement_id=settlement_id,
            required_item_id=required_item_id,
            amount=data["amount"],
        )


async def _parse_translation(rows: Rows, entity_type: str, entity_id: str, data: Any, field_name: str):
    model = models.Translation
    tablename = _tablename(model)

    translation = data.get(field_name, {})

    match translation.get("type"):
        case "translation":
            text_items = translation["lines"].items()
        case "text":
            text_items = [("any", translation["text"])]
        case _:
            return

    for lang, text in text_items:
        rows[(tablename, lang, entity_id)] = model(
            entity_type=entity_type,
            entity_id=entity_id,
            field=field_name,
            language=lang,
            text=text,
        )
