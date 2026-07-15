#!/bin/sh
# Runs on every container boot. This Space has no persistent storage, so the
# DB is wiped on every restart — re-provision the pilot-admin account here
# instead of doing it by hand after each sleep/wake cycle.
python3 manage.py ensure-pilot-admin
exec gunicorn -w 4 -b 0.0.0.0:7860 app:app
