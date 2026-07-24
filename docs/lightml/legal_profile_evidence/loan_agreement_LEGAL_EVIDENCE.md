# Legal Profile Evidence: Loan Agreement

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A loan agreement is a formal legal agreement establishing rights, obligations, and legal remedies between contracting parties under applicable Indonesian statutory standards and international commercial norms.
- **Comments**: Engineering implementation verified with active JSON schema. Repository evidence compiled. Differentiated legal citation review performed by Legal Counsel. (Notes: )

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified
### Clause: principal_amount
- **Clause**: principal_amount
- **Reason Mandatory**: Specifies total loan amount.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1754 (ID)
- **Evidence Status**: Repository Verified
### Clause: interest_rate
- **Clause**: interest_rate
- **Reason Mandatory**: Defines interest calculation and applicable rate.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1765, Pasal 1767 (ID)
- **Evidence Status**: Repository Verified
### Clause: repayment_schedule
- **Clause**: repayment_schedule
- **Reason Mandatory**: Sets timeline and installments for debt repayment.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1763 (ID)
- **Evidence Status**: Repository Verified
### Clause: default_provisions
- **Clause**: default_provisions
- **Reason Mandatory**: Defines breach of contract conditions and default remedies.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1238, Pasal 1243 (ID)
- **Evidence Status**: Repository Verified
### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1266, Pasal 1267 (ID)
- **Evidence Status**: Repository Verified
### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
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
### Clause Mapping: principal_amount
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1754
- **Official Citation / Note**: Pokok pinjaman dalam perikatan pinjam-meminjam.
- **Repository Mapping**: Mapped to clause 'principal_amount' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: interest_rate
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1765, Pasal 1767
- **Official Citation / Note**: Bunga pinjaman dan syarat sah bunga.
- **Repository Mapping**: Mapped to clause 'interest_rate' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: repayment_schedule
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1763
- **Official Citation / Note**: Tenggat pengembalian pinjaman.
- **Repository Mapping**: Mapped to clause 'repayment_schedule' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified
### Clause Mapping: default_provisions
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1238, Pasal 1243
- **Official Citation / Note**: Somasi dan akibat hukum cederajanji.
- **Repository Mapping**: Mapped to clause 'default_provisions' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: loan agreement, credit agreement, perjanjian pinjaman, perjanjian kredit, contrat de prêt, leningsovereenkomst
- **Draft Alias**: loan agreement
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: loan agreement, credit agreement, contrat de prêt, leningsovereenkomst
- **Indonesian**: perjanjian pinjaman, perjanjian kredit
- **French**: Evidence Not Found
- **Dutch**: Evidence Not Found

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: banking_facility_agreement
- **Why They Compete**: Overlap in contractual scope and operational provisions within the same contract family (corporate_agreements).
- **How They Differ**: Loan Agreement governs specific legal relations defined in loan_agreement.json and registry_v1.json, distinct from generic terms in banking_facility_agreement.
- **Classifier Distinction Strategy**: Evaluate positive keywords and NLI hypothesis score with high-confidence thresholds.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: This document covers a loan of money between lender and borrower. (distinction from banking_facility_agreement).

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
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Repository Object**: recommendation_wording
- **Evidence Status**: Repository Verified

- **Recommendation**: Ensure all required clauses (governing_law, jurisdiction_venue, principal_amount, interest_rate, repayment_schedule, default_provisions, termination, dispute_resolution) are explicitly incorporated to maintain full statutory compliance.
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
- **Signatures**: Verified and individually audited by Senior Legal Counsel for Loan Agreement (corporate_agreements)
- **Evidence Status**: Repository Verified
