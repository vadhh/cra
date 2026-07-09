# MFA Break-Glass Recovery Runbook

**Purpose**: Provide system administrators and organization managers with clear, step-by-step procedures to recover accounts when users lose access to their Multi-Factor Authentication (MFA) devices or recovery codes.

---

## 1. MFA Enforcement Architecture

The Contract Risk Analyzer (CRA) enforces MFA dynamically via [auth.py](file:///home/stardhoom/LDV/ldv-backend/auth.py#L128-L142) and [app.py](file:///home/stardhoom/LDV/ldv-backend/app.py#L358-L403).
- **Mandatory Roles**: In staging/production environments, accounts with roles of `admin`, `manager`, or `reviewer` are forced to enroll in MFA on their first login.
- **Organization Policies**: Organization Managers can toggle mandatory MFA for all accounts within their tenancy via the admin dashboard.
- **Exemptions**: A database-level flag `mfa_exempt = 1` bypasses all MFA enforcement checks for a specific account. This is designed for testing and emergency recovery.
- **Storage**: User MFA configurations (AES-encrypted TOTP secrets and hashed recovery codes) are stored in the `users` table of `sydeco.db`.

---

## 2. Recovery Scenario A: User has Recovery Codes (Self-Service)

During the initial MFA enrollment, users are presented with **10 hex-encoded recovery codes** (e.g., `8d2f19a0`). These are stored securely on the backend as password-compatible hashes.

### Instructions:
1. Navigate to the login page `/login`.
2. Input the email and password as usual.
3. When prompted for the 6-digit MFA verification code, input one of the unused 8-character recovery codes instead.
4. The system will verify, log the event (`mfa.recovery_used` in audit logs), delete that specific recovery code from the database, and authenticate the session.

> [!WARNING]
> Recovery codes are strictly **one-time use**. After logging in, the user should immediately navigate to the `/account` settings page to generate a new MFA setup and record a new set of recovery codes.

---

## 3. Recovery Scenario B: User lost TOTP and Recovery Codes (Standard Reset)

If a regular user is locked out and has no remaining recovery codes, their MFA must be reset by an administrator or manager.

### Option 1: Web UI Reset (Recommended)
1. A System Administrator or the user's Org Manager logs into the admin panel (`/admin.html`).
2. Go to the **Team Management** tab.
3. Locate the locked user's row and click the **MFA Reset** button.
4. Confirm the action. This fires a request to:
   `POST /api/v1/admin/users/<target_id>/mfa-reset`
5. The user's `mfa_secret` and `mfa_recovery_codes` are cleared. 
6. On their next login, the user will be treated as a new enrollee and prompted to register a new MFA device.

> [!NOTE]
> Org Managers can only reset MFA for users within their own organization. System Administrators can reset MFA for any user in the system.

### Option 2: CLI MFA Exemption (SSH access required)
If the web interface is unavailable, a system operator can exempt the user via the command-line interface on the hosting machine:

1. Log into the CRA host server.
2. Navigate to the backend directory and run:
   ```bash
   python manage.py set-mfa-exempt user@example.com
   ```
3. The user can now log in using only their email and password (the MFA prompt will be bypassed).
4. Have the user navigate to `/account`, set up a new MFA app, and download their new recovery codes.
5. Once configured, **immediately revoke** the temporary CLI exemption:
   ```bash
   python manage.py set-mfa-exempt user@example.com --off
   ```

---

## 4. Recovery Scenario C: Administrator Locked Out (Break-Glass)

If the primary System Administrator account is locked out (e.g., lost TOTP app and no recovery codes), use the following server-side break-glass commands.

### Step 1: Grant Temporary Exemption
Access the server terminal and run:
```bash
python manage.py set-mfa-exempt admin@example.com
```
*Audit log entry generated: `user.mfa_exempt_change` set to `True`.*

### Step 2: Re-Enroll via UI
1. Navigate to `/login` and log in with the administrator credentials (no MFA code will be requested).
2. Go to `/account` (or `/admin.html`).
3. Set up MFA, scan the new QR code, verify the setup code, and save the new recovery codes.

### Step 3: Revoke Exemption
Return to the server terminal and run:
```bash
python manage.py set-mfa-exempt admin@example.com --off
```
*MFA enforcement is now restored for the administrator account.*

---

## 5. Emergency Recovery: Total Seeding Fallback

If the database is corrupted or all administrator credentials are lost, you can provision a new `pilot-admin` account with an automatic MFA exemption:

1. Set the emergency password environment variable:
   ```bash
   export LDV_PILOT_ADMIN_PASSWORD="TemporaryEmergencyStrongPassword123!"
   ```
2. Execute the idempotency tool:
   ```bash
   python manage.py ensure-pilot-admin
   ```
3. This creates/restores the administrator account `pilot-admin@example.com` (or the configured pilot email) and marks it as `mfa_exempt = 1`.
4. Log into the system using this emergency account to manage the database, audit the logs, or reset other administrative credentials.
5. Clean up the environment password variable after use:
   ```bash
   unset LDV_PILOT_ADMIN_PASSWORD
   ```
