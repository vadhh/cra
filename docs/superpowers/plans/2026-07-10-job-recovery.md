# Job Recovery Durability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** An analysis is never permanently lost if the worker process crashes, is killed, or is restarted mid-job. The status vocabulary becomes exactly: `queued`, `processing`, `completed`, `failed`, `retryable`. A user can retry a `failed`/`retryable` analysis without re-uploading the file.

**Architecture:** The existing SQLite-row-as-source-of-truth design (CR-10) is preserved, not replaced — no new queue/broker is introduced. Three additive changes close the gap: (1) rename the in-flight status literal from `"running"` to `"processing"` end-to-end; (2) change `database.cleanup_stuck_analyses()` (the existing boot-time sweep that already catches orphaned rows after a crash) to mark them `"retryable"` instead of a dead-end `"failed"`; (3) add a `retry_count` column and a `POST /api/v1/result/<id>/retry` endpoint that re-submits the already-stored extracted text to the worker, capped at `_MAX_RETRIES` attempts.

**Tech Stack:** Python 3, Flask, SQLite (existing `_conn()`/WAL setup in `database.py`), the existing single-thread `ThreadPoolExecutor` in `worker.py`. No new dependencies.

## Global Constraints

- Exact status vocabulary required by the spec: `queued`, `processing`, `completed`, `failed`, `retryable`. No other status values should appear in new code.
- Do not introduce a new message broker, outbox table, or multi-worker leasing scheme — out of scope; the existing single-executor + DB-row + boot-sweep model already satisfies "must not lose an analysis," it just needs the state-machine and retry endpoint gaps closed.
- Existing tests `ldv-backend/tests/test_worker.py` and `ldv-backend/tests/test_async_api.py` must keep passing.
- `database.cleanup_stuck_analyses()`'s existing 30-minute age-gate (added 2026-07-02 to stop it from killing a sibling gunicorn worker's live job) must be preserved — only its terminal status value changes, not its trigger condition.

---

### Task 1: Rename `"running"` to `"processing"` everywhere, extend the hidden-result gate

