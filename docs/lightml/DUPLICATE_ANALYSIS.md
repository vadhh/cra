# Contract Risk Analyzer (CRA) — Duplicate Analysis

This document identifies duplicate data, logic, and code structures across the Contract Risk Analyzer repository and recommends methods for refactoring and merging.

---

## 1. Dataset Duplication

### 1.1. Overlapping Dangerous Clause Datasets
*   **Findings**:
    *   `dangerous_clauses_MASTERv2.csv` (1,212 rows) is the exact concatenation of `dangerous_clauses_MASTER.csv` (594 rows) and `dangerous_clauses_ADDITIONS.csv` (618 rows).
    *   `dangerous_clauses.csv` (613 rows) overlaps with `dangerous_clauses_MASTER.csv` by 148 rows.
*   **Recommendation**: Keep only `dangerous_clauses_MASTERv2.csv` as the single source of truth for dangerous clauses. Mark `dangerous_clauses.csv`, `dangerous_clauses_ADDITIONS.csv`, and `dangerous_clauses_MASTER.csv` as **deprecated** and remove them in the next cleanup cycle.

### 1.2. Overlapping Required Clause Datasets
*   **Findings**:
    *   `required_clauses_MASTER.csv` (900 data rows) contains the complete master library of required clauses across EN/ID/NL/FR.
    *   `required_clauses.csv` (117 data rows) is a historical subset.
    *   `required_clauses_final_OPTIMAL_with_Legal_Reference.csv` (880 data rows) is an older release version.
*   **Recommendation**: Keep only `required_clauses_MASTER.csv` as the required clause database. Deprecate `required_clauses.csv` and `required_clauses_final_OPTIMAL_with_Legal_Reference.csv`.

---

## 2. Code & Architectural Duplication

### 2.1. Double-Defined Contract Type Requirements (Static vs Dynamic)
*   **Findings**:
    *   `detector_rules._CONTRACT_TYPE_PROFILES` defines the required clauses for 10 contract types (employment, lease, software, etc.).
    *   The profile JSON files in `ldv-backend/detector/profiles/` (e.g. `employment_contract.json`, `lease_agreement.json`, etc.) define these same requirements.
    *   `required_clauses_for()` in `detector_rules.py` attempts to load requirements dynamically via `ProfileManager`, falling back to `_CONTRACT_TYPE_PROFILES`.
*   **Recommendation**:
    *   Keep this structure. The JSON files are the primary dynamic source of truth (enabling runtime updates without redeploying code), and `_CONTRACT_TYPE_PROFILES` serves as a safe local fallback.

### 2.2. Overlapping Scoring Policies
*   **Findings**:
    *   `detector_scorer.py` defines a hardcoded fallback `_DEFAULT_POLICY` dictionary.
    *   `ldv-backend/detector/policies/default_v1.json` defines the exact same calibrated scoring parameters.
*   **Recommendation**: Keep both. `default_v1.json` is the active, versioned policy loaded at runtime, while `_DEFAULT_POLICY` provides a safe fallback in case of IO errors.

### 2.3. Overlapping Risk Rules (Regex vs Keyword DB)
*   **Findings**:
    *   `detector_rules.py` implements regex rules for contract components.
    *   `risk_clause_db.py` matches legal clauses using keywords from expert CSV files.
    *   This overlap can lead to double-penalizing the same risk.
*   **Recommendation**:
    *   Keep the current mitigation in `risk_clause_db.py` (`_REGEX_OVERLAP`), which suppresses keyword findings when a matching regex rule has already triggered.

### 2.4. Duplicate API Routes
*   **Findings**:
    *   `/api/v1/upload` (asynchronous, returns 202, enqueues background job).
    *   `/api/v1/analyze` (synchronous legacy endpoint, returns 200 after inline analysis).
*   **Recommendation**: Keep both. `/api/v1/upload` is the standard route used by the frontend dashboard. `/api/v1/analyze` is a legacy route maintained for curl scripts and testing.

### 2.5. Duplicate Utility Helpers
*   **Findings**:
    *   `_to_int()` and CSV parser logic are duplicated in `clause_db.py` and `risk_clause_db.py`.
*   **Recommendation**:
    *   No change is needed. Keeping these adapters self-contained prevents cross-file dependency loops.
