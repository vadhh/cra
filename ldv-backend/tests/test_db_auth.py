"""Behavioral checks for the auth-related database layer. Run: python tests/test_db_auth.py"""
import os
import sys
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
_DB_PATH = _TMP.name

# Add parent directory to path to import database
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import importlib
import database  # noqa: E402
importlib.reload(database)

def setup_module(module):
    os.environ["LDV_DB_PATH"] = _DB_PATH
    database.init_db()


def test_org_and_user_roundtrip():
    oid = database.create_org("Acme")
    assert isinstance(oid, int)
    assert database.get_org_by_name("Acme")["id"] == oid

    uid = database.create_user(oid, "Person@Acme.com", "hash123", "user", "tok-abc")
    by_email = database.get_user_by_email("person@acme.com")  # lookup is case-insensitive
    assert by_email is not None and by_email["id"] == uid
    assert database.get_user_by_id(uid)["email"] == "person@acme.com"
    assert database.get_user_by_token("tok-abc")["id"] == uid
    assert database.get_user_by_token("nope") is None


def test_document_ownership_flows_to_result():
    oid = database.create_org("Beta")
    uid = database.create_user(oid, "b@beta.com", "h", "user", "tok-beta")
    doc_id = database.save_document(
        original_filename="x.txt", stored_filename="s.txt", file_path="/tmp/s.txt",
        file_size=3, file_type=".txt", language="en", extracted_text="hey",
        org_id=oid, owner_id=uid,
    )
    pub = database.save_analysis(doc_id, "Indonesia", "contract", 50, "MEDIUM", {"ok": True})
    row = database.get_result(pub)
    assert row["org_id"] == oid


if __name__ == "__main__":
    setup_module(None)
    test_org_and_user_roundtrip()
    test_document_ownership_flows_to_result()
    print("OK")
