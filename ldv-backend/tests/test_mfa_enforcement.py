"""End-to-end coverage for org-wide MFA enforcement (mfa-required toggle)
and the /api/v1/mfa/disable mandatory-MFA guard.

Run directly (NOT via pytest — auth.is_mfa_mandatory() has a
PYTEST_CURRENT_TEST escape hatch that would mask the enrollment assertion):
    python3 tests/test_mfa_enforcement.py
"""
import os
import sys
import tempfile

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
    existing_user = database.get_user_by_email(email)
    if existing_user:
        return existing_user["org_id"]
    existing = database.get_org_by_name(org)
    oid = existing["id"] if existing else database.create_org(org)
    database.create_user(oid, email, auth.hash_password("pw"), role, f"tok-{email}")
    return oid


def setup():
    org_a = _user("MfaOrgA", "mgr-a@a.com", "manager")
    org_b = _user("MfaOrgB", "mgr-b@b.com", "manager")
    _user("MfaOrgA", "root@a.com", "admin")
    _user("MfaOrgA", "plain@a.com", "user")
    return org_a, org_b


def test_manager_can_set_own_org():
    org_a, _ = setup()
    user = database.get_user_by_email("mgr-a@a.com")
    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]
    resp = c.post(f"/api/v1/admin/organizations/{org_a}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 200, resp.get_json()
    assert database.org_mfa_required(org_a) is True
    database.set_org_mfa_required(org_a, False)


def test_manager_forbidden_other_org():
    org_a, org_b = setup()
    user = database.get_user_by_email("mgr-a@a.com")
    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]
    resp = c.post(f"/api/v1/admin/organizations/{org_b}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 403, resp.get_json()
    assert database.org_mfa_required(org_b) is False


def test_admin_can_set_any_org():
    org_a, org_b = setup()
    user = database.get_user_by_email("root@a.com")
    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]
    resp = c.post(f"/api/v1/admin/organizations/{org_b}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 200, resp.get_json()
    assert database.org_mfa_required(org_b) is True
    database.set_org_mfa_required(org_b, False)


def test_toggle_forces_enrollment_on_next_login():
    org_a, _ = setup()
    database.set_org_mfa_required(org_a, True)
    c = app_module.app.test_client()
    resp = c.post("/login", json={"email": "plain@a.com", "password": "pw"})
    assert resp.status_code == 200, resp.get_json()
    assert resp.get_json().get("mfa_enroll_required") is True
    database.set_org_mfa_required(org_a, False)


def test_disable_blocked_when_org_mandatory():
    org_a, _ = setup()
    user = database.get_user_by_email("plain@a.com")
    database.update_user_mfa(user["id"], "dummy-secret", "[]")
    database.set_org_mfa_required(org_a, True)

    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]

    resp = c.post("/api/v1/mfa/disable", json={"password": "pw"})
    assert resp.status_code == 403, resp.get_json()
    assert database.get_user_by_id(user["id"])["mfa_secret"] is not None

    database.set_org_mfa_required(org_a, False)
    database.update_user_mfa(user["id"], None, None)


def test_disable_allowed_when_not_mandatory():
    org_a, _ = setup()
    user = database.get_user_by_email("plain@a.com")
    database.update_user_mfa(user["id"], "dummy-secret", "[]")
    database.set_org_mfa_required(org_a, False)

    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]

    resp = c.post("/api/v1/mfa/disable", json={"password": "pw"})
    assert resp.status_code == 200, resp.get_json()
    assert database.get_user_by_id(user["id"])["mfa_secret"] is None


def test_account_page_requires_login():
    c = app_module.app.test_client()
    resp = c.get("/account", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")

    c.post("/login", json={"email": "plain@a.com", "password": "pw"})
    resp2 = c.get("/account")
    assert resp2.status_code == 200


if __name__ == "__main__":
    setup_module(None)
    test_manager_can_set_own_org()
    test_manager_forbidden_other_org()
    test_admin_can_set_any_org()
    test_toggle_forces_enrollment_on_next_login()
    test_disable_blocked_when_org_mandatory()
    test_disable_allowed_when_not_mandatory()
    test_account_page_requires_login()
    print("OK")
