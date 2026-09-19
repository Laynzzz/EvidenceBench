import json
from hashlib import sha256

import pytest
from reportlab.pdfgen import canvas


def test_extracts_real_pdf_with_page_coordinates_and_stable_ids(pdf_source):
    from evidencebench.ingestion import extract_source
    from evidencebench.schemas import SourceDocument

    path, source = pdf_source
    doc = SourceDocument.model_validate(source)
    first, diagnostics = extract_source(path, doc, max_words=30, overlap=0)
    second, _ = extract_source(path, doc, max_words=30, overlap=0)
    assert first == second
    assert [u.page for u in first] == [1, 2]
    assert "Encrypt stored backup" in first[0].text
    assert "Restore backups monthly" in first[1].text
    assert first[0].bbox[0] == 72
    assert diagnostics["empty_pages"] == []


def test_source_tampering_rejected_before_extraction(pdf_source):
    from evidencebench.ingestion import extract_source
    from evidencebench.schemas import SourceDocument

    path, source = pdf_source
    path.write_bytes(b"corrupt")
    with pytest.raises(ValueError, match="checksum"):
        extract_source(path, SourceDocument.model_validate(source))


def test_blank_pdf_is_not_silently_accepted(pdf_source):
    from evidencebench.ingestion import extract_source
    from evidencebench.schemas import SourceDocument

    path, source = pdf_source
    pdf = canvas.Canvas(str(path), invariant=1)
    pdf.showPage()
    pdf.save()
    source.update(sha256=sha256(path.read_bytes()).hexdigest(), page_count=1)
    with pytest.raises(ValueError, match="text"):
        extract_source(path, SourceDocument.model_validate(source))


def test_clean_builds_have_same_fingerprint_and_roundtrip_records(pdf_source, tmp_path):
    from evidencebench.ingestion import build_corpus, load_units

    path, source = pdf_source
    raw = tmp_path / "raw"
    raw.mkdir()
    (raw / "backup-v1.pdf").write_bytes(path.read_bytes())
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"sources": [source]}))
    config = dict(manifest=str(manifest), raw_dir=str(raw), max_words=30, overlap=0)
    a = build_corpus(config, tmp_path / "a", fetch=False)
    b = build_corpus(config, tmp_path / "b", fetch=False)
    assert a["fingerprint"] == b["fingerprint"]
    assert load_units(tmp_path / "a") == load_units(tmp_path / "b")
    assert a["unit_count"] == 2
    with pytest.raises(FileExistsError):
        build_corpus(config, tmp_path / "a", fetch=False)
