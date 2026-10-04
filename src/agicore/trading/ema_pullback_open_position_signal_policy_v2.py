"""One offline V2 position per strategy/series, with admission before context creation.

Entry/stop fills retain their frozen semantics. This boundary owns no indicator,
broker, quantity, costs or additional exit. Carry one immutable book per scope;
suppressed raw events are audit records and never actionable deferred signals.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum

from .ema20_pullback_v2 import (
    EMA20PullbackBarV2,
    EMA20PullbackContextEvaluationV2,
    advance_ema20_pullback_v2,
)
from .ema_pullback_entry_confirmation_v2 import EntryConfirmationRecordV2
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionRecordV2,
    EntryExecutionStateV2,
    _confirmation_key,
    _valid_utc,
)
from .ema_pullback_exit_policy_v2 import EMA20ExitFillRecordV2
from .ema_pullback_initial_stop_v2 import InitialStopAtEntryV2
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    LongStopObservationInputV2,
    ShortStopObservationInputV2,
    StructuralStopExecutionBookV2,
    StructuralStopExecutionEvaluationV2,
    StructuralStopExecutionStateV2,
    StructuralStopFillRecordV2,
    StructuralStopTriggerPhaseV2,
    observe_structural_stop_v2,
)
from .regime_context_v2 import (
    RegimeContextEvaluation,
    RegimeContextLifetimeEvaluation,
    RegimeContextLifetimeState,
    RegimeContextStatus,
    RegimeDirection,
    RegimeEvent,
    RegimeEventContextV2,
    RegimeEventType,
    compose_regime_context_v2,
)

MAX_SIMULTANEOUS_POSITIONS_PER_SERIES = 1
PYRAMIDING = False
HEDGING = False
FLIP_ON_OPPOSITE_SIGNAL = False
SCALE_IN = False
SIGNAL_QUEUE_WHILE_OPEN = False


class OpenPositionSignalPolicyV2Error(ValueError):
    """Reject an inconsistent series history, noncausal fill or bypassed admission."""


class PositionStateV2(StrEnum):
    """Only terminal entry/exit fills change the position state."""

    FLAT = "FLAT"
    OPEN_LONG = "OPEN_LONG"
    OPEN_SHORT = "OPEN_SHORT"


class PositionSignalAdmissionStatusV2(StrEnum):
    """Raw composition remains traceable even when no context may be created."""

    NO_REGIME_EVENT = "NO_REGIME_EVENT"
    ADMITTED = "ADMITTED"
    AMBIGUOUS = "AMBIGUOUS"
    SUPPRESSED_POSITION_OPEN = "SUPPRESSED_POSITION_OPEN"


@dataclass(frozen=True)
class PositionSignalSuppressionV2:
    """Non-actionable telemetry; this record is never an execution source."""

    signal_bar_index: int
    signal_timestamp: datetime
    signal_direction: RegimeDirection
    source_event_types: tuple[RegimeEventType, ...]
    position_state: PositionStateV2
    active_position_entry_bar_index: int
    active_position_direction: RegimeDirection
    suppression_reason: str = "POSITION_ALREADY_OPEN"


@dataclass(frozen=True)
class PositionSignalDecisionV2:
    """Admission at a single Close, after the existing position's exit resolution."""

    composition: RegimeContextEvaluation
    position_state_at_signal_decision: PositionStateV2
    status: PositionSignalAdmissionStatusV2
    suppressions: tuple[PositionSignalSuppressionV2, ...] = ()
    pullback: EMA20PullbackContextEvaluationV2 | None = None


