"""Exact incremental EMA and pullback for validated invented observations.

This is a new replay component, not a change to the frozen strategy. Its
decisions must be checked against the existing full-history implementation.
"""

from __future__ import annotations

import hashlib
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction

from . import ema20_pullback_v2 as frozen
from . import regime_context_v2 as regime


def _exact(value: object) -> Fraction:
    if type(value) is int or isinstance(value, Fraction):
        return Fraction(value)
    if isinstance(value, Decimal) and value.is_finite():
        return Fraction(value)
    raise ValueError("validated exact price required")


class IncrementalEMA20:
    """Maintain the frozen seed and recurrence without rounding or resets."""

    def __init__(self) -> None:
        self.last_index = -1
        self.last_timestamp = None
        self.last_close = None
        self.seed_sum = Fraction(0)
        self.reference = None

    def append(self, bar: frozen.EMA20PullbackBarV2) -> None:
        """Append exactly one strictly increasing, already validated closed bar."""
        if (
            not isinstance(bar, frozen.EMA20PullbackBarV2)
            or not bar.is_closed
            or bar.bar_index != self.last_index + 1
            or (self.last_timestamp is not None and bar.timestamp_utc <= self.last_timestamp)
        ):
            raise ValueError("noncausal incremental EMA input")
        close = _exact(bar.close)
        if bar.bar_index < frozen.EMA_PERIOD:
            self.seed_sum += close
            if bar.bar_index == frozen.EMA_PERIOD - 1:
                self.reference = self.seed_sum / frozen.EMA_PERIOD
        else:
            self.reference = (2 * close + 19 * self.reference) / 21
        self.last_index, self.last_timestamp, self.last_close = (
            bar.bar_index,
            bar.timestamp_utc,
            close,
        )


def advance_pullback(
    previous: regime.RegimeContextLifetimeEvaluation | None,
    bar: frozen.EMA20PullbackBarV2,
    ema: IncrementalEMA20,
    *,
    directional_impulse_event: regime.RegimeEvent | None,
    reversal_transition_event: regime.RegimeEvent | None,
) -> frozen.EMA20PullbackContextEvaluationV2:
    """Apply frozen lifecycle and exact prior-close EMA geometry to one bar."""
    if ema.last_index != bar.bar_index - 1:
        raise ValueError("EMA must end at the immediately prior bar")
    if ema.last_timestamp is not None and ema.last_timestamp >= bar.timestamp_utc:
        raise ValueError("EMA must precede the candidate timestamp")
    result = None

    def predicate(context, index, timestamp):
        nonlocal result
        if (index, timestamp) != (bar.bar_index, bar.timestamp_utc):
            raise ValueError("candidate identity mismatch")
        status = frozen.EMA20PullbackStatusV2.INSUFFICIENT_EMA_WARMUP
        qualified, reference = False, None
        if index >= frozen.EMA_PERIOD:
            reference = ema.reference
            if reference is None or ema.last_close is None:
                raise ValueError("missing exact EMA after warmup")
            open_, high, low, close = map(_exact, (bar.open, bar.high, bar.low, bar.close))
            if high < max(open_, close) or low > min(open_, close) or high < low:
                raise ValueError("validated OHLC required")
            status = frozen.EMA20PullbackStatusV2.EVALUATED
            if context.source_event_direction is regime.RegimeDirection.LONG:
                qualified = (
                    ema.last_close > reference
                    and open_ >= reference
                    and low <= reference
                    and close > reference
                )
            else:
                qualified = (
                    ema.last_close < reference
                    and open_ <= reference
                    and high >= reference
                    and close < reference
                )
        result = frozen.EMA20PullbackEvaluationV2(
            status,
            qualified,
            index,
            timestamp,
            context.source_event_types,
            context.source_event_direction,
            context.source_event_bar_index,
            context.source_event_timestamp,
            reference,
        )
        return qualified

    lifetime = regime.advance_regime_context_v2(
        previous=previous,
        closed_bar_index=bar.bar_index,
        closed_bar_timestamp=bar.timestamp_utc,
        source_bar_closed=bar.is_closed,
        directional_impulse_event=directional_impulse_event,
        reversal_transition_event=reversal_transition_event,
        ema20_pullback_qualified=predicate,
    )
    if result is not None and result.pullback_qualified:
        lifetime = replace(
            lifetime, context=replace(lifetime.context, ema_reference=result.ema_reference)
        )
    return frozen.EMA20PullbackContextEvaluationV2(lifetime, result)


def fraction_sha256(value: Fraction | None) -> str | None:
    """Hash an exact normalized rational without decimal digit conversion."""
    if value is None:
        return None
    numerator, denominator = value.numerator, value.denominator
    n = abs(numerator).to_bytes(max(1, (abs(numerator).bit_length() + 7) // 8), "big")
    d = denominator.to_bytes(max(1, (denominator.bit_length() + 7) // 8), "big")
    payload = (
        (b"-" if numerator < 0 else b"+")
        + len(n).to_bytes(8, "big")
        + n
        + len(d).to_bytes(8, "big")
        + d
    )
    return hashlib.sha256(payload).hexdigest()


def decision_record(index, impulse_event, reversal_event, outcome):
    """Project a deterministic nonfinancial decision with exact-reference hashes."""
    ctx, pullback = outcome.lifetime.context, outcome.pullback
    return {
        "bar_index": index,
        "impulse": impulse_event,
        "reversal": reversal_event,
        "composition": outcome.lifetime.composition.status.value,
        "context_state": ctx.state.value,
        "source_event_bar_index": ctx.source_event_bar_index,
        "source_event_direction": ctx.source_event_direction,
        "pullback_bar_index": ctx.pullback_bar_index,
        "context_ema_sha256": fraction_sha256(ctx.ema_reference),
        "pullback": None
        if pullback is None
        else {
            "status": pullback.status.value,
            "qualified": pullback.pullback_qualified,
            "ema_reference_sha256": fraction_sha256(pullback.ema_reference),
        },
    }
