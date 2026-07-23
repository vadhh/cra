# Profile Readiness Report

## Objective

This report documents the formal deployment readiness state for all fifty-six (56) contract profiles registered within the Contract Risk Analyzer (CRA) system. As Legal-data and Content Owner, this evaluation establishes whether each profile meets technical, legal, and operational standards required for production deployment, beta staging, or legal sign-off under the CRA-LDV Directive.

---

## Readiness Classification Criteria

Each contract profile is evaluated against five (5) standardized readiness states:

1. **Production Candidate**: Fully implemented active JSON schema, verified risk rules, complete detection specification, validated corpus test results, and **signed physical legal approval from a qualified legal reviewer**.
2. **Beta Candidate**: Fully implemented active JSON schema, verified risk rules, complete detection specification, and functional corpus tests, but **formal physical legal sign-off remains Pending**.
3. **Engineering Required**: Schema mismatch, broken alias mapping, or missing required clause definition requiring engineering action prior to testing.
4. **Pending Legal Review**: Complete technical specification and draft detection rules, but pending statutory legal citation review across target jurisdictions (ID, BE, FR, NL, US, EN&W).
5. **Draft**: Registered in central registry, but lacking active runtime profile JSON configuration or complete corpus test coverage.

---

## Detailed Profile Readiness Audit (56 Profiles)

### 1. Technically Mature Core Profiles (11 Profiles)

