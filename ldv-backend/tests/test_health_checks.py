"""Self-check for app.py health checking endpoint (CR-09)."""
import importlib
import os
import sys
import tempfile
from unittest.mock import patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def test_health_checks_flow():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ["LDV_SECRET_KEY"] = "test-secret-key-123"
    os.environ.pop("LDV_ENCRYPTION_KEY", None)

    import database
    importlib.reload(database)
    database.init_db()

    import app
    importlib.reload(app)
    client = app.app.test_client()

    try:
        # --- Test healthy response ---
        resp = client.get("/health")
        print("HEALTH CHECK RESPONSE JSON:", resp.json)
        assert resp.status_code == 200, resp.status_code
        res_json = resp.json
        assert res_json["status"] == "healthy"
        assert res_json["checks"]["database"] == "ready"
        assert res_json["checks"]["datasets"] == "ready"

        # --- Test degraded database ---
        with patch("database.check_connection", return_value=False):
            resp = client.get("/health")
            assert resp.status_code == 500, resp.status_code
            assert resp.json["status"] == "degraded"
            assert resp.json["checks"]["database"] == "failed"

        # --- Test degraded datasets ---
        with patch("os.path.exists", return_value=False):
            resp = client.get("/health")
            assert resp.status_code == 500, resp.status_code
            assert resp.json["status"] == "degraded"
            assert resp.json["checks"]["datasets"] == "missing"
    finally:
        # Clean up
        os.remove(db_path)

if __name__ == "__main__":
    test_health_checks_flow()
    print("test_health_checks OK")
