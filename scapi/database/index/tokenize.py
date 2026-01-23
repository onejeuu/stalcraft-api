import re
import unicodedata


_PATTERN_NORMALIZE = re.compile(r"[^\w\u0400-\u04FF]+", re.UNICODE)
_PATTERN_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Normalize text: case folding, unicode normalization, punctuation removal."""

    text = unicodedata.normalize("NFKC", text.lower())
    text = _PATTERN_NORMALIZE.sub(" ", text)
    text = _PATTERN_SPACE.sub(" ", text).strip()
    return text


def words(text: str) -> set[str]:
    """Tokenize text into normalized word set."""

    return set(normalize(text).split(" "))


def ngrams(token: str, n: int = 3) -> set[str]:
    """Generate N-grams from token with edge padding."""

    if not token:
        return set()

    padded = f"#{token}#"

    ngrams = set()
    L = len(padded) - n + 1
    for i in range(L):
        ngrams.add(padded[i : i + n])

    if len(token) < n:
        ngrams.add(token)

    return ngrams


def ngramize(text: str) -> set[str]:
    """Convert text to N-gram set for fuzzy matching."""

    return {ngram for word in words(text) for ngram in ngrams(word)}
