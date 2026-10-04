"""Exact structural V2 stop known at Close[q], then immutable at entry.

Only closed High/Low observations in k..q calculate the level. An existing
offline entry fill subsequently classifies that fixed level; it never changes
the PR #291 execution rule or decides how a breached stop exits a position.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from fractions import Fraction
from typing import Protocol

from .ema20_pullback_v2 import _exact_price
from .ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationEvaluationV2,
    EntryConfirmationRecordV2,
)
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionRecordV2,
    EntryExecutionStateV2,
    EntryExecutionV2Error,
    _confirmation_key,
    _known_confirmation,
)
from .regime_context_v2 import RegimeDirection, RegimeEventType

TICK_SIZE = Fraction(1, 4)
STOP_BUFFER_TICKS = 1
STOP_BUFFER = TICK_SIZE * STOP_BUFFER_TICKS
STOP_KNOWN_AT = "Close[q]"
INITIAL_STOP_RECALCULATION = "FORBIDDEN"


class InitialStopV2Error(ValueError):
    """Reject inconsistent causal metadata or misuse of the immutable stop book."""


class InitialStopStatusV2(StrEnum):
    """Explicit outcomes of the structural window, before any entry exists."""

    EVALUATED = "EVALUATED"
    INVALID_STRUCTURAL_STOP_INPUT = "INVALID_STRUCTURAL_STOP_INPUT"
    INCOMPLETE_STRUCTURAL_STOP_WINDOW = "INCOMPLETE_STRUCTURAL_STOP_WINDOW"


class InitialStopStateV2(StrEnum):
    """Relation to the existing entry fill, without trigger or exit semantics."""

    ARMED = "ARMED"
    BREACHED_AT_ENTRY_OPEN = "BREACHED_AT_ENTRY_OPEN"


class StructuralStopBarInputV2(Protocol):
    """Closed structural observation; Open, Close and Volume are not read."""

    bar_index: int
    timestamp_utc: datetime
    is_closed: bool
    high: object
    low: object


@dataclass(frozen=True)
class InitialStopRecordV2:
    """Immutable exact level and qualified provenance, established at Close[q]."""

    source_regime_event_types: tuple[RegimeEventType, ...]
    source_regime_event_bar_index: int
    source_regime_event_timestamp: datetime
    source_regime_event_direction: RegimeDirection
    pullback_bar_index: int
    pullback_timestamp: datetime
    ema_reference: Fraction
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    structural_window_first_bar: int
    structural_window_last_bar: int
    structural_extreme: Fraction
    stop_buffer_ticks: int
    tick_size: Fraction
    initial_stop_price: Fraction
    stop_known_at_bar_index: int
    stop_known_at_timestamp: datetime
    confirmation: EntryConfirmationRecordV2


@dataclass(frozen=True)
class InitialStopAtEntryV2:
    """The same fixed stop bound to the PR #291 fill; no market bar is needed."""

    initial_stop_record: InitialStopRecordV2
    execution: EntryExecutionRecordV2
    entry_bar_index: int
    entry_bar_timestamp: datetime
    entry_price: Fraction
    stop_state: InitialStopStateV2


@dataclass(frozen=True)
class InitialStopEvaluationV2:
    """Fail-closed calculation, optionally bound to a subsequent offline fill."""

    confirmation: EntryConfirmationRecordV2
    status: InitialStopStatusV2
    initial_stop_record: InitialStopRecordV2 | None = None
    at_entry: InitialStopAtEntryV2 | None = None

    @property
    def initial_stop(self) -> Fraction | None:
        """A structural failure has no replacement stop."""
        return (
            None
            if self.initial_stop_record is None
            else self.initial_stop_record.initial_stop_price
        )

    @property
    def stop_state(self) -> InitialStopStateV2 | None:
        """ARMED/BREACHED are only known once a valid entry actually fills."""
        return None if self.at_entry is None else self.at_entry.stop_state


def _qualified_source(decision: EntryConfirmationEvaluationV2) -> EntryConfirmationRecordV2:
    try:
        record = _known_confirmation(decision)
    except EntryExecutionV2Error as error:
        raise InitialStopV2Error(str(error)) from error
    if record.confirmation_bar_index - record.pullback_bar_index not in (1, 2):
        raise InitialStopV2Error("confirmation must be k+1 or k+2")
    return record


