# MFA Enforcement Toggle + Self-Service Account Settings

Date: 2026-07-02

## Context

CLAUDE.md's P0 TODO lists "MFA enforcement UI, org/user management UI" as
outstanding. An audit of the current codebase found this note stale:
`admin.html` already ships full Team Management (create/suspend/role-change/
MFA-reset/download-access) and Organizations (create/retention) tabs, and
`login.html` already implements the complete MFA enrollment/challenge/
recovery-code flow, driven by `auth.is_mfa_mandatory()`.

Two real gaps remain:

1. `organizations.mfa_required` (column + `database.org_mfa_required()`
   reader, already consulted by `is_mfa_mandatory()`) has no write path —
   no API endpoint, CLI command, or UI control ever sets it. Org-wide MFA
   enforcement is currently unreachable.
2. `index.html` tells users to "activate MFA in your security settings,"
   but no such page exists. A user whose org doesn't mandate MFA has no way
   to opt in voluntarily.

## A. Org-wide MFA enforcement toggle

### Backend

- `database.py`: add `set_org_mfa_required(org_id: int, required: bool) -> None`,
  mirroring the existing `set_org_retention`. Add `"org.mfa_required_change"`
  to the audit-action allowlist (same list that already contains
  `"org.retention_change"`).
- `app.py`: new route

  ```
  POST /api/v1/admin/organizations/<int:org_id>/mfa-required
  @auth.role_required("manager")
  ```

  Body: `{"mfa_required": true|false}`. Permission model matches the
  existing retention endpoint exactly: non-admin callers are forbidden
  (403) unless `org_id == user["org_id"]`; admins may target any org.
  Writes an audit log entry (`user_id`, `org_id`, `resource_id=org_id`,
  `detail=str(mfa_required)`). Returns `{"ok": true}`.

No migration required — the column and reader already exist and are
already wired into `auth.is_mfa_mandatory()`; this closes the write-side
gap only.

### Frontend

`admin.html` Organizations tab: add an "MFA Enforcement" column next to
the existing retention-policy column. Renders as a two-state
Enabled/Disabled toggle (not a multi-option select like retention) that
POSTs immediately on click — no separate "Save" step, since it's a
boolean flip rather than a staged multi-field form. New JS method
`setOrgMfaRequired(orgId, required)` calls the new endpoint and reloads
that org's row from the already-loaded `organizations` array (no full
page refetch).

## B. Self-service security settings page

### Backend

None. `/api/v1/mfa/status`, `/api/v1/mfa/setup`, `/api/v1/mfa/enable`, and
`/api/v1/mfa/disable` already operate against `session["uid"]` (not just
`mfa_enroll_pending_uid`), so a logged-in user hitting these endpoints
outside the forced-enrollment flow already works today. `/disable`
already 403s when `org_mfa_required()` or `auth.is_mfa_mandatory()` is
true — the new page just needs to surface that error message.

The only route addition is serving the page itself:

```python
@app.route("/account")
def account_page():
    user = auth.current_user()
    if user is None:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "account.html")
```

No role restriction — any authenticated user may view their own settings.

### Frontend

New `ldv-frontend/account.html`, same visual system (Alpine.js, Tailwind
config, glass-card styling) as `admin.html`/`login.html`.

- On load: `GET /api/v1/mfa/status` → shows a status badge (`mfa_enabled`)
  and, if `mfa_mandatory` is true, a note explaining MFA cannot be
  disabled by the user.
- If MFA is off: "Enable MFA" button drives the same
  setup → QR code + manual key + recovery codes → 6-digit confirm → enable
  sequence already implemented in `login.html`'s `mfa_enroll` state,
  reusing `/api/v1/mfa/setup` and `/api/v1/mfa/enable`.
- If MFA is on: "Disable MFA" button calls `/api/v1/mfa/disable`; on 403
  (mandatory), show the returned error inline rather than treating it as
  a network failure.
- No recovery-code viewing/regeneration UI — codes are stored hashed and
  can't be redisplayed. Regenerating (disable then re-enroll) is already
  possible through the two flows above without a dedicated endpoint.

### Entry points

- `index.html`: existing "Multi-Factor Authentication is not enabled on
  your account" banner becomes a link to `/account` (currently static
  text).
- `admin.html` sidebar: add an "Account & Security" link above "Secure
  Logout".

## Testing

One test module extension (wherever org/auth admin endpoints are
currently tested) covering:

- Manager can set `mfa_required` for their own org.
- Manager gets 403 attempting to set it for a different org.
- Admin can set it for any org.
- After toggling an org's `mfa_required` to true, a user in that org
  without `mfa_secret` receives `mfa_enroll_required: true` on next login
  (end-to-end confirmation that the toggle actually reaches
  `is_mfa_mandatory()`).

No test for the account-settings page beyond the above, since it exercises
already-tested MFA endpoints with no new backend logic.

## Out of scope

- Server-side trusted-device tracking (currently client-only localStorage,
  30-day trust). Explicitly deferred per user decision during
  brainstorming.
- Recovery-code viewing/regeneration as a dedicated feature.
- Self-service password change (bundled option declined during
  brainstorming — MFA-only scope chosen).
