import re
import unicodedata


_PATTERN_NORMALIZE = re.compile(r"[^\w\u0400-\u04FF]+", re.UNICODE)
_PATTERN_SPACE = re.compile(r"\s+")


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text.lower())
    text = _PATTERN_NORMALIZE.sub(" ", text)
    text = _PATTERN_SPACE.sub(" ", text).strip()
    return text


def tokenize(text: str) -> set[str]:
    return set(normalize(text).split(" "))
