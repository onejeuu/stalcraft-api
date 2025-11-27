from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple, TypeAlias

from . import parsing, tokenize


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
    """Inverted Index, mapping from N-grams (tokens) to Entity IDs."""

    _entities: Entities = field(default_factory=dict)
    """Entity Storage, stores all translations (Entity ID -> {lang: text})."""

    def build(self, path: str, data: dict[str, Any]):
        index: Index = defaultdict(set)
        entities: Entities = defaultdict(dict)

        parser = self._get_parser(path)

        for entity_id, lang, text in parser(data):
            # collect translations for entity id
            entities[entity_id][lang] = text

            # tokenization & indexing, generate N-grams for fuzzy search
            for word in tokenize.words(text):
                tokens = tokenize.ngrams(word)

                # store mapping in inverted index, I[ngram] -> {entity_id}
                for ngram in tokens:
                    index[ngram].add(entity_id)

        self._index = dict(index)
        self._entities = dict(entities)

    def search(self, query: str, threshold: int = 1) -> list[Entity]:
        if not query:
            return []

        # tokenize user search query
        words = tokenize.words(query)
        ngrams = {ngram for word in words for ngram in tokenize.ngrams(word)}

        if not ngrams:
            return []

        # count how many N-grams from the query (Q) hit each indexed entity (I)
        # hits: {entity_id: count of matching N-grams}
        hits: dict[str, int] = defaultdict(int)

        # soft matching (OR) collect entity ids for all matching N-grams
        for ngram in ngrams & self._index.keys():
            for entity_id in self._index[ngram]:
                hits[entity_id] += 1

        results: list[Entity] = []
        num_ngrams = len(ngrams)

        # scoring & filtering hits
        for entity_id, count in hits.items():
            if count >= threshold:
                # (|Q ∩ I|) / (|Q|)
                score = round(count / num_ngrams, 2)

                translations = self._entities.get(entity_id, {})
                results.append(Entity(id=entity_id, translations=translations, score=score))

        # sort results by descending score
        return sorted(results, key=lambda r: r.score, reverse=True)

    def _get_parser(self, path: str):
        filename = path.split("/")[-1]

        match filename:
            case "listing.json":
                return parsing.listings

            case _:
                raise Exception("Unsupported file")
