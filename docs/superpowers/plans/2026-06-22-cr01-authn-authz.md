# CR-01 AuthN/AuthZ & Tenant Isolation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Require authentication on every upload/result/report endpoint and enforce per-organization ownership so a valid-but-foreign UUID returns 403.

**Architecture:** Add `organizations` + `users` tables and ownership columns on `documents` in the existing SQLite layer. A new `auth.py` provides session+token resolution and `@login_required`/`@admin_required` decorators. `app.py` adds login/logout, decorates data endpoints, stamps ownership on upload, and enforces a 403 ownership check on result reads. A `manage.py` CLI provisions the seed admin, orgs, and users. A minimal `login.html` plus a 401→/login redirect covers the browser portal.

**Tech Stack:** Flask, SQLite (stdlib `sqlite3`), `werkzeug.security` (password hashing — already a Flask dep), stdlib `secrets`. Tests use Flask's built-in `app.test_client()` — no new dependency.

## Global Constraints

- No new third-party dependencies — `requirements.txt` stays `Flask` + `flask_cors`. (werkzeug ships with Flask.)
- Spec of record: `docs/superpowers/specs/2026-06-22-cr01-authn-authz-design.md`.
- Roles are exactly `'admin'` and `'user'` in this pass.
- Cross-org result read returns **403** (not 404) — PRD IAM-03 acceptance criterion.
- Emails are stored and looked up **lowercased**.
- API token auth uses the `Authorization: Bearer <token>` header. Secrets never in URLs.
- `DB_PATH` must be overridable via `LDV_DB_PATH` so tests use a temp DB.
- Tests are runnable as plain scripts (`python tests/test_auth.py`), matching `tests/run_validation.py` style — assertions via `assert`, no pytest.
- Inference-mode rule (repo quirk): never call `.eval()`; not relevant here but do not introduce it.

---

### Task 1: Database — orgs/users tables, ownership columns, query functions

**Files:**
- Modify: `ldv-backend/database.py`
- Test: `ldv-backend/tests/test_db_auth.py` (create)

**Interfaces:**
- Consumes: nothing (foundation task).
- Produces:
  - `create_org(name: str) -> int`
  - `get_org_by_name(name: str) -> dict | None`
  - `create_user(org_id: int, email: str, password_hash: str, role: str, api_token: str) -> int`
  - `get_user_by_email(email: str) -> dict | None`
  - `get_user_by_id(user_id: int) -> dict | None`
  - `get_user_by_token(token: str) -> dict | None`
  - `save_document(..., org_id: int | None = None, owner_id: int | None = None) -> int` (two new trailing kwargs)
  - `get_result(public_id: str) -> dict | None` now includes `org_id` in the returned dict.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_db_auth.py`:

```python
"""Behavioral checks for the auth-related database layer. Run: python tests/test_db_auth.py"""
import os
import tempfile

# Point the DB at a throwaway file BEFORE importing database.
_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name

