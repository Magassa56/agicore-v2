"""Models for the offline AGIcore trading session coach."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SessionCoachDecision(StrEnum):
    """Possible coaching decisions for a trading session."""

    CONTINUE = "CONTINUE"
    REDUCE_RISK = "REDUCE_RISK"
    TAKE_BREAK = "TAKE_BREAK"
    STOP_TRADING = "STOP_TRADING"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


class SessionRiskLevel(StrEnum):
    """Recommended risk level before or during a session."""

    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass(frozen=True)
class PreSessionChecklist:
    """Checklist generated before trading starts."""

    discipline_state: str
    recurring_dangerous_contexts: tuple[str, ...]
    dangerous_hours: tuple[int, ...]
    playbook_rules: tuple[str, ...]
    daily_limits: tuple[str, ...]
    emotional_reminders: tuple[str, ...]
    recommended_risk_level: SessionRiskLevel
    decision: SessionCoachDecision


@dataclass(frozen=True)
class LiveSessionCoachResult:
    """In-session coach output based on current replay and behavior state."""

    alerts: tuple[str, ...]
    recommendations: tuple[str, ...]
    stop_recommended: bool
    break_recommended: bool
    reduce_size: bool
    decision: SessionCoachDecision


@dataclass(frozen=True)
class PostSessionReview:
    """Post-session coaching review."""

    discipline_summary: str
    detected_errors: tuple[str, ...]
    violated_rules: tuple[str, ...]
    strengths: tuple[str, ...]
    improvement_areas: tuple[str, ...]
    session_score: int
    memory_comparison: tuple[str, ...]
    decision: SessionCoachDecision


__all__ = [
    "LiveSessionCoachResult",
    "PostSessionReview",
    "PreSessionChecklist",
    "SessionCoachDecision",
    "SessionRiskLevel",
]
