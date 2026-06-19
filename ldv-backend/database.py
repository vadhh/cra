"""
database.py — SQLite persistence for Sydeco LightML Contract Risk Analyzer.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(__file__), "sydeco.db")

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
    uploaded_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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


@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
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
) -> int:
    with _conn() as db:
        cur = db.execute(
            """INSERT INTO documents
               (original_filename, stored_filename, file_path, file_size,
                file_type, language, extracted_text)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (original_filename, stored_filename, file_path, file_size,
             file_type, language, extracted_text),
        )
        return cur.lastrowid


def save_analysis(
    document_id: int,
    jurisdiction: str | None,
    document_type: str | None,
    risk_score: int | None,
    risk_label: str | None,
    result: dict,
) -> str:
    public_id = uuid.uuid4().hex
    with _conn() as db:
        db.execute(
            """INSERT INTO analyses
               (public_id, document_id, jurisdiction, document_type, risk_score, risk_label, result_json)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (public_id, document_id, jurisdiction, document_type, risk_score, risk_label,
             json.dumps(result)),
        )
        return public_id


def get_result(public_id: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.jurisdiction,
                      a.document_type, a.result_json, a.analyzed_at,
                      d.original_filename, d.file_size, d.file_type, d.language,
                      d.extracted_text, d.uploaded_at
               FROM analyses a
               JOIN documents d ON a.document_id = d.id
               WHERE a.public_id = ?""",
            (public_id,),
        ).fetchone()
        return dict(row) if row else None


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
