"""Self-check for pdf_report.py: Explain Mode + citation wiring, decimal->band confidence."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from pdf_report import generate_pdf, _confidence_line, _citation_line


def test_confidence_line_bands():
    assert _confidence_line(0.90) == "High confidence (90%)"
    assert _confidence_line(0.75) == "Medium confidence (75%)"
    assert _confidence_line(0.50) == "Low confidence (50%)"
    assert _confidence_line(None) == ""
    assert _confidence_line("not a number") == ""


def test_citation_line_prefers_source_article_then_note():
    assert _citation_line([{"source": "French Code civil", "article": "Art. 1844-1"}]) == \
        "Source: French Code civil, Art. 1844-1"
    assert _citation_line([{"source": "", "article": "", "note": "generic rationale"}]) == \
        "Source: generic rationale"
    assert _citation_line([]) == ""
    assert _citation_line(None) == ""


def _sample_result(with_explain: bool) -> dict:
    flag = {
        "id": "leonine_profit",
        "description": "Leonine profit clause",
        "severity": "HIGH",
        "evidence": "all profits go to Party A",
        "citations": [{"source": "French Code civil", "article": "Art. 1844-1", "status": "verified"}],
    }
    clause = {
        "clause_id": "force_majeure",
        "title": "Force Majeure",
        "required": True,
        "present": False,
        "citations": [{"source": "", "article": "", "note": "no force majeure protection"}],
    }
    if with_explain:
        flag["explanation"] = {
            "reason": "Allocating all profits to one party is void as a leonine clause.",
            "suggested_correction": "Profits shall be distributed proportionally to each party's contribution.",
            "confidence": 0.90,
        }
        clause["explanation"] = {
            "reason": "Without this clause, the company may remain liable even when performance becomes impossible.",
            "suggested_correction": "The Parties shall not be liable for failure resulting from events beyond their control.",
            "confidence": 0.80,
        }
    return {
        "layer1": {"red_flags": [flag], "clause_presence": [clause], "governing_law": "France", "venue": "Paris"},
        "layer2": {"document_type": "Partnership Agreement", "flagged_clauses": []},
        "layer3": {"score": 42, "label": "HIGH"},
        "language": "en",
        "jurisdiction": "FR",
    }


def test_generate_pdf_with_explain_mode_data():
    pdf_bytes = generate_pdf(_sample_result(with_explain=True))
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


def test_generate_pdf_falls_back_without_explain_mode_data():
    # Analyses saved before risk_explainer.py shipped won't carry 'explanation' —
    # generate_pdf must still render (using the static _REWRITES fallback).
    pdf_bytes = generate_pdf(_sample_result(with_explain=False))
    assert pdf_bytes[:4] == b"%PDF"
    assert len(pdf_bytes) > 1000


if __name__ == "__main__":
    test_confidence_line_bands()
    test_citation_line_prefers_source_article_then_note()
    test_generate_pdf_with_explain_mode_data()
    test_generate_pdf_falls_back_without_explain_mode_data()
    print("test_pdf_report OK")
