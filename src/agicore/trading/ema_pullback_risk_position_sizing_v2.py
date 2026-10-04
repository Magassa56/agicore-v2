"""Exact MNQ planned structural risk at Close[q], before any next-bar input.

Carry the immutable series book through registration and execution. Only an
APPROVE registers the unchanged PR #291 next-Open execution. REJECT is terminal
for the consumed pullback, with no execution, fallback or future reconsideration.
This is an offline price-risk budget, without costs or a realized-loss guarantee.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import StrEnum
from fractions import Fraction
from typing import Protocol

from .ema20_pullback_v2 import _exact_price
from .ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationEvaluationV2,
    EntryConfirmationOpportunityV2,
    EntryConfirmationRecordV2,
)
from .ema_pullback_entry_execution_v2 import (
    EntryExecutionBookV2,
    EntryExecutionOpenInputV2,
    EntryExecutionRecordV2,
    EntryExecutionStateV2,
    EntryExecutionV2Error,
    _known_confirmation,
    _valid_utc,
    execute_entry_open_v2,
    register_entry_execution_v2,
)
from .ema_pullback_initial_stop_v2 import (
    STOP_BUFFER_TICKS,
    TICK_SIZE,
    InitialStopEvaluationV2,
    InitialStopRecordV2,
    InitialStopStatusV2,
)
from .ema_pullback_open_position_signal_policy_v2 import (
    OpenPositionSignalPolicyBookV2,
    OpenPositionSignalPolicyV2Error,
    PositionStateV2,
    _require_admitted_pullback,
)
from .regime_context_v2 import RegimeDirection, RegimeEventContextV2, RegimeEventType

INSTRUMENT = "MNQ"
POINT_VALUE_USD = Fraction(2, 1)
TICK_VALUE_USD = Fraction(1, 2)
PLANNED_RISK_BUDGET_USD = Fraction(100, 1)
RISK_BUDGET_KIND = "PLANNED_STRUCTURAL_PRICE_RISK_BUDGET"
MIN_CONTRACTS = 1
MAX_CONTRACTS = 2
NO_RESIZING_AFTER_CONFIRMATION = True


class RiskPositionSizingV2Error(ValueError):
    """Reject noncausal metadata, changed provenance or misuse of the retained book."""


class RiskSizingDecisionV2(StrEnum):
    """Authorization before entry; never an order or fill."""

    APPROVE = "APPROVE"
    REJECT = "REJECT"


class RiskSizingStateV2(StrEnum):
    """Frozen authorization, or terminal rejection of this consumed opportunity."""

    APPROVED_FOR_NEXT_BAR_OPEN = "APPROVED_FOR_NEXT_BAR_OPEN"
    REJECTED_BY_RISK_ENGINE = "REJECTED_BY_RISK_ENGINE"


class RiskSizingRejectionReasonV2(StrEnum):
    """Fail-closed structural, data, qualification and position outcomes."""

    INVALID_INSTRUMENT = "INVALID_INSTRUMENT"
    UNQUALIFIED_CONFIRMATION = "UNQUALIFIED_CONFIRMATION"
    INVALID_CONFIRMATION_INPUT = "INVALID_CONFIRMATION_INPUT"
    INITIAL_STOP_UNAVAILABLE = "INITIAL_STOP_UNAVAILABLE"
    INITIAL_STOP_NOT_EVALUATED = "INITIAL_STOP_NOT_EVALUATED"
    INVALID_INITIAL_STOP_INPUT = "INVALID_INITIAL_STOP_INPUT"
    INVALID_INITIAL_STOP_PROVENANCE = "INVALID_INITIAL_STOP_PROVENANCE"
    INVALID_SIZING_REFERENCE_INPUT = "INVALID_SIZING_REFERENCE_INPUT"
    INVALID_SIZING_CLOCK = "INVALID_SIZING_CLOCK"
    INVALID_MNQ_TICK_GRID = "INVALID_MNQ_TICK_GRID"
    INVALID_STRUCTURAL_RISK_DISTANCE = "INVALID_STRUCTURAL_RISK_DISTANCE"
    RISK_PER_CONTRACT_EXCEEDS_BUDGET = "RISK_PER_CONTRACT_EXCEEDS_BUDGET"
    POSITION_ALREADY_OPEN = "POSITION_ALREADY_OPEN"
    INVALID_POSITION_STATE = "INVALID_POSITION_STATE"
    INVALID_POSITION_POLICY_INPUT = "INVALID_POSITION_POLICY_INPUT"


class RiskSizingCloseInputV2(Protocol):
    """Only the current closed candidate metadata and Close are sizing inputs."""

    bar_index: int
    timestamp_utc: datetime
    is_closed: bool
    close: object


def _opportunity_key(context: RegimeEventContextV2 | None, q: int, timestamp: datetime) -> tuple:
    if context is None:
        return (None, q, timestamp)
    return (
        context.source_event_bar_index,
        context.source_event_timestamp,
        context.source_event_direction,
        context.pullback_bar_index,
        context.pullback_timestamp,
    )


def _consumed_context(
    confirmation: EntryConfirmationEvaluationV2 | None,
) -> RegimeEventContextV2 | None:
    if isinstance(confirmation, EntryConfirmationEvaluationV2) and isinstance(
        confirmation.opportunity, EntryConfirmationOpportunityV2
    ):
        return confirmation.opportunity.consumed_context
    return None


@dataclass(frozen=True)
class RiskSizingDecisionRecordV2:
    """Immutable Close[q] snapshot, including provenance for rejected opportunities."""

    instrument: str | None
    direction: RegimeDirection | None
    source_regime_event_types: tuple[RegimeEventType, ...]
    source_regime_event_bar_index: int | None
    source_regime_event_timestamp: datetime | None
    pullback_bar_index: int | None
    pullback_timestamp: datetime | None
    ema_reference: Fraction | None
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    sizing_decision_known_at_bar: int
    sizing_decision_known_at_timestamp: datetime
    position_state_at_sizing: PositionStateV2 | None
    consumed_context: RegimeEventContextV2 | None
    confirmation: EntryConfirmationRecordV2 | None
    initial_stop_record: InitialStopRecordV2 | None
    decision: RiskSizingDecisionV2
    rejection_reason: RiskSizingRejectionReasonV2 | None
    sizing_reference_price: Fraction | None = None
    initial_stop_price: Fraction | None = None
    stop_distance_points: Fraction | None = None
    risk_per_contract_usd: Fraction | None = None
    raw_quantity: int | None = None
    approved_quantity: int = 0
    planned_total_risk_usd: Fraction | None = None
    tick_size: Fraction = TICK_SIZE
    point_value_usd: Fraction = POINT_VALUE_USD
    risk_budget_usd: Fraction = PLANNED_RISK_BUDGET_USD
    risk_budget_kind: str = RISK_BUDGET_KIND

    def __post_init__(self) -> None:
        if (
            not isinstance(self.decision, RiskSizingDecisionV2)
            or self.tick_size != TICK_SIZE
            or self.point_value_usd != POINT_VALUE_USD
            or self.risk_budget_usd != PLANNED_RISK_BUDGET_USD
            or self.risk_budget_kind != RISK_BUDGET_KIND
            or (self.confirmation_bar_index, self.confirmation_timestamp)
            != (self.sizing_decision_known_at_bar, self.sizing_decision_known_at_timestamp)
        ):
            raise RiskPositionSizingV2Error("risk record must retain the frozen Close[q] baseline")
        if self.decision is RiskSizingDecisionV2.REJECT:
            if (
                not isinstance(self.rejection_reason, RiskSizingRejectionReasonV2)
                or self.approved_quantity != 0
                or self.planned_total_risk_usd is not None
            ):
                raise RiskPositionSizingV2Error("REJECT cannot authorize a quantity")
            return
        if (
            self.instrument != INSTRUMENT
            or self.position_state_at_sizing is not PositionStateV2.FLAT
            or self.confirmation is None
            or self.initial_stop_record is None
            or self.consumed_context is None
            or self.rejection_reason is not None
            or type(self.approved_quantity) is not int
            or not MIN_CONTRACTS <= self.approved_quantity <= MAX_CONTRACTS
            or not all(
                isinstance(value, Fraction)
                for value in (
                    self.sizing_reference_price,
                    self.initial_stop_price,
                    self.stop_distance_points,
                    self.risk_per_contract_usd,
                    self.planned_total_risk_usd,
                )
            )
            or self.stop_distance_points <= 0
            or self.direction not in (RegimeDirection.LONG, RegimeDirection.SHORT)
            or self.stop_distance_points
            != (
                self.sizing_reference_price - self.initial_stop_price
                if self.direction is RegimeDirection.LONG
                else self.initial_stop_price - self.sizing_reference_price
            )
            or (self.sizing_reference_price / TICK_SIZE).denominator != 1
            or (self.initial_stop_price / TICK_SIZE).denominator != 1
            or self.risk_per_contract_usd != self.stop_distance_points * POINT_VALUE_USD
            or type(self.raw_quantity) is not int
            or self.raw_quantity != PLANNED_RISK_BUDGET_USD // self.risk_per_contract_usd
            or self.approved_quantity != min(MAX_CONTRACTS, self.raw_quantity)
            or self.planned_total_risk_usd != self.approved_quantity * self.risk_per_contract_usd
            or self.planned_total_risk_usd > PLANNED_RISK_BUDGET_USD
        ):
            raise RiskPositionSizingV2Error("APPROVE must satisfy exact planned-risk invariants")

    @property
    def state(self) -> RiskSizingStateV2:
        """Approval stays frozen; execution keeps its separate PR #291 state."""
        return (
            RiskSizingStateV2.APPROVED_FOR_NEXT_BAR_OPEN
            if self.decision is RiskSizingDecisionV2.APPROVE
            else RiskSizingStateV2.REJECTED_BY_RISK_ENGINE
        )

    @property
    def opportunity_key(self) -> tuple:
        """Retain one decision per consumed pullback, not one retry per future bar."""
        return _opportunity_key(
            self.consumed_context, self.confirmation_bar_index, self.confirmation_timestamp
        )


