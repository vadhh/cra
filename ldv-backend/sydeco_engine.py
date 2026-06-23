"""
sydeco_engine.py — Lightweight clause classifier using rule-based fallback patterns (CR-03 decoupled).

Classifies contract clauses into abusive_clause or payment_risk labels.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)

LABEL_MAP: dict[int, str] = {
    0: "abusive_clause",
    1: "payment_risk",
    2: "missing_mandatory",
    3: "normal",
}

# Contribution of each flagged clause to the raw risk score
_RISK_WEIGHTS: dict[str, int] = {
    "abusive_clause":    20,
    "payment_risk":      15,
    "missing_mandatory": 10,
}

_RULE_SPECS: list[dict] = [
    {
        "label": "abusive_clause",
        "patterns": [
            r"waives?\s+all\s+(?:legal\s+)?rights?",
            r"no\s+liability\s+whatsoever",
            r"(?:may|can|shall)\s+(?:modify|amend|change|terminate)\s+(?:this\s+)?(?:agreement|contract|terms?)\s+(?:at\s+any\s+time|without\s+notice)",
            r"all\s+(?:profits?|benefits?)\s+(?:shall\s+be\s+)?(?:go\s+to|belong\s+to|assigned\s+to)\s+one\s+party",
            r"sole\s+(?:and\s+absolute\s+)?discretion\s+without\s+(?:notice|consent)",
            r"renonce\s+[aà]\s+(?:tout|tous)\s+(?:ses\s+)?droits?",
            r"melepaskan\s+semua\s+hak",
        ],
    },
    {
        "label": "payment_risk",
        "patterns": [
            r"penalty\s+(?:of\s+)?(?:[1-9]\d|[1-9]\d\d)\s*%\s*per\s+(?:day|month)",
            r"interest\s+(?:rate\s+)?of\s+(?:[1-9]\d|[1-9]\d\d)\s*%",
            r"late\s+(?:payment\s+)?(?:fee|penalty|charge|interest)",
            r"p[eé]nalit[eé]\s+de\s+(?:[1-9]\d|[1-9]\d\d)\s*%",
            r"denda\s+(?:[1-9]\d|[1-9]\d\d)\s*%",
        ],
    },
]


def _rule_classify_clauses(clauses: list[str]) -> list[dict]:
    """Rule-based tagger: tag clauses matching known abusive/payment-risk patterns."""
    results = []
    for clause in clauses:
        for spec in _RULE_SPECS:
            for pat in spec["patterns"]:
                if re.search(pat, clause, re.I):
                    results.append({"clause": clause, "label": spec["label"]})
                    break
            else:
                continue
            break
    return results


def _split_clauses(text: str) -> list[str]:
    """Split contract text into clause-sized chunks suitable for classification."""
    chunks = re.split(r"(?<=[.!?])\s{1,3}(?=[A-Z0-9\(]|\Z)|\n{2,}", text)
    return [c.strip() for c in chunks if len(c.strip()) > 30]


def is_available() -> bool:
    """Tagger is always available in rule-only decoupled mode."""
    return True


def classify_clauses(text: str) -> list[dict]:
    """
    Classify each clause extracted from *text*.

    Returns
    -------
    list of {"clause": str, "label": str}
    """
    clauses = _split_clauses(text)
    return _rule_classify_clauses(clauses)


def quick_risk_score(text: str) -> dict | None:
    """
    Derive a rough risk score (0-100) from clause classifications.

    Returns
    -------
    {"score": int, "label": "LOW"|"MEDIUM"|"HIGH", "clause_count": int, "flagged": int}
    """
    tags = classify_clauses(text)
    if not tags:
        return None

    raw = sum(_RISK_WEIGHTS.get(t["label"], 0) for t in tags)
    score = min(100, raw)

    if score <= 33:
        label = "LOW"
    elif score <= 66:
        label = "MEDIUM"
    else:
        label = "HIGH"

    flagged = sum(1 for t in tags if t["label"] != "missing_mandatory")

    return {
        "score": score,
        "label": label,
        "clause_count": len(tags),
        "flagged": flagged,
    }
