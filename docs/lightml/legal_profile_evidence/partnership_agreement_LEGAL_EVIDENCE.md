# Legal Profile Evidence: Partnership Agreement

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A partnership agreement is a contract establishing a co-ownership structure under which two or more partners agree to pool resources and share the profits, losses, and management responsibilities of a business venture.
- **Comments**: Engineering implementation available. Repository evidence reviewed. Formal legal validation pending. Legal approval pending. (Notes: )

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Clause: capital_contribution
- **Clause**: capital_contribution
- **Reason Mandatory**: Defines the capital partners must contribute to the partnership.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: French civil-style code Article Art. 1832 (generic), French Code civil Article Art. 1832 (FR), KUHPerdata Article Pasal 1618 (ID)
- **Evidence Status**: Repository Verified

### Clause: profit_sharing
- **Clause**: profit_sharing
- **Reason Mandatory**: Establishes how profits and losses are shared among partners.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: French civil-style code Article Art. 1832 (generic), French Code civil Article Art. 1832 (FR), KUHPerdata Article Pasal 1618 (ID)
- **Evidence Status**: Repository Verified

### Clause: management_rights
- **Clause**: management_rights
- **Reason Mandatory**: Defines the voting and decision-making rights of partners.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: French Code civil Article Art. 1852 (FR), KUHPerdata Article Pasal 1636 (ID)
- **Evidence Status**: Repository Verified

### Clause: termination
- **Clause**: termination
- **Reason Mandatory**: Defines the conditions under which parties can end the contract.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
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
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 40 Tahun 2014 tentang Perasuransian, KUHPerdata Article Pasal 1636
- **Evidence Status**: Repository Verified

### Jurisdiction: Belgium
- **Jurisdiction**: Belgium
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: Belgian Civil Code, Book 5 Article Art. 5.88, Belgian Civil Code, Book 5 Article Art. 5.51
- **Evidence Status**: Repository Verified

### Jurisdiction: France
- **Jurisdiction**: France
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: French Code civil Article Art. 1224, French Code civil Article Art. 2288
- **Evidence Status**: Repository Verified

### Jurisdiction: Netherlands
- **Jurisdiction**: Netherlands
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: England & Wales
- **Jurisdiction**: England & Wales
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: United States
- **Jurisdiction**: United States
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
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

### Clause Mapping: capital_contribution
- **Law / Code**: French civil-style code
- **Article**: Art. 1832
- **Official Citation / Note**: Partners must contribute capital or industry
- **Repository Mapping**: Mapped to clause 'capital_contribution' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: capital_contribution
- **Law / Code**: French Code civil
- **Article**: Art. 1832
- **Official Citation / Note**: Les associés conviennent d'apporter des biens ou leur industrie
- **Repository Mapping**: Mapped to clause 'capital_contribution' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: capital_contribution
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1618
- **Official Citation / Note**: Setiap sekutu wajib memasukkan modal ke persekutuan
- **Repository Mapping**: Mapped to clause 'capital_contribution' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: profit_sharing
- **Law / Code**: French civil-style code
- **Article**: Art. 1832
- **Official Citation / Note**: Partners must share profits and losses
- **Repository Mapping**: Mapped to clause 'profit_sharing' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: profit_sharing
- **Law / Code**: French Code civil
- **Article**: Art. 1832
- **Official Citation / Note**: Les associés partagent le bénéfice ou profit et les pertes
- **Repository Mapping**: Mapped to clause 'profit_sharing' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: profit_sharing
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1618
- **Official Citation / Note**: Pembagian untung dan rugi diatur berdasarkan kontribusi modal
- **Repository Mapping**: Mapped to clause 'profit_sharing' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: management_rights
- **Law / Code**: French Code civil
- **Article**: Art. 1852
- **Official Citation / Note**: Les associés prennent les décisions collectives de gestion
- **Repository Mapping**: Mapped to clause 'management_rights' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: management_rights
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1636
- **Official Citation / Note**: Pengurus persekutuan ditunjuk untuk mengelola hubungan usaha
- **Repository Mapping**: Mapped to clause 'management_rights' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: partnership agreement, partnership contract, joint venture
- **Draft Alias**: joint venture agreement, perjanjian kemitraan, perjanjian kerjasama, contrat de partenariat, samenwerkingsovereenkomst
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: joint venture agreement, partnership contract, joint venture, partnership agreement
- **Indonesian**: perjanjian kemitraan, perjanjian kerjasama
- **French**: contrat de partenariat
- **Dutch**: samenwerkingsovereenkomst

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: joint_venture_agreement, commercial_agreement
- **Why They Compete**: Overlap in collaborative business structures, joint operations, and profit sharing.
- **How They Differ**: A partnership agreement establishes an ongoing co-ownership structure under which partners agree to pool resources and share all profits, losses, and management responsibilities of a business. A joint venture agreement is project-specific and does not create a permanent co-ownership entity.
- **Classifier Distinction Strategy**: Identify whether the parties are establishing an ongoing co-ownership business structure with mutual agency, or a project-specific collaboration (joint venture).

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: A partnership agreement establishes an ongoing co-ownership structure under which partners agree to pool resources and share all profits, losses, and management responsibilities of a business. A joint venture agreement is project-specific and does not create a permanent co-ownership entity. (commercial and legal separation from competing profiles: joint_venture_agreement, commercial_agreement).

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
- **Repository Source**: ldv-backend/detector/profiles/partnership_agreement.json
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
