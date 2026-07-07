import socket
from offline_net_trap import enable_network_trap, disable_network_trap, self_check


def test_non_loopback_connect_is_blocked():
    enable_network_trap()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(("8.8.8.8", 53))
            assert False, "expected RuntimeError for non-loopback connect"
        except RuntimeError as e:
            assert "BLOCKED" in str(e)
        finally:
            s.close()
    finally:
        disable_network_trap()


def test_loopback_connect_passes_through():
    enable_network_trap()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        try:
            s.connect(("127.0.0.1", 1))  # nothing listens on port 1 — refused, not blocked
        except RuntimeError:
            assert False, "loopback connect was wrongly blocked"
        except OSError:
            pass  # connection refused/unreachable is expected — it passed through the trap
        finally:
            s.close()
    finally:
        disable_network_trap()


def test_disable_restores_original_connect():
    original = socket.socket.connect
    enable_network_trap()
    disable_network_trap()
    assert socket.socket.connect is original


def test_self_check_reports_true_when_trap_works():
    result = self_check()
    disable_network_trap()
    assert result is True
