"""Self-check for the OCR fallback in app._extract_pdf() / app._ocr_pdf().

Skips (not fails) when the tesseract-ocr system binary isn't installed, since
that's an environment dependency this test can't install itself.
"""
import io
import sys
from pathlib import Path

import fitz
import pytest
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import app as ldv_app


def _tesseract_available() -> bool:
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        return True
    except Exception:
        return False


def _make_scanned_pdf(text: str) -> bytes:
    """Build a PDF with *text* rendered into a page image, no text layer."""
    img = Image.new("RGB", (800, 200), "white")
    draw = ImageDraw.Draw(img)
    draw.text((20, 80), text, fill="black")
    buf = io.BytesIO()
    img.save(buf, format="PNG")

    doc = fitz.open()
    page = doc.new_page(width=800, height=200)
    page.insert_image(page.rect, stream=buf.getvalue())
    return doc.tobytes()


@pytest.mark.skipif(not _tesseract_available(), reason="tesseract-ocr binary not installed")
def test_ocr_recovers_text_from_scanned_pdf():
    data = _make_scanned_pdf("GOVERNING LAW CLAUSE")
    text = ldv_app._extract_pdf(data)
    assert "GOVERNING" in text.upper()


def test_ocr_degrades_to_empty_when_tesseract_missing(monkeypatch):
    """_ocr_pdf() must not raise -- degrades to "" so the caller's existing
    'Scan/OCR required' error still surfaces, instead of a 500."""
    import pytesseract

    def _boom(*a, **kw):
        raise pytesseract.TesseractNotFoundError()

    monkeypatch.setattr(pytesseract, "image_to_string", _boom)
    data = _make_scanned_pdf("ANYTHING")
    doc = fitz.open(stream=data, filetype="pdf")
    assert ldv_app._ocr_pdf(doc) == ""
