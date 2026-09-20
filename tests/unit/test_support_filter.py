import copy
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


def module():
    path = Path("scripts/run_support_filter.py")
    assert path.exists(), "support-filter experiment is not implemented"
    spec = importlib.util.spec_from_file_location("support_filter", path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def row(key="q", status="answered", answerable=True):
    return dict(
        query_id=key,
        family_id=key,
        question="What was measured?",
        answer="value",
        answerable=answerable,
        answer_criteria="REFERENCE_SECRET",
        supporting_evidence=["GOLD_SECRET"] if answerable else [],
        citation_ids=["cited"] if status == "answered" else [],
        status=status,
        reason=None,
        elapsed_ms=10,
        trace={
            "packed_ids": ["cited", "other"],
            "packed_evidence": {"E1": "Paper\nvalue", "E2": "UNCITED_SECRET"},
        },
    )


def test_checker_inputs_exclude_gold_reference_and_uncited_text():
    m = module()
    inputs = m.checker_input(row())
    assert set(inputs) == {"question", "proposed_answer", "cited_evidence"}
    assert inputs["cited_evidence"] == {"E1": "Paper\nvalue"}
    assert "SECRET" not in json.dumps(inputs)
    broken = row()
    broken["citation_ids"] = ["missing"]
    with pytest.raises(ValueError):
        m.checker_input(broken)


def test_filter_keeps_all_rows_and_counts_errors_as_failures(tmp_path):
    m = module()
    rows = [row(str(i)) for i in range(4)] + [row("refusal", "refused")]
    before = copy.deepcopy(rows)
    calls = []

    class Judge:
        def check(self, payload):
            assert "SECRET" not in json.dumps(payload)
            calls.append(payload)
            if len(calls) == 3:
                raise RuntimeError("synthetic error")
            return {
                "verdict": ["SUPPORTED", "UNSUPPORTED", "", "invalid"][len(calls) - 1],
                "raw": "synthetic",
                "output_tokens": 1,
            }

    result = m.filter_rows(rows, Judge(), lambda key: None, tmp_path / "predictions.jsonl")
    assert [r["status"] for r in result] == ["answered", "refused", "failure", "failure", "refused"]
    assert len(calls) == 4 and rows == before
    assert result[0]["answer"] == "value"
    assert all(not r["answer"] and not r["citation_ids"] for r in result[1:4])
    assert result[-1]["answer"] == rows[-1]["answer"]
    with pytest.raises(FileExistsError):
        m.filter_rows(rows, Judge(), lambda key: None, tmp_path / "predictions.jsonl")


def test_extra_quality_guards_reject_answer_collapse():
    m = module()
    control = [row("p"), row("n", "refused", False)]
    control[0].update(answer="wrong", citation_ids=["wrong"])
    candidate = copy.deepcopy(control)
    candidate[0].update(answer="REFERENCE_SECRET", citation_ids=["GOLD_SECRET"])
    assert m.summarize(control, candidate, candidate)["passes_development_gate"]
    collapsed = copy.deepcopy(candidate)
    collapsed[0].update(status="refused", answer="", citation_ids=[])
    assert not m.summarize(control, candidate, collapsed)["passes_development_gate"]


def test_approval_binds_exact_snapshot(tmp_path):
    m = module()
    snapshot = {"synthetic": True}
    p = tmp_path / "approval.json"
    with pytest.raises(FileNotFoundError):
        m.check_approval(snapshot, p)
    p.write_text(
        json.dumps(
            {
                "status": "approved",
                "scope": "support-filter-v1",
                "snapshot_sha256": m.digest(m.canonical(snapshot)),
            }
        )
    )
    m.check_approval(snapshot, p)
    with pytest.raises(ValueError):
        m.check_approval({"different": True}, p)


def test_supervisor_timeout_is_retained_and_cannot_restart(tmp_path, monkeypatch):
    m = module()
    calls = []

    class Process:
        def wait(self, timeout=None):
            if timeout is not None:
                raise subprocess.TimeoutExpired("synthetic", timeout)
            calls.append("waited")

        def kill(self):
            calls.append("killed")

    def spawn(args, **kwargs):
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert "run_support_filter.py" in args[3]
        return Process()

    monkeypatch.setattr(m.subprocess, "Popen", spawn)
    root = tmp_path / "attempt"
    assert m.launch(root, {"deadline_seconds": 1}) == 124
    assert calls == ["killed", "waited"]
    assert json.loads((root / "termination.json").read_text())["reason"] == "timeout"
    with pytest.raises(FileExistsError):
        m.launch(root, {"deadline_seconds": 1})


@pytest.mark.parametrize("case", ["valid", "context_limit", "model_error", "timeout"])
def test_real_judge_adapter_with_fake_model_is_bounded(tmp_path, monkeypatch, case):
    import torch

    from evidencebench import generation

    m = module()

    class Tokenizer:
        eos_token_id = 0

        def apply_chat_template(self, messages, **kwargs):
            assert "REFERENCE_SECRET" not in str(messages)
            assert "UNCITED_SECRET" not in str(messages)
            return {
                "input_ids": torch.ones(
                    (1, 1537 if case == "context_limit" else 2), dtype=torch.long
                )
            }

        def __call__(self, labels, **kwargs):
            assert labels == ["SUPPORTED", "UNSUPPORTED"]
            return {"input_ids": [[3], [4]]}

        def decode(self, tokens, **kwargs):
            return "SUPPORTED"

    class Model:
        def generate(self, **kwargs):
            assert kwargs["max_new_tokens"] == 8
            assert 0 < kwargs["max_time"] <= 20
            assert kwargs["prefix_allowed_tokens_fn"](0, [1, 1]) == [3, 4]
            if case == "model_error":
                raise RuntimeError("synthetic model failure")
            return torch.tensor([[1, 1, 3, 0]])

    class Loader:
        def __init__(self, config):
            self.tokenizer, self.model = Tokenizer(), Model()

    monkeypatch.setattr(generation, "LocalGenerator", Loader)
    budget = m.Budget(tmp_path / "usage.json", m.LIMITS)
    judge = m.SupportJudge({"base_snapshot": {"release": {"generation": {}}}}, budget)
    if case == "timeout":
        times = iter([0, 0, 21])
        monkeypatch.setattr(m.time, "perf_counter", lambda: next(times))
    if case == "valid":
        assert judge.check(m.checker_input(row())) == {
            "verdict": "SUPPORTED",
            "raw": "SUPPORTED",
            "output_tokens": 2,
            "generation_calls": 1,
        }
    else:
        with pytest.raises((ValueError, RuntimeError, TimeoutError)):
            judge.check(m.checker_input(row()))
    assert budget.used["support_calls"] == (0 if case == "context_limit" else 1)
    assert budget.used["reserved_tokens"] == (0 if case == "context_limit" else 8)


@pytest.mark.parametrize("tamper", ["reference", "zero_tokens", "nonanswer_raw"])
def test_full_synthetic_worker_verifies_and_detects_tampering(tmp_path, monkeypatch, tamper):
    from huggingface_hub import constants

    m = module()
    source = {"control": [row("a"), row("b"), row("n", "refused", False)]}
    source["constrained"] = copy.deepcopy(source["control"])
    monkeypatch.setattr(m, "original_rows", lambda: copy.deepcopy(source))
    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", True)

    class Judge:
        def __init__(self, snapshot, budget):
            self.budget = budget

        def check(self, payload):
            self.budget.charge("support_calls")
            self.budget.charge("reserved_tokens", 8)
            verdict = "SUPPORTED" if self.budget.used["support_calls"] == 1 else "UNSUPPORTED"
            return {"verdict": verdict, "raw": verdict, "output_tokens": 2, "generation_calls": 1}

    monkeypatch.setattr(m, "SupportJudge", Judge)
    root = tmp_path / "attempt"
    root.mkdir()
    snapshot = {"deadline_seconds": 1200, "synthetic": True}
    (root / "attempt.json").write_bytes(m.canonical({"token": "token", "snapshot": snapshot}))
    (root / "worker.started").write_text("token")
    m.execute(snapshot, root)
    termination = {"reason": "process_exit", "exit_code": 0, "elapsed_seconds": 1}
    (root / "termination.json").write_bytes(m.canonical(termination))
    result = m.verify(root, snapshot)
    assert result["actual_output_tokens"] == 4
    assert result["metrics"]["filtered"]["query_count"] == 3
    assert result["metrics"]["filtered"]["answered_count"] == 1
    run = Path(result["run"])
    manifest_path = run / "manifest.json"
    manifest = m.read(manifest_path)
    predictions = run / "predictions.jsonl"
    original = predictions.read_bytes()
    saved = [json.loads(line) for line in original.splitlines()]
    if tamper == "reference":
        saved[0]["answer_criteria"] = "tampered reference"
    elif tamper == "zero_tokens":
        saved[0]["support_check"]["output_tokens"] = 0
    else:
        saved[-1]["support_check"]["raw"] = "unexpected model output"
    predictions.write_bytes(b"\n".join(m.canonical(r) for r in saved) + b"\n")
    manifest["files"]["predictions.jsonl"] = m.digest(predictions.read_bytes())
    manifest_path.write_bytes(m.canonical(manifest))
    with pytest.raises(ValueError):
        m.verify(root, snapshot)
    predictions.write_bytes(original)
    manifest["files"]["predictions.jsonl"] = m.digest(original)
    manifest_path.write_bytes(m.canonical(manifest))
    (root / "termination.json").write_bytes(m.canonical({**termination, "reason": "timeout"}))
    with pytest.raises(ValueError, match="supervisor"):
        m.verify(root, snapshot)


def test_default_cli_is_read_only_and_approval_failure_prevents_launch(monkeypatch):
    m = module()
    monkeypatch.setattr(m, "preflight", lambda: {"synthetic": True})
    monkeypatch.setattr(m, "launch", lambda *args: pytest.fail("must not launch"))
    monkeypatch.setattr(m, "execute", lambda *args: pytest.fail("must not execute"))
    monkeypatch.setattr("sys.argv", ["run_support_filter.py"])
    m.main()

    def reject(snapshot):
        raise ValueError("synthetic approval rejection")

    monkeypatch.setattr(m, "check_approval", reject)
    monkeypatch.setattr("sys.argv", ["run_support_filter.py", "--run-approved"])
    with pytest.raises(ValueError, match="approval rejection"):
        m.main()


@pytest.mark.parametrize("guard", ["retain_80_percent_f1", "retain_half_answers"])
def test_each_retention_guard_can_reject_an_otherwise_passing_gate(guard):
    m = module()
    candidate = [row(str(i)) for i in range(5)] + [row("n", "refused", False)]
    for r in candidate[:-1]:
        r.update(answer="REFERENCE_SECRET", citation_ids=["GOLD_SECRET"])
    if guard == "retain_half_answers":
        for r in candidate[1:-1]:
            r["answer"] = "wrong"
    control = copy.deepcopy(candidate)
    for r in control[:-1]:
        r["answer"] = "wrong"
    filtered = copy.deepcopy(candidate)
    retained = 3 if guard == "retain_80_percent_f1" else 1
    for r in filtered[retained:-1]:
        r.update(status="refused", answer="", citation_ids=[])
    result = m.summarize(control, candidate, filtered)
    assert not result["gate"][guard]
    assert all(v for k, v in result["gate"].items() if k != guard)
    assert not result["passes_development_gate"]


def test_new_checker_failures_reject_even_if_control_had_more_failures():
    m = module()
    candidate = [row(str(i)) for i in range(5)] + [row("n", "refused", False)]
    for r in candidate[:-1]:
        r.update(answer="REFERENCE_SECRET", citation_ids=["GOLD_SECRET"])
    control = copy.deepcopy(candidate)
    for r in control[:-1]:
        r["answer"] = "wrong"
    control[0].update(status="failure", answer="", citation_ids=[])
    filtered = copy.deepcopy(candidate)
    filtered[0].update(status="failure", answer="", citation_ids=[])
    result = m.summarize(control, candidate, filtered)
    assert result["gate"]["failures_do_not_increase"]
    assert not result["gate"].get("no_new_checker_failures", True)
    assert not result["passes_development_gate"]
