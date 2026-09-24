"""Check saved assistant-review provenance and quotations, not its semantic judgments."""

import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

from evidencebench.ingestion import digest

REVIEW = Path("reports/span-id-evidence-review.json")
FIELDS = {
    "packed_sufficiency": {"sufficient", "partial", "insufficient", "ambiguous"},
    "answer_quality": {"adequate", "partial", "inadequate", "ambiguous", "not_applicable"},
    "selected_quote_support": {"supported", "partial", "unsupported", "unclear", "not_applicable"},
    "clipping_effect": {"material", "not_demonstrated", "ambiguous"},
}


def verify(path=REVIEW):
    report = json.loads(path.read_text("utf-8"))
    sources = report["source_sha256"] | report["reviewer_artifact_sha256"]
    for source, expected in sources.items():
        if digest(Path(source).read_bytes()) != expected:
            raise ValueError(f"changed source: {source}")
    audit = json.loads(Path("reports/span-id-evidence-audit.json").read_text("utf-8"))
    if report["run"] != audit["run"]:
        raise ValueError("different source run")
    rows = [
        json.loads(line)
        for line in (Path(report["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]
    eligible = {r["query_id"]: r for r in rows if r["trace"]["packed_evidence"]}
    cases = report["cases"]
    if len(cases) != 32 or set(eligible) != {r["query_id"] for r in cases}:
        raise ValueError("review must cover exactly the 32 supplied-evidence cases")
    units = {
        u["element_id"]: u["text"]
        for u in pq.read_table(
            "data/processed/qasper-fresh-v1/units.parquet", filters=[("split", "=", "dev")]
        ).to_pylist()
    }
    checks = 0
    for case in cases:
        row = eligible[case["query_id"]]
        for field in ("question", "answer", "status", "answerable"):
            if case[field] != row[field]:
                raise ValueError(f"altered saved {field}")
        for field, allowed in FIELDS.items():
            if case[field] not in allowed:
                raise ValueError(f"unknown {field} rating")
        refused = row["status"] == "refused"
        if any(
            (case[field] == "not_applicable") != refused
            for field in ("answer_quality", "selected_quote_support")
        ):
            raise ValueError("refusal rating mismatch")
        if (
            refused and case["refusal_judgment"] not in {"justified", "unjustified", "unclear"}
        ) or (not refused and case["refusal_judgment"] is not None):
            raise ValueError("refusal judgment mismatch")
        packed = row["trace"]["packed_evidence"]
        originals = {f"E{i}": units[k] for i, k in enumerate(row["trace"]["packed_ids"], 1)}
        if not 1 <= len(case["evidence_checks"]) <= 3:
            raise ValueError("one to three source checks required")
        for check in case["evidence_checks"]:
            location, alias, quote = check["location"], check["evidence_id"], check["quote"]
            if location == "packed":
                texts = [packed[alias]]
            elif location == "original_paragraph":
                texts = [originals[alias]]
            elif location == "selected_quote":
                texts = [q["quote"] for q in row["answer_quotes"] if q["evidence_id"] == alias]
            else:
                raise ValueError("unknown evidence location")
            if not quote or not any(quote in text for text in texts):
                raise ValueError(f"unsupported exact evidence check: {case['query_id']}")
            checks += 1
    summary = {field: dict(Counter(c[field] for c in cases)) for field in FIELDS}
    summary["answer_quality_given_sufficient_packing"] = dict(
        Counter(c["answer_quality"] for c in cases if c["packed_sufficiency"] == "sufficient")
    )
    if summary != report["summary"]:
        raise ValueError("review counts differ from cases")
    return dict(status="verified", cases=len(cases), exact_evidence_checks=checks, summary=summary)


if __name__ == "__main__":
    print(json.dumps(verify()))
