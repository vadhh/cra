#!/usr/bin/env python3
"""Provisioning CLI for CR-01 auth.

  python manage.py seed-admin                          # uses LDV_ADMIN_EMAIL/PASSWORD
  python manage.py create-org "Acme"
  python manage.py create-user user@acme.com "Acme" --role user
"""
from __future__ import annotations

import argparse
import os
import secrets
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
    pu.add_argument("--role", default="user", choices=["user", "admin"])
    pp = sub.add_parser("purge")
    pp.add_argument("--dry-run", action="store_true")
    pd = sub.add_parser("purge-doc")
    pd.add_argument("public_id")
    sub.add_parser("gen-key")
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


if __name__ == "__main__":
    main()
