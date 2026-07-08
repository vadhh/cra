#!/usr/bin/env python3
"""Provisioning CLI for CR-01 auth.

  python manage.py seed-admin                          # uses LDV_ADMIN_EMAIL/PASSWORD
  python manage.py create-org "Acme"
  python manage.py create-user user@acme.com "Acme" --role user
"""
from __future__ import annotations

import argparse
import datetime
import os
import secrets
import shutil
import subprocess
import sys

from cryptography.fernet import Fernet

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


def purge_cmd(dry_run: bool) -> None:
    victims = database.purge_expired(dry_run=dry_run)
    for v in victims:
        if not dry_run and v.get("file_path"):
            try:
                os.remove(v["file_path"])
            except FileNotFoundError:
                pass
        tag = "would purge" if dry_run else "PURGE"
        print(f"{tag}: doc_id={v['document_id']} file={v['file_path']} expired={v['expires_at']}")
    verb = "eligible" if dry_run else "purged"
    print(f"{'(dry-run) ' if dry_run else ''}{len(victims)} document(s) {verb}.")


def purge_doc_cmd(public_id: str) -> None:
    info = database.delete_analysis(public_id)
    if info is None:
        sys.exit(f"No analysis with id {public_id}.")
    if info.get("file_path"):
        try:
            os.remove(info["file_path"])
        except FileNotFoundError:
            pass
    print(f"Purged analysis {public_id} (doc_id={info['document_id']}).")


def gen_key_cmd() -> None:
    print(Fernet.generate_key().decode())


def backup_cmd(dry_run: bool) -> None:
    backup_dir = os.getenv("LDV_BACKUP_DIR", "/var/backups/ldv")
    remote = os.getenv("LDV_BACKUP_REMOTE", "")
    keep_days = int(os.getenv("LDV_BACKUP_KEEP_DAYS", "30"))

    stamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = os.path.join(backup_dir, stamp)
    db_src = database.get_db_path()
    uploads_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "uploads")

    if dry_run:
        print(f"[dry-run] would create {dest}/")
        print(f"[dry-run] would copy {db_src} → {dest}/sydeco.db")
        print(f"[dry-run] would copy {uploads_src}/ → {dest}/uploads/")
        if remote:
            print(f"[dry-run] would rsync {dest}/ → {remote}")
        return

    os.makedirs(dest, exist_ok=True)
    shutil.copy2(db_src, os.path.join(dest, "sydeco.db"))
    if os.path.isdir(uploads_src):
        shutil.copytree(uploads_src, os.path.join(dest, "uploads"))
    print(f"Backup created: {dest}")

    if remote:
        cmd = ["rsync", "-az", "--delete", dest + "/", remote]
        result = subprocess.run(cmd)
        if result.returncode != 0:
            sys.exit(f"rsync to {remote} failed (exit {result.returncode})")
        print(f"Synced to {remote}")

    # prune old backups
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=keep_days)
    pruned = 0
    for entry in os.scandir(backup_dir):
        if not entry.is_dir():
            continue
        try:
            ts = datetime.datetime.strptime(entry.name, "%Y%m%dT%H%M%SZ")
        except ValueError:
            continue
        if ts < cutoff:
            shutil.rmtree(entry.path)
            pruned += 1
    if pruned:
        print(f"Pruned {pruned} backup(s) older than {keep_days} days.")


def set_retention_cmd(org_name: str, days: int) -> None:
    org = database.get_org_by_name(org_name)
    if org is None:
        sys.exit(f"No org named '{org_name}'.")
    database.set_org_retention(org["id"], days)
    print(f"Retention for '{org_name}' set to {days} days.")


def ensure_pilot_admin_cmd() -> None:
    """Idempotently (re)create the pilot-admin account and exempt it from MFA.
    Intended to run on every container boot — this Space has no persistent
    storage, so the DB (and this account) is wiped on every restart."""
    email = os.getenv("LDV_PILOT_ADMIN_EMAIL", "pilot-admin@ldv.local").strip().lower()
    password = os.getenv("LDV_PILOT_ADMIN_PASSWORD")
    if not password:
        print("LDV_PILOT_ADMIN_PASSWORD not set; skipping pilot-admin provisioning.")
        return
    org = database.get_org_by_name("Sydeco")
    org_id = org["id"] if org else database.create_org("Sydeco")
    user = database.get_user_by_email(email)
    if user is None:
        database.create_user(org_id, email, auth.hash_password(password), "admin", _gen_token())
        user = database.get_user_by_email(email)
        print(f"Created pilot-admin {email}.")
    else:
        print(f"pilot-admin {email} already exists.")
    database.update_user_mfa_exempt(user["id"], 1)
    print(f"MFA exemption ensured for {email}.")


def set_mfa_exempt_cmd(email: str, exempt: bool) -> None:
    user = database.get_user_by_email(email)
    if user is None:
        sys.exit(f"No user with email '{email}'.")
    database.update_user_mfa_exempt(user["id"], int(exempt))
    database.write_audit("user.mfa_exempt_change", user_id=user["id"], org_id=user["org_id"], resource_id=str(user["id"]), detail=str(exempt))
    print(f"MFA exemption for {email} set to {exempt}.")


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
    pu.add_argument("--role", default="user", choices=["user", "admin", "analyst", "reviewer", "manager"])
    pp = sub.add_parser("purge")
    pp.add_argument("--dry-run", action="store_true")
    pd = sub.add_parser("purge-doc")
    pd.add_argument("public_id")
    sub.add_parser("gen-key")
    pr = sub.add_parser("set-retention")
    pr.add_argument("org")
    pr.add_argument("days", type=int)
    pm = sub.add_parser("set-mfa-exempt", help="Exempt (or un-exempt) one user from mandatory MFA")
    pm.add_argument("email")
    pm.add_argument("--off", action="store_true", help="Remove the exemption instead of granting it")
    sub.add_parser("ensure-pilot-admin", help="Idempotently (re)create the pilot-admin account + MFA exemption on boot")
    pb = sub.add_parser("backup", help="Back up DB + uploads to LDV_BACKUP_DIR")
    pb.add_argument("--dry-run", action="store_true")
    pdm = sub.add_parser("download-model", help="Download a model repository from Hugging Face Hub")
    pdm.add_argument("repo_id")
    pdm.add_argument("--token", help="Optional Hugging Face access token")
    args = parser.parse_args()

    if args.cmd == "seed-admin":
        seed_admin()
    elif args.cmd == "create-org":
        create_org_cmd(args.name)
    elif args.cmd == "create-user":
        create_user_cmd(args.email, args.org, args.role)
    elif args.cmd == "purge":
        purge_cmd(args.dry_run)
    elif args.cmd == "purge-doc":
        purge_doc_cmd(args.public_id)
    elif args.cmd == "gen-key":
        gen_key_cmd()
    elif args.cmd == "set-retention":
        set_retention_cmd(args.org, args.days)
    elif args.cmd == "set-mfa-exempt":
        set_mfa_exempt_cmd(args.email, not args.off)
    elif args.cmd == "ensure-pilot-admin":
        ensure_pilot_admin_cmd()
    elif args.cmd == "backup":
        backup_cmd(args.dry_run)
    elif args.cmd == "download-model":
        from hf_hub_connector import download_repo_model
        download_repo_model(args.repo_id, token=args.token)


if __name__ == "__main__":
    main()
