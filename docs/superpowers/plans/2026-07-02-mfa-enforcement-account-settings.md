# MFA Enforcement Toggle + Self-Service Account Settings Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the two real MFA gaps found during the brainstorming audit — org admins have no way to turn on org-wide MFA enforcement, and users have no self-service page to voluntarily enable/disable their own MFA.

**Architecture:** Two small backend additions (a write path for `organizations.mfa_required`, and a bug fix so `/api/v1/mfa/disable` actually respects mandatory MFA) plus two frontend surfaces (`admin.html` gets an enforcement toggle, a new `account.html` reuses the existing MFA setup/enable/disable endpoints). No new tables, no new endpoints beyond one `mfa-required` route and one `/account` page route — everything else is already-shipped MFA plumbing (`auth.is_mfa_mandatory`, `database.org_mfa_required`, `/api/v1/mfa/{status,setup,enable,disable}`).

**Tech Stack:** Flask (`ldv-backend/app.py`, `ldv-backend/database.py`, `ldv-backend/auth.py`), sqlite3, Alpine.js + Tailwind CDN frontend pages (`ldv-frontend/*.html`), manual Python test scripts under `ldv-backend/tests/` (this repo does not use pytest fixtures/marks — tests are plain asserting scripts with a `if __name__ == "__main__"` runner, run via `python3 tests/<file>.py`).

## Global Constraints

- Permission model for the new org endpoint must exactly match the existing `/api/v1/admin/organizations/<id>/retention` endpoint: `@auth.role_required("manager")`, then `if u_role != "admin" and org_id != user["org_id"]: 403`.
- Every state-changing admin action must call `database.write_audit(...)`, matching the existing call sites in `ldv-backend/app.py`.
- Follow the codebase's existing test convention exactly (see `ldv-backend/tests/test_auth.py`): a temp sqlite DB via `tempfile`, `importlib.reload()` of `database`/`auth`/`app`, a module-level `client = app_module.app.test_client()`, an idempotent `_user()`/`setup()` helper, and a `if __name__ == "__main__":` runner block. Run tests with `python3 tests/<file>.py`, **not** `pytest` — `auth.is_mfa_mandatory()` has a `PYTEST_CURRENT_TEST` escape hatch that forces it to return `False` under pytest, which would silently break the enrollment-required assertion in Task 2.
- Frontend pages in this repo are self-contained HTML files that each duplicate the same Tailwind CDN config / font imports / `glass-card` styling (see `ldv-frontend/admin.html` and `ldv-frontend/login.html`). Follow that convention for the new `account.html` — do not attempt to factor out a shared header.
- Without `LDV_ENCRYPTION_KEY` set, `crypto.enc_str`/`crypto.dec_str` are pass-through (see `ldv-backend/crypto.py:50-61`), so tests may write plaintext values directly into `mfa_secret` without needing real Fernet encryption.

---

### Task 1: `database.set_org_mfa_required()` + audit allowlist

**Files:**
- Modify: `ldv-backend/database.py:114-119` (add function after `set_org_retention`)
- Modify: `ldv-backend/database.py:553-557` (audit allowlist)
- Test: `ldv-backend/tests/test_org_mfa_required.py` (new)

**Interfaces:**
- Produces: `database.set_org_mfa_required(org_id: int, required: bool) -> None`

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_org_mfa_required.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python3 tests/test_org_mfa_required.py`
Expected: `AttributeError: module 'database' has no attribute 'set_org_mfa_required'`

- [ ] **Step 3: Implement `set_org_mfa_required`**

In `ldv-backend/database.py`, immediately after `set_org_retention` (currently lines 114-119):

```python
def set_org_mfa_required(org_id: int, required: bool) -> None:
    with _conn() as db:
        db.execute(
            "UPDATE organizations SET mfa_required = ? WHERE id = ?", (1 if required else 0, org_id)
        )
```

- [ ] **Step 4: Add the audit action to the allowlist**

In `ldv-backend/database.py`, the `high_impact_actions` set inside `write_audit` (currently lines 553-557) reads:

```python
    high_impact_actions = {
        "delete", "cite.verify", "user.role_change", 
        "org.retention_change", "user.suspend", "user.unsuspend",
        "mfa.disable", "user.mfa_reset", "user.download.disable"
    }
```

Change it to:

```python
    high_impact_actions = {
        "delete", "cite.verify", "user.role_change", 
        "org.retention_change", "org.mfa_required_change", "user.suspend", "user.unsuspend",
        "mfa.disable", "user.mfa_reset", "user.download.disable"
    }
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd ldv-backend && python3 tests/test_org_mfa_required.py`
Expected: `test_org_mfa_required OK`

- [ ] **Step 6: Commit**

```bash
git add ldv-backend/database.py ldv-backend/tests/test_org_mfa_required.py
git commit -m "feat: add database.set_org_mfa_required write path"
```

---

### Task 2: `POST /api/v1/admin/organizations/<org_id>/mfa-required` endpoint

**Files:**
- Modify: `ldv-backend/app.py:936` (insert new route right after the retention endpoint, before the `# ── Admin API` comment)
- Test: `ldv-backend/tests/test_mfa_enforcement.py` (new)

