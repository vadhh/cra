# CR-01 — AuthN/AuthZ & Tenant Isolation (core-gap-first)

**Date:** 2026-06-22
**P0 item:** CR-01 (external review) / IAM-01–05, SEC-01 (PRD §10.1, §14)
**Scope decision:** core security gap first — defer MFA, full role matrix, signed-link expiry, audit log.

## Problem

The data path has no authentication. `/upload`, `/analyze`, and `/report` are fully
open; `/api/result/<uuid>` is protected only by the unguessable UUID. Documents and
analyses have no owner. A leaked or guessed UUID = full read access (IDOR). Admin
endpoints rely on a shared header token or loopback, not real accounts.

This closes the unauthenticated-access + cross-tenant-IDOR hole. It does **not**
implement the entire PRD IAM spec (see Deferred).

## Decisions

- **Scope:** core gap first.
- **Mechanism:** Flask signed-cookie sessions (browser) + per-user API token (curl).
- **Provisioning:** CLI, env-seeded bootstrap admin. No public signup.
- **Password hashing:** `werkzeug.security` (existing Flask dep — no new dependency).
- **Tokens:** stdlib `secrets.token_urlsafe`.
- **Roles:** two only — `admin`, `user`. Full 5-role matrix deferred.
- Admin shared-token guard is **replaced** by admin accounts (not kept as fallback).
- Existing test data backfills to the seed admin's org (not orphaned).

## Data model (`database.py`)

New tables:

```sql
CREATE TABLE organizations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id        INTEGER NOT NULL REFERENCES organizations(id),
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user',   -- 'admin' | 'user'
    api_token     TEXT UNIQUE,
    active        INTEGER NOT NULL DEFAULT 1,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Ownership columns on `documents` (analyses inherit ownership via `document_id` join,
so no column is added to `analyses`):

```sql
ALTER TABLE documents ADD COLUMN org_id   INTEGER REFERENCES organizations(id);
ALTER TABLE documents ADD COLUMN owner_id INTEGER REFERENCES users(id);
```

`init_db()` migration: create new tables, add the two columns if missing, and backfill
existing `documents` rows to the seed admin's org (if a seed admin exists; otherwise
leave NULL — NULL-org rows are admin-visible only).

## Auth mechanism

- **Browser:** `POST /login` with `email`+`password` → on success sets `session["uid"]`.
  Requires `app.secret_key`. Sourced from `LDV_SECRET_KEY`. If unset: generate an
  ephemeral per-process key via `secrets.token_hex` and log a loud warning (dev only —
  sessions will not survive a restart). `POST /logout` clears the session.
- **Programmatic:** per-user `api_token`, sent as `Authorization: Bearer <token>`.
- `get_current_user()` resolves the user from session **or** bearer token (active users
  only) and stores it on `flask.g`.
- `@login_required` — 401 if no current user.
- `@admin_required` — `@login_required` + `g.user.role == 'admin'`, else 403.

Password verification uses `check_password_hash`; comparison is constant-time inside
werkzeug. Login failures return a generic 401 (no user-enumeration distinction between
unknown email and bad password).

## Authorization rules (`app.py`)

| Endpoint | Guard | Notes |
|----------|-------|-------|
| `POST /upload` | `@login_required` | stamps `owner_id` + `org_id` from `g.user` |
| `POST /analyze` | `@login_required` | legacy curl path; still processes confidential text |
| `POST /report` | `@login_required` | |
| `GET /api/result/<uuid>` | `@login_required` + ownership | `admin OR row.org_id == g.user.org_id` else **403** |
| `GET /api/stats` | `@admin_required` | replaces `_admin_authorized()` |
| `GET /api/recent` | `@admin_required` | replaces `_admin_authorized()` |
| `GET /admin` | `@admin_required` | |

Ownership check is enforced in the DB read path: `get_result()` continues to join
`documents`, and the view returns 403 (not 404) when the row exists but belongs to
another org — matching the PRD IAM-03 acceptance criterion ("cross-org access → 403
even with a valid UUID").

## Provisioning CLI (`manage.py`)

- `seed-admin` — reads `LDV_ADMIN_EMAIL` / `LDV_ADMIN_PASSWORD`, creates a default org
  (`"Sydeco"`) + an `admin` user. Idempotent (skips if the email already exists).
- `create-org <name>`
- `create-user <email> <org-name> [--role user|admin]` — generates a random password
  and api_token, prints both once to stdout (never stored in plaintext).

## Frontend

- Add a minimal `login.html` (email/password form → `POST /login`).
- Existing portal JS: on a `401` from any fetch, redirect to `/login`.
- No org/user management UI in this pass (CLI covers the pilot).

## Testing (`tests/test_auth.py`)

Smallest runnable behavioral check, no framework beyond what the repo uses:

1. anonymous `GET /api/result/<uuid>` → 401
2. cross-org result (org B user reading org A's analysis) → 403
3. owner reads own result → 200
4. admin reads any result → 200
5. wrong password → 401 (and unknown email → same generic 401)
6. valid `api_token` authenticates a programmatic request → 200
7. anonymous `POST /upload` → 401

## Explicitly deferred (follow-up P0/P1)

- MFA (IAM-05 strong-auth portion beyond password).
- The `manager` / `analyst` / `legal reviewer` roles (full IAM-02 matrix).
- Org / user management web UI.
- **Signed, expiring** download links (IAM-04) — reports stay behind `@login_required`
  for now.
- Audit log of access/export/review/deletion events (SEC-06).
- Rate limiting / CSRF tokens (SEC-07) — session cookies should later be `SameSite`.

These do not block closing the unauthenticated-access and cross-tenant IDOR hole that
CR-01 is fundamentally about.
