# P0 #3 — Retention / Purge / Encryption-at-rest

**Date:** 2026-06-23
**Maps to:** PRD §14 SEC-02 (encrypt at rest + key rotation), SEC-05 (configurable retention + secure purge), partial SEC-09. CLAUDE.md P0 #3 / CR-04.
**Status:** approved design, pre-implementation.

## Problem

Uploaded contracts, extracted text, and analysis results currently persist
indefinitely in plaintext:

- file bytes → `uploads/<uuid>.<ext>` on disk, plaintext
- `documents.extracted_text` → SQLite, plaintext
- `analyses.result_json` → SQLite, plaintext
- no expiry, no purge, no encryption

Confidential client contracts must not sit unencrypted and undeletable. This
spec adds encryption-at-rest, a configurable retention window, and a purge
path (scheduled + on-request).

## Decisions (from brainstorming)

1. **Key unset → plaintext + loud warning + degraded flag.** Dev stays
   frictionless; production must set the key. Surfaced via `/health`.
2. **Retention configured by global env** `LDV_RETENTION_DAYS` (default 30).
   Per-org override column deferred until packages/billing land.
3. **On-request deletion exposed as an authenticated DELETE endpoint** now,
   alongside the scheduled and CLI purge paths.

## Architecture

### 1. `crypto.py` (new, ~40 lines)

Single responsibility: symmetric encrypt/decrypt of strings and bytes, keyed
from the environment. No other module knows about Fernet.

- Lazy `MultiFernet` singleton built from `LDV_ENCRYPTION_KEY`, a
  comma-separated list of urlsafe-base64 Fernet keys. **First key = primary**
  (used for all new `encrypt`); remaining keys are decrypt-only. This is the
  whole key-rotation story for free — add a new primary, keep the old key
  until everything is re-encrypted, then drop it.
- API:
  - `is_enabled() -> bool` — true iff at least one key is configured.
  - `enc_str(s: str) -> str` / `dec_str(s: str) -> str`
  - `enc_bytes(b: bytes) -> bytes` / `dec_bytes(b: bytes) -> bytes`
- **Key unset:** all `enc_*`/`dec_*` are passthrough (return input unchanged).
- **Tolerant decrypt for zero-migration rollout:** Fernet tokens self-identify
  with a `gAAAAA` magic prefix (version byte `0x80`). When a key is set:
  - input matches the token magic → `Fernet.decrypt`; on `InvalidToken`, raise
    (genuine corruption / wrong key — never silently pass bad data through).
  - input does not match the magic → it is legacy plaintext written before the
    key existed (`%PDF`, `PK\x03\x04`, raw extracted text, raw JSON) → return
    as-is.
  - `ponytail:` comment names this heuristic and its ceiling.
- `manage.py gen-key` prints a fresh `Fernet.generate_key()` for operators.

### 2. Encryption boundary — `database.py`

Encryption lives at the persistence boundary so every storage path is covered
and `app.py`'s text handling is untouched.

- `save_document(...)`: `enc_str(extracted_text)` before INSERT.
- `save_analysis(...)`: `enc_str(json.dumps(result))` before INSERT.
- `get_result(...)`: `dec_str` on `extracted_text` and `result_json` after
  SELECT (the latter parsed back via `json.loads`).
- `get_recent(...)`: returns no sensitive text — no change needed.

On-disk file bytes are encrypted in `app.py` at the single write site
(`open(file_path,"wb")`) via `crypto.enc_bytes`, and would be decrypted by
`crypto.dec_bytes` at any future read site (none today beyond purge, which only
unlinks). The stored file is the Fernet token bytes.

### 3. Retention — `documents.expires_at`

- New nullable `expires_at TIMESTAMP` column on `documents`.
- `init_db()` migration: add the column if missing; backfill existing rows to
  `uploaded_at + LDV_RETENTION_DAYS`.
- `save_document(...)` sets `expires_at = utcnow() + timedelta(days=N)` where
  `N = int(LDV_RETENTION_DAYS or 30)`.
- Analyses inherit expiry through their parent document (no separate column).

### 4. Purge — `manage.py`