**Interfaces:**
- Consumes: `database.set_org_mfa_required(org_id: int, required: bool) -> None` (Task 1), `database.org_mfa_required(org_id) -> bool` (existing), `database.write_audit(...)` (existing), `auth.role_required("manager")` (existing), `auth.normalize_role(role)` (existing), `_ip()` (existing helper in `app.py`)
- Produces: route `POST /api/v1/admin/organizations/<int:org_id>/mfa-required`, body `{"mfa_required": bool}`, `200 {"ok": true}` / `403 {"error": ...}`

- [ ] **Step 1: Write the failing test**

Create `ldv-backend/tests/test_mfa_enforcement.py`:

```python
"""End-to-end coverage for org-wide MFA enforcement (mfa-required toggle)
and the /api/v1/mfa/disable mandatory-MFA guard.

Run directly (NOT via pytest — auth.is_mfa_mandatory() has a
PYTEST_CURRENT_TEST escape hatch that would mask the enrollment assertion):
    python3 tests/test_mfa_enforcement.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

_TMP = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TMP.close()
_DB_PATH = _TMP.name

import importlib
import database  # noqa: E402
importlib.reload(database)
import auth      # noqa: E402
importlib.reload(auth)
import app as app_module  # noqa: E402
importlib.reload(app_module)
app_module.app.config["TESTING"] = True
app_module.app.testing = True


def setup_module(module):
    os.environ["LDV_DB_PATH"] = _DB_PATH
    os.environ["LDV_SECRET_KEY"] = "test-key"
    database.init_db()


client = app_module.app.test_client()


def _user(org, email, role):
    existing_user = database.get_user_by_email(email)
    if existing_user:
        return existing_user["org_id"]
    existing = database.get_org_by_name(org)
    oid = existing["id"] if existing else database.create_org(org)
    database.create_user(oid, email, auth.hash_password("pw"), role, f"tok-{email}")
    return oid


def setup():
    org_a = _user("MfaOrgA", "mgr-a@a.com", "manager")
    org_b = _user("MfaOrgB", "mgr-b@b.com", "manager")
    _user("MfaOrgA", "root@a.com", "admin")
    _user("MfaOrgA", "plain@a.com", "user")
    return org_a, org_b


def test_manager_can_set_own_org():
    org_a, _ = setup()
    c = app_module.app.test_client()
    c.post("/login", json={"email": "mgr-a@a.com", "password": "pw"})
    resp = c.post(f"/api/v1/admin/organizations/{org_a}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 200, resp.get_json()
    assert database.org_mfa_required(org_a) is True
    database.set_org_mfa_required(org_a, False)


def test_manager_forbidden_other_org():
    org_a, org_b = setup()
    c = app_module.app.test_client()
    c.post("/login", json={"email": "mgr-a@a.com", "password": "pw"})
    resp = c.post(f"/api/v1/admin/organizations/{org_b}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 403, resp.get_json()
    assert database.org_mfa_required(org_b) is False


def test_admin_can_set_any_org():
    org_a, org_b = setup()
    c = app_module.app.test_client()
    c.post("/login", json={"email": "root@a.com", "password": "pw"})
    resp = c.post(f"/api/v1/admin/organizations/{org_b}/mfa-required", json={"mfa_required": True})
    assert resp.status_code == 200, resp.get_json()
    assert database.org_mfa_required(org_b) is True
    database.set_org_mfa_required(org_b, False)


def test_toggle_forces_enrollment_on_next_login():
    org_a, _ = setup()
    database.set_org_mfa_required(org_a, True)
    c = app_module.app.test_client()
    resp = c.post("/login", json={"email": "plain@a.com", "password": "pw"})
    assert resp.status_code == 200, resp.get_json()
    assert resp.get_json().get("mfa_enroll_required") is True
    database.set_org_mfa_required(org_a, False)


def test_disable_blocked_when_org_mandatory():
    org_a, _ = setup()
    user = database.get_user_by_email("plain@a.com")
    database.update_user_mfa(user["id"], "dummy-secret", "[]")
    database.set_org_mfa_required(org_a, True)

    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]

    resp = c.post("/api/v1/mfa/disable", json={"password": "pw"})
    assert resp.status_code == 403, resp.get_json()
    assert database.get_user_by_id(user["id"])["mfa_secret"] is not None

    database.set_org_mfa_required(org_a, False)
    database.update_user_mfa(user["id"], None, None)


def test_disable_allowed_when_not_mandatory():
    org_a, _ = setup()
    user = database.get_user_by_email("plain@a.com")
    database.update_user_mfa(user["id"], "dummy-secret", "[]")
    database.set_org_mfa_required(org_a, False)

    c = app_module.app.test_client()
    with c.session_transaction() as sess:
        sess["uid"] = user["id"]

    resp = c.post("/api/v1/mfa/disable", json={"password": "pw"})
    assert resp.status_code == 200, resp.get_json()
    assert database.get_user_by_id(user["id"])["mfa_secret"] is None


def test_account_page_requires_login():
    c = app_module.app.test_client()
    resp = c.get("/account", follow_redirects=False)
    assert resp.status_code == 302
    assert "/login" in resp.headers.get("Location", "")

    c.post("/login", json={"email": "plain@a.com", "password": "pw"})
    resp2 = c.get("/account")
    assert resp2.status_code == 200


if __name__ == "__main__":
    setup_module(None)
    test_manager_can_set_own_org()
    test_manager_forbidden_other_org()
    test_admin_can_set_any_org()
    test_toggle_forces_enrollment_on_next_login()
    test_disable_blocked_when_org_mandatory()
    test_disable_allowed_when_not_mandatory()
    test_account_page_requires_login()
    print("OK")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ldv-backend && python3 tests/test_mfa_enforcement.py`
