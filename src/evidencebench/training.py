"""Train-only pair construction; query subsets are nested under a fixed seed."""

import hashlib
import logging
import time
from pathlib import Path

from evidencebench.labels import mine_negatives, validate_labels
from evidencebench.retrieval import BM25Retriever
from evidencebench.schemas import ContentUnit, QueryExample


def prepare_pairs(
    examples: list[QueryExample],
    units: list[ContentUnit],
    count: int,
    negatives: int,
    seed: int,
    method: str,
) -> list[dict]:
    if any(q.split != "train" for q in examples):
        raise ValueError("pair preparation accepts training labels only")
    validate_labels(examples, units)
    ordered = sorted(
        (q for q in examples if q.answerable),
        key=lambda q: hashlib.sha256(f"{seed}:{q.query_id}".encode()).hexdigest(),
    )
    if not 1 <= count <= len(ordered):
        raise ValueError("insufficient distinct training queries")
    lookup = {u.element_id: u for u in units}
    rows = []
    lexical = BM25Retriever([u for u in units if u.split == "train"]) if method == "hard" else None
    for query in ordered[:count]:
        selected = [(key, 1.0) for key in sorted(query.supporting_evidence)]
        selected += [
            (key, 0.0) for key in mine_negatives(query, units, negatives, seed, method, lexical)
        ]
        for key, label in selected:
            rows.append(
                {
                    "query_id": query.query_id,
                    "element_id": key,
                    "query": query.text,
                    "passage": lookup[key].text,
                    "label": label,
                }
            )
    return rows


