# Contract Risk Analyzer (CRA) — Profile Gap Report

This gap report evaluates the profile and data completeness of the Contract Risk Analyzer (CRA) compared to the historical Legal Document Verifier (LDV) knowledge base.

---

## 1. Profile Completeness Scores

Every contract profile registered in the system has been scored across six key data vectors:

| Profile ID | Required Clauses | Risk Rules | Recommendations | Business Impact | Legal Citations | Benchmark Fixtures | Overall Completeness |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **employment_contract** | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **lease_agreement** | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **non_disclosure_agreement** | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **service_agreement** | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **general_contract** | 100% | 100% | 100% | 100% | 100% | 100% | **100%** |
| **consulting_agreement** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |
| **commercial_agreement** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |
| **loan_agreement** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |
| **partnership_agreement** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |
| **purchase_agreement** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |
| **software_license** | 100% | 100% | 100% | 100% | 100% | 0% (Missing) | **83%** |

---

## 2. Identified Data Gaps

### 2.1. Missing Contract Profiles
*   **SaaS Agreement**: Referenced in `required_clauses_MASTER.csv` but lacks a dedicated JSON profile definition in `detector/profiles/`.
*   **IT Service Agreement**: Referenced in `required_clauses_MASTER.csv` but lacks a dedicated JSON profile.
*   **Construction Agreement**: Referenced in `required_clauses_MASTER.csv` but lacks a JSON profile.
*   **Insurance Agreement**: Referenced in `required_clauses_MASTER.csv` but lacks a JSON profile.

### 2.2. Unmapped Required Clauses (Orphans)
There are 14 contract-specific required clause IDs (such as `lease_term`, `rent_amount`, `security_deposit`, etc.) defined in `rules_classification.json` that do not map to Ilham's CSV `Clause_Name`s. They correctly fall back to default missing-clause weights, but they represent a minor data gap in terms of specific recommendations and business impacts.

### 2.3. Missing Benchmark Fixtures
The following 6 active profiles lack dedicated verification files in the test suite:
*   `consulting_agreement`
*   `commercial_agreement`
*   `loan_agreement`
*   `partnership_agreement`
*   `purchase_agreement`
*   `software_license`

---

## 3. Recommended Remediation Plan

1.  **Generate Missing Profiles**: Create `saas_agreement.json`, `it_service_agreement.json`, `construction_agreement.json`, and `insurance_agreement.json` to complete the catalog.
2.  **Verify Orphan Clauses**: Align the 14 unmapped clause IDs with Ilham's CSV database to ensure specific legal guidance matches when they are flagged.
3.  **Deploy Benchmark Files**: Provision 2 test files (PDF and DOCX) for each of the 6 missing-fixture profiles to ensure full integration coverage.
