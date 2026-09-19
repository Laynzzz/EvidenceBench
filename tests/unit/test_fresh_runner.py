import json
import subprocess

import pytest

from evidencebench.evaluation.fresh_runner import claim_worker, launch


def test_timeout_kills_waits_and_keeps_single_attempt(tmp_path, monkeypatch):
    calls = []

    class Process:
        def wait(self, timeout=None):
            calls.append(("wait", timeout))
            if timeout is not None:
                raise subprocess.TimeoutExpired("synthetic", timeout)
            return -1

        def kill(self):
            calls.append(("kill",))

    def spawn(command, **kwargs):
        assert kwargs["env"]["HF_HUB_OFFLINE"] == "1"
        assert kwargs["env"]["TRANSFORMERS_OFFLINE"] == "1"
        return Process()

    monkeypatch.setattr(subprocess, "Popen", spawn)
    root = tmp_path / "attempt"
    assert launch(root, {"synthetic": True}, seconds=1) == 124
    assert ("kill",) in calls and ("wait", None) in calls
    assert json.loads((root / "termination.json").read_text())["reason"] == "timeout"
    with pytest.raises(FileExistsError):
        launch(root, {"synthetic": True}, seconds=1)


def test_watchdog_subtracts_process_startup_from_total_deadline(tmp_path, monkeypatch):
    from evidencebench.evaluation import fresh_runner

    times = iter([10.0, 10.4, 10.5])
    monkeypatch.setattr(fresh_runner.time, "monotonic", lambda: next(times))

    class Process:
        def wait(self, timeout=None):
            assert timeout == pytest.approx(0.6)
            return 0

    monkeypatch.setattr(subprocess, "Popen", lambda *args, **kwargs: Process())
    assert launch(tmp_path / "attempt", {}, seconds=1) == 0


def test_spawn_failure_consumes_attempt_and_worker_cannot_start_twice(tmp_path, monkeypatch):
    def broken(command, **kwargs):
        raise OSError("synthetic launch failure")

    monkeypatch.setattr(subprocess, "Popen", broken)
    root = tmp_path / "attempt"
    with pytest.raises(OSError):
        launch(root, {}, seconds=1)
    record = json.loads((root / "attempt.json").read_text())
    assert (root / "termination.json").exists()
    with pytest.raises(ValueError, match="token"):
        claim_worker(root, "wrong")
    claim_worker(root, record["token"])
    with pytest.raises(FileExistsError):
        claim_worker(root, record["token"])


def test_cached_model_configs_are_required_and_all_cached_files_hashed(tmp_path, monkeypatch):
    import huggingface_hub

    from evidencebench.evaluation.fresh_runner import cached_model_files

    names = [
        "config.json",
        "tokenizer_config.json",
        "tokenizer.json",
        "model.safetensors",
        "modules.json",
        "config_sentence_transformers.json",
        "sentence_bert_config.json",
        "1_Pooling/config.json",
        "vocab.txt",
        "special_tokens_map.json",
    ]
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}")
    monkeypatch.setattr(
        huggingface_hub,
        "try_to_load_from_cache",
        lambda repo_id, filename, revision: str(tmp_path / filename),
    )
    model = {"model_id": "synthetic", "revision": "a" * 40}
    before = cached_model_files(model, "retrieval")
    (tmp_path / "special_tokens_map.json").write_text('{"changed":true}')
    after = cached_model_files(model, "retrieval")
    assert before["special_tokens_map.json"] != after["special_tokens_map.json"]
    (tmp_path / "1_Pooling/config.json").unlink()
    with pytest.raises(ValueError, match="cache"):
        cached_model_files(model, "retrieval")