def evaluate_risk_position_sizing_v2(
    *,
    instrument: object,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    confirmation: EntryConfirmationEvaluationV2 | None,
    initial_stop: InitialStopEvaluationV2 | None,
    position_state: PositionStateV2,
    bars_by_index: Mapping[int, RiskSizingCloseInputV2],
) -> RiskSizingDecisionRecordV2:
    """Evaluate only Close[q] and the already-known initial-stop snapshot.

    Invalid price/qualification/position inputs REJECT without fallback. Clock
    arguments must describe a real closed UTC observation. Use registration to
    freeze this result across repeated calls, market mutations and future bars.
    """
    if (
        type(closed_bar_index) is not int
        or closed_bar_index < 0
        or not _valid_utc(closed_bar_timestamp)
        or source_bar_closed is not True
    ):
        raise RiskPositionSizingV2Error(
            "sizing decision requires a closed bar with a valid UTC clock"
        )
    context = _consumed_context(confirmation)
    stop = (
        initial_stop.initial_stop_record
        if isinstance(initial_stop, InitialStopEvaluationV2)
        else None
    )
    values = {
        "instrument": instrument if isinstance(instrument, str) else None,
        "direction": None if context is None else context.source_event_direction,
        "source_regime_event_types": () if context is None else context.source_event_types,
        "source_regime_event_bar_index": None
        if context is None
        else context.source_event_bar_index,
        "source_regime_event_timestamp": None
        if context is None
        else context.source_event_timestamp,
        "pullback_bar_index": None if context is None else context.pullback_bar_index,
        "pullback_timestamp": None if context is None else context.pullback_timestamp,
        "ema_reference": None if context is None else context.ema_reference,
        "confirmation_bar_index": closed_bar_index,
        "confirmation_timestamp": closed_bar_timestamp,
        "sizing_decision_known_at_bar": closed_bar_index,
        "sizing_decision_known_at_timestamp": closed_bar_timestamp,
        "position_state_at_sizing": position_state
        if isinstance(position_state, PositionStateV2)
        else None,
        "consumed_context": context,
        "confirmation": None,
        "initial_stop_record": stop,
    }

    def reject(reason):
        return RiskSizingDecisionRecordV2(
            **values, decision=RiskSizingDecisionV2.REJECT, rejection_reason=reason
        )

    if not isinstance(instrument, str) or instrument != INSTRUMENT:
        return reject(RiskSizingRejectionReasonV2.INVALID_INSTRUMENT)
    try:
        record = _known_confirmation(confirmation)
    except (EntryExecutionV2Error, AttributeError, TypeError):
        return reject(RiskSizingRejectionReasonV2.UNQUALIFIED_CONFIRMATION)
    values["confirmation"] = record
    if (record.confirmation_bar_index, record.confirmation_timestamp) != (
        closed_bar_index,
        closed_bar_timestamp,
    ) or record.confirmation_bar_index - record.pullback_bar_index not in (1, 2):
        return reject(RiskSizingRejectionReasonV2.INVALID_CONFIRMATION_INPUT)
    if not isinstance(position_state, PositionStateV2):
        return reject(RiskSizingRejectionReasonV2.INVALID_POSITION_STATE)
    if position_state is not PositionStateV2.FLAT:
        return reject(RiskSizingRejectionReasonV2.POSITION_ALREADY_OPEN)
    if initial_stop is None or stop is None:
        return reject(RiskSizingRejectionReasonV2.INITIAL_STOP_UNAVAILABLE)
    if initial_stop.status is not InitialStopStatusV2.EVALUATED:
        return reject(RiskSizingRejectionReasonV2.INITIAL_STOP_NOT_EVALUATED)
    if (
        not isinstance(stop, InitialStopRecordV2)
        or initial_stop.confirmation != record
        or stop.confirmation != record
        or stop.source_regime_event_direction is not record.source_regime_event_direction
        or stop.source_regime_event_types != record.source_regime_event_types
        or (stop.source_regime_event_bar_index, stop.source_regime_event_timestamp)
        != (record.source_regime_event_bar_index, record.source_regime_event_timestamp)
        or (stop.pullback_bar_index, stop.pullback_timestamp)
        != (record.pullback_bar_index, record.pullback_timestamp)
        or stop.ema_reference != record.ema_reference
        or (stop.confirmation_bar_index, stop.confirmation_timestamp)
        != (closed_bar_index, closed_bar_timestamp)
        or initial_stop.at_entry is not None
        or (stop.stop_known_at_bar_index, stop.stop_known_at_timestamp)
        != (closed_bar_index, closed_bar_timestamp)
        or (stop.structural_window_first_bar, stop.structural_window_last_bar)
        != (record.pullback_bar_index, closed_bar_index)
        or stop.tick_size != TICK_SIZE
        or stop.stop_buffer_ticks != STOP_BUFFER_TICKS
    ):
        return reject(RiskSizingRejectionReasonV2.INVALID_INITIAL_STOP_PROVENANCE)
    candidate = bars_by_index.get(closed_bar_index)
    if candidate is None:
        return reject(RiskSizingRejectionReasonV2.INVALID_SIZING_REFERENCE_INPUT)
    if (getattr(candidate, "bar_index", None), getattr(candidate, "timestamp_utc", None)) != (
        closed_bar_index,
        closed_bar_timestamp,
    ) or getattr(candidate, "is_closed", None) is not True:
        return reject(RiskSizingRejectionReasonV2.INVALID_SIZING_CLOCK)
    reference = _exact_price(getattr(candidate, "close", None))
    values["sizing_reference_price"] = reference
    if reference is None:
        return reject(RiskSizingRejectionReasonV2.INVALID_SIZING_REFERENCE_INPUT)
    stop_price = _exact_price(stop.initial_stop_price)
    values["initial_stop_price"] = stop_price
    if stop_price is None:
        return reject(RiskSizingRejectionReasonV2.INVALID_INITIAL_STOP_INPUT)
    if (reference / TICK_SIZE).denominator != 1 or (stop_price / TICK_SIZE).denominator != 1:
        return reject(RiskSizingRejectionReasonV2.INVALID_MNQ_TICK_GRID)
    distance = (
        reference - stop_price
        if record.source_regime_event_direction is RegimeDirection.LONG
        else stop_price - reference
    )
    values["stop_distance_points"] = distance
    if distance <= 0:
        return reject(RiskSizingRejectionReasonV2.INVALID_STRUCTURAL_RISK_DISTANCE)
    risk = distance * POINT_VALUE_USD
    raw_quantity = PLANNED_RISK_BUDGET_USD // risk
    values.update(risk_per_contract_usd=risk, raw_quantity=raw_quantity)
    quantity = min(MAX_CONTRACTS, raw_quantity)
    if quantity < MIN_CONTRACTS:
        return reject(RiskSizingRejectionReasonV2.RISK_PER_CONTRACT_EXCEEDS_BUDGET)
    return RiskSizingDecisionRecordV2(
        **values,
        decision=RiskSizingDecisionV2.APPROVE,
        rejection_reason=None,
        approved_quantity=quantity,
        planned_total_risk_usd=quantity * risk,
    )


