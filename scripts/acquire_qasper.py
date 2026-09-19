"""Fetch checksum-pinned public QASPER v0.3 archives and extract JSON members only."""

import io
import tarfile
from pathlib import Path

import httpx

from evidencebench.ingestion import digest

ARCHIVES = {
    "qasper-train-dev-v0.3.tgz": "a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a",
    "qasper-test-and-evaluator-v0.3.tgz": (
        "72a52a41193e2838b8074f80ac074b94f956b84886c36a61c58a7df4171bdd72"
    ),
}


def main():
    root = Path("data/raw/qasper")
    root.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120, follow_redirects=True) as client:
        for name, expected in ARCHIVES.items():
            path = root / name
            content = (
                path.read_bytes()
                if path.exists()
                else client.get(f"https://qasper-dataset.s3.us-west-2.amazonaws.com/{name}")
                .raise_for_status()
                .content
            )
            if digest(content) != expected:
                raise ValueError(f"QASPER archive checksum mismatch: {name}")
            path.write_bytes(content)
            with tarfile.open(fileobj=io.BytesIO(content), mode="r:gz") as archive:
                for member in archive.getmembers():
                    basename = Path(member.name).name
                    if member.isfile() and basename in {
                        "qasper-train-v0.3.json",
                        "qasper-dev-v0.3.json",
                        "qasper-test-v0.3.json",
                    }:
                        stream = archive.extractfile(member)
                        if stream is None:
                            raise ValueError("missing archive member")
                        (root / basename).write_bytes(stream.read())
            print(f"Verified {name}")


if __name__ == "__main__":
    main()
