"""Tests for ShutdownHandler."""
from __future__ import annotations

from agicore.core.shutdown import ShutdownHandler


def test_initial_state_not_stopping() -> None:
    s = ShutdownHandler()
    assert not s.is_stopping()


def test_trigger_sets_stop_event() -> None:
    s = ShutdownHandler()
    s.trigger()
    assert s.is_stopping()
    assert s.stop_event.is_set()


def test_wait_returns_immediately_after_trigger() -> None:
    s = ShutdownHandler()
    s.trigger()
    assert s.wait(timeout=1.0) is True


def test_wait_times_out_when_no_signal() -> None:
    s = ShutdownHandler()
    assert s.wait(timeout=0.05) is False


def test_install_uninstall_idempotent() -> None:
    s = ShutdownHandler()
    s.install_signal_handlers()
    s.install_signal_handlers()  # idempotent — no error
    s.uninstall_signal_handlers()
    s.uninstall_signal_handlers()  # idempotent


def test_context_manager_installs_and_uninstalls() -> None:
    with ShutdownHandler() as s:
        assert s.is_stopping() is False
    # No assertion on signal handlers — just verify no crash on enter/exit