@dataclass(frozen=True)
class RiskSizedEntryRecordV2:
    """Frozen quantity linked to the unchanged actual entry; extra prices are diagnostic."""

    risk_decision: RiskSizingDecisionRecordV2
    execution: EntryExecutionRecordV2

    def __post_init__(self) -> None:
        if (
            self.risk_decision.decision is not RiskSizingDecisionV2.APPROVE
            or self.execution.confirmation != self.risk_decision.confirmation
        ):
            raise RiskPositionSizingV2Error("sized fill must retain its APPROVE provenance")

    @property
    def quantity(self) -> int:
        """Always the quantity determined at Close[q], including breached entry gaps."""
        return self.risk_decision.approved_quantity

    @property
    def actual_entry_price(self) -> Fraction:
        """Diagnostic base fill; never an input to the authorization or quantity."""
        return self.execution.execution_price_before_costs

    @property
    def actual_entry_to_stop_distance_points(self) -> Fraction:
        """Signed diagnostic distance; zero/negative means entry opened at/beyond stop."""
        stop = self.risk_decision.initial_stop_price
        return (
            self.actual_entry_price - stop
            if self.execution.execution_side is RegimeDirection.LONG
            else stop - self.actual_entry_price
        )


@dataclass(frozen=True)
class RiskPositionSizingBookV2:
    """One strategy/series' retained risk decisions and only authorized executions."""

    strategy_instance_id: str
    series_id: str
    decisions: tuple[RiskSizingDecisionRecordV2, ...] = ()
    executions: EntryExecutionBookV2 = field(default_factory=EntryExecutionBookV2)
    filled_entries: tuple[RiskSizedEntryRecordV2, ...] = ()

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.strategy_instance_id, self.series_id)
        ):
            raise RiskPositionSizingV2Error("risk book requires an explicit strategy/series scope")
        if not isinstance(self.decisions, tuple) or not all(
            isinstance(item, RiskSizingDecisionRecordV2) for item in self.decisions
        ):
            raise RiskPositionSizingV2Error("risk decisions must be an immutable history")
        if len({item.opportunity_key for item in self.decisions}) != len(self.decisions):
            raise RiskPositionSizingV2Error(
                "risk decision cannot be reconsidered for an opportunity"
            )
        if not isinstance(self.executions, EntryExecutionBookV2):
            raise RiskPositionSizingV2Error("risk book must own its canonical execution book")
        approvals = [
            item for item in self.decisions if item.decision is RiskSizingDecisionV2.APPROVE
        ]
        if len(approvals) != len(self.executions.entries) or any(
            not any(item.confirmation == entry.confirmation for item in approvals)
            for entry in self.executions.entries
        ):
            raise RiskPositionSizingV2Error("REJECT cannot create an entry execution")
        if not isinstance(self.filled_entries, tuple) or not all(
            isinstance(item, RiskSizedEntryRecordV2) for item in self.filled_entries
        ):
            raise RiskPositionSizingV2Error("sized fills must be an immutable history")
        filled = [
            entry
            for entry in self.executions.entries
            if entry.execution_state is EntryExecutionStateV2.FILLED
        ]
        if len(filled) != len(self.filled_entries) or len(
            {item.risk_decision.opportunity_key for item in self.filled_entries}
        ) != len(self.filled_entries):
            raise RiskPositionSizingV2Error(
                "each actual fill must have exactly one frozen quantity"
            )
        for sized in self.filled_entries:
            if self.for_decision(sized.risk_decision) != sized.risk_decision or not any(
                sized.execution == entry.execution for entry in filled
            ):
                raise RiskPositionSizingV2Error(
                    "sized fill must preserve the canonical risk/entry link"
                )

    def for_decision(self, decision: RiskSizingDecisionRecordV2) -> RiskSizingDecisionRecordV2:
        """Retrieve the original decision, rejecting changed or unregistered provenance."""
        if not isinstance(decision, RiskSizingDecisionRecordV2):
            raise RiskPositionSizingV2Error("lookup requires a risk decision record")
        for existing in self.decisions:
            if existing.opportunity_key == decision.opportunity_key:
                if existing != decision:
                    raise RiskPositionSizingV2Error("registered risk provenance cannot change")
                return existing
        raise RiskPositionSizingV2Error("risk decision must be registered at Close[q]")


