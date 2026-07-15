# Registry Health Report

This report evaluates the status of the central Contract Profile Registry and registered profiles.

---

## 1. Executive Summary
*   **Registry Status**: `🟢 HEALTHY (100% OPERATIONAL)`
*   **Total Registered Profiles**: **15**
*   **Validation Errors**: **0**

---

## 2. Profile Registry List
The central registry at [profiles.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/profiles.json) maps the following profiles:

| Profile ID | Target JSON File | Family | Release Stage |
| :--- | :--- | :--- | :--- |
| `commercial_agreement` | [commercial_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/commercial_agreement.json) | `commercial_agreements` | `stable` |
| `construction_agreement` | [construction_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/construction_agreement.json) | `property_agreements` | `stable` |
| `consulting_agreement` | [consulting_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/consulting_agreement.json) | `commercial_agreements` | `stable` |
| `employment_contract` | [employment_contract.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/employment_contract.json) | `employment_agreements` | `stable` |
| `general_contract` | [general_contract.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/general_contract.json) | `baseline_agreements` | `stable` |
| `insurance_agreement` | [insurance_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/insurance_agreement.json) | `baseline_agreements` | `stable` |
| `it_service_agreement` | [it_service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/it_service_agreement.json) | `commercial_agreements` | `stable` |
| `lease_agreement` | [lease_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/lease_agreement.json) | `property_agreements` | `stable` |
| `loan_agreement` | [loan_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/loan_agreement.json) | `corporate_agreements` | `stable` |
| `non_disclosure_agreement` | [non_disclosure_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/non_disclosure_agreement.json) | `commercial_agreements` | `stable` |
| `partnership_agreement` | [partnership_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/partnership_agreement.json) | `corporate_agreements` | `stable` |
| `purchase_agreement` | [purchase_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/purchase_agreement.json) | `commercial_agreements` | `stable` |
| `saas_agreement` | [saas_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/saas_agreement.json) | `commercial_agreements` | `stable` |
| `service_agreement` | [service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/service_agreement.json) | `commercial_agreements` | `stable` |
| `software_license` | [software_license.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/software_license.json) | `commercial_agreements` | `stable` |

---

## 3. Consistency Checks
*   **No Duplicate Aliases**: `✅ PASSED`. Every alias uniquely maps to a single profile.
*   **Schema Validation**: `✅ PASSED`. All JSON profiles conform to `contract_profile.schema.json`.
*   **Circular References**: `✅ PASSED`. No dependency loops detected.
