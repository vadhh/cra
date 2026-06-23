# Pinned Deployment & Health Checks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Lock direct dependencies in `requirements.txt`, expand `/health` to check database connection, datasets, and local model caches, and configure `Dockerfile` and `docker-compose.yml`.

**Tech Stack:** Python 3, Docker, Docker Compose, Flask.

---

## Global Constraints

- Working directory: `/home/stardhoom/LDV/ldv-backend`.
- All commands run from `ldv-backend/`.

---

## Tasks

### Task 1: Pin Dependencies in requirements.txt
- Modify: `ldv-backend/requirements.txt` (pin direct packages).

- [ ] **Step 1: Check installed packages in the current environment**
  Run `pip freeze` or query package versions to extract exact version numbers.
- [ ] **Step 2: Update requirements.txt with pinned versions**
  Update dependency entries to match standard pinned versions (e.g. `Flask==2.2.5`, `torch==2.0.1` etc. or versions matching current runtime).
- [ ] **Step 3: Commit**
  `git add requirements.txt && git commit -m "feat(cr09): pin Python package dependencies in requirements.txt"`

---

### Task 2: Implement Expanded Health Checks
- Modify: `ldv-backend/database.py` (add connectivity checks).
- Modify: `ldv-backend/app.py` (refactor `/health` endpoint).
- Test: `ldv-backend/tests/test_health_checks.py`

- [ ] **Step 1: Add connection check to `database.py`**
  Add a function `check_connection() -> bool` that runs a query like `SELECT 1` on the SQLite database.
- [ ] **Step 2: Refactor `/health` route in `app.py`**
  - Implement check for DB connection.
  - Implement check for dataset CSV files presence.
  - Implement check for offline HuggingFace model cache directories.
  - Expose status indicators and feature flags in the returned JSON.
- [ ] **Step 3: Write tests verifying `/health` response codes**
  Create `ldv-backend/tests/test_health_checks.py` asserting status payload and exit codes (200 on success, 500 when degraded).
- [ ] **Step 4: Commit**
  `git add database.py app.py tests/test_health_checks.py && git commit -m "feat(cr09): implement database, model, and dataset health checks"`

---

### Task 3: Dockerization & Container Configuration
- Create: `ldv-backend/Dockerfile`
- Create: `docker-compose.yml` (in the root directory)
- Test: Build container verification.

- [ ] **Step 1: Create `Dockerfile` inside `ldv-backend/`**
  Define container setup using `python:3.10-slim`, install system `libmagic1` package, copy sources, and trigger `gunicorn`.
- [ ] **Step 2: Create `docker-compose.yml` in the root workspace directory**
  Define service orchestration, map persistent data directories (SQLite database, file uploads, huggingface cache).
- [ ] **Step 3: Test and verify the Docker build**
  Run `docker compose build` to verify compiling completes without exceptions.
- [ ] **Step 4: Commit**
  `git add ldv-backend/Dockerfile docker-compose.yml && git commit -m "feat(cr09): docker containerization and compose setups"`

---

### Task 4: Documentation Update
- Modify: `CLAUDE.md` (Update P0 #5 / CR-09 status).

- [ ] **Step 1: Mark Pinned Dependencies task as DONE in CLAUDE.md**
- [ ] **Step 2: Commit**
  `git add CLAUDE.md && git commit -m "docs(cr09): update CLAUDE.md status to DONE for CR-09"`