def register_risk_position_sizing_v2(
    *,
    previous: RiskPositionSizingBookV2,
    position_policy: OpenPositionSignalPolicyBookV2,
    instrument: object,
    closed_bar_index: int,
    closed_bar_timestamp: datetime,
    source_bar_closed: bool,
    confirmation: EntryConfirmationEvaluationV2 | None,
    initial_stop: InitialStopEvaluationV2 | None,
    bars_by_index: Mapping[int, RiskSizingCloseInputV2],
) -> RiskPositionSizingBookV2:
    """Freeze risk once; only APPROVE may register PENDING next-bar execution.

    A repeated source returns before reading prices, stop or position state.
    Rejected sources stay rejected even if a later confirmation or price looks
    acceptable. The actual admitted/consumed source and Close[q] policy must
    match for a new authorization; no suppressed chain can bypass PR #294.
    """
    if not isinstance(previous, RiskPositionSizingBookV2) or not isinstance(
        position_policy, OpenPositionSignalPolicyBookV2
    ):
        raise RiskPositionSizingV2Error("registration requires the risk and position books")
    if (previous.strategy_instance_id, previous.series_id) != (
        position_policy.strategy_instance_id,
        position_policy.series_id,
    ):
        raise RiskPositionSizingV2Error("risk and position books must belong to the same scope")
    context = _consumed_context(confirmation)
    key = _opportunity_key(context, closed_bar_index, closed_bar_timestamp)
    for existing in previous.decisions:
        if existing.opportunity_key != key:
            continue
        if existing.consumed_context != context:
            raise RiskPositionSizingV2Error("consumed source provenance cannot change")
        if existing.decision is RiskSizingDecisionV2.APPROVE and (
            existing.instrument != instrument
            or existing.confirmation != _known_confirmation(confirmation)
            or (closed_bar_index, closed_bar_timestamp)
            != (existing.confirmation_bar_index, existing.confirmation_timestamp)
        ):
            raise RiskPositionSizingV2Error("approved confirmation provenance cannot change")
        return previous
    evaluation = evaluate_risk_position_sizing_v2(
        instrument=instrument,
        closed_bar_index=closed_bar_index,
        closed_bar_timestamp=closed_bar_timestamp,
        source_bar_closed=source_bar_closed,
        confirmation=confirmation,
        initial_stop=initial_stop,
        position_state=position_policy.position_state,
        bars_by_index=bars_by_index,
    )
    if evaluation.decision is RiskSizingDecisionV2.APPROVE:
        try:
            if not position_policy.signal_decisions or (
                position_policy.signal_decisions[-1].composition.closed_bar_index,
                position_policy.signal_decisions[-1].composition.closed_bar_timestamp,
            ) != (closed_bar_index, closed_bar_timestamp):
                raise OpenPositionSignalPolicyV2Error("confirmation policy Close is not known")
            _require_admitted_pullback(position_policy, evaluation.confirmation)
        except OpenPositionSignalPolicyV2Error:
            evaluation = replace(
                evaluation,
                decision=RiskSizingDecisionV2.REJECT,
                rejection_reason=RiskSizingRejectionReasonV2.INVALID_POSITION_POLICY_INPUT,
                approved_quantity=0,
                planned_total_risk_usd=None,
            )
    executions = previous.executions
    if evaluation.decision is RiskSizingDecisionV2.APPROVE:
        executions = register_entry_execution_v2(previous=executions, confirmation=confirmation)
    return replace(previous, decisions=(*previous.decisions, evaluation), executions=executions)


