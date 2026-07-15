"""OS-level network isolation check — independent of the Python socket trap
in offline_net_trap.py.

offline_net_trap.py proves this codebase makes no outbound calls *through
Python's socket module*, but a monkeypatch can't rule out a subprocess, a
native library, or anything else bypassing patched Python functions. This
script makes zero attempt to intercept anything — it just tries a real
outbound connection and reports whether the OS allowed it. Run it inside
`docker run --network=none` (or an equivalent network namespace) to get
kernel-level proof that is independent of this process's own code.

Run: python3 tests/os_level_network_check.py
Exit 0 if all targets were blocked (network genuinely isolated), 1 otherwise.
"""
import socket
import sys

TARGETS = [
    ("8.8.8.8", 53),
    ("1.1.1.1", 443),
    ("huggingface.co", 443),
]


def check_no_network() -> bool:
    all_blocked = True
    for host, port in TARGETS:
        try:
            s = socket.create_connection((host, port), timeout=3)
            s.close()
            print(f"FAIL: reached {host}:{port} -- network is NOT isolated")
            all_blocked = False
        except OSError as e:
            print(f"OK: connection to {host}:{port} blocked ({e})")
    return all_blocked


if __name__ == "__main__":
    ok = check_no_network()
    print("RESULT: network isolated" if ok else "RESULT: network reachable")
    sys.exit(0 if ok else 1)
