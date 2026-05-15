"""Risk and exposure data models — Phase 8C.

Pure data, fully offline. ``RiskManager`` consumes ``ExecutionIntent`` +
``ExposureSnapshot`` and produces ``RiskCheckResult``. All models are
frozen Pydantic for safe sharing across threads.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Canonical bus event types
# ============================================================================
EVT_RISK_PASSED: str = "risk.check.passed"
EVT_RISK_BLOCKED: str = "risk.check.blocked"


# ============================================================================
# Enums
# ============================================================================
class RiskLevel(str, Enum):
    """Severity tag for a single violation."""
    INFO = "INFO"
    WARN = "WARN"
    BLOCK = "BLOCK"


class RiskCheckCode(str, Enum):
    """Canonical violation codes."""
    OK = "OK"
    POSITION_SIZE_EXCEEDED = "POSITION_SIZE_EXCEEDED"
    EXPOSURE_EXCEEDED = "EXPOSURE_EXCEEDED"
    DRAWDOWN_EXCEEDED = "DRAWDOWN_EXCEEDED"
    DAILY_LOSS_EXCEEDED = "DAILY_LOSS_EXCEEDED"
    INSUFFICIENT_POSITION = "INSUFFICIENT_POSITION"
    INVALID_INTENT = "INVALID_INTENT"


class IntentSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# ============================================================================
# Limits configuration
# ============================================================================
class RiskLimits(BaseModel):
    """Configurable risk limits. Each ``None`` disables the corresponding check."""
    model_config = ConfigDict(frozen=True)

    # Per-symbol max units (absolute value)
    max_position_size: float | None = Field(default=None, ge=0)
    # Max gross exposure value across all symbols (sum of |qty*price|)
    max_exposure_value: float | None = Field(default=None, ge=0)
    # Max drawdown fraction in [0, 1]
    max_drawdown_pct: float | None = Field(default=None, ge=0, le=1)
    # Max absolute loss (positive number) allowed within the current day
    daily_loss_limit: float | None = Field(default=None, ge=0)


# ============================================================================
# Exposure snapshot (input to validation)
# ============================================================================
class SymbolExposure(BaseModel):
    """Per-symbol position summary."""
    model_config = ConfigDict(frozen=True)

    symbol: str = Field(..., min_length=1, max_length=32)
    quantity: float = Field(..., ge=0)               # long-only
    avg_entry_price: float = Field(..., ge=0)
    mark_price: float = Field(..., ge=0)

    @property
    def exposure_value(self) -> float:
        return abs(self.quantity * self.mark_price)


class ExposureSnapshot(BaseModel):
    """Aggregate runtime state used by the RiskManager."""
    model_config = ConfigDict(frozen=True)

    positions: dict[str, SymbolExposure] = Field(default_factory=dict)
    realized_pnl_total: float = 0.0
    daily_pnl: float = 0.0
    initial_equity: float = Field(..., gt=0)
    peak_equity: float = Field(..., gt=0)

    @property
    def current_equity(self) -> float:
        return self.initial_equity + self.realized_pnl_total

    @property
    def total_gross_exposure(self) -> float:
        return sum(p.exposure_value for p in self.positions.values())

    @property
    def drawdown_pct(self) -> float:
        if self.peak_equity <= 0:
            return 0.0
        dd = (self.peak_equity - self.current_equity) / self.peak_equity
        return max(0.0, dd)


def empty_snapshot(*, initial_equity: float = 10_000.0) -> ExposureSnapshot:
    """Convenience builder for a fresh, no-positions snapshot."""
    return ExposureSnapshot(
        positions={},
        realized_pnl_total=0.0,
        daily_pnl=0.0,
        initial_equity=initial_equity,
        peak_equity=initial_equity,
    )


# ============================================================================
# Intent (input to validation)
# ============================================================================
class ExecutionIntent(BaseModel):
    """Proposed order to validate before submission."""
    model_config = ConfigDict(frozen=True)

    intent_id: str = Field(..., min_length=1, max_length=64)
    symbol: str = Field(..., min_length=1, max_length=32)
    side: IntentSide
    quantity: float = Field(..., gt=0)
    estimated_price: float = Field(..., gt=0)
    timestamp: datetime


# ============================================================================
# Result (output of validation)
# ============================================================================
class RiskViolation(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: RiskCheckCode
    level: RiskLevel
    message: str = Field(..., max_length=256)
    limit_value: float | None = None
    actual_value: float | None = None


class RiskCheckResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    passed: bool
    violations: list[RiskViolation] = Field(default_factory=list)
    intent_id: str | None = None
    timestamp: datetime

    @property
    def is_blocked(self) -> bool:
        return any(v.level == RiskLevel.BLOCK for v in self.violations)


__all__ = [
    "RiskLevel",
    "RiskCheckCode",
    "IntentSide",
    "RiskLimits",
    "SymbolExposure",
    "ExposureSnapshot",
    "empty_snapshot",
    "ExecutionIntent",
    "RiskViolation",
    "RiskCheckResult",
    "EVT_RISK_PASSED",
    "EVT_RISK_BLOCKED",
]