Expected: FAIL on `test_manager_can_set_own_org` with a 404 (route doesn't exist yet)

- [ ] **Step 3: Implement the endpoint**

In `ldv-backend/app.py`, immediately after the retention endpoint (currently ending at line 933 with `return jsonify({"ok": True})`, right before the `# ── Admin API` comment at line ~938):

```python
@app.route("/api/v1/admin/organizations/<int:org_id>/mfa-required", methods=["POST"])
@auth.role_required("manager")
def api_admin_org_mfa_required(org_id: int):
    user = g.user
    u_role = auth.normalize_role(user["role"])
    data = request.json or {}
    required = bool(data.get("mfa_required"))

    if u_role != "admin" and org_id != user["org_id"]:
        return jsonify({"error": "Forbidden"}), 403

    database.set_org_mfa_required(org_id, required)
    database.write_audit("org.mfa_required_change", user_id=user["id"], org_id=org_id, resource_id=str(org_id), ip=_ip(), detail=str(required))
    return jsonify({"ok": True})
```

- [ ] **Step 4: Run test to verify it passes**

Note: this will still fail on `test_disable_blocked_when_org_mandatory` and `test_account_page_requires_login` until Tasks 3 and 5 are done — that's expected. Confirm the first three tests now pass:

Run: `cd ldv-backend/tests && python3 -c "
import test_mfa_enforcement as t
t.setup_module(None)
t.test_manager_can_set_own_org()
t.test_manager_forbidden_other_org()
t.test_admin_can_set_any_org()
t.test_toggle_forces_enrollment_on_next_login()
print('Task 2 tests OK')
"`
Expected: `Task 2 tests OK`

- [ ] **Step 5: Commit**

```bash
git add ldv-backend/app.py ldv-backend/tests/test_mfa_enforcement.py
git commit -m "feat: add admin endpoint to toggle org-wide MFA enforcement"
```

---

### Task 3: Fix `/api/v1/mfa/disable` to enforce mandatory MFA

**Files:**
- Modify: `ldv-backend/app.py:532-543`

**Interfaces:**
- Consumes: `database.org_mfa_required(org_id) -> bool` (existing), `auth.is_mfa_mandatory(user) -> bool` (existing) — same pattern already used by `/api/v1/mfa/skip` at `app.py:524`

This task fixes a real bug uncovered during planning: `/api/v1/mfa/disable` currently has no mandatory-MFA check at all, so a user in an org with `mfa_required=1` (or in a mandatory role) could disable their own MFA, silently defeating Task 1/2's enforcement toggle.

- [ ] **Step 1: Confirm the test from Task 2 fails here**

Run: `cd ldv-backend/tests && python3 -c "
import test_mfa_enforcement as t
t.setup_module(None)
t.test_disable_blocked_when_org_mandatory()
"`
Expected: `AssertionError` (current disable endpoint returns 200, not 403)

- [ ] **Step 2: Implement the fix**

In `ldv-backend/app.py`, replace the current `api_mfa_disable` (lines 532-543):

```python
@app.route("/api/v1/mfa/disable", methods=["POST"])
@auth.login_required
def api_mfa_disable():
    user = g.user
    data = request.json or {}
    password = data.get("password") or ""
    if not auth.verify_login(user["email"], password):
        return jsonify({"error": "Re-authentication failed: invalid password"}), 401
        
    database.update_user_mfa(user["id"], None, None)
    database.write_audit("mfa.disable", user_id=user["id"], org_id=user["org_id"], ip=_ip())
    return jsonify({"ok": True})
```

with:

```python
@app.route("/api/v1/mfa/disable", methods=["POST"])
@auth.login_required
def api_mfa_disable():
    user = g.user
    data = request.json or {}
    password = data.get("password") or ""
    if not auth.verify_login(user["email"], password):
        return jsonify({"error": "Re-authentication failed: invalid password"}), 401

    if database.org_mfa_required(user["org_id"]) or auth.is_mfa_mandatory(user):
        return jsonify({"error": "MFA is mandatory for this account"}), 403

    database.update_user_mfa(user["id"], None, None)
    database.write_audit("mfa.disable", user_id=user["id"], org_id=user["org_id"], ip=_ip())
    return jsonify({"ok": True})
```

- [ ] **Step 3: Run the two disable tests to verify they pass**

Run: `cd ldv-backend/tests && python3 -c "
import test_mfa_enforcement as t
t.setup_module(None)
t.test_disable_blocked_when_org_mandatory()
t.test_disable_allowed_when_not_mandatory()
print('Task 3 tests OK')
"`
Expected: `Task 3 tests OK`

- [ ] **Step 4: Commit**

```bash
git add ldv-backend/app.py
git commit -m "fix: enforce mandatory MFA on the /api/v1/mfa/disable endpoint"
```

---

### Task 4: `GET /account` route

**Files:**
- Modify: `ldv-backend/app.py` (insert after the `/citations` route block, currently ending at line 1177)

**Interfaces:**
- Consumes: `auth.current_user() -> dict | None` (existing, same helper used by `/admin` and `/citations` routes), `FRONTEND_DIR` (existing module constant)
- Produces: route `GET /account` — 302 redirect to `/login` when unauthenticated, else serves `ldv-frontend/account.html` (created in Task 5)

- [ ] **Step 1: Confirm the account-page test currently fails**

Run: `cd ldv-backend/tests && python3 -c "
import test_mfa_enforcement as t
t.setup_module(None)
t.test_account_page_requires_login()
"`
Expected: FAIL — `/account` currently 404s (falls through to `frontend_files`, which serves `index.html` with a 200 instead of a redirect, or errors since `account.html` doesn't exist yet)

- [ ] **Step 2: Implement the route**

In `ldv-backend/app.py`, immediately after the `citation_review_page` function (currently ending at line 1177, before the `@app.route("/swagger.json")` block):

```python
@app.route("/account")
def account_page():
    user = auth.current_user()
    if user is None:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "account.html")
```

- [ ] **Step 3: Run test to verify it passes**

(This also requires `account.html` to exist — do Task 5 first if running this in isolation, or run the full suite after Task 5.)

Run: `cd ldv-backend && python3 tests/test_mfa_enforcement.py`
Expected: `OK` (all 7 tests pass — this is the final task touching backend code, so this is the full green run)

- [ ] **Step 4: Commit**

```bash
git add ldv-backend/app.py
git commit -m "feat: add /account route for self-service security settings"
```

---

### Task 5: `ldv-frontend/account.html` — self-service MFA settings page

**Files:**
- Create: `ldv-frontend/account.html`

**Interfaces:**
- Consumes: `GET /api/v1/mfa/status` (existing, returns `{mfa_enabled, mfa_mandatory, email}`), `POST /api/v1/mfa/setup` (existing, body `{password}` when called from an authenticated session — required because `session.get("uid")` is set, not `mfa_enroll_pending_uid`; returns `{secret, provisioning_uri, recovery_codes}`), `POST /api/v1/mfa/enable` (existing, body `{code}`), `POST /api/v1/mfa/disable` (existing, body `{password}`; now returns 403 on mandatory MFA per Task 3)

No backend changes in this task — pure frontend, reusing endpoints that already work for a logged-in session.

- [ ] **Step 1: Create the page**

Create `ldv-frontend/account.html`. Copy the `<!DOCTYPE html>` through `</head>` block **verbatim** from `ldv-frontend/admin.html` (lines 1-238 — the Tailwind CDN config, Google Fonts, Material Symbols, and `<style>` block with `.glass-card`, `.gold-button`, `.spinner-ring`, etc.), changing only the `<title>` to `Account & Security — Sydeco CRA`. Then use this body and script:

```html
<body class="bg-background text-on-background font-body selection:bg-primary/30" x-data="accountApp()" x-init="load()">

  <header class="fixed top-0 left-0 right-0 z-40 h-16 flex items-center justify-between px-6 md:px-12 border-b border-outline-variant/10" style="background:rgba(14,19,31,0.9);backdrop-filter:blur(20px);">
    <a href="/" class="flex items-center gap-2 text-sm font-bold font-body text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;">
      <span class="material-symbols-outlined text-[18px]">arrow_back</span>
      Back to Sydeco CRA
    </a>
    <a href="/logout" class="text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors" style="text-decoration:none;">Secure Logout</a>
  </header>

  <main class="pt-28 pb-20 px-6 max-w-2xl mx-auto">
    <h1 class="font-editorial text-3xl mb-2">Account & Security</h1>
    <p class="text-on-surface-variant text-sm mb-8" x-text="email"></p>

    <div class="mb-4 bg-red-950/20 border border-red-500/30 rounded px-4 py-3 text-red-300 text-sm" x-show="errorMsg" x-text="errorMsg" style="display:none;"></div>
    <div class="mb-4 bg-teal-950/20 border border-teal-500/30 rounded px-4 py-3 text-teal-300 text-sm" x-show="successMsg" x-text="successMsg" style="display:none;"></div>

    <section class="glass-card p-6 space-y-6" x-show="view === 'status'">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="font-editorial text-lg font-bold text-primary">Multi-Factor Authentication</h2>
          <p class="text-xs text-on-surface-variant mt-1" x-text="mfaMandatory ? 'Mandatory for your organization or role.' : 'Optional — recommended for institutional accounts.'"></p>
        </div>
        <span class="px-3 py-1 rounded text-xs font-bold uppercase tracking-wider border"
              :class="mfaEnabled ? 'bg-teal-950/40 text-teal-400 border-teal-500/20' : 'bg-amber-950/40 text-amber-300 border-amber-500/20'"
              x-text="mfaEnabled ? 'Enabled' : 'Disabled'"></span>
      </div>

      <button type="button" class="gold-button px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider"
              x-show="!mfaEnabled" @click="view = 'enable_password'">Enable MFA</button>

      <button type="button" class="px-6 py-2.5 rounded text-xs font-bold uppercase tracking-wider border border-red-500/30 text-red-400 hover:bg-red-950/20 transition-colors"
              x-show="mfaEnabled" @click="view = 'disable_password'">Disable MFA</button>
    </section>

    <section class="glass-card p-6 space-y-4" x-show="view === 'enable_password'" style="display:none;">
      <h2 class="font-editorial text-lg font-bold text-primary">Confirm Password</h2>
      <p class="text-xs text-on-surface-variant">Re-enter your password to begin MFA setup.</p>
      <form @submit.prevent="startEnable()" class="space-y-4">
        <input type="password" x-model="password" placeholder="Password" required
               class="w-full bg-surface-container-lowest border border-outline-variant/30 text-on-surface px-4 py-2.5 rounded text-sm"/>
        <div class="flex gap-3">
          <button type="button" class="flex-1 py-2.5 border border-outline-variant/40 rounded text-xs font-semibold" @click="view = 'status'; password = ''">Cancel</button>
          <button type="submit" class="flex-[2] gold-button py-2.5 rounded text-xs font-bold uppercase tracking-wider" :disabled="loading" x-text="loading ? 'Verifying…' : 'Continue'"></button>
        </div>
      </form>
    </section>

    <section class="glass-card p-6 space-y-6" x-show="view === 'enroll'" style="display:none;">
      <h2 class="font-editorial text-lg font-bold text-primary">Set Up MFA</h2>
      <div class="flex flex-col md:flex-row gap-6 items-center bg-surface-container-lowest/30 p-5 border border-outline-variant/10 rounded">
        <div class="bg-white p-3 rounded shrink-0">
          <img :src="mfaSetup.qrCodeUrl" class="w-40 h-40 object-contain" alt="MFA QR Code"/>
        </div>
        <div class="space-y-2 text-sm text-on-surface-variant">
          <p class="font-bold text-on-surface">1. Scan QR Code</p>
          <p>Scan with Google Authenticator, Duo, or any TOTP app.</p>
          <p class="text-xs mt-2">Manual entry key: <code class="bg-surface-container px-2 py-1 rounded text-primary font-bold tracking-wider" x-text="mfaSetup.secret"></code></p>
        </div>
      </div>
      <div class="p-5 border border-outline-variant/15 rounded bg-surface-container-low/50">
        <p class="font-bold text-on-surface text-base mb-2">2. Save Recovery Codes</p>
        <p class="text-sm text-on-surface-variant mb-4">Store these somewhere safe — they won't be shown again.</p>
        <div class="grid grid-cols-2 md:grid-cols-5 gap-2 font-mono text-xs text-primary font-bold text-center bg-background/50 p-3 rounded border border-outline-variant/10">
          <template x-for="code in mfaSetup.recoveryCodes"><span x-text="code"></span></template>
        </div>
      </div>
      <form @submit.prevent="confirmEnable()" class="space-y-4 pt-2 border-t border-outline-variant/10">
        <label class="text-xs uppercase tracking-widest text-on-surface-variant">3. Verify TOTP Code</label>
        <input type="text" x-model="mfaCode" placeholder="000000" maxlength="6" required autocomplete="off"
               class="w-full bg-surface-container-lowest border border-outline-variant/30 text-on-surface text-center tracking-[0.5em] px-4 py-3 rounded text-xl font-bold"/>
        <div class="flex gap-3">
          <button type="button" class="flex-1 py-2.5 border border-outline-variant/40 rounded text-xs font-semibold" @click="view = 'status'; mfaCode = ''">Cancel</button>
          <button type="submit" class="flex-[2] gold-button py-2.5 rounded text-xs font-bold uppercase tracking-wider" :disabled="loading" x-text="loading ? 'Enabling…' : 'Enable MFA'"></button>
        </div>
      </form>
    </section>

    <section class="glass-card p-6 space-y-4" x-show="view === 'disable_password'" style="display:none;">
      <h2 class="font-editorial text-lg font-bold text-primary">Disable MFA</h2>
      <p class="text-xs text-on-surface-variant">Re-enter your password to confirm. This removes your authenticator enrollment and recovery codes.</p>
      <form @submit.prevent="confirmDisable()" class="space-y-4">
        <input type="password" x-model="password" placeholder="Password" required
               class="w-full bg-surface-container-lowest border border-outline-variant/30 text-on-surface px-4 py-2.5 rounded text-sm"/>
        <div class="flex gap-3">
          <button type="button" class="flex-1 py-2.5 border border-outline-variant/40 rounded text-xs font-semibold" @click="view = 'status'; password = ''">Cancel</button>
          <button type="submit" class="flex-[2] py-2.5 rounded text-xs font-bold uppercase tracking-wider border border-red-500/30 text-red-400 hover:bg-red-950/20 transition-colors" :disabled="loading" x-text="loading ? 'Disabling…' : 'Confirm Disable'"></button>
        </div>
      </form>
    </section>
  </main>

  <script>
    function accountApp() {
      return {
        loading: false,
        errorMsg: '',
        successMsg: '',
        view: 'status',
        email: '',
        mfaEnabled: false,
        mfaMandatory: false,
        password: '',
        mfaCode: '',
        mfaSetup: { secret: '', qrCodeUrl: '', recoveryCodes: [] },

        async load() {
          try {
            const resp = await fetch('/api/v1/mfa/status');
            if (resp.status === 401) { window.location.href = '/login'; return; }
            const data = await resp.json();
            this.email = data.email || '';
            this.mfaEnabled = !!data.mfa_enabled;
            this.mfaMandatory = !!data.mfa_mandatory;
          } catch (e) {
            this.errorMsg = 'Failed to load account status.';
          }
        },

        async startEnable() {
          this.loading = true; this.errorMsg = '';
          try {
            const resp = await fetch('/api/v1/mfa/setup', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ password: this.password })
            });
            const data = await resp.json().catch(() => ({}));
            this.password = '';
            if (resp.ok) {
              this.mfaSetup.secret = data.secret;
              this.mfaSetup.qrCodeUrl = 'https://chart.googleapis.com/chart?cht=qr&chl=' + encodeURIComponent(data.provisioning_uri) + '&chs=200x200&chld=L|0';
              this.mfaSetup.recoveryCodes = data.recovery_codes || [];
              this.view = 'enroll';
            } else {
              this.errorMsg = data.error || 'MFA setup failed.';
              this.view = 'status';
            }
          } catch (e) {
            this.errorMsg = 'Server error during MFA setup.';
            this.view = 'status';
          } finally { this.loading = false; }
        },

        async confirmEnable() {
          this.loading = true; this.errorMsg = '';
          try {
            const resp = await fetch('/api/v1/mfa/enable', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ code: this.mfaCode })
            });
            const data = await resp.json().catch(() => ({}));
            if (resp.ok) {
              this.mfaCode = '';
              this.successMsg = 'MFA enabled successfully.';
              this.view = 'status';
              await this.load();
            } else {
              this.errorMsg = data.error || 'Verification code failed.';
            }
          } catch (e) {
            this.errorMsg = 'Server error during MFA verification.';
          } finally { this.loading = false; }
        },

        async confirmDisable() {
          this.loading = true; this.errorMsg = '';
          try {
            const resp = await fetch('/api/v1/mfa/disable', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ password: this.password })
            });
            const data = await resp.json().catch(() => ({}));
            this.password = '';
            if (resp.ok) {
              this.successMsg = 'MFA disabled.';
              this.view = 'status';
              await this.load();
            } else {
              this.errorMsg = data.error || 'Failed to disable MFA.';
              this.view = 'status';
            }
          } catch (e) {
            this.errorMsg = 'Server error while disabling MFA.';
            this.view = 'status';
          } finally { this.loading = false; }
        }
      }
    }
  </script>
</body>
</html>
```

- [ ] **Step 2: Run the full backend test file (now that account.html exists)**

Run: `cd ldv-backend && python3 tests/test_mfa_enforcement.py`
Expected: `OK`

- [ ] **Step 3: Manual verification**

There is no frontend test framework in this repo (no existing JS tests for any `.html` page) — verify by hand:

```bash
cd ldv-backend
FLASK_APP=app.py LDV_SECRET_KEY=devkey python3 -m flask run --port 5000
```

In a browser: log in at `http://127.0.0.1:5000/login`, navigate to `http://127.0.0.1:5000/account`. Confirm:
1. Status card shows "Disabled" with an "Enable MFA" button.
2. Clicking it prompts for password; entering the wrong password shows an inline error (401), not a crash.
3. Entering the correct password shows the QR code, manual key, and 10 recovery codes.
4. Entering a valid 6-digit code from an authenticator app (or computed via `pyotp.TOTP(secret).now()` in a Python shell using the displayed manual key) enables MFA and returns to the status card showing "Enabled".
5. Clicking "Disable MFA" → correct password → status returns to "Disabled".

- [ ] **Step 4: Commit**

```bash
git add ldv-frontend/account.html
git commit -m "feat: add self-service MFA account settings page"
```

---

### Task 6: `admin.html` — MFA Enforcement toggle in Organizations tab

**Files:**
- Modify: `ldv-frontend/admin.html:550-559` (table header)
- Modify: `ldv-frontend/admin.html:562-591` (table row)
- Modify: `ldv-frontend/admin.html:1030-1032` (org load coercion)
- Modify: `ldv-frontend/admin.html:1224` (add new method after `saveOrgRetention`)

**Interfaces:**
- Consumes: `POST /api/v1/admin/organizations/<org_id>/mfa-required` (Task 2)

- [ ] **Step 1: Add the table header**

In `ldv-frontend/admin.html`, the Organizations table header currently reads (lines 550-559):

```html
                <thead>
                  <tr class="font-body text-xs text-on-surface-variant">
                    <th>Org ID</th>
                    <th>Corporate Tenant Name</th>
                    <th>Data Retention Policy</th>
                    <th>Monthly Scan Limits</th>
                    <th>Status</th>
                    <th style="text-align:right;">Save Configurations</th>
                  </tr>
                </thead>
```

Add an "MFA Enforcement" column after "Data Retention Policy":

```html
                <thead>
                  <tr class="font-body text-xs text-on-surface-variant">
                    <th>Org ID</th>
                    <th>Corporate Tenant Name</th>
                    <th>Data Retention Policy</th>
                    <th>MFA Enforcement</th>
                    <th>Monthly Scan Limits</th>
                    <th>Status</th>
                    <th style="text-align:right;">Save Configurations</th>
                  </tr>
                </thead>
```

- [ ] **Step 2: Add the table cell**

The retention `<td>` (lines 566-574) is immediately followed by the scan-limits `<td>`. Insert a new cell between them:

```html
                      <td>
                        <button type="button"
                                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase border transition-colors"
                                :class="org.mfa_required ? 'bg-teal-950/40 text-teal-400 border-teal-500/20' : 'bg-surface-container border-outline-variant/30 text-on-surface-variant hover:border-primary/40'"
                                @click="toggleOrgMfaRequired(org)"
                                x-text="org.mfa_required ? 'Enforced' : 'Optional'"></button>
                      </td>
```

- [ ] **Step 3: Coerce `mfa_required` to a boolean on load**

In `ldv-frontend/admin.html`, the `load()` method currently maps retention values (lines 1029-1032):

```js
            // Map temp retention values
            this.organizations.forEach(o => {
              this.tempRetention[o.id] = o.retention_days || 30;
            });
```

Extend it to also coerce `mfa_required` (SQLite returns `0`/`1`, not booleans):

```js
            // Map temp retention values
            this.organizations.forEach(o => {
              this.tempRetention[o.id] = o.retention_days || 30;
              o.mfa_required = !!o.mfa_required;
            });
```

- [ ] **Step 4: Add the toggle method**

In `ldv-frontend/admin.html`, immediately after `saveOrgRetention` (currently ending at line 1224):

```js
        async toggleOrgMfaRequired(org) {
          this.errorMsg = '';
          this.successMsg = '';
          const next = !org.mfa_required;
          try {
            const resp = await fetch(`/api/v1/admin/organizations/${org.id}/mfa-required`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ mfa_required: next })
            });
            if (resp.ok) {
              org.mfa_required = next;
              this.successMsg = `MFA enforcement ${next ? 'enabled' : 'disabled'} for organization #${org.id}.`;
            } else {
              const data = await resp.json();
              this.errorMsg = data.error || 'Failed to update MFA enforcement.';
            }
          } catch (e) {
            this.errorMsg = 'Network error.';
          }
        },
