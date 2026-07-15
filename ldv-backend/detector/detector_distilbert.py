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
    document_type    : {"label": str, "confidence": float, "candidates": list, "source": str}
                        source is "classifier" (ML) or "user_selected" (app.py override_type)
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

# Enforce offline mode if downloads not allowed
if _os.getenv("LDV_DOWNLOAD_MODELS", "0") != "1":
    _os.environ["HF_HUB_OFFLINE"] = "1"
    _os.environ["TRANSFORMERS_OFFLINE"] = "1"

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

# Minimum keyword hits to trust a keyword result over NLI
_KEYWORD_MIN_HITS = 2
# NLI confidence below this → apply keyword override when keyword is strong
_NLI_OVERRIDE_THRESHOLD = 0.85

_STATIC_KEYWORD_DOC_TYPES: dict[str, list[str]] = {
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
    "non-contract": [
        r"\bcurriculum\s+vitae\b", r"\bcv\b", r"\bresume\b",
        r"\beducation\b", r"\bwork\s+experience\b", r"\bskills\b",
        r"\bprofessional\s+summary\b", r"\bpersonal\s+details\b",
        r"\bexperience\s+summary\b",
    ],
}


<<<<<<< HEAD
_STATIC_DOC_TYPE_SPECS: list[dict] = [
=======

def _keyword_doc_type(text: str) -> tuple[str | None, int]:
    """Return (best_label, hit_count) from keyword matching on text[:1200].

    hit_count sums occurrences across all of a label's patterns, not just how
    many distinct patterns matched at least once. Categories with few
    surface-form synonyms (e.g. "non-disclosure agreement" has 6 patterns
    spanning 4 languages, vs. 17 for "lease agreement") would otherwise be
    structurally capped near _KEYWORD_MIN_HITS even when one strong,
    repeated term is the only signal to survive translation.
    """
    snippet = text[:1200]
    scores: dict[str, int] = {}
    for label, patterns in _KEYWORD_DOC_TYPES.items():
        count = sum(len(re.findall(p, snippet, re.I)) for p in patterns)
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
>>>>>>> 9852ba59887b6bbb8a65259bf6932e756a5d8352
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
    {
        "label":      "non-contract",
        "hypothesis": "This document is a resume, curriculum vitae (CV), article, advertisement, letter, or other non-contract text.",
    },
]

_CACHED_DOC_TYPE_SPECS: Optional[list[dict]] = None
_CACHED_KEYWORD_DOC_TYPES: Optional[dict[str, list[str]]] = None


def clear_classification_cache() -> None:
    """Clear cached document type specs and keyword overrides."""
    global _CACHED_DOC_TYPE_SPECS, _CACHED_KEYWORD_DOC_TYPES
    _CACHED_DOC_TYPE_SPECS = None
    _CACHED_KEYWORD_DOC_TYPES = None


def load_doc_type_specs() -> list[dict]:
    global _CACHED_DOC_TYPE_SPECS
    if _CACHED_DOC_TYPE_SPECS is not None:
        return _CACHED_DOC_TYPE_SPECS
    
    try:
        from detector.detector_profiles import ProfileManager
        manager = ProfileManager()
        specs = []
        for pid in manager.list_profiles():
            p = manager.get_profile(pid)
            label = p["metadata"]["display_name"].lower()
            specs.append({
                "label": label,
                "hypothesis": p["classification"]["nli_hypothesis"]
            })
        
        # Append non-contract specs that aren't in the registry
        for spec in _STATIC_DOC_TYPE_SPECS:
            if spec["label"] in ["invoice", "receipt", "purchase order", "non-contract"]:
                specs.append(spec)
                
        _CACHED_DOC_TYPE_SPECS = specs
        return _CACHED_DOC_TYPE_SPECS
    except Exception as e:
        logger.warning("Failed to load doc type specs dynamically, falling back to static: %s", e)
        return _STATIC_DOC_TYPE_SPECS


