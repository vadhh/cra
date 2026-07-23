"""Regression test: registry_v1.json classifier config must actually reach the
NLI hypothesis list and keyword fallback, not just sit unused in the JSON file.

Root cause this guards against: detector_distilbert.py had a dead
`load_doc_type_specs()`/`load_keyword_doc_types()` pair (sourced from an old,
unrelated ProfileManager) that `_classify_doc_type()` never called -- it read
the hardcoded 11-entry `_DOC_TYPE_SPECS` instead. That silently capped NLI
document-type classification at 11 of the registry's 56 profiles.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detector import profile_registry
from detector.detector_distilbert import (
    clear_classification_cache,
    load_doc_type_specs,
    load_keyword_doc_types,
    _keyword_doc_type,
)


def test_every_registry_profile_has_classifier_config():
    for pid in profile_registry.all_profile_ids():
        clf = profile_registry.classifier_for(pid)
        assert clf is not None, f"{pid} missing classifier block"
        assert clf["hypothesis"], f"{pid} missing hypothesis"
        assert clf["status"] in ("validated", "draft")


def test_doc_type_specs_cover_all_56_profiles_plus_non_contract():
    clear_classification_cache()
    specs = load_doc_type_specs()
    labels = {s["label"] for s in specs}
    assert len(specs) == 56 + 4  # registry profiles + invoice/receipt/purchase order/non-contract
    assert "distribution agreement" in labels  # a "partial" (draft) profile, not one of the original 11
    assert "government procurement contract" in labels


def test_keyword_fallback_matches_a_partial_profile():
    clear_classification_cache()
    text = (
        "DISTRIBUTION AGREEMENT\n\n"
        "This Distribution Agreement is entered into between Supplier and Distributor. "
        "The Distributor shall have the exclusive right to resell products within the assigned territory."
    )
    label, hits, _ = _keyword_doc_type(text)
    assert label == "distribution agreement"
    assert hits > 0


if __name__ == "__main__":
    test_every_registry_profile_has_classifier_config()
    test_doc_type_specs_cover_all_56_profiles_plus_non_contract()
    test_keyword_fallback_matches_a_partial_profile()
    print("PASS")
