"""Unit checks for auth.py. Run: python tests/test_auth_unit.py"""
import os
import sys
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database  # noqa: E402
import auth      # noqa: E402
from flask import Flask, jsonify, g  # noqa: E402

database.init_db()


def _seed():
    oid = database.create_org("Org1")
    h = auth.hash_password("s3cret")
    database.create_user(oid, "u@org1.com", h, "user", "tok-u")
    database.create_user(oid, "a@org1.com", auth.hash_password("admin-pw"), "admin", "tok-a")
    return oid


def _app():
    app = Flask(__name__)
    auth.configure_secret_key(app)

    @app.route("/me")
    @auth.login_required
    def me():
        return jsonify({"email": g.user["email"]})

    @app.route("/admin-only")
    @auth.admin_required
    def admin_only():
        return jsonify({"ok": True})

    return app


def test_verify_login():
    _seed()
    assert auth.verify_login("u@org1.com", "s3cret") is not None
    assert auth.verify_login("u@org1.com", "wrong") is None
    assert auth.verify_login("ghost@org1.com", "s3cret") is None


def test_decorators_and_token_auth():
    app = _app()
    c = app.test_client()

    assert c.get("/me").status_code == 401                                  # anonymous
    assert c.get("/me", headers={"Authorization": "Bearer tok-u"}).status_code == 200
    assert c.get("/admin-only", headers={"Authorization": "Bearer tok-u"}).status_code == 403
    assert c.get("/admin-only", headers={"Authorization": "Bearer tok-a"}).status_code == 200


if __name__ == "__main__":
    test_verify_login()
    test_decorators_and_token_auth()
    print("OK")
