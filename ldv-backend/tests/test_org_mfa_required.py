"""Self-check for set_org_mfa_required + org_mfa_required roundtrip."""
import importlib
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["LDV_DB_PATH"] = db_path
os.environ.pop("LDV_ENCRYPTION_KEY", None)

import database
importlib.reload(database)
database.init_db()

oid = database.create_org("AcmeCo")

assert database.org_mfa_required(oid) is False

database.set_org_mfa_required(oid, True)
assert database.org_mfa_required(oid) is True

database.set_org_mfa_required(oid, False)
assert database.org_mfa_required(oid) is False

os.remove(db_path)
print("test_org_mfa_required OK")