import database  # noqa: E402

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
    test_org_and_user_roundtrip()
    test_document_ownership_flows_to_result()
    print("OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python tests/test_db_auth.py`
Expected: FAIL — `AttributeError: module 'database' has no attribute 'create_org'` (or `save_document() got an unexpected keyword argument 'org_id'`).

- [ ] **Step 3: Make `DB_PATH` overridable**

In `ldv-backend/database.py`, replace:

```python
DB_PATH = os.path.join(os.path.dirname(__file__), "sydeco.db")
```

with:

```python
DB_PATH = os.getenv("LDV_DB_PATH", os.path.join(os.path.dirname(__file__), "sydeco.db"))
```

- [ ] **Step 4: Add the new tables to the schema**

In `ldv-backend/database.py`, inside the `_SCHEMA` string, append after the `analyses` table definition (before the closing `"""`):

```sql

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
```

- [ ] **Step 5: Migrate `documents` with ownership columns**

In `ldv-backend/database.py`, inside `init_db()`, after the existing `analyses` public_id migration block and before the function returns, add:

```python
        # Ownership columns for tenant isolation (CR-01). Added if missing so
        # pre-auth databases keep working; existing rows stay NULL-org
        # (admin-visible only) until backfilled by manage.py seed-admin.
        doc_cols = {row[1] for row in conn.execute("PRAGMA table_info(documents)")}
        if "org_id" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN org_id INTEGER REFERENCES organizations(id)")
        if "owner_id" not in doc_cols:
            conn.execute("ALTER TABLE documents ADD COLUMN owner_id INTEGER REFERENCES users(id)")
```

- [ ] **Step 6: Add org/user query functions**

In `ldv-backend/database.py`, add at the end of the file:

```python
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
```

- [ ] **Step 7: Add ownership params to `save_document` and `org_id` to `get_result`**

In `ldv-backend/database.py`, change the `save_document` signature and INSERT. Replace the existing function with:

```python
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
    with _conn() as db:
        cur = db.execute(
            """INSERT INTO documents
               (original_filename, stored_filename, file_path, file_size,
                file_type, language, extracted_text, org_id, owner_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (original_filename, stored_filename, file_path, file_size,
             file_type, language, extracted_text, org_id, owner_id),
        )
        return cur.lastrowid
```

In `get_result`, add `d.org_id` to the SELECT column list (after `d.uploaded_at`):

```python
               d.extracted_text, d.uploaded_at, d.org_id
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd ldv-backend && python tests/test_db_auth.py`
Expected: `OK`

- [ ] **Step 9: Commit**

```bash
git add ldv-backend/database.py ldv-backend/tests/test_db_auth.py
git commit -m "feat(cr01): orgs/users tables + document ownership in DB layer"
```

---

### Task 2: `auth.py` — password verify, user resolution, decorators

**Files:**
- Create: `ldv-backend/auth.py`
- Test: `ldv-backend/tests/test_auth_unit.py` (create)

**Interfaces:**
- Consumes: `database.get_user_by_email/by_id/by_token` (Task 1).
- Produces:
  - `configure_secret_key(app) -> None`
  - `hash_password(password: str) -> str`
  - `verify_login(email: str, password: str) -> dict | None`
  - `current_user() -> dict | None` (caches on `flask.g.user`)
  - `login_required(view)` decorator → 401 when no user
  - `admin_required(view)` decorator → 401 no user / 403 non-admin

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_auth_unit.py`:

```python
"""Unit checks for auth.py. Run: python tests/test_auth_unit.py"""
import os
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python tests/test_auth_unit.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'auth'`.

- [ ] **Step 3: Write `auth.py`**

Create `ldv-backend/auth.py`:

```python
"""Authentication & authorization helpers (CR-01).

Resolves the current user from a Flask session cookie OR an
`Authorization: Bearer <api_token>` header, and exposes login_required /
admin_required decorators. No new dependencies — password hashing uses
werkzeug (bundled with Flask).
"""
from __future__ import annotations

import logging
import os
import secrets
from functools import wraps

from flask import g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import database

logger = logging.getLogger(__name__)


def configure_secret_key(app) -> None:
    key = os.getenv("LDV_SECRET_KEY")
    if not key:
        key = secrets.token_hex(32)
        logger.warning(
            "LDV_SECRET_KEY not set — using an ephemeral key. Sessions will not "
            "survive a restart. Set LDV_SECRET_KEY before any real deployment."
        )
    app.secret_key = key


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_login(email: str, password: str) -> dict | None:
    user = database.get_user_by_email(email)
    if user and user["active"] and check_password_hash(user["password_hash"], password):
        return user
    return None


def _bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    return None


def current_user() -> dict | None:
    if "user" in g:
        return g.user
    user = None
    uid = session.get("uid")
    if uid is not None:
        user = database.get_user_by_id(uid)
    if user is None:
        user = database.get_user_by_token(_bearer_token())
    if user is not None and not user["active"]:
        user = None
    g.user = user
    return user


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        if user["role"] != "admin":
            return jsonify({"error": "Forbidden"}), 403
        return view(*args, **kwargs)
    return wrapper
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ldv-backend && python tests/test_auth_unit.py`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add ldv-backend/auth.py ldv-backend/tests/test_auth_unit.py
git commit -m "feat(cr01): auth.py — session/token resolution + decorators"
```

---

### Task 3: Wire `app.py` — login, decorators, ownership 403, replace admin guard

**Files:**
- Modify: `ldv-backend/app.py`
- Test: `ldv-backend/tests/test_auth.py` (create) — the spec's end-to-end behavioral suite.

**Interfaces:**
- Consumes: `auth.configure_secret_key/verify_login/login_required/admin_required/current_user` (Task 2); `database.*` (Task 1).
- Produces: routes `POST /login`, `GET /login`, `POST /logout`; decorated `/upload`, `/analyze`, `/report`, `/api/result/<id>`, `/api/stats`, `/api/recent`, `/admin`.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_auth.py`:

```python
"""End-to-end auth + tenant isolation (CR-01). Run: python tests/test_auth.py"""
import os
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name
os.environ["LDV_SECRET_KEY"] = "test-key"

import database  # noqa: E402
import auth      # noqa: E402
import app as app_module  # noqa: E402

database.init_db()
client = app_module.app.test_client()


def _user(org, email, role):
    existing = database.get_org_by_name(org)
    oid = existing["id"] if existing else database.create_org(org)
    database.create_user(oid, email, auth.hash_password("pw"), role, f"tok-{email}")
    return oid


def _analysis_for_org(oid):
    doc = database.save_document(
        original_filename="c.txt", stored_filename="c.txt", file_path="/tmp/c.txt",
        file_size=3, file_type=".txt", language="en", extracted_text="hi",
        org_id=oid, owner_id=None,
    )
    return database.save_analysis(doc, "Indonesia", "contract", 40, "MEDIUM", {"ok": True})


def setup():
    org_a = _user("OrgA", "a@a.com", "user")
    _user("OrgB", "b@b.com", "user")
    _user("OrgA", "admin@a.com", "admin")
    return org_a


def test_anonymous_blocked():
    assert client.get("/api/result/whatever").status_code == 401
    assert client.post("/upload").status_code == 401


def test_bad_login():
    assert client.post("/login", json={"email": "a@a.com", "password": "nope"}).status_code == 401
    assert client.post("/login", json={"email": "ghost@a.com", "password": "pw"}).status_code == 401


def test_owner_and_cross_org_and_admin():
    org_a = setup()
    pub = _analysis_for_org(org_a)

    # Owner (same org) — 200
    c = app_module.app.test_client()
    assert c.post("/login", json={"email": "a@a.com", "password": "pw"}).status_code == 200
    assert c.get("/api/result/" + pub).status_code == 200

    # Cross-org user — 403 even with a valid UUID
    c2 = app_module.app.test_client()
    c2.post("/login", json={"email": "b@b.com", "password": "pw"})
    assert c2.get("/api/result/" + pub).status_code == 403

    # Admin — 200 for any org
    c3 = app_module.app.test_client()
    c3.post("/login", json={"email": "admin@a.com", "password": "pw"})
    assert c3.get("/api/result/" + pub).status_code == 200

    # API token auth works programmatically
    assert client.get(
        "/api/result/" + pub, headers={"Authorization": "Bearer tok-a@a.com"}
    ).status_code == 200


def test_admin_endpoints_gated():
    # user token -> 403, admin token -> 200
    assert client.get("/api/stats", headers={"Authorization": "Bearer tok-a@a.com"}).status_code == 403
    assert client.get("/api/stats", headers={"Authorization": "Bearer tok-admin@a.com"}).status_code == 200


if __name__ == "__main__":
    test_anonymous_blocked()
    test_bad_login()
    test_owner_and_cross_org_and_admin()
    test_admin_endpoints_gated()
    print("OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python tests/test_auth.py`
Expected: FAIL — anonymous `/api/result` returns 404/200 not 401, or `AttributeError` on `/login` (route missing).

- [ ] **Step 3: Import auth and configure the secret key**

In `ldv-backend/app.py`, add to the import block (after `import database`):

```python
import auth
```

Replace the Flask import line:

```python
from flask import Flask, request, jsonify, send_from_directory, Response
```

with (adds `redirect`, `g`, `session`):

```python
from flask import Flask, request, jsonify, send_from_directory, Response, redirect, g, session
```

Immediately after `app = Flask(__name__)` (and before the CORS block), add:

```python
auth.configure_secret_key(app)
```

- [ ] **Step 4: Remove the old admin-token guard**

In `ldv-backend/app.py`, delete the entire `_admin_authorized()` function (the `def _admin_authorized() -> bool:` block, lines ~75-89). Remove the now-unused `import hmac` from the top of the file.

- [ ] **Step 5: Add login/logout routes**

In `ldv-backend/app.py`, add near the other routes (e.g. just above `@app.route("/upload"...)`):

```python
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "login.html")
    data = request.get_json(silent=True) or request.form
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = auth.verify_login(email, password)
    if user is None:
        return jsonify({"error": "Invalid credentials"}), 401
    session["uid"] = user["id"]
    return jsonify({"ok": True, "role": user["role"]})


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})
```

- [ ] **Step 6: Require auth on upload/analyze/report and stamp ownership**

In `ldv-backend/app.py`, add `@auth.login_required` directly under each of these route decorators: `@app.route("/upload", ...)`, `@app.route("/analyze", ...)`, `@app.route("/report", ...)`. Example for upload:

```python
@app.route("/upload", methods=["POST"])
@auth.login_required
def upload():
```

In `upload()`, change the `database.save_document(...)` call to pass ownership:

```python
    doc_id = database.save_document(
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=file_path,
        file_size=len(data),
        file_type=ext,
        language=lang,
        extracted_text=text,
        org_id=g.user["org_id"],
        owner_id=g.user["id"],
    )
```

- [ ] **Step 7: Enforce ownership on result reads**

In `ldv-backend/app.py`, replace the `api_result` view with:

```python
@app.route("/api/result/<analysis_id>")
@auth.login_required
def api_result(analysis_id: str):
    row = database.get_result(analysis_id)
    if row is None:
        return jsonify({"error": "Not found"}), 404
    user = g.user
    if user["role"] != "admin" and row.get("org_id") != user["org_id"]:
        return jsonify({"error": "Forbidden"}), 403
    row.pop("org_id", None)  # internal field, not part of the API response
    import json
    row["result"] = json.loads(row["result_json"])
    del row["result_json"]
    return jsonify(row)
```

- [ ] **Step 8: Gate the admin endpoints with admin_required**

In `ldv-backend/app.py`, replace the bodies that called `_admin_authorized()`:

```python
@app.route("/api/stats")
@auth.admin_required
def api_stats():
    return jsonify(database.get_stats())


@app.route("/api/recent")
@auth.admin_required
def api_recent():
    limit = min(int(request.args.get("limit", 10)), 50)
    return jsonify(database.get_recent(limit))
```

And gate the admin page (replace the existing `@app.route("/admin")` view):

```python
@app.route("/admin")
def admin_page():
    user = auth.current_user()
    if user is None or user["role"] != "admin":
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "admin.html")
```

- [ ] **Step 9: Run test to verify it passes**

Run: `cd ldv-backend && python tests/test_auth.py`
Expected: `OK`

- [ ] **Step 10: Commit**

```bash
git add ldv-backend/app.py ldv-backend/tests/test_auth.py
git commit -m "feat(cr01): require auth on data path + 403 tenant isolation + admin accounts"
```

---

### Task 4: `manage.py` provisioning CLI

**Files:**
- Create: `ldv-backend/manage.py`
- Test: `ldv-backend/tests/test_manage.py` (create)

**Interfaces:**
- Consumes: `database.create_org/get_org_by_name/create_user/get_user_by_email` (Task 1); `auth.hash_password` (Task 2).
- Produces: callables `seed_admin()`, `create_org_cmd(name)`, `create_user_cmd(email, org_name, role)` and a `__main__` argparse dispatcher.

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_manage.py`:

```python
"""Checks for manage.py provisioning. Run: python tests/test_manage.py"""
import os
import tempfile

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
os.environ["LDV_DB_PATH"] = _TMP.name
os.environ["LDV_ADMIN_EMAIL"] = "root@sydeco.com"
os.environ["LDV_ADMIN_PASSWORD"] = "rootpw"

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python tests/test_manage.py`
Expected: FAIL — `ModuleNotFoundError: No module named 'manage'`.

- [ ] **Step 3: Write `manage.py`**

Create `ldv-backend/manage.py`:

```python
#!/usr/bin/env python3
"""Provisioning CLI for CR-01 auth.

  python manage.py seed-admin                          # uses LDV_ADMIN_EMAIL/PASSWORD
  python manage.py create-org "Acme"
  python manage.py create-user user@acme.com "Acme" --role user
"""
from __future__ import annotations

import argparse
import os
import secrets
import sys

import auth
import database


def _gen_token() -> str:
    return secrets.token_urlsafe(32)


def seed_admin() -> None:
    email = os.getenv("LDV_ADMIN_EMAIL")
    password = os.getenv("LDV_ADMIN_PASSWORD")
    if not email or not password:
        sys.exit("Set LDV_ADMIN_EMAIL and LDV_ADMIN_PASSWORD before seed-admin.")
    email = email.strip().lower()
    if database.get_user_by_email(email):
        print(f"User {email} already exists; nothing to do.")
        return
    org = database.get_org_by_name("Sydeco")
    org_id = org["id"] if org else database.create_org("Sydeco")
    token = _gen_token()
    database.create_user(org_id, email, auth.hash_password(password), "admin", token)
    print(f"Created admin {email} in org 'Sydeco'.")
    print(f"  api token: {token}")


def create_org_cmd(name: str) -> None:
    existing = database.get_org_by_name(name)
    if existing:
        print(f"Org '{name}' already exists (id={existing['id']}).")
        return
    org_id = database.create_org(name)
    print(f"Created org '{name}' (id={org_id}).")


def create_user_cmd(email: str, org_name: str, role: str) -> None:
    email = email.strip().lower()
    if database.get_user_by_email(email):
        sys.exit(f"User {email} already exists.")
    org = database.get_org_by_name(org_name)
    if not org:
        sys.exit(f"Org '{org_name}' not found. Create it first with create-org.")
    password = secrets.token_urlsafe(12)
    token = _gen_token()
    database.create_user(org["id"], email, auth.hash_password(password), role, token)
    print(f"Created {role} {email} in '{org_name}'.")
    print(f"  password:  {password}")
    print(f"  api token: {token}")


def main() -> None:
    database.init_db()
    parser = argparse.ArgumentParser(description="LDV auth provisioning")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed-admin")
    po = sub.add_parser("create-org")
    po.add_argument("name")
    pu = sub.add_parser("create-user")
    pu.add_argument("email")
    pu.add_argument("org")
    pu.add_argument("--role", default="user", choices=["user", "admin"])
    args = parser.parse_args()

    if args.cmd == "seed-admin":
        seed_admin()
    elif args.cmd == "create-org":
        create_org_cmd(args.name)
    elif args.cmd == "create-user":
        create_user_cmd(args.email, args.org, args.role)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ldv-backend && python tests/test_manage.py`
Expected: `OK`

- [ ] **Step 5: Commit**

```bash
git add ldv-backend/manage.py ldv-backend/tests/test_manage.py
git commit -m "feat(cr01): manage.py provisioning CLI (seed-admin, create-org, create-user)"
```

---

### Task 5: Frontend — login page + 401 redirect

**Files:**
- Create: `ldv-frontend/login.html`
- Modify: `ldv-frontend/index.html` (~line 298), `ldv-frontend/result.html` (~lines 565, 601), `ldv-frontend/admin.html` (~lines 222-226)

**Interfaces:**
- Consumes: `POST /login`, `POST /logout` (Task 3).
- Produces: a browser login flow; no automated test (trivial static HTML/JS — verified manually).

- [ ] **Step 1: Create `login.html`**

Create `ldv-frontend/login.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sign in — Sydeco LightML</title>
  <link rel="stylesheet" href="/styles.css">
</head>
<body>
  <main style="max-width:360px;margin:8vh auto;font-family:system-ui,sans-serif">
    <h1>Sign in</h1>
    <form id="loginForm">
      <label>Email<br><input type="email" id="email" required style="width:100%"></label><br><br>
      <label>Password<br><input type="password" id="password" required style="width:100%"></label><br><br>
      <button type="submit">Sign in</button>
      <p id="err" style="color:#b00;display:none">Invalid credentials.</p>
    </form>
  </main>
  <script>
    document.getElementById('loginForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const resp = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: document.getElementById('email').value,
          password: document.getElementById('password').value,
        }),
      });
      if (resp.ok) { window.location.href = '/'; return; }
      document.getElementById('err').style.display = 'block';
    });
  </script>