@dataclass(frozen=True)
class PositionRecordV2:
    """Actual entry followed, at most once, by a formal stop or EMA20 exit fill."""

    entry: EntryExecutionRecordV2
    initial_stop_at_entry: InitialStopAtEntryV2
    exit: StructuralStopFillRecordV2 | EMA20ExitFillRecordV2 | None = None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.entry, EntryExecutionRecordV2)
            or not isinstance(self.initial_stop_at_entry, InitialStopAtEntryV2)
            or self.initial_stop_at_entry.execution != self.entry
        ):
            raise OpenPositionSignalPolicyV2Error("position requires the actual entry/stop link")
        if self.exit is not None and (
            not isinstance(self.exit, (StructuralStopFillRecordV2, EMA20ExitFillRecordV2))
            or self.exit.initial_stop_at_entry != self.initial_stop_at_entry
            or self.exit_bar_index < self.entry.execution_bar_index
        ):
            raise OpenPositionSignalPolicyV2Error("exit must retain the position's provenance")

    @property
    def exit_bar_index(self) -> int | None:
        """The actual terminal fill bar, independent of the formal exit type."""
        if isinstance(self.exit, EMA20ExitFillRecordV2):
            return self.exit.exit_execution_bar_index
        return None if self.exit is None else self.exit.trigger_bar_index

    @property
    def exit_timestamp(self) -> datetime | None:
        """The actual exit bar clock; no exact intrabar stop time is invented."""
        if isinstance(self.exit, EMA20ExitFillRecordV2):
            return self.exit.exit_execution_timestamp
        return None if self.exit is None else self.exit.trigger_bar_timestamp

    @property
    def state(self) -> PositionStateV2:
        """A breached entry still exists, then becomes FLAT only through its exit fill."""
        if self.exit is not None:
            return PositionStateV2.FLAT
        return (
            PositionStateV2.OPEN_LONG
            if self.entry.execution_side is RegimeDirection.LONG
            else PositionStateV2.OPEN_SHORT
        )


@dataclass(frozen=True)
class OpenPositionSignalPolicyBookV2:
    """One strategy instance and one instrument/series; no global exposure policy.

    Admissions preserve raw telemetry and exact consumed pullbacks. Entering a
    position clears the executable lifetime; exiting cannot restore that source.
    There is no queue, quantity, average entry price or pending reverse order.
    """

    strategy_instance_id: str
    series_id: str
    positions: tuple[PositionRecordV2, ...] = ()
    signal_decisions: tuple[PositionSignalDecisionV2, ...] = ()
    lifetime: RegimeContextLifetimeEvaluation | None = None
    active_stop: StructuralStopExecutionEvaluationV2 | None = None

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.strategy_instance_id, self.series_id)
        ):
            raise OpenPositionSignalPolicyV2Error("strategy instance and series must be named")
        if not isinstance(self.positions, tuple) or not all(
            isinstance(position, PositionRecordV2) for position in self.positions
        ):
            raise OpenPositionSignalPolicyV2Error("positions must be an immutable history")
        keys = [_confirmation_key(position.entry.confirmation) for position in self.positions]
        if len(keys) != len(set(keys)):
            raise OpenPositionSignalPolicyV2Error("a fill cannot create a second position")
        for earlier, later in zip(self.positions, self.positions[1:], strict=False):
            if (
                earlier.exit is None
                or later.entry.execution_bar_index <= earlier.exit_bar_index
                or later.entry.execution_bar_timestamp <= earlier.exit_timestamp
            ):
                raise OpenPositionSignalPolicyV2Error("positions cannot overlap or go backward")
        if not isinstance(self.signal_decisions, tuple) or not all(
            isinstance(decision, PositionSignalDecisionV2) for decision in self.signal_decisions
        ):
            raise OpenPositionSignalPolicyV2Error("signal decisions must be an immutable history")
        for earlier, later in zip(self.signal_decisions, self.signal_decisions[1:], strict=False):
            if (
                later.composition.closed_bar_index <= earlier.composition.closed_bar_index
                or later.composition.closed_bar_timestamp
                <= earlier.composition.closed_bar_timestamp
            ):
                raise OpenPositionSignalPolicyV2Error("signal decisions must advance causally")
        if self.active_position is None:
            if self.active_stop is not None:
                raise OpenPositionSignalPolicyV2Error("FLAT cannot retain an active position stop")
        elif (
            self.lifetime is not None
            or not isinstance(self.active_stop, StructuralStopExecutionEvaluationV2)
            or self.active_stop.initial_stop_at_entry != self.active_position.initial_stop_at_entry
        ):
            raise OpenPositionSignalPolicyV2Error("open position must block executable context")

    @property
    def active_position(self) -> PositionRecordV2 | None:
        """At most the last actual position can remain open."""
        return self.positions[-1] if self.positions and self.positions[-1].exit is None else None

    @property
    def position_state(self) -> PositionStateV2:
        return (
            self.active_position.state if self.active_position is not None else PositionStateV2.FLAT
        )

    @property
    def context(self) -> RegimeEventContextV2 | None:
        """Suppressed events never construct even an inactive context record."""
        return self.lifetime.context if self.lifetime is not None else None


