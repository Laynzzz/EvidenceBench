import pytest


def test_final_guard_requires_matching_code_labels_and_systems(tmp_path):
    from evidencebench.ingestion import canonical, digest
    from evidencebench.release import verify_final_lock

    code = tmp_path / "code.py"
    code.write_text("original")
    lock = tmp_path / "release-lock.json"
    lock.write_bytes(
        canonical(
            {
                "files": {str(code): digest(code.read_bytes())},
                "systems": ["baseline", "selected"],
                "corpus_fingerprint": "fp",
                "test_examples_hash": digest(canonical([])),
            }
        )
    )
    verify_final_lock(lock, [], "fp", ["baseline", "selected"])
    with pytest.raises(ValueError, match="provenance"):
        verify_final_lock(lock, [], "fp", ["baseline", "selected"], {"checkpoint": "wrong"})
    with pytest.raises(ValueError, match="systems"):
        verify_final_lock(lock, [], "fp", ["selected"])
    code.write_text("changed")
    with pytest.raises(ValueError, match="frozen"):
        verify_final_lock(lock, [], "fp", ["baseline", "selected"])
