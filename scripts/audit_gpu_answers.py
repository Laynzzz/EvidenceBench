"""Audit saved development answers without model execution or changing benchmark labels."""

import argparse
import importlib.util
import json
import math
from collections import Counter
from pathlib import Path

from evidencebench.evaluation.answers import token_f1
from evidencebench.generation_spans import build_spans
from evidencebench.ingestion import canonical, digest

RUN = Path("artifacts/gpu-support-v1/runs/20260920T025107Z-d0f904ba5f")
OUTPUT = Path("reports/gpu-answer-audit.json")
ANNOTATIONS = Path("reports/gpu-answer-review-draft.json")


def read(path):
    return json.loads(path.read_text("utf-8"))


def analyze(rows, decisions):
    ids = [r["query_id"] for r in rows]
    answered = [r for r in rows if r["status"] == "answered"]
    if len(set(ids)) != len(ids) or [d["query_id"] for d in decisions] != [
        r["query_id"] for r in answered
    ]:
        raise ValueError("exact unique saved-answer and decision roster required")
    if any(d["verdict"] not in {"SUPPORTED", "UNSUPPORTED", "FAILURE"} for d in decisions):
        raise ValueError("invalid checker verdict")
    denominator = sum(r["answerable"] for r in rows)
    if not denominator:
        raise ValueError("answerable denominator required")
    cases = []
    for row, decision in zip(answered, decisions, strict=True):
        trace = row["trace"]
        ids = trace["packed_ids"]
        packed = trace["packed_evidence"]
        if len(set(ids)) != len(ids) or set(packed) != {f"E{i}" for i in range(1, len(ids) + 1)}:
            raise ValueError("invalid packed evidence roster")
        aliases = {key: f"E{i}" for i, key in enumerate(ids, 1)}
        if not row["citation_ids"] or any(key not in aliases for key in row["citation_ids"]):
            raise ValueError("invalid saved citation")
        cited = {aliases[key]: packed[aliases[key]] for key in row["citation_ids"]}
        refs = row["answer_criteria"].split(" | Alternative human answer: ")
        f1 = max(token_f1(row["answer"], ref) for ref in refs) if row["answerable"] else None
        spans = build_spans(packed)
        # Uses labels deliberately: a diagnostic ceiling, never a candidate or output policy.
        best = max((token_f1(span, ref) for span in spans for ref in refs), default=0.0)
        cases.append(
            {
                "query_id": row["query_id"],
                "family_id": row["family_id"],
                "question": row["question"],
                "answer": row["answer"],
                "cited_evidence": cited,
                "answerable": row["answerable"],
                "reference": row["answer_criteria"],
                "verdict": decision["verdict"],
                "word_count": len(row["answer"].split()),
                "at_15_word_limit": len(row["answer"].split()) == 15,
                "source_span_match": row["answer"] in build_spans(cited),
                "citation_has_gold_id": bool(
                    set(row["citation_ids"]) & set(row["supporting_evidence"])
                ),
                "packed_has_gold_id": bool(set(ids) & set(row["supporting_evidence"])),
                "cited_1000_character_boundary": any(len(text) == 1000 for text in cited.values()),
                "answer_f1": f1,
                "best_packed_span_f1": best if row["answerable"] else None,
            }
        )
    original = sum(c["answer_f1"] or 0 for c in cases) / denominator
    retained = sum(c["answer_f1"] or 0 for c in cases if c["verdict"] == "SUPPORTED") / denominator
    return {
        "scope": "post-hoc diagnostic; no selection or revised scores",
        "query_count": len(rows),
        "answerable_denominator": denominator,
        "checked_answers": len(cases),
        "verdict_counts": dict(Counter(c["verdict"] for c in cases)),
        "source_matching_answers": sum(c["source_span_match"] for c in cases),
        "answers_at_15_word_limit": sum(c["at_15_word_limit"] for c in cases),
        "cited_at_1000_character_boundary": sum(c["cited_1000_character_boundary"] for c in cases),
        "original_f1": original,
        "retained_f1": retained,
        "removed_f1_contribution": original - retained,
        "answerable_cases_with_better_available_span": sum(
            c["answerable"] and c["best_packed_span_f1"] > c["answer_f1"] + 1e-12 for c in cases
        ),
        "cases": cases,
        "limitations": (
            "Reference-overlap ceilings use gold answers and can favor incomplete spans. "
            "They are not semantic correctness, a deployable selector, or an evaluation "
            "of a new model. Draft reviews are agent judgments, not independent human labels."
        ),
    }


def persist(path, result, check):
    data = canonical(result) + b"\n"
    if check or path.exists():
        if path.read_bytes() != data:
            raise ValueError("retained audit differs; refusing overwrite")
    else:
        with path.open("xb") as stream:
            stream.write(data)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--check", action="store_true")
    args = p.parse_args()
    spec = importlib.util.spec_from_file_location("gpu_runner", "scripts/run_gpu_support_filter.py")
    gpu = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gpu)
    snapshot, _ = gpu.preflight()
    verified = gpu.verify(gpu.ROOT, snapshot)
    if verified["run"] != RUN.as_posix():
        raise ValueError("only frozen development run allowed")
    decisions = [
        json.loads(line) for line in (RUN / "decisions.jsonl").read_text("utf-8").splitlines()
    ]
    rows = gpu.base_module().original_rows()["constrained"]
    result = analyze(rows, decisions)
    for field, variant in (("original_f1", "unfiltered"), ("retained_f1", "filtered")):
        if not math.isclose(
            result[field], verified["metrics"][variant]["answerable_token_f1"], abs_tol=1e-12
        ):
            raise ValueError("F1 decomposition does not reproduce verified metrics")
    annotations = read(ANNOTATIONS)
    cases = result["cases"]
    if annotations["reviewer_type"] != "agent_draft" or [
        a["query_id"] for a in annotations["cases"]
    ] != [c["query_id"] for c in cases]:
        raise ValueError("exact agent draft review roster required")
    for case, draft in zip(cases, annotations["cases"], strict=True):
        if (
            draft["response_assessment"]
            not in {"partial", "nonresponsive", "unclear", "responsive_label_conflict"}
            or not draft["rationale"]
        ):
            raise ValueError("incomplete agent draft")
        case["agent_draft"] = draft
    for name, h in annotations["extra_source_sha256"].items():
        if digest(Path(name).read_bytes()) != h:
            raise ValueError("review source changed")
    result.update(
        run=RUN.as_posix(),
        model_calls=0,
        final_test_used=False,
        external_spend_usd=0,
        agent_draft_counts=dict(Counter(d["response_assessment"] for d in annotations["cases"])),
        audit_source_sha256=digest(Path(__file__).read_bytes()),
        input_sha256={
            str(path).replace("\\", "/"): digest(path.read_bytes())
            for path in [
                RUN / "manifest.json",
                RUN / "inputs.json",
                RUN / "decisions.jsonl",
                ANNOTATIONS,
                Path("reports/gpu-support-readiness.json"),
            ]
        },
    )
    persist(OUTPUT, result, args.check)
    print(
        json.dumps(
            {
                "status": "verified" if args.check else "written",
                **{
                    k: v
                    for k, v in result.items()
                    if k not in {"cases", "input_sha256", "limitations"}
                },
            }
        )
    )


if __name__ == "__main__":
    main()
