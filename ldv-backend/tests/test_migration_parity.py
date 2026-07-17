"""Regression test: the 11 originally-mature profiles must stay in sync between
the legacy per-file registry (detector_profiles.py / detector/profiles/*.json,
still live in detector_scorer.py._compute_score() for weight/jurisdiction
overrides and in app.py's admin profile-management API) and the new
registry-driven system (profile_registry.py / registry_v1.json, used for
required-clause resolution and classifier config since P2).

This is the "migration parity" item from the 2026-07-16 management review:
"Demonstrate migration parity between the legacy code and the registry-driven
scorer through profile-by-profile regression testing." Two things can drift
independently now that both systems run side by side:

  1. required_clauses -- the legal-risk-critical mandatory clause set per
     profile. A silent drop/change here means a required clause stops being
     enforced without anyone noticing.
  2. resolve_profile_by_name() -- detector_scorer.py looks up the legacy
     profile by the *label the new system produces* (normalized document_type,
     which follows the new registry's display_name convention) to apply any
     custom scoring.weights / jurisdiction_adjustments. If the legacy alias
     list doesn't recognize that label, overrides silently stop applying
     (caught by a bare except in _compute_score(), so it fails silently, not
     loudly). Currently a no-op for all 11 profiles (none have a scoring
     block configured yet) but still a latent trap for whenever one is added.

Both checks found real drift on the first run: required_clauses matched
everywhere, but software_license's legacy aliases didn't include "software
license agreement", the exact label the new registry's display_name produces
(fixed alongside this test).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detector_profiles import ProfileManager
from detector import profile_registry

# The 11 profiles present in both the legacy registry and the new registry's
# "validated" tier -- the ones the 2026-07-16 review calls "already mature".
ORIGINAL_11 = [
    "employment_contract", "lease_agreement", "software_license",
    "service_agreement", "consulting_agreement", "commercial_agreement",
    "non_disclosure_agreement", "loan_agreement", "partnership_agreement",
    "purchase_agreement", "general_contract",
]


def test_original_11_present_in_both_systems():
    legacy_ids = set(ProfileManager()._registry.get("profiles", {}).keys())
    new_ids = set(profile_registry.all_profile_ids())
    missing_legacy = [pid for pid in ORIGINAL_11 if pid not in legacy_ids]
    missing_new = [pid for pid in ORIGINAL_11 if pid not in new_ids]
    assert not missing_legacy, f"missing from legacy profiles.json: {missing_legacy}"
    assert not missing_new, f"missing from registry_v1.json: {missing_new}"


def test_required_clauses_match_between_legacy_and_registry():
    manager = ProfileManager()
    mismatches = {}
    for pid in ORIGINAL_11:
        legacy = manager.get_profile(pid)
        legacy_clauses = {c["clause_id"] for c in (legacy.get("required_clauses") or [])}
        new_clauses = set(profile_registry.profile_for(pid).get("required_clauses") or [])
        if legacy_clauses != new_clauses:
            mismatches[pid] = {
                "legacy_only": sorted(legacy_clauses - new_clauses),
                "registry_only": sorted(new_clauses - legacy_clauses),
            }
    assert not mismatches, (
        "required_clauses drifted between legacy and registry-driven systems "
        f"for: {mismatches}"
    )


def test_legacy_weight_override_lookup_resolves_for_registry_labels():
    """detector_scorer._compute_score() calls resolve_profile_by_name(ctype)
    where ctype is the normalized document_type label the *new* registry-driven
    classifier now produces. If the legacy alias list hasn't kept up, weight/
    jurisdiction overrides silently stop applying (bare except in the scorer)."""
    manager = ProfileManager()
    unresolved = []
    for pid in ORIGINAL_11:
        label = profile_registry.profile_for(pid)["display_name"].lower()
        if manager.resolve_profile_by_name(label) is None:
            unresolved.append((pid, label))
    assert not unresolved, (
        "legacy ProfileManager.resolve_profile_by_name() doesn't recognize the "
        f"label the new registry produces for: {unresolved} -- add that label "
        "to the legacy profile's metadata.aliases"
    )


if __name__ == "__main__":
    test_original_11_present_in_both_systems()
    test_required_clauses_match_between_legacy_and_registry()
    test_legacy_weight_override_lookup_resolves_for_registry_labels()
    print("All migration parity checks passed.")
