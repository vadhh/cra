# Legal Profile Evidence: Employment Contract

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: An employment contract is an agreement under which an employee agrees to perform work under the direction and control of an employer in exchange for remuneration.
- **Comments**: Engineering implementation available. Repository evidence reviewed. Formal legal validation pending. Legal approval pending. (Notes: UU 13/2003 Ketenagakerjaan applies for ID.)

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: notice_period
- **Clause**: notice_period
- **Reason Mandatory**: Specifies advance notice required for termination or changes.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Clause: compensation
- **Clause**: compensation
- **Reason Mandatory**: Defines salary or wage obligations for work performed.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023 (ID)
- **Evidence Status**: Repository Verified

### Clause: working_hours
- **Clause**: working_hours
- **Reason Mandatory**: Defines mandatory hours of work per week or day.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023 (ID)
- **Evidence Status**: Repository Verified

### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
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
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 40 Tahun 2014 tentang Perasuransian, KUHPerdata Article Pasal 1636
- **Evidence Status**: Repository Verified

### Jurisdiction: Belgium
- **Jurisdiction**: Belgium
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Belgian Civil Code, Book 5 Article Art. 5.88, Belgian Civil Code, Book 5 Article Art. 5.51
- **Evidence Status**: Repository Verified

### Jurisdiction: France
- **Jurisdiction**: France
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: French Code civil Article Art. 1224, French Code civil Article Art. 2288
- **Evidence Status**: Repository Verified

### Jurisdiction: Netherlands
- **Jurisdiction**: Netherlands
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: England & Wales
- **Jurisdiction**: England & Wales
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: United States
- **Jurisdiction**: United States
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
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

### Clause Mapping: termination
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
- **Repository Mapping**: Mapped to clause 'termination' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: compensation
- **Law / Code**: Indonesian statute (UU)
- **Article**: UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023
- **Official Citation / Note**: UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023; peraturan ketenagakerjaan terkait.
- **Repository Mapping**: Mapped to clause 'compensation' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: working_hours
- **Law / Code**: Indonesian statute (UU)
- **Article**: UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023
- **Official Citation / Note**: UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023; peraturan ketenagakerjaan terkait.
- **Repository Mapping**: Mapped to clause 'working_hours' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: employment contract, labor contract, perjanjian kerja
- **Draft Alias**: employment agreement, work agreement, kontrak kerja
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: employment contract, employment agreement, work agreement, labor contract
- **Indonesian**: kontrak kerja, perjanjian kerja
- **French**: Evidence Not Found
- **Dutch**: Evidence Not Found

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: consulting_agreement, service_agreement
- **Why They Compete**: Provision of human labor in exchange for payment, creating regulatory and operational classification overlap.
- **How They Differ**: An employment contract is legally characterized by subordination, placing the employee under the employer's direct control and supervision. It triggers mandatory statutory protections such as minimum wage, leave, severance, and social security. Conversely, consulting and service agreements establish independent contractor relationships, where the service provider retains operational autonomy, manages their own tools, and is not subject to employer disciplinary power.
- **Classifier Distinction Strategy**: Verify if the contract contains elements of subordination (e.g. supervisor direction, disciplinary procedures, internal policies) and statutory employment rights (e.g. employee benefits, salary, working hours regulations) as opposed to independent contractor clauses (e.g. invoicing, client-independent provider status).

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: An employment contract is legally characterized by subordination, placing the employee under the employer's direct control and supervision. It triggers mandatory statutory protections such as minimum wage, leave, severance, and social security. Conversely, consulting and service agreements establish independent contractor relationships, where the service provider retains operational autonomy, manages their own tools, and is not subject to employer disciplinary power. (commercial and legal separation from competing profiles: consulting_agreement, service_agreement).

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
- **Repository Source**: ldv-backend/detector/profiles/employment_contract.json
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
