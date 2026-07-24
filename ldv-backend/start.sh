#!/bin/sh
# Runs on every container boot. This Space has no persistent storage, so the
# DB is wiped on every restart — re-provision the pilot-admin account here
# instead of doing it by hand after each sleep/wake cycle.
python3 manage.py ensure-pilot-admin
# F-13: -w 1 --threads instead of -w 4 keeps the in-memory rate-limit store
# (LDV_RATELIMIT_STORAGE_URL defaults to memory://, no Redis available on this
# single-container Space) correct — 4 separate worker processes each track
# their own counters, silently quadrupling the documented per-minute limits.
exec gunicorn -w 1 --threads 4 --worker-class gthread -b 0.0.0.0:7860 app:app
