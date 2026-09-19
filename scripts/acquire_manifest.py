"""Maintainer-only corpus acquisition. Review changes before accepting a new manifest."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pdfplumber

SOURCES = [
    ("800-207", "dev"),
    ("800-218", "dev"),
    ("800-137", "test"),
    ("800-153", "test"),
    ("800-167", "train"),
    ("800-193", "train"),
    ("800-63b-4", "train"),
    ("800-61r3", "train"),
    ("800-46r2", "train"),
    ("800-34r1", "train"),
]


def main():
    destination = Path("data/manifests/nist-cybersecurity.json")
    if destination.exists():
        raise SystemExit("Manifest already exists; do not silently update frozen sources")
    raw = Path("data/raw")
    raw.mkdir(parents=True, exist_ok=True)
    sources = []
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        for number, split in SOURCES:
            url = f"https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.{number}.pdf"
            if number in {"800-137", "800-153", "800-34r1"}:
                url = f"https://nvlpubs.nist.gov/nistpubs/Legacy/SP/nistspecialpublication{number}.pdf"
            response = client.get(url)
            response.raise_for_status()
            data = response.content
            if not data.startswith(b"%PDF-") or len(data) > 30_000_000:
                raise ValueError(f"Invalid or oversized PDF: {number}")
            document_id = f"nist-sp-{number}"
            path = raw / f"{document_id}.pdf"
            path.write_bytes(data)
            with pdfplumber.open(path) as pdf:
                count = len(pdf.pages)
            sources.append(
                dict(
                    document_id=document_id,
                    family_id=f"nist-sp-{number.split('r')[0].split('b')[0]}",
                    version=number,
                    url=url,
                    sha256=hashlib.sha256(data).hexdigest(),
                    retrieved_at=datetime.now(UTC).date().isoformat(),
                    page_count=count,
                    split=split,
                    mime_type="application/pdf",
                    license=(
                        "NIST technical publication; generally public domain in US. "
                        "Preserve attribution; third-party material may have separate rights."
                    ),
                )
            )
            print(f"{document_id}: {count} pages, {len(data)} bytes", flush=True)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps({"sources": sources}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
