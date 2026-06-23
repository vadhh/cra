"""Self-test for database schema migration of status tracking columns (CR-10)."""
import importlib
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

def test_db_migration_flow():
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    os.environ["LDV_DB_PATH"] = db_path

    # Create an old-schema database (without status/error_message in analyses)
    old_schema = """
    CREATE TABLE IF NOT EXISTS documents (
        id                INTEGER PRIMARY KEY AUTOINCREMENT,
        original_filename TEXT NOT NULL,
        stored_filename   TEXT NOT NULL,
        file_path         TEXT NOT NULL,
        file_size         INTEGER NOT NULL,
        file_type         TEXT NOT NULL,
        language          TEXT,
        extracted_text    TEXT,
        uploaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        expires_at        TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS analyses (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        public_id     TEXT UNIQUE,
        document_id   INTEGER NOT NULL REFERENCES documents(id),
        jurisdiction  TEXT,
        document_type TEXT,
        risk_score    INTEGER,
        risk_label    TEXT,
        result_json   TEXT NOT NULL,
        analyzed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """

    with sqlite3.connect(db_path) as conn:
        conn.executescript(old_schema)

    import database
    importlib.reload(database)

    # Verify table info before init_db migration runs
    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(analyses)")}
        assert "status" not in cols, "status column should not be in the initial old database schema"
        assert "error_message" not in cols, "error_message column should not be in the initial old database schema"

    # Trigger init_db() which should migrate columns
    database.init_db()

    # Verify table info after migration
    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(analyses)")}
        assert "status" in cols, "status column was not created/migrated"
        assert "error_message" in cols, "error_message column was not created/migrated"

    # Clean up
    os.remove(db_path)

if __name__ == "__main__":
    test_db_migration_flow()
    print("test_db_migration OK")
