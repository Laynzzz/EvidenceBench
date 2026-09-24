"""Recompute development evidence-path/clipping facts without model execution."""

import argparse
import importlib.util
import json
from collections import Counter
from pathlib import Path

from evidencebench.ingestion import canonical, digest

CORPUS = Path("data/processed/qasper-fresh-v1/units.parquet")
OUTPUT = Path("reports/span-id-evidence-audit.json")


def analyze(rows, units):
    if not rows or len({r["query_id"] for r in rows}) != len(rows):
        raise ValueError("nonempty unique query roster required")
    cases = []
    for row in rows:
        trace = row["trace"]
        packed, packed_ids = trace["packed_evidence"], trace["packed_ids"]
        pre = [x["element_id"] for x in trace["pre_ranking"]]
        post = [x["element_id"] for x in trace["post_ranking"]]
        if (
            len(set(packed_ids)) != len(packed_ids)
            or set(packed) != {f"E{i}" for i in range(1, len(packed_ids) + 1)}
            or len(packed_ids) > 3
            or packed_ids != post[: len(packed_ids)]
            or len(set(pre)) != len(pre)
            or len(set(post)) != len(post)
            or set(post) != set(pre)
        ):
            raise ValueError("invalid saved evidence roster")
        gold = set(row["supporting_evidence"])
        counts = dict(
            gold_in_retrieved=len(gold & set(pre)),
            gold_in_post_top3=len(gold & set(post[:3])),
            gold_in_packed=len(gold & set(packed_ids)),
            gold_in_cited=len(gold & set(row["citation_ids"])),
        )
        if not row["answerable"]:
            path = "benchmark_unanswerable"
        elif not counts["gold_in_retrieved"]:
            path = "no_gold_in_retrieved_roster"
        elif not counts["gold_in_post_top3"]:
            path = "gold_below_top3"
        elif not counts["gold_in_packed"]:
            path = "threshold_blocks_top3_gold"
        elif row["status"] == "refused":
            path = "model_refusal_with_gold_packed"
        elif row["status"] == "failure":
            path = "generation_failure_with_gold_packed"
        elif not counts["gold_in_cited"]:
            path = "gold_packed_but_not_cited"
        else:
            path = "gold_cited_semantics_unproven"
        passages = []
        for i, key in enumerate(packed_ids, 1):
            alias = f"E{i}"
            if key not in units or units[key]["split"] != "dev":
                raise ValueError("development source unit required")
            full, supplied = units[key]["text"], packed[alias]
            if supplied != full[:1000]:
                raise ValueError("saved prefix differs from frozen source unit")
            length = len(supplied)
            clipped = length < len(full)
            midword = bool(
                clipped and length and full[length - 1].isalnum() and full[length].isalnum()
            )
            quotes = [q["quote"] for q in row.get("answer_quotes", []) if q["evidence_id"] == alias]
            body = supplied.partition("\n")[2]
            if any(q not in body for q in quotes):
                raise ValueError("saved quote absent from supplied body")
            passages.append(
                dict(
                    evidence_id=alias,
                    element_id=key,
                    full_characters=len(full),
                    supplied_characters=length,
                    omitted_characters=len(full) - length,
                    clipped=clipped,
                    cut_inside_alphanumeric_word=midword,
                    gold_id=key in gold,
                    cited=key in row["citation_ids"],
                    selected_quote_touches_clipped_end=bool(
                        clipped and any(body.rstrip().endswith(q) for q in quotes)
                    ),
                    supplied_suffix=supplied[-80:],
                    omitted_prefix=full[length : length + 160],
                )
            )
        cases.append(
            dict(
                query_id=row["query_id"],
                question=row["question"],
                answerable=row["answerable"],
                status=row["status"],
                reason=row["reason"],
                evidence_path=path,
                pre_first_gold_rank=next((i for i, k in enumerate(pre, 1) if k in gold), None),
                post_first_gold_rank=next((i for i, k in enumerate(post, 1) if k in gold), None),
                top_score=trace["post_ranking"][0].get("reranker_score") if post else None,
                **counts,
                passages=passages,
            )
        )
    all_passages = [p for c in cases for p in c["passages"]]
    answerable = [c for c in cases if c["answerable"]]
    summary = dict(
        query_count=len(cases),
        answerable_count=len(answerable),
        status_counts=dict(Counter(c["status"] for c in cases)),
        evidence_paths=dict(Counter(c["evidence_path"] for c in answerable)),
        answerable_queries_with_gold_at_stage={
            k: sum(c[k] > 0 for c in answerable)
            for k in ["gold_in_retrieved", "gold_in_post_top3", "gold_in_packed", "gold_in_cited"]
        },
        refusal_reasons=dict(Counter(c["reason"] for c in cases if c["status"] == "refused")),
        answerable_refusals=sum(c["status"] == "refused" for c in answerable),
        packed_passage_occurrences=len(all_passages),
        clipped_passage_occurrences=sum(p["clipped"] for p in all_passages),
        midword_cut_occurrences=sum(p["cut_inside_alphanumeric_word"] for p in all_passages),
        queries_with_clipping=sum(any(p["clipped"] for p in c["passages"]) for c in cases),
        cited_clipped_occurrences=sum(p["cited"] and p["clipped"] for p in all_passages),
        selected_quote_at_clipped_end_occurrences=sum(
            p["selected_quote_touches_clipped_end"] for p in all_passages
        ),
    )
    return dict(summary=summary, cases=cases)


def build_report():
    import pyarrow.parquet as pq

    path = Path(__file__).with_name("run_span_id_answer.py")
    spec = importlib.util.spec_from_file_location("frozen_runner", path)
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    snapshot, _ = runner.preflight()
    verified = runner.engine.verify(runner.ROOT, snapshot)
    run = Path(verified["run"])
    predictions = run / "predictions.jsonl"
    rows = [json.loads(line) for line in predictions.read_text("utf-8").splitlines()]
    if len(rows) != 50 or sum(r["answerable"] for r in rows) != 38:
        raise ValueError("frozen 50-question development roster required")
    units = {
        u["element_id"]: u
        for u in pq.read_table(CORPUS, filters=[("split", "=", "dev")]).to_pylist()
    }
    result = analyze(rows, units)
    return dict(
        scope=(
            "Post-hoc saved-development diagnosis; not a new model evaluation or semantic verdict"
        ),
        run=verified["run"],
        model_calls=0,
        final_test_used=False,
        verified_snapshot_sha256=digest(canonical(snapshot)),
        source_sha256={
            p.as_posix(): digest(p.read_bytes())
            for p in [
                Path(__file__).relative_to(Path.cwd()),
                predictions,
                run / "config.json",
                CORPUS,
                Path("src/evidencebench/ingestion.py"),
            ]
        },
        limitations=(
            "Gold-ID membership is an annotation-agreement proxy, not evidence sufficiency. "
            "Clipped/midword flags identify string boundaries, not answer loss. Counts are "
            "passage occurrences across queries, not unique corpus paragraphs."
        ),
        **result,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    result = build_report()
    if args.verify:
        if json.loads(OUTPUT.read_text("utf-8")) != result:
            raise ValueError("saved audit differs from recomputation")
    else:
        OUTPUT.write_bytes(
            (json.dumps(result, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        )
    print(json.dumps({"status": "verified" if args.verify else "written", **result["summary"]}))


if __name__ == "__main__":
    main()
