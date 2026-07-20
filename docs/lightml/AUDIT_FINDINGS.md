# Contract Risk Analyzer (CRA) — Legal Engineering Internal Audit Report

> [!IMPORTANT]
> **Audit Standards:** This audit follows strict guidelines regarding legal sign-off. Compliance or approval is never assumed. If no physical signed evidence exists in the repository, the status is reported as **Evidence Not Found**.

## 1. Executive Summary
- **Total Registered Profiles**: 56
- **Technically Mature Profiles**: 11 (19.6%)
- **Partially Usable Profiles**: 45 (80.4%)
- **Detection Specifications coverage**: 45/45 (100.0%) for Partially Usable Profiles (100.0% coverage)
- **Contract Corpus coverage**: 56/56 (100.0%)

## 2. Classified Audit Findings

### [MAJOR] Active Profiles Missing Detection Specifications [RESOLVED]
- **Classification**: Resolved
- **Description**: All 45 Partially Usable Profiles have corresponding Detection Specification markdown files under `docs/lightml/detection_specifications/`.
- **Evidence**: 45 specifications found under `detection_specifications/` matching registered profiles. The 11 Technically Mature profiles do not require Detection Specifications.
- **Recommendation**: None.

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
