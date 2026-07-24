# Gate 3 — Internal Security Audit (2026-07-24)

**Scope:** `ldv-backend/` (Flask backend) — `app.py`, `auth.py`, `crypto.py`, `database.py`,
`manage.py`, `translator_client.py`, `worker.py`, `Dockerfile`, `requirements.txt`, and the
repository's git history/config as it pertains to secret handling.

**Method:** manual, code-level review (static reading + targeted `git log`/`git show`
inspection). No dynamic/penetration testing was performed against a running instance — this is
still not a substitute for an external pentest, but it is a real code-level audit, which is what
Gate 3 currently lacks.

**Auditor:** Claude (security-auditor agent), on behalf of the CRA 1.0-rc1 release process.

This is audit-only. No application code was modified.

---

## Summary verdict

**Gate 3 cannot be marked Passed as-is.** F-01 was originally raised as CRITICAL; **owner
(Afridho) reviewed and risk-accepted it 2026-07-24** — see note under F-01 below — so it no longer
independently blocks Gate 3. **Both HIGH findings (F-02, F-03) are fixed as of 2026-07-24** — see
their Status notes below. Beyond that, the auth/authz, CSRF, upload validation, and crypto code is
generally well-built and mostly matches the CLAUDE.md hardening claims — but 6 MEDIUM and 6 LOW
gaps remain (plaintext API tokens, DoS surface on file parsing, container running as root, etc.)
that should be fixed or explicitly risk-accepted before Gate 3 is closed.

| Severity | Count | Status |
|---|---|---|
| CRITICAL | 1 | Risk-accepted (F-01, 2026-07-24) |
| HIGH | 2 | ✅ Both fixed 2026-07-24 (F-02, F-03) |
| MEDIUM | 6 | Open |
| LOW | 6 | Open |
| INFO | 4 | N/A |

---

## CRITICAL

### F-01 — Live production secrets committed to git and pushed to a remote
**File:** `.env` (repo root, tracked), introduced in commit `37befe6 "check and profil"`, present
unchanged at current `HEAD`/`staging`/`master`/`release/cra-1.0-rc1`.

**Description:** The repository's `.gitignore` correctly excludes `ldv-backend/*.db`,
`ldv-backend/.session_secret`, `ldv-backend/uploads/`, `ldv-backend/data/` — but a root-level
`.env` file is tracked by git and contains, in cleartext:

- `LDV_SECRET_KEY` — the Flask session-signing key
- `LDV_ENCRYPTION_KEY` — the Fernet key used for encryption-at-rest of uploaded file bytes,
  `extracted_text`, and `result_json` (per CLAUDE.md CR-04)

This commit exists on `master`, `staging`, and `release/cra-1.0-rc1` (all of which have tracking
remotes to `origin` = `https://github.com/vadhh/cra.git`), so these values are not just
locally present but have very likely been pushed to GitHub — meaning they are (or were)
retrievable by anyone with read access to that repository, and simply deleting `.env` today does
**not** remove them from git history.

**Why this is critical, concretely:**
- **Session forgery:** anyone holding `LDV_SECRET_KEY` can mint a Flask session cookie for any
  `uid`, impersonating any user including an admin, bypassing `login`/MFA entirely (`auth.py`
  `current_user()` trusts `session["uid"]` on the strength of the cookie signature alone).
- **Data-at-rest decryption:** anyone holding `LDV_ENCRYPTION_KEY` can decrypt every stored
  `result_json`/`extracted_text`/uploaded file — i.e. every client's contract text — either from a
  DB/backup copy or in combination with the SSRF/other access below.
- **Signed download-link forgery:** `app.py::_dl_keys()` derives the HMAC key used for
  `/download/<token>` links directly from `LDV_SECRET_KEY` (see F-03). Anyone with this key can
  mint a valid, non-expiring-in-practice download token for **any** `analysis_id` and pull the
  original file bytes with no authentication at all.
- This `.env` also contains `LDV_REMOTE_TRANSLATION=local`, and the repo has an `hf-space` git
  remote pointing at `huggingface.co/spaces/vadhhh/ldv-pilot` — i.e. there is a real, live pilot
  deployment, and these values have the shape of genuinely-generated secrets (64-hex-char
  `LDV_SECRET_KEY`, well-formed urlsafe-base64 Fernet key), not obvious placeholders. Treat them
  as compromised production secrets, not test fixtures.

