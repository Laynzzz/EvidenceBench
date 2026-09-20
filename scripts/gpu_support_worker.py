"""Isolated CUDA worker: only whitelisted cited-evidence payloads, no labels/scoring."""

import argparse
import hashlib
import importlib.metadata
import json
import os
import time
from pathlib import Path


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def runtime_info():
    # Import/metadata inspection only; no CUDA allocation, tensor workload or model load.
    import torch
    import transformers

    return {
        "packages": dict(
            sorted(
                (d.metadata["Name"].lower(), d.version) for d in importlib.metadata.distributions()
            )
        ),
        "torch": torch.__version__,
        "cuda_build": torch.version.cuda,
        "transformers": transformers.__version__,
    }


def verify_model_files(snapshot):
    root = Path(snapshot["model_dir"])
    actual = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.relative_to(root).parts[0] != ".cache"
    }
    if actual != set(snapshot["model_sha256"]):
        raise ValueError("model file inventory differs from approved checkpoint")
    for name, h in snapshot["model_sha256"].items():
        if sha(root / name) != h:
            raise ValueError("model artifact changed")


def validate_payloads(rows, expected):
    if len(rows) != expected or len({r["query_id"] for r in rows}) != len(rows):
        raise ValueError("exact unique query roster required")
    for row in rows:
        if set(row) != {"query_id", "input"} or set(row["input"]) != {
            "question",
            "proposed_answer",
            "cited_evidence",
        }:
            raise ValueError("only whitelisted input fields allowed")
        p = row["input"]
        if not isinstance(p["question"], str) or not isinstance(p["proposed_answer"], str):
            raise ValueError("question and answer must be text")
        if not p["cited_evidence"] or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in p["cited_evidence"].items()
        ):
            raise ValueError("cited evidence must be nonempty text")


class Meter:
    def __init__(self, path, limit):
        self.path, self.limit, self.calls = path, limit, 0
        with path.open("xb") as f:
            f.write(encoded({"calls": 0, "reserved_tokens": 0, "call_limit": limit}))

    def charge(self):
        if self.calls >= self.limit:
            raise ValueError("call budget exhausted")
        self.calls += 1
        temp = self.path.with_suffix(".tmp")
        temp.write_bytes(
            encoded(
                {"calls": self.calls, "reserved_tokens": 8 * self.calls, "call_limit": self.limit}
            )
        )
        temp.replace(self.path)


def prefix_constraint(paths, prompt_length, eos):
    def allowed(batch_id, ids):
        prefix = list(ids[prompt_length:])
        tokens = set()
        for path in paths:
            if path[: len(prefix)] == prefix:
                tokens.add(eos if len(path) == len(prefix) else path[len(prefix)])
        if not tokens:
            raise ValueError("invalid constrained token prefix")
        return sorted(tokens)

    return allowed


def evaluate(payloads, judge, run):
    validate_payloads(payloads, len(payloads))
    meter = Meter(run / "usage.json", len(payloads))
    output = run / "decisions.jsonl"
    with output.open("xb"):
        pass
    rows = []
    for payload in payloads:
        before = meter.calls
        started = time.perf_counter()
        result = {
            "query_id": payload["query_id"],
            "input_sha256": hashlib.sha256(encoded(payload["input"])).hexdigest(),
            "verdict": "FAILURE",
            "reason": None,
            "raw": "",
            "output_tokens": 0,
        }
        try:
            result.update(judge(payload["input"], meter))
            if result["raw"] not in {"SUPPORTED", "UNSUPPORTED"}:
                raise ValueError("invalid checker output")
            result.update(
                verdict=result["raw"],
                reason="unsupported" if result["raw"] == "UNSUPPORTED" else None,
            )
        except Exception as exc:
            result.update(getattr(judge, "last_trace", {}))
            result.update(verdict="FAILURE", reason=type(exc).__name__)
        result.update(
            elapsed_ms=(time.perf_counter() - started) * 1000, generation_calls=meter.calls - before
        )
        if result["elapsed_ms"] > 20000:
            result.update(verdict="FAILURE", reason="timeout")
        rows.append(result)
        with output.open("ab") as stream:
            stream.write(encoded(result) + b"\n")
        print(f"GPU support checks {len(rows)}/{len(payloads)}", flush=True)
    return rows


