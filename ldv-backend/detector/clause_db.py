"""
clause_db.py — Runtime adapter for Ilham's required-clause database.

Reads datasets/required_clauses.csv (lawyer-authored) and exposes it to the
rest of the pipeline.  No ML, no models — a plain CSV parsed once into memory.

The CSV is a *clause library*: for each required clause it gives detection
keywords (per language), an impact level, and human-written Reason /
Recommendation / Business_Impact text.  It does NOT map clauses to contract
types — that mapping lives in detector_rules._CONTRACT_TYPE_PROFILES.

Day-1 scope: surface the rationale (Reason / Recommendation / Business_Impact
+ Impact_Level) for required clauses.  Detection keywords and severity
weighting are wired in on Day 2.

CSV schema
----------
    ID, Category, Clause_Name, Language, Keywords, Risk_Score,
    Impact_Level, Reason, Recommendation, Business_Impact

Public API
----------
    from detector.clause_db import clause_guidance, all_guidance, db_available

    g = clause_guidance("notice_period")        # -> dict | None
    g = clause_guidance("notice_period", "FR")  # French rationale if present
"""
from __future__ import annotations

import csv
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# datasets/ lives at the repo root: detector/ -> ldv-backend/ -> LDV/
_CSV_PATH = Path(__file__).resolve().parent.parent.parent / "datasets" / "required_clauses_MASTER.csv"

# ── Reconciliation: our clause_id  ->  Ilham's Clause_Name ──────────────────────
# Only confident 1:1 matches.  This map is *complete* as far as the two
# vocabularies overlap — it is NOT a partial stub.  The remaining gap is by
# design, in both directions:
#   • Profile clause IDs with no entry here (lease_term, rent_amount,
#     license_grant, ip_ownership, title_transfer, security_deposit,
#     maintenance_responsibility, default_provisions, capital_contribution,
#     profit_sharing, management_rights, goods_description, return_of_materials,
#     warranty_disclaimer) are clause types Ilham's CSV does not cover, so they
#     correctly fall back to the flat _W_MISSING_REQUIRED penalty in L3.  Do NOT
#     force them onto a near-name (e.g. warranty_disclaimer -> "Warranty" is a
#     semantic inverse and would attach misleading guidance).
#   • Ilham clauses with no entry here (Donation Object, Vehicle Description,
#     Duties of Agent, Scope of Authority, Full and Final Release, etc.) belong
#     to contract types we don't profile (donation, vehicle sale, agency,
#     settlement).  They wait for a matching detector, not a mapping.
# Adding a real mapping requires BOTH a detector clause_id and an Ilham
# Clause_Name that mean the same clause.  verify_mappings() guards against drift.
_CLAUSE_ID_TO_ILHAM: dict[str, str] = {
    "governing_law":        "Governing Law",
    "payment_terms":        "Payment Terms",
    "termination":          "Termination",
    "dispute_resolution":   "Dispute Resolution",
    "limitation_liability": "Liability",
    "confidentiality":      "Confidentiality",
    "force_majeure":        "Force Majeure",
    # NB: Ilham's "Notice" clause = formal communications between parties, NOT
    # an employment notice period (which she folds into "Termination").  So our
    # notice_period clause is intentionally left unmapped rather than mis-linked.
    "compensation":         "Salary",
    "working_hours":        "Working Hours",
    "scope_of_services":    "Scope of Work",
    "principal_amount":     "Loan Amount",
    "interest_rate":        "Interest Rate",
    "repayment_schedule":   "Repayment Schedule",
    "delivery_terms":       "Delivery Terms",
    "warranty":             "Warranty",
    # Cross-cutting boilerplate (detectors added in detector_rules generic section)
    "indemnification":      "Indemnification",
    "insurance":            "Insurance",
    "assignment":           "Assignment",
    "severability":         "Severability",
    "entire_agreement":     "Entire Agreement",
    "amendment":            "Amendment",
}

_DEFAULT_LANG = "EN"

# Lazy singleton: {clause_name -> {lang -> row dict}}
_DB: Optional[dict[str, dict[str, dict]]] = None


