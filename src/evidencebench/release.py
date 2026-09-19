"""Final evaluation accepts only the frozen code, data and named comparisons."""

from pathlib import Path

from evidencebench.ingestion import canonical, digest
from evidencebench.protocol import verify_protocol


def verify_final_lock(
    path: Path,
    examples: list,
    corpus_fingerprint: str,
    systems: list[str],
    provenance: dict | None = None,
) -> dict:
    lock = verify_protocol(path)
    if sorted(systems) != sorted(lock["systems"]):
        raise ValueError("final comparison systems differ from release freeze")
    if corpus_fingerprint != lock["corpus_fingerprint"]:
        raise ValueError("final corpus differs from release freeze")
    if provenance != lock.get("provenance"):
        raise ValueError("final runtime provenance differs from release freeze")
    if (
        digest(canonical([q.model_dump(mode="json") for q in examples]))
        != lock["test_examples_hash"]
    ):
        raise ValueError("final examples differ from release freeze")
    return lock
