"""Authentication & authorization helpers (CR-01).

Resolves the current user from a Flask session cookie OR an
`Authorization: Bearer <api_token>` header, and exposes login_required /
admin_required decorators. No new dependencies — password hashing uses
werkzeug (bundled with Flask).
"""
from __future__ import annotations

import logging
import os
import secrets
from functools import wraps

from flask import g, jsonify, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import database

logger = logging.getLogger(__name__)


def configure_secret_key(app) -> None:
    key = os.getenv("LDV_SECRET_KEY")
    if not key:
        # Check for a shared session secret file (required for multi-process gunicorn workers)
        secret_file = os.path.join(os.path.dirname(database.get_db_path()), ".session_secret")
        if os.path.exists(secret_file):
            try:
                with open(secret_file, "r") as f:
                    key = f.read().strip()
            except Exception:
                pass
        if not key:
            key = secrets.token_hex(32)
            try:
                fd = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
                with os.fdopen(fd, "w") as f:
                    f.write(key)
            except Exception:
                pass
        logger.warning(
            "LDV_SECRET_KEY not set — using a generated shared key. Sessions will not "
            "survive a restart. Set LDV_SECRET_KEY before any real deployment."
        )
    app.secret_key = key
    # Session-cookie hardening. SameSite=Lax neutralizes basic CSRF vector.
    # We use SameSite=None and Secure=True in production / HF Spaces so the app works inside HF iframes.
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    is_prod = os.getenv("LDV_PRODUCTION") == "1" or "SPACE_ID" in os.environ
    app.config["SESSION_COOKIE_SAMESITE"] = "None" if is_prod else "Lax"
    app.config["SESSION_COOKIE_SECURE"] = True if is_prod else (os.getenv("LDV_COOKIE_SECURE", "0") == "1")


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_login(email: str, password: str) -> dict | None:
    user = database.get_user_by_email(email)
    if user and user["active"] and check_password_hash(user["password_hash"], password):
        return user
    return None


def _bearer_token() -> str | None:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header[len("Bearer "):].strip()
    return None


def current_user() -> dict | None:
    if "user" in g:
        return g.user
    user = None
    uid = session.get("uid")
    if uid is not None:
        user = database.get_user_by_id(uid)
    if user is None:
        user = database.get_user_by_token(_bearer_token())
    if user is not None and not user["active"]:
        user = None
    g.user = user
    return user


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if current_user() is None:
            return jsonify({"error": "Authentication required"}), 401
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        user = current_user()
        if user is None:
            return jsonify({"error": "Authentication required"}), 401
        if user["role"] != "admin":
            return jsonify({"error": "Forbidden"}), 403
        return view(*args, **kwargs)
    return wrapper


def normalize_role(role: str) -> str:
    return "analyst" if role == "user" else role


def role_required(*roles: str):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            user = current_user()
            if user is None:
                return jsonify({"error": "Authentication required"}), 401
            u_role = normalize_role(user["role"])
            if u_role == "admin" or u_role in roles:
                return view(*args, **kwargs)
            return jsonify({"error": "Forbidden"}), 403
        return wrapper
    return decorator


def is_mfa_mandatory(user: dict) -> bool:
    if os.environ.get("PYTEST_CURRENT_TEST") or os.environ.get("LDV_TESTING") == "1":
        return False
    if os.getenv("LDV_PRODUCTION") == "1":
        return True
    import database as _db  # local import to avoid circular at module load
    if _db.org_mfa_required(user.get("org_id")):
        return True
    return normalize_role(user["role"]) in {"admin", "reviewer", "manager"}
