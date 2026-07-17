# Contract Risk Analyzer (CRA) — Profile Legal Engineering Documentation

> [!IMPORTANT]
> **Legal Disclaimer & Status Notice:** All validation statuses and dates in this document reflect engineering metadata and system verification runs. No contract profiles in this document have been formally signed off as legally approved by a human legal reviewer unless explicitly noted. All legal reviewer fields are marked as Pending.

## Table of Contents
- [Commercial Agreement (#commercial_agreement)](#commercial_agreement)
- [Construction Agreement (#construction_agreement)](#construction_agreement)
- [Consulting Agreement (#consulting_agreement)](#consulting_agreement)
- [Employment Contract (#employment_contract)](#employment_contract)
- [General Contract (#general_contract)](#general_contract)
- [Insurance Agreement (#insurance_agreement)](#insurance_agreement)
- [IT Service Agreement (#it_service_agreement)](#it_service_agreement)
- [Lease Agreement (#lease_agreement)](#lease_agreement)
- [Loan Agreement (#loan_agreement)](#loan_agreement)
- [Non-Disclosure Agreement (#non_disclosure_agreement)](#non_disclosure_agreement)
- [Partnership Agreement (#partnership_agreement)](#partnership_agreement)
- [Purchase Agreement (#purchase_agreement)](#purchase_agreement)
- [SaaS Agreement (#saas_agreement)](#saas_agreement)
- [Service Agreement (#service_agreement)](#service_agreement)
- [Software License (#software_license)](#software_license)

---

## Commercial Agreement <a name="commercial_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `commercial_agreement`
2. **Display Name**: Commercial Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: commercial agreement, business agreement, trade agreement
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Commercial Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "commercial agreement", "business agreement", "trade agreement"
- **Positive body indicators**:
  - EN: commercial, business
  - ID: komersial, bisnis
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "general_contract", "purchase_agreement", "service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - commercial agreement, business agreement, trade agreement
- **Closely competing contract types**: `general_contract`, `purchase_agreement`, `service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A general commercial agreement covers trade, business operations, and supply terms between businesses, more specific than general contracts but broader than dedicated purchase or service agreements.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `commercial_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `commercial_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `commercial_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Construction Agreement <a name="construction_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `construction_agreement`
2. **Display Name**: Construction Agreement
3. **Contract Family**: `property_agreements`
4. **Known Aliases**: construction agreement, building contract, aannemingsovereenkomst
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`, `scope_of_services`, `warranty`, `indemnification`, `insurance`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `scope_of_services` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `warranty` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `indemnification` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `insurance` (ID): Indonesian statute (UU) UU No. 40 Tahun 2014 tentang Perasuransian - UU No. 40 Tahun 2014 tentang Perasuransian; ketentuan polis dan perjanjian yang berlaku.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-14. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Construction, building, and engineering contract profile.
- **Positive title indicators**: Draft Suggestion - Contains words like "construction agreement", "building contract", "aannemingsovereenkomst"
- **Positive body indicators**:
  - EN: construction, building contract, contractor, engineering work, drawings, specifications
  - ID: konstruksi, pembangunan, kontraktor, pekerjaan sipil
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "lease_agreement", "general_contract")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - construction agreement, building contract, aannemingsovereenkomst
- **Closely competing contract types**: `lease_agreement`, `general_contract`
- **Legal disambiguation criteria**: Draft Suggestion - A construction agreement governs building, renovation, or infrastructure work, distinct from real estate leases or simple purchase agreements.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `construction_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `construction_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `construction_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Consulting Agreement <a name="consulting_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `consulting_agreement`
2. **Display Name**: Consulting Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: consulting agreement, consultancy agreement, advisory agreement
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `confidentiality`, `termination`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `scope_of_services` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `confidentiality` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 2000 tentang Rahasia Dagang - UU No. 30 Tahun 2000 tentang Rahasia Dagang; Pasal 1338 KUH Perdata; ketentuan wanprestasi KUH Perdata.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Consulting Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "consulting agreement", "consultancy agreement", "advisory agreement"
- **Positive body indicators**:
  - EN: consulting, consultant, advisory, services
  - ID: konsultan, konsultasi, penasihat, jasa
  - FR: consultant, conseil, prestations, accord de conseil
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "employment_contract", "service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - consulting agreement, consultancy agreement, advisory agreement
- **Closely competing contract types**: `employment_contract`, `service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A consulting agreement is characterized by independent service provision for a specific project or professional expertise without the subordination typical of employment.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `consulting_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `consulting_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `consulting_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Employment Contract <a name="employment_contract"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `employment_contract`
2. **Display Name**: Employment Contract
3. **Contract Family**: `employment_agreements`
4. **Known Aliases**: employment contract, labor contract, perjanjian kerja
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `termination`, `notice_period`, `compensation`, `working_hours`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `compensation` (ID): Indonesian statute (UU) UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023 - UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023; peraturan ketenagakerjaan terkait.
    - `working_hours` (ID): Indonesian statute (UU) UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023 - UU No. 13 Tahun 2003 tentang Ketenagakerjaan sebagaimana diubah melalui UU No. 6 Tahun 2023; peraturan ketenagakerjaan terkait.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Employment Contract profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "employment contract", "labor contract", "perjanjian kerja"
- **Positive body indicators**:
  - EN: employee, employer, employment, salary, wages, worker, work promise
  - ID: karyawan, majikan, gaji, pekerja, pemberi kerja, perjanjian kerja
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "consulting_agreement", "service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - employment contract, labor contract, perjanjian kerja
- **Closely competing contract types**: `consulting_agreement`, `service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - An employment contract establishes an employer-employee relationship characterized by subordination and direction, whereas service/consulting agreements involve independent parties without structural hierarchy.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `employment_contract`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `employment_contract`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `employment_contract`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## General Contract <a name="general_contract"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `general_contract`
2. **Display Name**: General Contract
3. **Contract Family**: `baseline_agreements`
4. **Known Aliases**: general contract, contract, agreement, perjanjian, kontrak
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard General Contract profile mapping required baseline clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "general contract", "contract", "agreement", "perjanjian", "kontrak"
- **Positive body indicators**:
  - Insufficient source material (no keyword overrides specified)
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "commercial_agreement", "service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - general contract, contract, agreement, perjanjian, kontrak
- **Closely competing contract types**: `commercial_agreement`, `service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A general contract is a baseline agreement used when the transaction does not fit into any specialized contract category.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `general_contract`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `general_contract`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `general_contract`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Insurance Agreement <a name="insurance_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `insurance_agreement`
2. **Display Name**: Insurance Agreement
3. **Contract Family**: `baseline_agreements`
4. **Known Aliases**: insurance agreement, insurance policy, verzekeringsovereenkomst
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`, `default_provisions`, `notice_period`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `default_provisions` (generic): general law Default provisions - Default clauses set the grounds for breach
    - `default_provisions` (FR): French Code civil Art. 1224 - La résolution résulte soit d'une clause résolutoire
    - `default_provisions` (ID): KUHPerdata Pasal 1238 - Wanprestasi memerlukan adanya pernyataan lalai
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-14. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard insurance policy or coverage agreement profile.
- **Positive title indicators**: Draft Suggestion - Contains words like "insurance agreement", "insurance policy", "verzekeringsovereenkomst"
- **Positive body indicators**:
  - EN: insurance policy, insurance agreement, premium payment, insurer, insured
  - ID: asuransi, polis asuransi, premi
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "general_contract")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - insurance agreement, insurance policy, verzekeringsovereenkomst
- **Closely competing contract types**: `general_contract`
- **Legal disambiguation criteria**: Draft Suggestion - An insurance agreement governs risk transfer and premium payment, distinct from indemnity clauses in standard commercial agreements.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `insurance_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `insurance_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `insurance_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## IT Service Agreement <a name="it_service_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `it_service_agreement`
2. **Display Name**: IT Service Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: it service agreement, it services agreement, information technology services contract
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`, `scope_of_services`, `confidentiality`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `scope_of_services` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `confidentiality` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 2000 tentang Rahasia Dagang - UU No. 30 Tahun 2000 tentang Rahasia Dagang; Pasal 1338 KUH Perdata; ketentuan wanprestasi KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-14. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Information Technology service agreement profile.
- **Positive title indicators**: Draft Suggestion - Contains words like "it service agreement", "it services agreement", "information technology services contract"
- **Positive body indicators**:
  - EN: it service, it services, it support, information technology services
  - ID: layanan ti, jasa ti, teknologi informasi
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "service_agreement", "saas_agreement", "software_license")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - it service agreement, it services agreement, information technology services contract
- **Closely competing contract types**: `service_agreement`, `saas_agreement`, `software_license`
- **Legal disambiguation criteria**: Draft Suggestion - An IT service agreement is specialized for technical services, service level agreements (SLAs), and infrastructure management, whereas general service agreements cover non-technical tasks.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `it_service_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `it_service_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `it_service_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Lease Agreement <a name="lease_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `lease_agreement`
2. **Display Name**: Lease Agreement
3. **Contract Family**: `property_agreements`
4. **Known Aliases**: lease agreement, rental agreement, tenancy agreement, perjanjian sewa
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `lease_term`, `rent_amount`, `security_deposit`, `maintenance_responsibility`, `termination`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `lease_term` (generic): French civil-style code Art. 1709 - Lease term must be defined or determinable
    - `lease_term` (FR): French Code civil Art. 1709 - Le contrat de louage doit être conclu pour un temps certain
    - `lease_term` (ID): KUHPerdata Pasal 1548 - Perjanjian sewa-menyewa dibuat untuk waktu tertentu
    - `rent_amount` (generic): French civil-style code Art. 1709 - Rent amount must be agreed by both parties
    - `rent_amount` (FR): French Code civil Art. 1709 - Le bail exige l'obligation de payer un prix certain
    - `rent_amount` (ID): KUHPerdata Pasal 1548 - Penyewa wajib membayar suatu harga sewa tertentu
    - `security_deposit` (generic): French civil-style code Art. 2288 - Security deposit is a caution/pledge contract
    - `security_deposit` (FR): French Code civil Art. 2288 - Dépôt de garantie ou cautionnement de obligations
    - `security_deposit` (ID): KUHPerdata Pasal 1820 - Penanggungan utang atau jaminan uang deposit sewa
    - `maintenance_responsibility` (generic): French civil-style code Art. 1719 - Landlord must maintain the leased premises
    - `maintenance_responsibility` (FR): French Code civil Art. 1719 - Le bailleur est obligé d'entretenir la chose louée
    - `maintenance_responsibility` (ID): KUHPerdata Pasal 1550 - Pemberi sewa wajib memelihara barang sewaan
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Lease Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "lease agreement", "rental agreement", "tenancy agreement", "perjanjian sewa"
- **Positive body indicators**:
  - EN: lease, tenant, landlord, rent, rental
  - ID: sewa, penyewa, pemilik, uang sewa
  - FR: bail, locataire, bailleur, loyer
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "construction_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - lease agreement, rental agreement, tenancy agreement, perjanjian sewa
- **Closely competing contract types**: `construction_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A lease agreement grants temporary possession and use of real or personal property in exchange for periodic rent, distinguished from sales or construction agreements.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `lease_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `lease_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `lease_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Loan Agreement <a name="loan_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `loan_agreement`
2. **Display Name**: Loan Agreement
3. **Contract Family**: `corporate_agreements`
4. **Known Aliases**: loan agreement, loan contract, creditor agreement, perjanjian pinjaman
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `principal_amount`, `interest_rate`, `repayment_schedule`, `default_provisions`, `termination`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `principal_amount` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `interest_rate` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `repayment_schedule` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `default_provisions` (generic): general law Default provisions - Default clauses set the grounds for breach
    - `default_provisions` (FR): French Code civil Art. 1224 - La résolution résulte soit d'une clause résolutoire
    - `default_provisions` (ID): KUHPerdata Pasal 1238 - Wanprestasi memerlukan adanya pernyataan lalai
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Loan Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "loan agreement", "loan contract", "creditor agreement", "perjanjian pinjaman"
- **Positive body indicators**:
  - EN: loan, lender, borrower, principal, interest
  - ID: pinjaman, pemberi pinjaman, penerima pinjaman, bunga
  - FR: prêt, prêteur, emprunteur, principal, intérêt
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "commercial_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - loan agreement, loan contract, creditor agreement, perjanjian pinjaman
- **Closely competing contract types**: `commercial_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A loan agreement governs the lending of principal funds from a lender to a borrower with repayment terms and interest, distinct from trade finance or equity investment.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `loan_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `loan_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `loan_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Non-Disclosure Agreement <a name="non_disclosure_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `non_disclosure_agreement`
2. **Display Name**: Non-Disclosure Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: non-disclosure agreement, NDA, confidentiality agreement, geheimhouding
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `confidentiality`, `termination`, `return_of_materials`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `confidentiality` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 2000 tentang Rahasia Dagang - UU No. 30 Tahun 2000 tentang Rahasia Dagang; Pasal 1338 KUH Perdata; ketentuan wanprestasi KUH Perdata.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `return_of_materials` (generic): general law Return of materials - NDA property return/destruction obligations are standard
    - `return_of_materials` (FR): French Code civil Art. 1134 - Les conventions légalement formées tiennent lieu de loi
    - `return_of_materials` (ID): KUHPerdata Pasal 1338 - Persetujuan yang dibuat secara sah berlaku sebagai undang-undang
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Non-Disclosure Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "non-disclosure agreement", "NDA", "confidentiality agreement", "geheimhouding"
- **Positive body indicators**:
  - EN: disclosure, confidential, confidentiality, NDA, receiving party
  - ID: kerahasiaan, rahasia, dwibahasa, penerima informasi
  - FR: confidentialité, informations confidentielles, partie réceptrice
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "general_contract")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - non-disclosure agreement, NDA, confidentiality agreement, geheimhouding
- **Closely competing contract types**: `general_contract`
- **Legal disambiguation criteria**: Draft Suggestion - An NDA specifically protects proprietary information and trade secrets from unauthorized disclosure, distinct from broader commercial agreements which may only contain confidentiality clauses as subsidiary terms.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `non_disclosure_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `non_disclosure_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `non_disclosure_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Partnership Agreement <a name="partnership_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `partnership_agreement`
2. **Display Name**: Partnership Agreement
3. **Contract Family**: `corporate_agreements`
4. **Known Aliases**: partnership agreement, partnership contract, joint venture
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `capital_contribution`, `profit_sharing`, `management_rights`, `termination`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `capital_contribution` (generic): French civil-style code Art. 1832 - Partners must contribute capital or industry
    - `capital_contribution` (FR): French Code civil Art. 1832 - Les associés conviennent d'apporter des biens ou leur industrie
    - `capital_contribution` (ID): KUHPerdata Pasal 1618 - Setiap sekutu wajib memasukkan modal ke persekutuan
    - `profit_sharing` (generic): French civil-style code Art. 1832 - Partners must share profits and losses
    - `profit_sharing` (FR): French Code civil Art. 1832 - Les associés partagent le bénéfice ou profit et les pertes
    - `profit_sharing` (ID): KUHPerdata Pasal 1618 - Pembagian untung dan rugi diatur berdasarkan kontribusi modal
    - `management_rights` (generic): general law Management rights - Management and voting rights govern the partnership
    - `management_rights` (FR): French Code civil Art. 1852 - Les associés prennent les décisions collectives de gestion
    - `management_rights` (ID): KUHPerdata Pasal 1636 - Pengurus persekutuan ditunjuk untuk mengelola hubungan usaha
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Partnership Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "partnership agreement", "partnership contract", "joint venture"
- **Positive body indicators**:
  - EN: partnership, partner, contribution, capital
  - ID: kemitraan, mitra, sekutu, modal
  - FR: partenariat, associé, apport, capital
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "joint_venture_agreement", "commercial_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - partnership agreement, partnership contract, joint venture
- **Closely competing contract types**: `joint_venture_agreement`, `commercial_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A partnership agreement establishes a co-ownership structure to share profits and losses of a business venture, distinct from joint ventures which are often project-specific.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `partnership_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `partnership_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `partnership_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Purchase Agreement <a name="purchase_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `purchase_agreement`
2. **Display Name**: Purchase Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: purchase agreement, sale agreement, sales contract, perjanjian pembelian
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `goods_description`, `payment_terms`, `delivery_terms`, `warranty`, `title_transfer`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `goods_description` (generic): Uniform Commercial Code UCC 2-201 - Description of goods is required for sale validity
    - `goods_description` (FR): French Code civil Art. 1583 - La vente est parfaite dès qu'on est convenu de la chose
    - `goods_description` (ID): KUHPerdata Pasal 1457 - Jual beli memerlukan penentuan barang yang dijual
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `delivery_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `warranty` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `title_transfer` (generic): Uniform Commercial Code UCC 2-401 - Title transfers upon physical delivery unless agreed
    - `title_transfer` (FR): French Code civil Art. 1583 - Le transfert de propriété s'opère par l'accord sur la chose
    - `title_transfer` (ID): KUHPerdata Pasal 1459 - Hak milik atas barang tidak pindah sebelum penyerahan
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Purchase Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "purchase agreement", "sale agreement", "sales contract", "perjanjian pembelian"
- **Positive body indicators**:
  - EN: purchase, sale, buyer, seller, goods
  - ID: pembelian, penjualan, pembeli, penjual, barang
  - FR: achat, vente, acheteur, vendeur, marchandises
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "commercial_agreement", "general_contract")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - purchase agreement, sale agreement, sales contract, perjanjian pembelian
- **Closely competing contract types**: `commercial_agreement`, `general_contract`
- **Legal disambiguation criteria**: Draft Suggestion - A purchase agreement specifically governs the transfer of ownership of physical goods or assets in exchange for payment, distinguished from service agreements.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `purchase_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `purchase_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `purchase_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## SaaS Agreement <a name="saas_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `saas_agreement`
2. **Display Name**: SaaS Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: saas agreement, software as a service agreement, cloud service agreement
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability`, `license_grant`, `ip_ownership`, `warranty_disclaimer`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `license_grant` (generic): general law IP usage license - License grant defines permissions and boundaries
    - `license_grant` (FR): French Code de la propriété intellectuelle Art. L122-4 - Toute représentation ou reproduction intégrale ou partielle requiert autorisation
    - `license_grant` (ID): UU Hak Cipta UU No. 28 Tahun 2014 - Lisensi hak cipta harus dibuat secara tertulis
    - `ip_ownership` (generic): general law IP ownership rules - Ownership of IP remains with creator unless assigned
    - `ip_ownership` (FR): French Code de la propriété intellectuelle Art. L111-1 - L'auteur jouit d'un droit de propriété incorporelle exclusif
    - `ip_ownership` (ID): UU Hak Cipta UU No. 28 Tahun 2014 - Hak milik kekayaan intelektual dilindungi oleh undang-undang
    - `warranty_disclaimer` (generic): Uniform Commercial Code UCC 2-316 - Disclaimers of implied warranties must be conspicuous
    - `warranty_disclaimer` (FR): French Code civil Art. 1643 - Exclusion de garantie des vices cachés possible si convenue
    - `warranty_disclaimer` (ID): KUHPerdata Pasal 1491 - Penyangkalan jaminan cacat tersembunyi dapat disepakati
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-14. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Software-as-a-Service profile.
- **Positive title indicators**: Draft Suggestion - Contains words like "saas agreement", "software as a service agreement", "cloud service agreement"
- **Positive body indicators**:
  - EN: saas, software as a service, cloud service, subscription fee, cloud agreement
  - ID: saas, layanan awan, berlangganan perangkat lunak
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "software_license", "it_service_agreement", "service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - saas agreement, software as a service agreement, cloud service agreement
- **Closely competing contract types**: `software_license`, `it_service_agreement`, `service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A SaaS agreement licenses access to hosted software as a service without transferring physical media or intellectual property rights, whereas a software license usually involves installation or redistribution rights.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `saas_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `saas_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `saas_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Service Agreement <a name="service_agreement"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `service_agreement`
2. **Display Name**: Service Agreement
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: service agreement, services agreement, master services agreement, MSA
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `scope_of_services` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `payment_terms` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1234 - KUH Perdata tentang perikatan dan pembayaran (termasuk Pasal 1234 dan seterusnya); regulasi sektor terkait jika berlaku.
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Service Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "service agreement", "services agreement", "master services agreement", "MSA"
- **Positive body indicators**:
  - EN: services, client, contractor, provider
  - ID: jasa, perjanjian jasa, pemberi jasa
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "consulting_agreement", "employment_contract", "it_service_agreement", "saas_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - service agreement, services agreement, master services agreement, MSA
- **Closely competing contract types**: `consulting_agreement`, `employment_contract`, `it_service_agreement`, `saas_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A service agreement governs the provision of general services by an independent contractor, distinguished from employment by the lack of direct employer control and typical corporate benefits.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `service_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `service_agreement`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `service_agreement`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

## Software License <a name="software_license"></a>

### 1. Legal Engineering Metadata
1. **Profile ID**: `software_license`
2. **Display Name**: Software License
3. **Contract Family**: `commercial_agreements`
4. **Known Aliases**: software license, license agreement, EULA, softwarelicentie
5. **Mandatory Clauses**: `governing_law`, `jurisdiction_venue`, `license_grant`, `ip_ownership`, `limitation_liability`, `warranty_disclaimer`, `termination`, `dispute_resolution`
6. **Recommended Clauses**: Insufficient source material
7. **Dangerous Clauses**: Insufficient source material
8. **Abusive Clauses**: Insufficient source material
9. **Illegal Clauses**: Insufficient source material
10. **Leonine Clauses**: Insufficient source material
11. **Jurisdictions**: Indonesia, Belgium, France, Netherlands, England & Wales, United States
12. **Legal References**:
    - `governing_law` (generic):   - Absence of a governing-law clause creates conflict-of-laws uncertainty over the applicable law
    - `governing_law` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338 - Pasal 1338 KUH Perdata (kebebasan berkontrak); hukum yang dipilih para pihak sepanjang tidak bertentangan dengan hukum yang berlaku.
    - `license_grant` (generic): general law IP usage license - License grant defines permissions and boundaries
    - `license_grant` (FR): French Code de la propriété intellectuelle Art. L122-4 - Toute représentation ou reproduction intégrale ou partielle requiert autorisation
    - `license_grant` (ID): UU Hak Cipta UU No. 28 Tahun 2014 - Lisensi hak cipta harus dibuat secara tertulis
    - `ip_ownership` (generic): general law IP ownership rules - Ownership of IP remains with creator unless assigned
    - `ip_ownership` (FR): French Code de la propriété intellectuelle Art. L111-1 - L'auteur jouit d'un droit de propriété incorporelle exclusif
    - `ip_ownership` (ID): UU Hak Cipta UU No. 28 Tahun 2014 - Hak milik kekayaan intelektual dilindungi oleh undang-undang
    - `limitation_liability` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1243, Pasal 1365 - KUH Perdata mengenai ganti rugi dan wanprestasi (Pasal 1243 dan seterusnya); Pasal 1365 KUH Perdata untuk perbuatan melawan hukum.
    - `warranty_disclaimer` (generic): Uniform Commercial Code UCC 2-316 - Disclaimers of implied warranties must be conspicuous
    - `warranty_disclaimer` (FR): French Code civil Art. 1643 - Exclusion de garantie des vices cachés possible si convenue
    - `warranty_disclaimer` (ID): KUHPerdata Pasal 1491 - Penyangkalan jaminan cacat tersembunyi dapat disepakati
    - `termination` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1320, Pasal 1338 - Pasal 1320 dan Pasal 1338 KUH Perdata tentang syarat sah perjanjian dan kebebasan berkontrak; prinsip umum hukum kontrak.
    - `dispute_resolution` (generic):   - Without a dispute-resolution clause, parties default to ordinary court litigation
    - `dispute_resolution` (ID): KUH Perdata (Indonesian Civil Code) Pasal 1338, UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa - UU No. 30 Tahun 1999 tentang Arbitrase dan Alternatif Penyelesaian Sengketa; HIR/RBg untuk litigasi; Pasal 1338 KUH Perdata.
13. **Score Weights**: Pending (uses global uncalibrated `default_v1` policy weights: CRITICAL=-20, HIGH=-15, MEDIUM=-10, LOW=-5)
14. **Recommendation Wording**: Pending
15. **Supported Languages**: EN, ID, FR
16. **Legal Reviewer**: Pending
17. **Validation Status**: Pending (Engineering: Validated)
18. **Comments**: This profile is marked as 'Validated' in the system registry configuration on date 2026-07-13. Formal external legal reviewer sign-off is pending.
19. **Approval Date**: Pending

### 2. Detection Specification
- **Contract definition**: Draft Suggestion - Standard Software License Agreement profile mapping required clauses.
- **Positive title indicators**: Draft Suggestion - Contains words like "software license", "license agreement", "EULA", "softwarelicentie"
- **Positive body indicators**:
  - EN: software, license, licensor, licensee, EULA
  - ID: perangkat lunak, lisensi, lisensor, penerima lisensi
  - FR: logiciel, licence, concédant, licencié
- **Negative indicators**: Draft Suggestion - Presence of core terminology from competing types (e.g., "saas_agreement", "it_service_agreement")
- **Aliases (EN, ID, FR, NL)**: Draft Suggestion - software license, license agreement, EULA, softwarelicentie
- **Closely competing contract types**: `saas_agreement`, `it_service_agreement`
- **Legal disambiguation criteria**: Draft Suggestion - A software license grants permission to use, modify, or distribute software code, often installed locally, distinct from SaaS which is hosted and accessed via a browser/API.

### 3. Proposed Test Fixtures
> [!NOTE]
> The following test fixtures are proposed specifications for testing and validation. No execution evidence is provided for these specific scenarios.

#### Fixture 1: Normal Contract
- **Expected Contract Type**: `software_license`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: None
- **Expected Severity**: Informational / Safe
- **Expected Score Range**: 90 - 100
- **Expected Legal References**: None (no risk findings)

#### Fixture 2: Missing Mandatory Clause Contract
- **Expected Contract Type**: `software_license`
- **Expected Missing Clauses**: `['governing_law']`
- **Expected Detected Risks**: Missing required clause `governing_law`
- **Expected Severity**: Medium / High (depending on clause category)
- **Expected Score Range**: 70 - 89
- **Expected Legal References**: KUH Perdata (Indonesian Civil Code) Pasal 1338

#### Fixture 3: Risky or Unbalanced Contract
- **Expected Contract Type**: `software_license`
- **Expected Missing Clauses**: None
- **Expected Detected Risks**: Unilateral Change or Excessive Penalty or Unlimited Liability
- **Expected Severity**: High / Critical
- **Expected Score Range**: 40 - 69
- **Expected Legal References**: KUHPerdata Pasal 1309 / French Code civil Art. 1231-5 (Excessive Penalty); Art. 1844-1 (Leonine)

---

