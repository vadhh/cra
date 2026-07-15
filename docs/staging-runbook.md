# Staging Deployment Runbook

**Purpose:** Validate the LDV stack on a staging server before promoting to production.  
**Audience:** The engineer running the deploy.  
**Gate:** Every checkbox in this document must pass before flipping `LDV_PRODUCTION=1` on the real server.

---

## 1. Prerequisites

| Requirement | Check |
|-------------|-------|
| Python 3.10+ | `python3 --version` |
| libmagic (`libmagic1`) | `apt install libmagic1` |
| rsync (for backups) | `apt install rsync` |
| NVIDIA driver + CUDA (optional, speeds up L2/L4) | `nvidia-smi` |
| Port 5000 open on the staging host | firewall / security group |
| A second machine or directory for backup rsync target | — |

---

## 2. Clone and Install

```bash
git clone https://github.com/vadhh/cra.git /opt/ldv
cd /opt/ldv/ldv-backend
pip install -r requirements.txt
```

Verify pinned deps installed cleanly — no version conflicts in pip output.

---

## 2a. Alternative: Docker Compose (skips steps 3–5)

`docker-compose.yml` runs the full stack (app + redis + nginx/TLS) in one command. Faster for local/staging smoke-testing than the bare-metal path above.

```bash
git clone https://github.com/vadhh/cra.git /opt/ldv && cd /opt/ldv

# nginx needs a cert — deploy/certs/ is gitignored (holds a private key),
# so a fresh clone has none. Generate a self-signed one first:
bash deploy/gen-cert.sh          # writes deploy/certs/server.{crt,key}

export LDV_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
export LDV_ENCRYPTION_KEY=$(cd ldv-backend && python3 manage.py gen-key)

docker compose up --build
```

Skipping `gen-cert.sh` is why nginx fails with `cannot load certificate "/etc/nginx/certs/server.crt"` — the mount exists, the file doesn't.

Seed the admin account (once containers are up):
```bash
docker compose exec app python3 manage.py seed-admin
```

Serves on `https://localhost` (self-signed — browser will warn). Continue at section 6 for the health check.

---

## 3. Environment Variables

Create `/opt/ldv/ldv-backend/.env` (never commit this file):

```bash
# --- REQUIRED ---
LDV_SECRET_KEY=<generate: python3 -c "import secrets; print(secrets.token_hex(32))">
LDV_ENCRYPTION_KEY=<generate: python3 manage.py gen-key>
LDV_PRODUCTION=1

# --- SECURITY ---
LDV_COOKIE_SECURE=1          # set to 0 only if staging has no HTTPS
LDV_CORS_ORIGINS=https://staging.example.com

# --- STORAGE ---
LDV_DB_PATH=/opt/ldv/data/sydeco.db
LDV_RETENTION_DAYS=30

# --- BACKUP ---
LDV_BACKUP_DIR=/var/backups/ldv
LDV_BACKUP_REMOTE=user@backup-host:/backups/ldv   # optional

# --- OPTIONAL ---
LDV_MAX_UPLOAD_MB=10
LDV_DOWNLOAD_LINK_TTL=900
LDV_REMOTE_TRANSLATION=0     # 1=Google, local=Helsinki-NLP offline
LDV_DEBUG=0                  # never 1 in staging/prod
```

Load before any command:
```bash
set -a && source /opt/ldv/ldv-backend/.env && set +a
```

Harden the file:
```bash
chmod 600 /opt/ldv/ldv-backend/.env
```

---

## 4. Database Initialisation

```bash
cd /opt/ldv/ldv-backend
mkdir -p /opt/ldv/data

# Init schema + run all migrations
python3 -c "import database; database.init_db()"

# Seed the first admin account
LDV_ADMIN_EMAIL=admin@example.com \
LDV_ADMIN_PASSWORD=<strong-password> \
python3 manage.py seed-admin

# Create a test org and users
python3 manage.py create-org "Test Org"
python3 manage.py create-user analyst@example.com "Test Org" --role analyst
python3 manage.py create-user reviewer@example.com "Test Org" --role reviewer
```

---

## 5. Start the Server

```bash
cd /opt/ldv/ldv-backend
gunicorn -w 2 -b 0.0.0.0:5000 \
  --timeout 120 \
  --access-logfile /var/log/ldv-access.log \
  --error-logfile /var/log/ldv-error.log \
  app:app
```

> Use `-w 1` if GPU memory is tight — each worker loads its own model copy.

---

## 6. Health Check

```bash
curl -s http://localhost:5000/health | python3 -m json.tool
```

Expected — all fields must be non-degraded:

```json
{
  "status": "ok",
  "encryption": "enabled",
  "layer2_available": true,
  "layer4_available": false,
  "db": "ok",
  "datasets": "ok"
}
```

**Block on:** `encryption: degraded` (means `LDV_ENCRYPTION_KEY` not set), `db: error`.

---

## 7. Automated Test Suite

