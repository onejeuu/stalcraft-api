import hashlib

from sqlalchemy.schema import CreateTable

from . import models


def checksum() -> str:
    ddl = "".join(str(CreateTable(table).compile()) for base in models.BASES for table in base.metadata.sorted_tables)
    return hashlib.md5(ddl.encode()).hexdigest()
