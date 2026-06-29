"""
detector_distilbert.py — Layer 2: DistilBERT-based semantic analysis.

Uses zero-shot NLI (Natural Language Inference) for document type detection
and suspicious clause classification — no fine-tuning required.

Model: typeform/distilbert-base-uncased-mnli (~67 MB, English)
Input: English text (translated by app.py when source language != English)

Public API
----------
    from detector.detector_distilbert import layer2_analyze

    result = layer2_analyze(text)

Returns
-------
dict:
    document_type    : {"label": str, "confidence": float, "candidates": list}
    flagged_clauses  : list[{"text": str, "label": str, "confidence": float}]
    layer2_available : bool  — False when model not loaded
"""
from __future__ import annotations

import logging
import re
from typing import Optional

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

logger = logging.getLogger(__name__)

import os as _os
_ENV_MODEL   = _os.getenv("LDV_DISTILBERT_MODEL", "")
_LOCAL_MODEL = _os.path.join(_os.path.dirname(__file__), "..", "models", "distilbert-base-uncased-mnli")
MODEL_ID = (
    _ENV_MODEL   if _ENV_MODEL   and _os.path.isdir(_ENV_MODEL)
    else _LOCAL_MODEL if _os.path.isdir(_LOCAL_MODEL)
    else "typeform/distilbert-base-uncased-mnli"
)

# ── Multilingual keyword-based document type detection ────────────────────────
# Used as a fallback / tiebreaker when NLI confidence is below the threshold.
# Patterns are anchored as whole words (\b) to avoid false matches like
# "employé annuellement" (French: "applied annually") triggering employment.

_KEYWORD_DOC_TYPES: dict[str, list[str]] = {
    "lease agreement": [
        r"\bbail\b", r"\bbailleur\b", r"\blocataire\b", r"\bloyer\b",
        r"\bhuurder\b", r"\bverhuurder\b", r"\bhuurprijs\b",
        r"\bhuurovereenkomst\b", r"\blandlord\b", r"\btenant\b",
        r"\brental\b", r"\brent\b", r"\blease\b", r"\bapartement\b",
        r"\bappartement\b", r"\bwoning\b", r"\bpremises\b",
    ],
    "employment contract": [
        r"\bemployeur\b", r"\bcontrat\s+de\s+travail\b",
        r"\barbeidsovereenkomst\b", r"\bsalari[eé]\b",
        r"\bwerknemer\b", r"\bwerkgever\b", r"\bsalary\b",
        r"\bwages?\b", r"\bemployee\b", r"\bemployer\b",
        r"\bperjanjian\s+kerja\b", r"\bkontrak\s+kerja\b",
    ],
    "non-disclosure agreement": [
        r"\bnon.?disclosure\b", r"\bconfidential(?:ity)?\b", r"\bNDA\b",
        r"\bgeheimhouding\b", r"\bvertrouwelijk\b", r"\bkerahasiaan\b",
    ],
    "service agreement": [
        r"\bservice\s+agreement\b", r"\bprestation[s]?\s+de\s+service[s]?\b",
        r"\bdienstverleningsovereenkomst\b", r"\bperjanjian\s+jasa\b",
        r"\bconsultanc[ey]\b",
    ],
    "loan agreement": [
        r"\bloan\s+agreement\b", r"\bpr[eê]t\b",
        r"\bleen(?:overeenkomst)?\b", r"\bborr?ower\b", r"\blender\b",
        r"\bpinjaman\b",
    ],
    "partnership agreement": [
        r"\bpartnership\b", r"\bvennoot(?:schap)?\b", r"\bpersekutuan\b",
    ],
    "software license": [
        r"\bsoftware\s+licen[sc]e\b", r"\blicense\s+agreement\b",
        r"\blicensor\b", r"\blicensee\b", r"\bend.?user\s+licen[sc]e\b",
        r"\bEULA\b", r"\bsource\s+code\b", r"\blicence\s+de\s+logiciel\b",
        r"\blisensi\s+perangkat\s+lunak\b", r"\bsoftwarelicentie\b",
    ],
    "invoice": [
        r"\binvoice\b", r"\binvoice\s+(?:number|no\.?|#)\b",
        r"\btax\s+invoice\b", r"\bfaktur\b", r"\bfaktur\s+pajak\b",
        r"\bfacture\b", r"\bfactuur\b",
        r"\bbill\s+to\b", r"\bship\s+to\b",
        r"\bamount\s+due\b", r"\bsubtotal\b",
    ],
    "receipt": [
        r"\breceipt\b", r"\breçu\b", r"\bkwitansi\b",
        r"\bbon\s+de\s+caisse\b", r"\bkas\s+bon\b",
        r"\bpayment\s+received\b", r"\breceived\s+with\s+thanks\b",
    ],
    "purchase order": [
        r"\bpurchase\s+order\b", r"\bP\.?O\.?\s*[#\-]?\s*\d",
        r"\bbon\s+de\s+commande\b", r"\bbestelbon\b",
        r"\bpesanan\s+pembelian\b", r"\bsurat\s+pesanan\b",
        r"\border\s+confirmation\b",
    ],
}