def _require_book(previous: OpenPositionSignalPolicyBookV2) -> None:
    if not isinstance(previous, OpenPositionSignalPolicyBookV2):
        raise OpenPositionSignalPolicyV2Error("carry the current strategy/series policy book")


def _require_clock(index: int, timestamp: datetime) -> None:
    if type(index) is not int or index < 0 or not _valid_utc(timestamp):
        raise OpenPositionSignalPolicyV2Error(
            "observation requires a nonnegative index and UTC clock"
        )


def _require_admitted_pullback(
    previous: OpenPositionSignalPolicyBookV2, confirmation: EntryConfirmationRecordV2
) -> None:
    for decision in previous.signal_decisions:
        if decision.composition.closed_bar_index != confirmation.pullback_bar_index:
            continue
        candidate = decision.pullback
        if (
            candidate is None
            or candidate.pullback is None
            or not candidate.pullback.pullback_qualified
        ):
            break
        context = candidate.lifetime.context
        if (
            context.state is RegimeContextLifetimeState.CONSUMED
            and context.source_event_types == confirmation.source_regime_event_types
            and context.source_event_direction is confirmation.source_regime_event_direction
            and context.source_event_bar_index == confirmation.source_regime_event_bar_index
            and context.source_event_timestamp == confirmation.source_regime_event_timestamp
            and context.pullback_bar_index == confirmation.pullback_bar_index
            and context.pullback_timestamp == confirmation.pullback_timestamp
            and context.ema_reference == confirmation.ema_reference
            and (
                not previous.positions
                or confirmation.source_regime_event_bar_index
                >= previous.positions[-1].exit_bar_index
            )
        ):
            return
        break
    raise OpenPositionSignalPolicyV2Error("entry requires a fresh admitted and consumed source")


def apply_position_entry_fill_v2(
    *,
    previous: OpenPositionSignalPolicyBookV2,
    executions: EntryExecutionBookV2,
    stops: StructuralStopExecutionBookV2,
    confirmation: EntryConfirmationRecordV2,
) -> OpenPositionSignalPolicyBookV2:
    """Open only from canonical FILLED at q+1, never from a signal or pending state.

    The previous policy decision must be Close[q]. Its own admitted/consumed
    pullback is required, preventing injection of an externally queued chain.
    A repeated canonical fill, including after its exit, cannot reopen it.
    """
    _require_book(previous)
    if not isinstance(executions, EntryExecutionBookV2):
        raise OpenPositionSignalPolicyV2Error("entry requires the canonical execution book")
    execution = executions.for_confirmation(confirmation)
    if execution.execution_state is not EntryExecutionStateV2.FILLED:
        return previous
    fill = execution.execution
    if not isinstance(fill, EntryExecutionRecordV2) or fill.confirmation != confirmation:
        raise OpenPositionSignalPolicyV2Error("FILLED must contain its immutable entry record")
    for position in previous.positions:
        if _confirmation_key(position.entry.confirmation) == _confirmation_key(confirmation):
            if position.entry != fill:
                raise OpenPositionSignalPolicyV2Error("existing fill provenance cannot change")
            return previous
    if previous.position_state is not PositionStateV2.FLAT:
        raise OpenPositionSignalPolicyV2Error("another fill would violate the one-position policy")
    if not previous.signal_decisions or (
        previous.signal_decisions[-1].composition.closed_bar_index
        != confirmation.confirmation_bar_index
        or previous.signal_decisions[-1].composition.closed_bar_timestamp
        != confirmation.confirmation_timestamp
        or fill.execution_bar_index != confirmation.confirmation_bar_index + 1
        or fill.execution_bar_timestamp <= confirmation.confirmation_timestamp
    ):
        raise OpenPositionSignalPolicyV2Error("entry must follow its known confirmation Close")
    _require_admitted_pullback(previous, confirmation)
    if not isinstance(stops, StructuralStopExecutionBookV2):
        raise OpenPositionSignalPolicyV2Error("entry requires its registered structural stop")
    stop = stops.for_confirmation(confirmation)
    if stop.initial_stop_at_entry.execution != fill:
        raise OpenPositionSignalPolicyV2Error("entry/stop provenance must match exactly")
    if not (
        (
            stop.stop_execution_state is StructuralStopExecutionStateV2.ARMED
            and stop.last_observed_bar_index is None
            and stop.last_observed_bar_timestamp is None
        )
        or (
            stop.stop_execution_state is StructuralStopExecutionStateV2.FILLED_STOP
            and stop.fill is not None
            and stop.fill.trigger_phase is StructuralStopTriggerPhaseV2.ENTRY_OPEN
            and stop.fill.trigger_bar_index == fill.execution_bar_index
            and stop.fill.trigger_bar_timestamp == fill.execution_bar_timestamp
        )
    ):
        raise OpenPositionSignalPolicyV2Error(
            "only the stop state known at entry Open may be bound"
        )
    return replace(
        previous,
        positions=(*previous.positions, PositionRecordV2(fill, stop.initial_stop_at_entry)),
        lifetime=None,
        active_stop=stop,
    )


