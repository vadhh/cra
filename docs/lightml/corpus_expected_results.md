# Expected Results for Corpus Fixtures (Original 33 Fixtures)

This master document details the objective expected results for the 33 corpus fixtures of the 11 Technically Mature Profiles. These results serve as the baseline for engine validation.

> [!IMPORTANT]
> **Risk Scoring Scale Note (Aligned with live CRA engine `detector_scorer.py._label()`):**
> - **0 – 30**: LOW (Safe / Informational)
> - **31 – 60**: MEDIUM
> - **61 – 80**: HIGH
> - **81 – 100**: CRITICAL
> Higher risk score indicates HIGHER risk.

## Profile: Commercial Agreement

### Fixture: `commercial_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `commercial_agreement/normal_contract.md` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `commercial_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `commercial_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['governing_law'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['governing_law'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['governing_law']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `commercial_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `commercial_agreement/risky_contract.md` |
| **Expected Profile** | `commercial_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Consulting Agreement

### Fixture: `consulting_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `consulting_agreement/normal_contract.md` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `consulting_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `consulting_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['scope_of_services'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['scope_of_services'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['scope_of_services']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `consulting_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `consulting_agreement/risky_contract.md` |
| **Expected Profile** | `consulting_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Employment Contract

### Fixture: `employment_contract/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `employment_contract/normal_contract.md` |
| **Expected Profile** | `employment_contract` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `employment_contract/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `employment_contract/missing_mandatory_clause.md` |
| **Expected Profile** | `employment_contract` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['compensation'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['compensation'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['compensation']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `employment_contract/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `employment_contract/risky_contract.md` |
| **Expected Profile** | `employment_contract` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: General Contract

### Fixture: `general_contract/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `general_contract/normal_contract.md` |
| **Expected Profile** | `general_contract` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `general_contract/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `general_contract/missing_mandatory_clause.md` |
| **Expected Profile** | `general_contract` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['governing_law'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['governing_law'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['governing_law']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `general_contract/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `general_contract/risky_contract.md` |
| **Expected Profile** | `general_contract` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Lease Agreement

### Fixture: `lease_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `lease_agreement/normal_contract.md` |
| **Expected Profile** | `lease_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `lease_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `lease_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `lease_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['rent_amount'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['rent_amount'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['rent_amount']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `lease_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `lease_agreement/risky_contract.md` |
| **Expected Profile** | `lease_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Loan Agreement

### Fixture: `loan_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `loan_agreement/normal_contract.md` |
| **Expected Profile** | `loan_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `loan_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `loan_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `loan_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['interest_rate'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['interest_rate'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['interest_rate']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `loan_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `loan_agreement/risky_contract.md` |
| **Expected Profile** | `loan_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Non Disclosure Agreement

### Fixture: `non_disclosure_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `non_disclosure_agreement/normal_contract.md` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `non_disclosure_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `non_disclosure_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['return_of_materials'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['return_of_materials'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['return_of_materials']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `non_disclosure_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `non_disclosure_agreement/risky_contract.md` |
| **Expected Profile** | `non_disclosure_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Partnership Agreement

### Fixture: `partnership_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `partnership_agreement/normal_contract.md` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `partnership_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `partnership_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['profit_sharing'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['profit_sharing'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['profit_sharing']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `partnership_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `partnership_agreement/risky_contract.md` |
| **Expected Profile** | `partnership_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Purchase Agreement

### Fixture: `purchase_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `purchase_agreement/normal_contract.md` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `purchase_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `purchase_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['goods_description'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['goods_description'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['goods_description']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `purchase_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `purchase_agreement/risky_contract.md` |
| **Expected Profile** | `purchase_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Service Agreement

### Fixture: `service_agreement/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `service_agreement/normal_contract.md` |
| **Expected Profile** | `service_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `service_agreement/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `service_agreement/missing_mandatory_clause.md` |
| **Expected Profile** | `service_agreement` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['scope_of_services'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['scope_of_services'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['scope_of_services']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `service_agreement/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `service_agreement/risky_contract.md` |
| **Expected Profile** | `service_agreement` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
## Profile: Software License

### Fixture: `software_license/normal_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `software_license/normal_contract.md` |
| **Expected Profile** | `software_license` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 0 - 30 |
| **Expected Risk Level** | LOW (Safe / Informational) |
| **Expected Recommendation** | Contract is standard and low risk. Proceed with standard execution. |
| **Expected PDF Generation Result** | PDF report compiles successfully with 0 red flags. |
| **Expected Detection Confidence** | High (100% keyword and NLI match) |

---
### Fixture: `software_license/missing_mandatory_clause.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `software_license/missing_mandatory_clause.md` |
| **Expected Profile** | `software_license` |
| **Expected Mandatory Clause Detection** | Missing mandatory clauses: ['license_grant'] |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | None detected |
| **Expected Abusive Clause Detection** | None detected |
| **Expected Illegal Clause Detection** | None detected |
| **Expected Leonine Clause Detection** | None detected |
| **Expected Risk Score** | 31 - 80 |
| **Expected Risk Level** | Medium / High |
| **Expected Recommendation** | Insert the missing mandatory clause(s): ['license_grant'] before signing. |
| **Expected PDF Generation Result** | PDF report compiles successfully with warning: Missing ['license_grant']. |
| **Expected Detection Confidence** | High (Missing clause keywords not found) |

---
### Fixture: `software_license/risky_contract.md`

| Field | Expected Result |
| --- | --- |
| **Fixture Name** | `software_license/risky_contract.md` |
| **Expected Profile** | `software_license` |
| **Expected Mandatory Clause Detection** | All required clauses present |
| **Expected Recommended Clause Detection** | None (No recommended clauses configured) |
| **Expected Dangerous Clause Detection** | Excessive penalty clause detected |
| **Expected Abusive Clause Detection** | Unilateral modification clause detected |
| **Expected Illegal Clause Detection** | None |
| **Expected Leonine Clause Detection** | None |
| **Expected Risk Score** | 61 - 100 |
| **Expected Risk Level** | High / Critical |
| **Expected Recommendation** | Negotiate or remove the following risky clauses: Unilateral Modification, Excessive Penalty Clause. |
| **Expected PDF Generation Result** | PDF report compiles successfully with high-severity red flags. |
| **Expected Detection Confidence** | Medium / High (Risk rules triggered on specific patterns) |

---
