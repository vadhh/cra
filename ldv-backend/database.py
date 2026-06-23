"""
database.py — SQLite persistence for Sydeco LightML Contract Risk Analyzer.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta

import crypto

DB_PATH = os.getenv("LDV_DB_PATH", os.path.join(os.path.dirname(__file__), "sydeco.db"))

_SCHEMA = """
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
    result_json   TEXT,
    status        TEXT NOT NULL DEFAULT 'completed',
    error_message TEXT,
    analyzed_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS organizations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id        INTEGER NOT NULL REFERENCES organizations(id),
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user',
    api_token     TEXT UNIQUE,
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


def retention_days() -> int:
    """Days a document is kept before purge. Invalid/≤0 → 30."""
    try:
        n = int(os.getenv("LDV_RETENTION_DAYS", "30"))
        return n if n > 0 else 30
    except ValueError:
        return 30


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(_SCHEMA)
        # Migrate pre-public_id databases: results are addressed by unguessable
        # UUIDs, never by the enumerable integer primary key.
        cols = {row[1] for row in conn.execute("PRAGMA table_info(analyses)")}
        if "public_id" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN public_id TEXT")
        for (row_id,) in conn.execute(
            "SELECT id FROM analyses WHERE public_id IS NULL"
        ).fetchall():
            conn.execute(
                "UPDATE analyses SET public_id = ? WHERE id = ?",
                (uuid.uuid4().hex, row_id),
            )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_analyses_public_id "
            "ON analyses(public_id)"
        )
        if "status" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN status TEXT DEFAULT 'completed'")
        if "error_message" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN error_message TEXT")
        # Ownership columns for tenant isolation (CR-01). Added if missing so
        # pre-auth databases keep working; existing rows stay NULL-org
        # (admin-visible only) until backfilled by manage.py seed-admin.
        doc_cols = {row[1] for row in conn.execute("PRAGMA table_info(documents)")}
        if "org_id" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN org_id INTEGER REFERENCES organizations(id)")
        if "owner_id" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN owner_id INTEGER REFERENCES users(id)")
        if "expires_at" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN expires_at TIMESTAMP")
            # Backfill existing rows from their upload time + retention window.
            conn.execute(
                "UPDATE documents SET expires_at = datetime(uploaded_at, ?) "
                "WHERE expires_at IS NULL",
                (f"+{retention_days()} days",),
            )


@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH, timeout=30.0)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()


def save_document(
    original_filename: str,
    stored_filename: str,
    file_path: str,
    file_size: int,
    file_type: str,
    language: str | None = None,
    extracted_text: str | None = None,
    org_id: int | None = None,
    owner_id: int | None = None,
) -> int:
    enc_text = crypto.enc_str(extracted_text) if extracted_text is not None else None
    expires_at = (datetime.utcnow() + timedelta(days=retention_days())).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with _conn() as db:
        cur = db.execute(
            """INSERT INTO documents
               (original_filename, stored_filename, file_path, file_size,
                file_type, language, extracted_text, org_id, owner_id, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (original_filename, stored_filename, file_path, file_size,
             file_type, language, enc_text, org_id, owner_id, expires_at),
        )
        return cur.lastrowid


def save_analysis(
    document_id: int,
    jurisdiction: str | None,
    document_type: str | None,
    risk_score: int | None,
    risk_label: str | None,
    result: dict | None,
    status: str = "completed",
    error_message: str | None = None,
) -> str:
    public_id = uuid.uuid4().hex
    res_enc = crypto.enc_str(json.dumps(result)) if result is not None else None
    with _conn() as db:
        db.execute(
            """INSERT INTO analyses
               (public_id, document_id, jurisdiction, document_type, risk_score, risk_label, result_json, status, error_message)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (public_id, document_id, jurisdiction, document_type, risk_score, risk_label,
             res_enc, status, error_message),
        )
        return public_id


def update_analysis(
    public_id: str,
    status: str,
    jurisdiction: str | None = None,
    document_type: str | None = None,
    risk_score: int | None = None,
    risk_label: str | None = None,
    result: dict | None = None,
    error_message: str | None = None,
) -> None:
    updates = ["status = ?"]
    params = [status]
    if jurisdiction is not None:
        updates.append("jurisdiction = ?")
        params.append(jurisdiction)
    if document_type is not None:
        updates.append("document_type = ?")
        params.append(document_type)
    if risk_score is not None:
        updates.append("risk_score = ?")
        params.append(risk_score)
    if risk_label is not None:
        updates.append("risk_label = ?")
        params.append(risk_label)
    if result is not None:
        updates.append("result_json = ?")
        params.append(crypto.enc_str(json.dumps(result)))
    if error_message is not None:
        updates.append("error_message = ?")
        params.append(error_message)
    params.append(public_id)
    query = f"UPDATE analyses SET {', '.join(updates)} WHERE public_id = ?"
    with _conn() as db:
        db.execute(query, tuple(params))


