"""Checks for manage.py provisioning. Run: python tests/test_manage.py"""
import os
import sys
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name
os.environ["LDV_ADMIN_EMAIL"] = "root@sydeco.com"
os.environ["LDV_ADMIN_PASSWORD"] = "rootpw"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import database  # noqa: E402
import manage    # noqa: E402

database.init_db()


def test_seed_admin_is_idempotent():
    manage.seed_admin()
    u = database.get_user_by_email("root@sydeco.com")
    assert u is not None and u["role"] == "admin"
    assert database.get_org_by_name("Sydeco") is not None
    manage.seed_admin()  # second call must not raise / duplicate
    assert database.get_user_by_email("root@sydeco.com") is not None


def test_create_org_and_user():
    manage.create_org_cmd("Client1")
    manage.create_user_cmd("user@client1.com", "Client1", "user")
    u = database.get_user_by_email("user@client1.com")
    assert u is not None and u["api_token"]


if __name__ == "__main__":
    test_seed_admin_is_idempotent()
    test_create_org_and_user()
    print("OK")
