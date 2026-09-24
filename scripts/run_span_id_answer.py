"""Span-ID answer experiment; default is read-only preparation, never inference."""

import argparse
import copy
import importlib.util
import json
from pathlib import Path

from evidencebench.ingestion import canonical, digest

ROOT = Path("artifacts/span-id-answer-v1")
APPROVAL = Path("reports/span-id-answer-authorization.json")
PROPOSAL = Path("docs/span-id-answer-proposal.md")
WORKER = Path("scripts/span_id_answer_worker.py")


def module(name):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


contract = module("span_id_answer_contract")
ALLOWANCE, LIMITS = contract.ALLOWANCE, contract.LIMITS


def approval(snapshot, path=APPROVAL):
    record = json.loads(path.read_text("utf-8"))
    if (
        record.get("status") != "approved"
        or record.get("scope") != contract.SCOPE
        or record.get("snapshot_sha256") != digest(canonical(snapshot))
        or record.get("limits") != ALLOWANCE
    ):
        raise ValueError("new exact-snapshot span-ID approval required")
    return record


# A private adapter reuses the reviewed supervision, metering, merge and scoring.
# Its globals are isolated from every predecessor loaded through importlib.
engine = module("run_grounded_answer")
prior_loader = engine.module
engine.module = lambda name: contract if name == "grounded_answer_contract" else prior_loader(name)
engine.ROOT, engine.APPROVAL, engine.PROPOSAL, engine.WORKER = ROOT, APPROVAL, PROPOSAL, WORKER
engine.approval = approval


def preflight():
    previous = module("run_grounded_answer")
    old, payloads = previous.preflight()
    verified = previous.verify(previous.ROOT, old)
    contract.validate_payloads(payloads, 32)
    snapshot = copy.deepcopy(old)
    paths = [
        Path(__file__).relative_to(Path.cwd()),
        WORKER,
        PROPOSAL,
        Path("scripts/span_id_answer_contract.py"),
        Path("reports/grounded-answer-development.json"),
    ]
    paths += [p for p in Path(verified["run"]).iterdir() if p.is_file()]
    paths += [p for p in previous.ROOT.iterdir() if p.is_file()]
    for path in paths:
        snapshot["source_sha256"][path.as_posix()] = digest(path.read_bytes())
    snapshot.update(
        scope=contract.SCOPE,
        prior_complete_snapshot_sha256=digest(canonical(old)),
        prior_complete_run=verified["run"],
        limits=copy.deepcopy(LIMITS),
        messages_sha256=digest(canonical([contract.messages(p) for p in payloads])),
        span_catalog_sha256=digest(canonical([contract.catalog(p["evidence"]) for p in payloads])),
        protocol=(
            "answer <=80 words; select 1-3 span IDs; deterministic <=40-word body "
            "spans and <=120-word total quotes; same 2048/384 token and 30-second limits"
        ),
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
            snapshot_sha256=digest(canonical(snapshot)),
            calls=len(payloads),
            limits=snapshot["limits"],
            attempt_exists=ROOT.exists(),
            model_calls=0,
        )
    print(json.dumps(result))


if __name__ == "__main__":
    main()
