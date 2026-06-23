"""Self-check for retention: expires_at backfill, dry-run, and real purge."""
import importlib
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

fd, db_path = tempfile.mkstemp(suffix=".db")
os.close(fd)
os.environ["LDV_DB_PATH"] = db_path
os.environ["LDV_RETENTION_DAYS"] = "30"
os.environ.pop("LDV_ENCRYPTION_KEY", None)

import database
importlib.reload(database)
database.init_db()

exp_id = database.save_document("old.txt", "s1.txt", "/tmp/s1.txt", 10, ".txt", "EN", "text")
live_id = database.save_document("new.txt", "s2.txt", "/tmp/s2.txt", 10, ".txt", "EN", "text")

# Force the first doc to be already expired.
with sqlite3.connect(db_path) as c:
    c.execute("UPDATE documents SET expires_at = datetime('now', '-1 day') WHERE id = ?", (exp_id,))
    c.commit()

# Dry-run reports the expired doc and deletes nothing.
dry = database.purge_expired(dry_run=True)
assert [v["document_id"] for v in dry] == [exp_id], dry
with sqlite3.connect(db_path) as c:
    assert c.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 2

# Real purge removes only the expired doc.
real = database.purge_expired()
assert [v["document_id"] for v in real] == [exp_id], real
with sqlite3.connect(db_path) as c:
    remaining = [r[0] for r in c.execute("SELECT id FROM documents")]
assert remaining == [live_id], remaining

# delete_analysis cascades doc + returns its file path.
pid = database.save_analysis(live_id, "EN", "Contract", 50, "MEDIUM", {"ok": True})
info = database.delete_analysis(pid)
assert info is not None and info["document_id"] == live_id, info
with sqlite3.connect(db_path) as c:
    assert c.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
assert database.delete_analysis(pid) is None

os.remove(db_path)
print("test_retention OK")
