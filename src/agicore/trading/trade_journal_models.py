"""Models for offline trade journal intelligence."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class JournalEmotion(StrEnum):
    """Emotional states manually attached to trades or sessions."""

    NEUTRAL = "NEUTRAL"
    CALM = "CALM"
    CONFIDENT = "CONFIDENT"
    FOCUSED = "FOCUSED"
    FEAR = "FEAR"
    GREED = "GREED"
    STRESS = "STRESS"
    TILT = "TILT"
    FATIGUE = "FATIGUE"
    ANGER = "ANGER"
    FRUSTRATION = "FRUSTRATION"
    EUPHORIA = "EUPHORIA"


class JournalMistakeType(StrEnum):
    """Manual mistake taxonomy for post-trade review."""

    FOMO = "FOMO"
    REVENGE_TRADING = "REVENGE_TRADING"
    OVERTRADING = "OVERTRADING"
    MOVED_STOP = "MOVED_STOP"
    LATE_ENTRY = "LATE_ENTRY"
    EARLY_ENTRY = "EARLY_ENTRY"
    LATE_EXIT = "LATE_EXIT"
    EARLY_EXIT = "EARLY_EXIT"
    CHASED_PRICE = "CHASED_PRICE"
    SIZE_TOO_LARGE = "SIZE_TOO_LARGE"
    IGNORED_PLAYBOOK = "IGNORED_PLAYBOOK"
    BROKE_RISK_RULES = "BROKE_RISK_RULES"
    NO_PREPLAN = "NO_PREPLAN"
    OTHER = "OTHER"


class JournalTag(StrEnum):
    """Common review tags used to group journal entries."""

    WIN = "WIN"
    LOSS = "LOSS"
    BREAKEVEN = "BREAKEVEN"
    HIGH_QUALITY = "HIGH_QUALITY"
    LOW_QUALITY = "LOW_QUALITY"
    REVIEW = "REVIEW"
    NEWS = "NEWS"
    LONDON_OPEN = "LONDON_OPEN"
    NEW_YORK_OPEN = "NEW_YORK_OPEN"
    BREAKOUT = "BREAKOUT"
    PULLBACK = "PULLBACK"
    RANGE = "RANGE"
    TREND = "TREND"


@dataclass(frozen=True)
class TradeJournalEntry:
    """Human journal metadata attached to a single trade."""

    trade_id: str
    session_date: date
    instrument: str
    direction: str
    setup_name: str
    entry_reason: str
    exit_reason: str
    emotion_before: JournalEmotion | None = None
    emotion_during: JournalEmotion | None = None
    emotion_after: JournalEmotion | None = None
    mistake_types: tuple[JournalMistakeType, ...] = ()
    tags: tuple[JournalTag, ...] = ()
    screenshot_paths: tuple[str, ...] = ()
    notes: str = ""
    followed_playbook: bool = True
    followed_risk_rules: bool = True


@dataclass(frozen=True)
class SessionJournalEntry:
    """Human journal metadata attached to a full trading session."""

    session_date: date
    instrument: str = ""
    dominant_emotion: JournalEmotion | None = None
    tags: tuple[JournalTag, ...] = ()
    screenshot_paths: tuple[str, ...] = ()
    notes: str = ""
    followed_playbook: bool = True
    followed_risk_rules: bool = True


@dataclass(frozen=True)
class JournalAnalysisResult:
    """Aggregated offline analysis of journaled trades and sessions."""

    total_trades: int
    total_sessions: int
    dominant_emotions: tuple[tuple[str, int], ...]
    recurring_mistakes: tuple[tuple[str, int], ...]
    most_noted_setups: tuple[tuple[str, int], ...]
    frequent_tags: tuple[tuple[str, int], ...]
    playbook_compliance_rate: float
    risk_rules_compliance_rate: float
    missing_screenshot_trade_ids: tuple[str, ...]
    keyword_flags: tuple[tuple[str, str], ...]
    trades_to_review: tuple[str, ...]
    improvement_plan: tuple[str, ...]


__all__ = [
    "JournalAnalysisResult",
    "JournalEmotion",
    "JournalMistakeType",
    "JournalTag",
    "SessionJournalEntry",
    "TradeJournalEntry",
]