def load_keyword_doc_types() -> dict[str, list[str]]:
    global _CACHED_KEYWORD_DOC_TYPES
    if _CACHED_KEYWORD_DOC_TYPES is not None:
        return _CACHED_KEYWORD_DOC_TYPES
    
    try:
        from detector.detector_profiles import ProfileManager
        manager = ProfileManager()
        kw_types = {}
        for pid in manager.list_profiles():
            p = manager.get_profile(pid)
            label = p["metadata"]["display_name"].lower()
            patterns = []
            ko = p["classification"].get("keyword_overrides", {})
            for lang, words in ko.items():
                for word in words:
                    escaped_word = re.escape(word)
                    pattern = escaped_word.replace(r"\ ", r"\s+").replace(" ", r"\s+")
                    patterns.append(rf"\b{pattern}\b")
            kw_types[label] = patterns

            
        # Append non-contract types
        for k in ["invoice", "receipt", "purchase order", "non-contract"]:
            kw_types[k] = _STATIC_KEYWORD_DOC_TYPES[k]
            
        _CACHED_KEYWORD_DOC_TYPES = kw_types
        return _CACHED_KEYWORD_DOC_TYPES
    except Exception as e:
        logger.warning("Failed to load keyword doc types dynamically, falling back to static: %s", e)
        return _STATIC_KEYWORD_DOC_TYPES


def _has_word(word: str, text: str) -> bool:
    pattern = r'\b' + re.escape(word).replace(r'\ ', r'\s+').replace(' ', r'\s+') + r'\b'
    return re.search(pattern, text, re.I) is not None

def _keyword_doc_type(text: str) -> tuple[str | None, int, bool]:
    """Return (best_label, hit_count, is_title_match) from highly specific keyword matching on text[:1200]."""
    # Extract the first 3 lines of the text for title-matching
    lines = [line.strip().lower() for line in text.split('\n') if line.strip()][:3]
    header = " ".join(lines)
    
    # 1. Header/Title Matching (Precedence based on explicit title terms)
    if any(x in header for x in ["saas", "software as a service"]):
        return "saas agreement", 5, True
    if any(x in header for x in ["it service", "it support", "information technology"]):
        return "it service agreement", 5, True
    if any(x in header for x in ["construction"]):
        return "construction agreement", 5, True
    if any(x in header for x in ["insurance"]):
        return "insurance agreement", 5, True
    if any(x in header for x in ["consulting", "consultant"]):
        return "consulting agreement", 5, True
    if any(x in header for x in ["partnership", "kemitraan"]):
        return "partnership agreement", 5, True
    if any(x in header for x in ["non-disclosure", "confidentiality", "nda", "kerahasiaan"]):
        return "non-disclosure agreement", 5, True
    if any(x in header for x in ["loan", "lender", "borrower", "pinjaman"]):
        return "loan agreement", 5, True
    if any(x in header for x in ["employment", "employee", "employer", "pekerjaan", "pekerja", "pemberi kerja", "perjanjian kerja"]):
        return "employment contract", 5, True
    if any(x in header for x in ["lease", "rental", "sewa", "bail"]):
        return "lease agreement", 5, True
    if any(x in header for x in ["software license", "lisensi", "eula"]):
        return "software license", 5, True
    if any(x in header for x in ["purchase agreement", "purchase of", "pembelian"]):
        return "purchase agreement", 5, True
    if any(x in header for x in ["commercial agreement", "commercial contract", "commercial b2b", "business agreement", "commercial"]):
        return "commercial agreement", 5, True
    if any(x in header for x in ["master services", "general contract", "general agreement", "long agreement"]):
        return "general contract", 5, True
    if any(x in header for x in ["service agreement", "services agreement", "prestation de service"]):
        return "service agreement", 5, True
    if any(x in header for x in ["invoice", "faktur"]):
        return "invoice", 5, True
    if any(x in header for x in ["receipt", "kwitansi", "reçu"]):
        return "receipt", 5, True
    if any(x in header for x in ["purchase order"]):
        return "purchase order", 5, True

    # 2. Body Snippet Matching
    snippet = text[:1200].lower()
    
    if any(_has_word(x, snippet) for x in ["saas", "software as a service"]):
        return "saas agreement", 5, False
    if any(_has_word(x, snippet) for x in ["it service", "it support", "information technology services"]):
        return "it service agreement", 5, False
    if any(_has_word(x, snippet) for x in ["construction", "building contract"]):
        return "construction agreement", 5, False
    if any(_has_word(x, snippet) for x in ["insurance policy", "insurer"]):
        return "insurance agreement", 5, False
    if any(_has_word(x, snippet) for x in ["software license", "licensor", "licensee", "eula"]):
        return "software license", 5, False
        
    if any(_has_word(x, snippet) for x in ["non-disclosure", "confidentiality", "nda"]):
        # Verify it's not a generic contract mentioning NDA
        if "master services" not in snippet and "services agreement" not in snippet:
            return "non-disclosure agreement", 5, False
        
    if any(_has_word(x, snippet) for x in ["loan", "lender", "borrower"]):
        return "loan agreement", 5, False
        
    if any(_has_word(x, snippet) for x in ["employee", "employer", "employment", "pekerja", "pemberi kerja", "perjanjian kerja"]):
        return "employment contract", 5, False
        
    if any(_has_word(x, snippet) for x in ["lease", "tenant", "landlord", "rent", "sewa", "bail"]):
        return "lease agreement", 5, False
        
    if any(_has_word(x, snippet) for x in ["partnership", "partner"]):
        if "non-disclosure" not in snippet and "confidentiality" not in snippet:
            return "partnership agreement", 5, False
            
    if any(_has_word(x, snippet) for x in ["purchase", "seller", "buyer", "goods"]):
        return "purchase agreement", 5, False
        
    if any(_has_word(x, snippet) for x in ["commercial agreement", "commercial contract", "business agreement"]):
        return "commercial agreement", 5, False
        
    if any(_has_word(x, snippet) for x in ["services", "provider", "client", "jasa"]):
        if any(_has_word(x, snippet) for x in ["consulting", "consultant", "advisory"]):
            return "consulting agreement", 5, False
        return "service agreement", 5, False
        
    return "general contract", 2, False


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

