"""Offline diagnostics and family reservation; never run inference or score new labels."""

import hashlib
import re
import unicodedata


def diagnose(answer, citations, packed_by_id, gold):
    """Classify one single-citation answer against IDs, not semantic correctness."""
    if len(citations) != 1 or citations[0] not in packed_by_id:
        raise ValueError("expected one citation in packed context")
    gold = set(gold)
    if not gold:
        return "unanswerable_answer"
    if citations[0] in gold:
        return "gold_citation"
    present = gold & packed_by_id.keys()
    if not present:
        return "gold_absent_from_context"
    if answer in {"Yes", "No"}:
        return "boolean_wrong_citation"

    def normalize(text):
        return " ".join(unicodedata.normalize("NFKC", text).split())

    quote = normalize(answer)
    if not quote:
        raise ValueError("empty answer")
    pattern = r"(?<!\w)" + re.escape(quote) + r"(?!\w)"
    if any(re.search(pattern, normalize(packed_by_id[key])) for key in present):
        return "quote_also_in_gold"
    return "gold_present_other_span"


def reserve_families(papers, excluded, validation_count, test_count):
    """Rank IDs without reading questions, labels, titles, or paper content."""
    if set(papers["dev"]) & set(papers["test"]):
        raise ValueError("source paper families overlap")
    result = {}
    for source, target, count in (
        ("dev", "validation", validation_count),
        ("test", "test", test_count),
    ):
        eligible = sorted(
            set(papers[source]) - set(excluded),
            key=lambda key: hashlib.sha256(f"fresh-eval-v1:42:{key}".encode()).hexdigest(),
        )
        if count <= 0 or len(eligible) < count:
            raise ValueError("not enough untouched families for positive reservation size")
        result[target] = {"primary": eligible[:count], "fallback": eligible[count:]}
    return result
