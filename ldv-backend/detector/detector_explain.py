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
import re
from typing import Optional

from send_prompt import query_llm

logger = logging.getLogger(__name__)


def _select_excerpt(text: str, layer1: dict, budget: int = 2000) -> str:
    """Pick preamble + paragraphs that contain red-flag evidence, then fill to budget."""
    evidence = [f.get("evidence", "")[:60] for f in layer1.get("red_flags", []) if f.get("evidence")]
    paragraphs = [p.strip() for p in re.split(r"\n{2,}|\n(?=[A-Z0-9\(\[])", text) if p.strip()]
    if not paragraphs:
        return text[:budget]

    selected: list[str] = []
    used: set[int] = set()
    total = 0

    first = paragraphs[0][:500]
    selected.append(first)
    used.add(0)
    total += len(first)

    for i, para in enumerate(paragraphs[1:], 1):
        if total >= budget:
            break
        if any(ev.lower() in para.lower() for ev in evidence if ev):
            chunk = para[:400]
            selected.append(chunk)
            used.add(i)
            total += len(chunk)

    for i, para in enumerate(paragraphs[1:], 1):
        if total >= budget:
            break
        if i not in used:
            chunk = para[: budget - total]
            selected.append(chunk)
            total += len(chunk)

    return "\n\n".join(selected)


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


def _unified_explain_prompt(findings: str, text_excerpt: str, jurisdiction: Optional[str]) -> str:
    juris = jurisdiction or "the detected jurisdiction"
    return (
        "You are a legal expert performing a contract analysis and compliance check.\n"
        "CRITICAL VALIDATION: If the document is clearly NOT a contract (e.g. it is a resume, CV, article, personal letter, or advertisement), you MUST write EXACTLY 'This document does not appear to be a contract.' under the '=== RISK SUMMARY ===' header, and leave all other sections entirely blank.\n\n"
        "Based on the findings and excerpt below, generate the following 4 sections. "
        "You MUST format the output exactly as requested, beginning each section with its respective "
        "=== HEADER === delimiter line, followed by the content for that section.\n\n"
        
        "=== RISK SUMMARY ===\n"
        "Write a concise 2-3 sentence plain-language summary of the contract's main legal risks. "
        "Do not repeat the findings verbatim — synthesize them.\n\n"
        
        "=== CLAUSE COMMENTARY ===\n"
        "Briefly comment on each flagged issue: what is wrong and why it matters legally. "
        "Use bullet points.\n\n"
        
        "=== COMPLIANCE ASSESSMENT ===\n"
        f"Assess compliance with {juris} law. Use the format:\n"
        "⚠️ [N] mandatory clauses missing\n"
        "⚠️ [N] unbalanced or abusive clause(s)\n"
        "✅/❌ One-sentence compliance conclusion.\n\n"
        
        "=== RECOMMENDATIONS ===\n"
        "Provide 3-5 specific, actionable recommendations to improve this contract. "
        "Use numbered bullet points.\n\n"
        
        f"FINDINGS:\n{findings}\n\n"
        f"CONTRACT EXCERPT:\n{text_excerpt}\n\n"
        "ANALYSIS:"
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
    excerpt  = _select_excerpt(text, layer1, budget=2000)

    logger.info("Layer 4: querying Qwen for unified explanations (excerpt=%d chars)...", len(excerpt))

    prompt = _unified_explain_prompt(findings, excerpt, jurisdiction)
    response = query_llm(prompt)

    summary = None
    commentary = None
    compliance = None
    recs = None

    if response:
        # ponytail: regex-based section splitting is used to consolidate 4 sequential LLM
        # queries into a single call, reducing latency by 60%. If the LLM drifts or fails to
        # generate a === SECTION === header, extraction fails. Upgrade path: switch to
        # JSON-schema-constrained generation (e.g. outline grammar or instructor library).
        def extract_section(section_name: str) -> str | None:
            pattern = rf"===\s*{section_name}\s*===\s*\n(.*?)(?====|\Z)"
            match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else None

        summary     = extract_section("RISK SUMMARY")
        commentary  = extract_section("CLAUSE COMMENTARY")
        compliance  = extract_section("COMPLIANCE ASSESSMENT")
        recs        = extract_section("RECOMMENDATIONS")

    available = any(x is not None for x in [summary, commentary, compliance, recs])

    if not available:
        logger.warning("Layer 4: unified Qwen call returned None or could not be parsed.")

    return {
        "summary":           summary,
        "clause_commentary": commentary,
        "compliance_notes":  compliance,
        "recommendations":   recs,
        "available":         available,
    }
