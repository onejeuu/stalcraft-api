from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple, TypeAlias

from . import parsing
from .tokenize import tokenize


Index: TypeAlias = dict[str, set[str]]
Translations = dict[str, str]
Entities = dict[str, Translations]


class Entity(NamedTuple):
    id: str
    translations: Translations
    score: float = 0.0


@dataclass
class SearchIndex:
    _index: Index = field(default_factory=dict)
    _entities: Entities = field(default_factory=dict)

    def build(self, path: str, data: dict[str, Any]):
        index: Index = defaultdict(set)
        entities: Entities = defaultdict(dict)

        parser = self._get_parser(path)

        for entity_id, lang, text in parser(data):
            entities[entity_id][lang] = text

            tokens = tokenize(text)

            for token in tokens:
                if token:
                    index[token].add(entity_id)

        self._index = dict(index)
        self._entities = dict(entities)

    def search(self, query: str, threshold: int = 1) -> list[Entity]:
        if not query:
            return []

        tokens = tokenize(query)
        if not tokens:
            return []

        hits: dict[str, int] = defaultdict(int)

        for token in tokens:
            if token in self._index:
                for entity_id in self._index[token]:
                    hits[entity_id] += 1

        results: list[Entity] = []
        num_tokens = len(tokens)

        for entity_id, count in hits.items():
            if count >= threshold:
                score = count / num_tokens
                translations = self._entities.get(entity_id, {})
                results.append(Entity(id=entity_id, translations=translations, score=score))

        results.sort(key=lambda r: r.score, reverse=True)

        return results

    def _get_parser(self, path: str):
        filename = path.split("/")[-1]

        match filename:
            case "listing.json":
                return parsing.listings

            case _:
                raise Exception("Unsupported file")