# Minimum keyword hits to trust a keyword result over NLI
_KEYWORD_MIN_HITS = 2
# NLI confidence below this → apply keyword override when keyword is strong
_NLI_OVERRIDE_THRESHOLD = 0.40


def _keyword_doc_type(text: str) -> tuple[str | None, int]:
    """Return (best_label, hit_count) from keyword matching on text[:1200]."""
    snippet = text[:1200]
    scores: dict[str, int] = {}
    for label, patterns in _KEYWORD_DOC_TYPES.items():
        count = sum(1 for p in patterns if re.search(p, snippet, re.I))
        if count > 0:
            scores[label] = count
    if not scores:
        return None, 0
    best = max(scores, key=lambda k: scores[k])
    return best, scores[best]


# ── Document type labels with calibrated hypotheses ───────────────────────────
# Each label has a specific hypothesis proven to discriminate well under
# typeform/distilbert-base-uncased-mnli (MultiNLI-trained).
# The article "a/an" issue is avoided by using descriptive phrasing.

_DOC_TYPE_SPECS: list[dict] = [
    {
        "label":      "employment contract",
        "hypothesis": "This document involves employment terms between employer and employee.",
    },
    {
        "label":      "lease agreement",
        "hypothesis": "This document is a lease or rental agreement for property.",
    },
    {
        "label":      "service agreement",
        "hypothesis": "This document covers the provision of services.",
    },
    {
        "label":      "commercial agreement",
        "hypothesis": "This document is a commercial agreement between businesses.",
    },
    {
        "label":      "non-disclosure agreement",
        "hypothesis": "This document involves confidentiality and non-disclosure obligations.",
    },
    {
        "label":      "software license",
        "hypothesis": "This document grants a license to use software between licensor and licensee.",
    },
    {
        "label":      "loan agreement",
        "hypothesis": "This document covers a loan of money between lender and borrower.",
    },
    {
        "label":      "partnership agreement",
        "hypothesis": "This document establishes a business partnership between parties.",
    },
    {
        "label":      "purchase agreement",
        "hypothesis": "This document covers the purchase or sale of goods or assets.",
    },
    {
        "label":      "consulting agreement",
        "hypothesis": "This document covers consulting or advisory services.",
    },
    {
        "label":      "general contract",
        "hypothesis": "This is a general legal agreement between two or more parties.",
    },
    {
        "label":      "invoice",
        "hypothesis": "This document is an invoice or bill requesting payment for goods or services.",
    },
    {
        "label":      "receipt",
        "hypothesis": "This document is a receipt confirming that payment has been received.",
    },
    {
        "label":      "purchase order",
        "hypothesis": "This document is a purchase order requesting the supply of goods or services.",
    },
]

# ── Clause risk hypotheses for zero-shot classification ───────────────────────
#
# Each entry has multiple hypotheses — the highest entailment score across
# all hypotheses is used (OR-logic). Phrasings are calibrated empirically
# against typeform/distilbert-base-uncased-mnli: concrete, direct language
# outperforms abstract legal terminology for MultiNLI-trained models.

