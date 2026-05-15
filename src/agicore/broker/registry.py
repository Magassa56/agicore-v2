"""Broker adapter registry — Phase 8G.

Maps adapter names to their constructor so that callers can obtain
the correct adapter by name without coupling to concrete classes.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .abstract_adapter import AbstractBrokerAdapter

_REGISTRY: dict[str, type] = {}


def _register() -> None:
    """Lazily populate the registry to avoid circular imports."""
    if _REGISTRY:
        return
    from .alpaca_paper_adapter import AlpacaPaperBrokerAdapter

    _REGISTRY["alpaca_paper"] = AlpacaPaperBrokerAdapter


def get_adapter(
    name: str,
    *,
    runtime_mode: str = "SANDBOX",
) -> "AbstractBrokerAdapter | None":
    """Return an initialised adapter for *name* in *runtime_mode*.

    Returns *None* if the adapter name is unknown.
    Raises ``LiveTradingForbiddenError`` if *runtime_mode* is not safe.
    """
    _register()
    cls = _REGISTRY.get(name)
    if cls is None:
        return None
    return cls(runtime_mode=runtime_mode)


def list_adapter_names() -> list[str]:
    """Return all registered adapter names."""
    _register()
    return sorted(_REGISTRY.keys())


__all__ = ["get_adapter", "list_adapter_names"]
