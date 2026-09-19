"""Build or verify fresh QASPER data; stdout contains aggregates, never test content."""

import argparse
import importlib.metadata
import json
import logging
import sys
from collections import Counter
from pathlib import Path

import httpx
import pdfplumber
import pyarrow as pa
import pyarrow.parquet as pq
from pdfminer.pdfexceptions import PDFException
from pdfplumber.utils.exceptions import PdfminerException

from evidencebench.chunking import normalize
from evidencebench.fresh_data import align_paper, download_pdf
from evidencebench.ingestion import audit_similar_documents, canonical, digest, load_units
from evidencebench.labels import read_labels, validate_labels
from evidencebench.protocol import verify_protocol
from evidencebench.qasper import select_annotation
from evidencebench.schemas import CorpusManifest, SourceDocument

RAW = Path("data/raw/qasper-fresh-v1")
OUTPUT = Path("data/processed/qasper-fresh-v1")
LABELS = Path("data/labels/qasper-fresh-v1")
REPORT = Path("reports/fresh-dataset.json")
RESERVATION = Path("data/manifests/fresh-evaluation-reservation.json")
TARGETS = {"dev": {True: 38, False: 12}, "test": {True: 75, False: 25}}
EXTRACTION = {p: importlib.metadata.version(p) for p in ("pdfplumber", "pdfminer-six")}


def read(path):
    return json.loads(path.read_text("utf-8"))


