"""
test_consent.py — Unit and Integration tests for TOS / Privacy Policy user consent API and upload gate.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import database
import auth
import app as flask_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    db_file = str(tmp_path / "test_consent.db")
    monkeypatch.setenv("LDV_DB_PATH", db_file)
    monkeypatch.setattr(database, "get_db_path", lambda: db_file)
    
    database.init_db()
    
    # Create test user
    org_id = database.create_org("Test Consent Org")
    user_id = database.create_user(org_id, "consent_user@test.com", "pass123", "analyst", "test_token_123")
    user = database.get_user_by_id(user_id)
    
    flask_app.app.config["TESTING"] = True
    with flask_app.app.test_client() as c:
        with c.session_transaction() as sess:
            sess["uid"] = user_id
        yield c, user_id


def test_consent_get_and_post(client):
    c, user_id = client
    
    # 1. Check initial consent status (False)
    res = c.get("/api/v1/consent")
    assert res.status_code == 200
    data = res.get_json()
    assert data["consented"] is False
    assert data["version"] == "1.0"
    
    # 2. Reject incomplete consent (missing privacy_accepted)
    res = c.post("/api/v1/consent", json={"tos_accepted": True, "privacy_accepted": False})
    assert res.status_code == 400
    
    # 3. Post valid consent
    res = c.post("/api/v1/consent", json={"tos_accepted": True, "privacy_accepted": True, "version": "1.0"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "recorded"
    assert data["tos_accepted"] is True
    assert data["privacy_accepted"] is True
    
    # 4. Check consent status again (True)
    res = c.get("/api/v1/consent")
    assert res.status_code == 200
    assert res.get_json()["consented"] is True


def test_consent_enforcement_gate(client, monkeypatch):
    c, user_id = client
    
    # Enable consent enforcement explicitly and disable test bypass flags
    monkeypatch.setenv("LDV_ENFORCE_CONSENT", "1")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.setenv("LDV_TESTING", "0")
    flask_app.app.config["TESTING"] = False
    
    headers = {"Origin": "http://localhost"}
    
    # Upload should fail with 403 CONSENT_REQUIRED before accepting consent
    res = c.post(
        "/api/v1/upload",
        data={"file": (pytest.importorskip("io").BytesIO(b"Sample contract text"), "test.txt")},
        headers=headers,
    )
    assert res.status_code == 403
    err_json = res.get_json()
    assert err_json.get("code") == "CONSENT_REQUIRED"
    
    # Accept consent
    res_consent = c.post(
        "/api/v1/consent",
        json={"tos_accepted": True, "privacy_accepted": True},
        headers=headers,
    )
    assert res_consent.status_code == 200
    
    # Upload should now pass the consent gate (progressing to file extraction)
    res_after = c.post(
        "/api/v1/upload",
        data={"file": (pytest.importorskip("io").BytesIO(b"Sample contract text"), "test.txt")},
        headers=headers,
    )
    assert res_after.status_code in (200, 202)  # Accepted or processed
