# Comprehensive Data & QA Hygiene Report (Items 1–6)

**Date:** 2026-07-24  
**Authors:** Ilham (Legal-data & Content Owner) & Afridho (Engineering Owner)  
**Scope:** Data and QA hygiene, release gate matrix alignment, deliverable re-classification, dataset consolidation, and product wording scope constraints.

---

## Executive Summary Matrix

| Item | Topic / Area | Status | Summary of Resolution / Actions Taken |
|:---:|---|:---:|---|
| **1** | Reversed Risk-Score Scale Fix | ✅ Resolved | Corrected scale in `docs/lightml/corpus_expected_results.md` to align with `detector_scorer.py._label()` (0–30 LOW/Safe to 81–100 CRITICAL); re-derived all 33 corpus fixtures across 11 profiles against live scoring logic. |
| **2** | Critical Scoring Error Handling | ✅ Logged / Halted | Halted code changes to prevent 'fixing blind' from truncated reviewer feedback; formally logged requirement in `CRA_RELEASE_GATE_MATRIX.md` to request full untruncated logs prior to code edits. |
| **3** | Package Terminology & Re-classification | ✅ Re-classified | Re-classified 17-file package across `GOLD_STANDARD_VALIDATION_SUMMARY.md` & matrix; dropped "Gold Standard" / "Phase 2" claims; redefined as "valid list of findings / initial legal evidence package". |
| **4** | Concrete Data Issues Closure | ✅ Closed | Registered standalone `saas_agreement`; harmonized naming (`construction_contract`, `insurance_contract`, `it_services_contract`); disambiguated SaaS vs License aliases; expanded FR/NL coverage; consolidated dataset pipeline via `scripts/import_datasets.py`; reconciled `required_clauses` mismatches. |
| **5** | Citation Coverage Gap Reconciliation | ✅ Reconciled | Reconciled "87/87 verified" claim with explicit caveat: 87 DB rows are verified, but 12 registry profiles have statutory citation coverage gaps ("Evidence Not Found"). |
| **6** | Legal-Conclusion Wording Scope Constraint | ✅ Enforced | Enforced hedged, risk-screening phrasing across `risk_explainer.py`, `pdf_report.py`, and author deliverables; strictly prohibited declarative terms ("unenforceable", "void", "safe to execute"). |

---

## Detailed Findings & Resolutions

### 1. Item 1 — Reversed Risk-Score Scale Fix
- **Issue:** `docs/lightml/corpus_expected_results.md` previously used an inverted risk scale where lower numbers represented critical risk and higher numbers represented low risk, contradicting the system's live scoring engine.
- **Resolution:**
  - Corrected the scale in `docs/lightml/corpus_expected_results.md` to align strictly with the authoritative `detector_scorer.py._label()` scale:
    - **0–30:** LOW Risk / Safe
    - **31–60:** MEDIUM Risk / Caution
    - **61–80:** HIGH Risk / High Risk
    - **81–100:** CRITICAL Risk / Severe Red Flags
  - Re-derived expected scores for all **33 corpus fixtures** across the 11 mature profiles using the actual live scoring logic.

---

### 2. Item 2 — Critical Scoring Error Handling
- **Issue:** External review feedback noted "critical scoring errors," but the provided feedback snippet in log outputs was truncated before specific line numbers or clauses were detailed.
- **Resolution:**
  - Halted speculative code changes to `detector_scorer.py` to prevent "fixing blind" without empirical evidence.
  - Formally logged a blocking requirement in `CRA_RELEASE_GATE_MATRIX.md` (Gate 2): full, untruncated reviewer logs must be requested and reviewed before implementing code modifications.

---

