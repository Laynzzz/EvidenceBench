"""Offline complete-answer worker; one explicitly approved attempt only."""

import argparse
import hashlib
import importlib.util
import json
import os
import time
from pathlib import Path


def support():
    p = Path(__file__).with_name("gpu_support_worker.py")
    spec = importlib.util.spec_from_file_location("support_helpers", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def contract():
    path = Path(__file__).with_name("grounded_answer_contract.py")
    spec = importlib.util.spec_from_file_location("answer_contract", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate(payloads, expected):
    contract().validate_payloads(payloads, expected)


class Meter:
    def __init__(self, path, limit):
        self.path, self.limit, self.calls = path, limit, 0
        with path.open("xb") as stream:
            stream.write(support().encoded(self.value()))

    def value(self):
        return {"calls": self.calls, "reserved_tokens": 384 * self.calls, "call_limit": self.limit}

    def charge(self):
        if self.calls >= self.limit:
            raise ValueError("generation budget exhausted")
        self.calls += 1
        temp = self.path.with_suffix(".tmp")
        temp.write_bytes(support().encoded(self.value()))
        temp.replace(self.path)


def evaluate(payloads, generate, run):
    helpers = support()
    validate(payloads, len(payloads))
    meter = Meter(run / "usage.json", len(payloads))
    with (run / "decisions.jsonl").open("xb") as stream:
        for i, p in enumerate(payloads, 1):
            start, before = time.perf_counter(), meter.calls
            result = {
                "query_id": p["query_id"],
                "input_sha256": hashlib.sha256(helpers.encoded(p)).hexdigest(),
                "raw": "",
                "output_tokens": 0,
                "reason": None,
            }
            try:
                result.update(generate(p, meter))
            except Exception as exc:
                result.update(getattr(generate, "last_trace", {}))
                result["reason"] = type(exc).__name__
            result.update(
                elapsed_ms=(time.perf_counter() - start) * 1000,
                generation_calls=meter.calls - before,
            )
            if result["elapsed_ms"] > 30000:
                result["reason"] = "timeout"
            stream.write(helpers.encoded(result) + b"\n")
            stream.flush()
            print(f"GPU generation {i}/{len(payloads)}", flush=True)


def load_generator(snapshot):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    if not torch.cuda.is_available() or "RTX 4090" not in torch.cuda.get_device_name(0):
        raise RuntimeError("approved RTX 4090 CUDA device 0 required")
    free, total = torch.cuda.mem_get_info(0)
    if free < 17 * 1024**3:
        raise RuntimeError("at least 17 GiB free VRAM required")
    torch.set_num_threads(4)
    tokenizer = AutoTokenizer.from_pretrained(
        snapshot["model_dir"], local_files_only=True, trust_remote_code=False
    )
    model = AutoModelForCausalLM.from_pretrained(
        snapshot["model_dir"],
        local_files_only=True,
        trust_remote_code=False,
        torch_dtype=torch.bfloat16,
        device_map={"": "cuda:0"},
        attn_implementation="sdpa",
    )
    model.eval()
    if any(p.device.type != "cuda" or p.dtype != torch.bfloat16 for p in model.parameters()):
        raise RuntimeError("all model parameters must be CUDA BF16")

    class Generate:
        last_trace = {}

        def __call__(self, payload, meter):
            self.last_trace = {"raw": "", "output_tokens": 0}
            start = time.perf_counter()
            inputs = tokenizer.apply_chat_template(
                contract().messages(payload),
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to("cuda:0")
            length = inputs["input_ids"].shape[1]
            if length > 2048:
                raise ValueError("context limit")
            remaining = 30 - (time.perf_counter() - start)
            if remaining <= 0:
                raise TimeoutError("preprocessing timeout")
            meter.charge()
            with torch.inference_mode():
                output = model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=384,
                    max_time=remaining,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            generated = output[0][length:]
            self.last_trace = {
                "raw": tokenizer.decode(generated, skip_special_tokens=True).strip(),
                "output_tokens": len(generated),
            }
            if len(generated) >= 384 and int(generated[-1]) != tokenizer.eos_token_id:
                raise ValueError("output token limit reached without EOS")
            return self.last_trace

    return Generate(), {
        "gpu": torch.cuda.get_device_name(0),
        "device": "cuda:0",
        "dtype": "bfloat16",
        "free_vram_before_load": free,
        "total_vram": total,
    }


def run_worker(run, token):
    helpers = support()
    root = run.parent.parent
    snapshot = json.loads((run / "config.json").read_text("utf-8"))
    attempt = json.loads((root / "attempt.json").read_text("utf-8"))
    approval = json.loads((root / "authorization.json").read_text("utf-8"))
    expected = hashlib.sha256(helpers.encoded(snapshot)).hexdigest()
    if (
        attempt["token"] != token
        or attempt["snapshot_sha256"] != expected
        or approval.get("snapshot_sha256") != expected
        or approval.get("status") != "approved"
        or approval.get("scope") != "grounded-answer-v1"
    ):
        raise ValueError("exact approved generation attempt required")
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
    validate(payloads, 32)
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", type=Path, required=True)
    p.add_argument("--token", required=True)
    args = p.parse_args()
    run_worker(args.run, args.token)


if __name__ == "__main__":
    main()