def _load() -> dict[str, dict[str, dict]]:
    """Parse the CSV once into {Clause_Name: {Language: row}}.  Fail soft."""
    global _DB
    if _DB is not None:
        return _DB

    db: dict[str, dict[str, dict]] = {}
    if not _CSV_PATH.exists():
        logger.warning("Required-clause DB not found at %s — guidance disabled.", _CSV_PATH)
        _DB = db
        return _DB

    try:
        with open(_CSV_PATH, newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                name = (row.get("Clause_Name") or "").strip()
                lang = (row.get("Language") or _DEFAULT_LANG).strip().upper()
                if not name:
                    continue
                db.setdefault(name, {})[lang] = {
                    "clause_name":       name,
                    "impact_level":      (row.get("Impact_Level") or "").strip(),
                    "risk_score":        _to_int(row.get("Risk_Score")),
                    "keywords":          _split_keywords(row.get("Keywords")),
                    "reason":            (row.get("Reason") or "").strip(),
                    "recommendation":    (row.get("Recommendation") or "").strip(),
                    "business_impact":   (row.get("Business_Impact") or "").strip(),
                    # MASTER-only fields
                    "contract_type":     (row.get("Contract_Type") or "").strip(),
                    "jurisdiction":      (row.get("Jurisdiction") or "").strip(),
                    "requirement_level": (row.get("Requirement_Level") or "").strip(),
                    "legal_reference":   (row.get("Legal_Reference") or "").strip(),
                }
        logger.info("Loaded required-clause DB: %d clauses from %s", len(db), _CSV_PATH.name)
    except Exception as e:  # malformed CSV must not break analysis
        logger.warning("Failed to load required-clause DB (%s) — guidance disabled.", e)
        db = {}

    _DB = db
    return _DB


def _to_int(val: Optional[str]) -> int:
    try:
        return int(float(val))
    except (TypeError, ValueError):
        return 0


def _split_keywords(val: Optional[str]) -> list[str]:
    if not val:
        return []
    return [k.strip() for k in val.split(",") if k.strip()]


# ── Public API ─────────────────────────────────────────────────────────────────

def db_available() -> bool:
    """True if the CSV was found and parsed with at least one clause."""
    return bool(_load())


def clause_guidance(clause_id: str, lang: str = _DEFAULT_LANG) -> Optional[dict]:
    """Return Ilham's guidance for one of our clause_ids, or None.

    Falls back to the English row when the requested language is absent.
    """
    db = _load()
    name = _CLAUSE_ID_TO_ILHAM.get(clause_id)
    if not name:
        return None
    by_lang = db.get(name)
    if not by_lang:
        return None
    return by_lang.get((lang or "").upper()) or by_lang.get(_DEFAULT_LANG) or next(iter(by_lang.values()))


def all_guidance(lang: str = _DEFAULT_LANG) -> dict[str, dict]:
    """Return {clause_id: guidance} for every reconciled clause that has DB data."""
    out: dict[str, dict] = {}
    for cid in _CLAUSE_ID_TO_ILHAM:
        g = clause_guidance(cid, lang)
        if g:
            out[cid] = g
    return out


def clause_keywords(clause_id: str) -> list[str]:
    """Union of Ilham's detection keywords across all languages for a clause.

    Language-agnostic on purpose: the caller (clause presence check) doesn't
    know the doc language, and EN/ID/FR keyword sets are distinct terms — a
    union just adds detection coverage, never removes it.  Empty if unmapped.
    """
    db = _load()
    name = _CLAUSE_ID_TO_ILHAM.get(clause_id)
    if not name:
        return []
    seen: list[str] = []
    for row in db.get(name, {}).values():
        for kw in row["keywords"]:
            low = kw.lower()
            if low and low not in seen:
                seen.append(low)
    return seen


def clause_impact(clause_id: str) -> str:
    """Ilham's Impact_Level for a clause (CRITICAL/HIGH/MEDIUM/LOW), or "" if unmapped."""
    g = clause_guidance(clause_id)  # impact is language-invariant; EN row is fine
    return (g["impact_level"] if g else "").upper()


def verify_mappings() -> list[str]:
    """Return the Ilham Clause_Names referenced by the map that are NOT in the CSV.

    Empty list == healthy.  A non-empty result means the CSV drifted (a clause
    was renamed/removed) and the affected clause_ids have silently lost their
    severity-scaled penalty, reverting to the flat L3 fallback.  Cheap enough to
    call at startup; the real point is to fail loud instead of scoring wrong.
    """
    db = _load()
    if not db:  # CSV missing entirely is a separate, already-logged condition
        return []
    return sorted({nm for nm in _CLAUSE_ID_TO_ILHAM.values() if nm not in db})


if __name__ == "__main__":  # python3 detector/clause_db.py — drift + coverage check
    assert db_available(), "CSV not found/parsed — cannot verify mappings"
    broken = verify_mappings()
    assert not broken, f"Map drift: Ilham names missing from CSV: {broken}"
    print(f"OK: {len(_CLAUSE_ID_TO_ILHAM)} mappings, all names present in CSV.")
    print(f"    {len(_load())} clauses in DB; "
          f"{len(_load()) - len(set(_CLAUSE_ID_TO_ILHAM.values()))} not reconciled "
          f"(contract types we don't profile — expected).")
