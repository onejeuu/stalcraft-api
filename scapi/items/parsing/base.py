import json
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, NamedTuple, Optional, TypeAlias

from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from scapi.enums import Realm

from .. import models


Model: TypeAlias = models.ScDatabaseModel
Rows: TypeAlias = dict[tuple, Model]

RealmName: TypeAlias = str
JSON: TypeAlias = dict[str, Any]
Item: TypeAlias = tuple[RealmName, JSON]


class ItemContext(NamedTuple):
    item: JSON
    realm: str
    entity_id: str


class BaseParser(ABC):
    filename: str
    model: type[Model]

    id_field: str = "id"
    translation_fields: Optional[list[str]] = None

    def __init__(self, session: AsyncSession, rows: Rows):
        self._session = session
        self._rows = rows

    @property
    def key(self) -> str:
        return str(self.model.__tablename__)

    @abstractmethod
    def create_entity(self, ctx: ItemContext) -> Any:
        pass

    async def parse_children(self, ctx: ItemContext):
        pass

    def extract_id(self, item: JSON) -> str:
        return str(item[self.id_field])

    async def parse(self):
        async for realm, data in self._load_file(self.filename):
            for item in data:
                await self.parse_item(item, realm)

    async def parse_item(self, item: JSON, realm: str):
        entity_id = self.extract_id(item)

        # Create item context
        ctx = ItemContext(item=item, realm=realm, entity_id=entity_id)

        # Parse main entity
        entity = self.create_entity(ctx)
        if entity:
            key = (self.key, realm, entity_id)
            self._rows[key] = entity

        # Parse translations
        if self.translation_fields:
            for field_name in self.translation_fields:
                self._parse_translation(ctx, field_name)

        # Parse embed data
        await self.parse_children(ctx)

    def _parse_translation(self, ctx: ItemContext, field_name: str):
        data = ctx.item[field_name]

        match data.get("type"):
            case "translation":
                text_items = data["lines"].items()

            case "text":
                text_items = [("any", data["text"])]

            case _:
                return

        for lang, text in text_items:
            key = ("translation", lang, ctx.entity_id)
            self._rows[key] = models.Translation(
                entity_type=self.key,
                entity_id=ctx.entity_id,
                field=field_name,
                language=lang,
                text=text,
            )

    async def _load_file(self, filename: str) -> AsyncIterator[tuple]:
        files = {f"{r.value}/{filename}": r.lower() for r in Realm}

        query = select(models.FileBlob).where(col(models.FileBlob.path).in_(files.keys()))
        blobs = await self._session.exec(query)

        for blob in blobs:
            yield files[blob.path], json.loads(blob.content)
