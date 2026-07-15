import unittest
from detector.detector_scorer import _compute_score

class TestScoringProfile(unittest.TestCase):

    def test_default_scoring_no_profile(self):
        # Features with missing mandatory clause but no matched profile
        features = {
            "missing_required": 1,
            "missing_mandatory_ids": ["notice_period"],
            "contract_type": "unknown",
            "matched_profile": False,
            "high_flags": 0,
            "medium_flags": 0,
            "unique_l2": 0,
            "unique_l2_items": [],
            "has_governing_law": True,
            "has_venue": True,
            "red_flags": []
        }
        policy = {
            "weights": {
                "missing_required_fallback": -10,
                "red_flag_high": -25,
                "red_flag_medium": -10,
                "l2_unique": -8,
                "no_governing_law": -12,
                "no_venue": -8,
                "impact_weights": {}
            }
        }
        
        # Expecting safety score of 90 (risk score 10)
        risk_score, breakdown = _compute_score(features, policy)
        self.assertEqual(risk_score, 10)
        self.assertEqual(len(breakdown), 1)
        self.assertEqual(breakdown[0]["points"], -10)

    def test_profile_specific_weights(self):
        # We test with employment_contract profile
        # First we simulate the scorer with customized features
        features = {
            "missing_required": 1,
            "missing_mandatory_ids": ["notice_period"],
            "contract_type": "employment contract",
            "matched_profile": True,
            "high_flags": 0,
            "medium_flags": 0,
            "unique_l2": 0,
            "unique_l2_items": [],
            "has_governing_law": True,
            "has_venue": True,
            "red_flags": [],
            "jurisdiction": "Indonesia"
        }
        
        policy = {
            "weights": {
                "missing_required_fallback": -10,
                "red_flag_high": -25,
                "red_flag_medium": -10,
                "l2_unique": -8,
                "no_governing_law": -12,
                "no_venue": -8,
                "impact_weights": {}
            }
        }
        
        # Run standard. Since no overrides are in employment_contract.json, it uses defaults.
        risk_score, breakdown = _compute_score(features, policy)
        self.assertEqual(risk_score, 10) # 100 - 10 = 90 safety, 10 risk

if __name__ == '__main__':
    unittest.main()
