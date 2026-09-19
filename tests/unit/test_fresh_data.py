from collections import Counter

import httpx
import pytest

from evidencebench.fresh_data import align_paper, download_pdf

PARAGRAPH = "The classifier uses contextual word vectors and a linear classification head."


def paper():
    def question(key, evidence, unanswerable=False):
        return {
            "question_id": key,
            "question": f"Question {key}?",
            "answers": [
                {
                    "answer": {
                        "unanswerable": unanswerable,
                        "evidence": evidence,
                        "extractive_spans": ["word vectors"],
                        "free_form_answer": "",
                        "yes_no": None,
                    }
                }
            ],
        }

    return {
        "title": "Synthetic paper",
        "abstract": PARAGRAPH,
        "full_text": [],
        "qas": [
            question("a", [PARAGRAPH]),
            question("b", [PARAGRAPH]),
            question("c", [PARAGRAPH]),
            question("d", [], True),
        ],
    }


def test_alignment_honors_quota_family_cap_and_order_without_mutating_counts():
    counts = Counter({True: 1})
    units, queries, audit = align_paper(
        "1234.56789",
        paper(),
        [PARAGRAPH],
        "a" * 64,
        "dev",
        counts,
        {True: 2, False: 1},
        set(),
        set(),
    )
    assert len(queries) == 2
    assert Counter(q.answerable for q in queries) == {True: 1, False: 1}
    assert counts == {True: 1}
    assert units[0].page == 1
    assert all(set(q.supporting_evidence) <= {u.element_id for u in units} for q in queries)
    other = paper()
    other["qas"].reverse()
    assert align_paper(
        "1234.56789", other, [PARAGRAPH], "a" * 64, "dev", counts, {True: 2, False: 1}, set(), set()
    ) == (units, queries, audit)


def test_alignment_rejects_missing_evidence_and_duplicate_ids():
    _, queries, audit = align_paper(
        "1234.56789",
        paper(),
        [PARAGRAPH],
        "a" * 64,
        "test",
        Counter(),
        {True: 10, False: 0},
        {"a", "b", "c"},
        set(),
    )
    assert not queries
    assert any(r["reason"] == "duplicate_query" for r in audit)
    _, queries, _ = align_paper(
        "1234.56789",
        paper(),
        ["Different page"],
        "a" * 64,
        "test",
        Counter(),
        {True: 10, False: 0},
        set(),
        set(),
    )
    assert not queries


def test_download_retains_two_attempt_budget_across_restarts(tmp_path):
    calls = []

    def fail(request):
        calls.append(request.url)
        return httpx.Response(503)

    with httpx.Client(transport=httpx.MockTransport(fail)) as client:
        with pytest.raises(ValueError, match="unavailable"):
            download_pdf(client, "1234.56789", tmp_path, pause=lambda _: None)
        with pytest.raises(ValueError, match="unavailable"):
            download_pdf(client, "1234.56789", tmp_path, pause=lambda _: None)
    assert len(calls) == 2


def test_download_bounds_bytes_verifies_cache_and_stops_on_rate_limit(tmp_path):
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"%PDF-123"))
    ) as client:
        path, metadata = download_pdf(client, "1234.56789", tmp_path, pause=lambda _: None)
        assert path.read_bytes() == b"%PDF-123"
        assert metadata["sha256"]
        path.write_bytes(b"changed")
        with pytest.raises(RuntimeError, match="checksum"):
            download_pdf(client, "1234.56789", tmp_path, pause=lambda _: None)
    with httpx.Client(transport=httpx.MockTransport(lambda _: httpx.Response(429))) as client:
        with pytest.raises(RuntimeError, match="rate limit"):
            download_pdf(client, "1234.98765", tmp_path, pause=lambda _: None)
    with httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(200, content=b"%PDF-123"))
    ) as client:
        with pytest.raises(ValueError, match="unavailable"):
            download_pdf(client, "1234.55555", tmp_path, pause=lambda _: None, max_bytes=6)
    assert not (tmp_path / "1234.55555.pdf").exists()


