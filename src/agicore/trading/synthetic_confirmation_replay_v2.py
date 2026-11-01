"""Causal synthetic V2 replay through confirmation, stopping before risk.

This does not produce an entry, stop, position or financial result. A confirmed
native opportunity is retained in memory for a later, separately governed stage.
"""

from __future__ import annotations

import hashlib
from collections.abc import Iterator, Mapping
from dataclasses import dataclass

from . import directional_impulse_v2 as impulse
from . import ema20_pullback_v2 as ema20
from . import ema_pullback_entry_confirmation_v2 as confirmation
from . import ema_pullback_v2_development_replay as replay
from . import regime_context_v2 as regime
from . import reversal_transition_v2 as reversal
from . import synthetic_pullback_replay_v2 as pullback

WINDOW = impulse.IMPULSE_RANGE_LOOKBACK + 1
SCHEMA = "agicore:synthetic-event-confirmation-replay:v2"


class ClosedPrefix(Mapping[int, ema20.EMA20PullbackBarV2]):
    """Expose only the observed prefix and reject future reads or enumeration."""

    def __init__(self, bars: Mapping[int, ema20.EMA20PullbackBarV2], through: int) -> None:
        self._bars = bars
        self._through = through

    def __getitem__(self, index: int) -> ema20.EMA20PullbackBarV2:
        if type(index) is not int or index > self._through:
            raise ValueError("future or invalid observation access")
        return self._bars[index]

    def __iter__(self) -> Iterator[int]:
        raise TypeError("enumeration of confirmation history is forbidden")

    def __len__(self) -> int:
        raise TypeError("confirmation history length is not observable")


@dataclass(frozen=True)
class ConfirmationReplayOutcome:
    """Durable summary plus native in-memory handoff, never an entry order."""

    summary: dict
    native_confirmation: confirmation.EntryConfirmationEvaluationV2 | None
    stop_window: tuple[ema20.EMA20PullbackBarV2, ...]


def confirmation_snapshot(value: confirmation.EntryConfirmationEvaluationV2 | None) -> dict | None:
    """Project provenance and exact-number hashes without decimal rounding."""
    if value is None:
        return None
    candidate, record = value.candidate, value.confirmation
    context = value.opportunity.consumed_context
    macd = None if candidate is None else candidate.macd_evaluation
    return {
        "state": value.state.value,
        "state_bar_index": value.closed_bar_index,
        "state_timestamp": value.closed_bar_timestamp,
        "pullback_bar_index": context.pullback_bar_index,
        "pullback_timestamp": context.pullback_timestamp,
        "pullback_body_low_sha256": pullback.fraction_sha256(value.opportunity.pullback_body_low),
        "pullback_body_high_sha256": pullback.fraction_sha256(value.opportunity.pullback_body_high),
        "candidate": None
        if candidate is None
        else {
            "bar_index": candidate.confirmation_bar_index,
            "timestamp": candidate.confirmation_timestamp,
            "status": candidate.status.value,
            "price_qualified": candidate.price_qualified,
            "momentum_qualified": candidate.momentum_qualified,
            "qualified": candidate.entry_confirmation,
            "macd_sha256": None if macd is None else pullback.fraction_sha256(macd.macd),
            "signal_sha256": None if macd is None else pullback.fraction_sha256(macd.signal),
            "histogram_sha256": None if macd is None else pullback.fraction_sha256(macd.histogram),
            "previous_macd_sha256": None
            if macd is None
            else pullback.fraction_sha256(macd.previous_macd),
            "previous_histogram_sha256": None
            if macd is None
            else pullback.fraction_sha256(macd.previous_histogram),
        },
        "confirmed": record is not None,
        "source_event_bar_index": context.source_event_bar_index,
        "source_event_timestamp": context.source_event_timestamp,
        "source_event_types": [family.value for family in context.source_event_types],
        "source_direction": context.source_event_direction,
        "confirmation_bar_index": None if record is None else record.confirmation_bar_index,
        "confirmation_timestamp": None if record is None else record.confirmation_timestamp,
        "ema_reference_sha256": pullback.fraction_sha256(context.ema_reference),
    }


