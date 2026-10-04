"""Deterministic offline STOP_MARKET protection of the immutable V2 stop.

Entry breaches exit at the existing entry Open. Later opening gaps are tested
before the adverse extreme; intrabar touches fill the fixed structural level.
No broker, costs, other exits, time expiration or position policy is involved.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum
from fractions import Fraction
from typing import Protocol

from .ema20_pullback_v2 import _exact_price
from .ema_pullback_entry_confirmation_v2 import EntryConfirmationRecordV2
from .ema_pullback_entry_execution_v2 import _confirmation_key
from .ema_pullback_initial_stop_v2 import (
    InitialStopAtEntryV2,
    InitialStopBookV2,
    InitialStopStateV2,
    _valid_utc,
)
from .regime_context_v2 import RegimeDirection, RegimeEventType

STOP_ORDER_SEMANTICS = "STOP_MARKET"
STOP_TOUCH_IS_TRIGGER = True
STOP_EXPIRES_ON_TIME_GAP = False
STOP_EXPIRES_AT_SESSION_BOUNDARY = False


class StructuralStopExecutionV2Error(ValueError):
    """Refuse unknown or changed initial-stop/entry provenance."""


class StructuralStopExecutionStateV2(StrEnum):
    """ARMED until one terminal fill or an irreversible observation failure."""

    ARMED = "ARMED"
    FILLED_STOP = "FILLED_STOP"
    FAILED_INCOMPLETE_STOP_OBSERVATION = "FAILED_INCOMPLETE_STOP_OBSERVATION"
    FAILED_INVALID_STOP_OBSERVATION = "FAILED_INVALID_STOP_OBSERVATION"


class StructuralStopExecutionStatusV2(StrEnum):
    """Failures never imply that the stop was untouched during missing data."""

    NOT_EVALUATED = "NOT_EVALUATED"
    EVALUATED = "EVALUATED"
    FAILED_INCOMPLETE_STOP_OBSERVATION = "FAILED_INCOMPLETE_STOP_OBSERVATION"
    FAILED_INVALID_STOP_OBSERVATION = "FAILED_INVALID_STOP_OBSERVATION"


class StructuralStopTriggerPhaseV2(StrEnum):
    """Opening fills are known at Open; OHLC touches have unknown intrabar time."""

    ENTRY_OPEN = "ENTRY_OPEN"
    BAR_OPEN_GAP = "BAR_OPEN_GAP"
    INTRABAR = "INTRABAR"


class ProtectiveStopActionV2(StrEnum):
    """Offline protective-action labels only; no order is submitted."""

    SELL = "SELL"
    BUY_TO_COVER = "BUY_TO_COVER"


class StructuralStopOpenInputV2(Protocol):
    """Opening metadata and price; no range is needed for an opening gap."""

    bar_index: int
    timestamp_utc: datetime
    open: object


class LongStopObservationInputV2(StructuralStopOpenInputV2, Protocol):
    """Only Low can be consulted after a LONG opening gap has been excluded."""

    low: object


class ShortStopObservationInputV2(StructuralStopOpenInputV2, Protocol):
    """Only High can be consulted after a SHORT opening gap has been excluded."""

    high: object


@dataclass(frozen=True)
class StructuralStopFillRecordV2:
    """Exact base exit and immutable event/pullback/confirmation/entry/stop chain."""

    source_regime_event_types: tuple[RegimeEventType, ...]
    source_regime_event_bar_index: int
    source_regime_event_timestamp: datetime
    source_regime_event_direction: RegimeDirection
    pullback_bar_index: int
    pullback_timestamp: datetime
    ema_reference: Fraction
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    entry_bar_index: int
    entry_bar_timestamp: datetime
    entry_price: Fraction
    initial_stop_price: Fraction
    structural_extreme: Fraction
    tick_size: Fraction
    stop_buffer_ticks: int
    stop_state_at_entry: InitialStopStateV2
    trigger_bar_index: int
    trigger_bar_timestamp: datetime
    trigger_phase: StructuralStopTriggerPhaseV2
    trigger_known_at: str
    base_stop_fill_price: Fraction
    protective_action: ProtectiveStopActionV2
    initial_stop_at_entry: InitialStopAtEntryV2
    exact_intrabar_timestamp: None = None
    order_semantics: str = STOP_ORDER_SEMANTICS


@dataclass(frozen=True)
class StructuralStopExecutionEvaluationV2:
    """Canonical monitoring state; end of data leaves an untriggered stop ARMED."""

    initial_stop_at_entry: InitialStopAtEntryV2
    stop_execution_state: StructuralStopExecutionStateV2 = StructuralStopExecutionStateV2.ARMED
    status: StructuralStopExecutionStatusV2 = StructuralStopExecutionStatusV2.NOT_EVALUATED
    last_observed_bar_index: int | None = None
    last_observed_bar_timestamp: datetime | None = None
    fill: StructuralStopFillRecordV2 | None = None

    @property
    def monitoring_first_bar(self) -> int:
        """Protect the entry bar itself after its already-filled Open."""
        return self.initial_stop_at_entry.entry_bar_index

    @property
    def next_observation_bar_index(self) -> int:
        """Do not infer an untouched stop over any skipped indexed observation."""
        return (
            self.monitoring_first_bar
            if self.last_observed_bar_index is None
            else self.last_observed_bar_index + 1
        )

    @property
    def stop_triggered(self) -> bool:
        """An invalid observation never produces a synthetic trigger or fill."""
        return (
            self.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP
            and self.fill is not None
        )


def _source_confirmation(source: InitialStopAtEntryV2) -> EntryConfirmationRecordV2:
    return source.initial_stop_record.confirmation


@dataclass(frozen=True)
class StructuralStopExecutionBookV2:
    """One offline series' immutable monitoring history; carry the returned book."""

    entries: tuple[StructuralStopExecutionEvaluationV2, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, StructuralStopExecutionEvaluationV2) for entry in self.entries
        ):
            raise StructuralStopExecutionV2Error(
                "stop execution history must be an immutable tuple"
            )
        keys = [
            _confirmation_key(_source_confirmation(entry.initial_stop_at_entry))
            for entry in self.entries
        ]
        if len(set(keys)) != len(keys):
            raise StructuralStopExecutionV2Error(
                "stop execution history must not duplicate a confirmation"
            )

    def for_confirmation(
        self, confirmation: EntryConfirmationRecordV2
    ) -> StructuralStopExecutionEvaluationV2:
        """Retrieve the canonical stop execution, rejecting changed or unknown sources."""
        if not isinstance(confirmation, EntryConfirmationRecordV2):
            raise StructuralStopExecutionV2Error("lookup requires an entry confirmation record")
        key = _confirmation_key(confirmation)
        for entry in self.entries:
            original = _source_confirmation(entry.initial_stop_at_entry)
            if _confirmation_key(original) == key:
                if original != confirmation:
                    raise StructuralStopExecutionV2Error(
                        "registered confirmation provenance cannot change"
                    )
                return entry
        raise StructuralStopExecutionV2Error("initial stop must be registered after its entry fill")


