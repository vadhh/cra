# Registry Change Proposal

## Objective
The objective of this proposal is to document adjustments required for the central registry [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json) to synchronize it with active backend implementations, resolve naming mismatches, and add missing profile definitions.

---

## 1. Proposals for Alignment

### Proposal 1: Integrate SaaS Agreement Profile
- **Current State**: `saas_agreement` exists as an active configuration ([saas_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/saas_agreement.json)) and has end-to-end test coverage. However, it is missing as a distinct profile ID in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json), and the term `'saas agreement'` is mapped as an alias of the `software_license` entry.
- **Proposed Change**: 
  - Add a new profile entry to the `profiles` array in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json) with ID `saas_agreement`.
  - Set its required clauses to match those in [saas_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/saas_agreement.json): `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`, `license_grant`, `ip_ownership`, `warranty_disclaimer`.
  - Remove `'saas agreement'` from `software_license` aliases in the registry.
- **Reason**: Eliminates the alias collision and ensures that SaaS contract uploads resolve to the correct required clause checklist and scoring rules.
- **Impact**: Restores correct system routing and prevents double-penalizing or scoring mismatches for SaaS documents.
- **Engineering Owner Required**: Afridho

### Proposal 2: Align Construction Profile Naming
- **Current State**: The active profile ID is `construction_agreement` ([construction_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/construction_agreement.json)), but the registry entry ID is `construction_contract`.
- **Proposed Change**: Update the profile ID in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json) from `construction_contract` to `construction_agreement`, and update all related alias mappings and required clause lists.
- **Reason**: Unifies the configuration ID space and resolves mapping errors between the active profile manager and the registry validator.
- **Impact**: Ensures that automated validators (like `validate_profiles.py`) and schema checks pass with 100% naming parity.
- **Engineering Owner Required**: Afridho

### Proposal 3: Align Insurance Profile Naming
- **Current State**: The active profile ID is `insurance_agreement` ([insurance_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/insurance_agreement.json)), but the registry ID is `insurance_contract`.
- **Proposed Change**: Update the profile ID in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json) from `insurance_contract` to `insurance_agreement`.
- **Reason**: Resolves naming mismatch between active configuration files and the central registry.
- **Impact**: Prevents profile loading errors during database persistence and analysis.
- **Engineering Owner Required**: Afridho

### Proposal 4: Align IT Services Profile Naming
- **Current State**: The active profile ID is `it_service_agreement` ([it_service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/it_service_agreement.json)), but the registry ID is `it_services_contract`.
- **Proposed Change**: Update the profile ID in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json) from `it_services_contract` to `it_service_agreement`.
- **Reason**: Ensures naming consistency across profile definitions.
- **Impact**: Resolves mismatch in the central registry validation trace.
- **Engineering Owner Required**: Afridho