@pytest.mark.parametrize("malformed_primary", [False, True])
def test_complete_builder_reproduces_without_writes_and_rejects_label_tampering(
    tmp_path, monkeypatch, malformed_primary
):
    import importlib.util
    import json
    import shutil
    from pathlib import Path

    from evidencebench.ingestion import canonical, digest

    repo = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location(
        "fresh_builder", repo / "scripts/build_fresh_qasper.py"
    )
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    (tmp_path / "scripts").mkdir()
    shutil.copyfile(
        repo / "scripts/build_fresh_qasper.py", tmp_path / "scripts/build_fresh_qasper.py"
    )
    for name in ("fresh_data", "qasper", "schemas", "labels", "ingestion", "chunking"):
        target = tmp_path / f"src/evidencebench/{name}.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(repo / f"src/evidencebench/{name}.py", target)
    for directory in ("data/manifests", "data/raw/qasper", "docs", "reports"):
        (tmp_path / directory).mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs/fresh-evaluation-protocol.md").write_text("Synthetic protocol")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(builder, "verify_protocol", lambda _: None)
    monkeypatch.setattr(builder, "load_units", lambda _: [])
    monkeypatch.setattr(builder, "read_labels", lambda _: [])
    monkeypatch.setattr(
        builder, "TARGETS", {"dev": {True: 1, False: 0}, "test": {True: 1, False: 0}}
    )
    builder.RAW.mkdir(parents=True)
    pools = {}
    for split, pid, body in (
        ("dev", "1234.11111", PARAGRAPH),
        (
            "test",
            "1234.22222",
            "Astronomers observe distant galaxies through telescopes during clear winter nights.",
        ),
    ):
        item = paper()
        item["title"] = split
        item["abstract"] = body
        item["qas"] = [item["qas"][0]]
        item["qas"][0]["question_id"] = split
        item["qas"][0]["answers"][0]["answer"]["evidence"] = [body]
        Path(f"data/raw/qasper/qasper-{split}-v0.3.json").write_bytes(canonical({pid: item}))
        payload = b"%PDF-synthetic-cache"
        # Distinct source hashes are required by CorpusManifest.
        payload += split.encode()
        (builder.RAW / f"{pid}.pdf").write_bytes(payload)
        (builder.RAW / f"{pid}.acquisition.json").write_bytes(
            canonical(
                {
                    "url": f"https://arxiv.org/pdf/{pid}",
                    "sha256": digest(payload),
                    "retrieved_at": "2026-09-19",
                }
            )
        )
        (builder.RAW / f"{pid}.pages.json").write_bytes(
            canonical(
                {
                    "pdf_sha256": digest(payload),
                    "extractor": builder.EXTRACTION,
                    "pages": [body],
                    "pages_sha256": digest(canonical([body])),
                }
            )
        )
        pools["validation" if split == "dev" else "test"] = {"primary": [pid], "fallback": []}
    if malformed_primary:
        bad_id = "1234.00000"
        bad_payload = b"%PDF-broken"
        (builder.RAW / f"{bad_id}.pdf").write_bytes(bad_payload)
        (builder.RAW / f"{bad_id}.acquisition.json").write_bytes(
            canonical(
                {
                    "url": f"https://arxiv.org/pdf/{bad_id}",
                    "sha256": digest(bad_payload),
                    "retrieved_at": "2026-09-19",
                }
            )
        )
        source_path = Path("data/raw/qasper/qasper-dev-v0.3.json")
        source = json.loads(source_path.read_text())
        source[bad_id] = paper()
        source_path.write_bytes(canonical(source))
        pools["validation"]["primary"].insert(0, bad_id)
    builder.RESERVATION.write_bytes(
        canonical({"source_sha256": {}, "exclusion_reasons": {}, "pools": pools})
    )
    builder.main([])
    if malformed_primary:
        assert (builder.RAW / "1234.00000.failure.json").exists()
    before = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*") if p.is_file()}
    builder.main(["--check"])
    after = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after
    assert json.loads(builder.REPORT.read_text())["validation"]["query_count"] == 2
    with (builder.LABELS / "test.jsonl").open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(RuntimeError, match="labels mismatch"):
        builder.main(["--check"])


def test_redirects_consume_request_budget_and_obey_delay(tmp_path):
    calls, pauses = [], []

    def redirect(request):
        calls.append(str(request.url))
        if len(calls) == 1:
            return httpx.Response(302, headers={"location": "/pdf/1234.56789.pdf"})
        return httpx.Response(200, content=b"%PDF-123")

    with httpx.Client(transport=httpx.MockTransport(redirect), follow_redirects=True) as client:
        path, _ = download_pdf(client, "1234.56789", tmp_path, pause=pauses.append)
    assert path.exists()
    assert pauses == [3, 3]
    assert calls == ["https://arxiv.org/pdf/1234.56789", "https://arxiv.org/pdf/1234.56789.pdf"]