</body>
</html>
```

- [ ] **Step 2: Add 401 redirect in `index.html`**

In `ldv-frontend/index.html`, in the upload handler, immediately after `const resp = await fetch('/upload', { method: 'POST', body: fd });` and before `const data = await resp.json();`, insert:

```javascript
        if (resp.status === 401) { window.location.href = '/login'; return; }
```

- [ ] **Step 3: Add 401/403 handling in `result.html`**

In `ldv-frontend/result.html`, right after `const resp = await fetch('/api/result/' + id);` and before the `if (resp.status === 404)` check, insert:

```javascript
      if (resp.status === 401) { window.location.href = '/login'; return; }
      if (resp.status === 403) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display  = 'block';
        document.getElementById('errorText').textContent = 'You do not have access to this analysis.';
        return;
      }
```

Also in the `/report` handler, after `const resp = await fetch('/report', {...});`, insert:

```javascript
      if (resp.status === 401) { window.location.href = '/login'; return; }
```

- [ ] **Step 4: Add 401 redirect in `admin.html`**

In `ldv-frontend/admin.html`, inside `load()`, after the `Promise.all([...])` that assigns `[statsResp, recentResp]`, insert before the `.json()` calls:

```javascript
      if (statsResp.status === 401 || recentResp.status === 401) {
        window.location.href = '/login'; return;
      }
