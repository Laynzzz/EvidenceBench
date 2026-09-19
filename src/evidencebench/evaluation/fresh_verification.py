"""Verify saved fresh comparison outputs without inference."""

import json

from evidencebench.evaluation.fresh_comparison import summarize
from evidencebench.indexing import load_index
from evidencebench.ingestion import canonical, digest


def verify_run(run, queries, units):
    def read(path):
        return json.loads(path.read_text("utf-8"))

    manifest = read(run / "manifest.json")
    owner = run.parent.parent
    attempt = read(owner / "attempt.json")
    termination = read(owner / "termination.json")
    if (
        termination.get("reason") != "process_exit"
        or termination.get("exit_code") != 0
        or attempt["snapshot"] != manifest["config"]
        or (owner / "worker.started").read_text("utf-8") != attempt["token"]
    ):
        raise ValueError("supervisor did not complete this exact attempt successfully")
    if manifest["status"] != "complete":
        raise ValueError("only complete comparisons can verify as complete")
    if (
        digest(canonical(manifest["config"])) != manifest["config_hash"]
        or read(run / "config.json") != manifest["config"]
        or digest((run / "source.zip").read_bytes()) != manifest["source_archive_hash"]
    ):
        raise ValueError("run source/config checksum mismatch")
    for name, checksum in manifest["files"].items():
        if digest((run / name).read_bytes()) != checksum:
            raise ValueError("saved output checksum mismatch")
    for name, checksum in manifest["config"].get("source_sha256", {}).items():
        from pathlib import Path

        if digest(Path(name).read_bytes()) != checksum:
            raise ValueError("pinned comparison source changed")
    load_index(run / "index", units, manifest["config"]["dataset_fingerprint"])
    lookup = {u.element_id: u for u in units}
    rows = {
        v: [json.loads(line) for line in (run / f"{v}.jsonl").read_text("utf-8").splitlines()]
        for v in ("control", "constrained")
    }
    for predictions in rows.values():
        if [r["query_id"] for r in predictions] != [q.query_id for q in queries]:
            raise ValueError("validation roster/order mismatch")
        for row, query in zip(predictions, queries, strict=True):
            expected = {
                "question": query.text,
                "family_id": query.family_id,
                "answerable": query.answerable,
                "answer_criteria": query.answer_criteria,
                "supporting_evidence": query.supporting_evidence,
            }
            if query.split != "dev" or any(row[k] != v for k, v in expected.items()):
                raise ValueError("row differs from frozen development labels")
            trace = row["trace"]
            if (
                len(trace["pre_ids"]) > 50
                or len(trace["post_ids"]) > 50
                or len(trace["packed_ids"]) > 3
            ):
                raise ValueError("evidence depth exceeded")
            packed = {
                f"E{i}": lookup[key].text[:1000] for i, key in enumerate(trace["packed_ids"], 1)
            }
            if trace["packed_evidence"] != packed or not set(row["citation_ids"]) <= set(
                trace["packed_ids"]
            ):
                raise ValueError("packed text or citation provenance mismatch")
    for a, b in zip(rows["control"], rows["constrained"], strict=True):
        for key in (
            "pre_ranking",
            "post_ranking",
            "pre_ids",
            "post_ids",
            "packed_ids",
            "packed_evidence",
        ):
            if a["trace"][key] != b["trace"][key]:
                raise ValueError("paired retrieval/context mismatch")
    metrics = summarize(rows)
    if metrics != read(run / "metrics.json"):
        raise ValueError("recomputed metrics mismatch")
    usage = read(run / "usage.json")
    expected_limits = manifest["config"].get("limits", usage["limits"])
    if usage["limits"] != expected_limits or any(
        not 0 <= n <= expected_limits[key] for key, n in usage["used"].items()
    ):
        raise ValueError("usage budget mismatch")
    if usage["used"]["document_embeddings"] != len(units):
        raise ValueError("index embedding count mismatch")
    for variant in rows:
        invoked = sum(bool(r["trace"]["packed_ids"]) for r in rows[variant])
        if usage["used"][f"{variant}_invocations"] != invoked:
            raise ValueError("generator invocation count mismatch")
    return {
        "status": "verified",
        "queries": len(queries),
        "metrics": metrics,
        "usage": usage["used"],
    }
