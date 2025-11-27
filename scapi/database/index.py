from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple, TypeAlias

from . import parsing, tokenize


Index: TypeAlias = dict[str, set[str]]
Translations = dict[str, str]
Entities = dict[str, Translations]


class Lookup(NamedTuple):
    id: str
    translations: Translations
    score: float = 0.0


@dataclass
class SearchIndex:
    _index: Index = field(default_factory=dict)
    """Inverted Index, mapping from N-grams (tokens) to Entity IDs."""

    _entities: Entities = field(default_factory=dict)
    """Entity Storage, stores all translations (Entity ID -> {lang: text})."""

    def build(self, path: str, data: Any):
        index: Index = defaultdict(set)
        entities: Entities = defaultdict(dict)

        parser = parsing.get(path)

        for entity_id, lang, text in parser(data):
            # collect translations for entity id
            entities[entity_id][lang] = text

            # tokenize & indexing, store mapping I[ngram] -> {entity_id}
            ngrams = tokenize.ngramize(text)

            for ngram in ngrams:
                index[ngram].add(entity_id)

        self._index = dict(index)
        self._entities = dict(entities)

    def get(self, entity_id: str) -> Translations | None:
        return self._entities.get(entity_id)

    def search(self, query: str, threshold: int) -> list[Lookup]:
        if not query:
            return []

        # tokenize user search query
        ngrams = tokenize.ngramize(query)

        if not ngrams:
            return []

        # count how many N-grams from the query (Q) hit each indexed entity (I)
        # hits: {entity_id: count of matching N-grams}
        hits: dict[str, int] = defaultdict(int)

        # soft matching (OR) collect entity ids for all matching N-grams
        for ngram in ngrams & self._index.keys():
            for entity_id in self._index[ngram]:
                hits[entity_id] += 1

        # create search results
        results: list[Lookup] = []
        num_ngrams = len(ngrams)

        # scoring & filtering hits
        for entity_id, count in hits.items():
            if count >= threshold:
                # (|Q ∩ I|) / (|Q|)
                score = round(count / num_ngrams, 2)

                translations = self._entities.get(entity_id, {})
                results.append(Lookup(id=entity_id, translations=translations, score=score))

        # sort results by descending score
        return sorted(results, key=lambda r: r.score, reverse=True)
