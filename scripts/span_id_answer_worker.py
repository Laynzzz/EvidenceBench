"""One approved span-ID generation attempt; reuse frozen inference machinery."""

import argparse
import importlib.util
import json
import os
from pathlib import Path


def load(name):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


contract = load("span_id_answer_contract")
backend = load("grounded_answer_worker")
# Only this private module instance is adapted. The frozen module and files stay intact.
backend.contract = lambda: contract
support = backend.support
validate = backend.validate
evaluate = backend.evaluate
load_generator = backend.load_generator


def run_worker(run, token):
    helpers = support()
    root = run.parent.parent
    snapshot = json.loads((run / "config.json").read_text("utf-8"))
    attempt = json.loads((root / "attempt.json").read_text("utf-8"))
    approval = json.loads((root / "authorization.json").read_text("utf-8"))
    expected = helpers.sha(run / "config.json")
    if (
        attempt.get("token") != token
        or attempt.get("snapshot_sha256") != expected
        or approval.get("snapshot_sha256") != expected
        or approval.get("status") != "approved"
        or approval.get("scope") != contract.SCOPE
        or approval.get("limits") != contract.ALLOWANCE
        or snapshot.get("scope") != contract.SCOPE
        or snapshot.get("limits") != contract.LIMITS
        or snapshot.get("deadline_seconds") != 1200
    ):
        raise ValueError("exact approved span-ID attempt required")
    with (root / "worker.started").open("x", encoding="utf-8") as stream:
        stream.write(token)
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise ValueError("offline execution required")
    for name, h in snapshot["source_sha256"].items():
        if helpers.sha(Path(name)) != h:
            raise ValueError("approved source changed")
    helpers.verify_model_files(snapshot)
    if (
        helpers.runtime_info() != snapshot["runtime"]
        or helpers.sha(run / "inputs.json") != snapshot["inputs_sha256"]
    ):
        raise ValueError("approved runtime or input changed")
    payloads = json.loads((run / "inputs.json").read_text("utf-8"))
    validate(payloads, contract.CALL_LIMIT)
    generate, hardware = load_generator(snapshot)
    evaluate(payloads, generate, run)
    (run / "worker-complete.json").write_bytes(
        helpers.encoded(
            {
                "status": "complete",
                "snapshot_sha256": expected,
                "hardware": hardware,
                "files": {
                    name: helpers.sha(run / name) for name in ("decisions.jsonl", "usage.json")
                },
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--token", required=True)
    args = parser.parse_args()
    run_worker(args.run, args.token)


if __name__ == "__main__":
    main()