def load_judge(snapshot):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; CPU fallback prohibited")
    if "RTX 4090" not in torch.cuda.get_device_name(0):
        raise RuntimeError("approved RTX 4090 must be CUDA device 0")
    free, total = torch.cuda.mem_get_info(0)
    if free < 17 * 1024**3:
        raise RuntimeError("less than 17 GiB free VRAM; no processes will be closed")
    torch.set_num_threads(4)
    model_dir = snapshot["model_dir"]
    tokenizer = AutoTokenizer.from_pretrained(
        model_dir, local_files_only=True, trust_remote_code=False
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_dir,
        local_files_only=True,
        trust_remote_code=False,
        torch_dtype=torch.bfloat16,
        device_map={"": "cuda:0"},
        attn_implementation="sdpa",
    )
    model.eval()
    if any(p.device.type != "cuda" or p.dtype != torch.bfloat16 for p in model.parameters()):
        raise RuntimeError("model must be entirely CUDA BF16")
    paths = tokenizer(["SUPPORTED", "UNSUPPORTED"], add_special_tokens=False)["input_ids"]
    if any(not 0 < len(p) < 8 for p in paths):
        raise ValueError("decision labels exceed token limit")

    class Judge:
        last_trace = {}

        def __call__(self, payload, meter):
            self.last_trace = {"raw": "", "output_tokens": 0}
            start = time.perf_counter()
            inputs = tokenizer.apply_chat_template(
                [
                    {"role": "system", "content": snapshot["system_prompt"]},
                    {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
                ],
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to("cuda:0")
            length = inputs["input_ids"].shape[1]
            if length > 1536:
                raise ValueError("checker context limit")
            remaining = 20 - (time.perf_counter() - start)
            if remaining <= 0:
                raise TimeoutError("checker preprocessing timeout")
            meter.charge()
            with torch.inference_mode():
                output = model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=8,
                    max_time=remaining,
                    prefix_allowed_tokens_fn=prefix_constraint(
                        paths, length, tokenizer.eos_token_id
                    ),
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            generated = output[0][length:]
            self.last_trace = {
                "raw": tokenizer.decode(generated, skip_special_tokens=True).strip(),
                "output_tokens": len(generated),
            }
            return self.last_trace

    return Judge(), {
        "gpu": torch.cuda.get_device_name(0),
        "free_vram_before_load": free,
        "total_vram": total,
        "dtype": "bfloat16",
        "device": "cuda:0",
    }


def run_worker(run, token):
    root = run.parent.parent
    snapshot = json.loads((run / "config.json").read_text("utf-8"))
    attempt = json.loads((root / "attempt.json").read_text("utf-8"))
    approval = json.loads((root / "authorization.json").read_text("utf-8"))
    expected = hashlib.sha256(encoded(snapshot)).hexdigest()
    if (
        attempt["token"] != token
        or attempt["snapshot_sha256"] != expected
        or approval.get("status") != "approved"
        or approval.get("scope") != "gpu-support-v1"
        or approval.get("snapshot_sha256") != expected
    ):
        raise ValueError("worker requires exact approved attempt")
    with (root / "worker.started").open("x", encoding="utf-8") as f:
        f.write(token)
    if os.environ.get("HF_HUB_OFFLINE") != "1" or os.environ.get("TRANSFORMERS_OFFLINE") != "1":
        raise RuntimeError("offline worker required")
    for name, h in snapshot["source_sha256"].items():
        if sha(Path(name)) != h:
            raise ValueError("worker source changed")
    verify_model_files(snapshot)
    if sha(run / "inputs.json") != snapshot["inputs_sha256"]:
        raise ValueError("input artifact changed")
    payloads = json.loads((run / "inputs.json").read_text("utf-8"))
    validate_payloads(payloads, 28)
    if runtime_info() != snapshot["runtime"]:
        raise ValueError("GPU runtime differs from approved snapshot")
    judge, hardware = load_judge(snapshot)
    evaluate(payloads, judge, run)
    (run / "worker-complete.json").write_bytes(
        encoded(
            {
                "status": "complete",
                "snapshot_sha256": expected,
                "hardware": hardware,
                "files": {name: sha(run / name) for name in ("decisions.jsonl", "usage.json")},
            }
        )
    )


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inspect", action="store_true")
    p.add_argument("--run", type=Path)
    p.add_argument("--token")
    args = p.parse_args()
    if args.inspect:
        print(json.dumps(runtime_info()))
    elif args.run and args.token:
        run_worker(args.run, args.token)
    else:
        p.error("read-only --inspect, or an approved worker run and token, required")


if __name__ == "__main__":
    main()