```

- [ ] **Step 5: Manual verification**

With the dev server running (from Task 5, Step 3) and logged in as an admin:
1. Go to `http://127.0.0.1:5000/admin#orgs`.
2. Confirm the new "MFA Enforcement" column renders "Optional" for existing orgs.
3. Click it → button flips to "Enforced" and a success banner appears.
4. Reload the page → confirm it still shows "Enforced" (persisted).
5. Log in as a user in that org without MFA set up → confirm they now hit the enrollment flow at `/login` (this exercises the same `mfa_enroll_required` path covered by the Task 2 test, now driven by the real UI toggle).

- [ ] **Step 6: Commit**

```bash
git add ldv-frontend/admin.html
git commit -m "feat: add MFA enforcement toggle to admin Organizations tab"
```

---

### Task 7: Wire entry points (`index.html` banner + `admin.html` sidebar link)

**Files:**
- Modify: `ldv-frontend/index.html:200-208`
- Modify: `ldv-frontend/admin.html:312-320`

- [ ] **Step 1: Turn the index.html MFA banner into a link**

In `ldv-frontend/index.html`, the banner currently reads (lines 200-208):

```html
    <div x-show="showMfaWarning" x-cloak style="display:none;" class="mb-8 flex items-center justify-between bg-amber-900/20 border border-amber-500/30 rounded p-4 text-amber-200 text-sm font-body">
      <div class="flex items-center gap-3">
        <span class="material-symbols-outlined text-amber-500">warning</span>
        <span><strong>Security Notice:</strong> Multi-Factor Authentication (MFA) is not enabled on your account. We strongly advise activating it in your security settings to secure institutional assets.</span>
      </div>
      <button @click="dismissMfaWarning()" class="text-amber-400 hover:text-amber-200 transition-colors flex items-center">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </div>
```

