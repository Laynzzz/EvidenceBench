import os

import numpy as np
import pytest


@pytest.mark.integration
def test_postgres_roundtrip_and_filtered_cosine_rank():
    from evidencebench.schemas import ContentUnit
    from evidencebench.storage import VectorStore

    dsn = os.environ.get("EVIDENCEBENCH_TEST_DATABASE_URL")
    if not dsn:
        pytest.skip("Set EVIDENCEBENCH_TEST_DATABASE_URL for the real database integration test")
    units = [
        ContentUnit(
            element_id=key,
            document_id=key,
            family_id=family,
            version="1",
            split="train",
            page=1,
            text=key,
            source_checksum="a" * 64,
            source_url="https://example.org/fixture.pdf",
        )
        for key, family in [("a", "backup"), ("b", "network"), ("c", "backup")]
    ]
    store = VectorStore(dsn)
    fingerprint = "fixture-" + os.urandom(8).hex()
    store.import_index(fingerprint, units, np.array([[1.0, 0.0], [0.0, 1.0], [0.8, 0.2]]))
    assert store.search(fingerprint, np.array([0.0, 1.0]), {}, 3)[0].element_id == "b"
    hits = store.search(fingerprint, np.array([0.0, 1.0]), {"family_id": "backup"}, 3)
    assert [h.element_id for h in hits] == ["c", "a"]
    assert len(store.search(fingerprint, np.array([0.0, 1.0]), {"document_id": "absent"}, 3)) == 0
    with pytest.raises(ValueError, match="missing"):
        store.search("absent", np.array([0.0, 1.0]), {}, 3)
    with pytest.raises(ValueError, match="dimension"):
        store.search(fingerprint, np.ones(3), {}, 3)
    with pytest.raises(ValueError, match="already exists"):
        store.import_index(fingerprint, units, np.ones((3, 2)))
    assert store.ready(fingerprint, 3)
    import psycopg

    with psycopg.connect(dsn) as conn:
        conn.execute("DELETE FROM eb_evidence WHERE index_id=%s AND element_id='a'", (fingerprint,))
    assert not store.ready(fingerprint, 3)
    with psycopg.connect(dsn) as conn:
        conn.execute("DELETE FROM eb_evidence WHERE index_id=%s", (fingerprint,))
        conn.execute("DELETE FROM eb_indexes WHERE fingerprint=%s", (fingerprint,))
