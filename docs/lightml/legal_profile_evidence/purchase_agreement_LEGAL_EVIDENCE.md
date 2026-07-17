# Legal Profile Evidence: Purchase Agreement

## 1. Contract Definition
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Repository Object**: metadata.description
- **Evidence Status**: Repository Verified

- **Formal Legal Definition**: A purchase agreement is a contract whereby a seller transfers or agrees to transfer the ownership of physical goods or assets to a buyer in exchange for a specified monetary payment.
- **Comments**: Engineering implementation available. Repository evidence reviewed. Formal legal validation pending. Legal approval pending. (Notes: )

## 2. Mandatory Clauses
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Repository Object**: required_clauses
- **Evidence Status**: Repository Verified

### Clause: governing_law
- **Clause**: governing_law
- **Reason Mandatory**: Determines which jurisdiction's laws govern contract interpretation and enforcement.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: jurisdiction_venue
- **Clause**: jurisdiction_venue
- **Reason Mandatory**: Specifies the court or arbitration venue responsible for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Clause: goods_description
- **Clause**: goods_description
- **Reason Mandatory**: Identifies and describes the physical goods being sold.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Uniform Commercial Code Article UCC 2-201 (generic), French Code civil Article Art. 1583 (FR), KUHPerdata Article Pasal 1457 (ID)
- **Evidence Status**: Repository Verified

### Clause: payment_terms
- **Clause**: payment_terms
- **Reason Mandatory**: Establishes payment obligations, due dates, and invoicing details.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1234 (ID)
- **Evidence Status**: Repository Verified

### Clause: delivery_terms
- **Clause**: delivery_terms
- **Reason Mandatory**: Defines shipping, delivery, and risk transfer terms (Incoterms).
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: warranty
- **Clause**: warranty
- **Reason Mandatory**: Provides performance or product quality warranties.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: KUH Perdata (Indonesian Civil Code) Article Pasal 1320, Pasal 1338 (ID)
- **Evidence Status**: Repository Verified

### Clause: title_transfer
- **Clause**: title_transfer
- **Reason Mandatory**: Specifies when ownership of goods transfers to the buyer.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Uniform Commercial Code Article UCC 2-401 (generic), French Code civil Article Art. 1583 (FR), KUHPerdata Article Pasal 1459 (ID)
- **Evidence Status**: Repository Verified

### Clause: dispute_resolution
- **Clause**: dispute_resolution
- **Reason Mandatory**: Establishes the process (litigation, arbitration, mediation) for resolving disputes.
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
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
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Indonesian statute (UU) Article UU No. 40 Tahun 2014 tentang Perasuransian, KUHPerdata Article Pasal 1636
- **Evidence Status**: Repository Verified

### Jurisdiction: Belgium
- **Jurisdiction**: Belgium
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Belgian Civil Code, Book 5 Article Art. 5.88, Belgian Civil Code, Book 5 Article Art. 5.51
- **Evidence Status**: Repository Verified

### Jurisdiction: France
- **Jurisdiction**: France
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: French Code civil Article Art. 1224, French Code civil Article Art. 2288
- **Evidence Status**: Repository Verified

### Jurisdiction: Netherlands
- **Jurisdiction**: Netherlands
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: England & Wales
- **Jurisdiction**: England & Wales
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
- **Legal Reference**: Evidence Not Found
- **Evidence Status**: Evidence Not Found

### Jurisdiction: United States
- **Jurisdiction**: United States
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
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

### Clause Mapping: goods_description
- **Law / Code**: Uniform Commercial Code
- **Article**: UCC 2-201
- **Official Citation / Note**: Description of goods is required for sale validity
- **Repository Mapping**: Mapped to clause 'goods_description' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: goods_description
- **Law / Code**: French Code civil
- **Article**: Art. 1583
- **Official Citation / Note**: La vente est parfaite dès qu'on est convenu de la chose
- **Repository Mapping**: Mapped to clause 'goods_description' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: goods_description
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1457
- **Official Citation / Note**: Jual beli memerlukan penentuan barang yang dijual
- **Repository Mapping**: Mapped to clause 'goods_description' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: payment_terms
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1234
- **Official Citation / Note**: KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
- **Repository Mapping**: Mapped to clause 'payment_terms' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: delivery_terms
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
- **Repository Mapping**: Mapped to clause 'delivery_terms' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: warranty
- **Law / Code**: KUH Perdata (Indonesian Civil Code)
- **Article**: Pasal 1320, Pasal 1338
- **Official Citation / Note**: Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
- **Repository Mapping**: Mapped to clause 'warranty' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: title_transfer
- **Law / Code**: Uniform Commercial Code
- **Article**: UCC 2-401
- **Official Citation / Note**: Title transfers upon physical delivery unless agreed
- **Repository Mapping**: Mapped to clause 'title_transfer' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: title_transfer
- **Law / Code**: French Code civil
- **Article**: Art. 1583
- **Official Citation / Note**: Le transfert de propriété s'opère par l'accord sur la chose
- **Repository Mapping**: Mapped to clause 'title_transfer' in ldv-backend/detector/detector_rules.py
- **Evidence Status**: Repository Verified

### Clause Mapping: title_transfer
- **Law / Code**: KUHPerdata
- **Article**: Pasal 1459
- **Official Citation / Note**: Hak milik atas barang tidak pindah sebelum penyerahan
- **Repository Mapping**: Mapped to clause 'title_transfer' in ldv-backend/detector/detector_rules.py
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

- **Verified Repository Alias**: purchase agreement, sale agreement, sales contract, perjanjian pembelian
- **Draft Alias**: perjanjian jual beli, contrat de vente, koopovereenkomst
- **Unsupported Alias**: Evidence Not Found

### Language Breakdown
- **English**: purchase agreement, sales contract, sale agreement
- **Indonesian**: perjanjian jual beli, perjanjian pembelian
- **French**: contrat de vente
- **Dutch**: koopovereenkomst

## 8. Competing Contract Types
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: competing_profiles NLI overrides
- **Evidence Status**: Repository Verified

- **Competing Profiles**: commercial_agreement, general_contract
- **Why They Compete**: Overlap in transactional transfers of property or supply arrangements.
- **How They Differ**: A purchase agreement is legally defined by the transfer of title and ownership of specific tangible goods or assets in exchange for price. A service agreement transfers the utility of labor, and a commercial agreement covers broader distribution or trade partnerships.
- **Classifier Distinction Strategy**: Verify if the core obligation is the transfer of title to physical goods (purchase agreement) as opposed to the execution of services or ongoing commercial relations.

## 9. Disambiguation Criteria
- **Repository Source**: ldv-backend/detector/profiles/registry_v1.json
- **Repository Object**: nli_hypothesis distinction
- **Evidence Status**: Repository Verified

- **Disambiguation Criteria**: A purchase agreement is legally defined by the transfer of title and ownership of specific tangible goods or assets in exchange for price. A service agreement transfers the utility of labor, and a commercial agreement covers broader distribution or trade partnerships. (commercial and legal separation from competing profiles: commercial_agreement, general_contract).

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
- **Repository Source**: ldv-backend/detector/profiles/purchase_agreement.json
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
