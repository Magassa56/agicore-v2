"""Models for offline trading session replay."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum


class ReplayEventType(StrEnum):
    """Replay event names emitted by the offline engine."""

    SESSION_STARTED = "SESSION_STARTED"
    TRADE_OPENED = "TRADE_OPENED"
    TRADE_CLOSED = "TRADE_CLOSED"
    RULE_VIOLATION = "RULE_VIOLATION"
    SESSION_STOP_RECOMMENDED = "SESSION_STOP_RECOMMENDED"
    SESSION_ENDED = "SESSION_ENDED"


class ReplayViolationType(StrEnum):
    """Supported replay rule violations."""

    OVERTRADING = "OVERTRADING"
    REVENGE_TRADING_PROBABLE = "REVENGE_TRADING_PROBABLE"
    DAILY_LOSS_EXCEEDED = "DAILY_LOSS_EXCEEDED"
    OUTSIDE_ALLOWED_HOURS = "OUTSIDE_ALLOWED_HOURS"
    MAX_TRADES_PER_DAY = "MAX_TRADES_PER_DAY"
    EXCESSIVE_UNIT_LOSS = "EXCESSIVE_UNIT_LOSS"


@dataclass(frozen=True)
class SessionReplayConfig:
    """Thresholds for offline session replay."""

    max_trades_per_day: int = 10
    overtrading_threshold: int = 10
    max_daily_loss: float | None = None
    max_unit_loss: float | None = None
    allowed_hours: tuple[int, ...] = ()
    revenge_trade_window_minutes: int = 5


@dataclass(frozen=True)
class ReplayViolation:
    """One detected behavior or rule violation."""

    kind: ReplayViolationType
    message: str
    timestamp: datetime
    trade_index: int | None = None
    penalty: int = 10


@dataclass(frozen=True)
class ReplayEvent:
    """Chronological event emitted during replay."""

    event_type: ReplayEventType
    timestamp: datetime
    session_day: date
    message: str
    trade_index: int | None = None
    violation: ReplayViolation | None = None


@dataclass(frozen=True)
class SessionReplaySummary:
    """Computed metrics for one trading session/day."""

    session_day: date
    total_pnl: float
    trade_count: int
    win_rate: float
    largest_loss: float
    largest_gain: float
    max_loss_streak: int
    start_time: datetime | None
    end_time: datetime | None
    discipline_score: int
    violations: tuple[ReplayViolation, ...] = ()


@dataclass(frozen=True)
class SessionReplayResult:
    """Replay output for all sessions."""

    sessions: tuple[SessionReplaySummary, ...]
    events: tuple[ReplayEvent, ...]
    discipline_score: int
    comparison_notes: tuple[str, ...] = field(default_factory=tuple)


__all__ = [
    "ReplayEvent",
    "ReplayEventType",
    "ReplayViolation",
    "ReplayViolationType",
    "SessionReplayConfig",
    "SessionReplayResult",
    "SessionReplaySummary",
]
