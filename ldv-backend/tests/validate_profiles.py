"""
validate_profiles.py — Machine validation: every clause ID in the profile
registry resolves to an approved clause ID in detector_rules._CLAUSE_RULES.

Run: python tests/validate_profiles.py
Exit 0 = all OK. Exit 1 = unmapped entries found.

ponytail: simple set diff; no framework needed.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from detector.detector_rules import _CLAUSE_RULES  # noqa: E402
from detector.profile_registry import _load  # noqa: E402

APPROVED_IDS = {r["id"] for r in _CLAUSE_RULES}
data = _load()
errors: list[str] = []

for profile in data["profiles"]:
    for cid in profile["required_clauses"]:
        if cid not in APPROVED_IDS:
            errors.append(
                f"Profile '{profile['id']}': unknown clause_id '{cid}'"
            )

# also check baseline
for cid in data["baseline_required"]:
    if cid not in APPROVED_IDS:
        errors.append(f"baseline_required: unknown clause_id '{cid}'")

if errors:
    print(f"VALIDATION FAILED — {len(errors)} unmapped clause reference(s):")
    for e in errors:
        print(f"  • {e}")
    sys.exit(1)

print(
    f"validate_profiles OK — {len(data['profiles'])} profiles, "
    f"{len(APPROVED_IDS)} approved clause IDs, 0 unmapped references."
)
