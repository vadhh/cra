# Engineering Action List

## Objective
The objective of this document is to list the technical changes that must be executed by the Engineering Owner (Afridho) to resolve registry, profile configuration, alias, and naming inconsistencies identified during the repository review.

---

## 1. Registry Updates ([registry_v1.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/registry_v1.json))
- [ ] **Rename Profile IDs**:
  - Update `construction_contract` to `construction_agreement`.
  - Update `insurance_contract` to `insurance_agreement`.
  - Update `it_services_contract` to `it_service_agreement`.
- [ ] **Add SaaS Agreement Profile**: Create a distinct profile block for `saas_agreement` with ID `saas_agreement` mapping the required clauses.
- [ ] **De-duplicate Aliases**:
  - Remove `'saas agreement'` from `software_license` aliases list.
  - Remove `'joint venture agreement'` from `partnership_agreement` aliases list.
  - Remove `'perjanjian kerjasama'` from `partnership_agreement` aliases list.
  - Remove `'samenwerkingsovereenkomst'` from `partnership_agreement` aliases list.
- [ ] **Reconcile Required Clauses**:
  - Update `it_services_contract` (renamed to `it_service_agreement`) required clauses to include `confidentiality`.
  - Update `construction_contract` (renamed to `construction_agreement`) required clauses to include `insurance` and `limitation_liability`.
  - Update `insurance_contract` (renamed to `insurance_agreement`) required clauses to include `default_provisions`, `payment_terms`, `limitation_liability`, and `notice_period`.

---

## 2. Active Profile JSON Updates ([profiles](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/))
- [ ] **Update Required Clauses**:
  - Add `ip_ownership` and `warranty_disclaimer` to [it_service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/it_service_agreement.json).
  - Add `delivery_terms` to [construction_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/construction_agreement.json).
  - Add `insurance` to [insurance_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/insurance_agreement.json).
- [ ] **Reset validation_status**: Update `"validation_status"` from `"Validated"` to `"Pending"` and set `"review_date"` to `null` across all 15 active profile JSON files:
  - [commercial_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/commercial_agreement.json)
  - [construction_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/construction_agreement.json)
  - [consulting_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/consulting_agreement.json)
  - [employment_contract.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/employment_contract.json)
  - [general_contract.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/general_contract.json)
  - [insurance_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/insurance_agreement.json)
  - [it_service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/it_service_agreement.json)
  - [lease_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/lease_agreement.json)
  - [loan_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/loan_agreement.json)
  - [non_disclosure_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/non_disclosure_agreement.json)
  - [partnership_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/partnership_agreement.json)
  - [purchase_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/purchase_agreement.json)
  - [saas_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/saas_agreement.json)
  - [service_agreement.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/service_agreement.json)
  - [software_license.json](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/profiles/software_license.json)

---

## 3. Detection Specification Updates ([detection_specifications](file:///mnt/c/Users/ADVAN/cra/docs/lightml/detection_specifications/))
- [ ] **Rename Specification Files**:
  - Rename `construction_contract.md` to `construction_agreement.md`.
  - Rename `insurance_contract.md` to `insurance_agreement.md`.
  - Rename `it_services_contract.md` to `it_service_agreement.md`.

---

## 4. Profile Loader & Backend Updates ([ldv-backend](file:///mnt/c/Users/ADVAN/cra/ldv-backend/))
- [ ] **Update Registry Loader**: Ensure `profile_registry.py` and `detector_rules.py` handle renamed profile IDs correctly.
- [ ] **Database Provenance**: Check if database migration queries or ALTER TABLE columns depend on hardcoded registry IDs (e.g. references to `construction_contract` in test databases or default mappings) and update them if name changes are applied.

---

## 5. Frontend & UI Updates ([ldv-frontend](file:///mnt/c/Users/ADVAN/cra/ldv-frontend/))
- [ ] **Verify Dropdown Mappings**: Check the manual document profile dropdown selector on the upload checklist inside [index.html](file:///mnt/c/Users/ADVAN/cra/ldv-frontend/index.html) to ensure it uses the correct, consistent names for the renamed profiles.