def test_full_worker_with_synthetic_models_retains_index_predictions_and_usage(
    tmp_path, monkeypatch
):
    from types import SimpleNamespace

    import numpy as np
    from huggingface_hub import constants

    from evidencebench import generation, generation_spans, indexing, reranking
    from evidencebench.evaluation import fresh_runner
    from evidencebench.ingestion import digest
    from evidencebench.schemas import ContentUnit

    unit = ContentUnit(
        element_id="gold",
        document_id="paper",
        family_id="paper",
        version="1",
        split="dev",
        page=1,
        text="Paper\nsource",
        source_checksum="a" * 64,
        source_url="https://example.org/paper",
    )
    queries = [
        SimpleNamespace(
            query_id=key,
            text="Synthetic question?",
            split="dev",
            family_id="paper",
            answerable=answerable,
            answer_criteria="source" if answerable else "SECRET",
            supporting_evidence=["gold"] if answerable else [],
        )
        for key, answerable in [("p", True), ("n", False)]
    ]

    class Encoder:
        def encode_document(self, texts, **kwargs):
            assert texts == ["Paper\nsource"]
            return np.ones((1, 3), dtype=np.float32) / np.sqrt(3)

        def encode_query(self, text, **kwargs):
            assert text == "Synthetic question?"
            return np.ones(3, dtype=np.float32) / np.sqrt(3)

    class Ranker:
        def predict(self, pairs, **kwargs):
            assert pairs == [("Synthetic question?", "Paper\nsource")]
            return np.array([4.0])

    class Model:
        def generate(self, **kwargs):
            return None

    class Generator:
        def __init__(self, config):
            self.config, self.model, self.tokenizer = config, Model(), None

        def generate(self, text, packed):
            assert packed == {"E1": "Paper\nsource"}
            assert text == "Synthetic question?"
            self.model.generate(max_new_tokens=64 if self.config.get("variant") else 100)
            self.last_output = "synthetic source"
            return {
                "status": "answered",
                "answer": "source",
                "reason": None,
                "evidence_ids": ["E1"],
            }

    monkeypatch.setattr(constants, "HF_HUB_OFFLINE", True)
    monkeypatch.setenv("HF_HUB_OFFLINE", "1")
    monkeypatch.setenv("TRANSFORMERS_OFFLINE", "1")
    monkeypatch.setattr(fresh_runner, "load_units", lambda _: [unit])
    monkeypatch.setattr(fresh_runner, "read_labels", lambda _: queries)
    monkeypatch.setattr(indexing, "load_encoder", lambda _: Encoder())
    monkeypatch.setattr(reranking, "load_cross_encoder", lambda _: Ranker())
    monkeypatch.setattr(generation, "LocalGenerator", Generator)
    monkeypatch.setattr(generation_spans, "SpanGenerator", Generator)
    snapshot = {
        "dataset_fingerprint": "b" * 64,
        "release": {"retrieval": {}, "reranker": {}, "generation": {"refusal_threshold": 3.0}},
    }
    fresh_runner.execute(snapshot, tmp_path)
    run = next((tmp_path / "runs").iterdir())
    manifest = json.loads((run / "manifest.json").read_text())
    assert manifest["status"] == "complete"
    for name, checksum in manifest["files"].items():
        assert digest((run / name).read_bytes()) == checksum
    assert (run / "index/embeddings.npy").exists()
    used = json.loads((run / "usage.json").read_text())["used"]
    assert used["document_embeddings"] == 1
    assert used["query_embeddings"] == used["reranker_pairs"] == 2
    assert used["control_calls"] == used["constrained_calls"] == 2
    assert used["reserved_tokens"] == 328
    assert len((run / "control.jsonl").read_text().splitlines()) == 2
    from evidencebench.evaluation.fresh_verification import verify_run

    (tmp_path / "attempt.json").write_text(json.dumps({"snapshot": snapshot, "token": "synthetic"}))
    (tmp_path / "worker.started").write_text("synthetic")
    termination = tmp_path / "termination.json"
    termination.write_text(json.dumps({"reason": "process_exit", "exit_code": 0}))
    assert verify_run(run, queries, [unit])["status"] == "verified"
    termination.write_text(json.dumps({"reason": "timeout", "exit_code": 124}))
    with pytest.raises(ValueError, match="supervisor"):
        verify_run(run, queries, [unit])
    termination.write_text(json.dumps({"reason": "process_exit", "exit_code": 0}))
    with (run / "control.jsonl").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="checksum"):
        verify_run(run, queries, [unit])