_CLAUSE_PRESENCE_HYPOTHESES: dict[str, str | list[str]] = {
    "governing_law":           "The agreement is governed by the laws of a particular place.",
    # Two hypotheses (OR-logic, same pattern as _DOC_TYPE_SPECS/clause
    # classification below): DistilBERT-MNLI is brittle across paraphrases of
    # this concept, and the single old phrasing ("Disputes will be handled by
    # a specific court or location.") both missed real venue clauses *and*
    # scored 0.97+ on unrelated short sentences (e.g. a bare "Between X and Y"
    # parties line, or a mistranslated property-inspection clause). These two
    # together cover real venue-clause phrasings while scoring <0.01 on both
    # false-positive premises found in the FR lease fixture.
    "jurisdiction_venue": [
        "This agreement specifies which court will hear any legal dispute.",
        "Legal proceedings between the parties will be exclusively conducted in a named court.",
    ],
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
    # Reworded from "One party is responsible for maintenance and repairs." —
    # the old phrasing scored 0.99 against a mistranslated property-inspection
    # sentence ("an adversarial record will be drawn up"); this phrasing keeps
    # the same true-positive score (0.996) but drops that false positive to 0.01.
    "maintenance_responsibility": "The landlord or tenant must pay for or arrange repairs and upkeep of the property.",
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
        download_allowed = _os.getenv("LDV_DOWNLOAD_MODELS", "0") == "1"
        local_files_only = not download_allowed
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, local_files_only=local_files_only)
        m = AutoModelForSequenceClassification.from_pretrained(MODEL_ID, local_files_only=local_files_only)
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

