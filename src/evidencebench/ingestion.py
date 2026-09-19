"""Checksum-verified PDF ingestion and content-addressed corpus artifacts."""

import hashlib
import importlib.metadata
import json
import re
from pathlib import Path
from typing import Any

import httpx
import pdfplumber
import pyarrow as pa
import pyarrow.parquet as pq

from evidencebench.chunking import NORMALIZATION_VERSION, chunk_words
from evidencebench.schemas import ContentUnit, CorpusManifest, SourceDocument


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fetch_source(source: SourceDocument, raw_dir: Path, max_bytes: int = 30_000_000) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    path = raw_dir / f"{source.document_id}.pdf"
    if path.exists():
        if digest(path.read_bytes()) != source.sha256:
            raise ValueError(f"cached source checksum mismatch: {source.document_id}")
        return path
    with httpx.stream("GET", str(source.url), follow_redirects=True, timeout=60) as response:
        response.raise_for_status()
        if response.headers.get("content-type", "").split(";")[0] != "application/pdf":
            raise ValueError(f"unexpected MIME type: {source.document_id}")
        data = bytearray()
        for block in response.iter_bytes():
            data.extend(block)
            if len(data) > max_bytes:
                raise ValueError("source download exceeds size limit")
    if digest(data) != source.sha256:
        raise ValueError(f"download checksum mismatch: {source.document_id}")
    path.write_bytes(data)
    return path


def extract_source(
    path: Path, source: SourceDocument, max_words: int = 180, overlap: int = 30
) -> tuple[list[ContentUnit], dict[str, Any]]:
    data = path.read_bytes()
    if digest(data) != source.sha256:
        raise ValueError(f"source checksum mismatch: {source.document_id}")
    if not data.startswith(b"%PDF-"):
        raise ValueError("source is not a PDF")
    units: list[ContentUnit] = []
    empty = []
    with pdfplumber.open(path, unicode_norm="NFKC") as pdf:
        if len(pdf.pages) != source.page_count:
            raise ValueError(f"page count mismatch: {source.document_id}")
        for page in pdf.pages:
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                empty.append(page.page_number)
            for ordinal, (text, bbox) in enumerate(chunk_words(words, max_words, overlap)):
                identity = [
                    source.sha256,
                    page.page_number,
                    ordinal,
                    text,
                    max_words,
                    overlap,
                    NORMALIZATION_VERSION,
                ]
                units.append(
                    ContentUnit(
                        element_id=digest(canonical(identity)),
                        document_id=source.document_id,
                        family_id=source.family_id,
                        version=source.version,
                        split=source.split,
                        page=page.page_number,
                        text=text,
                        bbox=bbox,
                        source_checksum=source.sha256,
                        source_url=source.url,
                    )
                )
            page.close()
    if not units:
        raise ValueError(f"no extractable text; OCR is out of scope: {source.document_id}")
    if len(empty) / source.page_count > 0.2:
        raise ValueError(f"too many pages without text: {source.document_id}")
    return units, {
        "document_id": source.document_id,
        "empty_pages": empty,
        "page_count": source.page_count,
        "unit_count": len(units),
    }


def audit_similar_documents(
    units: list[ContentUnit], threshold: float = 0.85
) -> list[dict[str, Any]]:
    """Full-document word 5-shingle Jaccard; this flags duplication, not semantic overlap."""
    texts: dict[str, list[str]] = {}
    families = {}
    for unit in units:
        texts.setdefault(unit.document_id, []).append(unit.text)
        families[unit.document_id] = unit.family_id
    shingles = {}
    for key, parts in texts.items():
        words = re.findall(r"\w+", " ".join(parts).lower())
        shingles[key] = {tuple(words[i : i + 5]) for i in range(max(0, len(words) - 4))}
    hits = []
    keys = sorted(shingles)
    for i, left in enumerate(keys):
        for right in keys[i + 1 :]:
            a, b = shingles[left], shingles[right]
            score = len(a & b) / len(a | b) if a | b else 0
            if score >= threshold and families[left] != families[right]:
                hits.append({"left": left, "right": right, "jaccard": score})
    return hits


def build_corpus(config: dict[str, Any], output: Path, fetch: bool = True) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(f"immutable output already exists: {output}")
    manifest = CorpusManifest.model_validate_json(Path(config["manifest"]).read_text("utf-8"))
    max_words, overlap = config.get("max_words", 180), config.get("overlap", 30)
    raw = Path(config["raw_dir"])
    units, diagnostics = [], []
    for source in sorted(manifest.sources, key=lambda item: item.document_id):
        path = fetch_source(source, raw) if fetch else raw / f"{source.document_id}.pdf"
        records, check = extract_source(path, source, max_words, overlap)
        units.extend(records)
        diagnostics.append(check)
    if len({u.element_id for u in units}) != len(units):
        raise ValueError("duplicate element IDs")
    similar = audit_similar_documents(units)
    if similar:
        raise ValueError(f"near-duplicate documents need family review: {similar}")
    records = [u.model_dump(mode="json") for u in units]
    recipe = {
        "schema_version": 1,
        "normalization": NORMALIZATION_VERSION,
        "extractor": {p: importlib.metadata.version(p) for p in ("pdfplumber", "pdfminer-six")},
        "max_words": max_words,
        "overlap": overlap,
        "sources": [
            s.model_dump(mode="json") for s in sorted(manifest.sources, key=lambda x: x.document_id)
        ],
        "records_hash": digest(canonical(records)),
    }
    report = {
        "fingerprint": digest(canonical(recipe)),
        "recipe": recipe,
        "unit_count": len(units),
        "documents": diagnostics,
        "near_duplicate_flags": similar,
    }
    output.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(records), output / "units.parquet")
    (output / "manifest.json").write_bytes(canonical(report))
    return report


def load_units(output: Path) -> list[ContentUnit]:
    records = pq.read_table(output / "units.parquet").to_pylist()
    manifest = json.loads((output / "manifest.json").read_text("utf-8"))
    if digest(canonical(records)) != manifest["recipe"]["records_hash"]:
        raise ValueError("processed corpus checksum mismatch")
    if digest(canonical(manifest["recipe"])) != manifest["fingerprint"]:
        raise ValueError("corpus manifest fingerprint mismatch")
    return [ContentUnit.model_validate(row) for row in records]