def _fill_stop(
    previous: StructuralStopExecutionEvaluationV2,
    index: int,
    timestamp: datetime,
    phase: StructuralStopTriggerPhaseV2,
    price: Fraction,
) -> StructuralStopExecutionEvaluationV2:
    bound = previous.initial_stop_at_entry
    stop = bound.initial_stop_record
    fill = StructuralStopFillRecordV2(
        source_regime_event_types=stop.source_regime_event_types,
        source_regime_event_bar_index=stop.source_regime_event_bar_index,
        source_regime_event_timestamp=stop.source_regime_event_timestamp,
        source_regime_event_direction=stop.source_regime_event_direction,
        pullback_bar_index=stop.pullback_bar_index,
        pullback_timestamp=stop.pullback_timestamp,
        ema_reference=stop.ema_reference,
        confirmation_bar_index=stop.confirmation_bar_index,
        confirmation_timestamp=stop.confirmation_timestamp,
        entry_bar_index=bound.entry_bar_index,
        entry_bar_timestamp=bound.entry_bar_timestamp,
        entry_price=bound.entry_price,
        initial_stop_price=stop.initial_stop_price,
        structural_extreme=stop.structural_extreme,
        tick_size=stop.tick_size,
        stop_buffer_ticks=stop.stop_buffer_ticks,
        stop_state_at_entry=bound.stop_state,
        trigger_bar_index=index,
        trigger_bar_timestamp=timestamp,
        trigger_phase=phase,
        trigger_known_at={
            StructuralStopTriggerPhaseV2.ENTRY_OPEN: "Open[e]",
            StructuralStopTriggerPhaseV2.BAR_OPEN_GAP: "Open[r]",
            StructuralStopTriggerPhaseV2.INTRABAR: "NO_LATER_THAN_CLOSE[r]",
        }[phase],
        base_stop_fill_price=price,
        protective_action=ProtectiveStopActionV2.SELL
        if stop.source_regime_event_direction is RegimeDirection.LONG
        else ProtectiveStopActionV2.BUY_TO_COVER,
        initial_stop_at_entry=bound,
    )
    return replace(
        previous,
        stop_execution_state=StructuralStopExecutionStateV2.FILLED_STOP,
        status=StructuralStopExecutionStatusV2.EVALUATED,
        last_observed_bar_index=index,
        last_observed_bar_timestamp=timestamp,
        fill=fill,
    )


