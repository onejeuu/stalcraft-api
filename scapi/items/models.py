from sqlmodel import Field, MetaData, SQLModel


class ScDatabaseModel(SQLModel):
    metadata = MetaData()


class Metadata(ScDatabaseModel, table=True):
    __tablename__: str = "metadata"

    key: str = Field(primary_key=True)
    value: str


class FileBlob(ScDatabaseModel, table=True):
    __tablename__: str = "repository"

    path: str = Field(primary_key=True)
    content: bytes
    size: int


class ScDatabaseParsed(ScDatabaseModel):
    metadata = MetaData()


class Translation(ScDatabaseParsed, table=True):
    __tablename__: str = "translation"

    entity_type: str = Field(primary_key=True)
    entity_id: str = Field(primary_key=True)
    field: str = Field(primary_key=True)
    language: str = Field(primary_key=True)
    text: str = Field(index=True)


class BaseItem(ScDatabaseParsed):
    id: str = Field(primary_key=True)
    realm: str = Field(primary_key=True)


class ItemListing(BaseItem, table=True):
    __tablename__: str = "listing"

    color: str = Field(default="")
    state: str = Field(default="")


class ItemStatistic(BaseItem, table=True):
    __tablename__: str = "stats"

    category: str = Field(default="")
    type: str = Field(default="")


class ItemAchievement(BaseItem, table=True):
    __tablename__: str = "achievements"

    points: int = Field(default=0)


class Settlement(BaseItem, table=True):
    __tablename__: str = "settlements"

    pass


class BaseBarter(ScDatabaseParsed):
    item_id: str = Field(primary_key=True)
    realm: str = Field(primary_key=True)

    settlement_id: str = Field(primary_key=True, foreign_key="settlements.id")


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
