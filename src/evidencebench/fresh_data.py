"""Isolated fresh-QASPER construction using frozen annotation/alignment helpers."""

import json
import time
from collections import Counter
from datetime import UTC, datetime

import httpx

from evidencebench.chunking import normalize
from evidencebench.ingestion import canonical, digest
from evidencebench.qasper import PageAligner, select_annotation
from evidencebench.schemas import ContentUnit, QueryExample


def align_paper(paper_id, paper, pages, checksum, split, counts, targets, seen_ids, seen_texts):
    """Return aligned units and at most two questions; caller owns global quota state."""
    aligner = PageAligner(pages)
    paragraphs = [("Abstract", paper["abstract"])] + [
        (section["section_name"], text)
        for section in paper["full_text"]
        for text in section["paragraphs"]
    ]
    units, mapping, queries, audit = [], {}, [], []
    family = f"qasper-{paper_id}"
    for ordinal, (section, text) in enumerate(paragraphs):
        text = normalize(text)
        span = aligner.locate(text)
        if span is None:
            continue
        key = digest(canonical(["qasper-v0.3-paragraph-v1", paper_id, ordinal, text]))
        units.append(
            ContentUnit(
                element_id=key,
                document_id=family,
                family_id=family,
                version=f"qasper-v0.3-pdf-{checksum[:12]}",
                split=split,
                page=span[0],
                page_end=span[1],
                section=section or None,
                text=paper["title"] + "\n" + text,
                source_checksum=checksum,
                source_url=f"https://arxiv.org/pdf/{paper_id}",
            )
        )
        mapping.setdefault(text, []).append(key)
    selected = Counter()
    ids, texts = set(seen_ids), set(seen_texts)
    for question in sorted(
        paper["qas"], key=lambda q: digest(f"fresh-eval-query-v1:42:{q['question_id']}".encode())
    ):
        key = question["question_id"]
        text = f"In the paper '{paper['title']}', {question['question']}"
        normalized = normalize(text).casefold()
        annotation = select_annotation(question)
        reason = None
        if key in ids or normalized in texts:
            reason = "duplicate_query"
        elif annotation is None:
            reason = "unsupported_annotation"
        elif len(queries) >= 2:
            reason = "family_cap"
        elif (
            counts[annotation["answerable"]] + selected[annotation["answerable"]]
            >= targets[annotation["answerable"]]
        ):
            reason = "quota_filled"
        elif not units or any(p not in mapping for p in annotation["evidence"]):
            reason = "evidence_not_aligned"
        if reason:
            audit.append({"query_id": key, "reason": reason})
            continue
        support = sorted({eid for p in annotation["evidence"] for eid in mapping[p]})
        queries.append(
            QueryExample(
                query_id=key,
                text=text,
                split=split,
                family_id=family,
                query_type="qasper-human",
                relevance={eid: 2 for eid in support},
                answerable=annotation["answerable"],
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
        selected[annotation["answerable"]] += 1
        ids.add(key)
        texts.add(normalized)
    return units, queries, audit


def download_pdf(client, paper_id, root, pause=None, max_bytes=30_000_000):
    """Stream a bounded PDF, retaining at most two network attempts across restarts."""
    pause = pause or time.sleep
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{paper_id}.pdf"
    metadata_path = root / f"{paper_id}.acquisition.json"
    if path.exists():
        if not metadata_path.exists():
            raise RuntimeError("cached PDF lacks checksum metadata")
        metadata = json.loads(metadata_path.read_text("utf-8"))
        if path.stat().st_size > max_bytes or digest(path.read_bytes()) != metadata["sha256"]:
            raise RuntimeError("cached PDF checksum mismatch")
        return path, metadata
    url = f"https://arxiv.org/pdf/{paper_id}"
    source_url = url
    for attempt in (1, 2):
        ledger = root / f"{paper_id}.attempt-{attempt}.json"
        if ledger.exists():
            previous = json.loads(ledger.read_text("utf-8"))
            if previous.get("status") == "redirect":
                url = previous["redirect_url"]
            continue
        record = {"url": url, "attempt": attempt, "status": "started"}
        with ledger.open("xb") as stream:
            stream.write(canonical(record))
        pause(3)
        try:
            with client.stream("GET", url, follow_redirects=False) as response:
                if response.status_code == 429:
                    record.update(status="rate_limited")
                    ledger.write_bytes(canonical(record))
                    raise RuntimeError("arXiv rate limit; acquisition stopped")
                if response.is_redirect and response.headers.get("location"):
                    destination = response.url.join(response.headers["location"])
                    if destination.scheme != "https" or destination.host != "arxiv.org":
                        raise ValueError("redirect outside PDF source")
                    url = str(destination)
                    record.update(status="redirect", redirect_url=url)
                    ledger.write_bytes(canonical(record))
                    continue
                response.raise_for_status()
                content = bytearray()
                for block in response.iter_bytes():
                    if len(content) + len(block) > max_bytes:
                        raise ValueError("PDF exceeds size limit")
                    content.extend(block)
            if not content.startswith(b"%PDF-"):
                raise ValueError("response is not PDF")
            metadata = {
                "url": source_url,
                "sha256": digest(bytes(content)),
                "retrieved_at": datetime.now(UTC).date().isoformat(),
                "bytes": len(content),
            }
            with path.open("xb") as stream:
                stream.write(content)
            with metadata_path.open("xb") as stream:
                stream.write(canonical(metadata))
            record.update(status="downloaded", sha256=metadata["sha256"])
            ledger.write_bytes(canonical(record))
            return path, metadata
        except (httpx.HTTPError, ValueError) as exc:
            record.update(status="failed", error=type(exc).__name__)
            ledger.write_bytes(canonical(record))
    raise ValueError("PDF unavailable after retained attempts")
