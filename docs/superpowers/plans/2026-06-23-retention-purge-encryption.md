# Retention / Purge / Encryption-at-rest Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Encrypt uploaded documents, extracted text, and analysis results at rest; add a configurable retention window with scheduled, CLI, and HTTP purge paths.

**Architecture:** A new `crypto.py` wraps Fernet (`MultiFernet` for free key rotation) with passthrough-when-unkeyed. `database.py` encrypts/decrypts at the persistence boundary and gains an `expires_at` retention column plus purge/delete helpers. `app.py` encrypts on-disk file bytes, exposes `DELETE /api/result/<id>`, and reports degraded mode via `/health`. `manage.py` gets `purge`, `purge-doc`, and `gen-key` subcommands.

**Tech Stack:** Python 3, Flask, SQLite (`sqlite3`), `cryptography` (Fernet). Tests are plain `python3` assert scripts under `ldv-backend/tests/` (repo convention — no pytest).

## Global Constraints

- All new env vars fail safe: `LDV_ENCRYPTION_KEY` unset → plaintext + one WARNING log (not fatal); `LDV_RETENTION_DAYS` invalid/≤0 → fall back to `30`.
- `cryptography` is pinned to `==48.0.0` (already installed; making it a direct dep).
- Encryption lives only in `crypto.py` and the `database.py` boundary + the single file-write site in `app.py`. No other module imports Fernet.
- `expires_at` is stored as `"YYYY-MM-DD HH:MM:SS"` (space-separated, UTC) so it string-compares correctly against SQLite `datetime()` and against `uploaded_at` (`CURRENT_TIMESTAMP`).
- Working directory for all commands: `/home/stardhoom/LDV/ldv-backend`.
- Run `python3` commands from `ldv-backend/` so flat imports (`import crypto`, `import database`) resolve.

---

### Task 1: `crypto.py` encryption module + dependency pin

**Files:**
- Create: `ldv-backend/crypto.py`
- Modify: `ldv-backend/requirements.txt` (append one line)
- Test: `ldv-backend/tests/test_crypto.py`

**Interfaces:**
- Consumes: nothing (leaf module).
- Produces:
  - `is_enabled() -> bool`
  - `enc_str(s: str) -> str` / `dec_str(s: str) -> str`
  - `enc_bytes(b: bytes) -> bytes` / `dec_bytes(b: bytes) -> bytes`
  - Module global `_loaded: bool` — tests set `crypto._loaded = False` to force a re-read of `LDV_ENCRYPTION_KEY` after changing it.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_crypto.py`:

```python
"""Self-check for crypto.py: round-trip, plaintext fallback, key rotation."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import Fernet
import crypto

KEY_A = Fernet.generate_key().decode()
KEY_B = Fernet.generate_key().decode()

# --- plaintext mode (no key) ---
os.environ.pop("LDV_ENCRYPTION_KEY", None)
crypto._loaded = False
assert crypto.is_enabled() is False
assert crypto.enc_str("hello") == "hello"
assert crypto.dec_str("hello") == "hello"
assert crypto.enc_bytes(b"hi") == b"hi"

# --- encrypted round-trip ---
os.environ["LDV_ENCRYPTION_KEY"] = KEY_A
crypto._loaded = False
assert crypto.is_enabled() is True
tok = crypto.enc_str("secret")
assert tok != "secret" and tok.startswith("gAAAAA")
assert crypto.dec_str(tok) == "secret"
assert crypto.dec_bytes(crypto.enc_bytes(b"%PDF-1.7")) == b"%PDF-1.7"

# --- legacy plaintext passes through even with a key set ---
assert crypto.dec_str("not a token") == "not a token"
assert crypto.dec_bytes(b"%PDF-1.7") == b"%PDF-1.7"

# --- rotation: token made under A still decrypts under [B, A] ---
os.environ["LDV_ENCRYPTION_KEY"] = f"{KEY_B},{KEY_A}"
crypto._loaded = False
assert crypto.dec_str(tok) == "secret"
new_tok = crypto.enc_str("again")          # encrypted under primary B
os.environ["LDV_ENCRYPTION_KEY"] = KEY_B   # drop A
crypto._loaded = False
assert crypto.dec_str(new_tok) == "again"

print("test_crypto OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/stardhoom/LDV/ldv-backend && python3 tests/test_crypto.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'crypto'`.

- [ ] **Step 3: Write minimal implementation**

Create `ldv-backend/crypto.py`:

```python
"""crypto.py — symmetric encryption-at-rest for documents/results (SEC-02).

