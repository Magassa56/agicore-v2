"""Predeclared invented fixtures. Never open a market dataset or select by PnL."""

from __future__ import annotations

from dataclasses import replace
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from fractions import Fraction

from agicore.trading.ema_pullback_v2_development_replay import DevelopmentReplayBarV2
from agicore.trading.regime_context_v2 import RegimeDirection
from tests.unit.trading.test_ema_pullback_regime_gated_baseline_v2 import _scenario

START = datetime(2099, 1, 1, tzinfo=UTC)
SEEDS = ()  # All fixtures use deterministic integer formulas, no random state.
SIZES = (1000, 5000, 10000, 20000)
FAMILIES = (
    "CONSTANT_CONTROL",
    "ONE_TICK_PULSE_THEN_CONSTANT",
    "NONCONSTANT_TICK_GRID_DRIFT_AND_OSCILLATION",
    "DENSE_LIFECYCLE_LONG_SHORT_WITH_GAPS_AND_OFF_SESSION_DATA",
)
SCENARIOS = (
    "impulse_profit", "reversal_profit", "qty1_profit", "first_confirmation",
    "risk_reject", "intrabar_stop", "gap_stop", "breached_1", "breached_2",
    "stop_wins", "position_suppressed", "exit_regime_admitted", "context_age",
    "context_elapsed", "confirmation_no", "confirmation_elapsed", "entry_gap",
    "entry_missing", "ema_gap", "context_eof", "confirmation_eof", "entry_eof",
    "open_eof", "ema_eof", "rejection_eof", "dual_probe",
)
ORACLE_CHECKPOINTS = (0, 18, 19, 20, 33, 34, 35, 63, 127, 255, 511, 999)


def lifecycle_fixture(name: str, direction: RegimeDirection) -> bytes:
    """Use every predeclared reference scenario, without profitability selection."""
    if name not in SCENARIOS:
        raise ValueError("undeclared scenario")
    bars = _scenario(name, direction)
    return ("\n".join(
        ";".join((b.timestamp_utc.strftime("%Y%m%d %H%M%S"),
                   *(str(getattr(b, f)) for f in ("open", "high", "low", "close")),
                   str(b.volume)))
        for b in bars.values()
    ) + "\n").encode("ascii")


def benchmark_bars(family: str, count: int):
    """Invent tick-grid observations; gaps/off-session rows remain actual rows."""
    if family not in FAMILIES or type(count) is not int or count < 2:
        raise ValueError("invalid predeclared fixture")
    templates = (
        tuple(_scenario("impulse_profit", RegimeDirection.LONG).values()),
        tuple(_scenario("reversal_profit", RegimeDirection.SHORT).values()),
    ) if family == FAMILIES[3] else None
    elapsed = 0
    for i in range(count):
        if i:
            elapsed += 1 + (12 if templates and i % 257 == 0 else 0)
        stamp = START + timedelta(minutes=elapsed)
        if templates:
            template = templates[(i // 57) % 2][i % 57]
            yield DevelopmentReplayBarV2(i, stamp, template.open, template.high,
                                        template.low, template.close, template.volume)
        else:
            ticks = 80000
            if family == FAMILIES[1] and i == 20:
                ticks += 1
            elif family == FAMILIES[2]:
                ticks += i // 17 + (i % 31 - 15) * 3 + (i % 7 - 3)
            price = Decimal(ticks) / 4
            yield DevelopmentReplayBarV2(i, stamp, price, price + Decimal("0.25"),
                                        price - Decimal("0.25"), price, 100)


def tick_close(family: str, index: int) -> Fraction:
    """Independent integer input formula for the indicator oracle."""
    return Fraction(next(b.close for b in benchmark_bars(family, index + 1)
                         if b.bar_index == index))


def resource_fixture_bars(family: str, count: int):
    """Dense resource fixtures start on Saturday; retain the original families too.

    This explicit clock-only extension is predeclared before resource tests.
    It makes off-session coverage present even at 1,000 bars; no strategy rule
    or input price/volume is changed and the original generator stays available.
    """
    shift = timedelta(days=2) if family == FAMILIES[3] else timedelta(0)
    for bar in benchmark_bars(family, count):
        yield replace(bar, timestamp_utc=bar.timestamp_utc + shift)


def dense_lifecycle_resource_bars_v2(count: int):
    """Predeclared dense contacts and exits; no profitability feedback or filtering.

    Close paths remain the original alternating invented templates. Pullback
    wicks reach the tick on the far side of the already-known exact prior EMA.
    Sixteen fixed cycles cover both sides with EMA exits, intrabar stops, gap
    stops, entry breaches, quantities one/two, risk rejection and confirmation
    failure. Every input remains invented; the original generator is preserved.
    """
    ema = None
    seed = Fraction()
    observed = {}
    for original in resource_fixture_bars(FAMILIES[3], count):
        i = original.bar_index
        cycle, offset = divmod(i, 57)
        mode = cycle % 16
        long = cycle % 2 == 0
        bar = original
        # Fixed tick-grid expansion of the event/confirmation pulse. The bounded
        # legacy prefix was seeded near zero momentum, whereas a continuous
        # stream retains momentum from prior cycles. Scale this prescribed
        # input pulse, preserving body/wick geometry; do not inspect its PnL.
        if 29 <= offset <= 36:
            bar = replace(bar, **{field: Decimal(20000) + 4 * (
                getattr(bar, field) - Decimal(20000))
                for field in ("open", "high", "low", "close")})
        pullback_offset = 33 if long else 34
        if offset == pullback_offset and ema is not None:
            ticks = ema * 4
            touch = (ticks.numerator // ticks.denominator if long
                     else -(-ticks.numerator // ticks.denominator))
            price = Decimal(touch) / 4
            if mode in (8, 9, 10, 11):
                price = min(price, bar.close - 35) if long else max(price, bar.close + 35)
            if mode in (12, 13):
                price = min(price, bar.close - 100) if long else max(price, bar.close + 100)
            bar = replace(bar, low=min(bar.low, price)) if long else replace(
                bar, high=max(bar.high, price))
        if offset == 35 and mode in (14, 15):
            pullback = observed[i - (2 if long else 1)]
            close = max(pullback.open, pullback.close) if long else min(
                pullback.open, pullback.close)
            bar = replace(bar, close=close, high=max(bar.high, close), low=min(bar.low, close))
        if offset in (36, 40) and mode in (2, 3, 4, 5, 6, 7, 10, 11):
            relevant = [observed[cycle * 57 + n] for n in range(pullback_offset, 36)]
            level = min(b.low for b in relevant) - Decimal("0.25") if long else (
                max(b.high for b in relevant) + Decimal("0.25"))
            if offset == 36 and mode in (6, 7) or offset == 40 and mode in (4, 5):
                opening = level - Decimal("0.25") if long else level + Decimal("0.25")
                bar = replace(bar, open=opening, high=max(opening, bar.close) + Decimal("0.25"),
                              low=min(opening, bar.close) - Decimal("0.25"))
            elif offset == 40 and mode in (2, 3, 10, 11):
                bar = replace(bar, low=min(bar.low, level)) if long else replace(
                    bar, high=max(bar.high, level))
        observed[i] = bar
        close = Fraction(bar.close)
        if i < 20:
            seed += close
            if i == 19:
                ema = seed / 20
        else:
            ema = (2 * close + 19 * ema) / 21
        yield bar
