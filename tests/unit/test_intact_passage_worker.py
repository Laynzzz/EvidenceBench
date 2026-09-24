import importlib.util
import json
from pathlib import Path

import pytest


def load(name="intact_passage_worker"):
    path = Path("scripts") / f"{name}.py"
    assert path.exists(), "intact-passage worker not implemented"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def payloads():
    return [
        dict(query_id=str(i), question="Which models?", evidence={"E1": "Title\n" + "x " * 750})
        for i in range(32)
    ]


def attempt(tmp_path, monkeypatch, worker, mutation=None):
    helpers = worker.support()
    run = tmp_path / "attempt" / "runs" / "synthetic"
    run.mkdir(parents=True)
    root = run.parent.parent
    source = tmp_path / "source.py"
    source.write_text("original")
    model = tmp_path / "model"
    model.mkdir()
    weights = model / "model.safetensors"
    weights.write_bytes(b"synthetic model checksum fixture; never loaded")
    (run / "inputs.json").write_bytes(helpers.encoded(payloads()))
    snapshot = dict(
        scope="intact-passage-v1",
        limits=dict(calls=32, max_new_tokens=384, reserved_tokens=12288),
        deadline_seconds=1200,
        source_sha256={str(source): helpers.sha(source)},
        runtime={"synthetic": True},
        model_dir=str(model),
        model_sha256={"model.safetensors": helpers.sha(weights)},
        inputs_sha256=helpers.sha(run / "inputs.json"),
    )
    if mutation == "snapshot_scope":
        snapshot["scope"] = "span-id-answer-v1"
    if mutation == "limits":
        snapshot["limits"]["calls"] = 33
    if mutation == "deadline":
        snapshot["deadline_seconds"] = 1201
    (run / "config.json").write_bytes(helpers.encoded(snapshot))
    checksum = helpers.sha(run / "config.json")
    (root / "attempt.json").write_bytes(
        helpers.encoded(dict(token="one", snapshot_sha256=checksum))
    )
    approval = dict(
        status="approved",
        scope="intact-passage-v1",
        snapshot_sha256=checksum,
        limits=dict(
            attempts=1,
            generation_calls=32,
            reserved_output_tokens=12288,
            worker_deadline_seconds=1200,
            external_spend_usd=0,
        ),
    )
    if mutation == "approval_scope":
        approval["scope"] = "span-id-answer-v1"
    if mutation == "approval_hash":
        approval["snapshot_sha256"] = "wrong"
    if mutation == "allowance":
        approval["limits"]["attempts"] = 2
    if mutation == "approval_status":
        approval["status"] = "pending"
    (root / "authorization.json").write_bytes(helpers.encoded(approval))
    monkeypatch.setenv("HF_HUB_OFFLINE", "0" if mutation == "offline" else "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(helpers, "runtime_info", lambda: {"synthetic": mutation != "runtime"})
    monkeypatch.setattr(worker, "support", lambda: helpers)
    if mutation == "source":
        source.write_text("changed")
    if mutation == "input":
        (run / "inputs.json").write_text("[]")
    if mutation == "model":
        weights.write_bytes(b"changed")
    if mutation == "config":
        (run / "config.json").write_text("{}")
    return run


@pytest.mark.parametrize(
    "mutation",
    [
        "snapshot_scope",
        "approval_scope",
        "approval_hash",
        "approval_status",
        "allowance",
        "limits",
        "deadline",
        "offline",
        "runtime",
        "source",
        "input",
        "model",
        "config",
        "token",
    ],
)
def test_tampering_rejected_before_model_loading(tmp_path, monkeypatch, mutation):
    worker = load()
    run = attempt(tmp_path, monkeypatch, worker, mutation)
    monkeypatch.setattr(
        worker, "load_generator", lambda _: pytest.fail("must reject before model loading")
    )
    with pytest.raises(ValueError):
        worker.run_worker(run, "wrong" if mutation == "token" else "one")
    assert not (run / "worker-complete.json").exists()


def test_intact_inputs_reach_metered_worker_and_attempt_cannot_repeat(tmp_path, monkeypatch):
    worker = load()
    run = attempt(tmp_path, monkeypatch, worker)

    def generate(payload, meter):
        assert payload["evidence"]["E1"] == "Title\n" + "x " * 750
        message = json.loads(worker.contract.messages(payload)[1]["content"])
        assert sum(len(q.split()) for q in message["evidence"]["E1"]["spans"].values()) == 750
        meter.charge()
        return {"raw": '{"answer":"","span_ids":[]}', "output_tokens": 12}

    monkeypatch.setattr(worker, "load_generator", lambda _: (generate, {"synthetic": True}))
    worker.run_worker(run, "one")
    usage = json.loads((run / "usage.json").read_text())
    assert usage == dict(calls=32, reserved_tokens=12288, call_limit=32)
    decisions = [json.loads(line) for line in (run / "decisions.jsonl").read_text().splitlines()]
    assert len(decisions) == 32
    assert all(d["reason"] is None and d["generation_calls"] == 1 for d in decisions)
    receipt = json.loads((run / "worker-complete.json").read_text())
    assert receipt["status"] == "complete"
    assert receipt["snapshot_sha256"] == worker.support().sha(run / "config.json")
    assert all(worker.support().sha(run / p) == h for p, h in receipt["files"].items())
    before = (run / "decisions.jsonl").read_bytes()
    with pytest.raises(FileExistsError):
        worker.run_worker(run, "one")
    assert (run / "decisions.jsonl").read_bytes() == before


def test_private_adapter_keeps_frozen_worker_input_contract_isolated():
    frozen = load("span_id_answer_worker")
    worker = load()
    worker.validate(payloads(), 32)
    with pytest.raises(ValueError):
        frozen.validate(payloads(), 32)
    with pytest.raises(ValueError):
        load("span_id_answer_worker").validate(payloads(), 32)
    with pytest.raises(ValueError):
        frozen.backend.contract().messages(payloads()[0])
    assert worker.contract.parse('{"answer":"","span_ids":[]}', {"E1": "Title\nText."})["refused"]
