# Explain Mode (Per-Risk Structured Explanations) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Every detected risk in the `/analyze` response (each L1 red flag, and each missing required clause) carries an inline `explanation` object with: what was detected, why it's a risk, severity, suggested correction, confidence score, and a source paragraph/text reference.

**Architecture:** A new, fast, deterministic module (`detector/risk_explainer.py`) assembles the 6 fields entirely from data L1/L3 already compute plus two small static guidance tables — no ML calls, so it runs on every `/analyze` request (no `?explain=1` gate, unlike the existing slow Qwen narrative mode in `detector_explain.py`, which is untouched and stays opt-in). It follows the exact pattern `citation_db.annotate_layer1()` already established: mutate `layer1["red_flags"]`/`layer1["clause_presence"]` in place, attaching a new key per finding.

**Tech Stack:** Python 3, existing `detector/clause_db.py` and `detector/detector_rules.py` modules, existing lawyer-authored CSVs in `datasets/`. No new dependencies.

## Global Constraints

- No ML/LLM calls — must stay fast enough to run unconditionally (not gated behind `?explain=1`).
- Additive only: existing `red_flags[]` / `clause_presence[]` dict shapes must keep every current key; only new keys are added. `tests/test_evidence_spans.py` and `tests/run_full_validation.py` must keep passing unmodified.
- Only clauses that are `required` and NOT `present` get an explanation (a present clause is not a risk). All `red_flags` entries get one (every red flag is by definition a risk).
- Reuse existing lawyer-authored guidance data (`clause_db.clause_guidance()`, and the `Reason`/`Recommendation` columns already present in the keyword-risk CSVs) before inventing new text. New static text is only for the ~13 hand-written regex red-flag rules, which have no CSV backing.

---

### Task 1: Surface the `reason` column that `risk_clause_db.py` already parses but drops

**Files:**
- Modify: `ldv-backend/detector/risk_clause_db.py:76-101` (the `_load()` row parser and entry dict), `ldv-backend/detector/risk_clause_db.py:159-166` (the `detect_keyword_flags()` output dict), `ldv-backend/detector/risk_clause_db.py:145` (self-check `__main__` block)
- Test: self-check inside `ldv-backend/detector/risk_clause_db.py`'s own `if __name__ == "__main__":` block (this module has no separate pytest file — it self-tests, matching existing convention)

