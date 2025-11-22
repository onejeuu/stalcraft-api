import hashlib
from typing import Any

from . import models


def checksum() -> str:
    tables: list[str] = []

    def toint(value: Any):
        return int(bool(value))

    for base in models.BASES:
        for table in base.metadata.sorted_tables:
            cols = [
                f"{col.name}:{col.type}:{toint(col.nullable)}:{toint(col.primary_key)}:{toint(col.default)}"
                for col in table.columns
            ]
            idxs = [f"idx:{','.join(c.name for c in idx.columns)}" for idx in table.indexes]
            fks = [f"fk:{fk.column.table.name}.{fk.column.name}" for fk in table.foreign_keys]
            tables.append(f"{table.name}({';'.join(cols)})({';'.join(idxs)})({';'.join(fks)})")

    flat = "&".join(sorted(tables))

    return hashlib.md5(flat.encode()).hexdigest()
