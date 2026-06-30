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
import json
import os

# Fallback default weights (provisional uncalibrated)
_DEFAULT_POLICY = {
    "version": "fallback_v1",
    "calibration_status": "provisional_uncalibrated",
    "limitation_notice": "This risk score is based on a provisional, uncalibrated scoring policy. The weights are uncalibrated and should not be used as authoritative legal advice.",
    "weights": {
        "missing_required_fallback": -10,
        "impact_weights": {
            "CRITICAL": -20,
            "HIGH": -15,
            "MEDIUM": -10,
            "LOW": -5
        },
        "red_flag_high": -25,
        "red_flag_medium": -10,
        "l2_unique": -8,
        "no_governing_law": -12,
        "no_venue": -8
    }
}

def load_scoring_policy(policy_name: Optional[str] = None) -> dict:
    """Load policy from detector/policies/{policy_name}.json or environment variable."""
    if not policy_name:
        policy_name = os.getenv("LDV_SCORING_POLICY", "default_v1")
    
    # Sanitize to avoid directory traversal
    policy_name = os.path.basename(policy_name)
    if not policy_name.endswith(".json"):
        policy_filename = f"{policy_name}.json"
    else:
        policy_filename = policy_name

    policy_path = os.path.join(os.path.dirname(__file__), "policies", policy_filename)
    try:
        if os.path.exists(policy_path):
            with open(policy_path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error("Failed to load scoring policy %s: %s. Falling back to default.", policy_name, e)
    
    return _DEFAULT_POLICY


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

def _compute_score(features: dict, policy: dict) -> tuple[int, list[dict]]:
    """Apply weights from policy to features; return (score, breakdown)."""
    score = 100
    breakdown = []

    w = policy.get("weights", _DEFAULT_POLICY["weights"])
    impact_weights = w.get("impact_weights", _DEFAULT_POLICY["weights"]["impact_weights"])
    w_missing_fallback = w.get("missing_required_fallback", -10)
    w_red_flag_high = w.get("red_flag_high", -25)
    w_red_flag_medium = w.get("red_flag_medium", -10)
    w_l2_unique = w.get("l2_unique", -8)
    w_no_gov_law = w.get("no_governing_law", -12)
    w_no_venue = w.get("no_venue", -8)

    ctype = features.get("contract_type", "unknown")
    for cid in features["missing_mandatory_ids"]:
        # Weight by Ilham's Impact_Level when the clause is reconciled to her DB;
        # fall back to the flat weight for unmapped clauses.
        impact = clause_impact(cid)
        points = impact_weights.get(impact, w_missing_fallback)
        score += points
        sev = f" [{impact}]" if impact else ""
        breakdown.append({
            "reason": f"Missing mandatory clause for {ctype} — {clause_title(cid)}{sev}",
            "points": points,
        })

    for _ in range(features["high_flags"]):
        score += w_red_flag_high
        breakdown.append({
            "reason": "HIGH severity red flag (L1)",
            "points": w_red_flag_high,
        })

    for _ in range(features["medium_flags"]):
        score += w_red_flag_medium
        breakdown.append({
            "reason": "MEDIUM severity red flag (L1)",
            "points": w_red_flag_medium,
        })

    for item in features["unique_l2_items"]:
        score += w_l2_unique
        breakdown.append({
            "reason": f"Flagged clause — {item['label']} (L2, not in L1)",
            "points": w_l2_unique,
        })

    if not features["has_governing_law"]:
        score += w_no_gov_law
        breakdown.append({
            "reason": "Governing law clause absent",
            "points": w_no_gov_law,
        })

    if not features["has_venue"]:
        score += w_no_venue
        breakdown.append({
            "reason": "Jurisdiction / venue clause absent",
            "points": w_no_venue,
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
                "source":          "kb_required_clauses",
            })
        report.append(entry)
    return report


_mlp_pipeline = None
_MLP_LOADED = False


def _mlp_score(features: dict) -> int | None:
    """Load risk_scorer.pkl once and return a score, or None if unavailable."""
    global _mlp_pipeline, _MLP_LOADED
    if not _MLP_LOADED:
        _MLP_LOADED = True
        pkl = os.path.join(os.path.dirname(__file__), "..", "data", "risk_scorer.pkl")
        pkl = os.path.normpath(os.getenv("LDV_RISK_SCORER_PATH", pkl))
        if os.path.exists(pkl):
            import pickle
            # Safe: pkl is generated by scripts/train_risk_scorer.py on this machine
            # and only loaded when LDV_USE_MLP_SCORER=1 is explicitly set by an operator.
            # Never load user-supplied pickles.
            with open(pkl, "rb") as f:
                _mlp_pipeline = pickle.load(f)
            logger.info("MLP risk scorer loaded from %s", pkl)
        else:
            logger.warning("LDV_USE_MLP_SCORER=1 but %s not found — falling back to deterministic", pkl)

    if _mlp_pipeline is None:
        return None

    vec = [[
        float(features.get("missing_required", 0)),
        float(features.get("high_flags", 0)),
        float(features.get("medium_flags", 0)),
        float(features.get("unique_l2", 0)),
        float(features.get("has_governing_law", False)),
        float(features.get("has_venue", False)),
        float(features.get("l2_available", False)),
    ]]
    raw = _mlp_pipeline.predict(vec)[0]
    return max(0, min(100, int(round(raw))))


def layer3_score(
    layer1: dict,
    layer2: Optional[dict] = None,
    lang: str = "EN",
    policy_name: Optional[str] = None,
) -> dict:
    """
    Compute the final combined risk score from Layer 1 and Layer 2 results.

    Parameters
    ----------
    layer1      : result of detector_rules.layer1_analyze()
    layer2      : result of detector_distilbert.layer2_analyze(), or None
    lang        : language code for required-clause rationale (EN/ID/FR; default EN)
    policy_name : scoring policy version file to resolve weights from

    Returns
    -------
    dict with keys: score, label, breakdown, features, contract_type,
    required_clauses, policy_version, calibration_status, limitation_notice, confidence
    """
    if layer2 is None:
        layer2 = {}

    policy = load_scoring_policy(policy_name)

    features = _extract_features(layer1, layer2)

    if os.getenv("LDV_USE_MLP_SCORER") == "1":
        mlp = _mlp_score(features)
        if mlp is not None:
            score = mlp
            breakdown = [{"reason": "MLP scorer (bootstrap)", "points": None}]
        else:
            score, breakdown = _compute_score(features, policy)
    else:
        score, breakdown = _compute_score(features, policy)

    label = _label(score)

    required_clauses = _required_clauses_report(features, lang)

    # Calculate analysis confidence (SCR-03)
    if features.get("l2_available") and isinstance(layer2, dict) and "document_type" in layer2:
        doc_type_info = layer2["document_type"] or {}
        confidence_val = doc_type_info.get("confidence")
        if confidence_val is not None:
            confidence = round(confidence_val * 100, 1)
        else:
            confidence = 50.0  # fallback when L2 runs but has no doc type confidence
    else:
        confidence = 30.0  # low confidence if L2 MNLI is not run/available

    # Remove internal helper key before returning
    export_features = {k: v for k, v in features.items() if k != "unique_l2_items"}

    logger.info(
        "Layer 3: score=%d (%s) deductions=%d contract_type=%s missing_mandatory=%d policy=%s confidence=%.1f%%",
        score, label, len(breakdown),
        features.get("contract_type"), len(features.get("missing_mandatory_ids", [])),
        policy.get("version"), confidence,
    )

    return {
        "score":              score,
        "label":              label,
        "breakdown":          breakdown,
        "features":           export_features,
        "contract_type":      features.get("contract_type"),
        "required_clauses":   required_clauses,
        "policy_version":     policy.get("version", "fallback_v1"),
        "calibration_status": policy.get("calibration_status", "provisional_uncalibrated"),
        "limitation_notice":  policy.get("limitation_notice", ""),
        "confidence":         confidence,
    }
