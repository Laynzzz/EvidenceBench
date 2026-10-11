"""Isolated offline worker for one approved claim-grounded answer attempt."""

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


contract = load("claim_grounded_contract")
backend = load("grounded_answer_worker")
# Reuse the reviewed model loader and metered generation loop with this contract.
backend.contract = lambda: contract
support = backend.support
validate = backend.validate
evaluate = backend.evaluate
load_generator = backend.load_generator


def prompt_lengths(payloads, tokenizer):
    validate(payloads, len(payloads))
    result = []
    for payload in payloads:
        encoded = tokenizer.apply_chat_template(
            contract.messages(payload), add_generation_prompt=True
        )
        length = len(encoded["input_ids"] if isinstance(encoded, dict) else encoded)
        if length > contract.MAX_INPUT_TOKENS:
            raise ValueError(f"prompt exceeds {contract.MAX_INPUT_TOKENS} tokens")
        result.append({"query_id": payload["query_id"], "input_tokens": length})
    return result


def inspect(model_dir, inputs_path):
    import torch
    from transformers import AutoTokenizer

    helpers = support()
    payloads = json.loads(inputs_path.read_text("utf-8"))
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir, local_files_only=True, trust_remote_code=False
    )
    if torch.version.cuda is None:
        raise RuntimeError("the pinned CUDA runtime is required for prompt inspection")
    return {
        "runtime": helpers.runtime_info(),
        "prompt_lengths": prompt_lengths(payloads, tokenizer),
    }


def run_worker(run, token):
    helpers = support()
    backend.support = support
    backend.validate = validate
    backend.evaluate = evaluate
    backend.load_generator = load_generator
    root = run.parent.parent
    snapshot = json.loads((run / "config.json").read_text("utf-8"))
    attempt = json.loads((root / "attempt.json").read_text("utf-8"))
    approval = json.loads((root / "authorization.json").read_text("utf-8"))
    expected = helpers.sha(run / "config.json")
    try:
        specification = contract.specification(snapshot.get("scope"))
    except ValueError as exc:
        raise ValueError("worker requires exact approved claim-grounded attempt") from exc
    if (
        attempt.get("token") != token
        or attempt.get("snapshot_sha256") != expected
        or attempt.get("consumes_single_attempt") is not True
        or approval.get("status") != "approved"
        or approval.get("scope") != snapshot.get("scope")
        or approval.get("snapshot_sha256") != expected
        or approval.get("limits") != specification["allowance"]
        or snapshot.get("limits") != specification["limits"]
        or snapshot.get("deadline_seconds") != specification["deadline_seconds"]
    ):
        raise ValueError("worker requires exact approved claim-grounded attempt")
    with (root / "worker.started").open("x", encoding="utf-8") as stream:
        stream.write(token)
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise ValueError("offline execution required")
    for name, expected_hash in snapshot["source_sha256"].items():
        if helpers.sha(Path(name)) != expected_hash:
            raise ValueError("approved source changed")
    for name, expected_hash in snapshot["baseline_source_sha256"].items():
        if helpers.sha(Path(name)) != expected_hash:
            raise ValueError("frozen baseline changed")
    helpers.verify_model_files(snapshot)
    if (
        helpers.runtime_info() != snapshot["runtime"]
        or helpers.sha(run / "inputs.json") != snapshot["inputs_sha256"]
    ):
        raise ValueError("approved runtime or inputs changed")
    payloads = json.loads((run / "inputs.json").read_text("utf-8"))
    validate(payloads, specification["limits"]["calls"])
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
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--inspect", action="store_true")
    mode.add_argument("--run", type=Path)
    parser.add_argument("--model-dir", type=Path)
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--token")
    args = parser.parse_args()
    if args.inspect:
        if args.model_dir is None or args.inputs is None:
            parser.error("--inspect requires --model-dir and --inputs")
        print(json.dumps(inspect(args.model_dir, args.inputs)))
    else:
        if args.token is None:
            parser.error("--run requires --token")
        run_worker(args.run, args.token)


if __name__ == "__main__":
    main()
