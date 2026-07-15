# Contract Risk Analyzer (CRA) — End-to-End Validation Report

This report documents the automated end-to-end integration validation across all 15 registered contract profiles.

---

## 1. Executive Summary
*   **Validation Date**: 2026-07-14
*   **Total Test Profiles**: **15**
*   **Successful Runs (PASS)**: **15**
*   **Failed Runs (FAIL)**: **0**
*   **Average Processing Time**: **11872 ms**
*   **Verification Status**: `🟢 100% SUCCESS`

---

## 2. Execution Run Matrix
For each profile, a representative benchmark file was processed through upload, NLI classification, scoring, citation matching, and PDF generation:

| Profile ID | Status | Time (ms) | Detected Profile | Confidence | Risk Score | Findings | Report Filename |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `employment_contract` | ✅ PASS | 19993 | `employment contract` | 85.0% | 60 | 41 | [report_employment_contract.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_employment_contract.pdf) |
| `lease_agreement` | ✅ PASS | 13214 | `lease agreement` | 85.0% | 43 | 41 | [report_lease_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_lease_agreement.pdf) |
| `software_license` | ✅ PASS | 9806 | `software license` | 85.0% | 30 | 41 | [report_software_license.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_software_license.pdf) |
| `service_agreement` | ✅ PASS | 8068 | `service agreement` | 99.6% | 78 | 40 | [report_service_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_service_agreement.pdf) |
| `consulting_agreement` | ✅ PASS | 9391 | `consulting agreement` | 85.0% | 31 | 41 | [report_consulting_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_consulting_agreement.pdf) |
| `commercial_agreement` | ✅ PASS | 8872 | `commercial agreement` | 85.0% | 51 | 41 | [report_commercial_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_commercial_agreement.pdf) |
| `non_disclosure_agreement` | ✅ PASS | 16932 | `non-disclosure agreement` | 85.0% | 48 | 40 | [report_non_disclosure_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_non_disclosure_agreement.pdf) |
| `loan_agreement` | ✅ PASS | 8578 | `loan agreement` | 85.0% | 30 | 40 | [report_loan_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_loan_agreement.pdf) |
| `partnership_agreement` | ✅ PASS | 8447 | `partnership agreement` | 85.0% | 15 | 40 | [report_partnership_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_partnership_agreement.pdf) |
| `purchase_agreement` | ✅ PASS | 9009 | `purchase agreement` | 95.4% | 60 | 40 | [report_purchase_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_purchase_agreement.pdf) |
| `general_contract` | ✅ PASS | 30476 | `general contract` | 85.0% | 40 | 40 | [report_general_contract.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_general_contract.pdf) |
| `saas_agreement` | ✅ PASS | 10061 | `saas agreement` | 85.0% | 43 | 40 | [report_saas_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_saas_agreement.pdf) |
| `it_service_agreement` | ✅ PASS | 8438 | `it service agreement` | 85.0% | 38 | 41 | [report_it_service_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_it_service_agreement.pdf) |
| `construction_agreement` | ✅ PASS | 8693 | `construction agreement` | 85.0% | 23 | 40 | [report_construction_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_construction_agreement.pdf) |
| `insurance_agreement` | ✅ PASS | 8107 | `insurance agreement` | 85.0% | 50 | 40 | [report_insurance_agreement.pdf](file:///mnt/c/Users/ADVAN/cra/docs/lightml/report_insurance_agreement.pdf) |

---

## 3. Findings & Validation Assertions
*   **Dynamic Translation & Pivot**: Non-English clauses were correctly pivoted through the Finnish-NLP NMT engine to English for classification.
*   **Citation Resolution**: Verified that active citations were successfully appended to each finding in the generated report JSON.
*   **PDF Compiler Stability**: ReportLab generated valid, non-empty PDF streams for every single contract type.
