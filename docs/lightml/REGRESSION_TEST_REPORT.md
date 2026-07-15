# CRA Regression Test Suite Report

This report documents the execution of the full automated regression test suite against the Contract Risk Analyzer (CRA) codebase.

---

## 1. Executive Summary
*   **Test Date**: 2026-07-14
*   **Total Tests Executed**: **20**
*   **Passed**: **20**
*   **Failed**: **0**
*   **Skipped**: **0**
*   **Execution Time**: **21.08 seconds**
*   **Overall Regression Status**: `🟢 100% PASSING`

---

## 2. Test Suite Categories and Results

| Test Category | File | Count | Passed | Failed | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Profile Validation** | `test_profile_validation_suite.py` | 7 | 7 | 0 | `🟢 PASS` |
| **Profile API Units** | `test_profiles_unit.py` | 11 | 11 | 0 | `🟢 PASS` |
| **Scoring Verification** | `test_scoring_profile.py` | 1 | 1 | 0 | `🟢 PASS` |
| **Evidence Span Mapping** | `test_evidence_spans.py` | 1 | 1 | 0 | `🟢 PASS` |

---

## 3. Findings & Resolution Details
*   **Test Suite Alignment**: Updated `test_profile_validation_suite.py` to correctly expect 15 registered profiles (reflecting the 4 new additions: SaaS, IT Service, Construction, and Insurance).
*   **Zero-Shot Templates Added**: Created mock positive/missing/dangerous text templates inside the test suite for the new profiles, resolving previous fallback score assertion mismatches.
*   **Raw Logs**: The complete raw stdout and stderr output is stored at [regression_test_raw.log](file:///mnt/c/Users/ADVAN/cra/docs/lightml/regression_test_raw.log).
