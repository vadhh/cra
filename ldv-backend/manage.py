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
    args = parser.parse_args()

    if args.cmd == "seed-admin":
        seed_admin()
    elif args.cmd == "create-org":
        create_org_cmd(args.name)
    elif args.cmd == "create-user":
        create_user_cmd(args.email, args.org, args.role)


if __name__ == "__main__":
    main()
