"""ShutdownHandler — graceful shutdown coordinator.

Bridges OS signals (SIGINT, SIGTERM) and a thread-safe stop event. The
RuntimeEngine installs handlers at startup; the ExecutionLoop watches the
event; user code can also call `trigger()` programmatically.
"""
from __future__ import annotations

import signal
from threading import Event as ThreadEvent
from types import FrameType
from typing import Iterable

import structlog

logger = structlog.get_logger(__name__)


# Signals we install handlers for by default. Restricted to those available
# on the running platform (Windows lacks SIGTERM in some Python builds).
DEFAULT_SIGNALS = (signal.SIGINT, getattr(signal, "SIGTERM", signal.SIGINT))


class ShutdownHandler:
    """Coordinator for graceful shutdown."""

    def __init__(self, *, drain_timeout_s: float = 30.0) -> None:
        self._stop_event = ThreadEvent()
        self._drain_timeout = drain_timeout_s
        self._previous_handlers: dict[int, object] = {}
        self._installed = False

    @property
    def stop_event(self) -> ThreadEvent:
        return self._stop_event

    @property
    def drain_timeout_s(self) -> float:
        return self._drain_timeout

    def install_signal_handlers(
        self, signals: Iterable[int] = DEFAULT_SIGNALS
    ) -> None:
        """Install OS signal handlers. Idempotent. Restores previous on uninstall."""
        if self._installed:
            return
        for sig in set(signals):
            try:
                self._previous_handlers[sig] = signal.signal(sig, self._on_signal)
                logger.debug("shutdown.signal_installed", signal=sig)
            except (ValueError, OSError) as exc:
                # signal.signal can fail when not in main thread or unsupported
                logger.warning("shutdown.signal_install_failed", signal=sig, error=str(exc))
        self._installed = True

    def uninstall_signal_handlers(self) -> None:
        if not self._installed:
            return
        for sig, prev in self._previous_handlers.items():
            try:
                signal.signal(sig, prev)  # type: ignore[arg-type]
            except (ValueError, OSError):
                pass
        self._previous_handlers.clear()
        self._installed = False

    def _on_signal(self, signum: int, frame: FrameType | None) -> None:
        logger.warning("shutdown.signal_received", signum=signum)
        self.trigger()

    def trigger(self) -> None:
        """Programmatic trigger. Safe from any thread."""
        if not self._stop_event.is_set():
            logger.info("shutdown.triggered")
        self._stop_event.set()

    def is_stopping(self) -> bool:
        return self._stop_event.is_set()

    def wait(self, timeout: float | None = None) -> bool:
        """Block until shutdown signaled. Returns True if signaled, False on timeout."""
        return self._stop_event.wait(timeout)

    def __enter__(self) -> "ShutdownHandler":
        self.install_signal_handlers()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.uninstall_signal_handlers()


__all__ = ["ShutdownHandler", "DEFAULT_SIGNALS"]
