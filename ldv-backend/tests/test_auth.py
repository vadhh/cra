"""End-to-end auth + tenant isolation (CR-01). Run: python tests/test_auth.py"""
import os
import sys
import tempfile

# Add parent directory to path so imports resolve when run from ldv-backend/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
_DB_PATH = _TMP.name

import importlib
import database  # noqa: E402
importlib.reload(database)
import auth      # noqa: E402
importlib.reload(auth)
import app as app_module  # noqa: E402
importlib.reload(app_module)
app_module.app.config["TESTING"] = True
app_module.app.testing = True

def setup_module(module):
    os.environ["LDV_DB_PATH"] = _DB_PATH
    os.environ["LDV_SECRET_KEY"] = "test-key"
    database.init_db()

client = app_module.app.test_client()


def _user(org, email, role):
    # Idempotent: skip if user already exists
    existing_user = database.get_user_by_email(email)
    if existing_user:
        return existing_user["org_id"]
    existing = database.get_org_by_name(org)
    oid = existing["id"] if existing else database.create_org(org)
    database.create_user(oid, email, auth.hash_password("pw"), role, f"tok-{email}")
    return oid


def _analysis_for_org(oid):
    doc = database.save_document(
        original_filename="c.txt", stored_filename="c.txt", file_path="/tmp/c.txt",
        file_size=3, file_type=".txt", language="en", extracted_text="hi",
        org_id=oid, owner_id=None,
    )
    return database.save_analysis(doc, "Indonesia", "contract", 40, "MEDIUM", {"ok": True})


def setup():
    org_a = _user("OrgA", "a@a.com", "user")
    _user("OrgB", "b@b.com", "user")
    _user("OrgA", "admin@a.com", "admin")
    return org_a


def test_anonymous_blocked():
    assert client.get("/api/v1/result/whatever").status_code == 401
    assert client.post("/api/v1/upload").status_code == 401


def test_bad_login():
    assert client.post("/login", json={"email": "a@a.com", "password": "nope"}).status_code == 401
    assert client.post("/login", json={"email": "ghost@a.com", "password": "pw"}).status_code == 401


def test_owner_and_cross_org_and_admin():
    org_a = setup()
    pub = _analysis_for_org(org_a)

    # Owner (same org) — 200
    c = app_module.app.test_client()
    assert c.post("/login", json={"email": "a@a.com", "password": "pw"}).status_code == 200
    assert c.get("/api/v1/result/" + pub).status_code == 200

    # Cross-org user — 403 even with a valid UUID
    c2 = app_module.app.test_client()
    c2.post("/login", json={"email": "b@b.com", "password": "pw"})
    assert c2.get("/api/v1/result/" + pub).status_code == 403

    # Admin — 200 for any org
    # Bypass /login via session_transaction: role "admin" is unconditionally
    # MFA-mandatory (auth.is_mfa_mandatory), so a plain /login POST here would
    # only set mfa_enroll_pending_uid, not uid, when run outside pytest (no
    # PYTEST_CURRENT_TEST escape hatch). This test is about tenant-isolation
    # authorization, not the login/MFA flow, so bypassing is correct.
    admin_user = database.get_user_by_email("admin@a.com")
    c3 = app_module.app.test_client()
    with c3.session_transaction() as sess:
        sess["uid"] = admin_user["id"]
    assert c3.get("/api/v1/result/" + pub).status_code == 200

    # API token auth works programmatically
    assert client.get(
        "/api/v1/result/" + pub, headers={"Authorization": "Bearer tok-a@a.com"}
    ).status_code == 200


def test_admin_endpoints_gated():
    # user token -> 403, admin token -> 200
    assert client.get("/api/v1/stats", headers={"Authorization": "Bearer tok-a@a.com"}).status_code == 403
    assert client.get("/api/v1/stats", headers={"Authorization": "Bearer tok-admin@a.com"}).status_code == 200


def test_get_logout():
    c = app_module.app.test_client()
    res = c.post("/login", json={"email": "a@a.com", "password": "pw"})
    assert res.status_code == 200
    with c.session_transaction() as sess:
        assert sess.get("uid") is not None
    res_logout = c.get("/logout")
    assert res_logout.status_code == 302
    assert "/login" in res_logout.headers.get("Location", "")
    with c.session_transaction() as sess:
        assert sess.get("uid") is None


if __name__ == "__main__":
    setup_module(None)
    test_anonymous_blocked()
    setup()  # Seed users before test_bad_login to ensure existing-user password test
    test_bad_login()
    test_owner_and_cross_org_and_admin()
    test_admin_endpoints_gated()
    test_get_logout()
    print("OK")
