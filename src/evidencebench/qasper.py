"""Conservative import of original QASPER annotations and verified PDF page locations."""

import re
from typing import Any

from evidencebench.chunking import normalize

REFERENCES = r"(?:BIBREF|CITATION|INLINEFORM|DISPLAYFORM|TABREF|FIGREF|SECREF|EQREF)\d*"


def numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", re.sub(REFERENCES, " ", normalize(text))))


def alignment_tokens(text: str) -> list[str]:
    text = re.sub(
        r"(?:BIBREF|CITATION|INLINEFORM|DISPLAYFORM|TABREF|FIGREF|SECREF|EQREF)\d*", " ", text
    )
    text = re.sub(r"(?<=\w)-\s*\n\s*(?=\w)", "", text)
    return re.findall(r"[a-z0-9]+", normalize(text).casefold())


def locate_paragraph(text: str, pages: list[str]) -> int | None:
    span = locate_span(text, pages)
    return span[0] if span and span[0] == span[1] else None


def grams(text: str) -> set[str]:
    return {text[i : i + 5] for i in range(len(text) - 4)}


class PageAligner:
    """Conservative automatic location, not a human-verified citation label.

    All normalized words must occur and >=90% of character 5-grams must occur.
    Ignoring whitespace accommodates joined PDF words and line hyphenation.
    Two-page spans are allowed; ambiguous locations are rejected.
    """

    def __init__(self, pages: list[str]):
        self.pages = ["".join(alignment_tokens(p)) for p in pages]
        self.spans = []
        for size in (1, 2):
            for start in range(len(pages) - size + 1):
                combined = "".join(self.pages[start : start + size])
                numeric = numbers(" ".join(pages[start : start + size]))
                self.spans.append(
                    (size, start + 1, start + size, combined, grams(combined), numeric)
                )

    def locate(self, text: str) -> tuple[int, int] | None:
        words = alignment_tokens(text)
        if len(words) < 8:
            return None
        # Reference expansions may insert text between these segments in the PDF.
        segments = re.split(
            r"(?:BIBREF|CITATION|INLINEFORM|DISPLAYFORM|TABREF|FIGREF|SECREF|EQREF)\d*", text
        )
        required = set().union(*(grams("".join(alignment_tokens(s))) for s in segments))
        if not required:
            return None
        accepted = []
        numeric = numbers(text)
        for size, first, last, page, available, page_numbers in self.spans:
            if (
                numeric <= page_numbers
                and all(w in page for w in words)
                and len(required & available) / len(required) >= 0.9
            ):
                accepted.append((size, first, last))
        if not accepted:
            return None
        shortest = min(a[0] for a in accepted)
        matches = [a for a in accepted if a[0] == shortest]
        return (matches[0][1], matches[0][2]) if len(matches) == 1 else None


def locate_span(text: str, pages: list[str]) -> tuple[int, int] | None:
    return PageAligner(pages).locate(text)


def select_annotation(question: dict[str, Any]) -> dict[str, Any] | None:
    answers = [item["answer"] for item in question["answers"]]
    if not answers or len({a["unanswerable"] for a in answers}) > 1:
        return None
    if answers[0]["unanswerable"]:
        return {"answerable": False, "evidence": [], "criteria": "Unanswerable in the named paper"}
    evidence, criteria = set(), []
    for answer in answers:
        if not answer["evidence"] or any(
            x.startswith("FLOAT SELECTED") for x in answer["evidence"]
        ):
            return None
        evidence.update(normalize(x) for x in answer["evidence"])
        if answer.get("extractive_spans"):
            criteria.append("; ".join(answer["extractive_spans"]))
        elif answer.get("free_form_answer"):
            criteria.append(answer["free_form_answer"])
        elif answer.get("yes_no") is not None:
            criteria.append("Yes" if answer["yes_no"] else "No")
        else:
            return None
    return {
        "answerable": True,
        "evidence": sorted(evidence),
        "criteria": " | Alternative human answer: ".join(dict.fromkeys(criteria)),
    }