_CLAUSE_SPECS: list[dict] = [
    {
        "label": "rights_waiver",
        "hypotheses": [
            "A person gives up their legal rights in this text.",
        ],
    },
    {
        "label": "leonine_clause",
        "hypotheses": [
            "One party receives all the benefits while the other bears all the risks in this text.",
            "One party receives all profits in this text.",
            "This text gives everything to one side.",
        ],
    },
    {
        "label": "payment_risk",
        "hypotheses": [
            "This text mentions a percentage penalty for late payment.",
            "A percentage fee is charged for late payment.",
        ],
    },
    {
        "label": "unilateral_modification",
        "hypotheses": [
            "One party can change the agreement without telling the other.",
        ],
    },
]

# Minimum NLI entailment confidence to report a clause as flagged
_CLAUSE_CONFIDENCE_THRESHOLD = 0.70

# ── Semantic clause-presence hypotheses ───────────────────────────────────────
# Used to answer "is this required clause semantically present?" via NLI, for
# clauses the keyword/regex pass missed.  Only clauses that can be *required*
# (appear in detector_rules._CONTRACT_TYPE_PROFILES) need a tuned hypothesis;
# anything else falls back to a humanized template built from the clause title.
# Phrasings follow the same concrete-language calibration as _CLAUSE_SPECS.

_CLAUSE_PRESENCE_HYPOTHESES: dict[str, str] = {
    "governing_law":           "The agreement is governed by the laws of a particular place.",
    "jurisdiction_venue":      "Disputes will be handled by a specific court or location.",
    "payment_terms":           "Payment must be made in a certain amount and time.",
    "termination":             "Either party can end the agreement.",
    "dispute_resolution":      "Disputes between the parties will be resolved in a defined way.",
    "limitation_liability":    "One party's liability is limited.",
    "notice_period":           "Advance notice must be given before ending the agreement.",
    "compensation":            "The worker is paid a salary or wage.",
    "working_hours":           "The worker works a set number of hours.",
    "lease_term":              "The lease lasts for a set period.",
    "rent_amount":             "A rent amount must be paid.",
    "security_deposit":        "A security deposit must be paid.",
    "maintenance_responsibility": "One party is responsible for maintenance and repairs.",
    "license_grant":           "A license to use the software is granted.",
    "ip_ownership":            "Intellectual property ownership is assigned to a party.",
    "warranty_disclaimer":     "Warranties are disclaimed and the product is provided as is.",
    "scope_of_services":       "Services or work will be performed.",
    "confidentiality":         "Information must be kept confidential.",
    "return_of_materials":     "Confidential materials must be returned or destroyed.",
    "principal_amount":        "A sum of money is loaned.",
    "interest_rate":           "Interest is charged on the loan.",
    "repayment_schedule":      "The loan is repaid on a schedule.",
    "default_provisions":      "Consequences apply if a party defaults.",
    "capital_contribution":    "Each partner contributes capital.",
    "profit_sharing":          "Profits and losses are shared between the partners.",
    "management_rights":       "Management and decision-making rights are defined.",
    "goods_description":       "The goods being sold are described.",
    "delivery_terms":          "Goods will be delivered in a certain way.",
    "warranty":                "A warranty is provided for the goods or work.",
    "title_transfer":          "Ownership or risk passes to the buyer.",
    "indemnification":         "One party will indemnify or hold the other harmless.",
    "insurance":               "A party must maintain insurance.",
    "assignment":              "Transferring or assigning the agreement is restricted.",
    "severability":            "If one clause is invalid, the rest of the contract still applies.",
    "entire_agreement":        "This is the entire agreement between the parties.",
}

# Presence may be reported a bit more leniently than a risk flag: a clause that
# is semantically present but oddly worded is still present.
_SEM_PRESENCE_THRESHOLD = 0.65

# ── Lazy model singleton ───────────────────────────────────────────────────────

_model: Optional[AutoModelForSequenceClassification] = None
_tokenizer: Optional[AutoTokenizer] = None
_load_attempted = False


