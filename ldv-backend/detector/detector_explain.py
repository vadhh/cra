"""
detector_explain.py — Layer 4: Qwen-powered legal explanation engine.

Takes structured findings from Layers 1, 2, and 3 as context and uses the
local Qwen LLM to generate:
  - A plain-language summary of the contract's main risks
  - Per-clause explanations for each flagged issue
  - A legal compliance assessment
  - Actionable recommendations

By passing structured context (not raw contract text), the LLM prompt is
focused and produces higher quality output than sending 1500 chars of raw
text.

Public API
----------
    from detector.detector_explain import layer4_explain

    result = layer4_explain(
        text,
        jurisdiction="Belgium",
        layer1=layer1_result,
        layer2=layer2_result,
        layer3=layer3_result,
    )

Returns
-------
dict:
    summary            : str | None  — overall plain-language risk summary
    clause_commentary  : str | None  — per-clause analysis (CBC-style)
    compliance_notes   : str | None  — legal compliance assessment
    recommendations    : str | None  — actionable advice
    available          : bool        — False when Qwen not loaded
"""
from __future__ import annotations

import logging
from typing import Optional

from send_prompt import query_llm

logger = logging.getLogger(__name__)


# ── Context builders ───────────────────────────────────────────────────────────

def _build_findings_summary(
    jurisdiction: Optional[str],
    layer1: dict,
    layer2: dict,
    layer3: dict,
) -> str:
    """Serialize L1/L2/L3 findings into a concise text block for the LLM prompt."""
    lines = []

    # Jurisdiction & governing law
    gov_law = layer1.get("governing_law")
    venue   = layer1.get("venue")
    lines.append(f"Jurisdiction detected: {jurisdiction or 'Unknown'}")
    lines.append(f"Governing law clause: {gov_law or 'NOT FOUND'}")
    lines.append(f"Venue clause: {venue or 'NOT FOUND'}")

    # Risk score
    score = layer3.get("score")
    label = layer3.get("label")
    lines.append(f"Risk score: {score}/100 ({label})")

    # Missing required clauses
    missing = layer3.get("features", {}).get("missing_required", 0)
    missing_ids = layer1.get("layer1_score", {}).get("missing_required", [])
    if missing_ids:
        lines.append(f"Missing required clauses ({missing}): {', '.join(missing_ids)}")
    else:
        lines.append("Missing required clauses: none")

    # L1 red flags
    red_flags = layer1.get("red_flags", [])
    if red_flags:
        lines.append(f"Rule-based red flags ({len(red_flags)}):")
        for f in red_flags:
            lines.append(f"  [{f['severity']}] {f['description']}: \"{f['evidence'][:120]}\"")
    else:
        lines.append("Rule-based red flags: none")

    # L2 flagged clauses
    flagged = layer2.get("flagged_clauses", [])
    if flagged:
        lines.append(f"DistilBERT flagged clauses ({len(flagged)}):")
        for c in flagged:
            lines.append(f"  [{c['label']} {c['confidence']:.0%}]: \"{c['text'][:120]}\"")
    else:
        lines.append("DistilBERT flagged clauses: none")

    # Doc type (L2)
    doc_type_l2 = layer2.get("document_type", {}).get("label")
    if doc_type_l2:
        lines.append(f"Document type (detected): {doc_type_l2}")

    return "\n".join(lines)


# ── Prompt templates ───────────────────────────────────────────────────────────

def _summary_prompt(findings: str, text_excerpt: str) -> str:
    return (
        "You are a legal expert. Based on the findings below, write a concise 2-3 sentence "
        "plain-language summary of the contract's main legal risks. "
        "Do not repeat the findings verbatim — synthesise them.\n\n"
        f"FINDINGS:\n{findings}\n\n"
        f"CONTRACT EXCERPT:\n{text_excerpt[:600]}\n\n"
        "RISK SUMMARY:"
    )


def _commentary_prompt(findings: str, text_excerpt: str) -> str:
    return (
        "You are a legal expert performing a clause-by-clause review. "
        "Based on the findings below, briefly comment on each flagged issue: "
        "what is wrong and why it matters legally. Use bullet points.\n\n"
        f"FINDINGS:\n{findings}\n\n"
        f"CONTRACT EXCERPT:\n{text_excerpt[:800]}\n\n"
        "CLAUSE COMMENTARY:"
    )


def _compliance_prompt(findings: str, jurisdiction: Optional[str]) -> str:
    juris = jurisdiction or "the detected jurisdiction"
    return (
        f"You are a legal compliance expert specialising in {juris} law. "
        "Based on the findings below, assess whether this contract complies with "
        f"the legal requirements of {juris}. "
        "Use the format:\n"
        "⚠️ [N] mandatory clauses missing\n"
        "⚠️ [N] unbalanced or abusive clause(s)\n"
        "✅/❌ One-sentence compliance conclusion.\n\n"
        f"FINDINGS:\n{findings}\n\n"
        "COMPLIANCE ASSESSMENT:"
    )


def _recommendations_prompt(findings: str) -> str:
    return (
        "You are a legal advisor. Based on the findings below, "
        "provide 3-5 specific, actionable recommendations to improve this contract. "
        "Use numbered bullet points.\n\n"
        f"FINDINGS:\n{findings}\n\n"
        "RECOMMENDATIONS:"
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def layer4_explain(
    text: str,
    jurisdiction: Optional[str] = None,
    layer1: Optional[dict] = None,
    layer2: Optional[dict] = None,
    layer3: Optional[dict] = None,
) -> dict:
    """
    Generate LLM-powered explanations for the structured findings.

    Returns gracefully with available=False when Qwen is not loaded.

    Parameters
    ----------
    text         : English contract text (first portion used as excerpt)
    jurisdiction : detected jurisdiction string
    layer1       : result of layer1_analyze()
    layer2       : result of layer2_analyze()
    layer3       : result of layer3_score()
    """
    layer1 = layer1 or {}
    layer2 = layer2 or {}
    layer3 = layer3 or {}

    findings = _build_findings_summary(jurisdiction, layer1, layer2, layer3)
    excerpt  = text[:1000]

    logger.info("Layer 4: querying Qwen for explanations...")

    summary     = query_llm(_summary_prompt(findings, excerpt))
    commentary  = query_llm(_commentary_prompt(findings, excerpt))
    compliance  = query_llm(_compliance_prompt(findings, jurisdiction))
    recs        = query_llm(_recommendations_prompt(findings))

    available = any(x is not None for x in [summary, commentary, compliance, recs])

    if not available:
        logger.warning("Layer 4: all Qwen calls returned None — model not loaded.")

    return {
        "summary":           summary,
        "clause_commentary": commentary,
        "compliance_notes":  compliance,
        "recommendations":   recs,
        "available":         available,
    }
