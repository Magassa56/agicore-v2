"""Health status enums and report model — Phase 8F.

HealthStatus values are used by DryRunHealthChecker and by AGIcoreManager
to surface system condition to supervisors and dashboards.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class HealthStatus(str, Enum):
    """Distinct health condition codes emitted by health checkers."""

    OK = "OK"
    """All checks passed — system operating normally."""

    STALLED_FEED = "STALLED_FEED"
    """No market ticks received within the expected window."""

    REPEATED_REJECTS = "REPEATED_REJECTS"
    """Order reject rate exceeds configured safety threshold."""

    QUEUE_CONGESTION = "QUEUE_CONGESTION"
    """Unfilled order backlog exceeds configured threshold."""

    COMPONENT_UNHEALTHY = "COMPONENT_UNHEALTHY"
    """A registered sub-component reported an error state."""


@dataclass(frozen=True)
class HealthReport:
    """A single health observation produced by a checker.

    Attributes
    ----------
    status:
        The HealthStatus code for this observation.
    detail:
        Human-readable explanation (structlog-friendly).
    """

    status: HealthStatus
    detail: str = ""


__all__ = ["HealthReport", "HealthStatus"]
