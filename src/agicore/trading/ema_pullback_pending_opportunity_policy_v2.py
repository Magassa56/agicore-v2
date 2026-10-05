"""One causal pre-position lock per offline V2 strategy/series.

The first formal consumed pullback locks the series. Frozen confirmation, stop,
risk and execution gates own all their arithmetic and terminal rules. Raw regime
events are evaluated after pending resolution and retained separately from the
filtered events passed to the existing position/context admission gate.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from itertools import pairwise

from .ema20_pullback_v2 import EMA20PullbackBarV2
from .ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationEvaluationV2,
    EntryConfirmationStateV2,
    advance_entry_confirmation_momentum_v2,
    begin_entry_confirmation_momentum_v2,
)
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionEvaluationV2,
    EntryExecutionOpenInputV2,
    EntryExecutionStateV2,
)
from .ema_pullback_initial_stop_v2 import (
    InitialStopBookV2,
    bind_initial_stop_to_entry_v2,
    register_initial_stop_v2,
)
from .ema_pullback_open_position_signal_policy_v2 import (
    OpenPositionSignalPolicyBookV2,
    PositionStateV2,
    _require_clock,
    advance_open_position_signal_policy_v2,
    apply_position_entry_fill_v2,
    resolve_position_stop_v2,
)
from .ema_pullback_risk_position_sizing_v2 import (
    INSTRUMENT,
    RiskPositionSizingBookV2,
    RiskSizingDecisionRecordV2,
    RiskSizingDecisionV2,
    execute_risk_approved_entry_open_v2,
    register_risk_position_sizing_v2,
)
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    LongStopObservationInputV2,
    ShortStopObservationInputV2,
    StructuralStopExecutionBookV2,
    StructuralStopExecutionStateV2,
    register_structural_stop_execution_v2,
)
from .regime_context_v2 import (
    RegimeContextEvaluation,
    RegimeContextStatus,
    RegimeDirection,
    RegimeEvent,
    RegimeEventContextV2,
    RegimeEventType,
    compose_regime_context_v2,
)

MAX_ACTIONABLE_PENDING_OPPORTUNITIES_PER_SERIES = 1
PENDING_OPPORTUNITY_LOCK = "FIRST_CONSUMED_PULLBACK_LOCKS"
PENDING_OPPORTUNITY_QUEUE = False
PENDING_OPPORTUNITY_REPLACEMENT = False
OPPOSITE_EVENT_CANCELS_PENDING = False
SAME_DIRECTION_EVENT_REFRESHES_PENDING = False

RegimeEventsAtCloseV2 = Callable[[], tuple[RegimeEvent | None, RegimeEvent | None]]


class PendingOpportunityPolicyV2Error(ValueError):
    """Keep structural/noncausal failures closed, retaining the module evidence."""

    def __init__(self, message: str, *, module_result: object = None) -> None:
        super().__init__(message)
        self.module_result = module_result


class PendingOpportunityStateV2(StrEnum):
    """Series ownership and immutable opportunity outcomes; no signal queue."""

    IDLE = "IDLE"
    AWAITING_CONFIRMATION = "AWAITING_CONFIRMATION"
    PENDING_ENTRY_EXECUTION = "PENDING_ENTRY_EXECUTION"
    POSITION_OWNED = "POSITION_OWNED"
    TERMINAL_CONFIRMATION_EXPIRED = "TERMINAL_CONFIRMATION_EXPIRED"
    TERMINAL_RISK_REJECTED = "TERMINAL_RISK_REJECTED"
    TERMINAL_EXECUTION_NOT_FILLED = "TERMINAL_EXECUTION_NOT_FILLED"
    TERMINAL_INCOMPLETE_CONFIRMATION = "TERMINAL_INCOMPLETE_CONFIRMATION"


class PendingSignalAdmissionStatusV2(StrEnum):
    """Actual raw composition, independent of the filtered actionable inputs."""

    NO_REGIME_EVENT = "NO_REGIME_EVENT"
    ADMITTED = "ADMITTED"
    AMBIGUOUS = "AMBIGUOUS"
    SUPPRESSED_PENDING_OPPORTUNITY = "SUPPRESSED_PENDING_OPPORTUNITY"
    SUPPRESSED_POSITION_OPEN = "SUPPRESSED_POSITION_OPEN"


_PENDING = (
    PendingOpportunityStateV2.AWAITING_CONFIRMATION,
    PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION,
)
_CONFIRMATION_EXPIRED = (
    EntryConfirmationStateV2.EXPIRED_NO_ENTRY_CONFIRMATION,
    EntryConfirmationStateV2.EXPIRED_CONFIRMATION_ELAPSED_TIME,
)
_EXECUTION_EXPIRED = (
    EntryExecutionStateV2.EXPIRED_NO_EXECUTION,
    EntryExecutionStateV2.EXPIRED_EXECUTION_GAP,
)


@dataclass(frozen=True)
class PendingOpportunityRecordV2:
    """The original consumed source followed by its canonical frozen records."""

    state: PendingOpportunityStateV2
    confirmation: EntryConfirmationEvaluationV2
    risk_decision: RiskSizingDecisionRecordV2 | None = None
    execution: EntryExecutionEvaluationV2 | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.state, PendingOpportunityStateV2) or not isinstance(
            self.confirmation, EntryConfirmationEvaluationV2
        ):
            raise PendingOpportunityPolicyV2Error("opportunity requires formal confirmation state")
        confirmation_state = self.confirmation.state
        if self.state in (
            PendingOpportunityStateV2.AWAITING_CONFIRMATION,
            PendingOpportunityStateV2.TERMINAL_INCOMPLETE_CONFIRMATION,
        ):
            valid = (
                confirmation_state is EntryConfirmationStateV2.AWAITING_CONFIRMATION
                and self.risk_decision is None
                and self.execution is None
            )
        elif self.state is PendingOpportunityStateV2.TERMINAL_CONFIRMATION_EXPIRED:
            valid = (
                confirmation_state in _CONFIRMATION_EXPIRED
                and self.risk_decision is None
                and self.execution is None
            )
        else:
            valid = (
                self.confirmation.entry_confirmation
                and isinstance(self.risk_decision, RiskSizingDecisionRecordV2)
                and self.risk_decision.confirmation == self.confirmation.confirmation
                and self.risk_decision.consumed_context == self.consumed_context
            )
            if self.state is PendingOpportunityStateV2.TERMINAL_RISK_REJECTED:
                valid = (
                    valid
                    and self.risk_decision.decision is RiskSizingDecisionV2.REJECT
                    and self.execution is None
                )
            elif self.state in (
                PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION,
                PendingOpportunityStateV2.POSITION_OWNED,
                PendingOpportunityStateV2.TERMINAL_EXECUTION_NOT_FILLED,
            ):
                valid = (
                    valid
                    and self.risk_decision.decision is RiskSizingDecisionV2.APPROVE
                    and isinstance(self.execution, EntryExecutionEvaluationV2)
                    and self.execution.confirmation == self.confirmation.confirmation
                )
                expected = {
                    PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION: (
                        EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN,
                    ),
                    PendingOpportunityStateV2.POSITION_OWNED: (EntryExecutionStateV2.FILLED,),
                    PendingOpportunityStateV2.TERMINAL_EXECUTION_NOT_FILLED: _EXECUTION_EXPIRED,
                }[self.state]
                valid = valid and self.execution.execution_state in expected
            else:
                valid = False
        if not valid:
            raise PendingOpportunityPolicyV2Error("impossible pending opportunity transition")

    @property
    def consumed_context(self) -> RegimeEventContextV2:
        """The consumed source remains immutable even after terminal resolution."""
        return self.confirmation.opportunity.consumed_context


@dataclass(frozen=True)
class PendingSignalSuppressionV2:
    """Audit-only event metadata; it is never a source for another opportunity."""

    suppressed_event_bar_index: int
    suppressed_event_timestamp: datetime
    suppressed_event_direction: RegimeDirection
    suppressed_event_types: tuple[RegimeEventType, ...]
    active_opportunity_source_event_bar: int
    active_opportunity_pullback_bar: int
    active_opportunity_direction: RegimeDirection
    active_opportunity_state: PendingOpportunityStateV2
    suppression_reason: str = "PENDING_OPPORTUNITY_ALREADY_ACTIVE"


@dataclass(frozen=True)
class PendingSignalDecisionV2:
    """Raw telemetry after resolution, before any new pullback can acquire ownership."""

    composition: RegimeContextEvaluation
    state_at_signal_decision: PendingOpportunityStateV2
    status: PendingSignalAdmissionStatusV2
    suppressions: tuple[PendingSignalSuppressionV2, ...] = ()


@dataclass(frozen=True)
class PendingOpportunityPolicyBookV2:
    """One strategy/series, with one actionable chain or one open position.

    stop_activations retains the immutable hand-off snapshots at entry Open.
    Thereafter the frozen position/exit gates own position monitoring and exits.
    """

    positions: OpenPositionSignalPolicyBookV2
    risks: RiskPositionSizingBookV2
    initial_stops: InitialStopBookV2 = field(default_factory=InitialStopBookV2)
    stop_activations: StructuralStopExecutionBookV2 = field(
        default_factory=StructuralStopExecutionBookV2
    )
    opportunities: tuple[PendingOpportunityRecordV2, ...] = ()
    signal_decisions: tuple[PendingSignalDecisionV2, ...] = ()
    end_of_data: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.positions, OpenPositionSignalPolicyBookV2)
            or not isinstance(self.risks, RiskPositionSizingBookV2)
            or (self.positions.strategy_instance_id, self.positions.series_id)
            != (self.risks.strategy_instance_id, self.risks.series_id)
            or not isinstance(self.initial_stops, InitialStopBookV2)
            or not isinstance(self.stop_activations, StructuralStopExecutionBookV2)
            or type(self.end_of_data) is not bool
        ):
            raise PendingOpportunityPolicyV2Error("carry the canonical books for one scope")
        if not isinstance(self.opportunities, tuple) or not all(
            isinstance(item, PendingOpportunityRecordV2) for item in self.opportunities
        ):
            raise PendingOpportunityPolicyV2Error("opportunities must be immutable history")
        sources = [item.consumed_context for item in self.opportunities]
        for earlier, later in pairwise(sources):
            if (
                later.pullback_bar_index <= earlier.pullback_bar_index
                or later.pullback_timestamp <= earlier.pullback_timestamp
            ):
                raise PendingOpportunityPolicyV2Error(
                    "consumed sources cannot repeat or go backward"
                )
        pending = [item for item in self.opportunities if item.state in _PENDING]
        if (
            len(pending) > MAX_ACTIONABLE_PENDING_OPPORTUNITIES_PER_SERIES
            or (pending and pending[-1] is not self.opportunities[-1])
            or (pending and self.positions.position_state is not PositionStateV2.FLAT)
            or (pending and self.positions.context != pending[-1].consumed_context)
            or (pending and self.end_of_data)
        ):
            raise PendingOpportunityPolicyV2Error("one pending owner excludes any second context")
        for item in self.opportunities:
            context = item.consumed_context
            if not any(
                decision.pullback is not None
                and decision.pullback.pullback is not None
                and decision.pullback.pullback.pullback_qualified
                and decision.pullback.lifetime.context == context
                and decision.composition.closed_bar_index == context.pullback_bar_index
                for decision in self.positions.signal_decisions
            ):
                raise PendingOpportunityPolicyV2Error(
                    "lock requires a formally admitted consumption"
                )
            if item.risk_decision is not None:
                self.risks.for_decision(item.risk_decision)
            if item.execution is not None and (
                self.risks.executions.for_confirmation(item.confirmation.confirmation)
                != item.execution
            ):
                raise PendingOpportunityPolicyV2Error("execution provenance cannot change")
            if item.state is PendingOpportunityStateV2.POSITION_OWNED and not any(
                position.entry == item.execution.execution for position in self.positions.positions
            ):
                raise PendingOpportunityPolicyV2Error(
                    "fill must transfer atomically to position ownership"
                )
        if not isinstance(self.signal_decisions, tuple) or not all(
            isinstance(item, PendingSignalDecisionV2) for item in self.signal_decisions
        ):
            raise PendingOpportunityPolicyV2Error("raw telemetry must be immutable history")
        for earlier, later in pairwise(self.signal_decisions):
            if (
                later.composition.closed_bar_index <= earlier.composition.closed_bar_index
                or later.composition.closed_bar_timestamp
                <= earlier.composition.closed_bar_timestamp
            ):
                raise PendingOpportunityPolicyV2Error("signal observations must advance causally")

    @property
    def active_opportunity(self) -> PendingOpportunityRecordV2 | None:
        """Only the final, nonterminal source may own the pending lock."""
        return (
            self.opportunities[-1]
            if self.opportunities and self.opportunities[-1].state in _PENDING
            else None
        )

    @property
    def state(self) -> PendingOpportunityStateV2:
        """Position ownership takes over without a logical admission gap."""
        if self.positions.position_state is not PositionStateV2.FLAT:
            return PendingOpportunityStateV2.POSITION_OWNED
        active = self.active_opportunity
        return PendingOpportunityStateV2.IDLE if active is None else active.state


def begin_pending_opportunity_policy_v2(
    *, strategy_instance_id: str, series_id: str
) -> PendingOpportunityPolicyBookV2:
    """Start an isolated immutable policy; indicators and events acquire no lock."""
    return PendingOpportunityPolicyBookV2(
        OpenPositionSignalPolicyBookV2(strategy_instance_id, series_id),
        RiskPositionSizingBookV2(strategy_instance_id, series_id),
    )


def _require_book(previous: PendingOpportunityPolicyBookV2) -> None:
    if not isinstance(previous, PendingOpportunityPolicyBookV2):
        raise PendingOpportunityPolicyV2Error("carry the current pending policy book")


def _require_healthy_position(positions: OpenPositionSignalPolicyBookV2) -> None:
    stop = positions.active_stop
    if stop is not None and stop.stop_execution_state not in (
        StructuralStopExecutionStateV2.ARMED,
        StructuralStopExecutionStateV2.FILLED_STOP,
    ):
        raise PendingOpportunityPolicyV2Error(
            f"fail-closed position observation: {stop.stop_execution_state}",
            module_result=positions,
        )


def adopt_pending_position_resolution_v2(
    *, previous: PendingOpportunityPolicyBookV2, positions: OpenPositionSignalPolicyBookV2
) -> PendingOpportunityPolicyBookV2:
    """Accept only monitoring/exit updates from the frozen position/exit gates.

    This adapter admits no event, consumes no context, changes no entry and
    cannot restore a closed position. It creates no exit or price of its own.
    """
    _require_book(previous)
    if previous.end_of_data:
        return previous
    original = previous.positions
    if (
        not isinstance(positions, OpenPositionSignalPolicyBookV2)
        or (positions.strategy_instance_id, positions.series_id)
        != (original.strategy_instance_id, original.series_id)
        or positions.signal_decisions != original.signal_decisions
        or positions.lifetime != original.lifetime
        or len(positions.positions) != len(original.positions)
        or any(
            old.entry != new.entry
            or old.initial_stop_at_entry != new.initial_stop_at_entry
            or (old.exit is not None and old.exit != new.exit)
            for old, new in zip(original.positions, positions.positions, strict=True)
        )
    ):
        raise PendingOpportunityPolicyV2Error(
            "position resolution cannot change immutable provenance"
        )
    _require_healthy_position(positions)
    return previous if positions == original else replace(previous, positions=positions)


def _advance_owner(
    previous: PendingOpportunityPolicyBookV2,
    index: int,
    timestamp: datetime,
    bars: Mapping[int, EMA20PullbackBarV2],
    instrument: object,
) -> tuple[
    tuple[PendingOpportunityRecordV2, ...],
    InitialStopBookV2,
    RiskPositionSizingBookV2,
    OpenPositionSignalPolicyBookV2 | None,
]:
    active = previous.active_opportunity
    if active is None:
        return previous.opportunities, previous.initial_stops, previous.risks, None
    if active.state is PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION:
        raise PendingOpportunityPolicyV2Error(
            "resolve the mandatory next Open before a later Close"
        )
    confirmation = advance_entry_confirmation_momentum_v2(
        previous=active.confirmation,
        closed_bar_index=index,
        closed_bar_timestamp=timestamp,
        source_bar_closed=True,
        bars_by_index=bars,
    )
    stops, risks, clock_policy = previous.initial_stops, previous.risks, None
    state, risk, execution = PendingOpportunityStateV2.AWAITING_CONFIRMATION, None, None
    if confirmation.state in _CONFIRMATION_EXPIRED:
        state = PendingOpportunityStateV2.TERMINAL_CONFIRMATION_EXPIRED
    elif confirmation.entry_confirmation:
        stops = register_initial_stop_v2(
            previous=stops, confirmation=confirmation, bars_by_index=bars
        )
        # The risk gate requires the current policy Close. These are filtered
        # actionable inputs, not raw telemetry. A pending source is already
        # CONSUMED, so this call can create no second context or pullback.
        clock_policy = advance_open_position_signal_policy_v2(
            previous=previous.positions,
            closed_bar_index=index,
            closed_bar_timestamp=timestamp,
            source_bar_closed=True,
            bars_by_index=bars,
        )
        risks = register_risk_position_sizing_v2(
            previous=risks,
            position_policy=clock_policy,
            instrument=instrument,
            closed_bar_index=index,
            closed_bar_timestamp=timestamp,
            source_bar_closed=True,
            confirmation=confirmation,
            initial_stop=stops.for_confirmation(confirmation.confirmation),
            bars_by_index=bars,
        )
        risk = risks.decisions[-1]
        if risk.decision is RiskSizingDecisionV2.APPROVE:
            state = PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION
            execution = risks.executions.for_confirmation(confirmation.confirmation)
        else:
            state = PendingOpportunityStateV2.TERMINAL_RISK_REJECTED
            # Release precedes raw admission. The clock-only scratch snapshot
            # is not committed as the real regime decision of this Close.
            clock_policy = None
    owner = PendingOpportunityRecordV2(state, confirmation, risk, execution)
    return (*previous.opportunities[:-1], owner), stops, risks, clock_policy


def advance_pending_opportunity_close_v2(
    *,
    previous: PendingOpportunityPolicyBookV2,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    bars_by_index: Mapping[int, EMA20PullbackBarV2],
    regime_events_at_close: RegimeEventsAtCloseV2,
    instrument: object = INSTRUMENT,
    stop_observation: LongStopObservationInputV2 | ShortStopObservationInputV2 | None = None,
) -> PendingOpportunityPolicyBookV2:
    """Resolve A -> determine lock -> raw events -> filtered context admission.

    The supplier is called only after pending confirmation/stop/risk resolution.
    A repeated Close returns before market/supplier reads. Suppressed telemetry
    never reaches the context gate and is never queued, replayed or restored.
    """
    _require_book(previous)
    if previous.end_of_data:
        return previous
    _require_clock(closed_bar_index, closed_bar_timestamp)
    if source_bar_closed is not True or not callable(regime_events_at_close):
        raise PendingOpportunityPolicyV2Error("a closed bar and raw event supplier are required")
    if previous.signal_decisions:
        latest = previous.signal_decisions[-1].composition
        if (closed_bar_index, closed_bar_timestamp) == (
            latest.closed_bar_index,
            latest.closed_bar_timestamp,
        ):
            return previous
        if (
            closed_bar_index <= latest.closed_bar_index
            or closed_bar_timestamp <= latest.closed_bar_timestamp
        ):
            raise PendingOpportunityPolicyV2Error("Close observations must advance causally")
    positions = resolve_position_stop_v2(
        previous=previous.positions,
        known_bar_index=closed_bar_index,
        known_bar_timestamp=closed_bar_timestamp,
        observation=stop_observation,
    )
    _require_healthy_position(positions)
    resolved = (
        previous if positions is previous.positions else replace(previous, positions=positions)
    )
    opportunities, stops, risks, clock_policy = _advance_owner(
        resolved, closed_bar_index, closed_bar_timestamp, bars_by_index, instrument
    )
    owner = opportunities[-1] if opportunities and opportunities[-1].state in _PENDING else None
    state = (
        PendingOpportunityStateV2.POSITION_OWNED
        if positions.position_state is not PositionStateV2.FLAT
        else PendingOpportunityStateV2.IDLE
        if owner is None
        else owner.state
    )
    impulse, reversal = regime_events_at_close()
    composition = compose_regime_context_v2(
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=True,
        directional_impulse_event=impulse,
        reversal_transition_event=reversal,
    )
    suppressions = ()
    if owner is not None:
        context = owner.consumed_context
        suppressions = tuple(
            PendingSignalSuppressionV2(
                closed_bar_index,
                closed_bar_timestamp,
                direction,
                tuple(
                    event.event_type
                    for event in composition.events
                    if event.event_direction is direction
                ),
                context.source_event_bar_index,
                context.pullback_bar_index,
                context.source_event_direction,
                owner.state,
            )
            for direction in RegimeDirection
            if any(event.event_direction is direction for event in composition.events)
        )
        status = (
            PendingSignalAdmissionStatusV2.SUPPRESSED_PENDING_OPPORTUNITY
            if composition.events
            else PendingSignalAdmissionStatusV2.NO_REGIME_EVENT
        )
        impulse = reversal = None
    elif positions.position_state is not PositionStateV2.FLAT:
        status = (
            PendingSignalAdmissionStatusV2.SUPPRESSED_POSITION_OPEN
            if composition.events
            else PendingSignalAdmissionStatusV2.NO_REGIME_EVENT
        )
    else:
        status = {
            RegimeContextStatus.UNQUALIFIED: PendingSignalAdmissionStatusV2.NO_REGIME_EVENT,
            RegimeContextStatus.QUALIFIED: PendingSignalAdmissionStatusV2.ADMITTED,
            RegimeContextStatus.AMBIGUOUS: PendingSignalAdmissionStatusV2.AMBIGUOUS,
        }[composition.status]
    if clock_policy is None:
        positions = advance_open_position_signal_policy_v2(
            previous=positions,
            closed_bar_index=closed_bar_index,
            closed_bar_timestamp=closed_bar_timestamp,
            source_bar_closed=True,
            bars_by_index=bars_by_index,
            directional_impulse_event=impulse,
            reversal_transition_event=reversal,
        )
    else:
        positions = clock_policy
    _require_healthy_position(positions)
    pullback = positions.signal_decisions[-1].pullback
    if (
        owner is None
        and pullback is not None
        and pullback.pullback is not None
        and pullback.pullback.pullback_qualified
    ):
        confirmation = begin_entry_confirmation_momentum_v2(
            pullback=pullback, pullback_bar=bars_by_index.get(closed_bar_index)
        )
        opportunities = (
            *opportunities,
            PendingOpportunityRecordV2(
                PendingOpportunityStateV2.AWAITING_CONFIRMATION, confirmation
            ),
        )
    decision = PendingSignalDecisionV2(composition, state, status, suppressions)
    return replace(
        previous,
        positions=positions,
        risks=risks,
        initial_stops=stops,
        opportunities=opportunities,
        signal_decisions=(*previous.signal_decisions, decision),
    )


def execute_pending_opportunity_open_v2(
    *, previous: PendingOpportunityPolicyBookV2, opening_bar: EntryExecutionOpenInputV2 | None
) -> PendingOpportunityPolicyBookV2:
    """Resolve the sole approved next Open and transfer ownership atomically.

    None denotes definitive absence of the executable bar, not an early poll.
    Normal execution expiry releases the lock. Failed input/clock outcomes retain
    their frozen evidence and raise fail-closed; they never silently unlock.
    A breached fill becomes a real position followed by its same-Open stop fill.
    """
    _require_book(previous)
    active = previous.active_opportunity
    if (
        previous.end_of_data
        or active is None
        or active.state is not PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION
    ):
        return previous
    risks = execute_risk_approved_entry_open_v2(
        previous=previous.risks, decision=active.risk_decision, opening_bar=opening_bar
    )
    execution = risks.executions.for_confirmation(active.confirmation.confirmation)
    if execution.execution_state is EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN:
        return previous
    stops, activations, positions = (
        previous.initial_stops,
        previous.stop_activations,
        previous.positions,
    )
    if execution.execution_state in _EXECUTION_EXPIRED:
        state = PendingOpportunityStateV2.TERMINAL_EXECUTION_NOT_FILLED
    elif execution.execution_state is EntryExecutionStateV2.FILLED:
        stops = bind_initial_stop_to_entry_v2(
            previous=stops,
            confirmation=active.confirmation.confirmation,
            executions=risks.executions,
        )
        activations = register_structural_stop_execution_v2(
            previous=activations, initial_stops=stops, confirmation=active.confirmation.confirmation
        )
        positions = apply_position_entry_fill_v2(
            previous=positions,
            executions=risks.executions,
            stops=activations,
            confirmation=active.confirmation.confirmation,
        )
        positions = resolve_position_stop_v2(
            previous=positions,
            known_bar_index=execution.execution.execution_bar_index,
            known_bar_timestamp=execution.execution.execution_bar_timestamp,
        )
        state = PendingOpportunityStateV2.POSITION_OWNED
    else:
        raise PendingOpportunityPolicyV2Error(
            f"fail-closed entry execution: {execution.execution_state}", module_result=risks
        )
    owner = replace(active, state=state, execution=execution)
    return replace(
        previous,
        positions=positions,
        risks=risks,
        initial_stops=stops,
        stop_activations=activations,
        opportunities=(*previous.opportunities[:-1], owner),
    )


def finish_pending_opportunity_policy_v2(
    *, previous: PendingOpportunityPolicyBookV2
) -> PendingOpportunityPolicyBookV2:
    """Terminate pending ownership at real end of data, without a synthetic bar/fill.

    Context and open-position end states remain owned by their frozen gates.
    The retained awaiting confirmation snapshot is not advanced with fake input.
    """
    _require_book(previous)
    if previous.end_of_data:
        return previous
    active = previous.active_opportunity
    if active is not None and active.state is PendingOpportunityStateV2.PENDING_ENTRY_EXECUTION:
        previous = execute_pending_opportunity_open_v2(previous=previous, opening_bar=None)
    elif active is not None:
        owner = replace(active, state=PendingOpportunityStateV2.TERMINAL_INCOMPLETE_CONFIRMATION)
        previous = replace(previous, opportunities=(*previous.opportunities[:-1], owner))
    return replace(previous, end_of_data=True)


__all__ = [
    "MAX_ACTIONABLE_PENDING_OPPORTUNITIES_PER_SERIES",
    "OPPOSITE_EVENT_CANCELS_PENDING",
    "PENDING_OPPORTUNITY_LOCK",
    "PENDING_OPPORTUNITY_QUEUE",
    "PENDING_OPPORTUNITY_REPLACEMENT",
    "SAME_DIRECTION_EVENT_REFRESHES_PENDING",
    "PendingOpportunityPolicyBookV2",
    "PendingOpportunityPolicyV2Error",
    "PendingOpportunityRecordV2",
    "PendingOpportunityStateV2",
    "PendingSignalAdmissionStatusV2",
    "PendingSignalDecisionV2",
    "PendingSignalSuppressionV2",
    "adopt_pending_position_resolution_v2",
    "advance_pending_opportunity_close_v2",
    "begin_pending_opportunity_policy_v2",
    "execute_pending_opportunity_open_v2",
    "finish_pending_opportunity_policy_v2",
]