def train(config: dict, smoke: bool = False) -> Path:
    """Adapted from train-sentence-transformers' cross-encoder production template.

    Uses project family splits, local MLflow, CPU fp32, and no Hub publication.
    Selection uses the shared end-to-end metric with an unchanged candidate pool.
    """
    import numpy as np
    import torch
    import yaml
    from datasets import Dataset
    from sentence_transformers import (
        CrossEncoderModelCardData,
        CrossEncoderTrainer,
        CrossEncoderTrainingArguments,
    )
    from sentence_transformers.cross_encoder.losses import BinaryCrossEntropyLoss
    from sentence_transformers.evaluation import SentenceEvaluator
    from transformers import EarlyStoppingCallback, TrainerCallback, set_seed

    from evidencebench.evaluation.metrics import score_ranking
    from evidencebench.ingestion import canonical, digest
    from evidencebench.labels import read_labels
    from evidencebench.pipelines import load_retrievers
    from evidencebench.protocol import verify_protocol
    from evidencebench.reranking import checkpoint_hash, load_cross_encoder
    from evidencebench.tracking import create_run, log_mlflow, run_lifecycle

    verify_protocol(Path(config["protocol"]))

    budget = yaml.safe_load(Path(config["budget_config"]).read_text("utf-8"))["training"]
    if not smoke and not budget["enabled"]:
        raise ValueError("training budget is not enabled")
    root = Path(config["runs_dir"])
    completed_or_started = list(root.glob("*/config.json"))
    if len(completed_or_started) >= budget["max_runs"]:
        raise ValueError("shared training run budget exhausted")
    set_seed(config["seed"])
    retrieval = yaml.safe_load(Path(config["retrieval_config"]).read_text("utf-8"))
    units, retrievers, metadata = load_retrievers(retrieval)
    training = read_labels(Path(config["train_labels"]))
    development = read_labels(Path(config["dev_labels"]))
    if any(q.split != "dev" for q in development):
        raise ValueError("training selection requires development labels only")
    validate_labels(development, units)
    rows = prepare_pairs(
        training,
        units,
        min(4, config["query_count"]) if smoke else config["query_count"],
        config["negatives"],
        config["subset_seed"],
        config["negative_method"],
    )
    run_config = {
        **config,
        "smoke": smoke,
        "corpus_fingerprint": metadata["fingerprint"],
        "index_fingerprint": metadata["index_fingerprint"],
        "train_pairs_hash": digest(canonical(rows)),
        "dev_labels_hash": digest(canonical([q.model_dump(mode="json") for q in development])),
    }
    run, manifest = create_run(root, run_config)
    with run_lifecycle(run, manifest, budget["max_seconds_per_run"]) as check_deadline:
        logging.basicConfig(
            level=logging.INFO,
            force=True,
            handlers=[logging.StreamHandler(), logging.FileHandler(run / "training.log")],
        )
        for noisy in ("httpx", "httpcore", "huggingface_hub", "urllib3", "filelock", "fsspec"):
            logging.getLogger(noisy).setLevel(logging.WARNING)
        (run / "pairs.jsonl").write_bytes(b"\n".join(canonical(row) for row in rows) + b"\n")
        model = load_cross_encoder(config["model"])
        model.model_card_data = CrossEncoderModelCardData(
            language="en",
            license="apache-2.0",
            model_name="EvidenceBench TinyBERT reranker adapted on QASPER-derived training data",
        )
        model.model_card_data.register_model(model)
        check_deadline()
        lookup = {u.element_id: u for u in units}
        examples = [q for q in development if q.answerable]
        if smoke:
            examples = examples[:2]
        candidates = {
            q.query_id: retrievers["hybrid"].retrieve(q.text, {}, config["candidate_k"])
            for q in examples
        }
        (run / "dev-candidates.json").write_bytes(
            canonical({k: [h.element_id for h in v] for k, v in candidates.items()})
        )

        class Evaluator(SentenceEvaluator):
            primary_metric = "dev_ndcg_at_10"
            greater_is_better = True

            def __init__(self):
                self.history = []

            def __call__(self, model, output_path=None, epoch=-1, steps=-1, **kwargs):
                values = []
                for q in examples:
                    check_deadline()
                    hits = candidates[q.query_id]
                    pairs = [(q.text, lookup[h.element_id].text) for h in hits]
                    scores = model.predict(
                        pairs, batch_size=config["batch_size"], show_progress_bar=False
                    )
                    if not np.isfinite(scores).all():
                        raise ValueError("nonfinite development scores")
                    ordered = sorted(
                        zip(hits, scores, strict=True), key=lambda x: (-x[1], x[0].element_id)
                    )
                    values.append(
                        score_ranking([h.element_id for h, _ in ordered], q.relevance, 10)["ndcg"]
                    )
                metrics = {self.primary_metric: float(np.mean(values))}
                self.history.append({"epoch": epoch, "steps": steps, **metrics})
                (run / "selection-history.json").write_bytes(canonical(self.history))
                return metrics

        started = time.perf_counter()

        class Deadline(TrainerCallback):
            def on_step_end(self, args, state, control, **kwargs):
                if time.perf_counter() - started > budget["max_seconds_per_run"]:
                    raise TimeoutError("shared local training time bound exceeded")

        evaluator = Evaluator()
        baseline_eval = evaluator(model)[evaluator.primary_metric]
        dataset = Dataset.from_list(
            [{k: r[k] for k in ("query", "passage", "label")} for r in rows]
        )
        n_pos = sum(row["label"] == 1 for row in rows)
        pos_weight = (len(rows) - n_pos) / n_pos
        loss = BinaryCrossEntropyLoss(model, pos_weight=torch.tensor(pos_weight))
        args = CrossEncoderTrainingArguments(
            output_dir=str(run / "checkpoints"),
            num_train_epochs=config["epochs"],
            max_steps=1 if smoke else -1,
            per_device_train_batch_size=config["batch_size"],
            per_device_eval_batch_size=config["batch_size"],
            learning_rate=config["learning_rate"],
            weight_decay=0.01,
            warmup_steps=0.1,
            lr_scheduler_type="linear",
            bf16=False,
            fp16=False,
            use_cpu=True,
            eval_strategy="epoch",
            save_strategy="epoch",
            save_total_limit=1,
            logging_steps=1 if smoke else 10,
            logging_first_step=True,
            load_best_model_at_end=True,
            metric_for_best_model=f"eval_{evaluator.primary_metric}",
            greater_is_better=True,
            report_to="none",
            seed=config["seed"],
            data_seed=config["seed"],
            dataloader_num_workers=0,
            dataloader_pin_memory=False,
            push_to_hub=False,
        )
        trainer = CrossEncoderTrainer(
            model=model,
            args=args,
            train_dataset=dataset,
            loss=loss,
            evaluator=evaluator,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=3), Deadline()],
        )
        try:
            trainer.train()
            score = evaluator(model)[evaluator.primary_metric]
            final = run / "final"
            model.save_pretrained(str(final))
            model_hash = checkpoint_hash(final)
            reloaded = load_cross_encoder(
                {**config["model"], "checkpoint": str(final), "checkpoint_hash": model_hash}
            )
            probe = [(rows[0]["query"], rows[0]["passage"])]
            np.testing.assert_allclose(model.predict(probe), reloaded.predict(probe), atol=1e-6)
            delta = score - baseline_eval
            verdict = "WIN" if delta >= 0.005 else "MARGINAL" if delta >= 0 else "REGRESSION"
            metrics = {
                "dev_ndcg_at_10": score,
                "baseline_ndcg_at_10": baseline_eval,
                "delta": delta,
                "elapsed_seconds": time.perf_counter() - started,
                "query_count": len({r["query_id"] for r in rows}),
                "pair_count": len(rows),
                "positive_pairs": n_pos,
                "pos_weight": pos_weight,
            }
            logging.info(
                "VERDICT: %s | score=%.4f | baseline=%.4f | delta=%+.4f",
                verdict,
                score,
                baseline_eval,
                delta,
            )
            (run / "metrics.json").write_bytes(canonical(metrics))
            (run / "loss-history.json").write_bytes(canonical(trainer.state.log_history))
            manifest.update(
                status="complete",
                checkpoint_hash=model_hash,
                checkpoint=str(final),
                reload_verified=True,
                verdict=verdict,
                **metrics,
            )
            check_deadline()
            manifest["mlflow_run_id"] = log_mlflow(run, run_config, metrics)
        except Exception as exc:
            manifest.update(
                status="failed",
                error=type(exc).__name__,
                elapsed_seconds=time.perf_counter() - started,
            )
            raise
        finally:
            (run / "manifest.json").write_bytes(canonical(manifest))
    return run
