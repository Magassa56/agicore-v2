"""Abstract broker adapter base and safety exceptions — Phase 8G.

LiveTradingForbiddenError is the hard gate that prevents any live capital
from being touched during paper/sandbox/dry-run sessions. Any adapter that
receives a non-paper runtime_mode must raise this error in __init__.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class LiveTradingForbiddenError(RuntimeError):
    """Raised when an adapter is initialised with a live-capital runtime mode.

    This is an unconditional hard-stop — no retry, no fallback.
    """


class AbstractBrokerAdapter(ABC):
    """Base class for all broker adapters in AGIcore-v2.

    All concrete subclasses MUST call ``_assert_safe_mode`` in their
    ``__init__`` before performing any I/O.
    """

    #: Runtime modes that are considered safe (no real capital at risk).
    SAFE_MODES: frozenset[str] = frozenset(
        {"SANDBOX", "REPLAY", "DRY_RUN", "PAPER", "LIVE_DISABLED"}
    )

    def __init__(self, *, runtime_mode: str) -> None:
        self._assert_safe_mode(runtime_mode)
        self._runtime_mode = runtime_mode

    @property
    def runtime_mode(self) -> str:
        """The runtime mode this adapter was initialised with."""
        return self._runtime_mode

    def _assert_safe_mode(self, mode: str) -> None:
        """Raise LiveTradingForbiddenError if *mode* is not in SAFE_MODES."""
        if mode not in self.SAFE_MODES:
            raise LiveTradingForbiddenError(
                f"Adapter refused to initialise: runtime_mode={mode!r} is not "
                f"in the safe-mode allowlist {sorted(self.SAFE_MODES)}. "
                "Live trading is permanently forbidden in AGIcore-v2."
            )

    @abstractmethod
    def ping(self) -> bool:
        """Return True if the adapter is reachable / operational."""

    @abstractmethod
    def submit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        *,
        order_type: str = "MARKET",
    ) -> dict:
        """Submit an order and return an execution-report dict."""


__all__ = ["AbstractBrokerAdapter", "LiveTradingForbiddenError"]