def execute_risk_approved_entry_open_v2(
    *,
    previous: RiskPositionSizingBookV2,
    decision: RiskSizingDecisionRecordV2,
    opening_bar: EntryExecutionOpenInputV2 | None,
) -> RiskPositionSizingBookV2:
    """Delegate the sole authorized next Open; quantity and risk never recompute.

    Rejection returns before every market-field read. Pending, absence, clock
    gaps, input validation, fills and idempotence remain exactly those of PR #291.
    Actual entry-to-stop distance is stored only as a diagnostic linked record.
    """
    if not isinstance(previous, RiskPositionSizingBookV2):
        raise RiskPositionSizingV2Error("execution requires the current risk book")
    registered = previous.for_decision(decision)
    if registered.decision is RiskSizingDecisionV2.REJECT:
        return previous
    executions = execute_entry_open_v2(
        previous=previous.executions, confirmation=registered.confirmation, opening_bar=opening_bar
    )
    if executions is previous.executions:
        return previous
    outcome = executions.for_confirmation(registered.confirmation)
    filled = previous.filled_entries
    if outcome.execution_state is EntryExecutionStateV2.FILLED:
        filled = (*filled, RiskSizedEntryRecordV2(registered, outcome.execution))
    return replace(previous, executions=executions, filled_entries=filled)


__all__ = [
    "INSTRUMENT",
    "MAX_CONTRACTS",
    "MIN_CONTRACTS",
    "NO_RESIZING_AFTER_CONFIRMATION",
    "PLANNED_RISK_BUDGET_USD",
    "POINT_VALUE_USD",
    "RISK_BUDGET_KIND",
    "TICK_SIZE",
    "TICK_VALUE_USD",
    "RiskPositionSizingBookV2",
    "RiskPositionSizingV2Error",
    "RiskSizedEntryRecordV2",
    "RiskSizingCloseInputV2",
    "RiskSizingDecisionRecordV2",
    "RiskSizingDecisionV2",
    "RiskSizingRejectionReasonV2",
    "RiskSizingStateV2",
    "evaluate_risk_position_sizing_v2",
    "execute_risk_approved_entry_open_v2",
    "register_risk_position_sizing_v2",
]
