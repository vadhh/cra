"""Self-check for worker.py background task queues and status tracking (CR-10)."""
import importlib
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["LDV_DB_PATH"] = db_path
os.environ.pop("LDV_ENCRYPTION_KEY", None)

import database
importlib.reload(database)
database.init_db()

# Mock app pipeline methods to avoid loading heavy PyTorch models in test
import app
_orig_run_analysis = app._run_analysis
app._run_analysis = lambda text, juri, lang: {
    "layer1": {},
    "layer2": {"document_type": {"label": "NDA"}},
    "layer3": {"score": 12, "label": "LOW"},
}

import worker

# Save dummy document
doc_id = database.save_document("test.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "extracted text content")

# Create a queued analysis
pid = database.save_analysis(doc_id, None, None, None, None, None, status="queued")

res = database.get_result(pid)
assert res["status"] == "queued"
assert res["result_json"] is None

# Submit the job
worker.submit_job(pid, "extracted text content", "EN", False)

# Wait for completion (it should run in background)
timeout = 5.0
start = time.time()
while time.time() - start < timeout:
    res = database.get_result(pid)
    if res["status"] in ("completed", "failed"):
        break
    time.sleep(0.1)

assert res["status"] == "completed"
assert res["risk_score"] == 12
assert res["risk_label"] == "LOW"
assert res["document_type"] == "NDA"
assert res["result_json"] is not None

# Test Failure case
pid_fail = database.save_analysis(doc_id, None, None, None, None, None, status="queued")

# Cause failure in the mock
def fail_run(text, juri, lang):
    raise ValueError("Pipeline crashed")

app._run_analysis = fail_run

# Submit failed job
worker.submit_job(pid_fail, "some content", "EN", False)

# Wait for failure
start = time.time()
while time.time() - start < timeout:
    res = database.get_result(pid_fail)
    if res["status"] in ("completed", "failed"):
        break
    time.sleep(0.1)

assert res["status"] == "failed"
assert "Pipeline crashed" in res["error_message"]

# Clean up
app._run_analysis = _orig_run_analysis
os.remove(db_path)
print("test_worker OK")