**Interfaces:**
- Produces: `detect_keyword_flags(text, exclude_ids=())` finding dicts now also carry `"reason": str` (previously only `"recommendation"` was surfaced, even though the CSV's `Reason` column — index 7 — was being read into `row[7]` and silently discarded).

**Called by:** `ldv-backend/detector/detector_rules.py:838` (`detect_red_flags` calls `detect_keyword_flags` as its second pass).

- [ ] **Step 1: Run the self-check to confirm today's baseline (no `reason` field)**

Run: `cd ldv-backend && python3 detector/risk_clause_db.py`
Expected output ends with `overlap suppression OK` (current behavior — `reason` doesn't exist yet, so there's nothing to fail on until Step 2 adds the assertion).

- [ ] **Step 2: Add the failing assertion to the self-check**

In `ldv-backend/detector/risk_clause_db.py`, inside `if __name__ == "__main__":`, directly after the existing line `assert "evidence_span" in f, "evidence_span missing in finding"`, add:

```python
    assert f.get("reason"), "reason missing in finding (CSV col 7 parsed but not surfaced)"
```

- [ ] **Step 3: Run it and confirm it fails**

Run: `cd ldv-backend && python3 detector/risk_clause_db.py`
Expected: `AssertionError: reason missing in finding (CSV col 7 parsed but not surfaced)`

- [ ] **Step 4: Capture `reason` in `_load()`**

In `ldv-backend/detector/risk_clause_db.py`, replace:

```python
                    risk, impact, recommend = _to_int(row[5]), row[6].strip(), row[8].strip()
                    if not clause_name or not phrases:
                        continue
                    e = db.get(clause_name)
                    if e is None:
                        db[clause_name] = {
                            "id": _slug(clause_name), "clause_name": clause_name,
                            "category": category, "risk_score": risk,
                            "impact_level": impact, "recommendation": recommend,
                            "phrases": list(dict.fromkeys(phrases)),
                        }
                    else:
                        for p in phrases:
                            if p not in e["phrases"]:
                                e["phrases"].append(p)
                        if risk > e["risk_score"]:
                            e.update(risk_score=risk, impact_level=impact,
                                     recommendation=recommend, category=category)
```

with:

```python
                    risk, impact = _to_int(row[5]), row[6].strip()
                    reason, recommend = row[7].strip(), row[8].strip()
                    if not clause_name or not phrases:
                        continue
                    e = db.get(clause_name)
                    if e is None:
                        db[clause_name] = {
                            "id": _slug(clause_name), "clause_name": clause_name,
                            "category": category, "risk_score": risk,
                            "impact_level": impact, "reason": reason,
                            "recommendation": recommend,
                            "phrases": list(dict.fromkeys(phrases)),
                        }
                    else:
                        for p in phrases:
                            if p not in e["phrases"]:
                                e["phrases"].append(p)
                        if risk > e["risk_score"]:
                            e.update(risk_score=risk, impact_level=impact, reason=reason,
                                     recommendation=recommend, category=category)
```

- [ ] **Step 5: Surface it in `detect_keyword_flags()`'s output**

In `ldv-backend/detector/risk_clause_db.py`, in the `out.append({...})` block inside `detect_keyword_flags()`, add a `"reason"` line next to the existing `"recommendation"` line:

```python
        out.append({
            "id":           entry["id"],
            "type":         entry["category"].lower(),
            "severity":     _SEVERITY.get(entry["impact_level"].lower(), "MEDIUM"),
            "description":  f"{entry['category']}: {entry['clause_name']}",
            "evidence":     text[start:end].strip().replace("\n", " "),
            "evidence_span": [match_start, match_end],
            "impact_level": entry["impact_level"],
            "reason":       entry["reason"],
            "recommendation": entry["recommendation"],
            "source":       "keyword_db",
        })
```

- [ ] **Step 6: Run the self-check again and confirm it passes**

Run: `cd ldv-backend && python3 detector/risk_clause_db.py`
Expected: ends with `overlap suppression OK` (no AssertionError this time).

- [ ] **Step 7: Run the existing evidence-span regression test to confirm nothing broke**

Run: `cd ldv-backend && python3 tests/test_evidence_spans.py`
Expected: no output / no traceback (bare-assert script; silent success means pass).

- [ ] **Step 8: Commit**

```bash
git add ldv-backend/detector/risk_clause_db.py
git commit -m "feat: surface reason field already parsed from risky-clause CSVs"
```

---

### Task 2: Build `risk_explainer.py` — the core per-finding explanation module

**Files:**
- Create: `ldv-backend/detector/risk_explainer.py`
- Test: Create `ldv-backend/tests/test_risk_explainer.py`

**Interfaces:**
- Consumes: `detector.detector_rules.layer1_analyze(text, jurisdiction) -> dict` (existing, returns `{governing_law, venue, clause_presence, red_flags, layer1_score}`), `detector.detector_rules.required_clauses_for(doc_type) -> list[str]` (existing), `detector.clause_db.clause_guidance(clause_id, lang="EN") -> dict | None` (existing, returns `{impact_level, reason, recommendation, business_impact, ...}` or `None`), `detector.clause_db.clause_impact(clause_id) -> str` (existing, returns `"CRITICAL"|"HIGH"|"MEDIUM"|"LOW"|""`)
- Produces: `explain_findings(layer1: dict, jurisdiction: str | None, doc_type_label: str | None) -> None` — mutates `layer1` in place, attaching `flag["explanation"]` to every entry in `layer1["red_flags"]` and `entry["explanation"]` to every entry in `layer1["clause_presence"]` where `required` is true and `present` is false. Each `explanation` dict has exactly these keys: `clause` (str), `reason` (str), `severity` (str), `suggested_correction` (str), `confidence` (float 0-1), `source_reference` (`{"text": str | None, "span": [int, int] | None}`).

**Called by:** Task 3 wires this into `ldv-backend/app.py:257` (`_run_analysis`).

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_risk_explainer.py`:

```python
"""Self-check for per-finding structured Explain Mode annotations (risk_explainer.py)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detector_rules import layer1_analyze
from detector.risk_explainer import explain_findings

text = (
    "This agreement is governed by the laws of France. "
    "The supplier accepts unlimited liability for all losses without limit. "
    "Payment is due within 3 days of invoice."
)

layer1 = layer1_analyze(text, jurisdiction="France")
explain_findings(layer1, jurisdiction="France", doc_type_label="service agreement")

# --- Red flag explanation: all 6 required fields present ---
flags_with_explanation = [f for f in layer1["red_flags"] if "explanation" in f]
assert flags_with_explanation, "expected at least one red flag to carry an explanation"
exp = flags_with_explanation[0]["explanation"]
for field in ("clause", "reason", "severity", "suggested_correction", "confidence", "source_reference"):
    assert field in exp, f"missing field: {field}"
assert isinstance(exp["confidence"], float) and 0 <= exp["confidence"] <= 1
assert exp["source_reference"]["span"] is not None

# --- Missing required clause also gets an explanation ---
missing = [c for c in layer1["clause_presence"] if c.get("required") and not c.get("present")]
assert missing, "expected at least one missing required clause in this fixture"
assert "explanation" in missing[0], "missing required clause should carry an explanation"
miss_exp = missing[0]["explanation"]
assert miss_exp["severity"] in ("CRITICAL", "HIGH", "MEDIUM", "LOW")
assert miss_exp["source_reference"] == {"text": None, "span": None}

# --- Present clauses are NOT annotated (only risks get explanations) ---
present = [c for c in layer1["clause_presence"] if c.get("present")]
assert present, "expected at least one present clause in this fixture"
assert "explanation" not in present[0], "present clauses are not risks; should not be annotated"

print("test_risk_explainer OK")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ldv-backend && python3 tests/test_risk_explainer.py`
Expected: `ModuleNotFoundError: No module named 'detector.risk_explainer'`

- [ ] **Step 3: Write `risk_explainer.py`**

Create `ldv-backend/detector/risk_explainer.py`:

```python
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
_RED_FLAG_GUIDANCE: dict[str, dict[str, str]] = {
    "leonine_profit": {
        "reason": "Allocating all profits to a single party breaches the principle of mutual benefit and can render the agreement void as a leonine clause under most civil-law systems.",
        "recommendation": "Redraft to allocate profit and loss proportionally to each party's contribution or ownership share.",
    },
    "leonine_no_loss": {
        "reason": "A leonine clause that shields one party from any loss undermines the shared-risk nature of the agreement and is frequently unenforceable.",
        "recommendation": "Ensure both parties share proportional exposure to losses, or justify the asymmetry with clear, separately-negotiated consideration.",
    },
    "excessive_penalty": {
        "reason": "A penalty rate this high functions as a punitive damages clause rather than a genuine pre-estimate of loss, and courts in many jurisdictions will reduce or strike it.",
        "recommendation": "Cap the penalty at a rate proportionate to reasonably foreseeable loss (commonly 1-2% per day, with an overall cap).",
    },
    "rights_waiver": {
        "reason": "A blanket waiver of all legal rights is overly broad, may be unenforceable against mandatory consumer or employment protections, and leaves the waiving party without recourse.",
        "recommendation": "Limit the waiver to specific, named rights and confirm it does not override non-waivable statutory protections.",
    },
    "unilateral_modification": {
        "reason": "Letting one party amend the agreement at will, without the other's consent, removes the mutuality required for a binding contract and exposes the other party to unpredictable terms.",
        "recommendation": "Require written agreement from both parties, or at minimum advance notice with a right to terminate, for any amendment.",
    },
    "total_liability_exclusion": {
        "reason": "Excluding all liability regardless of cause typically fails against gross negligence, willful misconduct, or statutory protections, and signals a serious imbalance of risk.",
        "recommendation": "Replace with a liability cap tied to contract value and carve out gross negligence, willful misconduct, and statutory liabilities.",
    },
    "auto_renewal_no_notice": {
        "reason": "Automatic renewal with little or no notice traps the counterparty into a new term before they can reasonably evaluate the relationship, and violates consumer-protection notice requirements in several jurisdictions.",
        "recommendation": "Require at least 30 days' written notice before renewal and an easy opt-out mechanism.",
    },
    "short_payment_window_high": {
        "reason": "A payment window this short (days or hours) gives the paying party little room to process invoices and creates disproportionate default/penalty risk for routine delays.",
        "recommendation": "Extend the payment window to a commercially standard term (e.g. net 30) or add a reasonable cure period before penalties apply.",
    },
    "short_payment_window_medium": {
        "reason": "An 8-14 day payment window is tighter than standard commercial terms and can create cash-flow strain and inadvertent default risk.",
        "recommendation": "Consider extending to net 30 unless a shorter cycle is specifically justified by the transaction type.",
    },
    "customer_pays_vendor_errors": {
        "reason": "Shifting the cost of the vendor's own mistakes onto the customer removes the vendor's incentive for quality control and is an unusual departure from standard risk allocation.",
        "recommendation": "Require the vendor to bear the cost of correcting its own errors or defects at no charge to the customer.",
    },
    "fee_for_dispute": {
        "reason": "Charging a fee merely to raise a complaint or dispute discourages legitimate claims and may be viewed as an unfair barrier to access to justice.",
        "recommendation": "Remove the fee; disputes should be raised without a financial barrier to entry.",
    },
    "no_liability_intentional": {
        "reason": "Excluding liability for intentional or grossly negligent conduct is void as against public policy in most legal systems -- a party cannot contract out of liability for its own bad faith.",
        "recommendation": "Remove the exclusion for intentional breach and gross negligence; liability limits should apply only to ordinary negligence.",
    },
    "illegal_object": {
        "reason": "The contract references activity that is criminal or otherwise illegal; an agreement with an illegal object is void and unenforceable in its entirety.",
        "recommendation": "Remove the illegal subject matter immediately and have counsel review whether the remainder of the contract is severable.",
    },
}


def _explain_red_flag(flag: dict) -> dict:
    guidance = _RED_FLAG_GUIDANCE.get(flag["id"], {})
    reason = flag.get("reason") or guidance.get("reason") or (
        f"This text matched a known risky-clause pattern ({flag.get('type', 'unspecified')})."
    )
    recommendation = flag.get("recommendation") or guidance.get("recommendation") or (
        "Have this clause reviewed and revised by counsel before signing."
    )
    return {
        "clause": flag.get("description") or flag.get("id"),
        "reason": reason,
        "severity": flag.get("severity", "MEDIUM"),
        "suggested_correction": recommendation,
        "confidence": _SOURCE_CONFIDENCE.get(flag.get("source"), 0.75),
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
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ldv-backend && python3 tests/test_risk_explainer.py`
Expected: `test_risk_explainer OK`

- [ ] **Step 5: Commit**

```bash
git add ldv-backend/detector/risk_explainer.py ldv-backend/tests/test_risk_explainer.py
git commit -m "feat: add risk_explainer for per-finding Explain Mode annotations"
```

---

### Task 3: Wire `explain_findings` into the `/analyze` pipeline

**Files:**
- Modify: `ldv-backend/app.py:21` (imports), `ldv-backend/app.py:257` (`_run_analysis`)
- Modify: `CLAUDE.md` ("Other modules" list) to document the new module

**Interfaces:**
- Consumes: `detector.risk_explainer.explain_findings(layer1, jurisdiction, doc_type_label) -> None` (Task 2)

- [ ] **Step 1: Add the import**

In `ldv-backend/app.py`, next to the existing citation import at line 21, add:

```python
from detector.citation_db import annotate_layer1
from detector.risk_explainer import explain_findings
```

- [ ] **Step 2: Call it after semantic backfill, before scoring**

In `ldv-backend/app.py`, in `_run_analysis`, change:

```python
    _semantic_backfill(layer1, doc_type_label, analysis_text)

    layer3 = layer3_score(layer1, layer2, lang=lang, policy_name=policy_name)
```

to:

```python
    _semantic_backfill(layer1, doc_type_label, analysis_text)
    explain_findings(layer1, jurisdiction, doc_type_label)

    layer3 = layer3_score(layer1, layer2, lang=lang, policy_name=policy_name)
```

(Placed after `_semantic_backfill` so clauses recovered by semantic NLI are correctly excluded from "missing" explanations. Not called in the earlier non-contract-document early return at `app.py:239-255` -- L3 clause-risk scoring is already skipped for those document types, so per-clause risk explanation is out of scope there too.)

- [ ] **Step 3: Manual smoke test against a running server**

Run: `cd ldv-backend && FLASK_APP=app.py python3 -m flask run --port 5000 &`
Then: `curl -s -X POST http://127.0.0.1:5000/analyze -F "file=@tests/fixtures/<any_existing_fixture>.txt" | python3 -m json.tool | grep -A6 '"explanation"'`
Expected: at least one `"explanation": {...}` block with `clause`, `reason`, `severity`, `suggested_correction`, `confidence`, `source_reference` keys visible in the output.

- [ ] **Step 4: Run the full regression suite**

Run: `cd ldv-backend && python3 tests/run_validation.py`
Expected: same pass count as before this change (this task is additive-only; no existing assertions reference `explanation`, so none should newly fail).

- [ ] **Step 5: Document the new module in CLAUDE.md**

In `/home/stardhoom/LDV/CLAUDE.md`, in the "### Other modules" bullet list, add a new bullet (matching the existing style of `citation_db.py`'s entry) documenting `risk_explainer.py`: its purpose (fast, deterministic per-finding Explain Mode), the 6 fields it attaches, and that it's wired in `_run_analysis` right after `_semantic_backfill`.

- [ ] **Step 6: Commit**

```bash
git add ldv-backend/app.py CLAUDE.md
git commit -m "feat: wire risk_explainer into the analyze pipeline"
```

---

## Self-Review Notes

- **Spec coverage:** (1) clause/missing-clause detected -> `explanation.clause`. (2) why it's a risk -> `explanation.reason`. (3) severity -> `explanation.severity`. (4) suggested correction -> `explanation.suggested_correction`. (5) confidence score -> `explanation.confidence`. (6) source paragraph/text reference -> `explanation.source_reference`. All 6 covered by Task 2/3.
- **Scope limitation, called out explicitly:** the non-contract-document early-return path in `_run_analysis` does not get explanations, since L3 (and therefore "required clause" semantics) doesn't run there either -- consistent with existing behavior, not a gap introduced by this plan.