def _load_model():
    global _model, _tokenizer, _load_attempted
    if _load_attempted:
        return _model, _tokenizer
    _load_attempted = True

    try:
        logger.info("Loading DistilBERT NLI model: %s", MODEL_ID)
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        m = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        m = m.to(device)
        m.training = False  # inference mode without using eval()
        _model = m
        logger.info("DistilBERT NLI model loaded on %s.", device)
    except Exception as exc:
        logger.error("Failed to load DistilBERT model: %s", exc)
        _model = None
        _tokenizer = None

    return _model, _tokenizer


def is_available() -> bool:
    model, _ = _load_model()
    return model is not None


# ── NLI inference helpers ──────────────────────────────────────────────────────

def _entailment_score(model, tokenizer, premise: str, hypothesis: str) -> float:
    """Return the entailment probability for (premise, hypothesis) pair."""
    device = next(model.parameters()).device
    inputs = tokenizer(
        premise,
        hypothesis,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        padding=True,
    ).to(device)
    with torch.no_grad():
        logits = model(**inputs).logits

    probs = torch.softmax(logits, dim=-1)[0]

    # Normalise label2id keys to uppercase to handle model variations
    label2id = {k.upper(): v for k, v in (model.config.label2id or {}).items()}
    entail_idx = label2id.get("ENTAILMENT", 2)

    return float(probs[entail_idx])


def _classify_doc_type(model, tokenizer, text: str) -> list[dict]:
    """Score text against each doc-type spec; return sorted by confidence desc."""
    results = []
    for spec in _DOC_TYPE_SPECS:
        score = _entailment_score(model, tokenizer, text, spec["hypothesis"])
        results.append({"label": spec["label"], "confidence": round(score, 4)})
    return sorted(results, key=lambda x: x["confidence"], reverse=True)


# ── Text splitting ─────────────────────────────────────────────────────────────

def _split_paragraphs(text: str, min_len: int = 60, max_len: int = 500) -> list[str]:
    """Split contract text into paragraph-sized chunks for clause analysis."""
    # Split on double-newlines, single newlines, or sentence-ending whitespace
    chunks = re.split(r"\n+|(?<=[.!?])\s{2,}", text)
    result = []
    for chunk in chunks:
        chunk = chunk.strip().replace("\n", " ")
        if len(chunk) < min_len:
            continue
        if len(chunk) > max_len:
            sentences = re.split(r"(?<=[.!?])\s+", chunk)
            current = ""
            for s in sentences:
                if len(current) + len(s) <= max_len:
                    current = (current + " " + s).strip()
                else:
                    if len(current) >= min_len:
                        result.append(current)
                    current = s
            if len(current) >= min_len:
                result.append(current)
        else:
            result.append(chunk)
    return result


# ── Public functions ───────────────────────────────────────────────────────────

def classify_document_type(text: str) -> dict:
    """
    Classify the document type using zero-shot NLI.

    Uses the first 800 characters — the preamble/header contains the most
    discriminative information for document type detection.

    Returns
    -------
    {"label": str, "confidence": float, "candidates": list[dict]}
    Null values when model unavailable.
    """
    model, tokenizer = _load_model()
    if model is None:
        return {"label": None, "confidence": None, "candidates": []}

    premise = text[:800].strip()
    candidates = _classify_doc_type(model, tokenizer, premise)

    top = candidates[0]

    # Keyword override: when NLI is uncertain, use multilingual keyword matching.
    # This prevents false positives like "employé annuellement" (French: "applied
    # annually") causing a lease agreement to be classified as employment contract.
    if top["confidence"] < _NLI_OVERRIDE_THRESHOLD:
        kw_label, kw_hits = _keyword_doc_type(text)
        if kw_label and kw_hits >= _KEYWORD_MIN_HITS:
            logger.info(
                "L2 doc type: NLI confidence %.2f < %.2f; keyword override → %s (%d hits)",
                top["confidence"], _NLI_OVERRIDE_THRESHOLD, kw_label, kw_hits,
            )
            top = {"label": kw_label, "confidence": round(kw_hits / 10.0, 2)}

    # If confidence is extremely low, treat the document type as unknown/None.
    if top["confidence"] < 0.15:
        top = {"label": None, "confidence": top["confidence"]}

    return {
        "label":      top["label"],
        "confidence": top["confidence"],
        "candidates": candidates[:4],
    }


