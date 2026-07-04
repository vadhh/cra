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

def get_db_path() -> str:
    return os.getenv("LDV_DB_PATH", os.path.join(os.path.dirname(__file__), "sydeco.db"))

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
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL UNIQUE,
    retention_days INTEGER,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id             INTEGER NOT NULL REFERENCES organizations(id),
    email              TEXT NOT NULL UNIQUE,
    password_hash      TEXT NOT NULL,
    role               TEXT NOT NULL DEFAULT 'user',
    api_token          TEXT UNIQUE,
    active             INTEGER NOT NULL DEFAULT 1,
    mfa_secret         TEXT,
    mfa_recovery_codes TEXT,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ts          TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    action      TEXT NOT NULL,
    user_id     INTEGER REFERENCES users(id),
    org_id      INTEGER REFERENCES organizations(id),
    resource_id TEXT,
    ip          TEXT,
    detail      TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts DESC);

CREATE TABLE IF NOT EXISTS download_links (
    token       TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL,
    expires_at  INTEGER NOT NULL,
    one_time    INTEGER DEFAULT 0,
    revoked     INTEGER DEFAULT 0,
    used        INTEGER DEFAULT 0
);
"""


def retention_days() -> int:
    """Global default retention days from env. Invalid/≤0 → 30."""
    try:
        n = int(os.getenv("LDV_RETENTION_DAYS", "30"))
        return n if n > 0 else 30
    except ValueError:
        return 30


def org_retention_days(org_id: int | None) -> int:
    """Per-org override if set, else global default."""
    if org_id is None:
        return retention_days()
    try:
        with _conn() as db:
            row = db.execute(
                "SELECT retention_days FROM organizations WHERE id = ?", (org_id,)
            ).fetchone()
        if row and row[0] is not None and int(row[0]) > 0:
            return int(row[0])
    except Exception:
        pass
    return retention_days()


def set_org_retention(org_id: int, days: int) -> None:
    with _conn() as db:
        db.execute(
            "UPDATE organizations SET retention_days = ? WHERE id = ?", (days, org_id)
        )


def set_org_mfa_required(org_id: int, required: bool) -> None:
    with _conn() as db:
        db.execute(
            "UPDATE organizations SET mfa_required = ? WHERE id = ?", (1 if required else 0, org_id)
        )


def org_mfa_required(org_id: int | None) -> bool:
    if org_id is None:
        return False
    try:
        with _conn() as db:
            row = db.execute(
                "SELECT mfa_required FROM organizations WHERE id = ?", (org_id,)
            ).fetchone()
        return bool(row and row[0])
    except Exception:
        return False


def init_db() -> None:
    with sqlite3.connect(get_db_path()) as conn:
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
        if "progress_pct" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN progress_pct INTEGER DEFAULT 0")
        if "progress_stage" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN progress_stage TEXT DEFAULT 'queued'")

        # Check if result_json has an outdated NOT NULL constraint
        info = conn.execute("PRAGMA table_info(analyses)").fetchall()
        result_json_not_null = False
        for row in info:
            if row[1] == "result_json" and row[3] == 1:
                result_json_not_null = True
                break

        if result_json_not_null:
            conn.execute("PRAGMA foreign_keys=OFF")
            conn.execute("ALTER TABLE analyses RENAME TO analyses_old")
            conn.executescript("""
            CREATE TABLE analyses (
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
            CREATE UNIQUE INDEX IF NOT EXISTS idx_analyses_public_id ON analyses(public_id);
            """)
            conn.execute("""
            INSERT INTO analyses (id, public_id, document_id, jurisdiction, document_type, risk_score, risk_label, result_json, status, error_message, analyzed_at)
            SELECT id, public_id, document_id, jurisdiction, document_type, risk_score, risk_label, result_json, status, error_message, analyzed_at
            FROM analyses_old
            """)
            conn.execute("DROP TABLE analyses_old")
            conn.execute("PRAGMA foreign_keys=ON")

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
        org_cols = {row[1] for row in conn.execute("PRAGMA table_info(organizations)")}
        if "retention_days" not in org_cols:
            conn.execute("ALTER TABLE organizations ADD COLUMN retention_days INTEGER")
        if "mfa_required" not in org_cols:
            conn.execute("ALTER TABLE organizations ADD COLUMN mfa_required INTEGER DEFAULT 0")

        user_cols = {row[1] for row in conn.execute("PRAGMA table_info(users)")}
        if "mfa_secret" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN mfa_secret TEXT")
        if "mfa_recovery_codes" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN mfa_recovery_codes TEXT")
        if "download_disabled" not in user_cols:
            conn.execute("ALTER TABLE users ADD COLUMN download_disabled INTEGER DEFAULT 0")

        # Sprint 4: Subscription usage tracking, case history, and professional review workflow
        for col, default_val in [
            ("contract_limit", 100),
            ("page_limit", 500),
            ("report_limit", 50),
            ("contract_used", 0),
            ("page_used", 0),
            ("report_used", 0)
        ]:
            if col not in org_cols:
                conn.execute(f"ALTER TABLE organizations ADD COLUMN {col} INTEGER DEFAULT {default_val}")

        if "client" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN client TEXT")
        if "case_folder" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN case_folder TEXT")

        if "review_status" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN review_status TEXT NOT NULL DEFAULT 'unreviewed'")
        if "reviewer_email" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN reviewer_email TEXT")
        if "review_comment" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN review_comment TEXT")
        if "reviewed_at" not in cols:
            conn.execute("ALTER TABLE analyses ADD COLUMN reviewed_at TIMESTAMP")

        # Auto-seed a default admin user if the users table is completely empty
        # (useful for fresh Docker deployments like Hugging Face Spaces)
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            admin_email = os.getenv("LDV_ADMIN_EMAIL", "admin@example.com").strip().lower()
            admin_password = os.getenv("LDV_ADMIN_PASSWORD", "password")
            
            # Ensure default organization exists
            org_row = conn.execute("SELECT id FROM organizations WHERE name = 'Sydeco'").fetchone()
            if not org_row:
                cur_org = conn.execute("INSERT INTO organizations (name) VALUES ('Sydeco')")
                org_id = cur_org.lastrowid
            else:
                org_id = org_row[0]
                
            from werkzeug.security import generate_password_hash
            import secrets
            hashed = generate_password_hash(admin_password)
            token = secrets.token_urlsafe(32)
            
            conn.execute(
                """INSERT INTO users (org_id, email, password_hash, role, api_token)
                   VALUES (?, ?, ?, ?, ?)""",
                (org_id, admin_email, hashed, "admin", token)
            )
            print(f"Auto-seeded default admin user: {admin_email} (password: {admin_password})")



@contextmanager
def _conn():
    c = sqlite3.connect(get_db_path(), timeout=30.0)
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
    client: str | None = None,
    case_folder: str | None = None,
) -> int:
    enc_text = crypto.enc_str(extracted_text) if extracted_text is not None else None
    expires_at = (datetime.utcnow() + timedelta(days=org_retention_days(org_id))).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
    with _conn() as db:
        cur = db.execute(
            """INSERT INTO documents
               (original_filename, stored_filename, file_path, file_size,
                file_type, language, extracted_text, org_id, owner_id, expires_at, client, case_folder)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (original_filename, stored_filename, file_path, file_size,
             file_type, language, enc_text, org_id, owner_id, expires_at, client, case_folder),
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
    progress_pct: int | None = None,
    progress_stage: str | None = None,
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
    if progress_pct is not None:
        updates.append("progress_pct = ?")
        params.append(progress_pct)
    if progress_stage is not None:
        updates.append("progress_stage = ?")
        params.append(progress_stage)
    params.append(public_id)
    query = f"UPDATE analyses SET {', '.join(updates)} WHERE public_id = ?"
    with _conn() as db:
        db.execute(query, tuple(params))


def get_result(public_id: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.jurisdiction,
                      a.document_type, a.result_json, a.analyzed_at, a.status, a.error_message,
                      a.progress_pct, a.progress_stage, a.review_status, a.reviewer_email,
                      a.review_comment, a.reviewed_at,
                      d.original_filename, d.file_size, d.file_type, d.language,
                      d.extracted_text, d.uploaded_at, d.org_id, d.client, d.case_folder
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


def check_connection() -> bool:
    """Execute a simple query to verify SQLite database connectivity."""
    try:
        with _conn() as db:
            db.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_stats(org_id: int | None = None) -> dict:
    with _conn() as db:
        if org_id is not None:
            total_docs     = db.execute("SELECT COUNT(*) FROM documents WHERE org_id = ?", (org_id,)).fetchone()[0]
            total_analyses = db.execute(
                "SELECT COUNT(*) FROM analyses a JOIN documents d ON a.document_id = d.id WHERE d.org_id = ?",
                (org_id,)
            ).fetchone()[0]
            avg            = db.execute(
                "SELECT AVG(risk_score) FROM analyses a JOIN documents d ON a.document_id = d.id WHERE d.org_id = ?",
                (org_id,)
            ).fetchone()[0]
            dist           = db.execute(
                """SELECT COALESCE(risk_label, 'PENDING') AS label, COUNT(*) AS cnt 
                   FROM analyses a JOIN documents d ON a.document_id = d.id 
                   WHERE d.org_id = ? GROUP BY risk_label""",
                (org_id,)
            ).fetchall()
        else:
            total_docs     = db.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            total_analyses = db.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]
            avg            = db.execute("SELECT AVG(risk_score) FROM analyses").fetchone()[0]
            dist           = db.execute(
                "SELECT COALESCE(risk_label, 'PENDING') AS label, COUNT(*) AS cnt FROM analyses GROUP BY risk_label"
            ).fetchall()

        return {
            "total_documents":   total_docs,
            "total_analyses":    total_analyses,
            "average_risk_score": round(avg, 1) if avg else 0,
            "distribution":      {r["label"]: r["cnt"] for r in dist},
        }


def get_recent(limit: int = 10, org_id: int | None = None) -> list[dict]:
    with _conn() as db:
        if org_id is not None:
            rows = db.execute(
                """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.document_type,
                          a.jurisdiction, a.analyzed_at, a.status, a.error_message,
                          d.original_filename, d.file_type
                   FROM analyses a
                   JOIN documents d ON a.document_id = d.id
                   WHERE d.org_id = ?
                   ORDER BY a.analyzed_at DESC LIMIT ?""",
                (org_id, limit),
            ).fetchall()
        else:
            rows = db.execute(
                """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.document_type,
                          a.jurisdiction, a.analyzed_at, a.status, a.error_message,
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


def update_user_mfa(user_id: int, mfa_secret: str | None, mfa_recovery_codes: str | None) -> None:
    with _conn() as db:
        db.execute(
            "UPDATE users SET mfa_secret = ?, mfa_recovery_codes = ? WHERE id = ?",
            (mfa_secret, mfa_recovery_codes, user_id)
        )


def save_download_link(token: str, analysis_id: str, expires_at: int, one_time: int) -> None:
    with _conn() as db:
        db.execute(
            "INSERT INTO download_links (token, analysis_id, expires_at, one_time) VALUES (?, ?, ?, ?)",
            (token, analysis_id, expires_at, one_time)
        )


def get_download_link(token: str) -> dict | None:
    with _conn() as db:
        row = db.execute(
            "SELECT * FROM download_links WHERE token = ?", (token,)
        ).fetchone()
        return dict(row) if row else None


def mark_download_link_used(token: str) -> None:
    with _conn() as db:
        db.execute("UPDATE download_links SET used = 1 WHERE token = ?", (token,))


def revoke_download_link(token: str) -> None:
    with _conn() as db:
        db.execute("UPDATE download_links SET revoked = 1 WHERE token = ?", (token,))


def revoke_all_download_links(analysis_id: str) -> None:
    with _conn() as db:
        db.execute("UPDATE download_links SET revoked = 1 WHERE analysis_id = ?", (analysis_id,))


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


def get_document_file_info(public_id: str) -> dict | None:
    """Return file_path, file_type, original_filename, org_id for download."""
    with _conn() as db:
        row = db.execute(
            """SELECT d.file_path, d.file_type, d.original_filename, d.org_id
               FROM analyses a JOIN documents d ON a.document_id = d.id
               WHERE a.public_id = ?""",
            (public_id,),
        ).fetchone()
        return dict(row) if row else None


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
    with sqlite3.connect(get_db_path()) as c:
        c.execute("VACUUM")
    return victims


def write_audit(
    action: str,
    user_id: int | None = None,
    org_id: int | None = None,
    resource_id: str | None = None,
    ip: str | None = None,
    detail: str | None = None,
) -> None:
    """Append one row to audit_log. Fire-and-forget — never raises.
    Dual-writes high-impact events to a durable append-only log file."""
    high_impact_actions = {
        "delete", "cite.verify", "user.role_change",
        "org.retention_change", "org.mfa_required_change", "user.suspend", "user.unsuspend",
        "mfa.disable", "user.mfa_reset", "user.download.disable"
    }
    
    if action in high_impact_actions:
        try:
            durable_path = os.path.join(os.path.dirname(get_db_path()), "audit_durable.log")
            log_line = json.dumps({
                "ts": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                "action": action,
                "user_id": user_id,
                "org_id": org_id,
                "resource_id": resource_id,
                "ip": ip,
                "detail": detail
            })
            with open(durable_path, "a") as f:
                f.write(log_line + "\n")
        except Exception as e:
            import logging
            logging.critical("DURABLE AUDIT WRITE FAILURE: Could not write to audit_durable.log. Error: %s", str(e))

    try:
        with _conn() as db:
            db.execute(
                "INSERT INTO audit_log (action, user_id, org_id, resource_id, ip, detail) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (action, user_id, org_id, resource_id, ip, detail),
            )
    except Exception as e:
        import logging
        logging.critical("AUDIT DATABASE WRITE FAILURE: Could not write action '%s'. Error: %s", action, str(e))


def get_audit_log(limit: int = 100, org_id: int | None = None) -> list[dict]:
    """Return recent audit rows, newest first. Admins pass org_id=None for all orgs."""
    with _conn() as db:
        if org_id is not None:
            rows = db.execute(
                "SELECT * FROM audit_log WHERE org_id = ? ORDER BY ts DESC LIMIT ?",
                (org_id, limit),
            ).fetchall()
        else:
            rows = db.execute(
                "SELECT * FROM audit_log ORDER BY ts DESC LIMIT ?", (limit,)
            ).fetchall()
        return [{**dict(r), "timestamp": r["ts"]} for r in rows]


def get_all_users() -> list[dict]:
    with _conn() as db:
        rows = db.execute("SELECT u.*, o.name AS org_name FROM users u JOIN organizations o ON u.org_id = o.id").fetchall()
        return [dict(r) for r in rows]


def get_users_by_org(org_id: int) -> list[dict]:
    with _conn() as db:
        rows = db.execute("SELECT u.*, o.name AS org_name FROM users u JOIN organizations o ON u.org_id = o.id WHERE u.org_id = ?", (org_id,)).fetchall()
        return [dict(r) for r in rows]


def get_all_orgs() -> list[dict]:
    with _conn() as db:
        rows = db.execute("SELECT * FROM organizations").fetchall()
        return [dict(r) for r in rows]


def update_user_status(user_id: int, active: int) -> None:
    with _conn() as db:
        db.execute("UPDATE users SET active = ? WHERE id = ?", (active, user_id))


def update_user_role(user_id: int, role: str) -> None:
    with _conn() as db:
        db.execute("UPDATE users SET role = ? WHERE id = ?", (role, user_id))


def update_user_download_access(user_id: int, download_disabled: int) -> None:
    with _conn() as db:
        db.execute("UPDATE users SET download_disabled = ? WHERE id = ?", (download_disabled, user_id))


def count_active_admins() -> int:
    with _conn() as db:
        row = db.execute("SELECT COUNT(*) FROM users WHERE role = 'admin' AND active = 1").fetchone()
        return row[0] if row else 0


def cleanup_stuck_analyses() -> None:
    """Fail analysis records abandoned by a crashed/killed process.

    Runs on every process start, including each gunicorn worker boot — so it
    must not touch jobs a sibling worker is still actively processing.
    # ponytail: age-gated instead of per-worker-owned; a job older than this
    # threshold is either done or truly stuck (L4 hard-caps at
    # LDV_GENERATION_TIMEOUT+30s, default 330s). Add per-worker leases if a
    # legitimate job ever needs to run longer than 30 min.
    """
    with _conn() as db:
        db.execute(
            "UPDATE analyses SET status = 'failed', error_message = 'Task interrupted during server reload.' "
            "WHERE status IN ('running', 'queued') AND analyzed_at < datetime('now', '-30 minutes')"
        )


def get_org_usage(org_id: int) -> dict:
    with _conn() as db:
        row = db.execute(
            """SELECT contract_limit, page_limit, report_limit,
                      contract_used, page_used, report_used
               FROM organizations WHERE id = ?""",
            (org_id,),
        ).fetchone()
        if not row:
            return {}
        return dict(row)


def increment_org_usage(org_id: int, contracts: int = 0, pages: int = 0, reports: int = 0) -> None:
    with _conn() as db:
        db.execute(
            """UPDATE organizations
               SET contract_used = contract_used + ?,
                   page_used = page_used + ?,
                   report_used = report_used + ?
               WHERE id = ?""",
            (contracts, pages, reports, org_id)
        )


def update_analysis_review(public_id: str, status: str, comment: str | None, reviewer_email: str | None) -> bool:
    with _conn() as db:
        cur = db.execute(
            """UPDATE analyses
               SET review_status = ?,
                   review_comment = ?,
                   reviewer_email = ?,
                   reviewed_at = CURRENT_TIMESTAMP
               WHERE public_id = ?""",
            (status, comment, reviewer_email, public_id)
        )
        return cur.rowcount > 0


def search_history(org_id: int | None, params: dict) -> list[dict]:
    query = """SELECT a.public_id AS id, a.risk_score, a.risk_label, a.document_type,
                      a.jurisdiction, a.analyzed_at, a.status, a.error_message,
                      a.review_status, a.reviewer_email, a.review_comment, a.reviewed_at,
                      d.original_filename, d.file_size, d.file_type, d.language,
                      d.uploaded_at, d.client, d.case_folder
               FROM analyses a
               JOIN documents d ON a.document_id = d.id"""
    
    where_clauses = []
    args = []
    
    if org_id is not None:
        where_clauses.append("d.org_id = ?")
        args.append(org_id)
        
    search = params.get("search")
    if search:
        where_clauses.append("(d.original_filename LIKE ? OR d.client LIKE ? OR d.case_folder LIKE ? OR a.error_message LIKE ?)")
        s_arg = f"%{search}%"
        args.extend([s_arg, s_arg, s_arg, s_arg])
        
    client = params.get("client")
    if client:
        where_clauses.append("d.client = ?")
        args.append(client)
        
    case_folder = params.get("case_folder")
    if case_folder:
        where_clauses.append("d.case_folder = ?")
        args.append(case_folder)
        
    doctype = params.get("type")
    if doctype:
        where_clauses.append("a.document_type = ?")
        args.append(doctype)
        
    status = params.get("status")
    if status:
        where_clauses.append("a.status = ?")
        args.append(status)
        
    min_score = params.get("min_score")
    if min_score is not None:
        try:
            where_clauses.append("a.risk_score >= ?")
            args.append(int(min_score))
        except ValueError:
            pass
            
    max_score = params.get("max_score")
    if max_score is not None:
        try:
            where_clauses.append("a.risk_score <= ?")
            args.append(int(max_score))
        except ValueError:
            pass
            
    if where_clauses:
        query += " WHERE " + " AND ".join(where_clauses)
        
    query += " ORDER BY a.analyzed_at DESC"
    
    try:
        limit = min(int(params.get("limit", 50)), 200)
    except (ValueError, TypeError):
        limit = 50
    query += " LIMIT ?"
    args.append(limit)
    
    try:
        offset = int(params.get("offset", 0))
        if offset > 0:
            query += " OFFSET ?"
            args.append(offset)
    except (ValueError, TypeError):
        pass
        
    with _conn() as db:
        rows = db.execute(query, tuple(args)).fetchall()
        return [dict(r) for r in rows]
