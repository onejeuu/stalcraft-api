import hashlib

from . import models


def generate() -> str:
    tables: list[str] = []

    for base in [models.BaseModel, models.ScDatabaseParsed]:
        for table in base.metadata.sorted_tables:
            cols = [f"{col.name}:{col.type}" for col in table.columns]
            tables.append(f"{table.name}({','.join(sorted(cols))})")

    flat = "|".join(sorted(tables))

    return hashlib.md5(flat.encode()).hexdigest()