Change the `<span>` text to a link to `/account`:

```html
    <div x-show="showMfaWarning" x-cloak style="display:none;" class="mb-8 flex items-center justify-between bg-amber-900/20 border border-amber-500/30 rounded p-4 text-amber-200 text-sm font-body">
      <div class="flex items-center gap-3">
        <span class="material-symbols-outlined text-amber-500">warning</span>
        <span><strong>Security Notice:</strong> Multi-Factor Authentication (MFA) is not enabled on your account. <a href="/account" class="underline hover:text-amber-50 transition-colors">Activate it in your security settings</a> to secure institutional assets.</span>
      </div>
      <button @click="dismissMfaWarning()" class="text-amber-400 hover:text-amber-200 transition-colors flex items-center">
        <span class="material-symbols-outlined text-[18px]">close</span>
      </button>
    </div>
```

- [ ] **Step 2: Add an Account & Security link to the admin sidebar**

In `ldv-frontend/admin.html`, the sidebar footer currently reads (lines 312-320):

```html
    <div class="px-6 mt-auto font-body">
      <div class="flex flex-col gap-3 pt-6 border-t border-outline-variant/10">
        <a class="flex items-center gap-3 text-on-surface-variant hover:text-primary transition-colors text-xs" href="/logout" style="text-decoration:none;">
          <span class="material-symbols-outlined text-[20px]">logout</span>
          <span>Secure Logout</span>
        </a>
      </div>
    </div>
```

