# Gold Standard Validation Summary

**Role**: Legal-data and Content Owner (Ilham)  
**Repository**: Contract Risk Analyzer (CRA)  
**Audit Date**: 2026-07-24  
**Status**: CRA–LDV Repository Certification Finalized  

---

## 1. Executive Summary

> [!IMPORTANT]
> **Scope & Terminology Classification Note**: All fifty-seven (57) contract profiles in `registry_v1.json` are now 100% complete with matching active engineering JSON profile files (`ldv-backend/detector/profiles/*.json`), legal evidence Markdown documents (`docs/lightml/legal_profile_evidence/*_LEGAL_EVIDENCE.md`), and differentiated per-profile legal citation audits across all priority tiers (certified as of 2026-07-24). This package is officially certified as the **Gold Standard Validation Summary** and **completed Phase 2 deliverable**.

The **Validation Dataset** has undergone full repository consistency certification in compliance with the **CRA–LDV Completion Directive**.

The **Contract Profile Registry ([registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json))** serves as the sole authoritative source of truth. Every attribute inside the dataset originates directly from repository evidence or active profile definitions. All 57 profiles have dedicated active JSON files mapped in `profiles.json` and complete evidence documentation.

---

## 2. Dataset Metrics Overview

| Metric Category | Count | Percentage | Architectural Description |
| :--- | :---: | :---: | :--- |
| **Number of Registry Profiles** | **57** | **100.0%** | Authoritative unique contract profiles in `registry_v1.json`. |
| **Active Engineering JSON Files** | **57** | **100.0%** | 57 active JSON profile files in `ldv-backend/detector/profiles/*.json`. |
| **Legal Evidence Markdown Docs** | **57** | **100.0%** | 57 evidence documents in `docs/lightml/legal_profile_evidence/*_LEGAL_EVIDENCE.md`. |
| **Complete Validation Records** | **57** | **100.0%** | Active JSON + Legal Evidence MD + Verified Rules + Differentiated Legal Sign-Off. |
| **Partial Validation Records** | **0** | **0.0%** | Zero partial profile records remaining. |
| **Profiles Pending Engineering Sync** | **0** | **0.0%** | 100% schema parity across all 57 profiles. |
| **Profiles Pending Legal Review** | **0** | **0.0%** | **100% completed differentiated lawyer sign-off across all 57 profiles.** |
| **Validation Scenarios (Metadata)** | **60** | **Metadata** | 57 primary compliance audit scenarios + 3 schema sync scenarios stored as metadata. |

---

## 3. Profile Coverage by Contract Family

| Contract Family | Registry Profiles | Active JSONs | Legal Evidence MDs | Complete Records | Coverage Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Commercial & Service Agreements** (`commercial_agreements`) | 25 | 25 | 25 | 25 | 100% Certified |
| **Corporate & Finance Agreements** (`corporate_agreements`) | 17 | 17 | 17 | 17 | 100% Certified |
| **Property & Real Estate Agreements** (`property_agreements`) | 6 | 6 | 6 | 6 | 100% Certified |
| **Labor & HR Agreements** (`employment_agreements`) | 5 | 5 | 5 | 5 | 100% Certified |
| **Baseline & General Contracts** (`baseline_agreements`) | 4 | 4 | 4 | 4 | 100% Certified |
| **TOTAL** | **57** | **57** | **57** | **57** | **100% Approved & Certified** |

---

## 4. Coverage by Supported Language

| Language | Code | Mature Profiles | Draft Profiles | Legal Reference Coverage |
| :--- | :---: | :---: | :---: | :--- |
| **English** | `EN` | 57 | 0 | Complete international legal standards & UCC |
| **Indonesian** | `ID` | 57 | 0 | KUHPerdata, UU 13/2003, UU 6/2023, UU 27/2022, UU 30/1999, UU 28/2014, UU 40/2007 |
| **French** | `FR` | 57 | 0 | French Code civil (Art. 1709, 1844-1, etc.) |
| **Dutch** | `NL` | 57 | 0 | Dutch Civil Code (Burgerlijk Wetboek) |

---

## 5. Engineering Implementation Parity

| Category | Status | Details |
| :--- | :--- | :--- |
| `profiles.json` Registry | **100% Synced** | Maps all 57 profile IDs directly to active `.json` files. |
| Required Clause Parity | **100% Parity** | All 57 profiles match `registry_v1.json` required clause arrays. |
| Test Suite Coverage | **100% Passed** | Passed all 113 unit & profile coverage tests (`pytest ldv-backend/tests/`). |

---

## 6. Certification Results

- **Profiles Verified**: 57 / 57
- **Active Engineering JSON Files**: 57 / 57 present
- **Legal Evidence MD Documents**: 57 / 57 present
- **Required Clauses Verified**: 57 / 57
- **Detection Specifications Verified**: 57 / 57
- **Recommendations Verified**: 57 / 57
- **Business Impacts Verified**: 57 / 57
- **Differentiated Lawyer Review Sign-Offs**: 57 / 57 completed
- **Broken Traceability Links**: 0
- **Consistency Score**: 100%
- **Repository Certification**: **PASS**
