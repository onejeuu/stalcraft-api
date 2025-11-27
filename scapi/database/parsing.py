from typing import Any


def listings(data: Any):
    for item in data:
        path = item["data"]
        entity_id = path.split("/")[-1].replace(".json", "")

        for lang, text in _translation(item, "name"):
            if text:
                yield (entity_id, lang, text)


def _translation(item: Any, field_name: str):
    translation = item.get(field_name, {})

    match translation.get("type"):
        case "translation":
            texts = translation["lines"].items()
        case "text":
            texts = [("any", translation["text"])]
        case _:
            return

    yield from texts