def replay_confirmation_native(raw: bytes) -> ConfirmationReplayOutcome:
    """Replay causally to the first confirmed signal or the end of invented input.

    Pending opportunities suppress further context admissions as in the V2
    pending policy. Once confirmed, stop before risk, execution or position
    handling; any remaining input bars are deliberately not replayed.
    """
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    windows, rejection, history = {}, {}, {}
    previous = pending = None
    native = None
    stop_window = ()
    ema = pullback.IncrementalEMA20()
    digest = hashlib.sha256()
    counts = {
        "impulses": 0,
        "reversals": 0,
        "qualified_contexts": 0,
        "pullbacks_evaluated": 0,
        "pullbacks_qualified": 0,
        "opportunities_started": 0,
        "confirmation_candidates": 0,
        "confirmations_qualified": 0,
        "confirmations_expired": 0,
        "events_suppressed_while_pending": 0,
    }
    stop_reason = "END_OF_INPUT"
    processed = 0
    for bar in bars:
        i = bar.bar_index
        price = ema20.EMA20PullbackBarV2(
            i, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        history[i] = price
        advanced = None
        if pending is not None:
            advanced = confirmation.advance_entry_confirmation_momentum_v2(
                previous=pending,
                closed_bar_index=i,
                closed_bar_timestamp=bar.timestamp_utc,
                source_bar_closed=True,
                bars_by_index=ClosedPrefix(history, i),
            )
            counts["confirmation_candidates"] += advanced.candidate is not None
            pending = (
                advanced
                if advanced.state is confirmation.EntryConfirmationStateV2.AWAITING_CONFIRMATION
                else None
            )
            if advanced.entry_confirmation:
                counts["confirmations_qualified"] += 1
                native = advanced
                k = advanced.confirmation.pullback_bar_index
                stop_window = tuple(history[j] for j in range(k, i + 1))
                stop_reason = "CONFIRMED_BEFORE_RISK"
                digest.update(
                    replay.canonical_replay_bytes_v2(
                        {
                            "bar_index": i,
                            "confirmation_progress": confirmation_snapshot(advanced),
                            "stop_reason": stop_reason,
                        }
                    )
                )
                processed = i + 1
                break
            if pending is None:
                counts["confirmations_expired"] += 1
        windows[i] = bar.closed_view()
        rejection[i] = reversal.RejectionBarV2(
            i, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
        )
        if i >= WINDOW:
            del windows[i - WINDOW]
            del rejection[i - WINDOW]
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=i, bars_by_index=windows
        ).event
        reversal_event = None
        if i >= reversal.CONFIRMATION_WINDOW_CLOSED_BARS:
            reversal_event = reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=i - reversal.CONFIRMATION_WINDOW_CLOSED_BARS,
                closed_bar_index=i,
                bars_by_index=rejection,
            ).event
        counts["impulses"] += detected is not None
        counts["reversals"] += reversal_event is not None
        suppressed = pending is not None
        if suppressed:
            counts["events_suppressed_while_pending"] += (detected is not None) + (
                reversal_event is not None
            )
        outcome = pullback.advance_pullback(
            previous,
            price,
            ema,
            directional_impulse_event=None if suppressed else detected,
            reversal_transition_event=None
            if suppressed or reversal_event is None
            else reversal_event.as_regime_event(),
        )
        previous = outcome.lifetime
        counts["qualified_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.QUALIFIED
        )
        counts["pullbacks_evaluated"] += outcome.pullback is not None
        qualified = outcome.pullback is not None and outcome.pullback.pullback_qualified
        counts["pullbacks_qualified"] += qualified
        started = None
        if qualified:
            pending = confirmation.begin_entry_confirmation_momentum_v2(
                pullback=outcome, pullback_bar=price
            )
            started = pending
            counts["opportunities_started"] += 1
        digest.update(
            replay.canonical_replay_bytes_v2(
                {
                    "bar_index": i,
                    "signal": pullback.decision_record(i, detected, reversal_event, outcome),
                    "suppressed": suppressed,
                    "confirmation_progress": confirmation_snapshot(advanced),
                    "confirmation_started": confirmation_snapshot(started),
                }
            )
        )
        ema.append(price)
        processed = i + 1
    if stop_reason == "END_OF_INPUT" and pending is not None:
        stop_reason = "END_OF_INPUT_AWAITING_CONFIRMATION"
    digest.update(
        replay.canonical_replay_bytes_v2(
            {
                "stop_reason": stop_reason,
                "pending": confirmation_snapshot(pending),
            }
        )
    )
    summary = {
        "schema": SCHEMA,
        "input_observations": len(bars),
        "processed_observations": processed,
        "stop_reason": stop_reason,
        "counts": counts,
        "events_sha256": digest.hexdigest(),
    }
    return ConfirmationReplayOutcome(summary, native, stop_window)
