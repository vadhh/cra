"""
sydeco_engine.py — Lightweight clause classifier using the Sydeco AI Core MLP.

Classifies contract clauses into three risk labels without requiring the Qwen LLM,
making it useful for testing and as a fast pre-screening layer on CPU-only hardware.

Labels
------
abusive_clause    — one-sided or unfair terms
payment_risk      — risky payment conditions
missing_mandatory — required clause appears absent

Usage
-----
    from sydeco_engine import classify_clauses, quick_risk_score

    tags  = classify_clauses(text)          # list of {clause, label}
    score = quick_risk_score(text)          # {score, label, clause_count, flagged}

Environment variables
---------------------
SYDECO_MLP_PATH   — override path to legal_mlp.pkl
                    (default: ~/Desktop/sydeco_ai_core_bundle/models/legal_mlp.pkl)
"""
from __future__ import annotations

import importlib.util
import logging
import os
import re
import sys
import types
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Model location ─────────────────────────────────────────────────────────────

_DEFAULT_MODEL_PATH = (
    Path.home() / "Desktop/sydeco_ai_core_bundle/models/legal_mlp.pkl"
)
MODEL_PATH = Path(os.getenv("SYDECO_MLP_PATH", str(_DEFAULT_MODEL_PATH)))

# ── Label & scoring constants ──────────────────────────────────────────────────

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

# ── Internal state ─────────────────────────────────────────────────────────────

_model = None
_load_attempted = False


# ── Dependency stubs ───────────────────────────────────────────────────────────

def _apply_stubs() -> None:
    """
    Pre-register stub modules in sys.modules so that the broken plugins inside
    ai_core_v2 (legal_transformer, legal_onnx) are never executed.

    - legal_transformer.py fails because the installed transformers version
      does not export Trainer / TrainingArguments via its trainer sub-module.
    - legal_onnx.py fails because onnxruntime is not installed.

    The MLP plugin (legal_text_mlp.py) only uses sklearn — no stubs needed there.
    """
    for name in (
        "ai_core_v2.plugins.legal_transformer",
        "ai_core_v2.plugins.legal_onnx",
        "onnxruntime",
    ):
        if name not in sys.modules:
            mod = types.ModuleType(name)
            mod.__spec__ = importlib.util.spec_from_loader(name, loader=None)
            sys.modules[name] = mod


# ── Model loader ───────────────────────────────────────────────────────────────

def _load_model():
    global _model, _load_attempted
    if _load_attempted:
        return _model
    _load_attempted = True

    if not MODEL_PATH.exists():
        logger.warning(
            "Sydeco MLP model not found at %s. "
            "Set SYDECO_MLP_PATH or place the file at the default location. "
            "Clause classifier disabled.",
            MODEL_PATH,
        )
        return None

    try:
        import pickle  # noqa: PLC0415 — local import after stubs are applied

        _apply_stubs()

        bundle_dir = str(MODEL_PATH.parent.parent)
        if bundle_dir not in sys.path:
            sys.path.insert(0, bundle_dir)

        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)  # nosec — loading user's own model file

        logger.info("Sydeco MLP loaded from %s.", MODEL_PATH)

    except Exception as exc:
        logger.error("Failed to load Sydeco MLP: %s", exc)

    return _model


# ── Rule-based fallback classifier ────────────────────────────────────────────
# Used when the MLP model file is unavailable.  Provides basic clause tagging
# so clause_tags is not always empty, even without legal_mlp.pkl.

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
    """Rule-based fallback: tag clauses matching known abusive/payment-risk patterns."""
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


# ── Text splitting ─────────────────────────────────────────────────────────────

def _split_clauses(text: str) -> list[str]:
    """Split contract text into clause-sized chunks suitable for classification."""
    chunks = re.split(r"(?<=[.!?])\s{1,3}(?=[A-Z0-9\(]|\Z)|\n{2,}", text)
    return [c.strip() for c in chunks if len(c.strip()) > 30]


# ── Public API ─────────────────────────────────────────────────────────────────

def is_available() -> bool:
    """Return True if the MLP model loaded successfully."""
    return _load_model() is not None


def classify_clauses(text: str) -> list[dict]:
    """
    Classify each clause extracted from *text*.

    Returns
    -------
    list of {"clause": str, "label": str}
    Empty list when the model is unavailable.
    """
    model = _load_model()
    clauses = _split_clauses(text)

    if model is None:
        # MLP unavailable — use rule-based fallback so clause_tags is never empty
        return _rule_classify_clauses(clauses)


    if not clauses:
        return []

    try:
        preds = model.predict(clauses)
        return [
            {"clause": clause, "label": LABEL_MAP.get(pred, str(pred))}
            for clause, pred in zip(clauses, preds)
            if LABEL_MAP.get(pred, str(pred)) != "normal"
        ]
    except Exception as exc:
        logger.error("Clause classification failed: %s", exc)
        return []


def quick_risk_score(text: str) -> dict | None:
    """
    Derive a rough risk score (0-100) from clause classifications.

    Returns
    -------
    {"score": int, "label": "LOW"|"MEDIUM"|"HIGH", "clause_count": int, "flagged": int}
    None when the model is unavailable.
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
