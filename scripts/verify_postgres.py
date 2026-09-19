"""Real-model/vector-store smoke; no labels or benchmark-quality claims."""

import json
import os
from pathlib import Path

import numpy as np
import yaml
from dotenv import load_dotenv

from evidencebench.indexing import load_encoder, load_index
from evidencebench.ingestion import canonical, load_units
from evidencebench.retrieval import DenseRetriever
from evidencebench.storage import VectorStore
from evidencebench.tracking import environment


def main():
    load_dotenv(".env")
    config = yaml.safe_load(Path("configs/retrieval.yaml").read_text())
    corpus = Path(config["corpus"])
    units = load_units(corpus)
    fingerprint = json.loads((corpus / "manifest.json").read_text())["fingerprint"]
    vectors, metadata = load_index(Path(config["index"]), units, fingerprint)
    store = VectorStore(os.environ["EVIDENCEBENCH_DATABASE_URL"])
    try:
        store.import_index(metadata["fingerprint"], units, vectors)
    except ValueError as exc:
        if "already exists" not in str(exc):
            raise
    model = load_encoder(config)
    rows = []
    for query in [
        "What is a policy enforcement point?",
        "How should source code be protected?",
        "How do organizations verify backups?",
    ]:
        vector = model.encode_query(query, normalize_embeddings=True, show_progress_bar=False)
        reference = DenseRetriever(units, vectors, lambda _, v=vector: v).retrieve(query, {}, 10)
        actual = store.search(metadata["fingerprint"], vector, {}, 10)
        assert [h.element_id for h in reference] == [h.element_id for h in actual]
        np.testing.assert_allclose(
            [h.retrieval_score for h in reference], [h.retrieval_score for h in actual], atol=1e-6
        )
        rows.append({"query": query, "top10_ids": [h.element_id for h in actual], "match": True})
    result = {
        "kind": "real-model PostgreSQL parity smoke, not quality evaluation",
        "queries": rows,
        "index_fingerprint": metadata["fingerprint"],
        "environment": environment(),
    }
    output = Path("artifacts/verification/postgres-parity.json")
    output.write_bytes(canonical(result))
    print(f"PASS: PostgreSQL/local top-10 parity on {len(rows)} queries. Saved {output}")


if __name__ == "__main__":
    main()
