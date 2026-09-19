"""Build the predeclared QASPER subset; output progress contains counts, never test examples."""

import argparse
import hashlib
import importlib.metadata
import json
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pdfplumber
import pyarrow as pa
import pyarrow.parquet as pq

from evidencebench.chunking import normalize
from evidencebench.ingestion import audit_similar_documents, canonical, digest
from evidencebench.labels import validate_labels
from evidencebench.qasper import PageAligner, select_annotation
from evidencebench.schemas import ContentUnit, CorpusManifest, QueryExample, SourceDocument

ROOT = Path("data/raw/qasper")
OUTPUT = Path("data/processed/qasper-v1")
LABELS = Path("data/labels/qasper-v1")
SEED = 42
TARGETS = {"train": (200, 0), "dev": (38, 12), "test": (75, 25)}
EXTRACTION = {
    "packages": {p: importlib.metadata.version(p) for p in ("pdfplumber", "pdfminer-six")},
    "unicode_norm": "NFKC",
    "method": "page.extract_text",
    "settings": {},
}
EXTRACTION_ID = digest(canonical(EXTRACTION))[:12]


def order(key):
    return hashlib.sha256(f"{SEED}:{key}".encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--labels", type=Path, default=LABELS)
    args = parser.parse_args()
    output, labels_dir = args.output, args.labels
    if output.exists() or labels_dir.exists():
        raise SystemExit("Immutable QASPER output exists; use a new version instead of overwriting")
    started = time.perf_counter()
    sources, all_units, all_queries, audit = [], [], [], []
    cache = ROOT / "processed-cache"
    cache.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=40, follow_redirects=True) as client:
        for split, (positive_target, negative_target) in TARGETS.items():
            filename = ROOT / f"qasper-{split}-v0.3.json"
            data = json.loads(filename.read_text("utf-8"))
            counts = Counter()
            for paper_id in sorted(data, key=order):
                if counts[True] >= positive_target and counts[False] >= negative_target:
                    break
                paper = data[paper_id]
                candidates = [(q, select_annotation(q)) for q in paper["qas"]]
                candidates = [
                    (q, a)
                    for q, a in candidates
                    if a is not None
                    and counts[a["answerable"]]
                    < (positive_target if a["answerable"] else negative_target)
                ]
                if not candidates:
                    continue
                path = ROOT / f"{paper_id}.pdf"
                url = f"https://arxiv.org/pdf/{paper_id}"
                try:
                    if not path.exists():
                        time.sleep(3)  # Polite sequential public-PDF acquisition.
                        response = client.get(url)
                        if response.status_code == 429:
                            raise RuntimeError(
                                "arXiv rate limit: stop acquisition and retain cache"
                            )
                        response.raise_for_status()
                        if (
                            not response.content.startswith(b"%PDF-")
                            or len(response.content) > 30_000_000
                        ):
                            raise ValueError("not a bounded PDF")
                        path.write_bytes(response.content)
                    checksum = digest(path.read_bytes())
                    acquisition = path.with_suffix(".acquisition.json")
                    if acquisition.exists():
                        acquired = json.loads(acquisition.read_text("utf-8"))
                        if acquired["sha256"] != checksum:
                            raise RuntimeError("Cached source checksum changed")
                    else:
                        acquired = {
                            "url": url,
                            "sha256": checksum,
                            "retrieved_at": datetime.fromtimestamp(path.stat().st_mtime, UTC)
                            .date()
                            .isoformat(),
                            "date_basis": "download file modification date at first import",
                        }
                        acquisition.write_bytes(canonical(acquired))
                    cached = cache / f"{paper_id}-{checksum[:12]}-{EXTRACTION_ID}.json"
                    if cached.exists():
                        pages = json.loads(cached.read_text("utf-8"))
                    else:
                        with pdfplumber.open(path, unicode_norm="NFKC") as pdf:
                            if len(pdf.pages) > 250:
                                raise ValueError("PDF exceeds page limit")
                            pages = []
                            for page in pdf.pages:
                                # Matching tolerates interleaved columns and joined words.
                                pages.append(page.extract_text() or "")
                                page.close()
                        cached.write_bytes(canonical(pages))
                except (httpx.HTTPError, ValueError) as exc:
                    audit.append(
                        {
                            "paper_id": paper_id,
                            "split": split,
                            "reason": "pdf_unavailable",
                            "error": type(exc).__name__,
                        }
                    )
                    continue
                document_id = f"qasper-{paper_id}"
                paragraphs = [("Abstract", paper["abstract"])] + [
                    (section["section_name"], text)
                    for section in paper["full_text"]
                    for text in section["paragraphs"]
                ]
                units, mapping = [], {}
                aligner = PageAligner(pages)
                for ordinal, (section, text) in enumerate(paragraphs):
                    normalized = normalize(text)
                    span = aligner.locate(normalized)
                    if span is None:
                        continue
                    element_id = digest(
                        canonical(["qasper-v0.3-paragraph-v1", paper_id, ordinal, normalized])
                    )
                    units.append(
                        ContentUnit(
                            element_id=element_id,
                            document_id=document_id,
                            family_id=document_id,
                            version=f"qasper-v0.3-pdf-{checksum[:12]}",
                            split=split,
                            page=span[0],
                            page_end=span[1],
                            section=section or None,
                            text=paper["title"] + "\n" + normalized,
                            source_checksum=checksum,
                            source_url=url,
                            bbox=None,
                        )
                    )
                    mapping.setdefault(normalized, []).append(element_id)
                accepted = []
                for question, annotation in sorted(
                    candidates, key=lambda pair: order(pair[0]["question_id"])
                ):
                    answerable = annotation["answerable"]
                    target = positive_target if answerable else negative_target
                    if counts[answerable] >= target:
                        continue
                    if any(paragraph not in mapping for paragraph in annotation["evidence"]):
                        audit.append(
                            {
                                "paper_id": paper_id,
                                "split": split,
                                "reason": "evidence_not_aligned",
                                "query_id": question["question_id"],
                            }
                        )
                        continue
                    if not units:
                        continue
                    support = sorted({key for p in annotation["evidence"] for key in mapping[p]})
                    accepted.append(
                        QueryExample(
                            query_id=question["question_id"],
                            text=f"In the paper '{paper['title']}', {question['question']}",
                            split=split,
                            family_id=document_id,
                            query_type="qasper-human",
                            relevance={key: 2 for key in support},
                            answerable=answerable,
                            answer_criteria=annotation["criteria"],
                            supporting_evidence=support,
                            label_provenance=(
                                "QASPER v0.3 original human annotations; unanimous answerability; "
                                "text-only evidence union. Automated paragraph/page alignment; "
                                "no new human review."
                            ),
                            review_status="human-reviewed",
                        )
                    )
                    counts[answerable] += 1
                if accepted:
                    sources.append(
                        SourceDocument(
                            document_id=document_id,
                            family_id=document_id,
                            version=f"qasper-v0.3-pdf-{checksum[:12]}",
                            url=url,
                            sha256=checksum,
                            retrieved_at=acquired["retrieved_at"],
                            page_count=len(pages),
                            split=split,
                            license=(
                                "QASPER dataset text/annotations: CC BY 4.0; original PDF "
                                "rights remain with authors; PDF not redistributed"
                            ),
                        )
                    )
                    all_units.extend(units)
                    all_queries.extend(accepted)
                    audit.append(
                        {
                            "paper_id": paper_id,
                            "split": split,
                            "reason": "accepted",
                            "paragraphs_total": len(paragraphs),
                            "paragraphs_aligned": len(units),
                            "queries": len(accepted),
                        }
                    )
                (ROOT / "build-progress.json").write_bytes(
                    canonical(
                        {
                            "audit": audit,
                            "split": split,
                            "counts": {str(k): v for k, v in counts.items()},
                        }
                    )
                )
                print(
                    f"{split}: {counts[True]}/{positive_target} answerable, "
                    f"{counts[False]}/{negative_target} unanswerable; {len(sources)} papers",
                    flush=True,
                )
            if counts[True] != positive_target or counts[False] != negative_target:
                raise ValueError(f"Insufficient eligible {split} examples: {dict(counts)}")
    corpus = CorpusManifest(sources=sources)
    validate_labels(all_queries, all_units)
    near_duplicates = audit_similar_documents(all_units)
    if near_duplicates:
        raise ValueError(f"Cross-family document duplicates require review: {near_duplicates}")
    records = [u.model_dump(mode="json") for u in all_units]
    recipe = {
        "schema_version": 1,
        "source": "QASPER v0.3",
        "seed": SEED,
        "paragraph_protocol": "original-paragraph-title-prefix-v1",
        "alignment": "all-words-numeric-consistent-char5-0.9-unique-1or2-pages-v3",
        "extractor": EXTRACTION,
        "sources": corpus.model_dump(mode="json")["sources"],
        "records_hash": digest(canonical(records)),
        "upstream_hashes": {p.name: digest(p.read_bytes()) for p in ROOT.glob("*.tgz")},
    }
    output.mkdir(parents=True)
    labels_dir.mkdir(parents=True)
    pq.write_table(pa.Table.from_pylist(records), output / "units.parquet")
    report = {
        "fingerprint": digest(canonical(recipe)),
        "recipe": recipe,
        "unit_count": len(records),
        "document_count": len(sources),
        "query_count": len(all_queries),
        "elapsed_seconds": time.perf_counter() - started,
    }
    (output / "manifest.json").write_bytes(canonical(report))
    for split in TARGETS:
        rows = [q for q in all_queries if q.split == split]
        (labels_dir / f"{split}.jsonl").write_text(
            "\n".join(q.model_dump_json() for q in rows) + "\n", encoding="utf-8"
        )
    (output / "alignment-audit.json").write_bytes(canonical(audit))
    Path("data/manifests/qasper-v1.json").write_bytes(canonical(corpus.model_dump(mode="json")))
    (output / "label-fingerprints.json").write_bytes(
        canonical({p.name: digest(p.read_bytes()) for p in labels_dir.glob("*.jsonl")})
    )
    print(
        json.dumps(
            {
                k: report[k]
                for k in (
                    "fingerprint",
                    "unit_count",
                    "document_count",
                    "query_count",
                    "elapsed_seconds",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
