"""Dataclasses for an offline trader playbook."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RiskRules:
    """Declared risk constraints for the trader playbook."""

    max_daily_loss: float | None = None
    max_trades_per_day: int | None = None
    max_consecutive_losses: int | None = None
    forbidden_hours: tuple[int, ...] = ()
    minimum_win_rate: float | None = None
    minimum_average_trade: float | None = None


@dataclass(frozen=True)
class TraderProfile:
    """Declared trader profile and setup rules."""

    name: str
    style_detected: str
    entry_conditions: tuple[str, ...] = ()
    exit_conditions: tuple[str, ...] = ()
    forbidden_conditions: tuple[str, ...] = ()
    risk_rules: RiskRules = field(default_factory=RiskRules)
    notes: str | None = None


@dataclass(frozen=True)
class PlaybookCheck:
    """Single comparison finding between declared playbook and realized stats."""

    rule: str
    expected: str
    actual: str
    status: str
    message: str


@dataclass(frozen=True)
class PlaybookComparison:
    """Comparison result between a playbook and trading statistics."""

    profile_name: str
    style_detected: str
    total_checks: int
    passed_checks: int
    failed_checks: int
    checks: tuple[PlaybookCheck, ...]

    @property
    def is_compliant(self) -> bool:
        return self.failed_checks == 0


__all__ = [
    "PlaybookCheck",
    "PlaybookComparison",
    "RiskRules",
    "TraderProfile",
]
