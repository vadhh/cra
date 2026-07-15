# Contract Risk Analyzer (CRA) — Migration Plan

This plan details the step-by-step steps for migrating historical datasets and resolving remaining functionality gaps in the Contract Risk Analyzer (CRA).

---

## Migration Roadmap

```mermaid
chronology
    title Gap Resolution Timeline
    2026-07-15 : Retrain MLP Classifier
    2026-07-16 : Cache Qwen LLM Weights
    2026-07-17 : Remove Deprecated Datasets
    2026-07-18 : Prepare PostgreSQL Migration
```

---

## 1. Action Items

### Step 1: Retrain the MLP Clause Classifier (`risk_scorer.pkl` / `legal_mlp.pkl`)
*   **Rationale**: The MLP classifier file is currently missing, causing `sydeco_engine.py` to fall back to rule-based classification. Retraining on current master CSVs will restore AI clause tag matching.
*   **Execution**:
    Run these commands inside the `app` container:
    ```bash
    # Step A: Compile training data from datasets directory
    python3 scripts/import_datasets.py

    # Step B: Retrain classifier and generate risk_scorer.pkl
    python3 scripts/train_mlp.py
    ```

### Step 2: Cache Qwen LLM weights for Layer 4 Explanations
*   **Rationale**: The prompt runner is ready, but tests are currently *PENDING* because the `Qwen3-1.7B` weights are not cached locally.
*   **Execution**:
    1.  Temporarily enable downloading by setting `LDV_DOWNLOAD_MODELS=1` in `docker-compose.yml`.
    2.  Restart the container to download and cache the model:
        ```bash
        docker compose up --build -d app
        ```
    3.  Once downloaded, revert `LDV_DOWNLOAD_MODELS` to `0` to enforce strict offline execution.

### Step 3: Remove Deprecated Datasets
*   **Rationale**: Deleting historical files prevents configuration conflicts and reduces confusion.
*   **Execution**:
    Safely delete the following files from `/datasets`:
    *   `dangerous_clauses.csv`
    *   `dangerous_clauses_ADDITIONS.csv`
    *   `dangerous_clauses_MASTER.csv`
    *   `required_clauses.csv`
    *   `required_clauses_final_OPTIMAL_with_Legal_Reference.csv`

### Step 4: Prepare PostgreSQL Schema Migration
*   **Rationale**: Upgrading from SQLite to PostgreSQL avoids database write-locking issues in multi-worker production environments.
*   **Execution**:
    Configure target database endpoints by injecting `LDV_DB_PATH=postgresql://user:pass@host:port/dbname` into Gunicorn environment variables.
