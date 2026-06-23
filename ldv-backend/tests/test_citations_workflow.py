"""Self-check for citations list, verification workflow and permissions (CIT-04 / CR-02)."""
import importlib
import os
import sys
import tempfile
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def test_citations_workflow():
    # 1. Create a temporary database path
    fd_db, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd_db)
    os.environ["LDV_DB_PATH"] = db_path
    os.environ["LDV_SECRET_KEY"] = "test-secret-key-123"
    os.environ.pop("LDV_ENCRYPTION_KEY", None)

    import database
    importlib.reload(database)
    database.init_db()

    # 2. Create a temporary CSV path for citations to avoid mutating live data
    fd_csv, csv_path = tempfile.mkstemp(suffix=".csv")
    os.close(fd_csv)
    
    # Seed mock citations CSV
    fieldnames = ["finding_id", "jurisdiction", "article", "source", "note", "status"]
    mock_rows = [
        {"finding_id": "leonine_profit", "jurisdiction": "FR", "article": "Art. 1844-1", "source": "Civil Code", "note": "Profit exclusion", "status": "draft"},
        {"finding_id": "payment_terms", "jurisdiction": "ID", "article": "Pasal 1234", "source": "KUHPerdata", "note": "Payment requirements", "status": "verified"},
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(mock_rows)

    # Patch citation_db to use our temporary CSV
    import detector.citation_db as citation_db
    importlib.reload(citation_db)
    citation_db._CSV_PATH = citation_db.Path(csv_path)
    citation_db._DB = None  # Clear cache

    # Seed org and users
    import auth
    importlib.reload(auth)
    oid = database.create_org("TestOrg")
    
    user_token = "user-token"
    database.create_user(oid, "user@testorg.com", auth.hash_password("password"), "user", user_token)
    
    admin_token = "admin-token"
    database.create_user(oid, "admin@testorg.com", auth.hash_password("password"), "admin", admin_token)

    # Import app to initialize routes using correct env
    import app
    importlib.reload(app)
    client = app.app.test_client()

    try:
        # --- Test 1: verify_citation function directly ---
        # Clear database cache first
        citation_db._DB = None
        assert citation_db.citations_for("leonine_profit", "FR", include_drafts=True)[0]["status"] == "draft"
        
        # Verify it
        res = citation_db.verify_citation("leonine_profit", "FR")
        assert res is True
        assert citation_db.citations_for("leonine_profit", "FR")[0]["status"] == "verified"

        # --- Test 2: GET /api/citations endpoint ---
        # 2a. Anonymous blocked
        resp = client.get("/api/citations")
        assert resp.status_code == 401

        # 2b. Normal user sees only verified
        resp = client.get("/api/citations", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        user_cites = resp.json
        # Under user, the newly verified 'leonine_profit' and originally verified 'payment_terms' are visible.
        # Let's revert 'leonine_profit' to draft in CSV to verify distinction.
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([
                {"finding_id": "leonine_profit", "jurisdiction": "FR", "article": "Art. 1844-1", "source": "Civil Code", "note": "Profit exclusion", "status": "draft"},
                {"finding_id": "payment_terms", "jurisdiction": "ID", "article": "Pasal 1234", "source": "KUHPerdata", "note": "Payment requirements", "status": "verified"},
            ])
        citation_db._DB = None  # Clear cache

        resp = client.get("/api/citations", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        user_cites = resp.json
        assert len(user_cites) == 1
        assert user_cites[0]["finding_id"] == "payment_terms"

        # 2c. Admin sees both drafts and verified
        resp = client.get("/api/citations", headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        admin_cites = resp.json
        assert len(admin_cites) == 2

        # --- Test 3: POST /api/citations/verify endpoint ---
        # 3a. Normal user blocked (403 Forbidden)
        resp = client.post("/api/citations/verify", json={"finding_id": "leonine_profit", "jurisdiction": "FR"}, headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 403

        # 3b. Admin verify succeeds
        resp = client.post("/api/citations/verify", json={"finding_id": "leonine_profit", "jurisdiction": "FR"}, headers={"Authorization": f"Bearer {admin_token}"})
        assert resp.status_code == 200
        assert resp.json["ok"] is True

        # Now normal user can see it since it's verified
        citation_db._DB = None  # Clear cache
        resp = client.get("/api/citations", headers={"Authorization": f"Bearer {user_token}"})
        assert resp.status_code == 200
        assert len(resp.json) == 2

    finally:
        # Clean up
        os.remove(db_path)
        os.remove(csv_path)

if __name__ == "__main__":
    test_citations_workflow()
    print("test_citations_workflow OK")
