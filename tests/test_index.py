import warnings

from scapi.database.index import parsing, tokenize
from scapi.database.index.search import Lookup, SearchIndex


def test_normalize():
    assert tokenize.normalize("Hello World!") == "hello world"
    assert tokenize.normalize("Привет, мир!") == "привет мир"
    assert tokenize.normalize("  spaces   ") == "spaces"
    assert tokenize.normalize("UPPER CASE") == "upper case"
    assert tokenize.normalize("a.b,c;d:e") == "a b c d e"


def test_words():
    assert tokenize.words("hello world") == {"hello", "world"}
    assert tokenize.words("hello  world") == {"hello", "world"}
    assert tokenize.words("") == {""}
    assert tokenize.words("single") == {"single"}


def test_ngrams():
    assert tokenize.ngrams("cat", 3) == {"cat", "#ca", "cat", "at#"}
    assert tokenize.ngrams("ab", 3) == {"#ab", "ab", "ab#"}
    assert tokenize.ngrams("", 3) == set()
    assert len(tokenize.ngrams("hello", 3)) == 5


def test_ngramize():
    result = tokenize.ngramize("hello world")
    assert len(result) > 0
    assert all(len(g) == 3 for g in result if len(g) == 3)


def test_extract():
    item = {
        "name": {"type": "translation", "lines": {"en": "Name", "ru": "Название"}},
        "title": {"type": "text", "text": "Achievement"},
    }

    result = parsing._extract(item, "name", "title")
    assert "Name" in result
    assert "Название" in result
    assert "Achievement" in result


def test_translations():
    item = {"name": {"type": "translation", "lines": {"en": "Name", "ru": "Название"}}}

    result = parsing._translations(item, "name")
    assert result == ["Name", "Название"]

    item = {"title": {"type": "text", "text": "Achievement"}}
    result = parsing._translations(item, "title")
    assert result == ["Achievement"]

    item = {}
    result = parsing._translations(item, "nonexistent")
    assert result == []

    item = {"field": {"type": "unknown"}}
    result = parsing._translations(item, "field")
    assert result == []


def test_get_parser():
    parser = parsing.get("ru/listing.json")
    assert callable(parser)

    parser = parsing.get("ru/stats.json")
    assert callable(parser)

    parser = parsing.get("ru/achievements.json")
    assert callable(parser)

    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        parser = parsing.get("unknown.txt")
        data = [{"test": "data"}]
        result = list(parser(data))

        assert len(w) == 1
        assert issubclass(w[0].category, UserWarning)

    assert result == []


def test_listings_parser():
    from scapi.database.index.parsing import _listings

    data = [
        {
            "data": "/items/attachment/other/1r1j6.json",
            "name": {"type": "translation", "lines": {"ru": "M203", "en": "M203"}},
        },
        {"data": "/items/misc/npr6.json", "name": {"type": "translation", "lines": {"ru": "Цинк", "en": "Zinc"}}},
    ]

    results = list(_listings(data))

    assert len(results) == 2

    entity_id1, entity1, texts1 = results[0]
    assert entity_id1 == "1r1j6"
    assert entity1["data"] == "/items/attachment/other/1r1j6.json"
    assert len(texts1) > 0

    entity_id2, entity2, texts2 = results[1]
    assert entity_id2 == "npr6"
    assert entity2["data"] == "/items/misc/npr6.json"
    assert len(texts2) > 0


def test_stats_parser():
    from scapi.database.index.parsing import _stats

    data = [
        {
            "id": "mut-flsh-kil",
            "category": "SURVIVAL",
            "type": "INTEGER",
            "name": {"type": "translation", "lines": {"ru": "Убито хрюш", "en": "Piggies killed"}},
        }
    ]

    results = list(_stats(data))

    assert len(results) == 1
    entity_id, entity, texts = results[0]

    assert entity_id == "mut-flsh-kil"
    assert entity["id"] == "mut-flsh-kil"
    assert entity["category"] == "SURVIVAL"
    assert len(texts) > 0


