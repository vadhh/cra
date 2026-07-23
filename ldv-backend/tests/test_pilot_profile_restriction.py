"""Self-check for the 2026-07-17 review's pilot restriction: manual contract-
type selection on /api/v1/upload and /api/v1/result/<id>/retry must be
limited to the 11 original (registry classifier.status == "validated")
profiles; anything else is rejected with 400 before any side effect."""
import importlib
import io
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))


def test_pilot_profile_restriction():
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

    oid = database.create_org("TestOrg")
    user_token = "user-api-token-123"
    database.create_user(oid, "user@testorg.com", auth.hash_password("password"), "user", user_token)

    submitted_jobs = []
    import worker
    worker.submit_job = lambda public_id, text, lang, explain, policy_name=None, override_jurisdiction=None, override_type=None: submitted_jobs.append((public_id, override_type))

    import app
    importlib.reload(app)
    client = app.app.test_client()
    headers = {"Authorization": f"Bearer {user_token}"}

    try:
        # Unit-level: helper resolves an original-11 profile and rejects a
        # non-pilot one (e.g. telecommunications_agreement, status=draft).
        assert app._resolve_pilot_type("lease") == "lease agreement"
        assert app._resolve_pilot_type("purchase agreement") == "purchase agreement"
        assert app._resolve_pilot_type("telecommunications agreement") is None
        assert app._resolve_pilot_type("not a real profile") is None

        # /api/v1/upload: a non-pilot type is rejected with 400, before any
        # usage-quota increment or job enqueue.
        usage_before = database.get_org_usage(oid)
        data = {"file": (io.BytesIO(b"Some contract text."), "contract.txt")}
        resp = client.post(
            "/api/v1/upload?type=telecommunications",
            data=data, headers=headers, content_type="multipart/form-data",
        )
        assert resp.status_code == 400, resp.status_code
        assert "not available in this pilot" in resp.json["error"]
        assert len(submitted_jobs) == 0
        usage_after = database.get_org_usage(oid)
        assert usage_before["contract_used"] == usage_after["contract_used"]

        # A pilot-available type (one of the 11) is accepted.
        data = {"file": (io.BytesIO(b"Some contract text."), "contract.txt")}
        resp = client.post(
            "/api/v1/upload?type=lease",
            data=data, headers=headers, content_type="multipart/form-data",
        )
        assert resp.status_code == 202, resp.status_code
        assert len(submitted_jobs) == 1
        assert submitted_jobs[0][1] == "lease"

        # /api/v1/result/<id>/retry: same rejection, before retry_analysis()
        # consumes a retry attempt.
        analysis_id = resp.json["id"]
        resp = client.post(
            f"/api/v1/result/{analysis_id}/retry",
            json={"type": "insurance agreement"},
            headers=headers,
        )
        assert resp.status_code == 400, resp.status_code
        assert "not available in this pilot" in resp.json["error"]
        assert len(submitted_jobs) == 1  # unchanged
    finally:
        os.remove(db_path)


if __name__ == "__main__":
    test_pilot_profile_restriction()
    print("test_pilot_profile_restriction OK")
