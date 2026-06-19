"""
detector_scorer.py — Layer 3: Deterministic feature-based risk scorer.

Combines structured output from Layer 1 (rules) and Layer 2 (DistilBERT)
into a single 0-100 risk score.  No ML inference — pure arithmetic on
feature vectors.  Designed so the weights can later be replaced by a
trained sklearn MLPClassifier without changing the public API.

De-duplication:  When the same finding is caught by both L1 red flags and
L2 flagged clauses, it is counted only once (the higher-penalty source wins).

Public API
----------
    from detector.detector_scorer import layer3_score

    result = layer3_score(layer1_result, layer2_result)

Returns
-------
dict:
    score     : int 0-100  (risk score — higher means more risk)
    label     : "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"
    breakdown : list[dict]  — each deduction with reason and points
    features  : dict        — raw feature vector (useful for future MLP training)
"""
from __future__ import annotations

import logging
from typing import Optional

from detector.detector_rules import (
    clause_title,
    evaluate_contract_type_requirements,
)
from detector.clause_db import clause_guidance, clause_impact

logger = logging.getLogger(__name__)

# ── Scoring weights ────────────────────────────────────────────────────────────
# These mirror what a trained MLP would learn from labelled data.
# Negative = deduction from base score of 100.

_W_MISSING_REQUIRED   = -10   # per missing required clause (fallback weight)

# Severity-scaled penalty for a missing mandatory clause, keyed by Ilham's
# Impact_Level.  Used when the clause is reconciled to her DB; otherwise the
# flat _W_MISSING_REQUIRED applies.
_IMPACT_WEIGHTS: dict[str, int] = {
    "CRITICAL": -20,
    "HIGH":     -15,
    "MEDIUM":   -10,
    "LOW":      -5,
}
_W_RED_FLAG_HIGH      = -25   # per HIGH severity L1 red flag
_W_RED_FLAG_MEDIUM    = -10   # per MEDIUM severity L1 red flag
_W_L2_UNIQUE          = -8    # per L2 flagged clause NOT already in L1
_W_NO_GOVERNING_LAW   = -12   # governing law clause absent (dedicated penalty)
_W_NO_VENUE           = -8    # jurisdiction/venue clause absent (dedicated penalty)

# These clause IDs have dedicated penalty lines; excluding them from the generic
# missing_required count prevents double-penalising the same gap.
_GOVERNANCE_CLAUSE_IDS = frozenset({"governing_law", "jurisdiction_venue"})

# L1 red flag IDs that map to L2 clause labels (for de-duplication)
_L1_TO_L2: dict[str, str] = {
    "rights_waiver":            "rights_waiver",
    "leonine_profit":           "leonine_clause",
    "leonine_no_loss":          "leonine_clause",
    "excessive_penalty":        "payment_risk",
    "unilateral_modification":  "unilateral_modification",
}


# ── Feature extraction ─────────────────────────────────────────────────────────

def _extract_features(layer1: dict, layer2: dict) -> dict:
    """Convert L1 + L2 dicts into a flat numeric feature vector."""
    red_flags   = layer1.get("red_flags", [])
    clauses     = layer1.get("clause_presence", [])
    l2_flagged  = layer2.get("flagged_clauses", []) if layer2 else []

    # Resolve which clauses are mandatory *for this contract type* (the explicit
    # contract-type → clause mapping lives in detector_rules._CONTRACT_TYPE_PROFILES).
    doc_type = ((layer2.get("document_type") or {}).get("label") if layer2 else None)
    requirements = evaluate_contract_type_requirements(clauses, doc_type)

    # Exclude governing_law / jurisdiction_venue — they have dedicated penalty
    # lines in _compute_score, so counting them here would double-penalise.
    missing_mandatory_ids = [
        cid for cid in requirements["missing"] if cid not in _GOVERNANCE_CLAUSE_IDS
    ]
    missing_required = len(missing_mandatory_ids)
    high_flags   = sum(1 for f in red_flags if f["severity"] == "HIGH")
    medium_flags = sum(1 for f in red_flags if f["severity"] == "MEDIUM")

    # L1 labels already covered (to de-duplicate with L2)
    l1_covered_l2_labels = {
        _L1_TO_L2[f["id"]] for f in red_flags if f["id"] in _L1_TO_L2
    }

    # L2 findings not already captured by L1
    unique_l2 = [
        c for c in l2_flagged
        if c["label"] not in l1_covered_l2_labels
    ]

    # clause_presence pattern check OR the dedicated detect_governing_law/detect_venue
    # functions (which use different patterns) — either source counts as "found"
    has_governing_law = (
        bool(layer1.get("governing_law"))
        or any(c["clause_id"] == "governing_law" and c["present"] for c in clauses)
    )
    has_venue = (
        bool(layer1.get("venue"))
        or any(c["clause_id"] == "jurisdiction_venue" and c["present"] for c in clauses)
    )

    return {
        "missing_required":     missing_required,
        "missing_mandatory_ids": missing_mandatory_ids,
        "contract_type":        requirements["contract_type"],
        "matched_profile":      requirements["matched_profile"],
        "mandatory_clauses":    requirements["mandatory"],
        "high_flags":           high_flags,
        "medium_flags":         medium_flags,
        "unique_l2":            len(unique_l2),
        "unique_l2_items":      unique_l2,
        "has_governing_law":    has_governing_law,
        "has_venue":            has_venue,
        "l2_available":         bool(layer2 and layer2.get("layer2_available")),
    }