def resolve_position_stop_v2(
    *,
    previous: OpenPositionSignalPolicyBookV2,
    known_bar_index: int,
    known_bar_timestamp: datetime,
    observation: LongStopObservationInputV2 | ShortStopObservationInputV2 | None = None,
) -> OpenPositionSignalPolicyBookV2:
    """Resolve the existing stop before signal admission; only FILLED_STOP makes FLAT.

    A breached entry needs no market input and can be resolved at its same Open.
    Otherwise pass the current observation permitted by the frozen stop gate:
    an opening gap, or the available adverse range (no invented intrabar time).
    End of data and fail-closed monitoring errors never synthesize an exit.
    """
    _require_book(previous)
    position = previous.active_position
    if position is None:
        return previous
    _require_clock(known_bar_index, known_bar_timestamp)
    if previous.signal_decisions and (
        known_bar_index <= previous.signal_decisions[-1].composition.closed_bar_index
        or known_bar_timestamp <= previous.signal_decisions[-1].composition.closed_bar_timestamp
    ):
        raise OpenPositionSignalPolicyV2Error(
            "stop resolution must precede that bar's Close decision"
        )
    stop = previous.active_stop
    if stop.stop_execution_state is StructuralStopExecutionStateV2.ARMED:
        if observation is not None and (
            observation.bar_index != known_bar_index
            or observation.timestamp_utc != known_bar_timestamp
        ):
            raise OpenPositionSignalPolicyV2Error("stop observation must belong to the current bar")
        monitored = observe_structural_stop_v2(
            previous=StructuralStopExecutionBookV2((stop,)),
            confirmation=position.entry.confirmation,
            observation=observation,
        )
        stop = monitored.entries[0]
    if stop.stop_execution_state is not StructuralStopExecutionStateV2.FILLED_STOP:
        return previous if stop is previous.active_stop else replace(previous, active_stop=stop)
    fill = stop.fill
    if (
        not isinstance(fill, StructuralStopFillRecordV2)
        or fill.initial_stop_at_entry != position.initial_stop_at_entry
        or fill.trigger_bar_index != known_bar_index
        or fill.trigger_bar_timestamp != known_bar_timestamp
    ):
        raise OpenPositionSignalPolicyV2Error("exit fill must be causal and retain the exact entry")
    closed = replace(position, exit=fill)
    return replace(previous, positions=(*previous.positions[:-1], closed), active_stop=None)


