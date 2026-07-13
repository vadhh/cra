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

        # Race simulation: a second retry_analysis() call on the same public_id
        # while it's already 'queued' (e.g. a double-clicked Retry button, or two
        # concurrent callers that both passed a stale pre-update read) must be
        # refused by the UPDATE's WHERE guard alone -- no separate SELECT check
        # is involved, so this also proves the WHERE clause does the gating.
        assert database.retry_analysis(pid) is None
        res = database.get_result(pid)
        assert res["status"] == "queued"
        assert res["retry_count"] == 1  # unchanged -- not double-incremented

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


if __name__ == "__main__":
    test_legacy_running_status_migrates_to_processing()
    test_hidden_result_statuses_constant()
    test_retry_flow()
    test_stuck_job_becomes_retryable()
    print("test_retry OK (tasks 1-3)")
