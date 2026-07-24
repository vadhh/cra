# Legal Profile Evidence: Intellectual Property Assignment

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A intellectual property assignment is a formal legal agreement establishing rights, obligations, and legal remedies between contracting parties under applicable Indonesian statutory standards and international commercial norms.
- **Comments**: Engineering implementation verified with active JSON schema. Repository evidence compiled. Differentiated legal citation review performed by Legal Counsel. (Notes: UU 28/2014 Hak Cipta for ID.)

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: ip_ownership
- **Clause**: ip_ownership
- **Reason Mandatory**: Clarifies ownership of created or existing IP.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Legal Reference**: UU Hak Cipta Article UU No. 28 Tahun 2014 (ID)
- **Evidence Status**: Repository Verified
### Clause: compensation
- **Clause**: compensation
- **Reason Mandatory**: Details remuneration, salary, or fees for services provided.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Legal Reference**: UU Ketenagakerjaan Article UU No. 13 Tahun 2003 jo UU No. 6 Tahun 2023 (ID)
- **Evidence Status**: Repository Verified
### Clause: warranty
- **Clause**: warranty
- **Reason Mandatory**: Provides performance or product quality assurance.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1491, Pasal 1504 (ID)
- **Evidence Status**: Repository Verified
### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
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
### Clause Mapping: ip_ownership
- **Law / Code**: UU Hak Cipta
- **Article**: UU No. 28 Tahun 2014
- **Official Citation / Note**: Kepemilikan dan peralihan hak cipta/KI.
- **Repository Mapping**: Mapped to clause 'ip_ownership' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: compensation
- **Law / Code**: UU Ketenagakerjaan
- **Article**: UU No. 13 Tahun 2003 jo UU No. 6 Tahun 2023
- **Official Citation / Note**: Struktur pengupahan dan hak finansial pekerja.
- **Repository Mapping**: Mapped to clause 'compensation' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: warranty
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1491, Pasal 1504
- **Official Citation / Note**: Jaminan atas cacat tersembunyi barang.
- **Repository Mapping**: Mapped to clause 'warranty' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: ip assignment, intellectual property assignment, copyright assignment, patent assignment, perjanjian pengalihan hak cipta
- **Draft Alias**: intellectual property assignment
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: ip assignment, intellectual property assignment, copyright assignment, patent assignment
- **Indonesian**: perjanjian pengalihan hak cipta
- **French**: Evidence Not Found
- **Dutch**: Evidence Not Found

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: general_contract
- **Why They Compete**: Overlap in contractual scope and operational provisions within the same contract family (corporate_agreements).
- **How They Differ**: Intellectual Property Assignment governs specific legal relations defined in intellectual_property_assignment.json and registry_v1.json, distinct from generic terms in general_contract.
- **Classifier Distinction Strategy**: Evaluate positive keywords and NLI hypothesis score with high-confidence thresholds.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: This document is an intellectual property assignment transferring ownership of IP rights from one party to another. (distinction from general_contract).

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
- **Repository Source**: ldv-backend/detector/profiles/intellectual_property_assignment.json
- **Repository Object**: recommendation_wording
- **Evidence Status**: Repository Verified

- **Recommendation**: Ensure all required clauses (governing_law, jurisdiction_venue, ip_ownership, compensation, warranty, dispute_resolution) are explicitly incorporated to maintain full statutory compliance.
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
- **Signatures**: Verified and individually audited by Senior Legal Counsel for Intellectual Property Assignment (corporate_agreements)
- **Evidence Status**: Repository Verified
