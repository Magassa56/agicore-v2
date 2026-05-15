"""Broker domain models — orders, positions, execution reports.

Phase 7C : safe abstraction layer for future broker integrations
(NinjaTrader, Alpaca). All models are Pydantic. Types are designed to be
broker-agnostic so a real adapter can implement the ``Broker`` Protocol
without changing this module or downstream code.

Lifecycle of an Order :
    PENDING → FILLED
            → CANCELLED
            → REJECTED
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ============================================================================
# Enums
# ============================================================================
class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


# ============================================================================
# Input DTO
# ============================================================================
class OrderRequest(BaseModel):
    """Input DTO for ``Broker.submit_order``. Immutable."""
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(..., min_length=1, max_length=32)
    side: OrderSide
    quantity: float = Field(..., gt=0)
    order_type: OrderType = OrderType.MARKET
    limit_price: float | None = Field(default=None, ge=0)
    client_order_id: str | None = Field(default=None, max_length=64)

    @model_validator(mode="after")
    def _limit_requires_price(self) -> "OrderRequest":
        if self.order_type == OrderType.LIMIT and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT orders")
        if self.order_type == OrderType.MARKET and self.limit_price is not None:
            # Allowed but ignored — keep strict to surface bugs
            raise ValueError("limit_price must be None for MARKET orders")
        return self


# ============================================================================
# Persistent state
# ============================================================================
class Order(BaseModel):
    """Persistent record of an order's full lifecycle."""
    model_config = ConfigDict(frozen=True)

    order_id: str = Field(..., min_length=1, max_length=64)
    client_order_id: str | None = Field(default=None, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=32)
    side: OrderSide
    quantity: float = Field(..., gt=0)
    order_type: OrderType
    limit_price: float | None = Field(default=None, ge=0)
    status: OrderStatus = OrderStatus.PENDING
    filled_price: float | None = Field(default=None, ge=0)
    filled_quantity: float | None = Field(default=None, ge=0)
    filled_at: datetime | None = None
    cancelled_at: datetime | None = None
    rejected_reason: str | None = Field(default=None, max_length=256)
    created_at: datetime


class Position(BaseModel):
    """Net position for a symbol. Long-only in Phase 7C."""
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float = Field(..., ge=0)  # long-only: 0 or positive
    avg_entry_price: float = Field(..., ge=0)
    realized_pnl: float = 0.0
    last_update: datetime


class ExecutionReport(BaseModel):
    """Outcome of a single broker call (submit / cancel)."""
    model_config = ConfigDict(frozen=True)

    order_id: str
    status: OrderStatus
    filled_price: float | None = None
    filled_quantity: float | None = None
    timestamp: datetime
    message: str = ""


# ============================================================================
# Protocol — future-compatible with NinjaTrader / Alpaca adapters
# ============================================================================
class Broker(Protocol):
    """Minimal broker interface. Adapter contract for real brokers."""

    def submit_order(self, request: OrderRequest) -> ExecutionReport: ...
    def cancel_order(self, order_id: str) -> ExecutionReport: ...
    def get_position(self, symbol: str) -> Position | None: ...
    def get_open_orders(self) -> list[Order]: ...


# ============================================================================
# Domain exceptions
# ============================================================================
class BrokerError(Exception):
    """Base class for all broker-related errors."""


class OrderNotFoundError(BrokerError, LookupError):
    """No order with that id."""


class InsufficientPositionError(BrokerError):
    """SELL would result in negative position (not supported in Phase 7C)."""


class InvalidOrderError(BrokerError, ValueError):
    """Order request failed validation at the broker."""


# ============================================================================
# Helpers
# ============================================================================
def utcnow() -> datetime:
    return datetime.now(timezone.utc)


__all__ = [
    "OrderSide",
    "OrderType",
    "OrderStatus",
    "OrderRequest",
    "Order",
    "Position",
    "ExecutionReport",
    "Broker",
    "BrokerError",
    "OrderNotFoundError",
    "InsufficientPositionError",
    "InvalidOrderError",
    "utcnow",
]