**2026-07-24 risk-acceptance note (Afridho):** the `github.com/vadhh/cra.git` repository is
private, and `.env` is intentionally tracked so the HF Spaces pilot deployment can pick up its
values. Given the repo's private visibility, this is accepted as a lower-severity finding rather
than an active compromise. **Residual risk not yet addressed by this acceptance:** anyone added as
a collaborator to the private repo (or to the `huggingface.co/spaces/vadhhh/ldv-pilot` space,
which may have separate/broader access) gets the session-signing and data-at-rest keys in
cleartext, with no way to audit who has fetched them historically. If collaborator access ever
expands, or the repo visibility changes, these keys should be rotated and moved to a proper
secret-manager/platform-secrets mechanism rather than a tracked `.env`. The GitHub PAT embedded in
the local `origin` remote URL (`ghp_...@github.com/vadhh/cra.git`) is a separate, local-only
exposure (git config, not repo history) — still worth rotating on general hygiene grounds, but out
of scope for this acceptance.

**Remediation (do all of these, in order):**
1. **Rotate immediately.** Generate a new `LDV_SECRET_KEY` (`python -c "import secrets;
   print(secrets.token_hex(32))"`) and a new primary `LDV_ENCRYPTION_KEY`
   (`python manage.py gen-key`), deploy them out-of-band (real secret manager / platform secrets
   UI — HF Spaces "Repository secrets", not a committed file), and restart all workers.
   - For `LDV_ENCRYPTION_KEY`, use `MultiFernet` rotation as designed: put the new key **first**
     in the comma-separated list and keep the old (compromised) key appended so already-encrypted
     rows still decrypt, then re-encrypt-at-rest and drop the old key on a follow-up pass — see
     `crypto.py` docstring, which already documents this rotation story.
2. **Invalidate all existing sessions** (the old `LDV_SECRET_KEY` must stop being valid) and
   **rotate every user's `api_token`** — the download-link HMAC and the bearer tokens are only as
   good as `LDV_SECRET_KEY`/DB secrecy, both now suspect.
3. **Remove `.env` from git history**, not just the working tree (`git filter-repo` /
   BFG Repo-Cleaner across every branch that has commit `37befe6` — `master`, `staging`,
   `release/cra-1.0-rc1`, and any others), then force-push and have every collaborator re-clone.
   Add `.env` to `.gitignore` (it currently is **not** listed there even though the equivalent
   `.env`-derived runtime files are).
4. Treat the exposure as a real incident: if this repo/space is or was public, or if anyone
   outside the trusted team had read access at any point, assume the keys and any data encrypted
   or sessions signed with them were compromised, and document this for Gate 3/Gate 5 sign-off.
5. Separately, and out of scope of "backend code" but directly observed in the same audit: the
   configured `origin` git remote URL for this working tree embeds a GitHub **personal access
   token** in cleartext (`https://ghp_...@github.com/vadhh/cra.git`, visible via `git remote -v`
   / `.git/config`). This is a live credential sitting in plaintext on disk. Revoke/rotate this
   PAT in GitHub settings and reconfigure the remote to use SSH or a credential helper instead of
   embedding the token in the URL, regardless of whether it's technically "in the repo".

**Status:** OPEN — requires immediate action, independent of Gate 3 scheduling.

---

## HIGH

### F-02 — "admin" role is global/cross-tenant, not org-scoped, with no structural guardrail against a customer org being granted it
**Files:** `auth.py:97-125` (`role_required`, `admin_required`), `app.py` — every org-scoping
check (`api_result`, `api_delete_result`, `api_retry_result`, `api_download_link`, `api_stats`,
`api_recent`, `api_history`, `api_result_review`, the `/api/v1/admin/*` family) uses the pattern
`if user["role"] != "admin" and row.get("org_id") != user["org_id"]`.

**Description:** Every org-ownership check in the codebase is written as "allow if admin, else
require same org". `role == "admin"` is a single global flag with no per-org scoping column —
there is no concept of "admin of org X only". `manage.py create-user --role admin` and the
`/api/v1/admin/users` POST endpoint (when called by an existing global admin) can both mint an
`admin` user attached to **any** `org_id`, including a customer/pilot-tenant org, not just the
operator's own "Sydeco" org. If that ever happens — by provisioning mistake, an over-eager support
workflow, or a compromised admin account creating another admin under a different org — that
account gets unrestricted read/delete/download/manage access to **every** organization's contract
data, not just its own. This is architecturally different from what "per-org document ownership"
and a "5-role matrix" implies to a reader of CLAUDE.md/PRD, and is worth an explicit design
decision rather than an implicit one.