### 3. Item 3 — Package Terminology & Re-classification
- **Issue:** The 17-file data-quality package was previously titled as a completed "Gold Standard" and "Phase 2 Deliverable," creating confusion regarding formal legal sign-off status.
- **Resolution:**
  - Re-classified the 17-file deliverable package across [GOLD_STANDARD_VALIDATION_SUMMARY.md](file:///mnt/c/Users/ADVAN/cra/docs/GOLD_STANDARD_VALIDATION_SUMMARY.md) and [CRA_RELEASE_GATE_MATRIX.md](file:///mnt/c/Users/ADVAN/cra/docs/CRA_RELEASE_GATE_MATRIX.md).
  - Explicitly dropped claims of it being a "Gold Standard" or "completed Phase 2 deliverable."
  - Redefined the package as a **"valid list of findings / initial legal evidence package"**, establishing clear scope boundaries without overclaiming legal validation completeness.

---

### 4. Item 4 — Concrete Data Issues Closure
- **Resolutions Across Data & Configuration Files:**
  - **a. Standalone `saas_agreement` Registration:** Registered `saas_agreement` as a standalone profile (`status: draft`) in `registry_v1.json` (promoted from legacy `detector/profiles/saas_agreement.json`), updated `competing_profiles` bidirectionally, and updated test suite assertions (57 profiles).
  - **b. Profile Naming Harmonization:** Standardized keys and titles for `construction_contract`, `insurance_contract`, and `it_services_contract` across `registry_v1.json` and active JSON files (`construction_agreement.json`, `insurance_agreement.json`, `it_service_agreement.json`).
  - **c. SaaS vs. Software License Alias Disambiguation:** Removed `"saas agreement"` alias from `software_license` in `registry_v1.json` per `ALIAS_REVIEW.md`, ensuring `"saas agreement"` resolves cleanly to `saas_agreement`.
  - **d. Multi-language Terminology Expansion:** Expanded French (FR) and Dutch (NL) statutory terminology dictionary coverage in `LEGAL_TERMINOLOGY_REVIEW.md` and dataset keyword aliases.
  - **e. Dataset Pipeline Consolidation:** Consolidated legacy and duplicate datasets via `scripts/import_datasets.py` pipeline, unifying references into `required_clauses_MASTER.csv` and `dangerous_clauses_MASTERv2.csv` while preserving all underlying physical files.
  - **f. `required_clauses` Reconciliation:** Reconciled `required_clauses` mismatches between registry profile definitions and active JSON profile files by taking the union of both sources per `REQUIRED_CLAUSE_RECONCILIATION.md`.

---

### 5. Item 5 — Citation Coverage Gap Reconciliation
- **Issue:** `datasets/legal_citations.csv` reports **87/87 rows `status=verified`**, but 12 registry profiles contain required clauses (e.g. `jurisdiction_venue`, `notice_period`) lacking statutory citations, reported as **Evidence Not Found**.
- **Resolution:**
  - Established an explicit caveat across project documentation ([CRA_RELEASE_GATE_MATRIX.md](file:///mnt/c/Users/ADVAN/cra/docs/CRA_RELEASE_GATE_MATRIX.md), [legal_review_packet.md](file:///mnt/c/Users/ADVAN/cra/docs/legal_review_packet.md), [LEGAL_CITATION_VERIFICATION.md](file:///mnt/c/Users/ADVAN/cra/docs/LEGAL_CITATION_VERIFICATION.md)):
    > *While 100% of the 87 existing rows in `datasets/legal_citations.csv` carry `status=verified`, this figure reflects internal database row verification, NOT 100% profile statutory coverage. 12 registry profiles still have required clauses lacking statutory citations, logged as 'Evidence Not Found' in the gap tracker.*

---

### 6. Item 6 — Legal-Conclusion Wording Scope Constraint
- **Issue:** Product outputs and author deliverables must function as an objective risk-screening tool and must avoid declarative legal conclusions.
- **Resolution:**
  - Enforced scope constraint across all authored deliverables and product outputs (`risk_explainer.py`, `pdf_report.py`, `CRA_RELEASE_GATE_MATRIX.md`).
  - **Prohibited Declarative Terms:** `"unenforceable"`, `"void"`, `"safe to execute"`, `"legally invalid"`.
  - **Mandatory Hedged Phrasing:** `"commonly held void in civil-law systems"`, `"may be unenforceable under mandatory consumer protections"`, `"frequently challenged in court"`, `"signals a significant risk imbalance"`.
  - Verified `risk_explainer.py` (`_RED_FLAG_GUIDANCE`) and `pdf_report.py` adhere strictly to hedged risk-screening language.

---

## Deliverable Impact & Verification Summary

| File / Module | Area Impacted | Verification / Self-Check Result |
|---|---|---|
| [docs/CRA_RELEASE_GATE_MATRIX.md](file:///mnt/c/Users/ADVAN/cra/docs/CRA_RELEASE_GATE_MATRIX.md) | Release Gates 2, 4 & Owners | Updated for Items 1–6; Gate 4 wording and citation sub-items reconciled. |
| [docs/legal_review_packet.md](file:///mnt/c/Users/ADVAN/cra/docs/legal_review_packet.md) | Section F & Sign-off | 87/87 citation reconciliation caveat added. |
| [docs/LEGAL_CITATION_VERIFICATION.md](file:///mnt/c/Users/ADVAN/cra/docs/LEGAL_CITATION_VERIFICATION.md) | Citation Gap Analysis | Reconciliation note added distinguishing DB rows from profile gaps. |
| [ldv-backend/detector/risk_explainer.py](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/risk_explainer.py) | Risk Explanations | All 13 guidance entries reworded to hedged risk-screening phrasing. |
| [ldv-backend/pdf_report.py](file:///mnt/c/Users/ADVAN/cra/ldv-backend/pdf_report.py) | PDF Generation | Disclaimers and recommendations verified as non-declarative. |
| [ldv-backend/detector/citation_db.py](file:///mnt/c/Users/ADVAN/cra/ldv-backend/detector/citation_db.py) | Citation DB Adapter | Self-check passed (`OK: 43 findings cited, 87 citation rows (87 verified)`). |
| [ldv-backend/tests/validate_profiles.py](file:///mnt/c/Users/ADVAN/cra/ldv-backend/tests/validate_profiles.py) | Registry Validation | Profile validation passed (`OK — 57 profiles, 43 approved clause IDs`). |

---

## Status Declaration

- **Item 1 (Reversed Risk-Score Scale Fix):** ✅ **RESOLVED**
- **Item 2 (Critical Scoring Error Handling):** ✅ **LOGGED / HALTED**
- **Item 3 (Package Terminology & Re-classification):** ✅ **RE-CLASSIFIED**
- **Item 4 (Concrete Data Issues Closure):** ✅ **CLOSED**
- **Item 5 (Citation Coverage Gap Reconciliation):** ✅ **RECONCILED**
- **Item 6 (Legal-Conclusion Wording Scope Constraint):** ✅ **ENFORCED**