```bash
cd /opt/ldv/ldv-backend

# Generate fixtures (once)
python3 tests/create_fixtures.py

# Quick regression (~2 min)
python3 tests/run_validation.py

# Full checklist (~10 min, skips L4 PENDING sections)
python3 tests/run_full_validation.py
```

Expected: **≥60 PASS · 0 FAIL**. WARN on `legal_mlp.pkl` is acceptable. Any FAIL = stop.

---

## 8. Auth & MFA Smoke Test

```bash
BASE=http://localhost:5000

# 1. Login as analyst
curl -sc cookies.txt -X POST $BASE/login \
  -H "Content-Type: application/json" \
  -d '{"email":"analyst@example.com","password":"<password>"}'
# Expect: {"mfa_enroll_required": true}  OR  session cookie

# 2. Skip MFA as analyst (must succeed — analyst role not mandatory)
curl -sb cookies.txt -X POST $BASE/api/v1/mfa/skip
# Expect: {"ok": true}

# 3. Set org mfa_required and retry (must be blocked)
# sqlite3 /opt/ldv/data/sydeco.db \
#   "UPDATE organizations SET mfa_required=1 WHERE name='Test Org';"
curl -sb cookies.txt -X POST $BASE/api/v1/mfa/skip
# Expect: 403 {"error": "MFA is mandatory for this account"}

# 4. Reviewer role — skip must always be 403 (role is mandatory)
curl -sc cookies2.txt -X POST $BASE/login \
  -H "Content-Type: application/json" \
  -d '{"email":"reviewer@example.com","password":"<password>"}'
curl -sb cookies2.txt -X POST $BASE/api/v1/mfa/skip
# Expect: 403
```

---

## 9. Upload & Analysis Smoke Test

```bash
# Upload a contract (requires auth cookie from step 8)
curl -sb cookies.txt -X POST $BASE/upload \
  -F "file=@/path/to/test-contract.pdf"
# Expect: {"id": "<uuid>", "status": "queued"}

UUID=<uuid from above>

# Poll until completed
curl -sb cookies.txt $BASE/api/v1/result/$UUID
# Expect: {"status": "completed", "progress_pct": 100, "_meta": {"encryption_enabled": true}, ...}
```

---

## 10. Cross-Org Access Control

```bash
# Create a second org + user
python3 manage.py create-org "Other Org"
python3 manage.py create-user other@example.com "Other Org" --role analyst

# Login as other@example.com, try to fetch the UUID from step 9
# Expect: 403 Forbidden
```

---

## 11. Backup Smoke Test

```bash
mkdir -p /var/backups/ldv

# Dry run first
python3 manage.py backup --dry-run

# Real run
python3 manage.py backup

# Confirm timestamped dir exists
ls /var/backups/ldv/
# Expect: 20260701T020000Z/sydeco.db  20260701T020000Z/uploads/
```

Install the nightly cron:
```bash
sudo cp /opt/ldv/deploy/ldv-backup.cron /etc/cron.d/ldv-backup
sudo chmod 644 /etc/cron.d/ldv-backup
# Edit the file: update /opt/ldv path and www-data user if different
```

---

## 12. Manual QA — Lawyer Spot-Check

Upload 5–10 real contracts (mix of FR/ID/NL, invoice + service agreement) and verify:

- [ ] `governing_law` detected correctly
- [ ] `jurisdiction` detected correctly
- [ ] `document_type` matches the actual contract type
- [ ] `red_flags` fire on genuinely risky clauses, not on clean contracts
- [ ] Citations shown are `verified` only (no `draft` in output)
- [ ] Risk score feels calibrated
- [ ] Non-contract documents (invoices) score low / get non-contract routing

This is the hardest gate. Code cannot substitute for a lawyer reading the output.

---

## 13. Production Promotion Checklist

Only proceed when all sections above pass:

- [ ] Section 6: `encryption: enabled`, `db: ok`
- [ ] Section 7: 0 FAIL
- [ ] Section 8: MFA skip returns 403 when mandatory
- [ ] Section 9: `encryption_enabled: true` in result, `progress_pct: 100`
- [ ] Section 10: 403 on cross-org UUID
- [ ] Section 11: backup dir created, nightly cron installed
- [ ] Section 12: lawyer spot-check signed off
- [ ] `LDV_COOKIE_SECURE=1` confirmed (HTTPS in place)
- [ ] `LDV_DEBUG=0` confirmed
- [ ] `.env` permissions: `chmod 600`
- [ ] Gunicorn running as non-root user (`www-data` or dedicated `ldv` user)
- [ ] Log rotation configured (`/etc/logrotate.d/ldv`)

---

## Known Acceptable Gaps at Staging

These are tracked but do not block the staging gate:

| Gap | Status |
|-----|--------|
| `legal_mlp.pkl` missing — `clause_tags` returns `[]` | Acceptable, sydeco_engine decoupled |
| L4 (Qwen) not loaded — `layer4_available: false` | Acceptable unless `?explain=1` is tested |
| FR/BE citation rows `draft` | Output suppresses drafts — acceptable |
| Bootstrap MLP risk scorer | Deterministic fallback active — acceptable |
