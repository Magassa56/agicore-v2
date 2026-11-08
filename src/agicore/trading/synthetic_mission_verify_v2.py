"""Independently verify a new invented-observation bundle in another process.

The generated input is reconstructed independently of the bundle. The event
pipeline is assembled again here, using the same underlying V2 predicates; this
is not an independent reimplementation of the frozen strategy predicates.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import zlib
from collections import deque
from pathlib import Path
from types import SimpleNamespace

from tools.agicore_v2_synthetic_scale_probe import generate_observations

from . import directional_impulse_v2 as impulse
from . import ema20_pullback_v2 as ema20
from . import ema_pullback_entry_confirmation_v2 as confirmation
from . import ema_pullback_initial_stop_v2 as structural_stop
from . import ema_pullback_open_position_signal_policy_v2 as position_policy
from . import ema_pullback_pending_opportunity_policy_v2 as pending_policy
from . import ema_pullback_v2_development_replay as replay
from . import regime_context_v2 as regime
from . import reversal_transition_v2 as reversal
from . import synthetic_pullback_replay_v2 as pullback
from .ema20_pullback_v2 import EMA20PullbackBarV2
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionOpenV2,
    EntryExecutionStateV2,
    _valid_utc,
    execute_entry_open_v2,
    register_entry_execution_v2,
)
from .ema_pullback_exit_policy_v2 import (
    MAX_EXIT_EXECUTION_ELAPSED_TIME,
    EMA20ExitFillRecordV2,
    EMA20ExitSignalRecordV2,
)
from .ema_pullback_risk_position_sizing_v2 import (
    INSTRUMENT,
    PositionStateV2,
    RiskSizedEntryRecordV2,
    RiskSizingDecisionV2,
    evaluate_risk_position_sizing_v2,
)
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    StructuralStopExecutionStateV2,
    observe_structural_stop_v2,
    register_structural_stop_execution_v2,
)
from .synthetic_confirmation_fixture_v2 import (
    PROFILES as CONFIRMATION_PROFILES,
)
from .synthetic_confirmation_fixture_v2 import (
    SCHEMA as CONFIRMATION_BUNDLE_SCHEMA,
)
from .synthetic_confirmation_fixture_v2 import generate_confirmation_fixture
from .synthetic_confirmation_replay_v2 import (
    SCHEMA as CONFIRMATION_SCHEMA,
)
from .synthetic_confirmation_replay_v2 import ClosedPrefix, confirmation_snapshot
from .synthetic_entry_replay_v2 import SCHEMA as ENTRY_SCHEMA
from .synthetic_exit_replay_v2 import SCHEMA as EXIT_SCHEMA
from .synthetic_mission_storage_v2 import (
    MAX_OBSERVATIONS,
    ROWS_PER_CHUNK,
    SCHEMA,
    canonical,
    sha,
)
from .synthetic_risk_replay_v2 import SCHEMA as RISK_SCHEMA
from .synthetic_stop_replay_v2 import SCHEMA as STOP_SCHEMA


def recompute_events(raw: bytes) -> dict:
    """Reassemble event/context progression separately from the producer."""
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    window = deque(maxlen=impulse.IMPULSE_RANGE_LOOKBACK + 1)
    previous = None
    digest = hashlib.sha256()
    counts = {"impulses": 0, "reversals": 0, "qualified_contexts": 0, "ambiguous_contexts": 0}
    for bar in bars:
        window.append(
            (
                bar.closed_view(),
                reversal.RejectionBarV2(
                    bar.bar_index, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
                ),
            )
        )
        impulse_view = {item[0].bar_index: item[0] for item in window}
        reversal_view = {item[1].bar_index: item[1] for item in window}
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=bar.bar_index, bars_by_index=impulse_view
        ).event
        candidate = bar.bar_index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
        reversal_event = None
        if candidate >= 0:
            reversal_event = reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=candidate,
                closed_bar_index=bar.bar_index,
                bars_by_index=reversal_view,
            ).event
        previous = regime.advance_regime_context_v2(
            previous=previous,
            closed_bar_index=bar.bar_index,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            directional_impulse_event=detected,
            reversal_transition_event=None
            if reversal_event is None
            else reversal_event.as_regime_event(),
        )
        counts["impulses"] += detected is not None
        counts["reversals"] += reversal_event is not None
        counts["qualified_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.QUALIFIED
        )
        counts["ambiguous_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.AMBIGUOUS
        )
        digest.update(
            replay.canonical_replay_bytes_v2(
                {
                    "bar_index": bar.bar_index,
                    "impulse": detected,
                    "reversal": reversal_event,
                    "context": previous,
                }
            )
        )
    digest.update(
        replay.canonical_replay_bytes_v2({"terminal": regime.finish_regime_context_v2(previous)})
    )
    return {"observations": len(bars), "counts": counts, "events_sha256": digest.hexdigest()}


def recompute_pullback_events(raw: bytes) -> dict:
    """Independently rebuild the event pipeline through exact pullback."""
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    window = deque(maxlen=impulse.IMPULSE_RANGE_LOOKBACK + 1)
    previous, ema = None, pullback.IncrementalEMA20()
    digest = hashlib.sha256()
    counts = {
        "impulses": 0,
        "reversals": 0,
        "qualified_contexts": 0,
        "pullbacks_evaluated": 0,
        "pullbacks_qualified": 0,
    }
    for bar in bars:
        window.append(
            (
                bar.closed_view(),
                reversal.RejectionBarV2(
                    bar.bar_index, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
                ),
            )
        )
        impulse_view = {item[0].bar_index: item[0] for item in window}
        reversal_view = {item[1].bar_index: item[1] for item in window}
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=bar.bar_index, bars_by_index=impulse_view
        ).event
        candidate = bar.bar_index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
        reversal_event = (
            None
            if candidate < 0
            else reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=candidate,
                closed_bar_index=bar.bar_index,
                bars_by_index=reversal_view,
            ).event
        )
        price = ema20.EMA20PullbackBarV2(
            bar.bar_index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        outcome = pullback.advance_pullback(
            previous,
            price,
            ema,
            directional_impulse_event=detected,
            reversal_transition_event=None
            if reversal_event is None
            else reversal_event.as_regime_event(),
        )
        previous = outcome.lifetime
        counts["impulses"] += detected is not None
        counts["reversals"] += reversal_event is not None
        counts["qualified_contexts"] += (
            previous.composition.status is regime.RegimeContextStatus.QUALIFIED
        )
        counts["pullbacks_evaluated"] += outcome.pullback is not None
        counts["pullbacks_qualified"] += (
            outcome.pullback is not None and outcome.pullback.pullback_qualified
        )
        digest.update(
            replay.canonical_replay_bytes_v2(
                pullback.decision_record(bar.bar_index, detected, reversal_event, outcome)
            )
        )
        ema.append(price)
    terminal = regime.finish_regime_context_v2(previous).context
    digest.update(
        replay.canonical_replay_bytes_v2(
            {
                "terminal_state": terminal.state.value,
                "source_event_bar_index": terminal.source_event_bar_index,
                "pullback_bar_index": terminal.pullback_bar_index,
                "ema_reference_sha256": pullback.fraction_sha256(terminal.ema_reference),
            }
        )
    )
    return {
        "schema": "agicore:synthetic-event-pullback-replay:v1",
        "observations": len(bars),
        "counts": counts,
        "events_sha256": digest.hexdigest(),
    }


def recompute_confirmation_events(raw: bytes, *, handoff: bool = False):
    """Reconstruct the first confirmed opportunity without orders or risk."""
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    window = deque(maxlen=impulse.IMPULSE_RANGE_LOOKBACK + 1)
    history = {}
    ema = pullback.IncrementalEMA20()
    lifetime = pending = native = None
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
    stop_reason, processed = "END_OF_INPUT", 0
    for bar in bars:
        index = bar.bar_index
        price = ema20.EMA20PullbackBarV2(
            index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        history[index] = price
        advanced = None
        if pending is not None:
            advanced = confirmation.advance_entry_confirmation_momentum_v2(
                previous=pending,
                closed_bar_index=index,
                closed_bar_timestamp=bar.timestamp_utc,
                source_bar_closed=True,
                bars_by_index=ClosedPrefix(history, index),
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
                stop_reason = "CONFIRMED_BEFORE_RISK"
                digest.update(
                    replay.canonical_replay_bytes_v2(
                        {
                            "bar_index": index,
                            "confirmation_progress": confirmation_snapshot(advanced),
                            "stop_reason": stop_reason,
                        }
                    )
                )
                processed = index + 1
                break
            if pending is None:
                counts["confirmations_expired"] += 1
        window.append(
            (
                bar.closed_view(),
                reversal.RejectionBarV2(
                    index, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
                ),
            )
        )
        impulse_bars = {pair[0].bar_index: pair[0] for pair in window}
        reversal_bars = {pair[1].bar_index: pair[1] for pair in window}
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=index, bars_by_index=impulse_bars
        ).event
        candidate = index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
        reversed_event = (
            None
            if candidate < 0
            else reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=candidate,
                closed_bar_index=index,
                bars_by_index=reversal_bars,
            ).event
        )
        counts["impulses"] += detected is not None
        counts["reversals"] += reversed_event is not None
        suppressed = pending is not None
        if suppressed:
            counts["events_suppressed_while_pending"] += (detected is not None) + (
                reversed_event is not None
            )
        outcome = pullback.advance_pullback(
            lifetime,
            price,
            ema,
            directional_impulse_event=None if suppressed else detected,
            reversal_transition_event=None
            if suppressed or reversed_event is None
            else reversed_event.as_regime_event(),
        )
        lifetime = outcome.lifetime
        counts["qualified_contexts"] += (
            lifetime.composition.status is regime.RegimeContextStatus.QUALIFIED
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
                    "bar_index": index,
                    "signal": pullback.decision_record(index, detected, reversed_event, outcome),
                    "suppressed": suppressed,
                    "confirmation_progress": confirmation_snapshot(advanced),
                    "confirmation_started": confirmation_snapshot(started),
                }
            )
        )
        ema.append(price)
        processed = index + 1
    if stop_reason == "END_OF_INPUT" and pending is not None:
        stop_reason = "END_OF_INPUT_AWAITING_CONFIRMATION"
    digest.update(
        replay.canonical_replay_bytes_v2(
            {"stop_reason": stop_reason, "pending": confirmation_snapshot(pending)}
        )
    )
    summary = {
        "schema": CONFIRMATION_SCHEMA,
        "input_observations": len(bars),
        "processed_observations": processed,
        "stop_reason": stop_reason,
        "counts": counts,
        "events_sha256": digest.hexdigest(),
    }
    return (summary, native, history) if handoff else summary


def recompute_stop_events(raw: bytes) -> dict:
    """Rebuild confirmation and evaluate the frozen stop on our own input window.

    This path does not use the producer's stop replay or its supplied tuple.
    It shares frozen V2 predicates and canonical encoding with the producer.
    """
    summary, native, history = recompute_confirmation_events(raw, handoff=True)
    if native is None or summary["stop_reason"] != "CONFIRMED_BEFORE_RISK":
        raise ValueError("the fixed stop profile did not confirm")
    source = native.confirmation
    k, q = source.pullback_bar_index, source.confirmation_bar_index
    if (
        type(k) is not int
        or type(q) is not int
        or not 0 <= k < q
        or q - k not in (1, 2)
        or summary["processed_observations"] != q + 1
    ):
        raise ValueError("invalid independently reconstructed window")
    # This independent map contains only validated, already-closed k..q bars.
    selected = {index: history[index] for index in range(k, q + 1)}
    result = structural_stop.evaluate_initial_stop_v2(confirmation=native, bars_by_index=selected)
    if (
        result.status is not structural_stop.InitialStopStatusV2.EVALUATED
        or result.initial_stop_record is None
        or result.at_entry is not None
    ):
        raise ValueError("independent stop not captured without entry")
    rows = raw.splitlines(keepends=True)
    if len(rows) != summary["input_observations"] or q >= len(rows):
        raise ValueError("independent row boundaries differ from input")
    return {
        "schema": STOP_SCHEMA,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "confirmation_replay": summary,
        "confirmation": json.loads(replay.canonical_replay_bytes_v2(source)),
        "window": {
            "first_bar_index": k,
            "last_bar_index": q,
            "raw_rows_sha256": hashlib.sha256(b"".join(rows[k : q + 1])).hexdigest(),
        },
        "stop": json.loads(replay.canonical_replay_bytes_v2(result)),
        "stop_reason": "STOP_CAPTURED_BEFORE_RISK",
    }


def _independent_admission_state(raw, expected, expected_history):
    """Reconstruct frozen admission through first confirmation, without costs.

    This verifier starts flat and does not cover subsequent opportunities or a
    pre-existing position. It deliberately rebuilds the gate from the input.
    """
    q = expected.confirmation.confirmation_bar_index
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    if type(q) is not int or not 0 <= q < len(bars):
        raise ValueError("invalid independently admitted confirmation clock")
    policy = pending_policy.begin_pending_opportunity_policy_v2(
        strategy_instance_id="VERIFIER_SYNTHETIC", series_id="FIRST_POSITION_ONLY"
    )
    history = {}
    window = deque(maxlen=impulse.IMPULSE_RANGE_LOOKBACK + 1)
    for bar in bars[: q + 1]:
        i = bar.bar_index
        history[i] = EMA20PullbackBarV2(
            i, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, True
        )
        window.append(
            (
                bar.closed_view(),
                reversal.RejectionBarV2(
                    i, bar.timestamp_utc, bar.close, True, bar.open, bar.high, bar.low
                ),
            )
        )
        if (
            policy.risks.decisions
            or policy.risks.executions.entries
            or policy.positions.positions
            or policy.initial_stops.entries
        ):
            raise ValueError("independent admission requires an initially empty position book")
        prefix = ClosedPrefix(history, i)
        owner = policy.active_opportunity
        if owner is not None:
            if owner.state is not pending_policy.PendingOpportunityStateV2.AWAITING_CONFIRMATION:
                raise ValueError("independent admission encountered a pending execution")
            signal = confirmation.advance_entry_confirmation_momentum_v2(
                previous=owner.confirmation,
                closed_bar_index=i,
                closed_bar_timestamp=bar.timestamp_utc,
                source_bar_closed=True,
                bars_by_index=prefix,
            )
            if signal.entry_confirmation:
                if i != q or signal != expected or history[i] != expected_history[i]:
                    raise ValueError("independent admission confirmation disagrees with input")
                clock = position_policy.advance_open_position_signal_policy_v2(
                    previous=policy.positions,
                    closed_bar_index=i,
                    closed_bar_timestamp=bar.timestamp_utc,
                    source_bar_closed=True,
                    bars_by_index=prefix,
                )
                if (
                    clock.position_state is not PositionStateV2.FLAT
                    or clock.positions
                    or not clock.signal_decisions
                    or (
                        clock.signal_decisions[-1].composition.closed_bar_index,
                        clock.signal_decisions[-1].composition.closed_bar_timestamp,
                    )
                    != (i, bar.timestamp_utc)
                ):
                    raise ValueError("independent admission policy is not flat at confirmation")
                position_policy._require_admitted_pullback(clock, signal.confirmation)
                return clock.position_state
        if i == q:
            raise ValueError("independent confirmation lacks a native pending admission")
        impulse_view = {item[0].bar_index: item[0] for item in window}
        reversal_view = {item[1].bar_index: item[1] for item in window}
        detected = impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=i, bars_by_index=impulse_view
        ).event
        previous = i - reversal.CONFIRMATION_WINDOW_CLOSED_BARS
        reversed_event = (
            None
            if previous < 0
            else reversal.evaluate_reversal_transition_event_v2(
                rejection_candidate_bar_index=previous,
                closed_bar_index=i,
                bars_by_index=reversal_view,
            ).event
        )
        events = (
            detected,
            None if reversed_event is None else reversed_event.as_regime_event(),
        )
        policy = pending_policy.advance_pending_opportunity_close_v2(
            previous=policy,
            closed_bar_index=i,
            closed_bar_timestamp=bar.timestamp_utc,
            source_bar_closed=True,
            bars_by_index=prefix,
            regime_events_at_close=lambda events=events: events,
        )
    raise ValueError("independent admission was not found")


def reconstruct_risk_native(raw: bytes) -> dict:
    """Independently rebuild confirmation, structural stop and risk decision."""
    summary, native, history = recompute_confirmation_events(raw, handoff=True)
    if native is None or summary["stop_reason"] != "CONFIRMED_BEFORE_RISK":
        raise ValueError("the fixed risk profile did not confirm")
    source = native.confirmation
    k, q = source.pullback_bar_index, source.confirmation_bar_index
    if (
        type(k) is not int
        or type(q) is not int
        or not 0 <= k < q
        or q - k not in (1, 2)
        or summary["processed_observations"] != q + 1
    ):
        raise ValueError("invalid independently reconstructed window")
    selected = {index: history[index] for index in range(k, q + 1)}
    stop_result = structural_stop.evaluate_initial_stop_v2(
        confirmation=native, bars_by_index=selected
    )
    if (
        stop_result.status is not structural_stop.InitialStopStatusV2.EVALUATED
        or stop_result.initial_stop_record is None
        or stop_result.at_entry is not None
    ):
        raise ValueError("independent stop not captured without entry")
    candidate_bar = history[q]
    admitted_state = _independent_admission_state(raw, native, history)
    risk_result = evaluate_risk_position_sizing_v2(
        instrument=INSTRUMENT,
        closed_bar_index=q,
        closed_bar_timestamp=source.confirmation_timestamp,
        source_bar_closed=True,
        confirmation=native,
        initial_stop=stop_result,
        position_state=admitted_state,
        bars_by_index={q: candidate_bar},
    )
    rows = raw.splitlines(keepends=True)
    if len(rows) != summary["input_observations"] or q >= len(rows):
        raise ValueError("independent row boundaries differ from input")
    return {
        "schema": RISK_SCHEMA,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "confirmation_replay": summary,
        "confirmation": json.loads(replay.canonical_replay_bytes_v2(source)),
        "window": {
            "first_bar_index": k,
            "last_bar_index": q,
            "raw_rows_sha256": hashlib.sha256(b"".join(rows[k : q + 1])).hexdigest(),
        },
        "stop": json.loads(replay.canonical_replay_bytes_v2(stop_result)),
        "risk": json.loads(replay.canonical_replay_bytes_v2(risk_result)),
        "stop_reason": "RISK_DECIDED_BEFORE_ENTRY",
    }


def reconstruct_entry_native(raw: bytes) -> dict:
    """Independently rebuild confirmation, structural stop, risk decision and entry execution."""
    summary, native, history = recompute_confirmation_events(raw, handoff=True)
    if native is None or summary["stop_reason"] != "CONFIRMED_BEFORE_RISK":
        raise ValueError("the fixed entry profile did not confirm")
    source = native.confirmation
    k, q = source.pullback_bar_index, source.confirmation_bar_index
    if (
        type(k) is not int
        or type(q) is not int
        or not 0 <= k < q
        or q - k not in (1, 2)
        or summary["processed_observations"] != q + 1
    ):
        raise ValueError("invalid independently reconstructed window")
    selected = {index: history[index] for index in range(k, q + 1)}
    stop_result = structural_stop.evaluate_initial_stop_v2(
        confirmation=native, bars_by_index=selected
    )
    if (
        stop_result.status is not structural_stop.InitialStopStatusV2.EVALUATED
        or stop_result.initial_stop_record is None
        or stop_result.at_entry is not None
    ):
        raise ValueError("independent stop not captured without entry")
    candidate_bar = history[q]
    admitted_state = _independent_admission_state(raw, native, history)
    risk_result = evaluate_risk_position_sizing_v2(
        instrument=INSTRUMENT,
        closed_bar_index=q,
        closed_bar_timestamp=source.confirmation_timestamp,
        source_bar_closed=True,
        confirmation=native,
        initial_stop=stop_result,
        position_state=admitted_state,
        bars_by_index={q: candidate_bar},
    )
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    rows = raw.splitlines(keepends=True)
    if len(rows) != summary["input_observations"] or len(bars) != len(rows) or q >= len(bars):
        raise ValueError("independent row boundaries differ from input")

    if risk_result.decision is RiskSizingDecisionV2.REJECT:
        entry_eval = None
        sized_entry = None
        bound_stop = stop_result
        stop_reason = "ENTRY_REJECTED_BY_RISK"
    else:
        opening_bar = None
        if q + 1 < len(bars):
            next_b = bars[q + 1]
            opening_bar = EntryExecutionOpenV2(
                bar_index=next_b.bar_index,
                timestamp_utc=next_b.timestamp_utc,
                open=next_b.open,
            )
        book = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=native)
        book = execute_entry_open_v2(previous=book, confirmation=source, opening_bar=opening_bar)
        entry_eval = book.for_confirmation(source)
        if entry_eval.execution_state is EntryExecutionStateV2.FILLED:
            if entry_eval.execution is None:
                raise ValueError("filled execution must contain execution record")
            sized_entry = RiskSizedEntryRecordV2(
                risk_decision=risk_result, execution=entry_eval.execution
            )
            stop_book = structural_stop.InitialStopBookV2(entries=(stop_result,))
            bound_stop_book = structural_stop.bind_initial_stop_to_entry_v2(
                previous=stop_book, confirmation=source, executions=book
            )
            bound_stop = bound_stop_book.for_confirmation(source)
            stop_reason = "ENTRY_FILLED_BEFORE_EXIT"
        else:
            sized_entry = None
            bound_stop = stop_result
            stop_reason = f"ENTRY_{entry_eval.execution_state.value}"

    entry_json = (
        json.loads(replay.canonical_replay_bytes_v2(entry_eval)) if entry_eval is not None else None
    )
    sized_json = (
        json.loads(replay.canonical_replay_bytes_v2(sized_entry))
        if sized_entry is not None
        else None
    )

    return {
        "schema": ENTRY_SCHEMA,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "confirmation_replay": summary,
        "confirmation": json.loads(replay.canonical_replay_bytes_v2(source)),
        "window": {
            "first_bar_index": k,
            "last_bar_index": q,
            "raw_rows_sha256": hashlib.sha256(b"".join(rows[k : q + 1])).hexdigest(),
        },
        "stop": json.loads(replay.canonical_replay_bytes_v2(bound_stop)),
        "risk": json.loads(replay.canonical_replay_bytes_v2(risk_result)),
        "entry": entry_json,
        "sized_entry": sized_json,
        "stop_reason": stop_reason,
    }


def _reconstruct_exit_without_costs(source, bound_stop, entry_eval, sized_entry, bars):
    """Independently replay the frozen stop/EMA predicates without accounting."""
    stop_book = structural_stop.InitialStopBookV2(entries=(bound_stop,))
    stops = register_structural_stop_execution_v2(
        previous=StructuralStopExecutionBookV2(), initial_stops=stop_book, confirmation=source
    )
    current = stops.for_confirmation(source)
    if current.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP:
        return current.fill, "FLAT", "EXIT_STRUCTURAL_STOP_FILLED"

    entry = entry_eval.execution
    is_long = source.source_regime_event_direction is regime.RegimeDirection.LONG
    adverse_name = "low" if is_long else "high"
    history = {}
    pending = None
    for bar in bars:
        idx, timestamp = bar.bar_index, bar.timestamp_utc
        if idx < entry.execution_bar_index:
            history[idx] = EMA20PullbackBarV2(
                idx, timestamp, bar.open, bar.high, bar.low, bar.close, True
            )
            continue
        current = stops.for_confirmation(source)
        if (
            idx != current.next_observation_bar_index
            or not _valid_utc(timestamp)
            or (idx == entry.execution_bar_index and timestamp != entry.execution_bar_timestamp)
            or (
                current.last_observed_bar_timestamp is not None
                and timestamp <= current.last_observed_bar_timestamp
            )
        ):
            raise ValueError("independent exit observation has invalid index or clock")
        opening = (
            entry.execution_price_before_costs
            if idx == entry.execution_bar_index
            else ema20._exact_price(bar.open)
        )
        if opening is None or opening <= 0:
            raise ValueError("independent exit opening price is invalid")
        level = bound_stop.initial_stop_record.initial_stop_price
        if idx > entry.execution_bar_index and (opening <= level if is_long else opening >= level):
            stops = observe_structural_stop_v2(
                previous=stops,
                confirmation=source,
                observation=SimpleNamespace(bar_index=idx, timestamp_utc=timestamp, open=opening),
            )
            result = stops.for_confirmation(source)
            if result.stop_execution_state is not StructuralStopExecutionStateV2.FILLED_STOP:
                raise ValueError("independent opening gap failed to resolve")
            return result.fill, "FLAT", "EXIT_STRUCTURAL_STOP_FILLED"
        if pending is not None:
            if idx != pending.exit_signal_bar_index + 1:
                raise ValueError("independent EMA exit requires next indexed open")
            if timestamp - pending.exit_signal_timestamp <= MAX_EXIT_EXECUTION_ELAPSED_TIME:
                return (
                    EMA20ExitFillRecordV2(pending, idx, timestamp, opening),
                    "FLAT",
                    "EXIT_EMA20_FILLED",
                )
            pending = None
        stops = observe_structural_stop_v2(
            previous=stops,
            confirmation=source,
            observation=SimpleNamespace(
                bar_index=idx,
                timestamp_utc=timestamp,
                open=opening,
                **{adverse_name: getattr(bar, adverse_name)},
            ),
        )
        current = stops.for_confirmation(source)
        if current.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP:
            return current.fill, "FLAT", "EXIT_STRUCTURAL_STOP_FILLED"
        if current.stop_execution_state is not StructuralStopExecutionStateV2.ARMED:
            raise ValueError("independent stop observation is invalid")
        history[idx] = EMA20PullbackBarV2(
            idx, timestamp, bar.open, bar.high, bar.low, bar.close, True
        )
        ema = ema20.evaluate_ema20_v2(
            through_bar_index=idx, bars_by_index=ClosedPrefix(history, idx)
        )
        if ema.status is ema20.EMA20StatusV2.EVALUATED:
            if ema.known_at_timestamp != timestamp:
                raise ValueError("independent EMA is not known at this close")
            qualifies = ema.last_close < ema.ema20 if is_long else ema.last_close > ema.ema20
            if qualifies:
                pending = EMA20ExitSignalRecordV2(
                    bound_stop.at_entry,
                    sized_entry.quantity,
                    idx,
                    timestamp,
                    ema.last_close,
                    ema.ema20,
                )
    return None, "OPEN_UNREALIZED", "OPEN_UNREALIZED_END_OF_DATA"


def reconstruct_exit_native(raw: bytes) -> dict:
    """Independently rebuild confirmation, stop, risk, entry and exit policy."""
    summary, native, history = recompute_confirmation_events(raw, handoff=True)
    if native is None or summary["stop_reason"] != "CONFIRMED_BEFORE_RISK":
        raise ValueError("the fixed exit profile did not confirm")
    source = native.confirmation
    k, q = source.pullback_bar_index, source.confirmation_bar_index
    if (
        type(k) is not int
        or type(q) is not int
        or not 0 <= k < q
        or q - k not in (1, 2)
        or summary["processed_observations"] != q + 1
    ):
        raise ValueError("invalid independently reconstructed window")
    selected = {index: history[index] for index in range(k, q + 1)}
    stop_result = structural_stop.evaluate_initial_stop_v2(
        confirmation=native, bars_by_index=selected
    )
    if (
        stop_result.status is not structural_stop.InitialStopStatusV2.EVALUATED
        or stop_result.initial_stop_record is None
        or stop_result.at_entry is not None
    ):
        raise ValueError("independent stop not captured without entry")
    candidate_bar = history[q]
    admitted_state = _independent_admission_state(raw, native, history)
    risk_result = evaluate_risk_position_sizing_v2(
        instrument=INSTRUMENT,
        closed_bar_index=q,
        closed_bar_timestamp=source.confirmation_timestamp,
        source_bar_closed=True,
        confirmation=native,
        initial_stop=stop_result,
        position_state=admitted_state,
        bars_by_index={q: candidate_bar},
    )
    bars = replay.parse_ninjatrader_last_rows_v2(raw)
    rows = raw.splitlines(keepends=True)
    if len(rows) != summary["input_observations"] or len(bars) != len(rows) or q >= len(bars):
        raise ValueError("independent row boundaries differ from input")

    if risk_result.decision is RiskSizingDecisionV2.REJECT:
        entry_eval = None
        sized_entry = None
        bound_stop = stop_result
        exit_record = None
        end_state = None
        stop_reason = "ENTRY_REJECTED_BY_RISK"
    else:
        opening_bar = None
        if q + 1 < len(bars):
            next_b = bars[q + 1]
            opening_bar = EntryExecutionOpenV2(
                bar_index=next_b.bar_index,
                timestamp_utc=next_b.timestamp_utc,
                open=next_b.open,
            )
        book = register_entry_execution_v2(previous=EntryExecutionBookV2(), confirmation=native)
        book = execute_entry_open_v2(previous=book, confirmation=source, opening_bar=opening_bar)
        entry_eval = book.for_confirmation(source)
        if entry_eval.execution_state is EntryExecutionStateV2.FILLED:
            if entry_eval.execution is None:
                raise ValueError("filled execution must contain execution record")
            sized_entry = RiskSizedEntryRecordV2(
                risk_decision=risk_result, execution=entry_eval.execution
            )
            stop_book = structural_stop.InitialStopBookV2(entries=(stop_result,))
            bound_stop_book = structural_stop.bind_initial_stop_to_entry_v2(
                previous=stop_book, confirmation=source, executions=book
            )
            bound_stop = bound_stop_book.for_confirmation(source)

            exit_record, end_state, stop_reason = _reconstruct_exit_without_costs(
                source, bound_stop, entry_eval, sized_entry, bars
            )
        else:
            sized_entry = None
            bound_stop = stop_result
            exit_record = None
            end_state = None
            stop_reason = f"ENTRY_{entry_eval.execution_state.value}"

    entry_json = (
        json.loads(replay.canonical_replay_bytes_v2(entry_eval)) if entry_eval is not None else None
    )
    sized_json = (
        json.loads(replay.canonical_replay_bytes_v2(sized_entry))
        if sized_entry is not None
        else None
    )
    exit_json = (
        json.loads(replay.canonical_replay_bytes_v2(exit_record))
        if exit_record is not None
        else None
    )

    return {
        "schema": EXIT_SCHEMA,
        "input_sha256": hashlib.sha256(raw).hexdigest(),
        "confirmation_replay": summary,
        "confirmation": json.loads(replay.canonical_replay_bytes_v2(source)),
        "window": {
            "first_bar_index": k,
            "last_bar_index": q,
            "raw_rows_sha256": hashlib.sha256(b"".join(rows[k : q + 1])).hexdigest(),
        },
        "stop": json.loads(replay.canonical_replay_bytes_v2(bound_stop)),
        "risk": json.loads(replay.canonical_replay_bytes_v2(risk_result)),
        "entry": entry_json,
        "sized_entry": sized_json,
        "exit": exit_json,
        "end_state": end_state,
        "stop_reason": stop_reason,
    }


def read_regular(path: Path, limit: int) -> bytes:
    """Read one bounded regular file without following a symlink or hardlink."""
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    if path.is_symlink():
        raise ValueError("symlink forbidden")
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_size > limit:
            raise ValueError("invalid evidence file")
        content = stream.read(limit + 1)
        if len(content) != info.st_size:
            raise ValueError("evidence changed during read")
        return content


def verify(
    bundle: Path, observations: int, *, stage: str = "events", profile: str = "standard"
) -> dict:
    """Regenerate invented input, validate every chunk, and repeat the replay."""
    if type(observations) is not int or not 1 <= observations <= MAX_OBSERVATIONS:
        raise ValueError("invalid observation count")
    if stage not in ("events", "pullback", "confirmation", "stop", "risk", "entry", "exit"):
        raise ValueError("unsupported replay stage")
    if profile not in ("standard", *CONFIRMATION_PROFILES):
        raise ValueError("unsupported invented profile")
    if profile != "standard" and stage not in ("confirmation", "stop", "risk", "entry", "exit"):
        raise ValueError(
            "confirmation profiles require the confirmation, stop, risk, entry or exit stage"
        )
    if stage in ("stop", "risk", "entry", "exit") and profile == "standard":
        raise ValueError(f"{stage} requires a fixed confirmation profile")
    expected_raw = (
        generate_observations(observations)
        if profile == "standard"
        else generate_confirmation_fixture(profile, observations)
    )
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("invalid bundle directory")
    chunk_dir = bundle / "chunks"
    if chunk_dir.is_symlink() or not chunk_dir.is_dir():
        raise ValueError("invalid chunk directory")
    manifest_bytes = read_regular(bundle / "manifest.json", 1_000_000)
    manifest = json.loads(manifest_bytes)
    expected_manifest_fields = {
        "schema",
        "domain",
        "observations",
        "raw_bytes",
        "raw_sha256",
        "rows_per_chunk",
        "codec",
        "zlib_runtime",
        "chunks",
    }
    if profile != "standard":
        expected_manifest_fields.add("profile")
    if (
        type(manifest) is not dict
        or canonical(manifest) != manifest_bytes
        or set(manifest) != expected_manifest_fields
    ):
        raise ValueError("invalid canonical bundle manifest")
    rows = expected_raw.splitlines(keepends=True)
    if (
        manifest["schema"] != (SCHEMA if profile == "standard" else CONFIRMATION_BUNDLE_SCHEMA)
        or (profile != "standard" and manifest["profile"] != profile)
        or manifest["domain"] != "INVENTED_GENERATOR_ONLY"
        or type(manifest["observations"]) is not int
        or manifest["observations"] != observations
        or type(manifest["raw_bytes"]) is not int
        or manifest["raw_bytes"] != len(expected_raw)
        or manifest["raw_sha256"] != sha(expected_raw)
        or type(manifest["rows_per_chunk"]) is not int
        or manifest["rows_per_chunk"] != ROWS_PER_CHUNK
        or manifest["codec"] != "ZLIB_LEVEL_9"
        or manifest["zlib_runtime"] != zlib.ZLIB_RUNTIME_VERSION
        or type(manifest["chunks"]) is not list
    ):
        raise ValueError("bundle identity mismatch")
    expected_count = (observations + ROWS_PER_CHUNK - 1) // ROWS_PER_CHUNK
    if len(manifest["chunks"]) != expected_count:
        raise ValueError("wrong chunk count")
    expected_names = {f"{i:04d}.zlib" for i in range(expected_count)}
    if set(os.listdir(chunk_dir)) != expected_names:
        raise ValueError("unexpected chunk inventory")
    for ordinal, entry in enumerate(manifest["chunks"]):
        if type(entry) is not dict or set(entry) != {
            "name",
            "first_row",
            "rows",
            "raw_bytes",
            "raw_sha256",
            "stored_bytes",
            "stored_sha256",
        }:
            raise ValueError("invalid chunk descriptor")
        start = ordinal * ROWS_PER_CHUNK
        section = rows[start : start + ROWS_PER_CHUNK]
        expected = b"".join(section)
        name = f"{ordinal:04d}.zlib"
        if (
            entry["name"] != name
            or type(entry["first_row"]) is not int
            or entry["first_row"] != start
            or type(entry["rows"]) is not int
            or entry["rows"] != len(section)
            or type(entry["raw_bytes"]) is not int
            or entry["raw_bytes"] != len(expected)
            or entry["raw_sha256"] != sha(expected)
            or type(entry["stored_bytes"]) is not int
            or not 0 < entry["stored_bytes"] <= ROWS_PER_CHUNK * 128 + 1_024
        ):
            raise ValueError("chunk identity mismatch")
        stored = read_regular(chunk_dir / name, ROWS_PER_CHUNK * 128 + 1_024)
        if len(stored) != entry["stored_bytes"] or sha(stored) != entry["stored_sha256"]:
            raise ValueError("stored chunk digest mismatch")
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(stored, len(expected) + 1)
        if not decoder.eof or decoder.unused_data or decoder.unconsumed_tail or decoded != expected:
            raise ValueError("decoded chunk differs from generated source")
    worker_bytes = read_regular(bundle / "worker.json", 1_000_000)
    worker = json.loads(worker_bytes)
    if type(worker) is not dict or canonical(worker) != worker_bytes:
        raise ValueError("invalid canonical worker output")
    if stage == "events":
        repeated = recompute_events(expected_raw)
    elif stage == "pullback":
        repeated = recompute_pullback_events(expected_raw)
    elif stage == "confirmation":
        repeated = recompute_confirmation_events(expected_raw)
    elif stage == "stop":
        repeated = recompute_stop_events(expected_raw)
    elif stage == "risk":
        repeated = reconstruct_risk_native(expected_raw)
    elif stage == "entry":
        repeated = reconstruct_entry_native(expected_raw)
    else:
        repeated = reconstruct_exit_native(expected_raw)
    if (
        worker.get("schema") != "agicore:invented-storage-replay-worker:v2"
        or worker.get("domain") != "SYNTHETIC_ONLY"
        or worker.get("stage", "events") != stage
        or worker.get("manifest_sha256") != sha(manifest_bytes)
        or worker.get("input_sha256") != sha(expected_raw)
        or worker.get("profile", "standard") != profile
        or (profile == "standard" and "profile" in worker)
        or any(
            type(worker.get(field)) is not int or worker[field] < 0
            for field in ("storage_wall_ns", "replay_wall_ns", "peak_rss_bytes")
        )
        or type(worker.get("replay")) is not dict
        or canonical(worker["replay"]) != canonical(repeated)
    ):
        raise ValueError("worker output does not match independent verification")
    receipt = {
        "schema": "agicore:invented-storage-replay-verification:v2",
        "status": "PASS",
        "observations": observations,
        "stage": stage,
        "input_sha256": sha(expected_raw),
        "manifest_sha256": sha(manifest_bytes),
        "replay": repeated,
        "scope": "INDEPENDENT_BUNDLE_AND_EVENT_PIPELINE_SHARED_FROZEN_PREDICATES",
    }
    if profile != "standard":
        receipt["profile"] = profile
    with (bundle / "verification.json").open("xb") as stream:
        stream.write(canonical(receipt))
    return receipt


def main() -> None:
    """Run the bundle verifier in a separate process."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--observations", type=int, required=True)
    parser.add_argument(
        "--stage",
        choices=("events", "pullback", "confirmation", "stop", "risk", "entry", "exit"),
        default="events",
    )
    parser.add_argument(
        "--profile", choices=("standard", *CONFIRMATION_PROFILES), default="standard"
    )
    args = parser.parse_args()
    verify(args.bundle, args.observations, stage=args.stage, profile=args.profile)


if __name__ == "__main__":
    main()
