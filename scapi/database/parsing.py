from typing import Any, Iterator


Items = list[dict[str, Any]]


def listings(data: Items):
    for item in data:
        path = item["data"]
        entity_id = path.split("/")[-1].replace(".json", "")
        yield from _extract_translations(item, entity_id, fields=["name"])


def stats(data: Items):
    for item in data:
        entity_id = item["id"]
        yield from _extract_translations(item, entity_id, fields=["name"])


def achievements(data: Items):
    for item in data:
        entity_id = item["id"]
        yield from _extract_translations(item, entity_id, fields=["name", "description"])


def _extract_translations(item: Any, entity_id: str, fields: list[str]) -> Iterator[tuple[str, str, str]]:
    for field_name in fields:
        for lang, text in _translations(item, field_name):
            if text:
                yield (entity_id, lang, text)


def _translations(item: Any, field_name: str):
    translation = item.get(field_name, {})

    match translation.get("type"):
        case "translation":
            texts = translation["lines"].items()
        case "text":
            texts = [("any", translation["text"])]
        case _:
            return

    yield from texts
