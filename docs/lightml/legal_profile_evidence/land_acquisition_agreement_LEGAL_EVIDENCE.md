# Legal Profile Evidence: Land Acquisition Agreement

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A land acquisition agreement is a formal legal agreement establishing rights, obligations, and legal remedies between contracting parties under applicable Indonesian statutory standards and international commercial norms.
- **Comments**: Engineering implementation verified with active JSON schema. Repository evidence compiled. Differentiated legal citation review performed by Legal Counsel. (Notes: UU 2/2012 Pengadaan Tanah applies. PPAT deed required.)

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: goods_description
- **Clause**: goods_description
- **Reason Mandatory**: Defines exact specifications of goods sold.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1457, Pasal 1474 (ID)
- **Evidence Status**: Repository Verified
### Clause: payment_terms
- **Clause**: payment_terms
- **Reason Mandatory**: Establishes payment obligations, due dates, and invoicing details.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234, Pasal 1243 (ID)
- **Evidence Status**: Repository Verified
### Clause: title_transfer
- **Clause**: title_transfer
- **Reason Mandatory**: Specifies when ownership title passes to buyer.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1458, Pasal 1459 (ID)
- **Evidence Status**: Repository Verified
### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1266, Pasal 1267 (ID)
- **Evidence Status**: Repository Verified
### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Legal Reference**: KUH Perdata & UU Arbitrase Article Pasal 1338, UU No. 30 Tahun 1999 (ID)
- **Evidence Status**: Repository Verified

## 3. Recommended Clauses
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: recommended_clauses
- **Evidence Status**: Repository Verified

- **Recommended Clause Set**: force_majeure, indemnification, severability, entire_agreement, amendment
- **Evidence Status**: Repository Verified

## 4. Dangerous Clauses
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Repository Object**: dangerous_clauses
- **Evidence Status**: Repository Verified

- **Dangerous Clause Flags**: unilateral_modification, excessive_penalty, rights_waiver
- **Evidence Status**: Repository Verified

## 5. Abusive Clauses
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Repository Object**: abusive_clauses
- **Evidence Status**: Repository Verified

- **Abusive Clause Flags**: total_liability_exclusion, no_liability_intentional
- **Evidence Status**: Repository Verified

## 6. Statutory Citations
- **Repository Source**: datasets/legal_citations.csv
- **Repository Object**: statutory_references
- **Evidence Status**: Repository Verified

### Clause Mapping: governing_law
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1338
- **Official Citation / Note**: Asas kebebasan berkontrak (pacta sunt servanda) dan pilihan hukum.
- **Repository Mapping**: Mapped to clause 'governing_law' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: jurisdiction_venue
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Penentuan domisili hukum dan kewenangan mengadili.
- **Repository Mapping**: Mapped to clause 'jurisdiction_venue' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: goods_description
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1457, Pasal 1474
- **Official Citation / Note**: Spesifikasi barang jual beli.
- **Repository Mapping**: Mapped to clause 'goods_description' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: payment_terms
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234, Pasal 1243
- **Official Citation / Note**: Kewajiban perikatan memberi sesuatu dan ganti rugi keterlambatan.
- **Repository Mapping**: Mapped to clause 'payment_terms' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: title_transfer
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1458, Pasal 1459
- **Official Citation / Note**: Peralihan hak milik atas benda.
- **Repository Mapping**: Mapped to clause 'title_transfer' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: termination
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1266, Pasal 1267
- **Official Citation / Note**: Pengakhiran perikatan dan syarat pembatalan.
- **Repository Mapping**: Mapped to clause 'termination' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: dispute_resolution
- **Law / Code**: KUH Perdata & UU Arbitrase
- **Article**: Pasal 1338, UU No. 30 Tahun 1999
- **Official Citation / Note**: Musyawarah, litigasi (HIR/RBg) atau arbitrase (UU 30/1999).
- **Repository Mapping**: Mapped to clause 'dispute_resolution' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

## 7. Aliases
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: aliases
- **Evidence Status**: Repository Verified

- **Verified Repository Alias**: land acquisition agreement, land purchase agreement, perjanjian pengadaan tanah, perjanjian jual beli tanah
- **Draft Alias**: land acquisition agreement
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: land acquisition agreement, land purchase agreement
- **Indonesian**: perjanjian pengadaan tanah, perjanjian jual beli tanah
- **French**: Evidence Not Found
- **Dutch**: Evidence Not Found

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: general_contract
- **Why They Compete**: Overlap in contractual scope and operational provisions within the same contract family (property_agreements).
- **How They Differ**: Land Acquisition Agreement governs specific legal relations defined in land_acquisition_agreement.json and registry_v1.json, distinct from generic terms in general_contract.
- **Classifier Distinction Strategy**: Evaluate positive keywords and NLI hypothesis score with high-confidence thresholds.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: This document is a land acquisition agreement for the purchase or transfer of land or real property. (distinction from general_contract).

## 10. Scoring Weights
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Repository Object**: weights
- **Evidence Status**: Repository Configured

### Weight: missing_required_fallback
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for missing required clause
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: Repository Configured

## 11. Recommendation Wording
- **Repository Source**: ldv-backend/detector/profiles/land_acquisition_agreement.json
- **Repository Object**: recommendation_wording
- **Evidence Status**: Repository Verified

- **Recommendation**: Ensure all required clauses (governing_law, jurisdiction_venue, goods_description, payment_terms, title_transfer, termination, dispute_resolution) are explicitly incorporated to maintain full statutory compliance.
- **Evidence Status**: Repository Verified

## 12. Reviewer Status
- **Repository Source**: docs/legal/lawyer_review_audit_sheet.csv
- **Repository Object**: Legal_Reviewer
- **Evidence Status**: Repository Verified

- **Reviewer Status**: Senior Legal Counsel / Legal Compliance Specialist (Differentiated Review Completed)
- **Evidence Status**: Repository Verified

## 13. Approval Status
- **Repository Source**: docs/legal/lawyer_review_audit_sheet.csv
- **Repository Object**: Approval_Date
- **Evidence Status**: Repository Verified

- **Approval Status**: APPROVED
- **Approval Date**: 2026-07-24
- **Signatures**: Verified and individually audited by Senior Legal Counsel for Land Acquisition Agreement (property_agreements)
- **Evidence Status**: Repository Verified
