"""Self-check for exact offset evidence spans in L1 rules and keyword matching (CR-06)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detector_rules import check_clause_presence, detect_red_flags

# --- Test Clause Presence Spans ---
text_clause = "This document is governed by the laws of the Republic of Indonesia. The payment is net 30 days."

# Check governing_law (should trigger regex rule)
clauses = check_clause_presence(text_clause, jurisdiction="Indonesia")
gov_law = next(c for c in clauses if c["clause_id"] == "governing_law")
assert gov_law["present"] is True
assert gov_law["evidence_span"] is not None
span = gov_law["evidence_span"]
assert text_clause[span[0]:span[1]].lower() == "governed by"

# Check payment_terms (should trigger keyword fallback)
# Required keyword: "net 30" (matches "net 30 days" or similar)
pay_terms = next(c for c in clauses if c["clause_id"] == "payment_terms")
assert pay_terms["present"] is True
assert pay_terms["evidence_span"] is not None
span = pay_terms["evidence_span"]
assert text_clause[span[0]:span[1]].lower() == "net 30 days"


# --- Test Red Flag Spans ---
text_flag = "The supplier accepts unlimited liability for all losses without limit."

flags = detect_red_flags(text_flag)
# "unlimited liability" is a keyword_db dangerous clause
danger = next(f for f in flags if f["id"] == "kw_unlimited_liability")
assert danger["evidence_span"] is not None
span = danger["evidence_span"]
assert text_flag[span[0]:span[1]].lower() == "unlimited liability"

# Test regex red flag: "sole and absolute discretion without consent" (unilateral modification)
text_regex_flag = "We may modify this contract at any time without notice."
flags_regex = detect_red_flags(text_regex_flag)
unilateral = next(f for f in flags_regex if f["id"] == "unilateral_modification")
assert unilateral["evidence_span"] is not None
span = unilateral["evidence_span"]
assert text_regex_flag[span[0]:span[1]].lower() == "may modify this contract at any time"

print("test_evidence_spans OK")
