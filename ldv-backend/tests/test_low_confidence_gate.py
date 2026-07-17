"""Unit tests for the Layer 2 classifier low-confidence confirmation gate (Issue #9)."""
import importlib
import json
import os
import sys
import tempfile
import time

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

def test_low_confidence_gating_flow():
    database, db_path = _fresh_db()
    
    import auth
    importlib.reload(auth)
    
    # Create Organization and Admin User
    oid = database.create_org("Test Org")
    admin_token = "admin-test-token"
    database.create_user(oid, "admin@testorg.com", auth.hash_password("password"), "admin", admin_token)

    # Mock _run_analysis to simulate a low-confidence classification result
    import app
    importlib.reload(app)
    
    _orig_run_analysis = app._run_analysis
    
    # We will simulate a low confidence auto-detected classification (confidence = 0.50)
    # unless an override is provided.
    def mock_run_analysis(text, jurisdiction, lang, policy_name=None, override_type=None):
        if override_type:
            return {
                "layer1": {},
                "layer2": {
                    "document_type": {
                        "label": override_type,
                        "confidence": 1.0,
                        "candidates": [{"label": override_type, "confidence": 1.0}],
                        "source": "user_selected"
                    }
                },
                "layer3": {"score": 25, "label": "LOW"},
            }
        return {
            "layer1": {},
            "layer2": {
                "document_type": {
                    "label": "employment contract",
                    "confidence": 0.50,
                    "candidates": [
                        {"label": "employment contract", "confidence": 0.50},
                        {"label": "service agreement", "confidence": 0.30}
                    ],
                    "source": "classifier"
                }
            },
            "layer3": {"score": 25, "label": "LOW"},
        }
        
    app._run_analysis = mock_run_analysis
    
    import worker
    importlib.reload(worker)

    try:
        # 1. Save dummy document and queued analysis
        doc_id = database.save_document("test.txt", "s.txt", "/tmp/s.txt", 10, ".txt", "EN", "extracted text content")
        pid = database.save_analysis(doc_id, None, None, None, None, None, status="queued")

        # 2. Run the job in the background (will trigger low confidence)
        worker.submit_job(pid, "extracted text content", "EN", False)

        # Wait for completion
        timeout = 5.0
        start = time.time()
        while time.time() - start < timeout:
            res = database.get_result(pid)
            if res["status"] in ("completed", "failed", "retryable"):
                break
            time.sleep(0.1)

        # Check that it got marked as retryable with low_confidence error_message
        res = database.get_result(pid)
        assert res["status"] == "retryable"
        assert res["error_message"] == "low_confidence"
        
        # Test API response hides full result but returns candidates
        client = app.app.test_client()
        headers = {"Authorization": f"Bearer {admin_token}"}
        
        resp = client.get(f"/api/v1/result/{pid}", headers=headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "retryable"
        assert data["error_message"] == "low_confidence"
        assert len(data["candidates"]) == 2
        assert data["detected_label"] == "employment contract"
        assert data["detected_confidence"] == 0.50
        assert data["result"] is None

        # 3. Simulate retry with manual confirmation override via POST request body
        resp_retry = client.post(f"/api/v1/result/{pid}/retry", headers=headers, json={"type": "service"})
        assert resp_retry.status_code == 202
        
        # Wait for retry job to complete
        start = time.time()
        while time.time() - start < timeout:
            res = database.get_result(pid)
            if res["status"] in ("completed", "failed"):
                break
            time.sleep(0.1)
            
        # Check that retry completed successfully with overridden type
        res = database.get_result(pid)
        assert res["status"] == "completed"
        assert res["document_type"] == "service"
        assert res["detection_source"] == "user_override"
        assert res["detection_confidence"] == 1.0
        assert res["error_message"] is None

    finally:
        app._run_analysis = _orig_run_analysis
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    test_low_confidence_gating_flow()
    print("test_low_confidence_gate OK")
