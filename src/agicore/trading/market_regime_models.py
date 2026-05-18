"""Models for offline market regime detection."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MarketRegime(StrEnum):
    """Market regimes detected by offline heuristics."""

    TRENDING_UP = "TRENDING_UP"
    TRENDING_DOWN = "TRENDING_DOWN"
    RANGING = "RANGING"
    CHOPPY = "CHOPPY"
    BREAKOUT = "BREAKOUT"
    REVERSAL = "REVERSAL"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    LOW_VOLATILITY = "LOW_VOLATILITY"
    NEWS_RISK = "NEWS_RISK"
    DEAD_MARKET = "DEAD_MARKET"


class RegimeStrength(StrEnum):
    """Strength bucket for the primary market regime."""

    WEAK = "WEAK"
    MODERATE = "MODERATE"
    STRONG = "STRONG"
    EXTREME = "EXTREME"


class VolatilityRegime(StrEnum):
    """Volatility condition inferred from ATR and range behavior."""

    LOW = "LOW"
    NORMAL = "NORMAL"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class SessionCondition(StrEnum):
    """Overall tradeability of the detected context."""

    FAVORABLE = "FAVORABLE"
    NEUTRAL = "NEUTRAL"
    CAUTION = "CAUTION"
    DANGEROUS = "DANGEROUS"


@dataclass(frozen=True)
class MarketRegimeAnalysis:
    """Complete offline market regime analysis result."""

    primary_regime: MarketRegime
    confidence: int
    strength: RegimeStrength
    volatility: VolatilityRegime
    session_condition: SessionCondition
    context_quality_score: int
    favorable_for_pullback_strategy: bool
    dangerous_market: bool
    detected_regimes: tuple[MarketRegime, ...]
    warnings: tuple[str, ...]
    recommendations: tuple[str, ...]
    compatibility_notes: tuple[str, ...] = ()


__all__ = [
    "MarketRegime",
    "MarketRegimeAnalysis",
    "RegimeStrength",
    "SessionCondition",
    "VolatilityRegime",
]