def _batch_entailment_scores(model, tokenizer, pairs: list[tuple[str, str]], batch_size: int = 16) -> list[float]:
    """Compute entailment probabilities for a list of (premise, hypothesis) pairs in batches."""
    if not pairs:
        return []

    device = next(model.parameters()).device
    # Normalise label2id keys to uppercase to handle model variations
    label2id = {k.upper(): v for k, v in (model.config.label2id or {}).items()}
    entail_idx = label2id.get("ENTAILMENT", 2)

    # ponytail: batch size is set to 16 by default to balance CPU/GPU memory footprint and parallel speedups.
    # Ceiling: large batch sizes (>64) on CPU or low-VRAM GPUs can cause memory congestion.
    # Upgrade: dynamically adjust batch size based on execution environment.
    env_batch = _os.getenv("LDV_NLI_BATCH_SIZE")
    if env_batch:
        try:
            batch_size = int(env_batch)
        except ValueError:
            pass

    scores = []
    for i in range(0, len(pairs), batch_size):
        batch = pairs[i:i + batch_size]
        premises = [p for p, _ in batch]
        hypotheses = [h for _, h in batch]

        try:
            inputs = tokenizer(
                premises,
                hypotheses,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            ).to(device)
            with torch.no_grad():
                logits = model(**inputs).logits

            probs = torch.softmax(logits, dim=-1)
            for j in range(len(batch)):
                scores.append(float(probs[j][entail_idx]))
        except Exception as e:
            logger.warning("Batch entailment score failed for range %d-%d: %s — falling back to sequential", i, i + len(batch), e)
            # Fail-soft: sequential fallback for the failed batch
            for premise, hypothesis in batch:
                try:
                    inputs = tokenizer(
                        premise,
                        hypothesis,
                        return_tensors="pt",
                        truncation=True,
                        max_length=512,
                        padding=True,
                    ).to(device)
                    with torch.no_grad():
                        lgt = model(**inputs).logits
                    prb = torch.softmax(lgt, dim=-1)[0]
                    scores.append(float(prb[entail_idx]))
                except Exception as ex:
                    logger.warning("Sequential fallback entailment score failed: %s", ex)
                    scores.append(0.0)

    return scores


def _entailment_score(model, tokenizer, premise: str, hypothesis: str) -> float:
    """Return the entailment probability for (premise, hypothesis) pair."""
    return _batch_entailment_scores(model, tokenizer, [(premise, hypothesis)])[0]


def _classify_doc_type(model, tokenizer, text: str) -> list[dict]:
    """Score text against each doc-type spec; return sorted by confidence desc."""
    pairs = [(text, spec["hypothesis"]) for spec in _DOC_TYPE_SPECS]
    scores = _batch_entailment_scores(model, tokenizer, pairs)

    results = []
<<<<<<< HEAD
    for spec in load_doc_type_specs():
        score = _entailment_score(model, tokenizer, text, spec["hypothesis"])
=======
    for spec, score in zip(_DOC_TYPE_SPECS, scores):