**Impact:** cross-tenant IDOR at the platform level, contingent on how `admin` accounts are
actually provisioned operationally (this is a design/process risk more than a directly
exploitable bug from outside, since creating an admin already requires an existing admin or
`manage.py` shell access — but it means the blast radius of "one admin credential compromised" is
*all* tenants, not one).

**Remediation:** Either (a) explicitly document that `admin` is a Sydeco-operator-only role never
to be granted to a customer-org account, and add a provisioning-time guard (e.g. `manage.py
create-user` refuses `--role admin` for any org other than the designated operator org; the
`/api/v1/admin/users` POST endpoint does the same), or (b) split the role into a true org-scoped
`org_admin` and a separate `platform_admin` capability gated more tightly (e.g. requiring a
dedicated env flag or a distinct login path). Given the current pilot is presumably single-tenant
or few-tenant, (a) is the fast fix; (b) is the correct long-term fix once there are multiple
paying orgs.

**Status:** ✅ FIXED 2026-07-24 (option a). Added `auth.is_operator_org(org_id)` (checks the
target org's name against `LDV_OPERATOR_ORG`, default `"Sydeco"`) and wired it as a guard in the
three admin-provisioning paths: `manage.py create-user --role admin` refuses for any org other
than the operator org; `POST /api/v1/admin/users` returns 403 when `role == "admin"` and the
target `org_id` isn't the operator org; `POST /api/v1/admin/users/<id>/role` returns 403 when
promoting a target user to `admin` outside the operator org. Full test suite 108/108 still
passing. Option (b) — splitting `admin` into `org_admin`/`platform_admin` — remains the
correct long-term fix once there are multiple paying orgs; not done here (out of scope for a
same-day High-severity fix).

### F-03 — Download-link HMAC key is naively derived from the session-signing secret (compounds F-01)
**File:** `app.py:389-402` (`_dl_keys`, `_make_download_token`, `_verify_download_token`).

**Description:** The signed/expiring download-link feature (IAM-04) is a good design — HMAC-SHA256
over `analysis_id:expires_at`, constant-time comparison via `hmac.compare_digest`, DB-tracked
one-time/revoked/expiry state. However, the signing key is not a dedicated secret: it's
`LDV_SECRET_KEY` (or the Flask session secret fallback) with the literal bytes `b":download"`
appended (`k + b":download"`). This is key *reuse with a naive suffix*, not a proper KDF
(e.g. HKDF) or an independent secret. Two consequences:
1. Anyone who obtains `LDV_SECRET_KEY` (see F-01) automatically obtains the download-link signing
   key too — there's no independent secret boundary between "can forge a session" and "can forge a
   download link". A defense-in-depth opportunity is lost.
2. HMAC with a *known, low-entropy, application-chosen* suffix appended to the key is not
   itself broken (HMAC's security doesn't depend on key-suffix secrecy the way it would for naive
   prefix-MAC schemes), but it's still non-standard key hygiene and worth tightening opportunistically.

**Remediation:** Derive the download-link key via a real KDF (e.g.
`hashlib.pbkdf2_hmac`/`hkdf` over `LDV_SECRET_KEY` with a fixed, distinct context label), or
better, support an independent `LDV_DOWNLOAD_LINK_SECRET` env var that defaults to the derived
value but can be rotated separately from the session secret. Low effort, meaningfully reduces
blast radius of a future session-secret leak.

**Status:** ✅ FIXED 2026-07-24. `app.py::_dl_keys()` now derives the download-link key via
`HMAC-SHA256(base_key, b"ldv-download-link-v1")` (domain separation, not a naive suffix) instead
of reusing `LDV_SECRET_KEY` with `+b":download"`. Also added an optional `LDV_DOWNLOAD_LINK_SECRET`
env var that, if set, overrides the derived key entirely — lets operators rotate the download-link
secret independently of the session secret. Full test suite 108/108 still passing.

---

## MEDIUM

### F-04 — API tokens stored in plaintext in the database
**File:** `database.py` (`users.api_token` column; `get_user_by_token`, `create_user`),
`manage.py` (`_gen_token`).

**Description:** Bearer API tokens (`tok-...` / `secrets.token_urlsafe(32)`) are stored as plain
text in the `users` table and looked up with a direct equality `SELECT ... WHERE api_token = ?`.
Unlike passwords (hashed via werkzeug) and MFA secrets (encrypted via `crypto.enc_str`), API
tokens get no protection at rest. Anyone who can read the `sydeco.db` file (backup, `LDV_DB_PATH`
misconfiguration, a future SQL-injection bug, an insider with filesystem access) can use every
token directly, indefinitely, with no rotation trigger.

**Remediation:** Store only a salted hash of the token (e.g. `sha256` is fine here since tokens
are already high-entropy random values, unlike passwords) and compare against the hash;
alternatively route tokens through `crypto.enc_str`/`dec_str` like the MFA secret. Provide a
`manage.py rotate-token <email>` command.

**Status:** OPEN.

### F-05 — No decompression/size bound on parsed DOCX/PDF content beyond the 10 MB upload cap
**File:** `app.py:206-241` (`_validate_and_extract`), `_extract_docx`/`_extract_pdf` (not shown
above but invoked here).

**Description:** Upload size is capped at `MAX_UPLOAD_BYTES` (10 MB default) before any parsing,
which is good baseline protection. But DOCX is a zip container and PDF supports internal
compression/object streams; neither `python-docx` (via Python's `zipfile`) nor `PyMuPDF` is given
an explicit decompressed-size or per-document CPU/memory ceiling in this code path. A small,
well-crafted "zip bomb" DOCX or a pathological PDF (deeply nested objects / compressed streams)
well under 10 MB compressed can expand to a much larger in-memory document or consume
disproportionate CPU during parsing. Given the analysis pipeline uses a single-worker
`ThreadPoolExecutor(max_workers=1)` (`worker.py`), one such file is enough to stall the entire
job queue for every tenant until it times out or OOMs the process — this is a more effective DoS
vector here than on a typical multi-worker service, precisely because of the P0 "async job queue"
design (CR-10).

**Remediation:** Add an explicit decompressed-text/page-count ceiling and a wall-clock timeout
around `_extract_docx`/`_extract_pdf` (the `_extract_pdf` path already computes `pages` — reject
above a sane page count before running full text extraction / L1–L4). `worker.py`'s single-thread
executor should also have a per-job timeout so one bad file can't wedge the queue indefinitely.

**Status:** OPEN.

### F-06 — Container runs as root
**File:** `Dockerfile`.

**Description:** No `USER` directive is set; the image runs `gunicorn` (and therefore the whole
Flask app, including all file/PDF/DOCX parsing of untrusted uploads) as `root` inside the
container. This is exactly the kind of untrusted-input-parsing workload (PDF/DOCX libraries have
had real memory-corruption CVEs historically) where container privilege matters — a parser
compromise as root inside the container is strictly worse than the same compromise as an
unprivileged user, especially combined with any future container-escape primitive.

**Remediation:** Add a non-root user and `USER` directive, e.g.:
```dockerfile
RUN useradd -m -u 1000 ldv
USER ldv
```
Ensure `/app/uploads`, `/app/data`, and the SQLite DB path are writable by that user (may need a
`chown` before the `USER` switch, or a mounted volume with correct ownership).

**Status:** OPEN.

### F-07 — Dependency versions not independently verified against CVE databases
**File:** `requirements.txt`.

**Description:** Pinning is done correctly (exact versions, no ranges) — this satisfies the
"reproducible deploy" P0 item. However, this audit was performed via static code reading only,
with no access to a live CVE feed/`pip-audit`/`safety` database, so no dependency in
`requirements.txt` (`torch`, `transformers`, `cryptography`, `Flask`, `gunicorn`,
`flask-limiter`, `python-magic`, `PyMuPDF`, etc.) has been checked against current CVE advisories
as part of this pass. Given the large ML dependency surface (`torch==2.11.0`,
`transformers==5.4.0`) and known history of deserialization/pickle-loading CVEs in the
ML-tooling ecosystem, this needs a dedicated automated pass.

**Remediation:** Run `pip-audit -r requirements.txt` (or `safety check`) as a CI gate before
Gate 3 sign-off, and periodically thereafter (e.g. weekly cron or on every dependency bump). Treat
any CRITICAL/HIGH CVE with no available patched pin as a Gate 3 blocker requiring a documented
risk acceptance.

**Status:** REQUIRES_USER_ACTION (needs a tool/network access this audit didn't have).

### F-08 — SSRF / data-exfiltration surface in the LightML translator microservice call is real but *config-gated*, not code-gated
**File:** `translator_client.py`.

**Description:** This module is already well-hardened relative to its risk (HTTPS-only unless
explicitly overridden, payload size cap, no body logging, fails open to "return original text" on
any error, hard `EXTERNAL_TRANSLATION_DISABLED=1` kill switch defaulting on) — the in-code
comments correctly acknowledge its own limits. The residual risk is structural, not a code bug:
`LIGHTML_TRANSLATOR_URL` is an operator-controlled env var, and nothing in code can verify it
actually points at a genuinely internal/protected host rather than an arbitrary attacker-controlled
HTTPS endpoint. If `EXTERNAL_TRANSLATION_DISABLED=0` and `LDV_REMOTE_TRANSLATION=local` are ever
set together with a misconfigured or attacker-influenced `LIGHTML_TRANSLATOR_URL` (e.g. via a
compromised deploy pipeline or a leaked `.env`, see F-01), full contract text for every non-English
document leaves this process to that URL, and `LDV_LIGHTML_API_KEY` (if set) leaks alongside it.

**Remediation:** No code change strictly required given the existing safeguards, but recommend
(a) an explicit allowlist of acceptable hostnames/CIDRs for `LIGHTML_TRANSLATOR_URL` checked at
process startup (fail closed if it doesn't match), rather than trusting the URL unconditionally
once HTTPS is satisfied, and (b) keeping `EXTERNAL_TRANSLATION_DISABLED=1` in every environment
until that allowlist exists. Document this explicitly as a Gate 3 condition if `LDV_REMOTE_TRANSLATION=local`
is ever turned on for the pilot.

**Status:** OPEN (config/process control, not purely code).

### F-09 — No account lockout / backoff beyond per-IP rate limiting on login and MFA verification
**File:** `app.py:423-483` (`login`), `552-595` (`api_mfa_enable`).

**Description:** `/login` is rate-limited at 10/min per IP (good), and MFA code verification
(`api_mfa_enable`, and the MFA branch inside `login`) has no dedicated stricter limit of its own —
it falls back to the global default (`60 per minute` per IP). Both are per-IP only; there is no
per-account lockout/backoff after N consecutive failures from *different* IPs (e.g. a small botnet
or rotating-proxy attacker distributing a password-spray or TOTP-guessing attack across many
source IPs would not be slowed by this at all, since each IP gets its own 10/min or 60/min
allowance). TOTP's 6-digit space (1,000,000 combinations, 30s windows, `valid_window=1` giving 3
valid codes at once) is reasonably resistant to brute force at *any single* rate-limited
IP, but a distributed attacker is not meaningfully rate-limited.

**Remediation:** Add a per-account (not just per-IP) failed-attempt counter with exponential
backoff or temporary lock, logged via the existing `write_audit("login.fail", ...)` /
`mfa` audit events (the audit trail already exists — just needs to feed a decision, not only a log
line).

**Status:** OPEN.

---

## LOW

### F-10 — Audit-log IP field is trivially spoofable
**File:** `app.py:131-132` (`_ip()`).

**Description:** `_ip()` returns `request.headers.get("X-Forwarded-For", request.remote_addr or "")`
unconditionally — i.e. it trusts a client-supplied header over the socket-level address whenever
present, with no check that the request actually came through a trusted reverse proxy. Every
`database.write_audit(..., ip=_ip())` call (login success/fail, upload, delete, download, admin
actions, MFA events) can therefore have its recorded IP forged by any direct caller simply by
sending an `X-Forwarded-For` header. This doesn't enable any access-control bypass (rate limiting
correctly uses `flask_limiter`'s `get_remote_address`, which reads the actual socket address, not
this header) — the impact is purely audit-log integrity, which still matters for SEC-06 if this
log is ever used for incident investigation or compliance evidence.

**Remediation:** Only trust `X-Forwarded-For`/`X-Real-IP` when the request is known to come from a
trusted reverse proxy (e.g. wrap the app with Werkzeug's `ProxyFix` configured with a fixed proxy
count, or explicitly check `request.remote_addr` is the known proxy's IP before trusting the
header). This matters more once the app sits behind gunicorn + a real reverse proxy in production —
right now, with `LDV_RATELIMIT_STORAGE_URL` defaulting to `memory://` and gunicorn run with `-w 4`
(4 worker processes, not sharing in-memory rate-limit state — see F-13), the deployment already
has multi-process consistency gaps worth addressing together.

**Status:** OPEN.

### F-11 — Hardcoded test-runner rate-limit bypass identity
**File:** `app.py:90-100` (`bypass_rate_limits`).

**Description:** Rate limiting is bypassed (in addition to the existing pytest/`LDV_TESTING` env
gates, and separately from the admin-bearer-token bypass) for any account whose email is exactly
`test-runner@ldv.internal`. This account is only ever created by the test scripts under
`tests/` (confirmed via repo-wide grep — nothing in `manage.py`/`database.init_db` seeds it), so
today it's low risk. But it's a magic string embedded directly in production code path logic
rather than gated by an env flag, so if that account is ever created against a real/production
database (e.g. a test suite accidentally pointed at `LDV_DB_PATH` for prod, or someone manually
provisions a user with that exact email for convenience), it becomes an unlimited-rate-limit
account indefinitely, with no audit trail marking it as "test-only".

**Remediation:** Gate this bypass behind an explicit env flag (e.g. `LDV_TEST_RUNNER_BYPASS=1`,
defaulting off) in addition to the email check, or drop the hardcoded email check entirely and
have the test suite provision its bypass via `LDV_TESTING=1` (which is already checked at the top
of the same function and is the correct mechanism).

**Status:** OPEN.

### F-12 — Content-Disposition filename not sanitized
**File:** `app.py:910-947` (`download_file`), uses `info["original_filename"]` (user-supplied at
upload time) directly in `Content-Disposition: attachment; filename="..."`.

**Description:** The original uploaded filename (fully attacker/user-controlled string) is
interpolated into the `Content-Disposition` header with only surrounding double-quotes, no
escaping of embedded `"` or control characters. Werkzeug/Flask's `Response` will reject header
values containing raw CR/LF (raises `ValueError`), so classic header-injection/response-splitting
is not exploitable here — but a filename containing a literal `"` can break out of the quoted
filename parameter in some older/less-strict HTTP clients, and there's no `filename*=UTF-8''...`
fallback for non-ASCII names, which is a correctness rather than security issue.

**Remediation:** Use `werkzeug.utils.secure_filename` or an explicit quote-escape (`filename.replace('"', '')`)
when building the header, or let Flask build it via `send_file(..., download_name=...)` which
already handles this correctly (used elsewhere in the codebase's `send_from_directory` calls for
static assets, just not here since this is a raw `Response`, not a real file on the served
directory).

**Status:** OPEN.

### F-13 — In-memory rate-limit storage is not shared across gunicorn workers
**File:** `app.py:81-87` (`limiter = Limiter(..., storage_uri=os.getenv("LDV_RATELIMIT_STORAGE_URL", "memory://"))`),
`Dockerfile:27` (`gunicorn -w 4 ...`).

**Description:** The default rate-limit storage is in-process memory. The Dockerfile runs
gunicorn with 4 worker processes, each an independent Python process with its own memory —
so the real effective rate limit in the shipped container is **4× the documented value** per
limit (e.g. "10 per minute" on `/login` is actually ~40/min across the 4 workers, since each
worker tracks its own counter). This is already flagged in the code comment ("Redis storage if
configured (required for multi-worker); defaults to memory") — i.e. the developer is aware — but
`LDV_RATELIMIT_STORAGE_URL` is not set in the Dockerfile/compose file, so the shipped default
silently under-delivers on the documented rate limits.

**Remediation:** Set `LDV_RATELIMIT_STORAGE_URL` to a real Redis instance in
`docker-compose.yml` (a `redis` package is already pinned in `requirements.txt`, so this is a
config change, not a code change) before relying on the documented per-minute limits in
production with `-w 4`.

**Status:** OPEN.

### F-14 — `.env.example` does not exist
**Description:** Per this audit's own checklist: no `.env` file should be committed (see F-01),
and a `.env.example` with placeholders should exist so operators know which variables to set.
Neither is currently true — the *real* `.env` is committed instead of an example one. Given the
extensive environment-variable table already documented in `CLAUDE.md`, an `.env.example` is easy
to generate from that table and should replace the committed `.env`.

**Remediation:** After completing F-01's remediation (secret rotation + history scrub), add a
`ldv-backend/.env.example` (or repo-root, matching wherever `.env` was expected to be loaded from)
listing every variable from the CLAUDE.md table with placeholder values (`YOUR_SECRET_KEY_HERE`,
`0`, etc.) and commit *that* instead. Confirm `.env` is added to `.gitignore` (currently absent).

**Status:** OPEN.

---

## INFO

### F-15 — CSRF Origin check correctly implemented, minor proxy-trust caveat
**File:** `app.py:107-126`. The `before_request` CSRF check (Origin/Referer host must match
`request.host`) is a reasonable, correctly-implemented defense-in-depth measure on top of
`SameSite=Lax`/`SameSite=None`+`Secure` cookies, and correctly exempts Bearer-token auth (which is
inherently CSRF-immune) and safe methods. Note that `request.host` reflects the `Host` header,
which — like the `X-Forwarded-For` issue in F-10 — is only trustworthy if the app sits behind a
correctly configured reverse proxy that doesn't forward an attacker-controlled `Host` header
unchanged. Worth confirming as part of the actual deployment's reverse-proxy config, not a code
fix.

### F-16 — Encryption-at-rest (`crypto.py`) implementation is sound
`Fernet`/`MultiFernet` usage is correct: authenticated encryption (Fernet is AES-128-CBC +
HMAC-SHA256, includes its own random IV and timestamp), key rotation via `MultiFernet` (first key
encrypts, all keys can decrypt) matches the documented rotation story, and the plaintext-vs-ciphertext
detection heuristic (`gAAAAA` magic prefix) is a reasonable zero-migration approach — a
token-shaped-but-corrupt value correctly raises `InvalidToken` rather than silently passing
through as plaintext. No issues found here beyond the key-provenance problem in F-01/F-03 (the
implementation is fine; the *key* is compromised).

### F-17 — Upload MIME/type validation is reasonable
`_validate_and_extract` (magic-byte sniffing + extension allowlist + the documented
`python-magic`-returns-`octet-stream`-for-DOCX workaround, gated specifically to `data[:2] ==
b"PK"`) is a sound, narrowly-scoped mitigation for the known libmagic quirk, not a blanket bypass.
Combined with the 10 MB cap and UUID-based server-side filenames (original filename is never used
to construct a filesystem path), there is no path-traversal risk in the upload path itself. See
F-05 for the separate decompression-bomb/DoS concern on the *content* of accepted files.

### F-18 — Debug mode is correctly gated
`app.run(debug=os.getenv("LDV_DEBUG", "0") == "1")` at the bottom of `app.py` defaults to off, and
production is expected to run under gunicorn (`Dockerfile` CMD) rather than the Flask dev server
at all, which is the correct posture — the Werkzeug interactive debugger (RCE risk if ever
internet-facing) is not reachable through the documented deployment path. No generic Flask error
page/stack-trace leakage was found in the reviewed error handlers.

---

## Recommendation for Gate 3 status

1. **Do not mark Gate 3 Passed.** F-01 alone is a hard blocker — it's not a hypothetical, it's a
   currently-live exposure of the actual signing/encryption keys in git history on a remote the
   team pushes to, for a project with a real HF Spaces pilot deployment.
2. Suggested Gate 3 update once F-01 is remediated (rotation + history scrub confirmed) and F-02
   (global-admin model) is at minimum explicitly documented/risk-accepted: move to
   **🟡 PARTIAL — critical secret exposure remediated, code-level audit complete, dependency CVE
   scan and formal external pentest still outstanding** rather than back to fully 🟡 PARTIAL as
   today, since "no independent security audit... performed" is no longer true after this pass —
   but F-07 (CVE scan) and any external/third-party validation are still open items before a full
   ✅ Passed.
3. Recommend re-running this audit (or at minimum re-verifying F-01 through F-06) after
   remediation, before Gate 3 is closed.
