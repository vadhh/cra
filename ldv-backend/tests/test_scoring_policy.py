"""Self-check for Layer 3 scoring policy versioning and confidence (CR-03)."""
import os
import sys
import tempfile
import json

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from detector.detector_scorer import load_scoring_policy, layer3_score

def test_scoring_policy_flow():
    # 1. Verify default policy loading
    policy = load_scoring_policy("default_v1")
    assert policy["version"] == "default_v1"
    assert policy["calibration_status"] == "provisional_uncalibrated"
    assert "limitation_notice" in policy

    # 2. Verify fallback policy loading on missing policy
    fallback = load_scoring_policy("non_existent_policy")
    assert fallback["version"] == "fallback_v1"
    assert fallback["calibration_status"] == "provisional_uncalibrated"

    # 3. Create a temporary custom scoring policy file to test weights override
    custom_policy_content = {
        "version": "custom_v99",
        "calibration_status": "calibrated",
        "limitation_notice": "Custom limitation notice.",
        "weights": {
            "missing_required_fallback": -5,
            "impact_weights": {
                "CRITICAL": -5,
                "HIGH": -5,
                "MEDIUM": -5,
                "LOW": -5
            },
            "red_flag_high": -50,
            "red_flag_medium": -50,
            "l2_unique": -50,
            "no_governing_law": -50,
            "no_venue": -50
        }
    }

    policies_dir = os.path.join(os.path.dirname(HERE), "detector", "policies")
    os.makedirs(policies_dir, exist_ok=True)
    custom_policy_path = os.path.join(policies_dir, "custom_v99.json")
    
    with open(custom_policy_path, "w", encoding="utf-8") as f:
        json.dump(custom_policy_content, f)

    try:
        # Load the custom policy
        custom_policy = load_scoring_policy("custom_v99")
        assert custom_policy["version"] == "custom_v99"
        assert custom_policy["calibration_status"] == "calibrated"

        # Mock inputs to layer3_score
        layer1_mock = {
            "red_flags": [
                {"id": "excessive_penalty", "severity": "HIGH", "evidence": "must pay 1000% fee"}
            ],
            "clause_presence": [
                {"clause_id": "governing_law", "title": "Governing Law", "present": False, "required": True},
                {"clause_id": "jurisdiction_venue", "title": "Jurisdiction", "present": False, "required": True},
                {"clause_id": "payment_terms", "title": "Payment Terms", "present": True, "required": True},
                {"clause_id": "termination", "title": "Termination", "present": True, "required": True},
                {"clause_id": "dispute_resolution", "title": "Dispute Resolution", "present": True, "required": True},
                {"clause_id": "limitation_liability", "title": "Limitation of Liability", "present": True, "required": True}
            ]
        }
        layer2_mock = {
            "layer2_available": True,
            "document_type": {"label": "NDA", "confidence": 0.95},
            "flagged_clauses": []
        }

        # Under custom_v99 policy, deductions should be:
        # - red_flag_high: -50
        # - no_governing_law: -50
        # - no_venue: -50
        # Total deductions: -150 -> score: max(0, 100 - 150) = 0 -> risk_score = 100 - 0 = 100
        res_custom = layer3_score(layer1_mock, layer2_mock, policy_name="custom_v99")
        assert res_custom["score"] == 100
        assert res_custom["policy_version"] == "custom_v99"
        assert res_custom["calibration_status"] == "calibrated"
        assert res_custom["limitation_notice"] == "Custom limitation notice."
        assert res_custom["confidence"] == 95.0

        # Under default_v1 policy, deductions should be:
        # - red_flag_high: -25
        # - no_governing_law: -12
        # - no_venue: -8
        # Total deductions: -45 -> score: 100 - 45 = 55 -> risk_score = 100 - 55 = 45
        res_default = layer3_score(layer1_mock, layer2_mock, policy_name="default_v1")
        print("BREAKDOWN:", res_default["breakdown"], "SCORE:", res_default["score"])
        assert res_default["score"] == 45
        assert res_default["policy_version"] == "default_v1"
        assert res_default["calibration_status"] == "provisional_uncalibrated"
        assert res_default["confidence"] == 95.0

    finally:
        if os.path.exists(custom_policy_path):
            os.remove(custom_policy_path)

if __name__ == "__main__":
    test_scoring_policy_flow()
    print("test_scoring_policy OK")
