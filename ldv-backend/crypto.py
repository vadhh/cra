"""crypto.py — symmetric encryption-at-rest for documents/results (SEC-02).

Keyed from LDV_ENCRYPTION_KEY: a comma-separated list of urlsafe-base64 Fernet
keys. The first key is primary (used for all new encryption); the rest are
decrypt-only, which is the whole key-rotation story. Unset = passthrough
plaintext + one warning, so localhost dev needs no key.
"""
from __future__ import annotations

import logging
import os

from cryptography.fernet import Fernet, MultiFernet

logger = logging.getLogger(__name__)

# Fernet tokens are urlsafe-base64 of a payload starting with version byte 0x80,
# which always renders as this prefix. ponytail: prefix heuristic distinguishes
# our ciphertext from legacy plaintext (%PDF, PK, raw text) for zero-migration
# rollout; a token-shaped-but-corrupt value still raises InvalidToken on decrypt
# rather than being silently passed through.
_MAGIC_B = b"gAAAAA"
_MAGIC_S = "gAAAAA"

_fernet: MultiFernet | None = None
_loaded = False


def _get() -> MultiFernet | None:
    global _fernet, _loaded
    if not _loaded:
        raw = os.getenv("LDV_ENCRYPTION_KEY", "").strip()
        keys = [k.strip() for k in raw.split(",") if k.strip()]
        if keys:
            _fernet = MultiFernet([Fernet(k.encode()) for k in keys])
        else:
            _fernet = None
            logger.warning(
                "LDV_ENCRYPTION_KEY unset — documents/results stored in "
                "PLAINTEXT. Set it before any real deployment."
            )
        _loaded = True
    return _fernet


def is_enabled() -> bool:
    return _get() is not None


def enc_str(s: str) -> str:
    f = _get()
    return f.encrypt(s.encode()).decode() if f else s


def dec_str(s: str) -> str:
    f = _get()
    if f is None:
        return s
    if s.startswith(_MAGIC_S):
        return f.decrypt(s.encode()).decode()
    return s


def enc_bytes(b: bytes) -> bytes:
    f = _get()
    return f.encrypt(b) if f else b


def dec_bytes(b: bytes) -> bytes:
    f = _get()
    if f is None:
        return b
    if b.startswith(_MAGIC_B):
        return f.decrypt(b)
    return b
