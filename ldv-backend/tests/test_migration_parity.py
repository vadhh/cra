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

  3. NLI hypothesis parity -- P2 ("make classifier config registry-driven")
     migrated the 11 profiles' hand-tuned NLI hypotheses out of the hardcoded
     `_DOC_TYPE_SPECS` list in detector_distilbert.py and into registry_v1.json.
     This is the ground truth that actually drove classification before P2 --
     a wording change here is the single highest-risk thing that could have
     silently degraded doc-type classification accuracy for the 11 already-
     trusted profiles. Checked byte-for-byte: no drift found.
  4. Keyword-detection path is untouched for the 11 -- _keyword_doc_type()'s
     hardcoded if/elif chain (not `load_keyword_doc_types()`) still drives
     keyword-based classification for these profiles; the registry's
     `positive_keywords` only feed an *additive* fallback for profiles outside
     the original 11, so this test just confirms that division of labor
     rather than diffing pattern lists (different keyword *sources* by design,
     not drift).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector.detector_profiles import ProfileManager
from detector.detector_distilbert import _DOC_TYPE_SPECS, _keyword_doc_type
from detector import profile_registry

# Maps each of the 11 profile ids to the label _DOC_TYPE_SPECS used for it
# pre-P2 (detector_distilbert.py's hardcoded hypothesis list). Not always the
# same string as the new registry's display_name.lower() -- e.g. software
# license's legacy label is "software license", the registry's is "software
# license agreement" (see test_dual_label_still_resolves_same_profile below).
PID_TO_LEGACY_LABEL = {
    "employment_contract": "employment contract",
    "lease_agreement": "lease agreement",
    "software_license": "software license",
    "service_agreement": "service agreement",
    "consulting_agreement": "consulting agreement",
    "commercial_agreement": "commercial agreement",
    "non_disclosure_agreement": "non-disclosure agreement",
    "loan_agreement": "loan agreement",
    "partnership_agreement": "partnership agreement",
    "purchase_agreement": "purchase agreement",
    "general_contract": "general contract",
}

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


def test_nli_hypothesis_matches_pre_migration_hardcoded_spec():
    """The single highest-risk change P2 could have made: silently altering
    the hand-tuned NLI hypothesis wording for an already-trusted profile,
    degrading classification accuracy without any structural signal (no
    missing field, no exception -- just a worse prompt). Diffed byte-for-byte
    against the pre-P2 ground truth (_DOC_TYPE_SPECS, kept in the file as the
    static fallback)."""
    legacy_hyp = {s["label"]: s["hypothesis"] for s in _DOC_TYPE_SPECS}
    mismatches = {}
    for pid, legacy_label in PID_TO_LEGACY_LABEL.items():
        old_hyp = legacy_hyp.get(legacy_label)
        new_hyp = (profile_registry.profile_for(pid).get("classifier") or {}).get("hypothesis")
        if old_hyp != new_hyp:
            mismatches[pid] = {"legacy": old_hyp, "registry": new_hyp}
    assert not mismatches, f"NLI hypothesis drifted from pre-P2 baseline for: {mismatches}"


def test_keyword_chain_untouched_for_original_11():
    """P2's commit message claims _keyword_doc_type()'s hardcoded chain for
    the 11 tuned profiles was left untouched (registry keywords only feed an
    *additive* fallback for profiles outside the 11). Spot-check with real
    trigger phrases for two profiles known to have hardcoded keyword checks
    (software_license, lease_agreement) -- confirms the chain still returns
    its original label, not a registry-fallback label, i.e. the hardcoded
    branch is still being hit first."""
    label, hits, is_override = _keyword_doc_type("This EULA grants a software license to licensee.")
    assert label == "software license", f"expected hardcoded chain label, got {label!r}"

    label, hits, is_override = _keyword_doc_type("The landlord and tenant agree to this lease for the premises.")
    assert label == "lease agreement", f"expected hardcoded chain label, got {label!r}"


def test_dual_label_still_resolves_same_profile():
    """software_license is the one profile where the keyword path's label
    ("software license") and the registry/NLI path's label ("software license
    agreement") diverge -- confirmed non-breaking because detect_profile()
    resolves both to the same profile (both are in registry_v1.json's own
    aliases list)."""
    from detector import profile_registry as reg
    keyword_path = reg.detect_profile("software license")
    nli_path = reg.detect_profile("software license agreement")
    assert keyword_path is not None and nli_path is not None
    assert keyword_path["id"] == nli_path["id"] == "software_license"


if __name__ == "__main__":
    test_original_11_present_in_both_systems()
    test_required_clauses_match_between_legacy_and_registry()
    test_legacy_weight_override_lookup_resolves_for_registry_labels()
    test_nli_hypothesis_matches_pre_migration_hardcoded_spec()
    test_keyword_chain_untouched_for_original_11()
    test_dual_label_still_resolves_same_profile()
    print("All migration parity checks passed.")
