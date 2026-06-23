# Asynchronous Job Queue Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Offload contract analysis execution to an in-process background thread pool, save task status (`queued`, `running`, `completed`, `failed`) and any error logs in the database, and refactor the Flask upload/results endpoints to support asynchronous polling.

**Tech Stack:** Python 3, Flask, SQLite, `concurrent.futures`. Tests are plain Python assert scripts under `tests/` (no pytest).

---

## Global Constraints

- Working directory: `/home/stardhoom/LDV/ldv-backend`.
- All commands run from `ldv-backend/`.
- No new external package dependencies (no Celery, no Redis).

---

## Tasks

### Task 1: Database Migration
- Modify: `ldv-backend/database.py` (add `status` and `error_message` to `analyses` table, auto-migrate, and support query/updates).
- Test: `ldv-backend/tests/test_db_migration.py`

- [ ] **Step 1: Write the failing migration test**
  Create `ldv-backend/tests/test_db_migration.py` to assert that schema has `status` and `error_message` columns on `analyses`, and that older db schema auto-updates in `init_db()`.
- [ ] **Step 2: Run test to verify it fails**
  `python3 tests/test_db_migration.py`
- [ ] **Step 3: Update `database.py` schema and migration code**
  - Add `status TEXT DEFAULT 'completed'` and `error_message TEXT` to `_SCHEMA`.
  - Add column detection in `init_db()` and alter table if columns are missing.
  - Update `save_analysis` to accept `status` and `error_message` parameter.
  - Add a new helper `update_analysis_status(public_id, status, error_message=None, result=None)` to update state during processing.
- [ ] **Step 4: Run test to verify migration passes**
  `python3 tests/test_db_migration.py`
- [ ] **Step 5: Commit**
  `git add database.py tests/test_db_migration.py && git commit -m "feat(cr10): database schema migrations for status tracking"`

---

### Task 2: Background Worker Module
- Create: `ldv-backend/worker.py` (manages background thread executor and pipeline execution wrapper).
- Test: `ldv-backend/tests/test_worker.py`

- [ ] **Step 1: Create background worker thread pool in `worker.py`**
  - Initialize a single worker thread executor: `ThreadPoolExecutor(max_workers=1)`.
  - Define `submit_job(public_id, ...)` that enqueues the analysis pipeline execution.
  - Inside the job wrapper:
    - Update DB status to `running`.
    - Call the analysis pipeline logic.
    - Save the result and update DB status to `completed`.
    - If an exception occurs, update DB status to `failed` and log the traceback to `error_message`.
- [ ] **Step 2: Write `tests/test_worker.py` and verify background task processing**
- [ ] **Step 3: Commit**
  `git add worker.py tests/test_worker.py && git commit -m "feat(cr10): worker module with thread pool execution"`

---

### Task 3: API Endpoint Integration
- Modify: `ldv-backend/app.py`
- Test: `ldv-backend/tests/test_async_api.py`

- [ ] **Step 1: Refactor `POST /upload` and `POST /analyze`**
  - Validate and save the uploaded document.
  - Create a queued analysis entry in the database.
  - Submit the job to `worker.submit_job()`.
  - Return `202 Accepted` with `{"id": public_id, "status": "queued"}`.
- [ ] **Step 2: Refactor `GET /api/result/<public_id>`**
  - Check status in database.
  - If `queued` or `running`: return status 200 (or 202) with `{"id": public_id, "status": status, "result": None}`.
  - If `failed`: return status 200 (or 500) with `{"id": public_id, "status": "failed", "error": error_message, "result": None}`.
  - If `completed`: return the standard completed results.
- [ ] **Step 3: Write API tests and run to verify endpoint responses**
- [ ] **Step 4: Commit**
  `git add app.py tests/test_async_api.py && git commit -m "feat(cr10): async endpoint refactors for upload and results"`

---

### Task 4: Documentation
- Modify: `CLAUDE.md` (Update status of P0 #4 / CR-10).

- [ ] **Step 1: Mark Async Job Queue as DONE in CLAUDE.md**
- [ ] **Step 2: Commit**
  `git add CLAUDE.md && git commit -m "docs(cr10): update CLAUDE.md status to DONE for CR-10"`
