import warnings
from functools import wraps
from typing import Any, Callable, Iterator, TypeAlias

from scapi.enums import IndexFile


Entity: TypeAlias = dict[str, Any]
Data: TypeAlias = list[Entity]
Rows: TypeAlias = Iterator[tuple[str, Entity, list[str]]]
Parser: TypeAlias = Callable[[Any], Rows]

_PARSERS: dict[str, Parser] = {}


def get(path: str) -> Parser:
    """Retrieve parser for file path."""

    filename = path.split("/")[-1]

    if filename not in _PARSERS:
        warnings.warn(f"Unknown file type: '{path}'")
        return lambda _: iter(())  # type: ignore

    return _PARSERS[filename]


def _register(filename: str):
    def decorator(func: Parser) -> Parser:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        _PARSERS[filename] = wrapper
        return wrapper

    return decorator


@_register(IndexFile.LISTING)
def _listings(data: Data):
    for item in data:
        path = item["data"]
        entity_id = path.split("/")[-1].replace(".json", "")
        yield (entity_id, item, _extract(item, "name"))


@_register(IndexFile.STATS)
def _stats(data: Data):
    for item in data:
        entity_id = item["id"]
        yield (entity_id, item, _extract(item, "name"))


@_register(IndexFile.ACHIEVEMENTS)
def _achievements(data: Data):
    for item in data:
        entity_id = item["id"]
        yield (entity_id, item, _extract(item, "title"))  # "description"


def _extract(item: Any, *fields: str):
    return [text for field in fields for text in _translations(item, field)]


def _translations(item: Any, field: str) -> list[str]:
    translation = item.get(field, {})

    match translation.get("type"):
        case "translation":
            lines: dict[str, str] = translation.get("lines", {})
            return [text for text in lines.values() if text]
        case "text":
            text = translation.get("text", "")
            return [text] if text else []

    return []
