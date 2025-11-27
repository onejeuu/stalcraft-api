import warnings
from functools import wraps
from typing import Any, Callable, Iterator, TypeAlias

from .enums import IndexFile


Items: TypeAlias = list[dict[str, Any]]
Texts: TypeAlias = Iterator[tuple[str, str, str]]
Parser: TypeAlias = Callable[[Any], Texts]

_PARSERS: dict[str, Parser] = {}


def get(path: str) -> Parser:
    filename = path.split("/")[-1]

    if filename not in _PARSERS:
        warnings.warn(f"Unknown file type: '{path}'")
        return lambda _: iter(())

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
def _listings(data: Items) -> Texts:
    for item in data:
        path = item["data"]
        entity_id = path.split("/")[-1].replace(".json", "")
        yield from _extract_translations(item, entity_id, fields=["name"])


@_register(IndexFile.STATS)
def _stats(data: Items) -> Texts:
    for item in data:
        entity_id = item["id"]
        yield from _extract_translations(item, entity_id, fields=["name"])


@_register(IndexFile.ACHIEVEMENTS)
def _achievements(data: Items) -> Texts:
    for item in data:
        entity_id = item["id"]
        yield from _extract_translations(item, entity_id, fields=["name", "description"])


def _extract_translations(item: Any, entity_id: str, fields: list[str]) -> Texts:
    for field_name in fields:
        for lang, text in _translations(item, field_name):
            if text:
                yield (entity_id, lang, text)


def _translations(item: Any, field_name: str) -> Iterator[tuple[str, str]]:
    translation = item.get(field_name, {})

    match translation.get("type"):
        case "translation":
            texts = translation["lines"].items()
        case "text":
            texts = [("any", translation["text"])]
        case _:
            return

    yield from texts