>>>>>>> 9852ba59887b6bbb8a65259bf6932e756a5d8352
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
    {"label": str, "confidence": float, "candidates": list[dict], "source": str, ...}
    Null values when model unavailable. "source" is always "classifier" here;
    app.py overrides it to "user_selected" when the user picks the document
    type manually, so consumers can tell a real ML confidence from a
    user override in the audit trail.
    """
    model, tokenizer = _load_model()
    if model is None:
        return {
            "label": None,
            "confidence": None,
            "model_confidence": None,
            "keyword_override_confidence": None,
            "override_applied": False,
            "override_reason": None,
            "source": "classifier",
            "candidates": []
        }

    premise = text[:800].strip()
    candidates = _classify_doc_type(model, tokenizer, premise)

    top = candidates[0]
    
    # Store initial model state
    model_conf = float(top["confidence"])
    final_label = top["label"]
    final_conf = model_conf
    
    keyword_override_conf = 0.0
    override_applied = False
    override_reason = None
    source = "classifier"

    # Keyword override: when NLI is uncertain, use multilingual keyword matching.
    kw_label, kw_hits, is_title_match = _keyword_doc_type(text)
    
    if kw_label:
        is_generic_nli = top["label"] in ["service agreement", "general contract"]
        is_specific_kw = kw_label not in ["service agreement", "general contract"]
        
        # Override conditions:
        # 1. Ground truth title matched explicitly
        # 2. NLI confidence is below threshold
        # 3. NLI output is generic (e.g. services) but keywords found a highly specific subtype (e.g. saas, IT service)
        if is_title_match or top["confidence"] < _NLI_OVERRIDE_THRESHOLD or (is_generic_nli and is_specific_kw):
            override_applied = True
            source = "keyword_override"
            keyword_override_conf = 0.85
            final_label = kw_label
            final_conf = 0.85
            
            if is_title_match:
                override_reason = "title_match"
            elif is_generic_nli and is_specific_kw:
                override_reason = "generic_to_specific"
            else:
                override_reason = "keyword_match"
                
            logger.info(
                "L2 doc type override: selected '%s' (NLI was '%s' %.4f, reason=%s)",
                kw_label, top["label"], model_conf, override_reason,
            )

    # If confidence is extremely low, treat the document type as unknown/None.
    if final_conf < 0.15:
        final_label = None

    return {
        "label":                      final_label,
        "confidence":                 final_conf,
        "model_confidence":           model_conf,
        "keyword_override_confidence": keyword_override_conf,
        "override_applied":           override_applied,
        "override_reason":            override_reason,
        "source":                     source,
        "candidates":                 candidates[:4],
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

    pairs = []
    task_mapping = []  # tracks (para_idx, spec_label) for each pair

    for para_idx, para in enumerate(paragraphs):
        for spec in _CLAUSE_SPECS:
            # OR-logic: take the highest score across all hypotheses for this label
            for hyp in spec["hypotheses"]:
                pairs.append((para, hyp))
                task_mapping.append((para_idx, spec["label"]))

    if not pairs:
        return []

    scores = _batch_entailment_scores(model, tokenizer, pairs)

    # Resolve the highest score per paragraph
    para_best = {i: (None, 0.0) for i in range(len(paragraphs))}
    for (para_idx, label), score in zip(task_mapping, scores):
        if score > para_best[para_idx][1]:
            para_best[para_idx] = (label, score)

    flagged = []
    for para_idx, para in enumerate(paragraphs):
        best_label, best_score = para_best[para_idx]
        if best_score >= _CLAUSE_CONFIDENCE_THRESHOLD:
            flagged.append({
                "text":       para[:300],
                "label":      best_label,
                "confidence": round(best_score, 4),
            })

    return flagged


def _presence_hypotheses(clause_id: str, title: str) -> list[str]:
    """Tuned hypothesis/hypotheses for a clause, or a humanized fallback."""
    h = _CLAUSE_PRESENCE_HYPOTHESES.get(clause_id)
    if not h:
        return [f"This document contains provisions about {title.lower()}."]
    return h if isinstance(h, list) else [h]


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

    pairs = []
    task_mapping = []  # tracks (clause_id, para_idx) for each pair

    for clause_id, title in clauses:
        hyps = _presence_hypotheses(clause_id, title)
        for para_idx, para in enumerate(paragraphs):
            for hyp in hyps:
                pairs.append((para, hyp))
                task_mapping.append((clause_id, para_idx))

    if not pairs:
        return {}

    scores = _batch_entailment_scores(model, tokenizer, pairs)

    # Resolve the highest score per clause
    clause_best = {clause_id: 0.0 for clause_id, _ in clauses}
    for (clause_id, _), score in zip(task_mapping, scores):
        if score > clause_best[clause_id]:
            clause_best[clause_id] = score

    found: dict[str, float] = {}
    for clause_id, _ in clauses:
        best_score = clause_best[clause_id]
        if best_score >= _SEM_PRESENCE_THRESHOLD:
            found[clause_id] = round(best_score, 4)

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
            "document_type":    {"label": None, "confidence": None, "candidates": [], "source": "classifier"},
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