def test_achievements_parser():
    from scapi.database.index.parsing import _achievements

    data = [
        {
            "id": "closed_beta_2014",
            "title": {"type": "translation", "lines": {"ru": "Старая гвардия", "en": "Old Guard"}},
            "description": {"type": "translation", "lines": {"ru": "Поддержать EXBO", "en": "Support EXBO"}},
            "points": 20,
        }
    ]

    results = list(_achievements(data))

    assert len(results) == 1
    entity_id, entity, texts = results[0]

    assert entity_id == "closed_beta_2014"
    assert entity["id"] == "closed_beta_2014"
    assert entity["points"] == 20
    assert len(texts) > 0


def test_search_index_build():
    index = SearchIndex()

    mock_data = [
        {
            "data": "/items/attachment/other/1r1j6.json",
            "name": {"type": "translation", "lines": {"ru": "M203", "en": "M203"}},
        },
        {"data": "/items/misc/npr6.json", "name": {"type": "translation", "lines": {"ru": "Цинк", "en": "Zinc"}}},
        {
            "data": "/items/other/7l9d3.json",
            "name": {"type": "translation", "lines": {"ru": "Премиум на 180 дней", "en": "Premium for 180 days"}},
        },
        {
            "data": "/items/drink/6w5jj.json",
            "name": {"type": "translation", "lines": {"ru": "Брусничная водка", "en": "Lingonberry Vodka"}},
        },
    ]

    index.build("ru/listing.json", mock_data)

    assert len(index._entities) == 4
    assert "1r1j6" in index._entities
    assert "npr6" in index._entities
    assert "7l9d3" in index._entities
    assert "6w5jj" in index._entities
    assert len(index._index) > 0


def test_search_index_get():
    index = SearchIndex()
    mock_data = [{"data": "/items/attachment/other/1r1j6.json", "name": {"type": "text", "text": "M203"}}]
    index.build("ru/listing.json", mock_data)

    entity = index.get("1r1j6")
    assert entity is not None
    assert entity["data"] == "/items/attachment/other/1r1j6.json"

    assert index.get("nonexistent") is None


def test_search():
    index = SearchIndex()
    mock_data = [
        {"data": "/items/attachment/other/1r1j6.json", "name": {"type": "text", "text": "M203"}},
        {"data": "/items/misc/npr6.json", "name": {"type": "text", "text": "Цинк"}},
        {"data": "/items/other/7l9d3.json", "name": {"type": "text", "text": "Премиум на 180 дней"}},
        {"data": "/items/drink/6w5jj.json", "name": {"type": "text", "text": "Брусничная водка"}},
    ]
    index.build("ru/listing.json", mock_data)

    results = index.search("m203", threshold=0.5)
    assert len(results) == 1
    assert isinstance(results[0], Lookup)
    assert results[0].id == "1r1j6"
    assert results[0].score > 0

    results = index.search("цинк", threshold=0.5)
    assert len(results) == 1
    assert results[0].id == "npr6"

    results = index.search("премиум", threshold=0.5)
    assert len(results) == 1
    assert results[0].id == "7l9d3"

    results = index.search("водка", threshold=0.5)
    assert len(results) == 1
    assert results[0].id == "6w5jj"

    results = index.search("endgame", threshold=0.5)
    assert len(results) == 0

    results = index.search("???", threshold=0.5)
    assert len(results) == 0

    results = index.search("", threshold=0.5)
    assert len(results) == 0


def test_search_entity_with_zero_ngrams():
    index = SearchIndex()

    index._entities["id"] = {"data": "/test.json"}
    index._counts["id"] = 0

    index._keys = set()

    results = index.search("query", threshold=0.1)
    assert len(results) == 0


def test_search_query_with_only_punctuation():
    index = SearchIndex()
    mock_data = [
        {
            "data": "/items/attachment/other/1r1j6.json",
            "name": {"type": "translation", "lines": {"ru": "M203", "en": "M203"}},
        }
    ]
    index.build("ru/listing.json", mock_data)

    for query in ["!!!", "???", "   ", "...", ",,,", ";"]:
        results = index.search(query, threshold=0.1)
        assert len(results) == 0