Add an "Account & Security" link above "Secure Logout":

```html
    <div class="px-6 mt-auto font-body">
      <div class="flex flex-col gap-3 pt-6 border-t border-outline-variant/10">
        <a class="flex items-center gap-3 text-on-surface-variant hover:text-primary transition-colors text-xs" href="/account" style="text-decoration:none;">
          <span class="material-symbols-outlined text-[20px]">shield_person</span>
          <span>Account & Security</span>
        </a>
        <a class="flex items-center gap-3 text-on-surface-variant hover:text-primary transition-colors text-xs" href="/logout" style="text-decoration:none;">
          <span class="material-symbols-outlined text-[20px]">logout</span>
          <span>Secure Logout</span>
        </a>
      </div>
    </div>
```

- [ ] **Step 3: Manual verification**

With the dev server running:
1. Log in at `/login` with a user that has no MFA enabled and is not in an MFA-mandatory org/role → confirm the amber banner on `/` now contains a working link to `/account`.
2. Go to `/admin` as an admin → confirm the "Account & Security" sidebar link appears above "Secure Logout" and navigates to `/account`.

- [ ] **Step 4: Commit**

```bash
git add ldv-frontend/index.html ldv-frontend/admin.html
git commit -m "feat: link MFA banner and admin sidebar to the account settings page"
```
