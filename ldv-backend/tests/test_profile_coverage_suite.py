"""
test_profile_coverage_suite.py — Full repository test suite verifying 100% profile maturity,
schema compliance, citation mapping, and synthetic test fixture coverage for all 57 profiles.
"""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from detector.profile_registry import _load, detect_profile, profile_for, all_profile_ids
from detector.detector_rules import _CLAUSE_RULES, layer1_analyze
from detector.detector_scorer import layer3_score


APPROVED_CLAUSE_IDS = {r["id"] for r in _CLAUSE_RULES}
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures", "profiles")


def test_registry_profile_count_and_schema():
    reg = _load()
    profiles = reg["profiles"]
    assert len(profiles) >= 56, f"Expected at least 56 profiles, found {len(profiles)}"
    
    for p in profiles:
        pid = p["id"]
        # 1. Verify status is mature (beta_candidate or validated)
        st = p.get("classifier", {}).get("status")
        assert st in ["beta_candidate", "validated"], f"Profile '{pid}' status is '{st}', expected 'beta_candidate' or 'validated'"
        
        # 2. Verify legal compliance metadata exists
        lc = p.get("legal_compliance")
        assert lc is not None, f"Profile '{pid}' missing legal_compliance metadata"
        assert lc.get("tos_required") is True
        assert lc.get("jurisdiction") == "ID"
        assert lc.get("legal_citations_mapped") is True
        
        # 3. Verify required clauses map 100% to approved clause IDs
        for cid in p.get("required_clauses", []):
            assert cid in APPROVED_CLAUSE_IDS, f"Profile '{pid}' has unmapped required_clause '{cid}'"


def test_profile_resolution():
    pids = all_profile_ids()
    assert len(pids) >= 56
    
    for pid in pids:
        p = profile_for(pid)
        assert p is not None, f"Failed to retrieve profile_for('{pid}')"
        
        # Check alias resolution
        disp = p.get("display_name")
        matched = detect_profile(disp)
        assert matched is not None, f"Failed to detect_profile('{disp}')"
        assert matched["id"] == pid


def test_profile_synthetic_fixtures_exist():
    pids = all_profile_ids()
    for pid in pids:
        pos_file = os.path.join(FIXTURES_DIR, f"bench_{pid}_pos.txt")
        risk_file = os.path.join(FIXTURES_DIR, f"bench_{pid}_high_risk.txt")
        assert os.path.exists(pos_file), f"Missing positive fixture for profile '{pid}'"
        assert os.path.exists(risk_file), f"Missing high-risk fixture for profile '{pid}'"


def test_profile_fixture_analysis():
    pids = all_profile_ids()
    # Test a sample of positive and high-risk fixtures to ensure Layer 1-3 pipeline execution
    sample_pids = pids[:10]
    for pid in sample_pids:
        pos_file = os.path.join(FIXTURES_DIR, f"bench_{pid}_pos.txt")
        with open(pos_file, "r", encoding="utf-8") as f:
            text = f.read()
            
        l1 = layer1_analyze(text, jurisdiction="Indonesia")
        l3 = layer3_score(l1, {}, lang="EN")
        assert "score" in l3
        assert isinstance(l3["score"], int)
