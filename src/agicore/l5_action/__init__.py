"""AGIcore-v2 L5 — Action layer.

Phase 7C : safe broker abstraction. Mock implementation for offline
validation. Future-compatible with NinjaTrader / Alpaca adapters via
the ``Broker`` Protocol.
"""
from .broker_mock import MockBroker
from .broker_models import (
    Broker,
    BrokerError,
    ExecutionReport,
    InsufficientPositionError,
    InvalidOrderError,
    Order,
    OrderNotFoundError,
    OrderRequest,
    OrderSide,
    OrderStatus,
    OrderType,
    Position,
)
from .execution_service import ExecutionService

__all__ = [
    # Enums
    "OrderSide",
    "OrderType",
    "OrderStatus",
    # Models
    "OrderRequest",
    "Order",
    "Position",
    "ExecutionReport",
    # Protocol
    "Broker",
    # Implementation
    "MockBroker",
    # Service
    "ExecutionService",
    # Errors
    "BrokerError",
    "OrderNotFoundError",
    "InsufficientPositionError",
    "InvalidOrderError",
]