# ── Scoring ────────────────────────────────────────────────────────────────────

def _compute_score(features: dict) -> tuple[int, list[dict]]:
    """Apply weights to features; return (score, breakdown)."""
    score = 100
    breakdown = []

    ctype = features.get("contract_type", "unknown")
    for cid in features["missing_mandatory_ids"]:
        # Weight by Ilham's Impact_Level when the clause is reconciled to her DB;
        # fall back to the flat weight for unmapped clauses.
        impact = clause_impact(cid)
        points = _IMPACT_WEIGHTS.get(impact, _W_MISSING_REQUIRED)
        score += points
        sev = f" [{impact}]" if impact else ""
        breakdown.append({
            "reason": f"Missing mandatory clause for {ctype} — {clause_title(cid)}{sev}",
            "points": points,
        })

    for _ in range(features["high_flags"]):
        score += _W_RED_FLAG_HIGH
        breakdown.append({
            "reason": "HIGH severity red flag (L1)",
            "points": _W_RED_FLAG_HIGH,
        })

    for _ in range(features["medium_flags"]):
        score += _W_RED_FLAG_MEDIUM
        breakdown.append({
            "reason": "MEDIUM severity red flag (L1)",
            "points": _W_RED_FLAG_MEDIUM,
        })

    for item in features["unique_l2_items"]:
        score += _W_L2_UNIQUE
        breakdown.append({
            "reason": f"Flagged clause — {item['label']} (L2, not in L1)",
            "points": _W_L2_UNIQUE,
        })

    if not features["has_governing_law"]:
        score += _W_NO_GOVERNING_LAW
        breakdown.append({
            "reason": "Governing law clause absent",
            "points": _W_NO_GOVERNING_LAW,
        })

    if not features["has_venue"]:
        score += _W_NO_VENUE
        breakdown.append({
            "reason": "Jurisdiction / venue clause absent",
            "points": _W_NO_VENUE,
        })

    score = max(0, min(100, score))
    # Convert safety score (100=clean) to risk score (100=risky)
    risk_score = 100 - score
    return risk_score, breakdown


def _label(risk_score: int) -> str:
    if risk_score <= 30:
        return "LOW"
    if risk_score <= 60:
        return "MEDIUM"
    if risk_score <= 80:
        return "HIGH"
    return "CRITICAL"


# ── Public API ─────────────────────────────────────────────────────────────────

def _required_clauses_report(features: dict, lang: str) -> list[dict]:
    """Per mandatory clause (for the detected contract type): presence + Ilham's
    lawyer-authored rationale, when the clause is reconciled to the DB.

    Pure surfacing — does not affect the score.
    """
    report = []
    for item in features.get("mandatory_clauses", []):
        cid = item["clause_id"]
        entry = {
            "clause_id": cid,
            "title":     item["title"],
            "present":   item["present"],
        }
        g = clause_guidance(cid, lang)
        if g:
            entry.update({
                "impact_level":    g["impact_level"],
                "reason":          g["reason"],
                "recommendation":  g["recommendation"],
                "business_impact": g["business_impact"],
                "source":          "ilham_required_clauses",
            })
        report.append(entry)
    return report


def layer3_score(
    layer1: dict,
    layer2: Optional[dict] = None,
    lang: str = "EN",
) -> dict:
    """
    Compute the final combined risk score from Layer 1 and Layer 2 results.

    Parameters
    ----------
    layer1 : result of detector_rules.layer1_analyze()
    layer2 : result of detector_distilbert.layer2_analyze(), or None
    lang   : language code for required-clause rationale (EN/ID/FR; default EN)

    Returns
    -------
    dict with keys: score, label, breakdown, features, contract_type,
    required_clauses
    """
    if layer2 is None:
        layer2 = {}

    features = _extract_features(layer1, layer2)
    score, breakdown = _compute_score(features)
    label = _label(score)

    required_clauses = _required_clauses_report(features, lang)

    # Remove internal helper key before returning
    export_features = {k: v for k, v in features.items() if k != "unique_l2_items"}

    logger.info(
        "Layer 3: score=%d (%s) deductions=%d contract_type=%s missing_mandatory=%d",
        score, label, len(breakdown),
        features.get("contract_type"), len(features.get("missing_mandatory_ids", [])),
    )

    return {
        "score":            score,
        "label":            label,
        "breakdown":        breakdown,
        "features":         export_features,
        "contract_type":    features.get("contract_type"),
        "required_clauses": required_clauses,
    }
