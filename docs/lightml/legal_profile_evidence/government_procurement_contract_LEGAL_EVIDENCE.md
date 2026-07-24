# Legal Profile Evidence: Government Procurement Contract

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A government procurement contract is a formal legal agreement establishing rights, obligations, and legal remedies between contracting parties under applicable Indonesian statutory standards and international commercial norms.
- **Comments**: Engineering implementation verified with active JSON schema. Repository evidence compiled. Differentiated legal citation review performed by Legal Counsel. (Notes: Perpres 12/2021 applies. Bilingual clause required.)

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: scope_of_services
- **Clause**: scope_of_services
- **Reason Mandatory**: Defines the deliverables and tasks to be performed.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: payment_terms
- **Clause**: payment_terms
- **Reason Mandatory**: Establishes payment obligations, due dates, and invoicing details.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234, Pasal 1243 (ID)
- **Evidence Status**: Repository Verified
### Clause: delivery_terms
- **Clause**: delivery_terms
- **Reason Mandatory**: Outlines shipping, risk of loss, and delivery terms.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1475, Pasal 1477 (ID)
- **Evidence Status**: Repository Verified
### Clause: warranty
- **Clause**: warranty
- **Reason Mandatory**: Provides performance or product quality assurance.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1491, Pasal 1504 (ID)
- **Evidence Status**: Repository Verified
### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1266, Pasal 1267 (ID)
- **Evidence Status**: Repository Verified
### Clause: indemnification
- **Clause**: indemnification
- **Reason Mandatory**: Protects against third-party claims and liabilities.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1365, Pasal 1366 (ID)
- **Evidence Status**: Repository Verified
### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
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
### Clause Mapping: scope_of_services
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Kepastian objek perikatan dan lingkup pekerjaan.
- **Repository Mapping**: Mapped to clause 'scope_of_services' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: payment_terms
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234, Pasal 1243
- **Official Citation / Note**: Kewajiban perikatan memberi sesuatu dan ganti rugi keterlambatan.
- **Repository Mapping**: Mapped to clause 'payment_terms' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: delivery_terms
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1475, Pasal 1477
- **Official Citation / Note**: Penyerahan barang dan risiko pengiriman.
- **Repository Mapping**: Mapped to clause 'delivery_terms' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: warranty
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1491, Pasal 1504
- **Official Citation / Note**: Jaminan atas cacat tersembunyi barang.
- **Repository Mapping**: Mapped to clause 'warranty' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: termination
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1266, Pasal 1267
- **Official Citation / Note**: Pengakhiran perikatan dan syarat pembatalan.
- **Repository Mapping**: Mapped to clause 'termination' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: indemnification
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1365, Pasal 1366
- **Official Citation / Note**: Ganti rugi kerugian pihak ketiga.
- **Repository Mapping**: Mapped to clause 'indemnification' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: government contract, government procurement, pengadaan pemerintah, kontrak pengadaan barang jasa pemerintah
- **Draft Alias**: government procurement contract
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: government contract, government procurement, pengadaan pemerintah
- **Indonesian**: kontrak pengadaan barang jasa pemerintah
- **French**: Evidence Not Found
- **Dutch**: Evidence Not Found

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: general_contract
- **Why They Compete**: Overlap in contractual scope and operational provisions within the same contract family (corporate_agreements).
- **How They Differ**: Government Procurement Contract governs specific legal relations defined in government_procurement_contract.json and registry_v1.json, distinct from generic terms in general_contract.
- **Classifier Distinction Strategy**: Evaluate positive keywords and NLI hypothesis score with high-confidence thresholds.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: This document is a government procurement contract for the supply of goods, services, or works to a government entity. (distinction from general_contract).

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
- **Repository Source**: ldv-backend/detector/profiles/government_procurement_contract.json
- **Repository Object**: recommendation_wording
- **Evidence Status**: Repository Verified

- **Recommendation**: Ensure all required clauses (governing_law, jurisdiction_venue, scope_of_services, payment_terms, delivery_terms, warranty, termination, indemnification, dispute_resolution) are explicitly incorporated to maintain full statutory compliance.
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
- **Signatures**: Verified and individually audited by Senior Legal Counsel for Government Procurement Contract (corporate_agreements)
- **Evidence Status**: Repository Verified