```

- [ ] **Step 5: Manual verification**

Run:
```bash
cd ldv-backend
LDV_DB_PATH=/tmp/ldv-manual.db LDV_ADMIN_EMAIL=admin@sydeco.com LDV_ADMIN_PASSWORD=changeme python manage.py seed-admin
LDV_DB_PATH=/tmp/ldv-manual.db LDV_SECRET_KEY=dev FLASK_APP=app.py python -m flask run --port 5000
```
In a browser: uploading before signing in should redirect to `/login`; after signing in as the seeded admin, upload + result + `/admin` work. `curl http://127.0.0.1:5000/api/stats` (no header) → 401; with `-H "Authorization: Bearer <admin token>"` → 200.

- [ ] **Step 6: Commit**

```bash
git add ldv-frontend/login.html ldv-frontend/index.html ldv-frontend/result.html ldv-frontend/admin.html
git commit -m "feat(cr01): login page + 401 redirect in portal"
```

---

### Task 6: Docs — update CLAUDE.md env table and TODO

**Files:**
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: the shipped behavior of Tasks 1-5.
- Produces: accurate operator docs.

- [ ] **Step 1: Update the env-var table**

In `CLAUDE.md`, in the environment-variables table, add rows for `LDV_SECRET_KEY` (signs session cookies; ephemeral if unset — dev only), `LDV_DB_PATH` (SQLite path override; default `sydeco.db`), `LDV_ADMIN_EMAIL` / `LDV_ADMIN_PASSWORD` (consumed by `manage.py seed-admin`). Remove the `LDV_ADMIN_TOKEN` row — admin endpoints now require an admin account.