def _valid_utc(value: object) -> bool:
    return (
        isinstance(value, datetime)
        and value.tzinfo is not None
        and value.utcoffset() == timedelta(0)
    )


def evaluate_initial_stop_v2(
    *,
    confirmation: EntryConfirmationEvaluationV2,
    bars_by_index: Mapping[int, StructuralStopBarInputV2],
) -> InitialStopEvaluationV2:
    """Calculate one Close[q] snapshot, accessing exactly k..q and no entry bar.

    Use register_initial_stop_v2 to retain the snapshot across repeated calls.
    All required indices are checked for completeness before price validation.
    No Open/Close/OHLC-body validation, positivity or distance filter is added.
    """
    source = _qualified_source(confirmation)
    k, q = source.pullback_bar_index, source.confirmation_bar_index
    window = [bars_by_index.get(index) for index in range(k, q + 1)]
    if any(bar is None for bar in window):
        return InitialStopEvaluationV2(
            source, InitialStopStatusV2.INCOMPLETE_STRUCTURAL_STOP_WINDOW
        )
    lows, highs = [], []
    previous_timestamp = None
    for index, bar in zip(range(k, q + 1), window, strict=True):
        timestamp = bar.timestamp_utc
        if (
            type(bar.bar_index) is not int
            or bar.bar_index != index
            or not _valid_utc(timestamp)
            or (previous_timestamp is not None and timestamp <= previous_timestamp)
            or (index == k and timestamp != source.pullback_timestamp)
            or (index == q and timestamp != source.confirmation_timestamp)
        ):
            raise InitialStopV2Error("structural window metadata must match closed k..q")
        if bar.is_closed is not True:
            return InitialStopEvaluationV2(
                source, InitialStopStatusV2.INVALID_STRUCTURAL_STOP_INPUT
            )
        high, low = _exact_price(bar.high), _exact_price(bar.low)
        if high is None or low is None or high < low:
            return InitialStopEvaluationV2(
                source, InitialStopStatusV2.INVALID_STRUCTURAL_STOP_INPUT
            )
        highs.append(high)
        lows.append(low)
        previous_timestamp = timestamp
    is_long = source.source_regime_event_direction is RegimeDirection.LONG
    extreme = min(lows) if is_long else max(highs)
    stop_price = extreme - STOP_BUFFER if is_long else extreme + STOP_BUFFER
    record = InitialStopRecordV2(
        source_regime_event_types=source.source_regime_event_types,
        source_regime_event_bar_index=source.source_regime_event_bar_index,
        source_regime_event_timestamp=source.source_regime_event_timestamp,
        source_regime_event_direction=source.source_regime_event_direction,
        pullback_bar_index=k,
        pullback_timestamp=source.pullback_timestamp,
        ema_reference=source.ema_reference,
        confirmation_bar_index=q,
        confirmation_timestamp=source.confirmation_timestamp,
        structural_window_first_bar=k,
        structural_window_last_bar=q,
        structural_extreme=extreme,
        stop_buffer_ticks=STOP_BUFFER_TICKS,
        tick_size=TICK_SIZE,
        initial_stop_price=stop_price,
        stop_known_at_bar_index=q,
        stop_known_at_timestamp=source.confirmation_timestamp,
        confirmation=source,
    )
    return InitialStopEvaluationV2(source, InitialStopStatusV2.EVALUATED, record)


@dataclass(frozen=True)
class InitialStopBookV2:
    """One offline series' retained Close[q] snapshots; carry the returned book.

    Equivalent registrations never read the structure again, including failed
    snapshots. Altering metadata under the same causal identity is rejected.
    """

    entries: tuple[InitialStopEvaluationV2, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, InitialStopEvaluationV2) for entry in self.entries
        ):
            raise InitialStopV2Error("stop history must be an immutable tuple of evaluations")
        keys = [_confirmation_key(entry.confirmation) for entry in self.entries]
        if len(set(keys)) != len(keys):
            raise InitialStopV2Error("stop history must not duplicate a confirmation")

    def for_confirmation(self, confirmation: EntryConfirmationRecordV2) -> InitialStopEvaluationV2:
        """Look up the original snapshot and refuse changed or unknown provenance."""
        if not isinstance(confirmation, EntryConfirmationRecordV2):
            raise InitialStopV2Error("lookup requires an entry confirmation record")
        key = _confirmation_key(confirmation)
        for entry in self.entries:
            if _confirmation_key(entry.confirmation) == key:
                if entry.confirmation != confirmation:
                    raise InitialStopV2Error("registered confirmation provenance cannot change")
                return entry
        raise InitialStopV2Error("stop must be registered at its qualified confirmation close")


