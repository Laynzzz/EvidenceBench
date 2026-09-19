"""Freeze data and scoring before selection. Print counts/hashes, not test examples."""

import json
from pathlib import Path

from evidencebench.ingestion import canonical, digest, load_units
from evidencebench.labels import read_labels, validate_labels

corpus = Path("data/processed/qasper-v1")
labels_dir = Path("data/labels/qasper-v1")
units = load_units(corpus)
examples = [
    q for split in ("train", "dev", "test") for q in read_labels(labels_dir / f"{split}.jsonl")
]
counts = validate_labels(examples, units)
if counts["splits"] != {"train": 200, "dev": 50, "test": 100}:
    raise ValueError("predeclared query counts not met")
selection = {
    "query_ids": {
        split: [q.query_id for q in examples if q.split == split]
        for split in ("train", "dev", "test")
    },
    "paper_ids": sorted({q.family_id.removeprefix("qasper-") for q in examples}),
}
protocol = {
    "name": "qasper-derived-v1",
    "counts": counts,
    "files": {
        str(p).replace("\\", "/"): digest(p.read_bytes())
        for p in [
            *sorted(labels_dir.glob("*.jsonl")),
            corpus / "manifest.json",
            Path("data/manifests/qasper-v1.json"),
        ]
    },
    "ranking": "binary upstream evidence; unjudged treated nonrelevant; answerable denominator",
    "metrics": ["recall_at_5", "recall_at_10", "recall_at_20", "ndcg_at_10", "mrr"],
    "selection_metric": "ndcg_at_10",
    "candidate_k": 50,
    "refusal_calibration": (
        "maximize balanced accuracy of upstream answerability on dev top score; "
        "tie prefers higher coverage"
    ),
    "answer_scoring": (
        "maximum normalized token F1 against human alternatives; "
        "refusals/failures zero on answerable questions"
    ),
    "citation_scoring": (
        "ID validity, quoted-span presence, upstream evidence precision/recall; "
        "not semantic entailment"
    ),
    "test_policy": (
        "no model selection from test; one frozen final comparison; "
        "failed release requires protocol reset"
    ),
}
for filename, value in (("qasper-selection.json", selection), ("qasper-protocol.json", protocol)):
    target = Path("data/manifests") / filename
    content = canonical(value)
    if target.exists() and target.read_bytes() != content:
        raise ValueError("refusing to replace a frozen benchmark protocol")
    target.write_bytes(content)
print(json.dumps(counts))