def advance_open_position_signal_policy_v2(
    *,
    previous: OpenPositionSignalPolicyBookV2,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    stop_observation: LongStopObservationInputV2 | ShortStopObservationInputV2 | None = None,
    directional_impulse_event: RegimeEvent | None = None,
    reversal_transition_event: RegimeEvent | None = None,
) -> OpenPositionSignalPolicyBookV2:
    """Exit resolution -> position state -> Close regime admission -> formal pullback.

    OPEN never invokes the lifetime/pullback evaluator or reads its bar mapping.
    A new event at the Close of an exited bar may create a fresh context, whose
    own event bar remains ineligible under the already frozen lifetime gate.
    Identical repeated Close processing returns the current book without reads.
    """
    _require_book(previous)
    _require_clock(closed_bar_index, closed_bar_timestamp)
    if source_bar_closed is not True:
        raise OpenPositionSignalPolicyV2Error("signal admission requires the current closed bar")
    if previous.signal_decisions:
        latest = previous.signal_decisions[-1].composition
        if (
            closed_bar_index == latest.closed_bar_index
            and closed_bar_timestamp == latest.closed_bar_timestamp
        ):
            composition = compose_regime_context_v2(
                closed_bar_index=closed_bar_index,
                closed_bar_timestamp=closed_bar_timestamp,
                source_bar_closed=True,
                directional_impulse_event=directional_impulse_event,
                reversal_transition_event=reversal_transition_event,
            )
            if composition != latest:
                raise OpenPositionSignalPolicyV2Error(
                    "a processed Close cannot change its raw events"
                )
            return previous
        if (
            closed_bar_index <= latest.closed_bar_index
            or closed_bar_timestamp <= latest.closed_bar_timestamp
        ):
            raise OpenPositionSignalPolicyV2Error("signal Close decisions must strictly increase")
    resolved = resolve_position_stop_v2(
        previous=previous,
        known_bar_index=closed_bar_index,
        known_bar_timestamp=closed_bar_timestamp,
        observation=stop_observation,
    )
    composition = compose_regime_context_v2(
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=True,
        directional_impulse_event=directional_impulse_event,
        reversal_transition_event=reversal_transition_event,
    )
    position = resolved.active_position
    if position is not None:
        suppressions = tuple(
            PositionSignalSuppressionV2(
                closed_bar_index,
                closed_bar_timestamp,
                direction,
                tuple(
                    event.event_type
                    for event in composition.events
                    if event.event_direction is direction
                ),
                resolved.position_state,
                position.entry.execution_bar_index,
                position.entry.execution_side,
            )
            for direction in RegimeDirection
            if any(event.event_direction is direction for event in composition.events)
        )
        decision = PositionSignalDecisionV2(
            composition,
            resolved.position_state,
            PositionSignalAdmissionStatusV2.SUPPRESSED_POSITION_OPEN
            if composition.events
            else PositionSignalAdmissionStatusV2.NO_REGIME_EVENT,
            suppressions,
        )
        return replace(resolved, signal_decisions=(*resolved.signal_decisions, decision))
    pullback = advance_ema20_pullback_v2(
        previous=resolved.lifetime,
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=True,
        bars_by_index=bars_by_index,
        directional_impulse_event=directional_impulse_event,
        reversal_transition_event=reversal_transition_event,
    )
    status = {
        RegimeContextStatus.UNQUALIFIED: PositionSignalAdmissionStatusV2.NO_REGIME_EVENT,
        RegimeContextStatus.QUALIFIED: PositionSignalAdmissionStatusV2.ADMITTED,
        RegimeContextStatus.AMBIGUOUS: PositionSignalAdmissionStatusV2.AMBIGUOUS,
    }[composition.status]
    decision = PositionSignalDecisionV2(
        composition, PositionStateV2.FLAT, status, pullback=pullback
    )
    return replace(
        resolved,
        signal_decisions=(*resolved.signal_decisions, decision),
        lifetime=pullback.lifetime,
    )


__all__ = [
    "FLIP_ON_OPPOSITE_SIGNAL",
    "HEDGING",
    "MAX_SIMULTANEOUS_POSITIONS_PER_SERIES",
    "PYRAMIDING",
    "SCALE_IN",
    "SIGNAL_QUEUE_WHILE_OPEN",
    "OpenPositionSignalPolicyBookV2",
    "OpenPositionSignalPolicyV2Error",
    "PositionRecordV2",
    "PositionSignalAdmissionStatusV2",
    "PositionSignalDecisionV2",
    "PositionSignalSuppressionV2",
    "PositionStateV2",
    "advance_open_position_signal_policy_v2",
    "apply_position_entry_fill_v2",
    "resolve_position_stop_v2",
]