def get_result(public_id: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.jurisdiction,
                      a.document_type, a.result_json, a.analyzed_at, a.status, a.error_message,
                      d.original_filename, d.file_size, d.file_type, d.language,
                      d.extracted_text, d.uploaded_at, d.org_id
               FROM analyses a
               JOIN documents d ON a.document_id = d.id
               WHERE a.public_id = ?""",
            (public_id,),
        ).fetchone()
        if row is None:
            return None
        d = dict(row)
        if d.get("extracted_text") is not None:
            d["extracted_text"] = crypto.dec_str(d["extracted_text"])
        if d.get("result_json") is not None:
            d["result_json"] = crypto.dec_str(d["result_json"])
        return d


def get_stats() -> dict:
    with _conn() as db:
        total_docs     = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        total_analyses = db.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
        avg            = db.execute("SELECT AVG(risk_score) FROM analyses").fetchone()[0]
        dist           = db.execute(
            "SELECT risk_label, COUNT(*) AS cnt FROM analyses GROUP BY risk_label"
        ).fetchall()
        return {
            "total_documents":   total_docs,
            "total_analyses":    total_analyses,
            "average_risk_score": round(avg, 1) if avg else 0,
            "distribution":      {r["risk_label"]: r["cnt"] for r in dist},
        }


def get_recent(limit: int = 10) -> list[dict]:
    with _conn() as db:
        rows = db.execute(
            """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.document_type,
                      a.jurisdiction, a.analyzed_at,
                      d.original_filename, d.file_type
               FROM analyses a
               JOIN documents d ON a.document_id = d.id
               ORDER BY a.analyzed_at DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


def create_org(name: str) -> int:
    with _conn() as db:
        cur = db.execute("INSERT INTO organizations (name) VALUES (?)", (name,))
        return cur.lastrowid


def get_org_by_name(name: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            "SELECT * FROM organizations WHERE name = ?", (name,)
        ).fetchone()
        return dict(row) if row else None


def create_user(org_id: int, email: str, password_hash: str,
                role: str, api_token: str) -> int:
    with _conn() as db:
        cur = db.execute(
            """INSERT INTO users (org_id, email, password_hash, role, api_token)
               VALUES (?, ?, ?, ?, ?)""",
            (org_id, email.strip().lower(), password_hash, role, api_token),
        )
        return cur.lastrowid


def get_user_by_email(email: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
        return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    with _conn() as db:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None


def get_user_by_token(token: str) -> dict | None:
    if not token:
        return None
    with _conn() as db:
        row = db.execute(
            "SELECT * FROM users WHERE api_token = ?", (token,)
        ).fetchone()
        return dict(row) if row else None


def delete_analysis(public_id: str) -> dict | None:
    """Delete one analysis and its parent document. Returns the document's
    file_path so the caller can unlink it, or None if public_id is unknown."""
    with _conn() as db:
        row = db.execute(
            """SELECT d.id AS document_id, d.file_path
               FROM analyses a JOIN documents d ON a.document_id = d.id
               WHERE a.public_id = ?""",
            (public_id,),
        ).fetchone()
        if row is None:
            return None
        doc_id = row["document_id"]
        db.execute("DELETE FROM analyses WHERE document_id = ?", (doc_id,))
        db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        return {"file_path": row["file_path"], "document_id": doc_id}


def purge_expired(dry_run: bool = False) -> list[dict]:
    """Documents past their expires_at. dry_run lists without deleting.
    Caller unlinks the returned file_paths. ponytail: row+file delete + VACUUM
    is the secure-erase ceiling — SSD overwrite-in-place is unreliable; rely on
    full-disk/volume encryption for the rest."""
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    with _conn() as db:
        rows = db.execute(
            """SELECT id AS document_id, file_path, expires_at FROM documents
               WHERE expires_at IS NOT NULL AND expires_at < ?""",
            (now,),
        ).fetchall()
        victims = [dict(r) for r in rows]
        if dry_run or not victims:
            return victims
        ids = [v["document_id"] for v in victims]
        marks = ",".join("?" * len(ids))
        db.execute(f"DELETE FROM analyses WHERE document_id IN ({marks})", tuple(ids))
        db.execute(f"DELETE FROM documents WHERE id IN ({marks})", tuple(ids))
    # VACUUM cannot run inside the _conn() transaction; reclaim on a fresh conn.
    with sqlite3.connect(DB_PATH) as c:
        c.execute("VACUUM")
    return victims