def register_structural_stop_execution_v2(
    *,
    previous: StructuralStopExecutionBookV2,
    initial_stops: InitialStopBookV2,
    confirmation: EntryConfirmationRecordV2,
) -> StructuralStopExecutionBookV2:
    """Activate the PR #292 stop after entry, without reading any market bar.

    BREACHED_AT_ENTRY_OPEN fills immediately at the retained entry Open. The
    original entry stays FILLED. ARMED starts monitoring at e, not e+1.
    """
    if not isinstance(previous, StructuralStopExecutionBookV2) or not isinstance(
        initial_stops, InitialStopBookV2
    ):
        raise StructuralStopExecutionV2Error(
            "registration requires stop execution and initial stop books"
        )
    evaluation = initial_stops.for_confirmation(confirmation)
    bound = evaluation.at_entry
    if bound is None:
        raise StructuralStopExecutionV2Error(
            "registration requires the initial stop bound to its entry fill"
        )
    stop, entry = bound.initial_stop_record, bound.execution
    direction = stop.source_regime_event_direction
    if (
        stop != evaluation.initial_stop_record
        or stop.confirmation != confirmation
        or entry.confirmation != confirmation
        or bound.entry_bar_index != stop.confirmation_bar_index + 1
        or bound.entry_bar_index != entry.execution_bar_index
        or bound.entry_bar_timestamp != entry.execution_bar_timestamp
        or bound.entry_price != entry.execution_price_before_costs
        or direction is not entry.execution_side
        or not isinstance(stop.initial_stop_price, Fraction)
        or not isinstance(bound.entry_price, Fraction)
    ):
        raise StructuralStopExecutionV2Error(
            "initial stop and entry must retain their qualified provenance"
        )
    armed = (
        stop.initial_stop_price < bound.entry_price
        if direction is RegimeDirection.LONG
        else stop.initial_stop_price > bound.entry_price
    )
    if bound.stop_state is not (
        InitialStopStateV2.ARMED if armed else InitialStopStateV2.BREACHED_AT_ENTRY_OPEN
    ):
        raise StructuralStopExecutionV2Error("stop state must match its immutable entry relation")
    for existing in previous.entries:
        if _confirmation_key(
            _source_confirmation(existing.initial_stop_at_entry)
        ) == _confirmation_key(confirmation):
            previous.for_confirmation(confirmation)
            if existing.initial_stop_at_entry != bound:
                raise StructuralStopExecutionV2Error(
                    "registered initial stop or entry provenance cannot change"
                )
            return previous
    registered = StructuralStopExecutionEvaluationV2(bound)
    if bound.stop_state is InitialStopStateV2.BREACHED_AT_ENTRY_OPEN:
        registered = _fill_stop(
            registered,
            bound.entry_bar_index,
            bound.entry_bar_timestamp,
            StructuralStopTriggerPhaseV2.ENTRY_OPEN,
            bound.entry_price,
        )
    return StructuralStopExecutionBookV2((*previous.entries, registered))


