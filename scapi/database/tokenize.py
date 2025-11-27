import re
import unicodedata


_PATTERN_NORMALIZE = re.compile(r"[^\w\u0400-\u04FF]+", re.UNICODE)
_PATTERN_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.lower())
    text = _PATTERN_NORMALIZE.sub(" ", text)
    text = _PATTERN_SPACE.sub(" ", text).strip()
    return text


def words(text: str) -> set[str]:
    return set(normalize(text).split(" "))


def ngrams(token: str, n: int = 3) -> set[str]:
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
