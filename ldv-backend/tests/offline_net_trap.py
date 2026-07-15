"""Socket-level egress trap — proves an offline validation run makes zero
outbound network calls.

ponytail: blocks the interpreter's socket layer, not raw syscalls —
sufficient to prove this codebase makes no outbound calls under test, not a
full network-namespace sandbox. Upgrade to iptables/netns only if a future
audit needs kernel-level proof.
"""
import socket

_orig_connect = socket.socket.connect


def _blocked_connect(self, address):
    host = address[0] if isinstance(address, tuple) else address
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise RuntimeError(f"BLOCKED offline-mode outbound connect to {address!r}")
    return _orig_connect(self, address)


def enable_network_trap() -> None:
    socket.socket.connect = _blocked_connect


def disable_network_trap() -> None:
    socket.socket.connect = _orig_connect


def self_check() -> bool:
    """Enable the trap and prove a real outbound connect attempt is blocked."""
    enable_network_trap()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect(("8.8.8.8", 53))
    except RuntimeError as e:
        return "BLOCKED" in str(e)
    else:
        return False
    finally:
        s.close()