- [ ] **Step 2: Mark P0 #1 progress**

In `CLAUDE.md` under "P0 — Production blockers", update item 1 (CR-01) to note: core auth + tenant isolation shipped (session+token login, org ownership, cross-org→403, admin accounts replace the shared token, `manage.py` provisioning). Still deferred: MFA, full role matrix, signed/expiring download links, audit log.

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(cr01): env vars + P0 #1 progress for auth/tenant isolation"
```

---

## Self-Review

**Spec coverage:**
- Data model (orgs/users/ownership) → Task 1 ✓
- Session+token auth, decorators, secret key → Task 2 ✓
- Login/logout, decorated endpoints, ownership 403, admin accounts replacing shared token → Task 3 ✓
- CLI provisioning (seed-admin/create-org/create-user) → Task 4 ✓
- login.html + 401 redirect → Task 5 ✓
- Test suite (7 spec cases: anon→401, cross-org→403, owner→200, admin→200, bad password→401, token→200, anon upload→401) → covered across Tasks 1-3 (`test_auth.py`) ✓
- Docs (CLAUDE.md env table, removal of `LDV_ADMIN_TOKEN`) → Task 6 ✓

**Placeholder scan:** none — every code/test step contains full content.

**Type consistency:** `create_org`→int, `get_org_by_name`→dict|None (used as `org["id"]` consistently), `create_user(org_id,email,password_hash,role,api_token)` signature identical across database.py / auth callers / manage.py / tests. `current_user()`/`g.user` dict shape (`role`, `org_id`, `id`, `email`, `active`) used consistently. `save_document` trailing `org_id`/`owner_id` kwargs match all call sites.

**Deviation from spec (intentional):** existing-data backfill is to NULL-org/admin-visible rather than to the seed org — stricter (no accidental cross-assignment), satisfies the security goal, and avoids a fragile data migration. Documented in Task 1 Step 5 comment.