def register_initial_stop_v2(
    *,
    previous: InitialStopBookV2,
    confirmation: EntryConfirmationEvaluationV2,
    bars_by_index: Mapping[int, StructuralStopBarInputV2],
) -> InitialStopBookV2:
    """Capture the closed structure once, without recalculation on repeated calls."""
    if not isinstance(previous, InitialStopBookV2):
        raise InitialStopV2Error("registration requires an initial stop book")
    source = _qualified_source(confirmation)
    for entry in previous.entries:
        if _confirmation_key(entry.confirmation) == _confirmation_key(source):
            previous.for_confirmation(source)
            return previous
    evaluation = evaluate_initial_stop_v2(confirmation=confirmation, bars_by_index=bars_by_index)
    return InitialStopBookV2((*previous.entries, evaluation))


def bind_initial_stop_to_entry_v2(
    *,
    previous: InitialStopBookV2,
    confirmation: EntryConfirmationRecordV2,
    executions: EntryExecutionBookV2,
) -> InitialStopBookV2:
    """Classify the fixed stop against a canonical fill, without any bar input.

    Pending/expired/failed executions do not arm a stop. An invalid structural
    snapshot remains unavailable; this gate neither synthesizes a substitute
    nor cancels a fill. BREACHED_AT_ENTRY_OPEN preserves FILLED unchanged.
    """
    if not isinstance(previous, InitialStopBookV2) or not isinstance(
        executions, EntryExecutionBookV2
    ):
        raise InitialStopV2Error("entry binding requires the stop and execution books")
    evaluation = previous.for_confirmation(confirmation)
    execution_state = executions.for_confirmation(confirmation)
    if execution_state.execution_state is not EntryExecutionStateV2.FILLED:
        return previous
    fill = execution_state.execution
    if fill is None or fill.confirmation != confirmation:
        raise InitialStopV2Error("a filled execution must retain its original confirmation")
    if evaluation.at_entry is not None:
        if evaluation.at_entry.execution != fill:
            raise InitialStopV2Error("entry binding cannot replace its immutable fill")
        return previous
    stop = evaluation.initial_stop_record
    if stop is None:
        return previous
    if (
        fill.execution_bar_index != stop.confirmation_bar_index + 1
        or fill.execution_side is not stop.source_regime_event_direction
        or fill.source_regime_event_types != stop.source_regime_event_types
        or fill.source_regime_event_bar_index != stop.source_regime_event_bar_index
        or fill.source_regime_event_timestamp != stop.source_regime_event_timestamp
        or fill.source_regime_event_direction is not stop.source_regime_event_direction
        or (fill.pullback_bar_index, fill.pullback_timestamp)
        != (stop.pullback_bar_index, stop.pullback_timestamp)
        or (fill.confirmation_bar_index, fill.confirmation_timestamp)
        != (stop.confirmation_bar_index, stop.confirmation_timestamp)
        or fill.ema_reference != stop.ema_reference
        or not isinstance(fill.execution_price_before_costs, Fraction)
    ):
        raise InitialStopV2Error("entry fill provenance must match the original structural stop")
    armed = (
        stop.initial_stop_price < fill.execution_price_before_costs
        if fill.execution_side is RegimeDirection.LONG
        else stop.initial_stop_price > fill.execution_price_before_costs
    )
    binding = InitialStopAtEntryV2(
        initial_stop_record=stop,
        execution=fill,
        entry_bar_index=fill.execution_bar_index,
        entry_bar_timestamp=fill.execution_bar_timestamp,
        entry_price=fill.execution_price_before_costs,
        stop_state=InitialStopStateV2.ARMED if armed else InitialStopStateV2.BREACHED_AT_ENTRY_OPEN,
    )
    updated = replace(evaluation, at_entry=binding)
    return InitialStopBookV2(
        tuple(updated if entry is evaluation else entry for entry in previous.entries)
    )
