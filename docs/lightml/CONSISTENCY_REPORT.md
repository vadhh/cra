# Contract Risk Analyzer (CRA) — Repository Consistency Audit Report

> [!IMPORTANT]
> **Audit Disclaimer:** This consistency check evaluates alignment between configuration manifests and actual files. Non-compliance is flagged explicitly as **Evidence Not Found** where evidence is missing.

## 1. Naming Consistency
- **Findings**: Discrepancies exist between active profile names in `profiles.json` and the central registry `registry_v1.json`.
- **Specific Mismatches**:
  - Active ID `construction_agreement` maps to registry ID `construction_contract`.
  - Active ID `insurance_agreement` maps to registry ID `insurance_contract`.
  - Active ID `it_service_agreement` maps to registry ID `it_services_contract`.
- **Verification Status**: Inconsistent (Naming convention mismatch between active Profile Manager and registry manifest).

## 2. Registry Consistency
- **Findings**: The active profile `saas_agreement` is defined in `profiles.json` and has a JSON definition, but is entirely missing as a distinct profile ID in `registry_v1.json`.
- **Verification Status**: Inconsistent (Active profile list is out of sync with central registry).

## 3. Aliases Consistency
- **Findings**: Alias collisions and overlaps exist in the registry notes and mappings. For instance, the term 'saas agreement' is mapped as an alias of the `software_license` profile in the registry, while a separate active profile file `saas_agreement.json` exists in the system.
- **Verification Status**: Inconsistent (Overlapping aliases between software license and SaaS agreement).

## 4. Detection Specification Coverage
- **Findings**: Specifications exist for all 45 Partially Usable profiles in the registry. The 11 Technically Mature profiles do not require Detection Specifications.
- **Verification Status**: Compliant (Specifications present for all 45 Partially Usable profiles).

## 5. Corpus Coverage
- **Findings**: Contract corpus fixtures exist for all 56 profiles in the registry. Each has a dedicated directory with a normal, missing, and risky contract draft.
- **Verification Status**: Compliant (Corpus contains 168 files covering all registered types).

## 6. Legal Reference Availability
- **Findings**: Legal citations exist in `legal_citations.csv` matching some of the required clauses. However, 12 profiles in the registry have required clauses with no matching citations. In these cases, **Evidence Not Found** for legal citations is reported in the trace.
- **Verification Status**: Partial Coverage.

## 7. Duplicated Profiles
- **Findings**: No duplicated profile IDs were found in the registry file `registry_v1.json`.
- **Verification Status**: Compliant.

## 8. Orphan Profiles
- **Findings**: Several profiles in `registry_v1.json` (such as `grant_agreement`, `settlement_agreement`, etc.) have no individual JSON definition or code implementation in the repository, making them draft/orphan registry entries.
- **Verification Status**: Draft Only (Inactive entries in registry).
