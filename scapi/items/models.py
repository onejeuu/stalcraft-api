from sqlmodel import Field, SQLModel


class Metadata(SQLModel, table=True):
    __tablename__ = "metadata"  # type: ignore

    key: str = Field(primary_key=True)
    value: str


class FileBlob(SQLModel, table=True):
    __tablename__ = "repository"  # type: ignore

    path: str = Field(primary_key=True)
    content: bytes
    size: int

