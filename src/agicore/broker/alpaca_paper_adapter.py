"""AlpacaPaperBrokerAdapter — deterministic paper-trading adapter (Phase 8G).

This adapter simulates Alpaca's order execution in paper mode.
It fills all market orders immediately at a deterministic synthetic price
and never touches real capital.

Safety gate: raises LiveTradingForbiddenError for any non-paper mode.
"""
from __future__ import annotations

import hashlib
import threading

import structlog

from .abstract_adapter import AbstractBrokerAdapter

logger = structlog.get_logger(__name__)


class AlpacaPaperBrokerAdapter(AbstractBrokerAdapter):
    """Paper-trading adapter simulating Alpaca Markets.

    Parameters
    ----------
    runtime_mode:
        Must be one of SAFE_MODES; otherwise LiveTradingForbiddenError
        is raised unconditionally.
    """

    NAME: str = "alpaca_paper"

    def __init__(self, *, runtime_mode: str = "SANDBOX") -> None:
        super().__init__(runtime_mode=runtime_mode)
        self._lock = threading.RLock()
        self._order_seq: int = 0
        logger.info(
            "alpaca_paper_adapter.init",
            runtime_mode=runtime_mode,
        )

    # ---------------------------------------------------------------- API

    def ping(self) -> bool:
        """Always reachable — no network required."""
        return True

    def submit_order(
        self,
        symbol: str,
        quantity: float,
        side: str,
        *,
        order_type: str = "MARKET",
    ) -> dict:
        """Submit a synthetic order. Returns a deterministic execution report."""
        with self._lock:
            self._order_seq += 1
            seq = self._order_seq

        order_id = hashlib.sha256(
            f"{self._runtime_mode}:{symbol}:{side}:{seq}".encode()
        ).hexdigest()[:16]

        fill_price = self._synthetic_price(symbol, seq)
        status = "FILLED"

        report = {
            "order_id": order_id,
            "symbol": symbol,
            "quantity": quantity,
            "side": side,
            "order_type": order_type,
            "status": status,
            "fill_price": fill_price,
            "sequence": seq,
        }
        logger.info(
            "alpaca_paper.order_filled",
            order_id=order_id,
            symbol=symbol,
            side=side,
            qty=quantity,
            price=fill_price,
        )
        return report

    # ---------------------------------------------------------------- internals

    @staticmethod
    def _synthetic_price(symbol: str, seq: int) -> float:
        """Deterministic synthetic price based on symbol and sequence."""
        digest = hashlib.sha256(f"{symbol}:{seq}".encode()).digest()
        raw = int.from_bytes(digest[:4], "big")
        # Map to a price between 1.00 and 1000.00
        return 1.0 + (raw % 99900) / 100.0


__all__ = ["AlpacaPaperBrokerAdapter"]
