"""risk_explainer.py — fast, deterministic per-finding explanations ("Explain Mode").

Attaches an inline `explanation: {...}` object to every red flag and missing
required clause in layer1, mirroring how citation_db.annotate_layer1() attaches
`citations: [...]`. Purely assembled from already-computed L1 data plus two
static guidance tables below — no ML calls, so this runs on every request (no
`?explain=1` gate needed, unlike the slower Qwen narrative mode in
detector_explain.py, which this module does not touch or replace).
"""
from __future__ import annotations

from detector import clause_db
from detector.detector_rules import required_clauses_for

# Confidence is a static per-detection-method score, not a per-instance ML
# probability: regex rules are hand-tuned/high-precision; keyword_db findings
# require corroboration (see risk_clause_db.py's _MIN_CORROBORATION); a
# missing-clause finding has survived a 3-pass check (regex + keyword +
# semantic NLI backfill) by the time it reaches here.
# ponytail: method-level static score, not per-instance. Upgrade path: thread
# a real per-instance probability through if a customer needs finer-grained
# numbers than these.
_SOURCE_CONFIDENCE = {"regex": 0.90, "keyword_db": 0.75}
_MISSING_CLAUSE_CONFIDENCE = 0.80

# Reason/recommendation for the hand-written regex red-flag rules in
# detector_rules._RED_FLAGS. keyword_db findings carry their own reason/
# recommendation straight from the lawyer-authored CSVs (risk_clause_db.py)
# instead of using this table. Add an entry here whenever a new rule is added
# to detector_rules._RED_FLAGS.
#
# `recommendation` is drafted as ready-to-paste replacement clause language
# (not "how to fix" advice) per reviewer feedback 2026-07-13: "Do not only
# explain. Generate the beginning of a replacement clause." `illegal_object`
# is the one deliberate exception -- an illegal clause cannot be redrafted
# into a legal one, so its recommendation is a removal instruction instead.
_RED_FLAG_GUIDANCE: dict[str, dict[str, str]] = {
    "leonine_profit": {
        "reason": "Allocating all profits to a single party breaches the principle of mutual benefit and can render the agreement void as a leonine clause under most civil-law systems.",
        "recommendation": "Profits shall be distributed proportionally to each party's contribution as set out in Schedule A. No party may be excluded from losses while retaining the right to profits.",
    },
    "leonine_no_loss": {
        "reason": "A leonine clause that shields one party from any loss undermines the shared-risk nature of the agreement and is frequently unenforceable.",
        "recommendation": "Each party shall bear losses in proportion to their respective investment or contribution share as defined herein.",
    },
    "excessive_penalty": {
        "reason": "A penalty rate this high functions as a punitive damages clause rather than a genuine pre-estimate of loss, and courts in many jurisdictions will reduce or strike it.",
        "recommendation": "Late payment interest shall not exceed 0.5% per month (6% per annum), calculated on the overdue outstanding amount.",
    },
    "rights_waiver": {
        "reason": "A blanket waiver of all legal rights is overly broad, may be unenforceable against mandatory consumer or employment protections, and leaves the waiving party without recourse.",
        "recommendation": "Each party retains all statutory rights and remedies afforded under applicable law. No general waiver of rights is granted by this agreement.",
    },
    "unilateral_modification": {
        "reason": "Letting one party amend the agreement at will, without the other's consent, removes the mutuality required for a binding contract and exposes the other party to unpredictable terms.",
        "recommendation": "This agreement may only be amended by a written instrument signed by authorised representatives of all parties, with a minimum notice period of 30 days.",
    },
    "total_liability_exclusion": {
        "reason": "Excluding all liability regardless of cause typically fails against gross negligence, willful misconduct, or statutory protections, and signals a serious imbalance of risk.",
        "recommendation": "The total aggregate liability of either party shall not exceed the total fees paid under this agreement in the 12 months preceding the event giving rise to liability.",
    },
    "auto_renewal_no_notice": {
        "reason": "Automatic renewal with little or no notice traps the counterparty into a new term before they can reasonably evaluate the relationship, and violates consumer-protection notice requirements in several jurisdictions.",
        "recommendation": "This agreement renews automatically for successive 12-month terms unless either party provides written notice of non-renewal at least 60 days before the current term expires.",
    },
    "short_payment_window_high": {
        "reason": "A payment window this short (days or hours) gives the paying party little room to process invoices and creates disproportionate default/penalty risk for routine delays.",
        "recommendation": "Payment shall be due within thirty (30) days of the invoice date (\"Net 30\"), unless a different term is expressly agreed in writing by both parties.",
    },
    "short_payment_window_medium": {
        "reason": "An 8-14 day payment window is tighter than standard commercial terms and can create cash-flow strain and inadvertent default risk.",
        "recommendation": "Payment shall be due within thirty (30) days of the invoice date (\"Net 30\"), unless a shorter cycle is expressly justified by the nature of the transaction.",
    },
    "customer_pays_vendor_errors": {
        "reason": "Shifting the cost of the vendor's own mistakes onto the customer removes the vendor's incentive for quality control and is an unusual departure from standard risk allocation.",
        "recommendation": "The Vendor shall bear, at no cost to the Customer, all expenses arising from the correction of errors or defects caused by the Vendor's own acts or omissions.",
    },
    "fee_for_dispute": {
        "reason": "Charging a fee merely to raise a complaint or dispute discourages legitimate claims and may be viewed as an unfair barrier to access to justice.",
        "recommendation": "Either party may raise a dispute under this agreement without payment of any fee. Dispute-resolution costs shall be allocated as set out in the Dispute Resolution clause.",
    },
    "no_liability_intentional": {
        "reason": "Excluding liability for intentional or grossly negligent conduct is void as against public policy in most legal systems -- a party cannot contract out of liability for its own bad faith.",
        "recommendation": "Nothing in this agreement excludes or limits either party's liability for intentional misconduct, fraud, or gross negligence; the liability limits in this agreement apply only to ordinary negligence.",
    },
    "illegal_object": {
        "reason": "The contract references activity that is criminal or otherwise illegal; an agreement with an illegal object is void and unenforceable in its entirety.",
        "recommendation": "Remove the illegal subject matter immediately and have counsel review whether the remainder of the contract is severable.",
    },
}


