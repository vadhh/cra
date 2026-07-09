# Multilingual Fixture Manifest

This document maps all the test fixtures used in the Contract Risk Analyzer (CRA) offline multilingual validation suite ([run_offline_validation.py](file:///home/stardhoom/LDV/ldv-backend/tests/run_offline_validation.py)). 

It outlines the expected language, document type, contract classification, and the exact presence/absence ground-truth requirements verified by the quality check checks.

---

## 1. Core Multilingual Quality Fixtures (Layer 2 NLI & Layer 3 Scorer)

These documents exercise the core extraction, translation, document-type classification, and clause-presence checks.

### 1.1. Indonesian Employment Contract
*   **File Path**: [pdf/01_employment_id.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/pdf/01_employment_id.pdf) (derived from [txt/01_employment_id.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/01_employment_id.txt))
*   **Expected Language**: `id` (Indonesian)
*   **Expected Contract Type**: `employment contract` (`is_contract = True`)
*   **Expected Present Clauses**:
    - `governing_law` (checks for Indonesian Labor Law references)
    - `termination` (provisions for employee exit)
    - `working_hours` (work hour details)
    - `compensation` (salary details)
*   **Expected Missing Clauses**:
    - `jurisdiction_venue`
    - `notice_period`
    - `dispute_resolution`

### 1.2. Belgian French Lease Agreement
*   **File Path**: [pdf/02_lease_be.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/pdf/02_lease_be.pdf) (derived from [txt/02_lease_be.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/02_lease_be.txt))
*   **Expected Language**: `fr` (French)
*   **Expected Contract Type**: `lease agreement` (`is_contract = True`)
*   **Expected Present Clauses**:
    - `governing_law` (Belgian Civil Code)
    - `termination` (termination with 3 months' notice)
    - `rent_amount` (rent details)
    - `security_deposit` (security deposit of 2 months' rent)
    - `lease_term` (explicit 3-year term)
*   **Expected Missing Clauses**:
    - `jurisdiction_venue`
    - `maintenance_responsibility`
    - `dispute_resolution`

### 1.3. English Non-Disclosure Agreement (NDA)
*   **File Path**: [pdf/03_nda_en.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/pdf/03_nda_en.pdf) (derived from [txt/14_low_risk_nda_en.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/14_low_risk_nda_en.txt))
*   **Expected Language**: `en` (English)
*   **Expected Contract Type**: `non-disclosure agreement` (`is_contract = True`)
*   **Expected Present Clauses**:
    - `governing_law` (Laws of England and Wales)
    - `termination` (added explicitly to exercise detection)
    - `confidentiality` (core confidentiality covenant)
*   **Expected Missing Clauses**:
    - `jurisdiction_venue`
    - `return_of_materials`
    - `dispute_resolution`

---

## 2. Basic Language & Contract Type Validation Fixtures

These fixtures verify that the pipeline correctly extracts and classifies document meta-parameters without requiring detailed clause checks.

### 2.1. French Employment Document
*   **File Path**: [docx/02_employment_fr.docx](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/docx/02_employment_fr.docx)
*   **Expected Language**: `fr` (French)
*   **Expected Contract Type**: `employment contract` (`is_contract = True`)

### 2.2. Dutch NDA Document
*   **File Path**: [docx/03_nda_nl.docx](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/docx/03_nda_nl.docx)
*   **Expected Language**: `nl` (Dutch)
*   **Expected Contract Type**: `non-disclosure agreement` (`is_contract = True`, resolved via keyword fallback on *Geheimhoudingsovereenkomst*)

### 2.3. Indonesian Unilateral Risk Document
*   **File Path**: [txt/12_high_risk_unilateral_id.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/12_high_risk_unilateral_id.txt)
*   **Expected Language**: `id` (Indonesian)
*   **Expected Contract Type**: `service agreement` (`is_contract = True`)

### 2.4. Dutch Lease Document
*   **File Path**: [txt/13_medium_risk_lease_nl.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/13_medium_risk_lease_nl.txt)
*   **Expected Language**: `nl` (Dutch)
*   **Expected Contract Type**: `lease agreement` (`is_contract = True`)

---

## 3. Negative & Non-Contract Validation Fixtures

These fixtures ensure the pipeline does not raise false positives or classify non-contracts as agreements.

### 3.1. English Brochure
*   **File Path**: [pdf/05_brochure_en.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/pdf/05_brochure_en.pdf)
*   **Expected Language**: `en` (English)
*   **Expected Outcome**: `is_contract = False` (No analysis performed downstream)

### 3.2. French Internal Memo
*   **File Path**: [docx/06_memo_fr.docx](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/docx/06_memo_fr.docx)
*   **Expected Language**: `fr` (French)
*   **Expected Outcome**: `is_contract = False` (No analysis performed downstream)

### 3.3. Dutch Product Brochure
*   **File Path**: [docx/07_brochure_nl.docx](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/docx/07_brochure_nl.docx)
*   **Expected Language**: `nl` (Dutch)
*   **Expected Outcome**: `is_contract = False` (No analysis performed downstream)

### 3.4. Indonesian Business Notice
*   **File Path**: [txt/16_notice_id.txt](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/txt/16_notice_id.txt)
*   **Expected Language**: `id` (Indonesian)
*   **Expected Outcome**: `is_contract = False` (No analysis performed downstream)

---

## 4. Exception Handling & Edge-Case Fixtures

These verify robust system degradation under malformed, blank, or scanned document inputs.

### 4.1. Scanned Blank PDF
*   **File Path**: [pdf/06_scanned_blank_en.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/pdf/06_scanned_blank_en.pdf)
*   **Expected Behavior**: Raises `ScanRequired` warning or exception (identifies absence of digital text layer, requesting OCR fallback).

### 4.2. Empty Stream PDF
*   **File Path**: [negative/empty.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/negative/empty.pdf)
*   **Expected Behavior**: Raises graceful extraction warning (`Cannot open empty stream.`), returning HTTP 400.

### 4.3. Malformed PDF
*   **File Path**: [negative/fake.pdf](file:///home/stardhoom/LDV/ldv-backend/tests/fixtures/negative/fake.pdf)
*   **Expected Behavior**: Raises graceful format loading exception (`Failed to open stream`), returning HTTP 400.
