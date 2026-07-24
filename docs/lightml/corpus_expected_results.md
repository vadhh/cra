# Expected Results for Corpus Fixtures (Original 33 Fixtures)

This master document details the objective, lawyer-reviewed expected results for all 33 corpus fixtures across the 11 Technically Mature Profiles. These ground-truth scores, risk levels, and detection confidences serve as the baseline for engine validation.

> [!IMPORTANT]
> **Risk Scoring Scale Note (Aligned with live CRA engine `detector_scorer.py._label()`):**
> - **0 – 30**: LOW (Safe / Informational)
> - **31 – 60**: MEDIUM (Caution / Operational Risk)
> - **61 – 80**: HIGH (High Risk / Substantive Exposure)
> - **81 – 100**: CRITICAL (Severe Risk / Illegal or Abusive Terms)
> Higher risk score indicates HIGHER risk.

---

## 1. Profile: Employment Contract (`employment_contract`)

### Fixture 1: `pdf/01_employment_id.pdf`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `pdf/01_employment_id.pdf` |
| **Expected Profile** | `employment_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 3/7 present (missing: `governing_law`, `jurisdiction_venue`, `notice_period`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 45 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing 4 required clauses (including venue & governing law) creates procedural uncertainty, but core employment terms (compensation, working hours) are present with no red flags fired, placing it in MEDIUM risk. |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with medium-level warnings for missing required clauses) |
| **Expected Detection Confidence** | High (0.90 regex / structural PDF extraction) |

---
### Fixture 2: `txt/01_employment_id.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/01_employment_id.txt` |
| **Expected Profile** | `employment_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 2/7 present (missing: `governing_law`, `jurisdiction_venue`, `termination`, `notice_period`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 60 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing 5 of 7 mandatory clauses (including termination and dispute resolution) significantly increases vulnerability, placing score at the upper boundary of MEDIUM (60/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with multiple missing clause warnings) |
| **Expected Detection Confidence** | High (0.90 text extraction and keyword matching) |

---
### Fixture 3: `txt/11_low_risk_employment_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/11_low_risk_employment_en.txt` |
| **Expected Profile** | `employment_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 4/7 present (missing: `jurisdiction_venue`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 46 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Core employment & salary terms intact; missing dispute venue and termination mechanics warrants a MEDIUM risk classification (46/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with 3 missing clause warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---

## 2. Profile: Lease Agreement (`lease_agreement`)

### Fixture 4: `pdf/02_lease_be.pdf`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `pdf/02_lease_be.pdf` |
| **Expected Profile** | `lease_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/8 present (missing: `jurisdiction_venue`, `maintenance_responsibility`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 41 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Essential lease terms (rent, term, deposit) are present; missing maintenance breakdown and venue shifts risk score into lower-MEDIUM (41/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with missing clause summary) |
| **Expected Detection Confidence** | High (0.90 PDF parsing) |

---
### Fixture 5: `txt/02_lease_be.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/02_lease_be.txt` |
| **Expected Profile** | `lease_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 4/8 present (missing: `jurisdiction_venue`, `lease_term`, `maintenance_responsibility`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 51 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing lease term duration and maintenance allocation creates moderate operational risk, placing score at 51 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with missing lease term & venue warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---
### Fixture 6: `txt/13_medium_risk_lease_nl.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/13_medium_risk_lease_nl.txt` |
| **Expected Profile** | `lease_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 2/8 present (missing: `jurisdiction_venue`, `lease_term`, `security_deposit`, `maintenance_responsibility`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 76 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Severe structural deficiency with 6 of 8 mandatory clauses absent (including lease term, deposit, and termination), accumulating high missing-clause point deductions resulting in HIGH risk (76/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with high-risk advisory header and 6 missing clause warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---

## 3. Profile: Software License (`software_license`)

### Fixture 7: `txt/bench_software_license_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_software_license_pos.txt` |
| **Expected Profile** | `software_license` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 30 |
| **Expected Risk Level** | LOW |
| **Legal Justification** | Complete license grant, IP ownership, and liability disclaimers present with 0 red flags; minor missing administrative clauses keep risk in the LOW range (30/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with minimal informational notices) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 8: `txt/bench_software_license_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_software_license_neg.txt` |
| **Expected Profile** | `software_license` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 63 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Presence of critical red flag patterns (unilateral rights / broad liability exclusion) elevates risk score directly into HIGH (63/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly displaying prominent red-flag risk callouts) |
| **Expected Detection Confidence** | High (0.90 benchmark red flag match) |

---
### Fixture 9: `txt/08_medium_risk_partial_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/08_medium_risk_partial_en.txt` |
| **Expected Profile** | `software_license` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 4/8 present (missing: `jurisdiction_venue`, `warranty_disclaimer`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 53 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing warranty disclaimer and dispute venue creates exposure, but valid license grant prevents critical escalation, resulting in 53 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with medium risk warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---

## 4. Profile: Service Agreement (`service_agreement`)

### Fixture 10: `docx/01_service_agreement_en.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/01_service_agreement_en.docx` |
| **Expected Profile** | `service_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/7 present (missing: `jurisdiction_venue`, `termination`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 31 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Clear scope of services and payment terms present; missing termination clause places it just above LOW threshold at 31 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with 2 missing clause warnings) |
| **Expected Detection Confidence** | High (0.90 docx parsing) |

---
### Fixture 11: `txt/06_high_risk_leonine_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/06_high_risk_leonine_en.txt` |
| **Expected Profile** | `service_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/7 present (missing: `jurisdiction_venue`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Abusive / Leonine clauses detected) |
| **Expected Risk Score** | 99 |
| **Expected Risk Level** | CRITICAL |
| **Legal Justification** | One-sided leonine risk allocation (excluding vendor from all losses while claiming all profits) is severely abusive under contract law, triggering maximum risk weight (99/100 CRITICAL). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with critical red-flag alert box and redlining recommendations) |
| **Expected Detection Confidence** | High (0.95 high-precision rule match) |

---
### Fixture 12: `txt/15_critical_risk_no_law_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/15_critical_risk_no_law_en.txt` |
| **Expected Profile** | `service_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `scope_of_services`) |
| **Expected Dangerous Clause Detection** | Informational: 3 fired |
| **Expected Risk Score** | 100 |
| **Expected Risk Level** | CRITICAL |
| **Legal Justification** | Multiple severe red flags including illegal object and exclusion of liability for intentional misconduct present extreme legal exposure, resulting in a score of 100 (CRITICAL). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with maximum severity critical warnings and legal disclaimer) |
| **Expected Detection Confidence** | High (0.95 rule match) |

---

## 5. Profile: Consulting Agreement (`consulting_agreement`)

### Fixture 13: `txt/bench_consulting_agreement_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_consulting_agreement_pos.txt` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 31 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Comprehensive consulting scope, confidentiality, and payment terms; missing dispute resolution mechanism places score at 31 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with 1 minor warning) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 14: `txt/bench_consulting_agreement_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_consulting_agreement_neg.txt` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 64 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Contains severe risk-shifting provisions forcing client to pay for consultant errors, elevating score to HIGH (64/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with red-flag risk callouts) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 15: `txt/07_high_risk_missing_clauses_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/07_high_risk_missing_clauses_en.txt` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/7 present (missing: `jurisdiction_venue`, `confidentiality`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 23 |
| **Expected Risk Level** | LOW |
| **Legal Justification** | Basic consulting scope and payment present with zero red flags; missing confidentiality and venue results in a LOW score (23/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with low risk label) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---

## 6. Profile: Commercial Agreement (`commercial_agreement`)

### Fixture 16: `txt/bench_commercial_agreement_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_commercial_agreement_pos.txt` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 4/6 present (missing: `limitation_liability`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 51 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing limitation of liability in a commercial agreement creates uncapped risk exposure, resulting in a score of 51 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with liability cap warning) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 17: `txt/bench_commercial_agreement_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_commercial_agreement_neg.txt` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/6 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 56 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Unilateral liability waiver fired, resulting in 56 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with red flag warning) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 18: `docx/bench_commercial_agreement_pos.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/bench_commercial_agreement_pos.docx` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 4/6 present (missing: `limitation_liability`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 51 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Format parity variant matching txt positive benchmark score (51 MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with liability warning) |
| **Expected Detection Confidence** | High (0.90 docx parsing) |

---

## 7. Profile: Non Disclosure Agreement (`non_disclosure_agreement`)

### Fixture 19: `pdf/03_nda_en.pdf`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `pdf/03_nda_en.pdf` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 3/6 present (missing: `jurisdiction_venue`, `return_of_materials`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 41 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Core NDA confidentiality obligation present; missing return of materials and venue puts score at 41 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with 3 missing clause warnings) |
| **Expected Detection Confidence** | High (0.90 PDF parsing) |

---
### Fixture 20: `txt/14_low_risk_nda_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/14_low_risk_nda_en.txt` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 3/6 present (missing: `termination`, `return_of_materials`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 48 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Standard NDA missing termination term and asset return clause, scoring 48 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---
### Fixture 21: `docx/03_nda_nl.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/03_nda_nl.docx` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 2/6 present (missing: `jurisdiction_venue`, `termination`, `return_of_materials`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 48 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Multilingual Dutch NDA missing 4 mandatory clauses, scoring 48 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with Dutch clause warnings) |
| **Expected Detection Confidence** | High (0.85 docx parsing) |

---

## 8. Profile: Loan Agreement (`loan_agreement`)

### Fixture 22: `txt/bench_loan_agreement_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_loan_agreement_pos.txt` |
| **Expected Profile** | `loan_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 30 |
| **Expected Risk Level** | LOW |
| **Legal Justification** | Principal amount, interest rate, and repayment schedule present with zero red flags, placing it at the top of LOW risk (30/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with low-risk summary) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 23: `txt/bench_loan_agreement_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_loan_agreement_neg.txt` |
| **Expected Profile** | `loan_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 63 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Compounded daily late payment penalty creates punitive risk, raising score to HIGH (63/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with penalty warning callouts) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 24: `txt/09_medium_risk_no_venue_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/09_medium_risk_no_venue_en.txt` |
| **Expected Profile** | `loan_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/8 present (missing: `jurisdiction_venue`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 38 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Core loan terms present; missing venue and termination shifts score to 38 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with 3 missing clause warnings) |
| **Expected Detection Confidence** | High (0.85 text parsing) |

---

## 9. Profile: Partnership Agreement (`partnership_agreement`)

### Fixture 25: `txt/bench_partnership_agreement_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_partnership_agreement_pos.txt` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 15 |
| **Expected Risk Level** | LOW |
| **Legal Justification** | Capital contributions, profit sharing, and management rights fully articulated; score is 15 (LOW). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with minimal warnings) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 26: `txt/bench_partnership_agreement_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_partnership_agreement_neg.txt` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 48 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Unilateral partner control clause elevates risk score to 48 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with red-flag warnings) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 27: `docx/bench_partnership_agreement_pos.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/bench_partnership_agreement_pos.docx` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/7 present (missing: `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 15 |
| **Expected Risk Level** | LOW |
| **Legal Justification** | Format parity variant matching txt positive benchmark score (15 LOW). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with minimal warnings) |
| **Expected Detection Confidence** | High (0.90 docx parsing) |

---

## 10. Profile: Purchase Agreement (`purchase_agreement`)

### Fixture 28: `txt/bench_purchase_agreement_pos.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_purchase_agreement_pos.txt` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `warranty`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 1 fired |
| **Expected Risk Score** | 60 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Missing product warranty combined with informational clause flags places score at 60 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with warranty warning) |
| **Expected Detection Confidence** | High (0.90 benchmark match) |

---
### Fixture 29: `txt/bench_purchase_agreement_neg.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/bench_purchase_agreement_neg.txt` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 6/8 present (missing: `warranty`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | PASS (Red flags fired) |
| **Expected Risk Score** | 93 |
| **Expected Risk Level** | CRITICAL |
| **Legal Justification** | Severe liability exclusion and aggressive forfeiture terms trigger CRITICAL risk classification (93/100). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with redlining callout boxes) |
| **Expected Detection Confidence** | High (0.95 rule match) |

---
### Fixture 30: `pdf/bench_purchase_agreement_pos.pdf`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `pdf/bench_purchase_agreement_pos.pdf` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/8 present (missing: `jurisdiction_venue`, `warranty`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 1 fired |
| **Expected Risk Score** | 68 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Missing warranty and dispute venue in PDF container format brings risk score to 68 (HIGH). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with PDF risk summary) |
| **Expected Detection Confidence** | High (0.90 PDF parsing) |

---

## 11. Profile: General Contract (`general_contract`)

### Fixture 31: `docx/04_legal_memo_en.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/04_legal_memo_en.docx` |
| **Expected Profile** | `general_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 1/6 present (missing: `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 70 |
| **Expected Risk Level** | HIGH |
| **Legal Justification** | Informal legal memo missing 5 of 6 essential contract clauses results in 70 (HIGH). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with high-risk incomplete contract disclaimer) |
| **Expected Detection Confidence** | High (0.85 docx parsing) |

---
### Fixture 32: `docx/06_memo_fr.docx`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `docx/06_memo_fr.docx` |
| **Expected Profile** | `general_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 2/6 present (missing: `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 58 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | French memo missing 4 mandatory clauses, scoring 58 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with missing clause notices) |
| **Expected Detection Confidence** | High (0.85 docx parsing) |

---
### Fixture 33: `txt/04_long_agreement_en.txt`
| Field | Expected Result |
| --- | --- |
| **Fixture Path** | `txt/04_long_agreement_en.txt` |
| **Expected Profile** | `general_contract` |
| **Expected Identification** | PASS |
| **Expected Mandatory Clause Detection** | 5/6 present (missing: `jurisdiction_venue`) |
| **Expected Dangerous Clause Detection** | Informational: 0 fired |
| **Expected Risk Score** | 40 |
| **Expected Risk Level** | MEDIUM |
| **Legal Justification** | Detailed agreement missing only venue clause, scoring 40 (MEDIUM). |
| **Expected PDF Generation Result** | PASS (Compiles cleanly with venue warning) |
| **Expected Detection Confidence** | High (0.90 text parsing) |