def _observe_stop(
    previous: StructuralStopExecutionEvaluationV2,
    observation: LongStopObservationInputV2 | ShortStopObservationInputV2 | None,
) -> StructuralStopExecutionEvaluationV2:
    if (
        previous.stop_execution_state is not StructuralStopExecutionStateV2.ARMED
        or observation is None
    ):
        return previous

    def failure(incomplete=False):
        return replace(
            previous,
            stop_execution_state=StructuralStopExecutionStateV2.FAILED_INCOMPLETE_STOP_OBSERVATION
            if incomplete
            else StructuralStopExecutionStateV2.FAILED_INVALID_STOP_OBSERVATION,
            status=StructuralStopExecutionStatusV2.FAILED_INCOMPLETE_STOP_OBSERVATION
            if incomplete
            else StructuralStopExecutionStatusV2.FAILED_INVALID_STOP_OBSERVATION,
        )

    index = getattr(observation, "bar_index", None)
    if type(index) is not int or index < 0:
        return failure()
    expected = previous.next_observation_bar_index
    if index > expected:
        return failure(incomplete=True)
    if index < expected:
        return failure()
    timestamp = getattr(observation, "timestamp_utc", None)
    bound = previous.initial_stop_at_entry
    if (
        not _valid_utc(timestamp)
        or (index == bound.entry_bar_index and timestamp != bound.entry_bar_timestamp)
        or (
            previous.last_observed_bar_timestamp is not None
            and timestamp <= previous.last_observed_bar_timestamp
        )
    ):
        return failure()
    is_long = bound.initial_stop_record.source_regime_event_direction is RegimeDirection.LONG
    level = bound.initial_stop_record.initial_stop_price
    if index == bound.entry_bar_index:
        opening = bound.entry_price  # Open[e] is already known; no second entry-gap test.
    else:
        opening = _exact_price(getattr(observation, "open", None))
        if opening is None:
            return failure()
        if opening <= level if is_long else opening >= level:
            return _fill_stop(
                previous, index, timestamp, StructuralStopTriggerPhaseV2.BAR_OPEN_GAP, opening
            )
    adverse = _exact_price(getattr(observation, "low" if is_long else "high", None))
    if adverse is None or (adverse > opening if is_long else adverse < opening):
        return failure()
    if adverse <= level if is_long else adverse >= level:
        return _fill_stop(previous, index, timestamp, StructuralStopTriggerPhaseV2.INTRABAR, level)
    return replace(
        previous,
        status=StructuralStopExecutionStatusV2.EVALUATED,
        last_observed_bar_index=index,
        last_observed_bar_timestamp=timestamp,
    )


def observe_structural_stop_v2(
    *,
    previous: StructuralStopExecutionBookV2,
    confirmation: EntryConfirmationRecordV2,
    observation: LongStopObservationInputV2 | ShortStopObservationInputV2 | None,
) -> StructuralStopExecutionBookV2:
    """Process the next indexed bar, gap first, then its known adverse extreme.

    An opening-gap result never reads an extreme. Otherwise the caller must
    supply the bar's completed adverse-range observation; no exact touch time
    is inferred. None denotes end of available observations and leaves ARMED
    unchanged. Terminal states return without reading any market attribute.
    """
    if not isinstance(previous, StructuralStopExecutionBookV2):
        raise StructuralStopExecutionV2Error("observation requires the current stop execution book")
    existing = previous.for_confirmation(confirmation)
    advanced = _observe_stop(existing, observation)
    if advanced is existing:
        return previous
    return StructuralStopExecutionBookV2(
        tuple(advanced if entry is existing else entry for entry in previous.entries)
    )
