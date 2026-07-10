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


if __name__ == "__main__":
    test_legacy_running_status_migrates_to_processing()
    test_hidden_result_statuses_constant()
    test_retry_flow()
    print("test_retry OK (tasks 1-2)")