def retain(path, value, check=False):
    if check or path.exists():
        if read(path) != value:
            raise ValueError("retained artifact differs")
    else:
        with path.open("xb") as stream:
            stream.write(canonical(value))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="rebuild from cache without network/writes"
    )
    args = parser.parse_args(argv)
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    verify_protocol(Path("data/manifests/release-lock.json"))
    reserved = read(RESERVATION)
    for path, expected in reserved["source_sha256"].items():
        if digest(Path(path).read_bytes()) != expected:
            raise ValueError("reservation input checksum mismatch")
    excluded = set().union(*(set(v) for v in reserved["exclusion_reasons"].values()))
    pools = reserved["pools"]
    all_ids = [p for pool in pools.values() for group in pool.values() for p in group]
    if len(all_ids) != len(set(all_ids)) or set(all_ids) & excluded:
        raise ValueError("reservation family overlap")
    pinned_paths = [
        RESERVATION,
        Path("scripts/build_fresh_qasper.py"),
        Path("src/evidencebench/fresh_data.py"),
        Path("src/evidencebench/qasper.py"),
        Path("src/evidencebench/schemas.py"),
        Path("src/evidencebench/labels.py"),
        Path("src/evidencebench/ingestion.py"),
        Path("src/evidencebench/chunking.py"),
        Path("docs/fresh-evaluation-protocol.md"),
    ]
    contract = {
        "sources": {p.as_posix(): digest(p.read_bytes()) for p in pinned_paths},
        "extractor": EXTRACTION,
        "protocol": "fresh-evaluation-v1",
        "model_calls": 0,
    }
    if not args.check:
        RAW.mkdir(parents=True, exist_ok=True)
    retain(RAW / "build-contract.json", contract, args.check)
    old_units = load_units(Path("data/processed/qasper-v1"))
    old_queries = [
        q
        for s in ("train", "dev", "test")
        for q in read_labels(Path(f"data/labels/qasper-v1/{s}.jsonl"))
    ]
    seen_ids = {q.query_id for q in old_queries}
    seen_texts = {normalize(q.text).casefold() for q in old_queries}
    sources, units, queries, audit, counts_by_split = [], [], [], [], {}
    cache_hashes = {}
    with httpx.Client(timeout=30, follow_redirects=True) as client:
        for split, targets in TARGETS.items():
            data = read(Path(f"data/raw/qasper/qasper-{split}-v0.3.json"))
            pool = pools["validation" if split == "dev" else "test"]
            counts = Counter()
            for ordinal, paper_id in enumerate(pool["primary"] + pool["fallback"], 1):
                if all(counts[k] == v for k, v in targets.items()):
                    break
                paper = data[paper_id]
                annotations = [select_annotation(q) for q in paper["qas"]]
                if not any(
                    a and counts[a["answerable"]] < targets[a["answerable"]] for a in annotations
                ):
                    audit.append(
                        {
                            "paper_id": paper_id,
                            "split": split,
                            "reason": "no_eligible_annotation_for_remaining_quota",
                        }
                    )
                    continue
                failure_path = RAW / f"{paper_id}.failure.json"
                if failure_path.exists():
                    audit.append(read(failure_path))
                    continue
                try:
                    path = RAW / f"{paper_id}.pdf"
                    meta_path = RAW / f"{paper_id}.acquisition.json"
                    if args.check:
                        metadata = read(meta_path)
                        if digest(path.read_bytes()) != metadata["sha256"]:
                            raise RuntimeError("source checksum changed")
                    else:
                        path, metadata = download_pdf(client, paper_id, RAW)
                    pages_path = RAW / f"{paper_id}.pages.json"
                    if pages_path.exists():
                        extracted = read(pages_path)
                        if (
                            extracted["pdf_sha256"] != metadata["sha256"]
                            or extracted["extractor"] != EXTRACTION
                            or digest(canonical(extracted["pages"])) != extracted["pages_sha256"]
                        ):
                            raise RuntimeError("extraction cache checksum mismatch")
                        pages = extracted["pages"]
                    else:
                        if args.check:
                            raise RuntimeError("verification requires extraction cache")
                        with pdfplumber.open(path, unicode_norm="NFKC") as pdf:
                            if not 0 < len(pdf.pages) <= 250:
                                raise ValueError("PDF page count outside bounds")
                            pages = []
                            for page in pdf.pages:
                                pages.append(page.extract_text() or "")
                                page.close()
                        retain(
                            pages_path,
                            {
                                "pdf_sha256": metadata["sha256"],
                                "extractor": EXTRACTION,
                                "pages": pages,
                                "pages_sha256": digest(canonical(pages)),
                            },
                        )
                    cache_hashes[pages_path.as_posix()] = digest(pages_path.read_bytes())
                except (ValueError, httpx.HTTPError, PDFException, PdfminerException) as exc:
                    if args.check:
                        raise RuntimeError("verification cache is incomplete") from exc
                    failure = {
                        "paper_id": paper_id,
                        "split": split,
                        "reason": "pdf_unavailable_or_invalid",
                        "error": type(exc).__name__,
                    }
                    retain(failure_path, failure)
                    audit.append(failure)
                    print(
                        json.dumps({"split": split, "visited": ordinal, "skipped_pdf": True}),
                        flush=True,
                    )
                    continue
                paper_units, accepted, query_audit = align_paper(
                    paper_id,
                    paper,
                    pages,
                    metadata["sha256"],
                    split,
                    counts,
                    targets,
                    seen_ids,
                    seen_texts,
                )
                audit.extend({"paper_id": paper_id, "split": split, **r} for r in query_audit)
                audit.append(
                    {
                        "paper_id": paper_id,
                        "split": split,
                        "reason": "aligned",
                        "accepted": len(accepted),
                        "paragraphs": len(paper_units),
                        "pool": "primary" if ordinal <= len(pool["primary"]) else "fallback",
                    }
                )
                if accepted:
                    sources.append(
                        SourceDocument(
                            document_id=f"qasper-{paper_id}",
                            family_id=f"qasper-{paper_id}",
                            version=f"qasper-v0.3-pdf-{metadata['sha256'][:12]}",
                            url=metadata["url"],
                            sha256=metadata["sha256"],
                            retrieved_at=metadata["retrieved_at"],
                            page_count=len(pages),
                            split=split,
                            license=(
                                "QASPER text/annotations: CC BY 4.0; PDF rights remain "
                                "with authors; PDF not redistributed"
                            ),
                        )
                    )
                    units.extend(paper_units)
                    queries.extend(accepted)
                    for query in accepted:
                        counts[query.answerable] += 1
                        seen_ids.add(query.query_id)
                        seen_texts.add(normalize(query.text).casefold())
                if not args.check:
                    (RAW / "progress.json").write_bytes(
                        canonical(
                            {
                                "split": split,
                                "answerable": counts[True],
                                "unanswerable": counts[False],
                                "visited": ordinal,
                                "retained_papers": len(sources),
                                "audit": audit,
                            }
                        )
                    )
                print(
                    json.dumps(
                        {
                            "split": split,
                            "answerable": counts[True],
                            "unanswerable": counts[False],
                            "visited": ordinal,
                        }
                    ),
                    flush=True,
                )
            if any(counts[k] != v for k, v in targets.items()):
                raise RuntimeError("insufficient eligible queries; protocol unchanged")
            counts_by_split[split] = {"answerable": counts[True], "unanswerable": counts[False]}
    corpus = CorpusManifest(sources=sources)
    validation = validate_labels(queries, units)
    if audit_similar_documents(old_units + units):
        raise RuntimeError("near-duplicate family review required; no examples emitted")
    if {u.family_id for u in units} & {u.family_id for u in old_units}:
        raise RuntimeError("fresh and old corpus overlap")
    records = [u.model_dump(mode="json") for u in units]
    recipe = {
        "source": "QASPER v0.3",
        "build_contract": contract,
        "sources": corpus.model_dump(mode="json")["sources"],
        "records_hash": digest(canonical(records)),
        "cache_sha256": cache_hashes,
    }
    manifest = {
        "fingerprint": digest(canonical(recipe)),
        "recipe": recipe,
        "unit_count": len(units),
        "document_count": len(sources),
        "query_count": len(queries),
    }
    if not args.check:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        LABELS.mkdir(parents=True, exist_ok=True)
    parquet = OUTPUT / "units.parquet"
    if args.check or parquet.exists():
        if pq.read_table(parquet).to_pylist() != records:
            raise RuntimeError("retained corpus mismatch")
    else:
        pq.write_table(pa.Table.from_pylist(records), parquet)
    retain(OUTPUT / "manifest.json", manifest, args.check)
    retain(OUTPUT / "alignment-audit.json", audit, args.check)
    for split in TARGETS:
        payload = b"".join(
            canonical(q.model_dump(mode="json")) + b"\n" for q in queries if q.split == split
        )
        path = LABELS / f"{split}.jsonl"
        if args.check or path.exists():
            if path.read_bytes() != payload:
                raise RuntimeError("retained labels mismatch")
        else:
            with path.open("xb") as stream:
                stream.write(payload)
    paths = [
        OUTPUT / "manifest.json",
        parquet,
        OUTPUT / "alignment-audit.json",
        LABELS / "dev.jsonl",
        LABELS / "test.jsonl",
        RAW / "build-contract.json",
    ]
    result = {
        "status": "built_not_model_evaluated",
        "validation": validation,
        "counts": counts_by_split,
        "fingerprint": manifest["fingerprint"],
        "paragraphs": len(units),
        "papers": len(sources),
        "model_calls": 0,
        "files": {p.as_posix(): digest(p.read_bytes()) for p in paths},
        "audit_counts": dict(sorted(Counter(r["reason"] for r in audit).items())),
        "near_duplicate_families": 0,
        "known_prior_family_overlap": 0,
    }
    retain(REPORT, result, args.check)
    verify_protocol(Path("data/manifests/release-lock.json"))
    print(json.dumps({"mode": "verified" if args.check else "built", **result}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Validation exceptions can contain question/reference text; never expose
        # them in terminal output while constructing the reserved final test.
        print(json.dumps({"status": "stopped", "error_type": type(exc).__name__}), file=sys.stderr)
        sys.exit(1)
