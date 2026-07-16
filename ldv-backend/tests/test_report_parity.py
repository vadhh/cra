"""tests/test_report_parity.py — Priority 4 from the 2026-07-16 management
review: "Implement report parity tests... A mismatch must fail the test."

Both surfaces are built from the exact same dict: app.py's POST
/api/v1/report takes whatever JSON the client already fetched from
/api/v1/result/<id> and passes it straight into generate_pdf() with no
server-side re-derivation (see app.py:1294-1299). So "parity" here means:
generate_pdf() must not drop, mistranslate, or independently re-derive any
field that's present in that JSON. A field present in the JSON fixture but
absent from the rendered PDF text is a real PDF bug, not a data problem.

Uses `distribution_agreement` -- one of the 45 "partial" registry profiles
from docs/p7_catalogue_reconciliation.md -- specifically because the PDF's
profile-resolution code used to only recognize the original 11 legacy
profiles (fixed alongside this test; see pdf_report.py's profile_registry
switch).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

import fitz  # PyMuPDF -- already a hard dependency, used by app.py for input extraction

from pdf_report import generate_pdf
from detector import profile_registry


def _pdf_text(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        return "".join(page.get_text() for page in doc)
    finally:
        doc.close()


def _portal_result() -> dict:
    profile = profile_registry.profile_for("distribution_agreement")
    return {
        "language": "en",
        "jurisdiction": "Indonesia",
        "layer1": {
            "governing_law": "Indonesia",
            "venue": "Jakarta",
            "red_flags": [{
                "id": "excessive_penalty",
                "description": "Excessive late-payment penalty",
                "severity": "HIGH",
                "evidence": "5% per day penalty on any late payment",
                "citations": [{"source": "KUHPerdata", "article": "Art. 1250", "status": "verified"}],
            }],
            "clause_presence": [{
                "clause_id": "termination",
                "title": "Termination",
                "required": True,
                "present": False,
            }],
        },
        "layer2": {
            "document_type": {
                "label": profile["display_name"].lower(),
                "confidence": 0.81,
                "candidates": [{"label": profile["display_name"].lower(), "confidence": 0.81}],
                "source": "classifier",
            },
            "flagged_clauses": [],
        },
        "layer3": {
            "score": 63,
            "label": "HIGH",
            "breakdown": [
                {"reason": "HIGH severity red flag: excessive_penalty", "points": -25},
                {"reason": "Missing mandatory clause: termination", "points": -15},
            ],
        },
    }


def test_pdf_contains_contract_type_and_profile_version():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    profile = profile_registry.profile_for("distribution_agreement")
    assert profile["display_name"] in text
    assert profile["version"] in text


def test_pdf_contains_jurisdiction_and_language():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    assert result["jurisdiction"] in text
    assert re.search(r"\bEN\b", text)


def test_pdf_contains_confidence_and_score():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    assert "81.0%" in text
    assert str(result["layer3"]["score"]) in text
    assert result["layer3"]["label"] in text


def test_pdf_contains_findings_and_severity():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    flag = result["layer1"]["red_flags"][0]
    assert flag["description"] in text
    assert flag["severity"] in text


def test_pdf_contains_score_breakdown():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    for item in result["layer3"]["breakdown"]:
        assert item["reason"] in text


def test_pdf_contains_citations():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    citation = result["layer1"]["red_flags"][0]["citations"][0]
    assert citation["source"] in text
    assert citation["article"] in text


def test_pdf_contains_recommendation_for_missing_clause_and_high_severity():
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    assert "Termination" in text
    assert "HIGH-severity" in text


def test_pdf_does_not_overclaim_legal_validation():
    # Regression guard for the exact overclaiming bug this test file was
    # written alongside: the legacy per-profile JSON files hardcoded
    # `"validation_status": "Validated"` with no supporting evidence. The PDF
    # must never print a bare "Validated" legal-approval claim.
    result = _portal_result()
    text = _pdf_text(generate_pdf(result))
    assert "legal clause-list approval not yet established" in text


if __name__ == "__main__":
    test_pdf_contains_contract_type_and_profile_version()
    test_pdf_contains_jurisdiction_and_language()
    test_pdf_contains_confidence_and_score()
    test_pdf_contains_findings_and_severity()
    test_pdf_contains_score_breakdown()
    test_pdf_contains_citations()
    test_pdf_contains_recommendation_for_missing_clause_and_high_severity()
    test_pdf_does_not_overclaim_legal_validation()
    print("test_report_parity OK")
