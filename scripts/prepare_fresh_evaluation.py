"""Audit saved development citations and reserve unused paper families without inference."""

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from evidencebench.evaluation.development_audit import diagnose, reserve_families
from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.protocol import verify_protocol

AUDIT = Path("reports/citation-diagnostics-development.json")
RESERVATION = Path("data/manifests/fresh-evaluation-reservation.json")
RAW = Path("data/raw/qasper")


def read(path):
    return json.loads(Path(path).read_text("utf-8"))


def retained_output(path, value, check):
    if check or path.exists():
        if read(path) != value:
            raise ValueError(f"retained output mismatch: {path}")
    else:
        with path.open("xb") as stream:
            stream.write(canonical(value) + b"\n")


def citation_audit():
    report_path = Path("reports/answer-spans-development.json")
    report = read(report_path)
    units = load_units(Path("data/processed/qasper-v1"))
    by_text = defaultdict(list)
    for unit in units:
        by_text[(unit.family_id, unit.text[:1000])].append(unit.element_id)
    result = {"scope": "saved development predictions only; no semantic judgments", "variants": {}}
    result["source_report_sha256"] = digest(report_path.read_bytes())
    for variant in ("constrained", "focused"):
        path = Path(report["experiments"][variant]["run"]) / "predictions.jsonl"
        manifest = read(path.parent / "manifest.json")
        if digest(path.read_bytes()) != manifest["predictions_hash"]:
            raise ValueError("prediction checksum mismatch")
        rows = [json.loads(line) for line in path.read_text("utf-8").splitlines()]
        records = []
        for row in rows:
            packed = {}
            for text in row["trace"].get("packed_evidence", {}).values():
                matches = by_text[(row["family_id"], text)]
                if len(matches) != 1:
                    raise ValueError("packed passage does not map uniquely")
                # Exclude the title wrapper from quote diagnostics, as the generator does.
                packed[matches[0]] = text.split("\n", 1)[-1]
            gold = row["supporting_evidence"]
            category = (
                diagnose(row["answer"], row["citation_ids"], packed, gold)
                if row["status"] == "answered"
                else row["status"]
            )
            records.append(
                {
                    "query_id": row["query_id"],
                    "answerable": row["answerable"],
                    "status": row["status"],
                    "category": category,
                    "gold_in_packed_context": sorted(set(gold) & packed.keys()),
                    "citation_ids": row["citation_ids"],
                }
            )
        counts = dict(sorted(Counter(r["category"] for r in records).items()))
        expected = report["experiments"][variant]["metrics"]["candidate"]
        answered = sum(r["status"] == "answered" for r in rows)
        if (
            abs(counts.get("gold_citation", 0) / answered - expected["upstream_citation_precision"])
            > 1e-12
        ):
            raise ValueError("diagnostic counts disagree with citation precision")
        result["variants"][variant] = {
            "predictions": path.as_posix(),
            "predictions_sha256": digest(path.read_bytes()),
            "counts": counts,
            "records": records,
        }
    return result


def reservation():
    # On verification retain the pre-acquisition inventory. Future PDF downloads
    # must not silently redefine which families were untouched at reservation time.
    if RESERVATION.exists():
        inventory = read(RESERVATION)["prior_cache_inventory"]
    else:
        inventory = sorted(
            p.as_posix() for p in [*RAW.glob("*.pdf"), *(RAW / "processed-cache").glob("*.json")]
        )
    selection_path = Path("data/manifests/qasper-selection.json")
    audit_path = Path("data/processed/qasper-v1/alignment-audit.json")
    exclusions = {
        "v1_selected": sorted(read(selection_path)["paper_ids"]),
        "v1_alignment_attempted": sorted({r["paper_id"] for r in read(audit_path)}),
        "prior_cached": sorted({Path(p).stem.split("-", 1)[0] for p in inventory}),
    }
    excluded = set().union(*(set(ids) for ids in exclusions.values()))
    paths = [RAW / f"qasper-{split}-v0.3.json" for split in ("dev", "test")]
    # Only dictionary keys are used; no label-based or title-based selection.
    papers = {split: list(read(path)) for split, path in zip(("dev", "test"), paths, strict=True)}
    return {
        "version": "fresh-paper-reservation-v1",
        "status": "reserved_only_not_aligned_or_evaluated",
        "selection": (
            "sha256(fresh-eval-v1:42:<paper_id>); source dev -> validation, source test -> test"
        ),
        "freshness_scope": (
            "excluded known local usage; not a model-pretraining contamination guarantee"
        ),
        "source_sha256": {
            p.as_posix(): digest(p.read_bytes()) for p in [*paths, selection_path, audit_path]
        },
        "prior_cache_inventory": inventory,
        "exclusion_reasons": exclusions,
        "excluded_family_count": len(excluded),
        "pools": reserve_families(papers, excluded, 60, 120),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="verify retained outputs without writes"
    )
    args = parser.parse_args()
    verify_protocol(Path("data/manifests/release-lock.json"))
    audit, reserved = citation_audit(), reservation()
    retained_output(AUDIT, audit, args.check)
    retained_output(RESERVATION, reserved, args.check)
    print(
        json.dumps(
            {
                "mode": "verified" if args.check else "prepared",
                "citation_counts": {v: r["counts"] for v, r in audit["variants"].items()},
                "excluded_families": reserved["excluded_family_count"],
                "reserved_families": {
                    s: {k: len(v) for k, v in p.items()} for s, p in reserved["pools"].items()
                },
                "model_calls": 0,
            }
        )
    )


if __name__ == "__main__":
    main()
