"""Restore fixed development paragraphs; default preflight never runs inference."""

import argparse
import copy
import importlib.util
import json
from pathlib import Path

from evidencebench.ingestion import canonical, digest

ROOT = Path("artifacts/intact-passage-v1")
APPROVAL = Path("reports/intact-passage-authorization.json")
PROPOSAL = Path("docs/intact-passage-proposal.md")
WORKER = Path("scripts/intact_passage_worker.py")
CORPUS = Path("data/processed/qasper-fresh-v1/units.parquet")


def module(name):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


contract = module("intact_passage_contract")
ALLOWANCE, LIMITS = contract.ALLOWANCE, contract.LIMITS


def approval(snapshot, path=APPROVAL):
    record = json.loads(path.read_text("utf-8"))
    if (
        record.get("status") != "approved"
        or record.get("scope") != contract.SCOPE
        or record.get("snapshot_sha256") != digest(canonical(snapshot))
        or record.get("limits") != ALLOWANCE
    ):
        raise ValueError("new exact-snapshot intact-passage approval required")
    return record


def dev_units():
    import pyarrow.parquet as pq

    return {
        u["element_id"]: u
        for u in pq.read_table(CORPUS, filters=[("split", "=", "dev")]).to_pylist()
    }


def restore_rows(rows, units):
    result = copy.deepcopy(rows)
    if len({r["query_id"] for r in result}) != len(result):
        raise ValueError("unique source roster required")
    for row in result:
        trace = row["trace"]
        ids, packed = trace["packed_ids"], trace["packed_evidence"]
        if len(set(ids)) != len(ids) or set(packed) != {f"E{i}" for i in range(1, len(ids) + 1)}:
            raise ValueError("invalid original passage aliases")
        if not packed:
            if row["status"] != "refused" or row["reason"] != "insufficient_evidence":
                raise ValueError("empty evidence must remain original threshold refusal")
            continue
        for i, key in enumerate(ids, 1):
            if key not in units or units[key]["split"] != "dev":
                raise ValueError("same development source paragraph required")
            full = units[key]["text"]
            alias = f"E{i}"
            if packed[alias] != full[:1000]:
                raise ValueError("original clipped prefix differs from source")
            packed[alias] = full
    return result


# Only this private engine instance changes. Saved baseline metrics use unchanged
# answers/IDs; its evidence trace is restored for candidate merging, not rescoring text.
engine = module("run_grounded_answer")
prior_loader = engine.module
engine.module = lambda name: contract if name == "grounded_answer_contract" else prior_loader(name)
engine.ROOT, engine.APPROVAL, engine.PROPOSAL, engine.WORKER = ROOT, APPROVAL, PROPOSAL, WORKER
engine.approval = approval
original_baseline_rows = engine.baseline_rows
engine.baseline_rows = lambda expected: restore_rows(original_baseline_rows(expected), dev_units())
original_score = engine.score


def span_baseline_rows():
    report = json.loads(Path("reports/span-id-answer-development.json").read_text("utf-8"))
    return [
        json.loads(line)
        for line in (Path(report["run"]) / "predictions.jsonl").read_text("utf-8").splitlines()
    ]


def score(base, source, candidate, previous):
    result = original_score(base, source, candidate, previous)
    span = span_baseline_rows()
    if [r["query_id"] for r in span] != [r["query_id"] for r in candidate]:
        raise ValueError("span comparison roster/order differs")
    saved = module("run_gpu_generation").score(base, source, span)["candidate"]
    result["saved_span_id_baseline"] = saved
    result["gate"]["f1_exceeds_saved_span_id"] = (
        result["candidate"]["answerable_token_f1"] > saved["answerable_token_f1"]
    )
    result["passes_development_gate"] = all(result["gate"].values())
    return result


engine.score = score


def preflight():
    previous = module("run_span_id_answer")
    old, clipped_payloads = previous.preflight()
    verified = previous.engine.verify(previous.ROOT, old)
    report = json.loads(Path("reports/span-id-answer-development.json").read_text("utf-8"))
    if Path(report["run"]).resolve() != Path(verified["run"]).resolve():
        raise ValueError("span baseline report must identify the verified run")
    payloads = engine.payloads_for(engine.baseline_rows(old["baseline_run"]))
    contract.validate_payloads(payloads, 32)
    if [p["query_id"] for p in payloads] != [p["query_id"] for p in clipped_payloads]:
        raise ValueError("generation roster/order changed")
    snapshot = copy.deepcopy(old)
    paths = [
        Path(__file__).relative_to(Path.cwd()),
        WORKER,
        PROPOSAL,
        CORPUS,
        Path("scripts/intact_passage_contract.py"),
        Path("reports/span-id-answer-development.json"),
    ]
    paths += [p for p in Path(verified["run"]).iterdir() if p.is_file()]
    paths += [p for p in previous.ROOT.iterdir() if p.is_file()]
    for path in paths:
        snapshot["source_sha256"][path.as_posix()] = digest(path.read_bytes())
    snapshot.update(
        scope=contract.SCOPE,
        prior_span_snapshot_sha256=digest(canonical(old)),
        prior_span_run=verified["run"],
        inputs_sha256=digest(canonical(payloads)),
        messages_sha256=digest(canonical([contract.messages(p) for p in payloads])),
        span_catalog_sha256=digest(canonical([contract.catalog(p["evidence"]) for p in payloads])),
        protocol="same span-ID format and 2048/384 tokens; original fixed paragraphs, no clipping",
        gate="previous eleven conditions plus F1 strictly above saved span-ID result",
    )
    return snapshot, payloads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--run-approved", action="store_true")
    mode.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    snapshot, payloads = preflight()
    if args.run_approved:
        result = engine.launch(snapshot, payloads, ROOT)
    elif args.verify:
        result = engine.verify(ROOT, snapshot)
    else:
        result = dict(
            status="ready_for_authorization",
            model_calls=0,
            snapshot_sha256=digest(canonical(snapshot)),
            calls=len(payloads),
            limits=LIMITS,
            attempt_exists=ROOT.exists(),
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
