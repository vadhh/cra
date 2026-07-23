# Required Clause Reconciliation

## Objective
The objective of this document is to analyze required clause configuration mismatches between the active JSON profiles and their definitions in [registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json), recommending a path for reconciliation.

---

## 1. Mismatch Analysis and Resolutions

### Profile: IT Services Contract
- **Active Profile**: `it_service_agreement` ([it_service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/it_service_agreement.json))
- **Registry Profile**: `it_services_contract`
- **Clause Differences**:
  - Active profile contains: `confidentiality` (missing in registry)
  - Registry contains: `ip_ownership`, `warranty_disclaimer` (missing in active profile)
- **Resolution Recommendation**:
  - `confidentiality`: **Active Profile Correct**. IT service providers routinely access client proprietary environments. The registry entry must be updated to include `confidentiality`.
  - `ip_ownership` & `warranty_disclaimer`: **Registry Correct**. IT service contracts must define intellectual property rights for deliverables and disclaim default implied warranties. The active profile JSON must be updated to include these.
  - **Reconciliation Status**: Requires Engineering Review to synchronize.

### Profile: Construction Contract
- **Active Profile**: `construction_agreement` ([construction_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/construction_agreement.json))
- **Registry Profile**: `construction_contract`
- **Clause Differences**:
  - Active profile contains: `insurance`, `limitation_liability` (missing in registry)
  - Registry contains: `delivery_terms` (missing in active profile)
- **Resolution Recommendation**:
  - `insurance` & `limitation_liability`: **Active Profile Correct**. Construction agreements must require commercial general liability insurance and define liability limits to satisfy statutory compliance (such as Indonesian UU 2/2017). The registry entry must be updated to include these.
  - `delivery_terms`: **Registry Correct**. Handover, inspection, and provisional acceptance are core elements of building works. The active profile JSON must be updated to include `delivery_terms`.
  - **Reconciliation Status**: Requires Engineering Review to synchronize.

### Profile: Insurance Contract
- **Active Profile**: `insurance_agreement` ([insurance_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/insurance_agreement.json))
- **Registry Profile**: `insurance_contract`
- **Clause Differences**:
  - Active profile contains: `default_provisions`, `payment_terms`, `limitation_liability`, `notice_period` (missing in registry)
  - Registry contains: `insurance` (missing in active profile)
- **Resolution Recommendation**:
  - `default_provisions`, `payment_terms`, `limitation_liability`, `notice_period`: **Active Profile Correct**. Insurance contracts must detail premium payments, policy cancellation periods, and coverage limits. The registry entry must be updated to include these.
  - `insurance`: **Registry Correct**. The primary object of the contract is the coverage itself. The active profile JSON must be updated to include `insurance`.
  - **Reconciliation Status**: Requires Engineering Review to synchronize.

### Profile: SaaS Agreement
- **Active Profile**: `saas_agreement` ([saas_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/saas_agreement.json))
- **Registry Profile**: *None (Omitted from central registry)*
- **Clause Differences**: Active profile JSON has a complete schema, but no registry definition exists.
- **Resolution Recommendation**: **Active Profile Correct**. SaaS represents a primary commercial model for client uploads and needs a distinct registry definition.
- **Reconciliation Status**: Requires Engineering Review to add the registry profile.

---

## 2. Synchronization Summary

| Profile ID (Active) | Registry ID | Mismatch Status | Resolution Pathway |
| :--- | :--- | :--- | :--- |
| `it_service_agreement` | `it_services_contract` | Requires Engineering Review | Update registry with `confidentiality`; update JSON with `ip_ownership` and `warranty_disclaimer`. |
| `construction_agreement` | `construction_contract` | Requires Engineering Review | Update registry with `insurance` and `limitation_liability`; update JSON with `delivery_terms`. |
| `insurance_agreement` | `insurance_contract` | Requires Engineering Review | Update registry with `default_provisions`, `payment_terms`, `limitation_liability`, `notice_period`; update JSON with `insurance`. |
| `saas_agreement` | *Missing* | Requires Engineering Review | Create registry entry mapping the active profile required clauses. |