Keyed from LDV_ENCRYPTION_KEY: a comma-separated list of urlsafe-base64 Fernet
keys. The first key is primary (used for all new encryption); the rest are
decrypt-only, which is the whole key-rotation story. Unset = passthrough
plaintext + one warning, so localhost dev needs no key.
"""
from __future__ import annotations

import logging
import os

from cryptography.fernet import Fernet, MultiFernet

logger = logging.getLogger(__name__)

# Fernet tokens are urlsafe-base64 of a payload starting with version byte 0x80,
# which always renders as this prefix. ponytail: prefix heuristic distinguishes
# our ciphertext from legacy plaintext (%PDF, PK, raw text) for zero-migration
# rollout; a token-shaped-but-corrupt value still raises InvalidToken on decrypt
# rather than being silently passed through.
_MAGIC_B = b"gAAAAA"
_MAGIC_S = "gAAAAA"

_fernet: MultiFernet | None = None
_loaded = False


def _get() -> MultiFernet | None:
    global _fernet, _loaded
    if not _loaded:
        raw = os.getenv("LDV_ENCRYPTION_KEY", "").strip()
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if keys:
            _fernet = MultiFernet([Fernet(k.encode()) for k in keys])
        else:
            _fernet = None
            logger.warning(
                "LDV_ENCRYPTION_KEY unset — documents/results stored in "
                "PLAINTEXT. Set it before any real deployment."
            )
        _loaded = True
    return _fernet


def is_enabled() -> bool:
    return _get() is not None


def enc_str(s: str) -> str:
    f = _get()
    return f.encrypt(s.encode()).decode() if f else s


def dec_str(s: str) -> str:
    f = _get()
    if f is None:
        return s
    if s.startswith(_MAGIC_S):
        return f.decrypt(s.encode()).decode()
    return s


def enc_bytes(b: bytes) -> bytes:
    f = _get()
    return f.encrypt(b) if f else b


def dec_bytes(b: bytes) -> bytes:
    f = _get()
    if f is None:
        return b
    if b.startswith(_MAGIC_B):
        return f.decrypt(b)
    return b
```

Append to `ldv-backend/requirements.txt`:

```
cryptography==48.0.0
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd /home/stardhoom/LDV/ldv-backend && python3 tests/test_crypto.py`
Expected: prints `test_crypto OK`, exit 0.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/crypto.py ldv-backend/tests/test_crypto.py ldv-backend/requirements.txt
git commit -m "feat(cr04): crypto.py Fernet encryption-at-rest helper (SEC-02)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 2: `database.py` — encryption boundary, retention column, purge/delete helpers

**Files:**
- Modify: `ldv-backend/database.py`
- Test: `ldv-backend/tests/test_retention.py`

**Interfaces:**
- Consumes: `crypto.enc_str` / `crypto.dec_str` (Task 1).
- Produces:
  - `retention_days() -> int`
  - `save_document(...)` now also persists `expires_at` and encrypts `extracted_text` (signature unchanged).
  - `save_analysis(...)` now encrypts `result_json` (signature unchanged).
  - `get_result(public_id) -> dict | None` returns **decrypted** `extracted_text` and `result_json`.
  - `delete_analysis(public_id: str) -> dict | None` → `{"file_path": str, "document_id": int}` or `None`.
  - `purge_expired(dry_run: bool = False) -> list[dict]` → each item `{"document_id": int, "file_path": str, "expires_at": str}`.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_retention.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/stardhoom/LDV/ldv-backend && python3 tests/test_retention.py`
Expected: FAIL — `AttributeError: module 'database' has no attribute 'purge_expired'`.

- [ ] **Step 3: Write minimal implementation**

In `ldv-backend/database.py`, change the imports block (top of file) to add `crypto` and datetime helpers:

```python
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta

import crypto
```

Add `expires_at` to the `documents` table in `_SCHEMA` (the `CREATE TABLE IF NOT EXISTS documents (...)` block) — append the column after `uploaded_at`:

```python
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
```

Add a retention helper just above `init_db()`:

```python
def retention_days() -> int:
    """Days a document is kept before purge. Invalid/≤0 → 30."""
    try:
        n = int(os.getenv("LDV_RETENTION_DAYS", "30"))
        return n if n > 0 else 30
    except ValueError:
        return 30
```

In `init_db()`, add an `expires_at` migration right after the `owner_id` block (still inside the `with sqlite3.connect(DB_PATH) as conn:` body):

```python
        if "expires_at" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN expires_at TIMESTAMP")
            # Backfill existing rows from their upload time + retention window.
            conn.execute(
                "UPDATE documents SET expires_at = datetime(uploaded_at, ?) "
                "WHERE expires_at IS NULL",
                (f"+{retention_days()} days",),
            )
```

Replace the body of `save_document(...)` (keep the signature) so it encrypts the text and sets `expires_at`:

```python
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
```

In `save_analysis(...)`, encrypt the JSON — change the `json.dumps(result)` argument so the VALUES tuple reads:

```python
            (public_id, document_id, jurisdiction, document_type, risk_score, risk_label,
             crypto.enc_str(json.dumps(result))),
```

In `get_result(...)`, decrypt before returning — replace `return dict(row) if row else None` with:

```python
        if row is None:
            return None
        d = dict(row)
        if d.get("extracted_text") is not None:
            d["extracted_text"] = crypto.dec_str(d["extracted_text"])
        d["result_json"] = crypto.dec_str(d["result_json"])
        return d
```

Add the two new helpers at the end of `database.py`:

```python
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
        db.execute(f"DELETE FROM analyses WHERE document_id IN ({marks})", ids)
        db.execute(f"DELETE FROM documents WHERE id IN ({marks})", ids)
    # VACUUM cannot run inside the _conn() transaction; reclaim on a fresh conn.
    with sqlite3.connect(DB_PATH) as c:
        c.execute("VACUUM")
    return victims
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd /home/stardhoom/LDV/ldv-backend && python3 tests/test_retention.py && python3 tests/test_crypto.py`
Expected: `test_retention OK` then `test_crypto OK`, exit 0.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/database.py ldv-backend/tests/test_retention.py
git commit -m "feat(cr04): encrypt text/results at rest + expires_at retention + purge helpers (SEC-02/05)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 3: `app.py` — encrypt file bytes, DELETE endpoint, /health degraded flags

**Files:**
- Modify: `ldv-backend/app.py` (imports ~line 21; file write ~267; new route after `api_result` ~329; `/health` ~426)

**Interfaces:**
- Consumes: `crypto.enc_bytes` / `crypto.is_enabled` (Task 1); `database.delete_analysis`, `database.retention_days`, `database.get_result` (Task 2).
- Produces: `DELETE /api/result/<analysis_id>` → `{"deleted": true, "id": <id>}` (200), 404 unknown, 403 cross-org; `/health` gains `encryption.enabled` and `retention_days`.

- [ ] **Step 1: Add the import**

In `ldv-backend/app.py`, add `import crypto` next to the existing `import database` / `import auth` lines (around line 21):

```python
import database
import auth
import crypto
```

- [ ] **Step 2: Encrypt the file bytes at the single write site**

Replace the upload write (around line 267):

```python
    with open(file_path, "wb") as f:
        f.write(data)
```

with:

```python
    with open(file_path, "wb") as f:
        f.write(crypto.enc_bytes(data))
```

- [ ] **Step 3: Add the DELETE route**

Immediately after the `api_result` function (after its `return jsonify(...)` near line 329), add:

```python
@app.route("/api/result/<analysis_id>", methods=["DELETE"])
@auth.login_required
def api_delete_result(analysis_id: str):
    row = database.get_result(analysis_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    user = g.user
    if user["role"] != "admin" and row.get("org_id") != user["org_id"]:
        return jsonify({"error": "Forbidden"}), 403
    info = database.delete_analysis(analysis_id)
    if info and info.get("file_path"):
        try:
            os.remove(info["file_path"])
        except FileNotFoundError:
            pass
    logger.info("DELETE: id=%s org=%s by=%s", analysis_id, row.get("org_id"), user["email"])
    return jsonify({"deleted": True, "id": analysis_id})
```

- [ ] **Step 4: Add degraded-mode flags to /health**

In the `/health` route, extend the returned dict (after `"sydeco_mlp": mlp_available(),`):

```python
        "sydeco_mlp":        mlp_available(),
        "encryption":        {"enabled": crypto.is_enabled()},
        "retention_days":    database.retention_days(),
```

- [ ] **Step 5: Verify the app imports and /health reports the flags**

Run:

```bash
cd /home/stardhoom/LDV/ldv-backend && python3 - <<'PY'
import os
os.environ.pop("LDV_ENCRYPTION_KEY", None)
import app
c = app.app.test_client()
h = c.get("/health").get_json()
assert h["encryption"] == {"enabled": False}, h
assert h["retention_days"] == 30, h
# DELETE without auth must not 200.
assert c.delete("/api/result/deadbeef").status_code in (401, 403), "auth gate missing"
print("app smoke OK")
PY
```

Expected: prints `app smoke OK`. (A `LDV_ENCRYPTION_KEY unset` WARNING line above it is expected.)

- [ ] **Step 6: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/app.py
git commit -m "feat(cr04): encrypt uploaded file bytes, DELETE /api/result, /health degraded flags

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 4: `manage.py` — purge, purge-doc, gen-key subcommands

**Files:**
- Modify: `ldv-backend/manage.py`

**Interfaces:**
- Consumes: `database.purge_expired`, `database.delete_analysis` (Task 2). `os` is already imported at the top of `manage.py`.
- Produces: CLI `python manage.py purge [--dry-run]`, `python manage.py purge-doc <public_id>`, `python manage.py gen-key`.

- [ ] **Step 1: Add the Fernet import**

In `ldv-backend/manage.py`, add to the imports block (after `import database`):

```python
from cryptography.fernet import Fernet
```

- [ ] **Step 2: Add the three command functions**

Add after `create_user_cmd(...)` (before `main()`):

```python
def purge_cmd(dry_run: bool) -> None:
    victims = database.purge_expired(dry_run=dry_run)
    for v in victims:
        if not dry_run and v.get("file_path"):
            try:
                os.remove(v["file_path"])
            except FileNotFoundError:
                pass
        tag = "would purge" if dry_run else "PURGE"
        print(f"{tag}: doc_id={v['document_id']} file={v['file_path']} expired={v['expires_at']}")
    verb = "eligible" if dry_run else "purged"
    print(f"{'(dry-run) ' if dry_run else ''}{len(victims)} document(s) {verb}.")


def purge_doc_cmd(public_id: str) -> None:
    info = database.delete_analysis(public_id)
    if info is None:
        sys.exit(f"No analysis with id {public_id}.")
    if info.get("file_path"):
        try:
            os.remove(info["file_path"])
        except FileNotFoundError:
            pass
    print(f"Purged analysis {public_id} (doc_id={info['document_id']}).")


def gen_key_cmd() -> None:
    print(Fernet.generate_key().decode())
```

- [ ] **Step 3: Wire the subparsers and dispatch**

In `main()`, after the `create-user` parser setup (after `pu.add_argument("--role", ...)`), add:

```python
    pp = sub.add_parser("purge")
    pp.add_argument("--dry-run", action="store_true")
    pd = sub.add_parser("purge-doc")
    pd.add_argument("public_id")
    sub.add_parser("gen-key")
```

And in the dispatch chain (after the `create-user` branch), add:

```python
    elif args.cmd == "purge":
        purge_cmd(args.dry_run)
    elif args.cmd == "purge-doc":
        purge_doc_cmd(args.public_id)
    elif args.cmd == "gen-key":
        gen_key_cmd()
```

- [ ] **Step 4: Verify the commands work end-to-end**

Run:

```bash
cd /home/stardhoom/LDV/ldv-backend && python3 - <<'PY'
import subprocess, tempfile, os, sqlite3, sys
fd, db = tempfile.mkstemp(suffix=".db"); os.close(fd)
env = {**os.environ, "LDV_DB_PATH": db, "LDV_RETENTION_DAYS": "30"}
env.pop("LDV_ENCRYPTION_KEY", None)
def run(*a):
    return subprocess.run([sys.executable, "manage.py", *a], env=env,
                          capture_output=True, text=True)
# gen-key prints a usable Fernet key
out = run("gen-key").stdout.strip()
from cryptography.fernet import Fernet; Fernet(out.encode()); print("gen-key OK")
# seed a doc, force-expire it, purge
import database; database.init_db()
did = database.save_document("x.txt","s.txt","/tmp/s.txt",1,".txt","EN","t")
with sqlite3.connect(db) as c:
    c.execute("UPDATE documents SET expires_at=datetime('now','-1 day') WHERE id=?", (did,)); c.commit()
assert "1 document(s) eligible" in run("purge","--dry-run").stdout
assert "1 document(s) purged" in run("purge").stdout
with sqlite3.connect(db) as c:
    assert c.execute("SELECT COUNT(*) FROM documents").fetchone()[0] == 0
os.remove(db); print("manage purge OK")
PY
```

Expected: prints `gen-key OK` then `manage purge OK`.

- [ ] **Step 5: Commit**

```bash
cd /home/stardhoom/LDV
git add ldv-backend/manage.py
git commit -m "feat(cr04): manage.py purge / purge-doc / gen-key commands (SEC-05)

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

### Task 5: Document the new env vars and operations in CLAUDE.md

**Files:**
- Modify: `CLAUDE.md` (env var table; user-provisioning section; TODO P0 #3)

**Interfaces:** none (docs only).

- [ ] **Step 1: Add env vars to the table**

In the `**Environment variables (security defaults — all fail closed):**` table, add two rows (after the `LDV_DB_PATH` row):

```markdown
| `LDV_ENCRYPTION_KEY` | unset | Comma-separated Fernet keys (first = primary, rest decrypt-only for rotation) encrypting stored documents, extracted text, and results. **Unset = plaintext + startup warning + `encryption.enabled:false` in `/health`.** Mint with `python manage.py gen-key`. |
| `LDV_RETENTION_DAYS` | `30` | Days a document is kept before `manage.py purge` deletes it. Invalid/≤0 falls back to 30. |
```

- [ ] **Step 2: Document purge operations**

After the `python manage.py create-user ...` block, add:

````markdown
**Retention / purge (CR-04):** Documents carry an `expires_at` (`uploaded_at + LDV_RETENTION_DAYS`). Delete expired data on a schedule via cron:
```bash
python manage.py purge --dry-run     # preview what would be deleted
python manage.py purge               # delete expired docs + files, VACUUM, log
python manage.py purge-doc <uuid>    # immediate single deletion (by analysis id)
```
Example crontab (daily 03:00): `0 3 * * * cd /path/to/ldv-backend && python3 manage.py purge >> purge.log 2>&1`. Users can also self-delete via `DELETE /api/result/<uuid>` (auth + org-ownership enforced). Encryption at rest is active when `LDV_ENCRYPTION_KEY` is set; existing plaintext rows are read transparently and re-encrypted on next write.
````

- [ ] **Step 3: Update TODO P0 #3**

Replace the P0 #3 list item:

```markdown
3. **Retention / purge / encryption-at-rest** (CR-04) — uploads, extracted text, results, logs cannot persist indefinitely in `uploads/` + SQLite. Add retention+purge controls; encrypt stored documents.
```

with:

```markdown
3. ~~**Retention / purge / encryption-at-rest**~~ (CR-04) — **DONE (core).** `crypto.py` (Fernet/`MultiFernet`, key rotation) encrypts on-disk file bytes + `extracted_text` + `result_json` at rest, keyed by `LDV_ENCRYPTION_KEY` (unset = plaintext + degraded flag in `/health`). `documents.expires_at` retention (`LDV_RETENTION_DAYS`, default 30); `manage.py purge`/`purge-doc` (cron-driven) + `DELETE /api/result/<uuid>` for on-request deletion; purge logs as the deletion audit. Still TODO: SEC-09 backups (no backup system yet), structured SEC-06 audit table, per-org retention policy, report-metadata degraded surfacing (CR-09).
```

- [ ] **Step 4: Commit**

```bash
cd /home/stardhoom/LDV
git add CLAUDE.md
git commit -m "docs(cr04): retention/purge/encryption env vars, ops, P0 #3 status

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
```

---

## Final verification

- [ ] Run both self-checks together:

```bash
cd /home/stardhoom/LDV/ldv-backend
python3 tests/test_crypto.py && python3 tests/test_retention.py
```
Expected: `test_crypto OK` and `test_retention OK`.

- [ ] Confirm the full validation suite still passes (no regressions):

```bash
cd /home/stardhoom/LDV/ldv-backend && python3 tests/run_validation.py
```
Expected: same PASS/WARN/FAIL counts as before this change (no new FAIL).
