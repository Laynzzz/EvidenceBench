import json

import numpy as np
import pytest
from test_retrieval import make_units


def test_index_roundtrip_checks_corpus_order_and_tampering(tmp_path):
    from evidencebench.indexing import load_index, save_index

    root = tmp_path / "index"
    units = make_units()
    vectors = np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.2]], dtype=np.float32)
    save_index(
        root,
        units,
        vectors,
        {"corpus_fingerprint": "a" * 64, "model_id": "fixture", "revision": "b" * 40},
    )
    restored, meta = load_index(root, units, "a" * 64)
    np.testing.assert_allclose(restored, vectors)
    assert meta["dimension"] == 2
    with pytest.raises(ValueError, match="order"):
        load_index(root, list(reversed(units)), "a" * 64)
    with pytest.raises(ValueError, match="corpus"):
        load_index(root, units, "c" * 64)
    np.save(root / "embeddings.npy", np.ones((3, 2)))
    with pytest.raises(ValueError, match="checksum"):
        load_index(root, units, "a" * 64)
    assert json.loads((root / "manifest.json").read_text())["model_id"] == "fixture"