- `purge [--dry-run]`: select `documents` where `expires_at < now`; for each,
  unlink `file_path`, delete dependent `analyses` rows, delete the `documents`
  row. `VACUUM` afterward to reclaim pages.
  - **Secure-erase ceiling:** on SSD, overwrite-in-place is unreliable theater;
    we rely on row+file deletion + `VACUUM`. `ponytail:` comment names this and
    points at full-disk/volume encryption as the real defense.
  - Each deletion logged as `PURGE: doc_id=.. file=.. analyses=N expired=..` —
    this log is the deletion audit trail until the structured SEC-06 audit
    table lands.
  - `--dry-run` reports what would be deleted without touching anything (also
    the self-check hook).
- `purge-doc <analysis_public_id>`: immediate deletion of one analysis and its
  document + file. Operator-side counterpart to the DELETE endpoint.
- `gen-key`: print a new Fernet key.

`database.py` gains the data-layer helpers these call:
`purge_expired(dry_run=False) -> list[dict]` and
`delete_analysis(public_id) -> dict | None` (returns the unlinked file_path +
counts, or None if not found). The file unlink happens in the caller
(`manage.py` / route) so the DB module stays filesystem-light.

### 5. Delete endpoint — `app.py`

`DELETE /api/result/<analysis_id>`:
- `@auth.login_required`, same ownership rule as the GET (`api_result`): admin
  or matching `org_id`, else 403; 404 if unknown.
- Looks up the row, deletes analysis + document via `database.delete_analysis`,
  unlinks the file, returns `{"deleted": true, "id": <analysis_id>}`.
- Reuses the existing `/api/result/<id>` path; `/api/v1` versioning remains the
  separate P3 task and is **not** introduced here.

### 6. Degraded mode — `/health`

Add to the existing `/health` payload:
```json
"encryption": {"enabled": true},
"retention_days": 30
```
When `encryption.enabled` is false the app has logged a startup warning. Full
report-metadata surfacing (CR-09) is noted as a follow-up, not in this change.

### 7. `requirements.txt`

Pin `cryptography==48.0.0` (currently only transitively present; now a direct
dependency).

## Data flow

```
upload → validate/extract → enc_bytes(file) → uploads/<uuid>   (token bytes)
                          → save_document(enc_str(text), expires_at)
                          → run analysis → save_analysis(enc_str(result_json))

GET /api/result/<id> → get_result → dec_str(text), json.loads(dec_str(json))
DELETE /api/result/<id> → ownership check → delete_analysis + unlink file

cron → manage.py purge → delete docs where expires_at < now → VACUUM → log
```

## Error handling

- Missing/blank `LDV_ENCRYPTION_KEY`: passthrough plaintext + one startup
  WARNING + `encryption.enabled=false` in `/health`. Not fatal.
- Malformed key value: `Fernet`/`MultiFernet` raises at first use; let it
  surface loudly (operator misconfiguration, must not run thinking it's
  encrypting when it isn't).
- `InvalidToken` on a token-shaped input: raise (corruption / wrong key).
- Invalid `LDV_RETENTION_DAYS`: fall back to 30 with a warning (matches the
  existing safe-parse pattern used for the cookie limit).
- Purge unlink of an already-missing file: ignore (`missing_ok=True`), still
  delete the DB row.

## Testing / self-checks

- `crypto.py __main__`: assert round-trip (`dec_str(enc_str(x)) == x`),
  plaintext fallback (`dec_str(legacy_plaintext) == legacy_plaintext`), bytes
  round-trip, and rotation (encrypt under key A, add key B as primary, old
  token still decrypts).
- A small purge test against a temp `LDV_DB_PATH`: insert an expired + a live
  document, run `purge_expired(dry_run=True)` (reports the expired one, deletes
  nothing) then real purge (expired gone, live retained).

## Out of scope

- **SEC-09 backups** — no backup system exists; nothing to encrypt yet. Noted.
- **SEC-06 structured audit table** — separate P0 #1 follow-up; purge logging
  serves as the interim deletion audit.
- **Per-org retention policy** — global env default now; per-org column later.
- **Report-metadata degraded surfacing (CR-09)** — `/health` only for now.

## Files touched

- `ldv-backend/crypto.py` (new)
- `ldv-backend/database.py`
- `ldv-backend/app.py`
- `ldv-backend/manage.py`
- `ldv-backend/requirements.txt`
- `CLAUDE.md` (env var table + TODO P0 #3 status)
