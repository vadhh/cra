# PT Sydeco Contract Risk Analyzer - Legal Benchmark Report

## 1. Overview Summary Metrics
*   **Language Detection Accuracy**: 100.0%
*   **Jurisdiction Classification Accuracy**: 100.0%
*   **Contract Classification Accuracy**: 100.0%
*   **Clause Presence Detection Accuracy**: 80.8%
*   **Clause Detection Precision**: 75.0% (Avoidance of false positives)
*   **Clause Detection Recall**: 81.8% (Avoidance of false negatives)

## 2. Clause Matching Details
*   **True Positives (TP)**: 9 (Expected present, detected present)
*   **True Negatives (TN)**: 12 (Expected missing, detected missing)
*   **False Positives (FP)**: 3 (Expected missing, detected present)
*   **False Negatives (FN)**: 2 (Expected present, detected missing)

## 3. Fixture Analysis Log

### `pdf/01_employment_id.pdf`
*   **Language**: Detected `id`, Match: `🟢 PASS`
*   **Jurisdiction**: Detected `Indonesia`, Match: `🟢 PASS`
*   **Document Type**: Detected `employment contract`, Match: `🟢 PASS`
*   **Clause Verification Details**:
    - `governing_law`: 🟢 True Positive
    - `termination`: 🟢 True Positive
    - `working_hours`: 🟢 True Positive
    - `compensation`: 🟢 True Positive
    - `jurisdiction_venue`: 🟢 True Negative
    - `notice_period`: 🟢 True Negative
    - `dispute_resolution`: 🟢 True Negative

### `pdf/02_lease_be.pdf`
*   **Language**: Detected `fr`, Match: `🟢 PASS`
*   **Jurisdiction**: Detected `Belgium`, Match: `🟢 PASS`
*   **Document Type**: Detected `lease agreement`, Match: `🟢 PASS`
*   **Clause Verification Details**:
    - `governing_law`: 🔴 False Negative (Missed detection)
    - `termination`: 🟢 True Positive
    - `rent_amount`: 🟢 True Positive
    - `security_deposit`: 🟢 True Positive
    - `jurisdiction_venue`: 🔴 False Positive (Highlight drift)
    - `lease_term`: 🔴 False Positive (Highlight drift)
    - `maintenance_responsibility`: 🟢 True Negative
    - `dispute_resolution`: 🔴 False Positive (Highlight drift)

### `pdf/03_nda_en.pdf`
*   **Language**: Detected `en`, Match: `🟢 PASS`
*   **Jurisdiction**: Detected `England & Wales`, Match: `🟢 PASS`
*   **Document Type**: Detected `non-disclosure agreement`, Match: `🟢 PASS`
*   **Clause Verification Details**:
    - `governing_law`: 🟢 True Positive
    - `termination`: 🔴 False Negative (Missed detection)
    - `confidentiality`: 🟢 True Positive
    - `jurisdiction_venue`: 🟢 True Negative
    - `return_of_materials`: 🟢 True Negative
    - `dispute_resolution`: 🟢 True Negative

### `pdf/04_incomplete_en.pdf`
*   **Language**: Detected `en`, Match: `🟢 PASS`
*   **Jurisdiction**: Detected `Unknown`, Match: `🟢 PASS`
*   **Document Type**: Detected `software license`, Match: `🟢 PASS`
*   **Clause Verification Details**:
    - `governing_law`: 🟢 True Negative
    - `jurisdiction_venue`: 🟢 True Negative
    - `termination`: 🟢 True Negative
    - `dispute_resolution`: 🟢 True Negative
    - `limitation_liability`: 🟢 True Negative

### `pdf/05_brochure_en.pdf`
*   **Language**: Detected `en`, Match: `🟢 PASS`
*   **Jurisdiction**: Detected `Unknown`, Match: `🟢 PASS`
*   **Document Type**: Detected `None`, Match: `🟢 PASS`
