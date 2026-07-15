import unittest
import os
import json
from detector.detector_profiles import validate_profile, ProfileValidationError, ProfileManager

class TestContractProfiles(unittest.TestCase):

    def test_valid_profile_validation(self):
        valid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "stable",
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family",
                "description": "Test description",
                "aliases": ["test alias"]
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis",
                "keyword_overrides": {
                    "EN": ["test"]
                }
            },
            "required_clauses": [
                {
                    "clause_id": "test_clause",
                    "severity_override": "HIGH",
                    "custom_report_wording": {
                        "EN": "Test wording"
                    }
                }
            ]
        }
        # Should not raise any exceptions
        try:
            validate_profile(valid_profile)
        except ProfileValidationError as exc:
            self.fail(f"validate_profile raised ProfileValidationError unexpectedly: {exc}")

    def test_invalid_profile_missing_root_key(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            # "validation_status" missing
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("Missing required root key: 'validation_status'", str(context.exception))

    def test_invalid_profile_wrong_type(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "stable",
            "review_date": "2026-07-13",
            "metadata": "not-a-dict", # invalid type
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("metadata must be a dictionary", str(context.exception))

    def test_invalid_profile_invalid_metadata(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "stable",
            "review_date": "2026-07-13",
            "metadata": {
                # "display_name" missing
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("metadata.display_name must be a non-empty string", str(context.exception))

    def test_profile_manager_registry(self):
        manager = ProfileManager()
        profiles = manager.list_profiles()
        self.assertIn("employment_contract", profiles)
        self.assertIn("lease_agreement", profiles)
        
        emp = manager.get_profile("employment_contract")
        self.assertEqual(emp["profile_id"], "employment_contract")
        self.assertEqual(emp["metadata"]["family"], "employment_agreements")
        
        # Test caching
        emp2 = manager.get_profile("employment_contract")
        self.assertIs(emp, emp2)

    def test_invalid_clause_rule_not_recognized(self):
        manager = ProfileManager()
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "stable",
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": [
                {
                    "clause_id": "non_existent_rule_id"
                }
            ]
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile, manager._rules)
        self.assertIn("clause_id 'non_existent_rule_id' is not a recognized rule in classification layer", str(context.exception))

    def test_invalid_version_format(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0",  # Invalid semver format
            "validation_status": "Validated",
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("version must follow semantic versioning format", str(context.exception))

    def test_invalid_review_date_format(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "Validated",
            "review_date": "2026/07/13",  # Invalid date format
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("review_date must follow ISO date format YYYY-MM-DD", str(context.exception))

    def test_invalid_validation_status(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "UnknownStatus",  # Invalid state
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("must be one of: Validated, Beta, Preparation, Archived, Custom", str(context.exception))

    def test_invalid_language(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "Validated",
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["XX"],  # Invalid language code
                "jurisdictions": ["generic"]
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("Invalid language 'XX'", str(context.exception))

    def test_invalid_jurisdiction(self):
        invalid_profile = {
            "profile_id": "test_profile",
            "version": "1.0.0",
            "validation_status": "Validated",
            "review_date": "2026-07-13",
            "metadata": {
                "display_name": "Test Profile",
                "family": "test_family"
            },
            "coverage": {
                "languages": ["EN"],
                "jurisdictions": ["invalid_jur"]  # Invalid jurisdiction
            },
            "classification": {
                "nli_hypothesis": "Test hypothesis"
            },
            "required_clauses": []
        }
        with self.assertRaises(ProfileValidationError) as context:
            validate_profile(invalid_profile)
        self.assertIn("Invalid jurisdiction 'invalid_jur'", str(context.exception))

if __name__ == '__main__':
    unittest.main()

