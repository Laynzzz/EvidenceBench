"""Offline GPU span-generation worker; one explicitly approved attempt only."""

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


def validate(payloads, expected):
    if len(payloads) != expected or len({p["query_id"] for p in payloads}) != expected:
        raise ValueError("exact unique generation roster required")
    for p in payloads:
        if set(p) != {"query_id", "system_prompt", "user_prompt", "choices"}:
            raise ValueError("only whitelisted prompt fields allowed")
        if not all(
            isinstance(p[k], str) and p[k] for k in ("query_id", "system_prompt", "user_prompt")
        ):
            raise ValueError("text prompts required")
        if not isinstance(p["choices"], list) or not p["choices"] or p["choices"][0] != "UNKNOWN":
            raise ValueError("refusal choice required")
        if not all(isinstance(c, str) and c for c in p["choices"]) or len(set(p["choices"])) != len(
            p["choices"]
        ):
            raise ValueError("unique text choices required")


class Meter:
    def __init__(self, path, limit):
        self.path, self.limit, self.calls = path, limit, 0
        with path.open("xb") as stream:
            stream.write(support().encoded(self.value()))

    def value(self):
        return {"calls": self.calls, "reserved_tokens": 64 * self.calls, "call_limit": self.limit}

    def charge(self):
        if self.calls >= self.limit:
            raise ValueError("generation budget exhausted")
        self.calls += 1
        temp = self.path.with_suffix(".tmp")
        temp.write_bytes(support().encoded(self.value()))
        temp.replace(self.path)


class Trie:
    def __init__(self, paths, prompt_length, eos):
        self.root, self.prompt_length, self.eos = {}, prompt_length, eos
        for path in paths:
            node = self.root
            for token in path:
                node = node.setdefault(int(token), {})
            node[None] = {}

    def __call__(self, batch_id, ids):
        tail = ids[self.prompt_length :]
        tokens = tail.tolist() if hasattr(tail, "tolist") else tail
        node = self.root
        for token in tokens:
            if int(token) not in node:
                raise ValueError("invalid span prefix")
            node = node[int(token)]
        return sorted(self.eos if key is None else key for key in node)


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
                if result["raw"] not in p["choices"]:
                    raise ValueError("output not in eligible choices")
            except Exception as exc:
                result.update(getattr(generate, "last_trace", {}))
                result["reason"] = type(exc).__name__
            result.update(
                elapsed_ms=(time.perf_counter() - start) * 1000,
                generation_calls=meter.calls - before,
            )
            if result["elapsed_ms"] > 20000:
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
                [
                    {"role": "system", "content": payload["system_prompt"]},
                    {"role": "user", "content": payload["user_prompt"]},
                ],
                add_generation_prompt=True,
                return_tensors="pt",
                return_dict=True,
            ).to("cuda:0")
            length = inputs["input_ids"].shape[1]
            if length > 1536:
                raise ValueError("context limit")
            encoded = tokenizer(payload["choices"], add_special_tokens=False)["input_ids"]
            paths = [p for p in encoded if 0 < len(p) < 64]
            trie = Trie(paths, length, tokenizer.eos_token_id)
            remaining = 20 - (time.perf_counter() - start)
            if remaining <= 0:
                raise TimeoutError("preprocessing timeout")
            meter.charge()
            with torch.inference_mode():
                output = model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=64,
                    max_time=remaining,
                    prefix_allowed_tokens_fn=trie,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
            generated = output[0][length:]
            self.last_trace = {
                "raw": tokenizer.decode(generated, skip_special_tokens=True).strip(),
                "output_tokens": len(generated),
            }
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
        or approval.get("scope") != "gpu-generation-v1"
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