def _confidence_band(score: float) -> str:
    """High/Medium/Low label for a 0-1 confidence score.

    Lawyers read words better than decimals (reviewer feedback 2026-07-13);
    `confidence` (the raw float) is kept in the explanation dict alongside
    this label so a caller can still show the percentage if it wants to.
    """
    return "High" if score >= 0.85 else "Medium" if score >= 0.65 else "Low"


def _explain_red_flag(flag: dict) -> dict:
    guidance = _RED_FLAG_GUIDANCE.get(flag["id"], {})
    reason = flag.get("reason") or guidance.get("reason") or (
        f"This text matched a known risky-clause pattern ({flag.get('type', 'unspecified')})."
    )
    recommendation = flag.get("recommendation") or guidance.get("recommendation") or (
        "Have this clause reviewed and revised by counsel before signing."
    )
    confidence = _SOURCE_CONFIDENCE.get(flag.get("source"), 0.75)
    return {
        "clause": flag.get("description") or flag.get("id"),
        "reason": reason,
        "severity": flag.get("severity", "MEDIUM"),
        "suggested_correction": recommendation,
        "confidence": confidence,
        "confidence_label": _confidence_band(confidence),
        "source_reference": {
            "text": flag.get("evidence"),
            "span": flag.get("evidence_span"),
        },
    }


def _explain_missing_clause(entry: dict, jurisdiction: str | None) -> dict:
    title = entry.get("title") or entry["clause_id"]
    guidance = clause_db.clause_guidance(entry["clause_id"])
    if guidance:
        reason = guidance["reason"]
        recommendation = guidance["recommendation"]
    else:
        reason = f"'{title}' is a required clause for this contract type and was not found in the document text."
        recommendation = (
            f"Add a clause covering '{title}' appropriate to {jurisdiction or 'the applicable'} "
            "law; consult a licensed reviewer for exact wording."
        )
    severity = clause_db.clause_impact(entry["clause_id"]) or "MEDIUM"
    return {
        "clause": f"{title} (missing)",
        "reason": reason,
        "severity": severity,
        "suggested_correction": recommendation,
        "confidence": _MISSING_CLAUSE_CONFIDENCE,
        "confidence_label": _confidence_band(_MISSING_CLAUSE_CONFIDENCE),
        "source_reference": {"text": None, "span": None},
    }


def explain_findings(layer1: dict, jurisdiction: str | None, doc_type_label: str | None) -> None:
    """Attach an inline `explanation: {...}` to every red flag and missing
    required clause in *layer1*, in place. Pure assembly -- no ML calls."""
    for flag in layer1.get("red_flags") or []:
        flag["explanation"] = _explain_red_flag(flag)

    required = set(required_clauses_for(doc_type_label))
    for entry in layer1.get("clause_presence") or []:
        if entry["clause_id"] in required and not entry.get("present"):
            entry["explanation"] = _explain_missing_clause(entry, jurisdiction)