def classify_clauses(text: str) -> list[dict]:
    """
    Scan each paragraph of text for abusive, leonine, payment-risk,
    or unclear clauses using zero-shot NLI.

    Only returns paragraphs where at least one label exceeds
    _CLAUSE_CONFIDENCE_THRESHOLD.

    Returns
    -------
    list of {"text": str, "label": str, "confidence": float}
    Empty list when model unavailable or no suspicious clauses found.
    """
    model, tokenizer = _load_model()
    if model is None:
        return []

    paragraphs = _split_paragraphs(text)
    paragraphs = paragraphs[:40]  # cap for CPU inference time

    flagged = []
    for para in paragraphs:
        best_label = None
        best_score = 0.0

        for spec in _CLAUSE_SPECS:
            # OR-logic: take the highest score across all hypotheses for this label
            for hyp in spec["hypotheses"]:
                score = _entailment_score(model, tokenizer, para, hyp)
                if score > best_score:
                    best_score = score
                    best_label = spec["label"]

        if best_score >= _CLAUSE_CONFIDENCE_THRESHOLD:
            flagged.append({
                "text":       para[:300],
                "label":      best_label,
                "confidence": round(best_score, 4),
            })

    return flagged


def _presence_hypothesis(clause_id: str, title: str) -> str:
    """Tuned hypothesis for a clause, or a humanized fallback from its title."""
    h = _CLAUSE_PRESENCE_HYPOTHESES.get(clause_id)
    if h:
        return h
    return f"This document contains provisions about {title.lower()}."


def semantic_clause_presence(
    text: str,
    clauses: list[tuple[str, str]],
    max_paragraphs: int = 25,
) -> dict[str, float]:
    """Semantic (NLI) presence check for clauses the keyword pass missed.

    For each (clause_id, title) in *clauses*, score the clause's presence
    hypothesis against the document's paragraphs and report it present when any
    paragraph's entailment exceeds _SEM_PRESENCE_THRESHOLD.  Reuses the already
    loaded DistilBERT NLI model (no new model, no Qwen) so it costs seconds, not
    minutes, and only runs on the handful of missing required clauses.

    Returns {clause_id: confidence} for semantically-present clauses only.
    Empty dict when the model is unavailable or *clauses* is empty.
    """
    model, tokenizer = _load_model()
    if model is None or not clauses:
        return {}

    paragraphs = _split_paragraphs(text)[:max_paragraphs]
    if not paragraphs:
        return {}

    found: dict[str, float] = {}
    for clause_id, title in clauses:
        hyp = _presence_hypothesis(clause_id, title)
        best = 0.0
        for para in paragraphs:
            score = _entailment_score(model, tokenizer, para, hyp)
            if score > best:
                best = score
            if best >= _SEM_PRESENCE_THRESHOLD:
                break  # early exit — one entailing paragraph is enough
        if best >= _SEM_PRESENCE_THRESHOLD:
            found[clause_id] = round(best, 4)

    if found:
        logger.info("L2 semantic presence recovered %d clause(s): %s",
                    len(found), ", ".join(found))
    return found


def layer2_analyze(text: str) -> dict:
    """
    Run all Layer 2 (DistilBERT NLI) checks on English text.

    Parameters
    ----------
    text : English contract text (translated upstream when needed)

    Returns
    -------
    dict with keys: document_type, flagged_clauses, layer2_available
    """
    available = is_available()

    if not available:
        logger.warning("Layer 2 unavailable: DistilBERT model not loaded.")
        return {
            "document_type":    {"label": None, "confidence": None, "candidates": []},
            "flagged_clauses":  [],
            "layer2_available": False,
        }

    doc_type = classify_document_type(text)
    flagged  = classify_clauses(text)

    logger.info(
        "Layer 2: doc_type=%s (%.2f) flagged_clauses=%d",
        doc_type["label"], doc_type["confidence"] or 0, len(flagged),
    )

    return {
        "document_type":    doc_type,
        "flagged_clauses":  flagged,
        "layer2_available": True,
    }
