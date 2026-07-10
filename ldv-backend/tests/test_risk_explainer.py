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
