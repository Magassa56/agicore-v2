"""Offline market regime detection for AGIcore Trading."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .market_regime_models import (
    MarketRegime,
    MarketRegimeAnalysis,
    RegimeStrength,
    SessionCondition,
    VolatilityRegime,
)


def detect_market_regime(
    *,
    prices: Iterable[float],
    ema_fast: Iterable[float] = (),
    ema_slow: Iterable[float] = (),
    atr: Iterable[float] = (),
    ranges: Iterable[float] = (),
    volume: Iterable[float] | None = None,
    timestamps: Iterable[datetime] | None = None,
    strategy_dna: Any | None = None,
    session_replay_result: Any | None = None,
    behavior_result: Any | None = None,
    dangerous_hours: Iterable[int] = (14, 15, 20, 21),
) -> MarketRegimeAnalysis:
    """Detect market regime with deterministic offline heuristics."""
    price_values = _numbers(prices)
    fast_values = _numbers(ema_fast)
    slow_values = _numbers(ema_slow)
    atr_values = _numbers(atr)
    range_values = _numbers(ranges)
    volume_values = _numbers(volume or ())
    time_values = tuple(timestamps or ())
    dangerous_hour_set = set(int(hour) for hour in dangerous_hours)

    if len(price_values) < 2:
        return MarketRegimeAnalysis(
            primary_regime=MarketRegime.DEAD_MARKET,
            confidence=40,
            strength=RegimeStrength.WEAK,
            volatility=VolatilityRegime.LOW,
            session_condition=SessionCondition.CAUTION,
            context_quality_score=20,
            favorable_for_pullback_strategy=False,
            dangerous_market=True,
            detected_regimes=(MarketRegime.DEAD_MARKET,),
            warnings=("Insufficient price history",),
            recommendations=("Collect more bars before classifying the market context.",),
            compatibility_notes=_compatibility_notes(
                strategy_dna=strategy_dna,
                session_replay_result=session_replay_result,
                behavior_result=behavior_result,
                latest_hour=None,
            ),
        )

    latest_price = price_values[-1]
    price_change = latest_price - price_values[0]
    price_range = max(price_values) - min(price_values)
    normalized_move = abs(price_change) / max(price_range, 1e-9)
    fast_slow_gap = _latest_gap_ratio(fast_values, slow_values, latest_price)
    latest_hour = time_values[-1].hour if time_values else None

    atr_ratio = _latest_to_baseline_ratio(atr_values)
    range_ratio = _latest_to_baseline_ratio(range_values)
    volume_ratio = _latest_to_baseline_ratio(volume_values)
    volatility = _volatility_regime(atr_ratio, range_ratio)
    ema_trend = _ema_trend(fast_values, slow_values)
    regimes: list[MarketRegime] = []
    warnings: list[str] = []

    if _is_breakout(price_values, atr_ratio, range_ratio):
        regimes.append(MarketRegime.BREAKOUT)
    if _is_reversal(fast_values, slow_values, price_values):
        regimes.append(MarketRegime.REVERSAL)
    if ema_trend == MarketRegime.TRENDING_UP and normalized_move >= 0.45:
        regimes.append(MarketRegime.TRENDING_UP)
    if ema_trend == MarketRegime.TRENDING_DOWN and normalized_move >= 0.45:
        regimes.append(MarketRegime.TRENDING_DOWN)
    if _is_choppy(price_values, fast_slow_gap, atr_ratio):
        regimes.append(MarketRegime.CHOPPY)
    elif _is_ranging(price_values, fast_slow_gap, normalized_move):
        regimes.append(MarketRegime.RANGING)
    if volatility in (VolatilityRegime.HIGH, VolatilityRegime.EXTREME):
        regimes.append(MarketRegime.HIGH_VOLATILITY)
    if volatility == VolatilityRegime.LOW:
        regimes.append(MarketRegime.LOW_VOLATILITY)
    if _is_news_risk(atr_ratio, range_ratio, volume_ratio):
        regimes.append(MarketRegime.NEWS_RISK)
    if _is_dead_market(price_values, atr_ratio, range_ratio, volume_ratio):
        regimes.append(MarketRegime.DEAD_MARKET)

    regimes = list(dict.fromkeys(regimes or [MarketRegime.RANGING]))
    primary = _primary_regime(regimes)
    confidence = _confidence(
        primary=primary,
        normalized_move=normalized_move,
        atr_ratio=atr_ratio,
        range_ratio=range_ratio,
        fast_slow_gap=fast_slow_gap,
    )
    strength = _strength(confidence)

    if latest_hour in dangerous_hour_set:
        warnings.append(f"Dangerous hour detected: {latest_hour:02d}:00")
    if MarketRegime.NEWS_RISK in regimes:
        warnings.append("ATR/range/volume expansion suggests news risk.")
    if MarketRegime.DEAD_MARKET in regimes:
        warnings.append("Compressed price action suggests a dead market.")
    if MarketRegime.CHOPPY in regimes:
        warnings.append("Alternating price action suggests choppy conditions.")

    compatibility = _compatibility_notes(
        strategy_dna=strategy_dna,
        session_replay_result=session_replay_result,
        behavior_result=behavior_result,
        latest_hour=latest_hour,
    )
    warnings.extend(note for note in compatibility if note.startswith("Risk:"))

    favorable_pullback = _favorable_for_ema20_pullback(
        regimes=tuple(regimes),
        fast_slow_gap=fast_slow_gap,
        volatility=volatility,
        latest_hour=latest_hour,
        strategy_dna=strategy_dna,
    )
    dangerous = _dangerous_market(tuple(regimes), latest_hour, dangerous_hour_set, behavior_result)
    quality = _context_quality_score(
        regimes=tuple(regimes),
        confidence=confidence,
        favorable_for_pullback=favorable_pullback,
        dangerous=dangerous,
    )
    condition = _session_condition(quality, dangerous)

    return MarketRegimeAnalysis(
        primary_regime=primary,
        confidence=confidence,
        strength=strength,
        volatility=volatility,
        session_condition=condition,
        context_quality_score=quality,
        favorable_for_pullback_strategy=favorable_pullback,
        dangerous_market=dangerous,
        detected_regimes=tuple(regimes),
        warnings=tuple(dict.fromkeys(warnings)),
        recommendations=_recommendations(
            primary=primary,
            volatility=volatility,
            favorable_for_pullback=favorable_pullback,
            dangerous=dangerous,
            condition=condition,
        ),
        compatibility_notes=tuple(note for note in compatibility if not note.startswith("Risk:")),
    )


def render_market_regime_markdown(analysis: MarketRegimeAnalysis) -> str:
    """Render a Markdown report for a market regime analysis."""
    lines = [
        "# Market Regime Detection",
        "",
        "## Regime detecte",
        "",
        f"- Principal: {analysis.primary_regime.value}",
        f"- Confiance: {analysis.confidence}/100",
        f"- Force: {analysis.strength.value}",
        f"- Regimes secondaires: {_join_regimes(analysis.detected_regimes)}",
        "",
        "## Volatilite",
        "",
        f"- Regime: {analysis.volatility.value}",
        "",
        "## Qualite du marche",
        "",
        f"- Score contexte: {analysis.context_quality_score}/100",
        f"- Condition session: {analysis.session_condition.value}",
        "",
        "## Risque contexte",
        "",
        f"- Marche dangereux: {'yes' if analysis.dangerous_market else 'no'}",
        *_bullet_lines(analysis.warnings),
        "",
        "## Compatibilite EMA20 pullback",
        "",
        f"- Favorable: {'yes' if analysis.favorable_for_pullback_strategy else 'no'}",
        *_bullet_lines(analysis.compatibility_notes),
        "",
        "## Recommandations",
        "",
        *_bullet_lines(analysis.recommendations),
        "",
    ]
    return "\n".join(lines)


def _numbers(values: Iterable[float]) -> tuple[float, ...]:
    return tuple(float(value) for value in values)


def _latest_to_baseline_ratio(values: tuple[float, ...]) -> float:
    if len(values) < 2:
        return 1.0
    baseline = sum(values[:-1]) / len(values[:-1])
    return values[-1] / baseline if baseline > 0 else 1.0


def _latest_gap_ratio(fast: tuple[float, ...], slow: tuple[float, ...], price: float) -> float:
    if not fast or not slow or price == 0:
        return 0.0
    return abs(fast[-1] - slow[-1]) / abs(price)


def _ema_trend(fast: tuple[float, ...], slow: tuple[float, ...]) -> MarketRegime | None:
    if len(fast) < 2 or len(slow) < 2:
        return None
    fast_slope = fast[-1] - fast[-2]
    slow_slope = slow[-1] - slow[-2]
    if fast[-1] > slow[-1] and fast_slope >= 0 and slow_slope >= 0:
        return MarketRegime.TRENDING_UP
    if fast[-1] < slow[-1] and fast_slope <= 0 and slow_slope <= 0:
        return MarketRegime.TRENDING_DOWN
    return None


def _volatility_regime(atr_ratio: float, range_ratio: float) -> VolatilityRegime:
    signal = max(atr_ratio, range_ratio)
    if signal >= 2.0:
        return VolatilityRegime.EXTREME
    if signal >= 1.35:
        return VolatilityRegime.HIGH
    if atr_ratio <= 0.70 and range_ratio <= 0.80:
        return VolatilityRegime.LOW
    return VolatilityRegime.NORMAL


def _is_breakout(prices: tuple[float, ...], atr_ratio: float, range_ratio: float) -> bool:
    if len(prices) < 4:
        return False
    prior = prices[:-1]
    leaves_range = prices[-1] > max(prior) or prices[-1] < min(prior)
    return leaves_range and (atr_ratio >= 1.10 or range_ratio >= 1.10)


def _is_reversal(
    fast: tuple[float, ...],
    slow: tuple[float, ...],
    prices: tuple[float, ...],
) -> bool:
    if len(fast) < 2 or len(slow) < 2 or len(prices) < 3:
        return False
    crossed_up = fast[-2] <= slow[-2] and fast[-1] > slow[-1]
    crossed_down = fast[-2] >= slow[-2] and fast[-1] < slow[-1]
    price_turn = (prices[-3] > prices[-2] < prices[-1]) or (prices[-3] < prices[-2] > prices[-1])
    return (crossed_up or crossed_down) and price_turn


def _is_choppy(prices: tuple[float, ...], fast_slow_gap: float, atr_ratio: float) -> bool:
    if len(prices) < 5:
        return False
    returns = [prices[index] - prices[index - 1] for index in range(1, len(prices))]
    alternations = sum(
        1
        for index in range(1, len(returns))
        if returns[index] and returns[index - 1] and returns[index] * returns[index - 1] < 0
    )
    return alternations >= max(3, len(returns) // 2) and fast_slow_gap < 0.003 and atr_ratio >= 0.9


def _is_ranging(prices: tuple[float, ...], fast_slow_gap: float, normalized_move: float) -> bool:
    if len(prices) < 4:
        return False
    return fast_slow_gap < 0.0025 and normalized_move < 0.35


def _is_news_risk(atr_ratio: float, range_ratio: float, volume_ratio: float) -> bool:
    return atr_ratio >= 1.80 or range_ratio >= 1.80 or volume_ratio >= 2.00


def _is_dead_market(
    prices: tuple[float, ...],
    atr_ratio: float,
    range_ratio: float,
    volume_ratio: float,
) -> bool:
    if len(prices) < 4:
        return False
    price_range = max(prices) - min(prices)
    mid_price = abs(sum(prices) / len(prices)) or 1.0
    compressed = price_range / mid_price < 0.0015
    quiet_volume = volume_ratio <= 0.75 if volume_ratio != 1.0 else True
    return compressed and atr_ratio <= 0.75 and range_ratio <= 0.80 and quiet_volume


def _primary_regime(regimes: list[MarketRegime]) -> MarketRegime:
    priority = (
        MarketRegime.NEWS_RISK,
        MarketRegime.DEAD_MARKET,
        MarketRegime.BREAKOUT,
        MarketRegime.REVERSAL,
        MarketRegime.TRENDING_UP,
        MarketRegime.TRENDING_DOWN,
        MarketRegime.CHOPPY,
        MarketRegime.RANGING,
        MarketRegime.HIGH_VOLATILITY,
        MarketRegime.LOW_VOLATILITY,
    )
    for regime in priority:
        if regime in regimes:
            return regime
    return regimes[0]


def _confidence(
    *,
    primary: MarketRegime,
    normalized_move: float,
    atr_ratio: float,
    range_ratio: float,
    fast_slow_gap: float,
) -> int:
    base = 55
    if primary in (MarketRegime.TRENDING_UP, MarketRegime.TRENDING_DOWN):
        base += int(min(25, normalized_move * 30)) + int(min(10, fast_slow_gap * 2500))
    elif primary == MarketRegime.BREAKOUT:
        base += int(min(30, (max(atr_ratio, range_ratio) - 1.0) * 35))
    elif primary in (MarketRegime.NEWS_RISK, MarketRegime.DEAD_MARKET):
        base += int(min(35, abs(max(atr_ratio, range_ratio) - 1.0) * 30))
    elif primary in (MarketRegime.RANGING, MarketRegime.CHOPPY):
        base += 15
    return _clamp(base, 0, 100)


def _strength(confidence: int) -> RegimeStrength:
    if confidence >= 90:
        return RegimeStrength.EXTREME
    if confidence >= 75:
        return RegimeStrength.STRONG
    if confidence >= 55:
        return RegimeStrength.MODERATE
    return RegimeStrength.WEAK


def _favorable_for_ema20_pullback(
    *,
    regimes: tuple[MarketRegime, ...],
    fast_slow_gap: float,
    volatility: VolatilityRegime,
    latest_hour: int | None,
    strategy_dna: Any | None,
) -> bool:
    trend_ok = MarketRegime.TRENDING_UP in regimes or MarketRegime.TRENDING_DOWN in regimes
    volatility_ok = volatility in (VolatilityRegime.NORMAL, VolatilityRegime.HIGH)
    structure_ok = MarketRegime.CHOPPY not in regimes and MarketRegime.NEWS_RISK not in regimes
    ema_gap_ok = 0.001 <= fast_slow_gap <= 0.02
    hours = tuple(getattr(strategy_dna, "allowed_hours", ()) or ())
    hour_ok = latest_hour is None or not hours or latest_hour in hours
    return trend_ok and volatility_ok and structure_ok and ema_gap_ok and hour_ok


def _dangerous_market(
    regimes: tuple[MarketRegime, ...],
    latest_hour: int | None,
    dangerous_hours: set[int],
    behavior_result: Any | None,
) -> bool:
    if any(
        regime in regimes
        for regime in (
            MarketRegime.NEWS_RISK,
            MarketRegime.DEAD_MARKET,
            MarketRegime.CHOPPY,
            MarketRegime.HIGH_VOLATILITY,
        )
    ):
        return True
    if latest_hour in dangerous_hours:
        return True
    scores = getattr(behavior_result, "scores", None)
    return bool(scores is not None and getattr(scores, "emotional_risk_score", 100) < 60)


def _context_quality_score(
    *,
    regimes: tuple[MarketRegime, ...],
    confidence: int,
    favorable_for_pullback: bool,
    dangerous: bool,
) -> int:
    score = 50 + (confidence - 50) // 2
    if favorable_for_pullback:
        score += 20
    if dangerous:
        score -= 30
    if MarketRegime.RANGING in regimes:
        score -= 5
    if MarketRegime.CHOPPY in regimes:
        score -= 15
    if MarketRegime.DEAD_MARKET in regimes:
        score -= 20
    return _clamp(score, 0, 100)


def _session_condition(score: int, dangerous: bool) -> SessionCondition:
    if dangerous and score < 45:
        return SessionCondition.DANGEROUS
    if dangerous or score < 60:
        return SessionCondition.CAUTION
    if score >= 75:
        return SessionCondition.FAVORABLE
    return SessionCondition.NEUTRAL


def _recommendations(
    *,
    primary: MarketRegime,
    volatility: VolatilityRegime,
    favorable_for_pullback: bool,
    dangerous: bool,
    condition: SessionCondition,
) -> tuple[str, ...]:
    items: list[str] = []
    if dangerous:
        items.append("Reduce size or pause until context risk normalizes.")
    if primary == MarketRegime.NEWS_RISK:
        items.append("Avoid new entries around suspected news expansion.")
    if primary == MarketRegime.DEAD_MARKET:
        items.append("Wait for range and volume expansion before trading.")
    if primary == MarketRegime.CHOPPY:
        items.append("Avoid EMA pullback entries until directional structure improves.")
    if volatility == VolatilityRegime.EXTREME:
        items.append("Require wider stops or stand aside during extreme volatility.")
    if favorable_for_pullback:
        items.append("EMA20 pullback context is acceptable if entry trigger confirms.")
    if condition == SessionCondition.FAVORABLE and not items:
        items.append("Market context is clean enough for normal playbook execution.")
    return tuple(dict.fromkeys(items or ["Monitor context and wait for clearer regime evidence."]))


def _compatibility_notes(
    *,
    strategy_dna: Any | None,
    session_replay_result: Any | None,
    behavior_result: Any | None,
    latest_hour: int | None,
) -> tuple[str, ...]:
    notes: list[str] = []
    if strategy_dna is not None:
        notes.append(f"Strategy DNA loaded: {getattr(strategy_dna, 'name', 'unknown')}")
        allowed_hours = tuple(getattr(strategy_dna, "allowed_hours", ()) or ())
        if latest_hour is not None and allowed_hours and latest_hour not in allowed_hours:
            notes.append(f"Risk: outside Strategy DNA allowed hours at {latest_hour:02d}:00")
    if session_replay_result is not None:
        discipline = getattr(session_replay_result, "discipline_score", None)
        if discipline is not None:
            notes.append(f"Replay discipline score: {discipline}/100")
    if behavior_result is not None:
        scores = getattr(behavior_result, "scores", None)
        if scores is not None:
            notes.append(f"Behavior emotional risk score: {scores.emotional_risk_score}/100")
            if scores.emotional_risk_score < 60:
                notes.append("Risk: behavior state is emotionally fragile")
    return tuple(notes)


def _join_regimes(regimes: tuple[MarketRegime, ...]) -> str:
    return ", ".join(regime.value for regime in regimes) if regimes else "None"


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int, lower: int, upper: int) -> int:
    return max(lower, min(upper, value))


__all__ = [
    "detect_market_regime",
    "render_market_regime_markdown",
]
