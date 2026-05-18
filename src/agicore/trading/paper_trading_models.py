"""Models for offline paper trading adapter simulation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PaperOrderSide(StrEnum):
    """Supported paper order sides."""

    BUY = "BUY"
    SELL = "SELL"


class PaperOrderType(StrEnum):
    """Supported paper order types."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


class PaperOrderStatus(StrEnum):
    """Lifecycle status for simulated paper orders."""

    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"


@dataclass(frozen=True)
class PaperOrderRequest:
    """Paper order request. This never routes to a real broker."""

    symbol: str
    side: PaperOrderSide
    quantity: float
    order_type: PaperOrderType = PaperOrderType.MARKET
    simulated_price: float = 0.0
    risk_allowed: bool = True
    trading_enabled: bool = True
    client_order_id: str | None = None


@dataclass(frozen=True)
class PaperPosition:
    """Simple in-memory simulated position."""

    symbol: str
    quantity: float
    average_price: float
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0


@dataclass(frozen=True)
class PaperAccountState:
    """Simple simulated paper account state."""

    cash: float
    equity: float
    realized_pnl: float
    open_positions: int
    trading_enabled: bool


@dataclass(frozen=True)
class PaperOrderResult:
    """Result returned by the offline paper adapter."""

    order_id: str
    request: PaperOrderRequest
    status: PaperOrderStatus
    accepted: bool
    reason: str
    filled_quantity: float = 0.0
    fill_price: float | None = None
    position: PaperPosition | None = None
    account_state: PaperAccountState | None = None


__all__ = [
    "PaperAccountState",
    "PaperOrderRequest",
    "PaperOrderResult",
    "PaperOrderSide",
    "PaperOrderStatus",
    "PaperOrderType",
    "PaperPosition",
]
