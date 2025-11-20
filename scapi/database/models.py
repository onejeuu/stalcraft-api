from typing import Any, Dict

from sqlalchemy import JSON, Column
from sqlmodel import Field, MetaData, SQLModel


class BaseModel(SQLModel):
    metadata = MetaData()


class BaseParsed(SQLModel):
    metadata = MetaData()


BASES: list[type[SQLModel]] = [BaseModel, BaseParsed]


class BaseEntity(BaseParsed):
    realm: str = Field(primary_key=True)
    id: str = Field(primary_key=True)


class BaseBarter(BaseParsed):
    realm: str = Field(primary_key=True)
    item_id: str = Field(primary_key=True)
    settlement_id: str = Field(primary_key=True)


class Metadata(BaseModel, table=True):
    __tablename__: str = "metadata"

    key: str = Field(primary_key=True)
    value: str


class FileBlob(BaseModel, table=True):
    __tablename__: str = "repository"

    path: str = Field(primary_key=True)
    content: bytes
    size: int


class Translation(BaseParsed, table=True):
    __tablename__: str = "translation"

    entity_type: str = Field(primary_key=True)
    entity_id: str = Field(primary_key=True)
    field: str = Field(primary_key=True)
    language: str = Field(primary_key=True)
    text: str = Field(index=True)
    args: Dict[str, Any] = Field(sa_column=Column(JSON), default_factory=dict)


class ItemListing(BaseEntity, table=True):
    __tablename__: str = "listing"

    color: str = Field(default="")
    state: str = Field(default="")


class ItemStatistic(BaseEntity, table=True):
    __tablename__: str = "stats"

    category: str = Field(default="")
    type: str = Field(default="")


class ItemAchievement(BaseEntity, table=True):
    __tablename__: str = "achievements"

    points: int = Field(default=0)


class Settlement(BaseEntity, table=True):
    __tablename__: str = "settlements"

    pass


class BarterRecipe(BaseBarter, table=True):
    __tablename__: str = "barter_recipes"

    required_level: int = Field(default=1)


class BarterOffer(BaseBarter, table=True):
    __tablename__: str = "barter_recipe_offers"

    index: int = Field(primary_key=True)
    cost: int = Field(default=0)
    currency: str = Field(default="money")


class BarterRequirement(BaseBarter, table=True):
    __tablename__: str = "barter_recipe_requirements"

    required_item_id: str = Field(primary_key=True)
    amount: int = Field(default=1)
