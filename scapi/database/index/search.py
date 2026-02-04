from collections import defaultdict
from typing import Any, ClassVar, NamedTuple, TypeAlias

from . import parsing, tokenize


Index: TypeAlias = dict[str, set[str]]
Keys: TypeAlias = set[str]
Counts: TypeAlias = dict[str, int]
Entity: TypeAlias = dict[str, Any]
Entities: TypeAlias = dict[str, Entity]


class Lookup(NamedTuple):
    """Search result entry."""

    id: str
    data: dict[str, Any]
    score: float = 0.0
    """Similarity score between query and entity (`0.0`-`1.0`)."""


class SearchIndex:
    """In-memory search index for entity lookup with N-gram tokenization."""

    SCORE_ROUND: ClassVar[int] = 2
    """Number of decimals for score rounding."""

    JACCARD_WEIGHT: ClassVar[float] = 0.8
    """Weight factor for Jaccard similarity in scoring."""

    def __init__(self):
        self._index: Index = {}
        """Inverted index mapping N-grams to entity IDs."""

        self._keys: Keys = set()
        """Unique entity IDs."""

        self._entities: Entities = {}
        """Entity storage (ID -> JSON{})."""

        self._counts: Counts = {}
        """N-gram counts per entity ID."""

    def build(self, path: str, data: Any):
        """Build index from structured data at given path."""

        index: Index = defaultdict(set)
        counts: dict[str, set[str]] = defaultdict(set)
        entities: Entities = defaultdict(lambda: defaultdict(dict))

        parser = parsing.get(path)

        for entity_id, entity, texts in parser(data):
            # collect translations for entity id
            entities[entity_id] = entity

            # tokenize & indexing, store mapping I[ngram] -> {entity_id}
            for text in texts:
                ngrams = tokenize.ngramize(text)

                for ngram in ngrams:
                    index[ngram].add(entity_id)
                    counts[entity_id].add(ngram)

        # update instance values
        self._index = dict(index)
        self._keys = set(self._index.keys())
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
        for ngram in ngrams & self._keys:
            for entity_id in self._index[ngram]:
                hits[entity_id] += 1

        # query ngrams count
        q_num_ngrams = len(ngrams)

        # create search results
        results: list[Lookup] = []

        # scoring & filtering hits
        for entity_id, count in hits.items():
            # entity ngrams count
            e_num_ngrams = self._counts.get(entity_id, 0)

            if e_num_ngrams <= 0:
                continue

            # score: max(|Q ∩ I| / min(|Q|, |I|), w × |Q ∩ I| / (|Q| + |I| − |Q ∩ I|))
            min_size = min(q_num_ngrams, e_num_ngrams)
            union_size = q_num_ngrams + e_num_ngrams - count
            overlap = count / min_size if min_size > 0 else 0.0
            jaccard = count / union_size if union_size > 0 else 0.0
            score = round(max(overlap, jaccard * self.JACCARD_WEIGHT), self.SCORE_ROUND)

            # filter by threshold
            if score >= threshold:
                item = self._entities.get(entity_id, {})
                results.append(Lookup(id=entity_id, data=item, score=score))

        # sort results by descending score
        return sorted(results, key=lambda r: r.score, reverse=True)

    def __repr__(self):
        return f"{self.__class__.__name__}(entities={len(self._entities)}, index={len(self._index)})"
