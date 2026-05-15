"""AGIcore-v2 — broker package (Phase 8G).

Provides safe, mode-gated broker adapters for paper/sandbox trading.
Live trading is permanently gated by LiveTradingForbiddenError.
"""
from __future__ import annotations

from .abstract_adapter import AbstractBrokerAdapter, LiveTradingForbiddenError
from .alpaca_paper_adapter import AlpacaPaperBrokerAdapter
from .registry import get_adapter

__all__ = [
    "AbstractBrokerAdapter",
    "AlpacaPaperBrokerAdapter",
    "LiveTradingForbiddenError",
    "get_adapter",
]
