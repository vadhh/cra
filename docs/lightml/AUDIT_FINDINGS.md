# Contract Risk Analyzer (CRA) — Legal Engineering Internal Audit Report

> [!IMPORTANT]
> **Audit Standards:** This audit follows strict guidelines regarding legal sign-off. Compliance or approval is never assumed. If no physical signed evidence exists in the repository, the status is reported as **Evidence Not Found**.

## 1. Executive Summary
- **Total Registered Profiles**: 56
- **Technically Mature Profiles**: 11 (19.6%)
- **Partially Usable Profiles**: 45 (80.4%)
- **Detection Specifications coverage**: 42/56 (75.0%)
- **Contract Corpus coverage**: 56/56 (100.0%)

## 2. Classified Audit Findings

### [MAJOR] Active Profiles Missing Detection Specifications
- **Classification**: Major
- **Description**: Active implemented profiles under `profiles.json` do not have corresponding Detection Specification markdown files under `docs/lightml/detection_specifications/`.
- **Evidence**: The following 11 Technically Mature Profiles have **Evidence Not Found** for their Detection Specification:
  - `employment_contract`
  - `lease_agreement`
  - `software_license`
  - `service_agreement`
  - `consulting_agreement`
  - `commercial_agreement`
  - `non_disclosure_agreement`
  - `loan_agreement`
  - `partnership_agreement`
  - `purchase_agreement`
  - `general_contract`
  *(Note: Three additional profile implementations construction_contract, insurance_contract, and it_services_contract exist in the repository but are not recognized as Technically Mature for production baseline purposes)*
- **Recommendation**: Generate Detection Specification markdown files for these 11 Technically Mature Profiles using the same structure as the incomplete ones.

### [CRITICAL] Lack of Signed Legal Reviewer Sign-off for All Profiles
- **Classification**: Critical
- **Description**: No physical evidence of signed legal approval (e.g. by a qualified legal reviewer) exists in the repository for any of the 56 contract profiles. All profiles are legally unverified.
- **Evidence**: **Evidence Not Found** (All 56 profiles list `Legal_Reviewer: Pending` and `Approval_Date: Pending`).
- **Recommendation**: Initiate a formal review cycle with the Legal Data Owner (Ilham) to review the configurations, aliases, and legal references, and record signed approval documents in the repository.

### [MINOR] Registry and Active Profile Naming Inconsistencies
- **Classification**: Minor
- **Description**: Discrepancies in naming conventions between the active profile registry `profiles.json` and the central registry `registry_v1.json`.
- **Evidence**:
  - `construction_agreement` (active) vs `construction_contract` (registry)
  - `insurance_agreement` (active) vs `insurance_contract` (registry)
  - `it_service_agreement` (active) vs `it_services_contract` (registry)
- **Recommendation**: Reconcile naming conventions across registries to ensure 1:1 mapping consistency.

### [INFORMATIONAL] Profile `saas_agreement` Omitted from Phase 2 Registry
- **Classification**: Informational
- **Description**: The active profile `saas_agreement` has an individual JSON definition and e2e test fixtures, but is entirely missing from the central `registry_v1.json` file. Instead, the registry maps 'saas agreement' as an alias of the `software_license` profile.
- **Evidence**: **Evidence Not Found** (No registry profile exists with ID `saas_agreement` in `registry_v1.json`).
- **Recommendation**: Determine whether SaaS Agreements should be reconciled under a single `software_license` profile or split into two separate registered profiles.