| Profile ID | Contract Family | Supported Languages | Required Clauses | Detection Spec | Risk Rules | Legal Evidence | Expected Results | Current Status | Readiness State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `commercial_agreement` | Commercial & Trade | EN, ID | `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `limitation_liability`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `consulting_agreement` | Professional Services | EN, ID, FR | `governing_law`, `jurisdiction_venue`, `scope_of_services`, `payment_terms`, `confidentiality`, `termination`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `employment_contract` | Labor & HR | EN, ID | `governing_law`, `jurisdiction_venue`, `termination`, `notice_period`, `compensation`, `working_hours`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `general_contract` | General Covenants | EN, ID | `governing_law`, `jurisdiction_venue`, `payment_terms`, `termination`, `dispute_resolution`, `limitation_liability` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `lease_agreement` | Real Estate | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `rent_amount`, `lease_term`, `use_of_premises`, `maintenance`, `termination`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `loan_agreement` | Finance & Credit | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `principal_amount`, `interest_rate`, `repayment_terms`, `default_provisions`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `non_disclosure_agreement` | IP & Confidentiality | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `definition_confidential_info`, `term_of_confidentiality`, `exclusions`, `return_materials`, `remedies`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `partnership_agreement` | Corporate / JV | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `capital_contributions`, `profit_sharing`, `management_structure`, `dissolution`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `purchase_agreement` | Commercial & Trade | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `product_description`, `purchase_price`, `delivery_terms`, `warranties`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `service_agreement` | Operations / Services | EN, ID, FR, NL | `governing_law`, `jurisdiction_venue`, `scope_of_work`, `payment_terms`, `service_levels`, `limitation_liability`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |
| `software_license` | IP & Software | EN, ID, NL | `governing_law`, `jurisdiction_venue`, `grant_of_license`, `use_restrictions`, `intellectual_property`, `warranty_disclaimer`, `limitation_liability`, `dispute_resolution` | Complete | Layer 1–3 Active | Pending Sign-off | Passed (100%) | Staging Active | **Beta Candidate** |

### 2. Active Profile Schema Inconsistencies (4 Profiles)

| Profile ID | Contract Family | Supported Languages | Required Clauses | Detection Spec | Risk Rules | Legal Evidence | Expected Results | Current Status | Readiness State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `construction_contract` | Real Estate & Works | EN, ID | Registry: `delivery_terms`; JSON: `insurance`, `limitation_liability` | Draft Spec | Partial Match | Pending Sign-off | Partial | Name Mismatch (`construction_agreement`) | **Engineering Required** |
| `insurance_contract` | Finance & Risk | EN, ID | Registry: `insurance`; JSON: `payment_terms`, `notice_period` | Draft Spec | Partial Match | Pending Sign-off | Partial | Name Mismatch (`insurance_agreement`) | **Engineering Required** |
| `it_services_contract` | Operations & IT | EN, ID | Registry: `ip_ownership`, `warranty_disclaimer`; JSON: `confidentiality` | Draft Spec | Partial Match | Pending Sign-off | Partial | Name Mismatch (`it_service_agreement`) | **Engineering Required** |
| `saas_agreement` | IP & Software | EN, ID | Active JSON complete schema | Missing Spec | Active Loader | Pending Sign-off | Partial | Missing Registry Parent Entry | **Engineering Required** |

### 3. Draft & Staging Profiles (41 Profiles)

| Profile ID (Sample of 41) | Contract Family | Supported Languages | Required Clauses | Detection Spec | Risk Rules | Legal Evidence | Expected Results | Current Status | Readiness State |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `agency_agreement` | Commercial & Trade | EN, ID | Defined in `registry_v1.json` | `spec_agency_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `distribution_agreement` | Commercial & Trade | EN, ID | Defined in `registry_v1.json` | `spec_distribution_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `franchise_agreement` | Commercial & Trade | EN, ID | Defined in `registry_v1.json` | `spec_franchise_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `factoring_agreement` | Finance & Credit | EN, ID | Defined in `registry_v1.json` | `spec_factoring_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `mortgage_deed` | Real Estate | EN, ID | Defined in `registry_v1.json` | `spec_mortgage_deed.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `escrow_agreement` | Finance & Escrow | EN, ID | Defined in `registry_v1.json` | `spec_escrow_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `patent_license` | IP & Licensing | EN, ID | Defined in `registry_v1.json` | `spec_patent_license.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `trademark_license` | IP & Licensing | EN, ID | Defined in `registry_v1.json` | `spec_trademark_license.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| `consignment_agreement` | Commercial & Trade | EN, ID | Defined in `registry_v1.json` | `spec_consignment_agreement.md` | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |
| *... (32 Additional Profiles)* | Various | EN, ID | Defined in `registry_v1.json` | Draft Specs | General Fallback | Pending Sign-off | Untested | Staging Draft | **Pending Legal Review** |

---

## Repository Readiness Summary

| Readiness Category | Count | Percentage | Mandatory Action Required Before Production |
| :--- | :--- | :--- | :--- |
| **Production Candidate** | 0 | 0.0% | Requires signed legal review document for $\ge 1$ profile. |
| **Beta Candidate** | 11 | 19.6% | Requires physical legal sign-off from qualified counsel. |
| **Engineering Required** | 4 | 7.1% | Reconcile registry and JSON schema required clause arrays. |
| **Pending Legal Review** | 41 | 73.2% | Complete statutory citation mapping and active JSON specs. |
| **Draft** | 0 | 0.0% | All 56 profiles have at least registry entries and draft specs. |
| **TOTAL REPOSITORY PROFILES** | **56** | **100.0%** | **Overall System Readiness: Staging / Beta Quality** |

---

## Key Profile Categorization Lists

### Profiles Ready for Production
- **Count**: `0`
- **Status**: Currently **NO profile** is certified for immediate commercial production deployment. Per the CRA-LDV Directive, no legal approval may be fabricated or assumed, and all 56 profiles maintain `Pending` legal sign-off status until physical signature files are recorded.

### Profiles Pending Engineering (4 Profiles)
1. `construction_contract` (`construction_agreement.json` — required clause mismatch)
2. `insurance_contract` (`insurance_agreement.json` — required clause mismatch)
3. `it_services_contract` (`it_service_agreement.json` — required clause mismatch)
4. `saas_agreement` (`saas_agreement.json` — missing parent registry entry)

### Profiles Pending Legal Review (52 Profiles)
- **11 Beta Candidate Core Profiles** (Technically complete, awaiting physical legal approval signature):
  1. `commercial_agreement`
  2. `consulting_agreement`
  3. `employment_contract`
  4. `general_contract`
  5. `lease_agreement`
  6. `loan_agreement`
  7. `non_disclosure_agreement`
  8. `partnership_agreement`
  9. `purchase_agreement`
  10. `service_agreement`
  11. `software_license`
- **41 Staging Draft Profiles** (Awaiting formal legal citation verification and active profile JSON creation):
  - `agency_agreement`, `distribution_agreement`, `franchise_agreement`, `factoring_agreement`, `mortgage_deed`, `escrow_agreement`, `patent_license`, `trademark_license`, `consignment_agreement`, and 32 additional registered contract profiles.
