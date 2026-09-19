from hashlib import sha256

import pytest
from reportlab.pdfgen import canvas


@pytest.fixture
def pdf_source(tmp_path):
    """Original synthetic fixture, independent of benchmark documents and labels."""
    path = tmp_path / "manual.pdf"
    pdf = canvas.Canvas(str(path), invariant=1)
    for line in [
        "Back up databases daily. Encrypt stored backup files.",
        "Restore backups monthly to verify data integrity.",
    ]:
        pdf.drawString(72, 720, line)
        pdf.showPage()
    pdf.save()
    return path, dict(
        document_id="backup-v1",
        family_id="backup",
        version="1",
        url="https://example.org/manual.pdf",
        sha256=sha256(path.read_bytes()).hexdigest(),
        retrieved_at="2026-09-18",
        page_count=2,
        split="train",
        license="Original synthetic test fixture; CC0",
        mime_type="application/pdf",
    )
