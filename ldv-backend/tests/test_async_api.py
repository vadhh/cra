"""Self-check for app.py upload and api_result asynchronous endpoints (CR-10)."""
import importlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def test_async_api_flow():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ["LDV_SECRET_KEY"] = "test-secret-key-123"
    os.environ.pop("LDV_ENCRYPTION_KEY", None)

    import database
    importlib.reload(database)
    database.init_db()

    import auth
    importlib.reload(auth)

    # Seed org and users
    oid = database.create_org("TestOrg")
    user_token = "user-api-token-123"
    database.create_user(oid, "user@testorg.com", auth.hash_password("password"), "user", user_token)

    other_oid = database.create_org("OtherOrg")
    other_token = "other-api-token-123"
    database.create_user(other_oid, "other@otherorg.com", auth.hash_password("password"), "user", other_token)

    # Mock worker.submit_job
    submitted_jobs = []
    import worker
    worker.submit_job = lambda public_id, text, lang, explain, policy_name=None: submitted_jobs.append((public_id, text, lang, explain, policy_name))

    # Import app to initialize routes
    import app
    importlib.reload(app)
    client = app.app.test_client()

    try:
        # --- Test Upload (POST /upload) ---
        data = {
            "file": (io.BytesIO(b"This is a dummy contract document."), "contract.txt")
        }
        headers = {
            "Authorization": f"Bearer {user_token}"
        }
        resp = client.post("/api/v1/upload", data=data, headers=headers, content_type="multipart/form-data")
        assert resp.status_code == 202, resp.status_code
        res_json = resp.json
        assert "id" in res_json
        assert res_json["status"] == "queued"

        # Verify job was enqueued
        analysis_id = res_json["id"]
        assert len(submitted_jobs) == 1
        assert submitted_jobs[0][0] == analysis_id
        assert "dummy contract document" in submitted_jobs[0][1]

        # --- Test Result Polling (GET /api/result/<id>) ---
        # 1. Queued state
        resp = client.get(f"/api/v1/result/{analysis_id}", headers=headers)
        assert resp.status_code == 200, resp.status_code
        assert resp.json["status"] == "queued"
        assert resp.json["result"] is None

        # 2. Processing state
        database.update_analysis(analysis_id, status="processing")
        resp = client.get(f"/api/v1/result/{analysis_id}", headers=headers)
        assert resp.status_code == 200, resp.status_code
        assert resp.json["status"] == "processing"
        assert resp.json["result"] is None

        # 3. Completed state
        mock_result = {"layer1": {}, "layer2": {}, "layer3": {"score": 5, "label": "LOW"}}
        database.update_analysis(analysis_id, status="completed", risk_score=5, risk_label="LOW", result=mock_result)
        resp = client.get(f"/api/v1/result/{analysis_id}", headers=headers)
        assert resp.status_code == 200, resp.status_code
        assert resp.json["status"] == "completed"
        assert resp.json["result"] == mock_result

        # Verify raw_text / extracted_text is excluded by default
        assert "extracted_text" not in resp.json
        assert "raw_text" not in resp.json

        # Verify raw_text is included when ?debug=1 is provided
        resp_debug = client.get(f"/api/v1/result/{analysis_id}?debug=1", headers=headers)
        assert resp_debug.status_code == 200
        assert resp_debug.json.get("raw_text") == "This is a dummy contract document."

        # --- Test Access Control ---
        # Accessing result from another organization must fail with 403
        other_headers = {
            "Authorization": f"Bearer {other_token}"
        }
        resp = client.get(f"/api/v1/result/{analysis_id}", headers=other_headers)
        assert resp.status_code == 403, resp.status_code
    finally:
        os.remove(db_path)

if __name__ == "__main__":
    test_async_api_flow()
    print("test_async_api OK")
