"""Load the frozen release index into the local database without replacing it."""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from evidencebench.indexing import load_index
from evidencebench.ingestion import load_units
from evidencebench.storage import VectorStore


def main():
    load_dotenv()
    release = yaml.safe_load(Path("configs/release.yaml").read_text("utf-8"))
    config = release["retrieval"]
    units = load_units(Path(config["corpus"]))
    vectors, metadata = load_index(Path(config["index"]), units, release["corpus_fingerprint"])
    if metadata["fingerprint"] != release["index_fingerprint"]:
        raise ValueError("release index mismatch")
    store = VectorStore(os.environ[config["database_url_env"]])
    try:
        store.import_index(metadata["fingerprint"], units, vectors)
    except ValueError as exc:
        if "already exists" not in str(exc):
            raise
    if not store.ready(metadata["fingerprint"], len(units)):
        raise ValueError("existing database index is incomplete; inspect before recovery")
    print(f"Verified {len(units)} release evidence rows")


if __name__ == "__main__":
    main()
