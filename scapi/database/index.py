from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple, TypeAlias

from . import parsing, tokenize


Index: TypeAlias = dict[str, set[str]]

Entity = dict[str, Any]
Entities = dict[str, Entity]


class Lookup(NamedTuple):
    """Search result entry."""

    id: str
    data: dict[str, Any]
    score: float = 0.0


# TODO: remove dataclass?
@dataclass
class SearchIndex:
    """In-memory search index for entity lookup with N-gram tokenization."""

    _index: Index = field(default_factory=dict, repr=False)
    """Inverted Index, mapping from N-grams (tokens) to Entity IDs."""

    _entities: Entities = field(default_factory=dict, repr=False)
    """Entity Storage, stores all translations (Entity ID -> {lang: text})."""

    _counts: dict[str, int] = field(default_factory=dict, repr=False)
    """N-gram Counts, mapping Entity ID to total unique N-grams."""

    def build(self, path: str, data: Any):
        """Build index from structured data at given path."""

        # TODO: multilang fix
        index: Index = defaultdict(set)
        entities: Entities = defaultdict(lambda: defaultdict(dict))
        counts: dict[str, set[str]] = defaultdict(set)

        parser = parsing.get(path)

        for item, entity_id, text in parser(data):
            # collect translations for entity id
            entities[entity_id] = item

            # tokenize & indexing, store mapping I[ngram] -> {entity_id}
            ngrams = tokenize.ngramize(text)

            for ngram in ngrams:
                index[ngram].add(entity_id)
                counts[entity_id].add(ngram)

        self._index = dict(index)
        self._entities = dict(entities)
        self._counts = {entity_id: len(ngrams) for entity_id, ngrams in counts.items()}

    def get(self, entity_id: str) -> Entity | None:
        """Retrieve entity data by ID."""

        return self._entities.get(entity_id)

    def search(self, query: str, threshold: float) -> list[Lookup]:
        """
        Search entities with similarity scoring.

        Args:
            query: Search text.
            threshold: Minimum similarity score (`0.0`-`1.0`).

        Returns:
            List of matched entities sorted by relevance.
        """

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

        # query ngrams count
        q_num_ngrams = len(ngrams)

        # scoring & filtering hits
        for entity_id, count in hits.items():
            # entity ngrams count
            e_num_ngrams = self._counts.get(entity_id, 0)

            if e_num_ngrams <= 0:
                continue

            # |Q ∩ I| / (|Q| + |I| - |Q ∩ I|)
            union = q_num_ngrams + e_num_ngrams - count

            # TODO: consider length fix
            score = round(count / union, 2) if union != 0 else 0.0

            # filter by threshold
            if score >= threshold:
                item = self._entities.get(entity_id, {})
                results.append(Lookup(id=entity_id, data=item, score=score))

        # sort results by descending score
        return sorted(results, key=lambda r: r.score, reverse=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(entities={len(self._entities)}, index={len(self._index)})"
