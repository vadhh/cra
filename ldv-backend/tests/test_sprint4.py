"""Unit tests for Sprint 4 Customer Experience features."""
import importlib
import io
import os
import sys
import tempfile
import json
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def test_sprint4_workflow():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ["LDV_SECRET_KEY"] = "test-secret-key-s4"
    os.environ.pop("LDV_ENCRYPTION_KEY", None)

    import crypto
    importlib.reload(crypto)

    import database
    importlib.reload(database)
    database.init_db()

    # Mock worker to prevent background worker threads running in the test
    import worker
    worker.submit_job = lambda public_id, text, lang, explain, policy_name=None: None

    import app
    importlib.reload(app)
    client = app.app.test_client()

    try:
        # 1. Create orgs and users
        org_id1 = database.create_org("Organization One")
        org_id2 = database.create_org("Organization Two")

        # Update limits on Org 1
        with database._conn() as conn:
            conn.execute(
                """UPDATE organizations 
                   SET contract_limit = 2, page_limit = 10, report_limit = 2 
                   WHERE id = ?""",
                (org_id1,)
            )

        u_manager_id = database.create_user(org_id1, "manager@org1.com", "hash", "manager", "tok-manager")
        u_reviewer_id = database.create_user(org_id1, "reviewer@org1.com", "hash", "reviewer", "tok-reviewer")
        u_analyst_id = database.create_user(org_id1, "analyst@org1.com", "hash", "analyst", "tok-analyst")
        
        u_org2_id = database.create_user(org_id2, "analyst@org2.com", "hash", "analyst", "tok-org2")
        u_admin_id = database.create_user(org_id1, "admin@system.com", "hash", "admin", "tok-admin")

        # --- Test 1: Upload Limits Enforcement ---
        # Log in as analyst on Org 1
        with client.session_transaction() as sess:
            sess["uid"] = u_analyst_id

        # First upload (1 page equivalent) -> should pass with 202
        data = io.BytesIO(b"Simple contract text. Paragraph one.")
        resp = client.post(
            "/api/v1/upload?client=ClientA&case_folder=Folder1",
            data={"file": (data, "agreement1.txt")}
        )
        assert resp.status_code == 202, resp.json
        analysis_id = resp.json["id"]

        # Manually complete the job in DB
        database.update_analysis(analysis_id, status="completed", risk_score=25, risk_label="LOW", result={})

        # Check in DB that client/folder got saved
        res_data = database.get_result(analysis_id)
        assert res_data["client"] == "ClientA"
        assert res_data["case_folder"] == "Folder1"

        # Check usage in DB
        usage = database.get_org_usage(org_id1)
        assert usage["contract_used"] == 1
        assert usage["page_used"] == 1

        # Second upload (12 pages equivalent) -> should fail (exceeds page limit of 10)
        large_data = io.BytesIO(b"Long contract " * 2000) # text len = 28000 -> 14 pages
        resp = client.post(
            "/api/v1/upload",
            data={"file": (large_data, "agreement2.txt")}
        )
        assert resp.status_code == 403, resp.status_code
        assert "page allowance exhausted" in resp.json["error"]

        # Upload a small one -> contract_used will reach 2
        data_small = io.BytesIO(b"Small text")
        resp = client.post(
            "/api/v1/upload",
            data={"file": (data_small, "agreement_small.txt")}
        )
        assert resp.status_code == 202, resp.json
        analysis_id_2 = resp.json["id"]
        # Manually complete
        database.update_analysis(analysis_id_2, status="completed", risk_score=50, risk_label="MEDIUM", result={})

        # Third upload (small) -> should fail (exceeds contract limit of 2)
        data_exceeded = io.BytesIO(b"Exceeded text")
        resp = client.post(
            "/api/v1/upload",
            data={"file": (data_exceeded, "agreement_exceeded.txt")}
        )
        assert resp.status_code == 403, resp.status_code
        assert "contract allowance exhausted" in resp.json["error"]

        # --- Test 2: Usage Endpoint ---
        # Manager gets usage
        with client.session_transaction() as sess:
            sess["uid"] = u_manager_id
        resp = client.get("/api/v1/usage")
        assert resp.status_code == 200, resp.json
        assert resp.json["contract_used"] == 2
        assert resp.json["contract_limit"] == 2

        # Analyst cannot get usage
        with client.session_transaction() as sess:
            sess["uid"] = u_analyst_id
        resp = client.get("/api/v1/usage")
        assert resp.status_code == 403, resp.status_code

        # --- Test 3: History Search & Tenant Isolation ---
        # Let's seed an analysis in Org 2
        with client.session_transaction() as sess:
            sess["uid"] = u_org2_id
        data_org2 = io.BytesIO(b"Org 2 contract text")
        resp = client.post(
            "/api/v1/upload?client=ClientB&case_folder=ProjectX",
            data={"file": (data_org2, "org2_doc.txt")}
        )
        assert resp.status_code == 202
        analysis_id_org2 = resp.json["id"]
        database.update_analysis(analysis_id_org2, status="completed", risk_score=10, risk_label="LOW", result={})

        # Log in back as Org 1 analyst and search history
        with client.session_transaction() as sess:
            sess["uid"] = u_analyst_id
        resp = client.get("/api/v1/history")
        assert resp.status_code == 200
        history = resp.json
        # Should only see the two completed/queued/failed files from Org 1
        assert len(history) == 2
        assert all(h["client"] == "ClientA" or h["client"] is None for h in history)

        # Search by client
        resp = client.get("/api/v1/history?client=ClientA")
        assert len(resp.json) == 1
        assert resp.json[0]["client"] == "ClientA"

        # Search by keyword
        resp = client.get("/api/v1/history?search=agreement_small")
        assert len(resp.json) == 1
        assert "agreement_small.txt" in resp.json[0]["original_filename"]

        # System admin searches history -> sees everything (both Org 1 and Org 2)
        with client.session_transaction() as sess:
            sess["uid"] = u_admin_id
        resp = client.get("/api/v1/history")
        assert len(resp.json) == 3

        # --- Test 4: Professional Review Workflow ---
        # Reviewer on Org 1 reviews Org 1 analysis
        with client.session_transaction() as sess:
            sess["uid"] = u_reviewer_id
        resp = client.post(
            f"/api/v1/result/{analysis_id}/review",
            json={"status": "confirmed", "comment": "Legally sound contract."}
        )
        assert resp.status_code == 200, resp.json

        # Retrieve and verify review status
        res_reviewed = database.get_result(analysis_id)
        assert res_reviewed["review_status"] == "confirmed"
        assert res_reviewed["reviewer_email"] == "reviewer@org1.com"
        assert res_reviewed["review_comment"] == "Legally sound contract."

        # Non-reviewer/non-admin attempts to review -> 403
        with client.session_transaction() as sess:
            sess["uid"] = u_analyst_id
        resp = client.post(
            f"/api/v1/result/{analysis_id}/review",
            json={"status": "rejected", "comment": "Analyst override"}
        )
        assert resp.status_code == 403

        # Reviewer from another org attempts to review -> 403 (tenant isolation)
        u_reviewer_org2_id = database.create_user(org_id2, "reviewer@org2.com", "hash", "reviewer", "tok-reviewer2")
        with client.session_transaction() as sess:
            sess["uid"] = u_reviewer_org2_id
        resp = client.post(
            f"/api/v1/result/{analysis_id}/review",
            json={"status": "rejected", "comment": "Cross-org hack"}
        )
        assert resp.status_code == 403

        # --- Test 5: PDF Report Generation & Limits ---
        # Generate report for reviewed analysis
        with client.session_transaction() as sess:
            sess["uid"] = u_analyst_id
        # We need mock analysis result data structure
        mock_pdf_payload = {
            "risk_score": 25,
            "risk_label": "LOW",
            "jurisdiction": "FR",
            "document_type": "nda",
            "review_status": "confirmed",
            "reviewer_email": "reviewer@org1.com",
            "review_comment": "Legally sound contract.",
            "reviewed_at": datetime.now(timezone.utc).isoformat()
        }
        resp = client.post("/api/v1/report", json=mock_pdf_payload)
        assert resp.status_code == 200
        assert resp.headers["Content-Disposition"] == "attachment; filename=contract_risk_report.pdf"

        # Check usage is incremented
        usage = database.get_org_usage(org_id1)
        assert usage["report_used"] == 1

        # Trigger second report -> usage is 2 (equals limit)
        resp = client.post("/api/v1/report", json=mock_pdf_payload)
        assert resp.status_code == 200

        # Trigger third report -> 403 (exceeded)
        resp = client.post("/api/v1/report", json=mock_pdf_payload)
        assert resp.status_code == 403
        assert "professional report allowance exhausted" in resp.json["error"]

    finally:
        os.remove(db_path)

if __name__ == "__main__":
    test_sprint4_workflow()
    print("test_sprint4_workflow OK")
