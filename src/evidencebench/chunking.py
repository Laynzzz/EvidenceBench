"""Versioned page-local word windows; bounding boxes use PDF top-left coordinates."""

import re
import unicodedata
from typing import Any

NORMALIZATION_VERSION = "nfkc-whitespace-v1"


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip()


def chunk_words(
    words: list[dict[str, Any]], max_words: int = 180, overlap: int = 30
) -> list[tuple[str, tuple[float, float, float, float]]]:
    if max_words < 1 or not 0 <= overlap < max_words:
        raise ValueError("overlap must be nonnegative and smaller than max_words")
    chunks = []
    for start in range(0, len(words), max_words - overlap):
        window = words[start : start + max_words]
        text = normalize(" ".join(w["text"] for w in window))
        if text:
            box = (
                min(w["x0"] for w in window),
                min(w["top"] for w in window),
                max(w["x1"] for w in window),
                max(w["bottom"] for w in window),
            )
            chunks.append((text, tuple(round(v, 3) for v in box)))
        if start + max_words >= len(words):
            break
    return chunks
