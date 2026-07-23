# Gold Standard Validation Guide

**Role**: Legal-data and Content Owner (Ilham)  
**Repository**: Contract Risk Analyzer (CRA)  
**Document Version**: 4.0 (Repository Certification Finalized)  
**Target Audience**: Engineering Team, QA Automation Engineers, Legal Technology Auditors  

---

## Source of Truth

> [!IMPORTANT]
> **The Contract Profile Registry ([registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json)) is the sole legal source of truth for contract profiles.**
>
> - **Strict Repository Traceability**: Every attribute in the dataset must originate from repository evidence or be explicitly marked `Repository Evidence Not Available`.
> - **One Registry Profile = One Workbook Row**: The dataset contains **exactly 56 rows**, matching the 56 unique Contract Profiles in `registry_v1.json`.
> - **Validation Scenarios as Metadata**: Scenario details are stored strictly as metadata in the `Scenario Count` column and do **NOT** generate extra rows.
> - **Engineering Implementation Artifacts**: Files such as `construction_agreement.json`, `insurance_agreement.json`, `it_service_agreement.json`, and `saas_agreement.json` are engineering implementation artifacts only.

---

## 1. Purpose

The **Gold Standard Validation Dataset** ([GOLD_STANDARD_VALIDATION_DATASET.xlsx](file:///mnt/c/Users/ADVAN/cra/docs/GOLD_STANDARD_VALIDATION_DATASET.xlsx)) serves as the certified empirical benchmark for evaluating the **Contract Risk Analyzer (CRA)** engine against expected legal outcomes across all **56 Contract Profiles** defined in `registry_v1.json`.

---

## 2. Dataset Structure & 21 Attributes

The dataset workbook defines **21 standardized attributes** for every primary record:

1. **Validation ID**: Unique identifier (`VAL-001` through `VAL-056`).
2. **Registry Profile ID**: Authoritative ID from `registry_v1.json` (e.g., `employment_contract`).
3. **Canonical Profile Name**: Official display name from `registry_v1.json`.
4. **Contract Family**: Taxonomy grouping (`commercial_agreements`, `corporate_agreements`, `property_agreements`, `employment_agreements`, `baseline_agreements`).
5. **Languages**: Supported contract languages (`EN, ID`, etc.).
6. **Scenario Count**: Number of validation scenarios evaluated.
7. **Required Clauses**: Mandatory clauses required by `registry_v1.json`.
8. **Recommended Clauses**: Prescribed best-practice clauses or `Repository Evidence Not Available`.
9. **Dangerous Clauses**: Unfavorable or high-risk clauses or `Repository Evidence Not Available`.
10. **Abusive Clauses**: One-sided or coercive clause provisions or `Repository Evidence Not Available`.
11. **Illegal Clauses**: Direct statutory violations or `Repository Evidence Not Available`.
12. **Leonine Clauses**: Unbalanced rights/penalty distributions or `Repository Evidence Not Available`.
13. **Expected Risk**: Quantitative risk output (`High Risk`, `Medium Risk`, `Low Risk`).
14. **Expected Recommendation**: Mandatory remediation advice text.
15. **Expected Business Impact**: Commercial and operational risk description.
16. **Detection Specification**: Path to specification file or `Repository Evidence Not Available`.
17. **Evidence Source**: Path to legal evidence document or `Repository Evidence Not Available`.
18. **Engineering Status**: Active runtime implementation status.
19. **Reviewer Required**: Legal and engineering role assigned for sign-off.
20. **Repository Status**: `Complete (Beta Candidate)`, `Pending Engineering Sync`, or `Partial (Pending Legal Review)`.
21. **Repository Notes**: Descriptive lineage notes for the profile.

---

## 3. PASS / FAIL Criteria

### PASS Criteria
1. **Classification Accuracy**: Engine correctly identifies `Registry Profile ID` with confidence score >= 0.70.
2. **Missing Clause Recall**: 100% of required clauses in `Required Clauses` are flagged when absent.
3. **Risk Scoring Precision**: Engine risk output matches `Expected Risk`.
4. **Remediation Alignment**: Generated recommendation matches `Expected Recommendation`.

### FAIL Criteria
1. **Misclassification**: Engine assigns an incorrect profile ID or generic fallback when a specific profile exists.
2. **Undetected Mandatory Clause**: Engine fails to flag a missing clause defined in `registry_v1.json`.
3. **Risk Score Drift**: Actual risk score deviates by > 15 points from baseline expected score.