**Files:**
- Modify: `ldv-backend/worker.py:22,32,42,44,48,63` (all `status="running"` call sites)
- Modify: `ldv-backend/database.py:174` (status column migration block — add a one-line legacy-value normalizer) and `ldv-backend/database.py:779` (`cleanup_stuck_analyses` query's `status IN (...)` clause)
- Modify: `ldv-backend/app.py:714-718` (`api_result`'s hidden-status check) — extract into a named constant
- Modify: `ldv-frontend/index.html:1029,1035-1037` (poll loop status branch + comment)
- Test: Add `ldv-backend/tests/test_retry.py` (new file, also used by Tasks 2-3)

**Interfaces:**
- Produces: `app._HIDDEN_RESULT_STATUSES: frozenset[str]` = `{"queued", "processing", "failed", "retryable"}` — a module-level constant other tasks/tests can import directly without a Flask app/request context.

- [ ] **Step 1: Write the failing test for the DB-side rename migration**

Create `ldv-backend/tests/test_retry.py`:

```python
"""Self-check for job-recovery status vocabulary, stuck-job recovery, and retry."""
import importlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def _fresh_db():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ.pop("LDV_ENCRYPTION_KEY", None)
    import database
    importlib.reload(database)
    database.init_db()
    return database, db_path


def test_legacy_running_status_migrates_to_processing():
    database, db_path = _fresh_db()
    try:
        doc_id = database.save_document("t.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "text")
        pid = database.save_analysis(doc_id, None, None, None, None, None, status="running")

        # Re-running init_db() simulates a process restart after the rename ships;
        # any row still holding the old "running" literal must be normalized.
        database.init_db()

        res = database.get_result(pid)
        assert res["status"] == "processing"
    finally:
        os.remove(db_path)


def test_hidden_result_statuses_constant():
    import app
    assert app._HIDDEN_RESULT_STATUSES == {"queued", "processing", "failed", "retryable"}


if __name__ == "__main__":
    test_legacy_running_status_migrates_to_processing()
    test_hidden_result_statuses_constant()
    print("test_retry OK (task 1)")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `AssertionError` on `res["status"] == "processing"` (still `"running"` — no migration line yet), or `AttributeError: module 'app' has no attribute '_HIDDEN_RESULT_STATUSES'`.

- [ ] **Step 3: Add the legacy-value migration in `database.py`**

In `ldv-backend/database.py`, change:

```python
            if "status" not in cols:
                conn.execute("ALTER TABLE analyses ADD COLUMN status TEXT DEFAULT 'completed'")
```

to:

```python
            if "status" not in cols:
                conn.execute("ALTER TABLE analyses ADD COLUMN status TEXT DEFAULT 'completed'")
            # "running" was renamed to "processing" (2026-07-10, job-recovery durability
            # work) to match the standard queued/processing/completed/failed/retryable
            # vocabulary. Idempotent -- a no-op once no row holds the old value.
            conn.execute("UPDATE analyses SET status = 'processing' WHERE status = 'running'")
```

- [ ] **Step 4: Rename the literal in `worker.py`**

In `ldv-backend/worker.py`, replace every occurrence of `status="running"` with `status="processing"` (6 occurrences, at the calls tagged `extracting`, `classifying`, `analyzing`, `scoring`, `reasoning`, and `preparing`-before-completion). Use:

```bash
cd ldv-backend && sed -i 's/status="running"/status="processing"/g' worker.py
```

- [ ] **Step 5: Rename the literal in `database.cleanup_stuck_analyses()`**

In `ldv-backend/database.py`, in `cleanup_stuck_analyses()`, change:

```python
        db.execute(
            "UPDATE analyses SET status = 'failed', error_message = 'Task interrupted during server reload.' "
            "WHERE status IN ('running', 'queued') AND analyzed_at < datetime('now', '-30 minutes')"
        )
```

to (status literal only for now — the `'failed'` -> `'retryable'` terminal-state change happens in Task 3):

```python
        db.execute(
            "UPDATE analyses SET status = 'failed', error_message = 'Task interrupted during server reload.' "
            "WHERE status IN ('processing', 'queued') AND analyzed_at < datetime('now', '-30 minutes')"
        )
```

- [ ] **Step 6: Extract the hidden-result check into a named constant in `app.py`**

In `ldv-backend/app.py`, near the top of the file after the other module-level constants (find `_NON_CONTRACT_TYPES` or similar existing constant and add nearby), add:

```python
# Statuses where result_json isn't ready to serve: the job is still in flight
# (queued/processing) or needs a retry before it will ever produce a result
# (failed/retryable).
_HIDDEN_RESULT_STATUSES = {"queued", "processing", "failed", "retryable"}
```

Then in `api_result()`, change:

```python
    status = row.get("status", "completed")
    if status in ("queued", "running", "failed"):
        row["result"] = None
        row.pop("result_json", None)
        return jsonify(row)
```

to:

```python
    status = row.get("status", "completed")
    if status in _HIDDEN_RESULT_STATUSES:
        row["result"] = None
        row.pop("result_json", None)
        return jsonify(row)
```

- [ ] **Step 7: Run the test to verify it passes**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `test_retry OK (task 1)`

- [ ] **Step 8: Update the frontend poll loop**

In `ldv-frontend/index.html`, change:

```javascript
                const status = data.status; // queued, running, completed, failed
                this.progressPct = data.progress_pct !== undefined ? data.progress_pct : this.progressPct;

                if (status === 'queued') {
                  this.activeStage = 'uploading';
                  this.progressText = 'Queuing file…';
                } else if (status === 'running') {
                  this.activeStage = data.progress_stage || this.activeStage;
                  this.progressText = data.progress_stage ? data.progress_stage.replace('_', ' ').toUpperCase() + '…' : 'PROCESSING…';
```

to:

```javascript
                const status = data.status; // queued, processing, completed, failed, retryable
                this.progressPct = data.progress_pct !== undefined ? data.progress_pct : this.progressPct;

                if (status === 'queued') {
                  this.activeStage = 'uploading';
                  this.progressText = 'Queuing file…';
                } else if (status === 'processing') {
                  this.activeStage = data.progress_stage || this.activeStage;
                  this.progressText = data.progress_stage ? data.progress_stage.replace('_', ' ').toUpperCase() + '…' : 'PROCESSING…';
```

(The `retryable` branch and Retry button are added in Task 4, once the retry endpoint from Task 2 exists.)

- [ ] **Step 9: Run the existing worker/async regression tests**

Run: `cd ldv-backend && python3 tests/test_worker.py && python3 tests/test_async_api.py`
Expected: both print their `... OK` success line — these tests don't hardcode the string `"running"` in assertions (they poll for `("completed", "failed")`), so the rename should not break them.

- [ ] **Step 10: Commit**

```bash
git add ldv-backend/worker.py ldv-backend/database.py ldv-backend/app.py ldv-frontend/index.html ldv-backend/tests/test_retry.py
git commit -m "refactor: rename in-flight job status running -> processing"
```

---

### Task 2: Add `retry_count` and the retry endpoint

**Files:**
- Modify: `ldv-backend/database.py` (schema migration block, near line 273 after the `review_status`/`reviewed_at` migrations) — add `retry_count` column and a new `retry_analysis()` function
- Modify: `ldv-backend/app.py` — add `POST /api/v1/result/<analysis_id>/retry` route, placed after the existing `DELETE /api/v1/result/<analysis_id>` route (around line 746)
- Test: extend `ldv-backend/tests/test_retry.py` (from Task 1)

**Interfaces:**
- Consumes: `database.get_result(public_id) -> dict | None` (existing, already returns `extracted_text`, `language`, `org_id`), `worker.submit_job(public_id, text, lang, explain, ...) -> None` (existing)
- Produces: `database.retry_analysis(public_id: str) -> str | None` — returns `"queued"` on success (and increments `retry_count`, clears `error_message`), or `None` if the analysis isn't `failed`/`retryable` or has hit `database._MAX_RETRIES` (default 3).

- [ ] **Step 1: Write the failing test**

Append to `ldv-backend/tests/test_retry.py` (before the `if __name__ ==` block):

```python
def test_retry_flow():
    database, db_path = _fresh_db()
    try:
        doc_id = database.save_document("t.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "some contract text")
        pid = database.save_analysis(doc_id, None, None, None, None, None, status="failed")

        # First retry: allowed, flips to queued, increments retry_count
        assert database.retry_analysis(pid) == "queued"
        res = database.get_result(pid)
        assert res["status"] == "queued"
        assert res["retry_count"] == 1

        # Exhaust the retry budget (default _MAX_RETRIES=3): fail it again each time
        for _ in range(2):
            database.update_analysis(pid, status="failed")
            assert database.retry_analysis(pid) == "queued"

        # 4th retry attempt is refused (retry_count is now at the cap)
        database.update_analysis(pid, status="failed")
        assert database.retry_analysis(pid) is None

        # Retrying a 'completed' analysis is refused (wrong status)
        pid2 = database.save_analysis(doc_id, None, None, None, None, None, status="completed")
        assert database.retry_analysis(pid2) is None
    finally:
        os.remove(db_path)
```

And update the `if __name__ ==` block at the bottom to also call it:

```python
if __name__ == "__main__":
    test_legacy_running_status_migrates_to_processing()
    test_hidden_result_statuses_constant()
    test_retry_flow()
    print("test_retry OK (tasks 1-2)")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `AttributeError: module 'database' has no attribute 'retry_analysis'`

- [ ] **Step 3: Add the `retry_count` column migration**

In `ldv-backend/database.py`, in `init_db()`, next to the existing `review_status`/`reviewer_email`/`review_comment`/`reviewed_at` column-add block, add:

```python
            if "retry_count" not in cols:
                conn.execute("ALTER TABLE analyses ADD COLUMN retry_count INTEGER NOT NULL DEFAULT 0")
```

- [ ] **Step 4: Add `retry_analysis()` to `database.py`**

In `ldv-backend/database.py`, add near `cleanup_stuck_analyses()`:

```python
_MAX_RETRIES = 3


def retry_analysis(public_id: str) -> str | None:
    """Move a failed/retryable analysis back to 'queued' for re-execution.

    Returns "queued" on success, or None if the analysis isn't in a
    retryable state or has exhausted its retry budget (_MAX_RETRIES).
    Caller is responsible for re-submitting the job to the worker.
    """
    with _conn() as db:
        row = db.execute(
            "SELECT status, retry_count FROM analyses WHERE public_id = ?",
            (public_id,),
        ).fetchone()
        if row is None or row["status"] not in ("failed", "retryable"):
            return None
        if row["retry_count"] >= _MAX_RETRIES:
            return None
        db.execute(
            "UPDATE analyses SET status = 'queued', retry_count = retry_count + 1, "
            "error_message = NULL WHERE public_id = ?",
            (public_id,),
        )
        return "queued"
```

- [ ] **Step 5: Run the test to verify it passes**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `test_retry OK (tasks 1-2)`

- [ ] **Step 6: Add the retry endpoint in `app.py`**

In `ldv-backend/app.py`, after the existing `DELETE /api/v1/result/<analysis_id>` route, add:

```python
@app.route("/api/v1/result/<analysis_id>/retry", methods=["POST"])
@auth.login_required
def retry_result(analysis_id: str):
    row = database.get_result(analysis_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    user = g.user
    if user["role"] != "admin" and row.get("org_id") != user["org_id"]:
        return jsonify({"error": "Forbidden"}), 403

    new_status = database.retry_analysis(analysis_id)
    if new_status is None:
        return jsonify({"error": "Analysis is not retryable (wrong status or retry limit exhausted)"}), 409

    text = row.get("extracted_text")
    lang = row.get("language") or "unknown"
    worker.submit_job(analysis_id, text, lang, False)

    database.write_audit(
        "analysis.retry", user_id=user["id"], org_id=row.get("org_id"),
        resource_id=analysis_id, ip=_ip(),
    )
    return jsonify({"id": analysis_id, "status": "queued"}), 202
```

- [ ] **Step 7: Manual smoke test against a running server**

Run: `cd ldv-backend && FLASK_APP=app.py python3 -m flask run --port 5000 &`
Then: upload a file, note the returned `id`, force it to `failed` via `sqlite3 sydeco.db "UPDATE analyses SET status='failed' WHERE public_id='<id>'"`, then `curl -X POST -H "Authorization: Bearer <token>" http://127.0.0.1:5000/api/v1/result/<id>/retry`
Expected: `{"id": "<id>", "status": "queued"}` with HTTP 202, and polling `/api/v1/result/<id>` afterward shows it progress to `completed`.

- [ ] **Step 8: Commit**

```bash
git add ldv-backend/database.py ldv-backend/app.py ldv-backend/tests/test_retry.py
git commit -m "feat: add retry_count and POST /api/v1/result/<id>/retry endpoint"
```

---

### Task 3: Crash recovery — stuck jobs become `retryable`, not a dead-end `failed`

**Files:**
- Modify: `ldv-backend/database.py` (`cleanup_stuck_analyses()`)
- Test: extend `ldv-backend/tests/test_retry.py`

**Interfaces:**
- Produces: `cleanup_stuck_analyses()` now sets `status = 'retryable'` (previously `'failed'`) for rows abandoned by a crashed/killed process, so `retry_analysis()` (Task 2) can pick them back up without requiring a fresh upload — this is the core "must not lose an analysis if the worker crashes" guarantee.

- [ ] **Step 1: Write the failing test**

Append to `ldv-backend/tests/test_retry.py` (before the `if __name__ ==` block):

```python
def test_stuck_job_becomes_retryable():
    database, db_path = _fresh_db()
    try:
        doc_id = database.save_document("t.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "text")
        pid = database.save_analysis(doc_id, None, None, None, None, None, status="processing")

        # Backdate analyzed_at to simulate a job abandoned 31 minutes ago
        # (a worker crash mid-job, or a process kill before pickup)
        with database._conn() as db:
            db.execute(
                "UPDATE analyses SET analyzed_at = datetime('now', '-31 minutes') WHERE public_id = ?",
                (pid,),
            )

        database.cleanup_stuck_analyses()

        res = database.get_result(pid)
        assert res["status"] == "retryable"
        assert "restart" in res["error_message"].lower()

        # It must now be retryable via the normal retry path (not a dead end)
        assert database.retry_analysis(pid) == "queued"
    finally:
        os.remove(db_path)
```

Update the `if __name__ ==` block:

```python
if __name__ == "__main__":
    test_legacy_running_status_migrates_to_processing()
    test_hidden_result_statuses_constant()
    test_retry_flow()
    test_stuck_job_becomes_retryable()
    print("test_retry OK (tasks 1-3)")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `AssertionError` on `res["status"] == "retryable"` (still `"failed"` — old terminal state).

- [ ] **Step 3: Change the terminal state in `cleanup_stuck_analyses()`**

In `ldv-backend/database.py`, change:

```python
        db.execute(
            "UPDATE analyses SET status = 'failed', error_message = 'Task interrupted during server reload.' "
            "WHERE status IN ('processing', 'queued') AND analyzed_at < datetime('now', '-30 minutes')"
        )
```

to:

```python
        db.execute(
            "UPDATE analyses SET status = 'retryable', "
            "error_message = 'Interrupted by a server restart -- click Retry to resume.' "
            "WHERE status IN ('processing', 'queued') AND analyzed_at < datetime('now', '-30 minutes')"
        )
```

Also update the function's docstring line "Fail analysis records abandoned by a crashed/killed process." to "Mark analysis records abandoned by a crashed/killed process as retryable." to keep it accurate.

- [ ] **Step 4: Run the test to verify it passes**

Run: `cd ldv-backend && python3 tests/test_retry.py`
Expected: `test_retry OK (tasks 1-3)`

- [ ] **Step 5: Commit**

```bash
git add ldv-backend/database.py ldv-backend/tests/test_retry.py
git commit -m "fix: crash-interrupted jobs recover as retryable instead of a dead-end failed"
```

---

### Task 4: Frontend — surface `retryable` state with a Retry button

**Files:**
- Modify: `ldv-frontend/index.html:916` (Alpine `data()` object — add `showRetry` state)
- Modify: `ldv-frontend/index.html:1038-1051` (poll loop — add the `retryable` branch, keep existing `completed`/`failed` branches)
- Modify: `ldv-frontend/index.html:705-714` (button row — add the Retry button)

**Interfaces:**
- Consumes: `POST /api/v1/result/<id>/retry` (Task 2)

- [ ] **Step 1: Add `showRetry` to the Alpine data object**

In `ldv-frontend/index.html`, next to the existing `errorMsg: '',` field in the `return { ... }` data object (line 916), add:

```javascript
        errorMsg: '',
        showRetry: false,
```

- [ ] **Step 2: Add the `retryable` poll branch**

In `ldv-frontend/index.html`, change:

```javascript
                } else if (status === 'completed') {
                  this.activeStage = 'preparing';
                  this.progressPct = 100;
                  this.progressText = 'COMPLETED';
                  this.stopTimers();
                  setTimeout(() => {
                    window.location.href = '/result/' + this.analysisId;
                  }, 1000);
                } else if (status === 'failed') {
                  this.progressPct = 100;
                  this.progressText = 'FAILED';
                  this.errorMsg = data.error_message || 'Analysis pipeline processing failed.';
                  this.stopTimers();
                }
```

to:

```javascript
                } else if (status === 'completed') {
                  this.activeStage = 'preparing';
                  this.progressPct = 100;
                  this.progressText = 'COMPLETED';
                  this.stopTimers();
                  setTimeout(() => {
                    window.location.href = '/result/' + this.analysisId;
                  }, 1000);
                } else if (status === 'retryable') {
                  this.progressPct = 100;
                  this.progressText = 'INTERRUPTED';
                  this.errorMsg = (data.error_message || 'Analysis was interrupted.') + ' Click Retry to resume.';
                  this.showRetry = true;
                  this.stopTimers();
                } else if (status === 'failed') {
                  this.progressPct = 100;
                  this.progressText = 'FAILED';
                  this.errorMsg = data.error_message || 'Analysis pipeline processing failed.';
                  this.stopTimers();
                }
```

- [ ] **Step 3: Add the `retryAnalysis()` method**

In `ldv-frontend/index.html`, directly after the existing `pollStatus() { ... }` method definition, add:

```javascript
        async retryAnalysis() {
          this.showRetry = false;
          this.errorMsg = '';
          this.progressPct = 0;
          this.progressText = 'Retrying…';
          const resp = await fetch(`/api/v1/result/${this.analysisId}/retry`, { method: 'POST' });
          if (resp.ok) {
            this.pollStatus();
          } else {
            const err = await resp.json().catch(() => ({}));
            this.errorMsg = err.error || 'Retry failed.';
          }
        },
```

- [ ] **Step 4: Add the Retry button**

In `ldv-frontend/index.html`, change:

```html
            <div class="pt-4 flex gap-4 w-full max-w-md justify-center">
              <button type="button" @click="cancelPipeline()"
                      class="px-6 py-3 rounded-md border border-outline-variant/40 hover:bg-surface-container text-xs font-semibold font-body transition-all">
                Cancel Analysis
              </button>
              <button type="button" @click="runInBackground()" x-show="!errorMsg"
                      class="gold-button px-6 py-3 rounded-md text-xs font-bold font-body uppercase tracking-wider">
                Run in Background
              </button>
            </div>
```

to:

```html
            <div class="pt-4 flex gap-4 w-full max-w-md justify-center">
              <button type="button" @click="cancelPipeline()"
                      class="px-6 py-3 rounded-md border border-outline-variant/40 hover:bg-surface-container text-xs font-semibold font-body transition-all">
                Cancel Analysis
              </button>
              <button type="button" @click="retryAnalysis()" x-show="showRetry"
                      class="gold-button px-6 py-3 rounded-md text-xs font-bold font-body uppercase tracking-wider">
                Retry Analysis
              </button>
              <button type="button" @click="runInBackground()" x-show="!errorMsg"
                      class="gold-button px-6 py-3 rounded-md text-xs font-bold font-body uppercase tracking-wider">
                Run in Background
              </button>
            </div>
```

- [ ] **Step 5: Manual browser verification**

Run: start the backend (`FLASK_APP=app.py python3 -m flask run --port 5000`) and serve/open `ldv-frontend/index.html` per the existing dev workflow. Upload a document, then in a second terminal force its row to `retryable` (`sqlite3 ldv-backend/sydeco.db "UPDATE analyses SET status='retryable', error_message='test' WHERE public_id='<id>'"`), and confirm on the next poll tick (within 2s) the UI shows "INTERRUPTED" with a visible "Retry Analysis" button, and clicking it resumes the analysis to completion.

- [ ] **Step 6: Commit**

```bash
git add ldv-frontend/index.html
git commit -m "feat: surface retryable job status with a Retry Analysis button"
```

---

## Self-Review Notes

- **Spec coverage:** "must not lose an analysis if the worker crashes" -> Task 3 (existing boot-time sweep now recovers instead of dead-ending). "browser closes" -> already a non-issue architecturally (job execution is 100% server-side; confirmed during exploration, no code change needed, not fabricated as a task). "job is interrupted" -> Tasks 2+3 together (retryable state + retry endpoint). "status states queued/processing/completed/failed/retryable" -> Task 1 (rename + vocabulary) + Task 3 (retryable wired into the crash path).
- **Placeholder scan:** no TBD/TODO left; every step has literal file paths, line anchors, and complete code.
- **Type consistency:** `retry_analysis()` return type (`str | None`) is used consistently in both the Task 2 test and the Task 2 Step 6 endpoint code (`new_status is None` check). `_HIDDEN_RESULT_STATUSES` (Task 1) and the `cleanup_stuck_analyses` status literals (Task 1 Step 5, Task 3 Step 3) agree on the same five-state vocabulary throughout.
