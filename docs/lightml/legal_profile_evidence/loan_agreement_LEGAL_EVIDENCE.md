# Legal Profile Evidence: Loan Agreement

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A loan agreement is a contract whereby a lender transfers a principal sum of money to a borrower, who agrees to repay the principal along with agreed-upon interest according to a specified schedule.
- **Comments**: Engineering implementation available. Repository evidence reviewed. Formal legal validation pending. Legal approval pending. (Notes: )

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
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Clause: principal_amount
- **Clause**: principal_amount
- **Reason Mandatory**: Defines the principal sum of money loaned.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234 (ID)
- **Evidence Status**: Repository Verified

### Clause: interest_rate
- **Clause**: interest_rate
- **Reason Mandatory**: Specifies the interest rate charged on the loan.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234 (ID)
- **Evidence Status**: Repository Verified

### Clause: repayment_schedule
- **Clause**: repayment_schedule
- **Reason Mandatory**: Defines the schedule and installments for loan repayment.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234 (ID)
- **Evidence Status**: Repository Verified

### Clause: default_provisions
- **Clause**: default_provisions
- **Reason Mandatory**: Sets the grounds for breach and acceleration of debt.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: French Code civil Article Art. 1224 (FR), KUHPerdata Article Pasal 1238 (ID)
- **Evidence Status**: Repository Verified

### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa (ID)
- **Evidence Status**: Repository Verified

## 3. Recommended Clauses
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: recommended_clauses
- **Evidence Status**: Evidence Not Found

- **Purpose**: Evidence Not Found
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

## 4. Dangerous / Abusive / Illegal / Leonine Clauses
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: dangerous_clauses / abusive_clauses / illegal_clauses / leonine_clauses
- **Evidence Status**: Evidence Not Found

### Dangerous Clauses
- **Classification Reason**: Evidence Not Found
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Abusive Clauses
- **Classification Reason**: Evidence Not Found
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Illegal Clauses
- **Classification Reason**: Evidence Not Found
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Leonine Clauses
- **Classification Reason**: Evidence Not Found
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

## 5. Applicable Jurisdictions
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: jurisdictions
- **Evidence Status**: Repository Verified

### Jurisdiction: Indonesia
- **Jurisdiction**: Indonesia
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 40 Tahun 2014 tentang Perasuransian, KUHPerdata Article Pasal 1636
- **Evidence Status**: Repository Verified

### Jurisdiction: Belgium
- **Jurisdiction**: Belgium
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: Belgian Civil Code, Book 5 Article Art. 5.88, Belgian Civil Code, Book 5 Article Art. 5.51
- **Evidence Status**: Repository Verified

### Jurisdiction: France
- **Jurisdiction**: France
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: French Code civil Article Art. 1224, French Code civil Article Art. 2288
- **Evidence Status**: Repository Verified

### Jurisdiction: Netherlands
- **Jurisdiction**: Netherlands
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: England & Wales
- **Jurisdiction**: England & Wales
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: United States
- **Jurisdiction**: United States
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

## 6. Legal References
- **Repository Source**: datasets/legal_citations.csv
- **Repository Object**: finding_id
- **Evidence Status**: Repository Verified

### Clause Mapping: governing_law
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1338
- **Official Citation / Note**: Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
- **Repository Mapping**: Mapped to clause 'governing_law' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: principal_amount
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234
- **Official Citation / Note**: KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
- **Repository Mapping**: Mapped to clause 'principal_amount' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: interest_rate
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234
- **Official Citation / Note**: KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
- **Repository Mapping**: Mapped to clause 'interest_rate' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: repayment_schedule
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234
- **Official Citation / Note**: KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
- **Repository Mapping**: Mapped to clause 'repayment_schedule' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: default_provisions
- **Law / Code**: French Code civil
- **Article**: Art. 1224
- **Official Citation / Note**: La résolution résulte soit d'une clause résolutoire
- **Repository Mapping**: Mapped to clause 'default_provisions' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: default_provisions
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1238
- **Official Citation / Note**: Wanprestasi memerlukan adanya pernyataan lalai
- **Repository Mapping**: Mapped to clause 'default_provisions' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: termination
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
- **Repository Mapping**: Mapped to clause 'termination' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: dispute_resolution
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa
- **Official Citation / Note**: UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
- **Repository Mapping**: Mapped to clause 'dispute_resolution' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

## 7. Aliases
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: aliases
- **Evidence Status**: Repository Verified

- **Verified Repository Alias**: loan agreement, loan contract, creditor agreement, perjanjian pinjaman
- **Draft Alias**: credit agreement, perjanjian kredit, contrat de prêt, leningsovereenkomst
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: loan contract, loan agreement, creditor agreement, credit agreement
- **Indonesian**: perjanjian pinjaman, perjanjian kredit
- **French**: contrat de prêt
- **Dutch**: leningsovereenkomst

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: commercial_agreement, general_contract
- **Why They Compete**: Overlap with payment schedules, debt structures, or commercial credits.
- **How They Differ**: A loan agreement is a financial contract whose essential purpose is the provision of credit, defining the transfer of a principal sum of money and the borrower's absolute obligation to repay it with interest. General commercial contracts may contain payment schedules or trade credit terms but do not involve the lending of financial principal.
- **Classifier Distinction Strategy**: Check if the contract's primary object is the lending of a capital sum with interest charges and debt acceleration provisions.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: A loan agreement is a financial contract whose essential purpose is the provision of credit, defining the transfer of a principal sum of money and the borrower's absolute obligation to repay it with interest. General commercial contracts may contain payment schedules or trade credit terms but do not involve the lending of financial principal. (commercial and legal separation from competing profiles: commercial_agreement, general_contract).

## 10. Scoring Weights
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Repository Object**: weights
- **Evidence Status**: Repository Configured

### Weight: missing_required_fallback
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'missing_required_fallback'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: impact_weight_CRITICAL
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for missing required clause with CRITICAL impact level
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: impact_weight_HIGH
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for missing required clause with HIGH impact level
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: impact_weight_MEDIUM
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for missing required clause with MEDIUM impact level
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: impact_weight_LOW
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for missing required clause with LOW impact level
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: red_flag_high
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'red_flag_high'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: red_flag_medium
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'red_flag_medium'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: l2_unique
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'l2_unique'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: no_governing_law
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'no_governing_law'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

### Weight: no_venue
- **Repository Source**: ldv-backend/detector/policies/default_v1.json
- **Purpose**: Score deduction for risk finding 'no_venue'
- **Engineering Rationale**: Penalty-based scoring where baseline is 100
- **Calibration Status**: 
```
Engineering Default
Repository Configured
Not Yet Legally Calibrated
```

## 11. Recommendation Wording
- **Repository Source**: ldv-backend/detector/profiles/loan_agreement.json
- **Repository Object**: recommendation_wording
- **Evidence Status**: Evidence Not Found

- **Recommendation**: Draft Recommendation
- **Evidence Status**: Evidence Not Found

## 12. Reviewer Status
- **Repository Source**: docs/lightml/CRA_56_PROFILE_LEGAL_VALIDATION.xlsx
- **Repository Object**: Legal_Reviewer
- **Evidence Status**: Evidence Not Found

- **Reviewer Status**: Pending
- **Evidence Status**: Evidence Not Found

## 13. Approval Status
- **Repository Source**: docs/lightml/CRA_56_PROFILE_LEGAL_VALIDATION.xlsx
- **Repository Object**: Approval_Date
- **Evidence Status**: Evidence Not Found

- **Approval Status**: Pending
- **Approval Date**: Pending
- **Signatures**: Pending
- **Evidence Status**: Evidence Not Found
