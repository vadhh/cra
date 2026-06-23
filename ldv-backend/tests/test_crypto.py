"""Self-check for crypto.py: round-trip, plaintext fallback, key rotation."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cryptography.fernet import Fernet
import crypto

KEY_A = Fernet.generate_key().decode()
KEY_B = Fernet.generate_key().decode()

# --- plaintext mode (no key) ---
os.environ.pop("LDV_ENCRYPTION_KEY", None)
crypto._loaded = False
assert crypto.is_enabled() is False
assert crypto.enc_str("hello") == "hello"
assert crypto.dec_str("hello") == "hello"
assert crypto.enc_bytes(b"hi") == b"hi"

# --- encrypted round-trip ---
os.environ["LDV_ENCRYPTION_KEY"] = KEY_A
crypto._loaded = False
assert crypto.is_enabled() is True
tok = crypto.enc_str("secret")
assert tok != "secret" and tok.startswith("gAAAAA")
assert crypto.dec_str(tok) == "secret"
assert crypto.dec_bytes(crypto.enc_bytes(b"%PDF-1.7")) == b"%PDF-1.7"

# --- legacy plaintext passes through even with a key set ---
assert crypto.dec_str("not a token") == "not a token"
assert crypto.dec_bytes(b"%PDF-1.7") == b"%PDF-1.7"

# --- rotation: token made under A still decrypts under [B, A] ---
os.environ["LDV_ENCRYPTION_KEY"] = f"{KEY_B},{KEY_A}"
crypto._loaded = False
assert crypto.dec_str(tok) == "secret"
new_tok = crypto.enc_str("again")          # encrypted under primary B
os.environ["LDV_ENCRYPTION_KEY"] = KEY_B   # drop A
crypto._loaded = False
assert crypto.dec_str(new_tok) == "again"

print("test_crypto OK")
