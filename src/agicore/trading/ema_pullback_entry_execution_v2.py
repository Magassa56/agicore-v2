"""Deterministic offline V2 entry at the next bar's Open, without broker access.

A series-scoped immutable book keeps one execution state per qualified
confirmation. The only market fields read are bar_index, timestamp_utc and
open, even when the caller holds a complete future OHLCV observation.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timedelta
from enum import StrEnum
from fractions import Fraction
from typing import Protocol

from .ema20_pullback_v2 import _exact_price
from .ema_pullback_entry_confirmation_v2 import (
    EntryConfirmationEvaluationV2,
    EntryConfirmationRecordV2,
    EntryConfirmationStateV2,
)
from .regime_context_v2 import RegimeDirection, RegimeEventType

MAX_EXECUTION_AGE_CLOSED_BARS = 1
MAX_EXECUTION_ELAPSED_TIME = timedelta(minutes=1)
ENTRY_DECISION_MOMENT = "Close[q]"
EXECUTION_POINT = "Open[q+1]"
ORDER_SEMANTICS = "MARKET"
NO_FILL_ON_CONFIRMATION_BAR = True
NO_MAX_ENTRY_GAP_FILTER = True


class EntryExecutionV2Error(ValueError):
    """Reject inconsistent qualified provenance or misuse of the execution book."""


class EntryExecutionStateV2(StrEnum):
    """Pending next Open, or an irreversible offline execution outcome."""

    PENDING_NEXT_BAR_OPEN = "PENDING_NEXT_BAR_OPEN"
    FILLED = "FILLED"
    EXPIRED_NO_EXECUTION = "EXPIRED_NO_EXECUTION"
    EXPIRED_EXECUTION_GAP = "EXPIRED_EXECUTION_GAP"
    FAILED_INVALID_EXECUTION_INPUT = "FAILED_INVALID_EXECUTION_INPUT"
    FAILED_INVALID_EXECUTION_CLOCK = "FAILED_INVALID_EXECUTION_CLOCK"


class EntryExecutionStatusV2(StrEnum):
    """Distinguish invalid clock/input from pending, expired or filled state."""

    NOT_EVALUATED = "NOT_EVALUATED"
    EVALUATED = "EVALUATED"
    INVALID_EXECUTION_CLOCK = "INVALID_EXECUTION_CLOCK"
    INVALID_EXECUTION_INPUT = "INVALID_EXECUTION_INPUT"


class EntryExecutionActionV2(StrEnum):
    """Market semantics labels only; these never submit a live order."""

    BUY = "BUY"
    SELL_SHORT = "SELL_SHORT"


class EntryExecutionOpenInputV2(Protocol):
    """Minimal opening observation; no OHLCV/closure attributes are required."""

    bar_index: int
    timestamp_utc: datetime
    open: object


@dataclass(frozen=True)
class EntryExecutionOpenV2:
    """Opening snapshot; malformed values reach explicit fail-closed statuses."""

    bar_index: int
    timestamp_utc: datetime
    open: object


@dataclass(frozen=True)
class EntryExecutionRecordV2:
    """Immutable base fill and full provenance, without costs, quantity or exits."""

    source_regime_event_types: tuple[RegimeEventType, ...]
    source_regime_event_bar_index: int
    source_regime_event_timestamp: datetime
    source_regime_event_direction: RegimeDirection
    pullback_bar_index: int
    pullback_timestamp: datetime
    ema_reference: Fraction
    confirmation_bar_index: int
    confirmation_timestamp: datetime
    execution_bar_index: int
    execution_bar_timestamp: datetime
    execution_side: RegimeDirection
    execution_price_before_costs: Fraction
    execution_action: EntryExecutionActionV2
    confirmation: EntryConfirmationRecordV2
    order_semantics: str = ORDER_SEMANTICS


@dataclass(frozen=True)
class EntryExecutionEvaluationV2:
    """Canonical state of one confirmation; a terminal state is never reopened."""

    confirmation: EntryConfirmationRecordV2
    execution_state: EntryExecutionStateV2 = EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN
    status: EntryExecutionStatusV2 = EntryExecutionStatusV2.NOT_EVALUATED
    execution: EntryExecutionRecordV2 | None = None

    @property
    def expected_execution_bar_index(self) -> int:
        """Only q+1 can execute, irrespective of later data availability."""
        return self.confirmation.confirmation_bar_index + MAX_EXECUTION_AGE_CLOSED_BARS


def _confirmation_key(record: EntryConfirmationRecordV2) -> tuple:
    return (
        record.source_regime_event_bar_index,
        record.source_regime_event_timestamp,
        record.source_regime_event_direction,
        record.pullback_bar_index,
        record.pullback_timestamp,
        record.confirmation_bar_index,
        record.confirmation_timestamp,
    )


@dataclass(frozen=True)
class EntryExecutionBookV2:
    """One offline series' immutable execution history, including terminal states.

    Callers must carry the returned book forward. Re-registering an equivalent
    confirmation cannot reset its state; changing metadata under the same causal
    identity is an error. No global state, position policy or broker is involved.
    """

    entries: tuple[EntryExecutionEvaluationV2, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.entries, tuple) or not all(
            isinstance(entry, EntryExecutionEvaluationV2) for entry in self.entries
        ):
            raise EntryExecutionV2Error("execution history must be an immutable tuple of states")
        keys = [_confirmation_key(entry.confirmation) for entry in self.entries]
        if len(set(keys)) != len(keys):
            raise EntryExecutionV2Error("execution history must not duplicate a confirmation")

    def for_confirmation(
        self, confirmation: EntryConfirmationRecordV2
    ) -> EntryExecutionEvaluationV2:
        """Retrieve the canonical state, refusing altered provenance or unregistered sources."""
        if not isinstance(confirmation, EntryConfirmationRecordV2):
            raise EntryExecutionV2Error("lookup requires an entry confirmation record")
        key = _confirmation_key(confirmation)
        for entry in self.entries:
            if _confirmation_key(entry.confirmation) == key:
                if entry.confirmation != confirmation:
                    raise EntryExecutionV2Error("registered confirmation provenance cannot change")
                return entry
        raise EntryExecutionV2Error("confirmation must be registered at its qualified close")


def _known_confirmation(decision: EntryConfirmationEvaluationV2) -> EntryConfirmationRecordV2:
    if (
        not isinstance(decision, EntryConfirmationEvaluationV2)
        or decision.state is not EntryConfirmationStateV2.CONFIRMED
        or decision.entry_confirmation is not True
        or decision.candidate is None
        or decision.candidate.entry_confirmation is not True
    ):
        raise EntryExecutionV2Error("execution requires a qualified closed confirmation")
    record = decision.confirmation
    context = decision.opportunity.consumed_context
    if (
        (record.confirmation_bar_index, record.confirmation_timestamp)
        != (decision.closed_bar_index, decision.closed_bar_timestamp)
        or (record.confirmation_bar_index, record.confirmation_timestamp)
        != (decision.candidate.confirmation_bar_index, decision.candidate.confirmation_timestamp)
        or record.source_regime_event_types != context.source_event_types
        or record.source_regime_event_bar_index != context.source_event_bar_index
        or record.source_regime_event_timestamp != context.source_event_timestamp
        or record.source_regime_event_direction is not context.source_event_direction
        or (record.pullback_bar_index, record.pullback_timestamp)
        != (context.pullback_bar_index, context.pullback_timestamp)
        or record.ema_reference != context.ema_reference
    ):
        raise EntryExecutionV2Error(
            "qualified confirmation provenance must match its consumed source"
        )
    if not _valid_utc(record.confirmation_timestamp):
        raise EntryExecutionV2Error("qualified confirmation timestamp must be aware UTC")
    return record


def register_entry_execution_v2(
    *, previous: EntryExecutionBookV2, confirmation: EntryConfirmationEvaluationV2
) -> EntryExecutionBookV2:
    """Register PENDING at Close[q], with no bar access and no same-bar fill."""
    if not isinstance(previous, EntryExecutionBookV2):
        raise EntryExecutionV2Error("registration requires the current execution book")
    record = _known_confirmation(confirmation)
    if any(
        _confirmation_key(entry.confirmation) == _confirmation_key(record)
        for entry in previous.entries
    ):
        previous.for_confirmation(record)  # Also reject changed metadata under the same identity.
        return previous
    return EntryExecutionBookV2((*previous.entries, EntryExecutionEvaluationV2(record)))


def _valid_utc(timestamp: object) -> bool:
    return (
        isinstance(timestamp, datetime)
        and timestamp.tzinfo is not None
        and timestamp.utcoffset() == timedelta(0)
    )


def _advance_open(
    previous: EntryExecutionEvaluationV2, opening_bar: EntryExecutionOpenInputV2 | None
) -> EntryExecutionEvaluationV2:
    if previous.execution_state is not EntryExecutionStateV2.PENDING_NEXT_BAR_OPEN:
        return previous

    def result(state, status=EntryExecutionStatusV2.EVALUATED):
        return replace(previous, execution_state=state, status=status)

    if opening_bar is None:
        return result(EntryExecutionStateV2.EXPIRED_NO_EXECUTION)
    index = getattr(opening_bar, "bar_index", None)
    if type(index) is not int or index < 0:
        return result(
            EntryExecutionStateV2.FAILED_INVALID_EXECUTION_INPUT,
            EntryExecutionStatusV2.INVALID_EXECUTION_INPUT,
        )
    expected = previous.expected_execution_bar_index
    if index > expected:
        return result(EntryExecutionStateV2.EXPIRED_NO_EXECUTION)
    timestamp = getattr(opening_bar, "timestamp_utc", None)
    source = previous.confirmation
    if index == source.confirmation_bar_index and timestamp == source.confirmation_timestamp:
        return previous  # Close[q] can register, but never fill its own confirmation.
    if index != expected or not _valid_utc(timestamp) or timestamp <= source.confirmation_timestamp:
        return result(
            EntryExecutionStateV2.FAILED_INVALID_EXECUTION_CLOCK,
            EntryExecutionStatusV2.INVALID_EXECUTION_CLOCK,
        )
    if timestamp - source.confirmation_timestamp > MAX_EXECUTION_ELAPSED_TIME:
        return result(EntryExecutionStateV2.EXPIRED_EXECUTION_GAP)
    price = _exact_price(getattr(opening_bar, "open", None))
    if price is None or price <= 0:
        return result(
            EntryExecutionStateV2.FAILED_INVALID_EXECUTION_INPUT,
            EntryExecutionStatusV2.INVALID_EXECUTION_INPUT,
        )
    direction = source.source_regime_event_direction
    record = EntryExecutionRecordV2(
        source.source_regime_event_types,
        source.source_regime_event_bar_index,
        source.source_regime_event_timestamp,
        direction,
        source.pullback_bar_index,
        source.pullback_timestamp,
        source.ema_reference,
        source.confirmation_bar_index,
        source.confirmation_timestamp,
        index,
        timestamp,
        direction,
        price,
        EntryExecutionActionV2.BUY
        if direction is RegimeDirection.LONG
        else EntryExecutionActionV2.SELL_SHORT,
        source,
    )
    return replace(
        previous,
        execution_state=EntryExecutionStateV2.FILLED,
        status=EntryExecutionStatusV2.EVALUATED,
        execution=record,
    )


def execute_entry_open_v2(
    *,
    previous: EntryExecutionBookV2,
    confirmation: EntryConfirmationRecordV2,
    opening_bar: EntryExecutionOpenInputV2 | None,
) -> EntryExecutionBookV2:
    """Resolve only the next Open for a registered confirmation, idempotently.

    None reports definitive absence of q+1 (including end of data), not a poll
    before the Open becomes available. A later index expires without reading its
    timestamp or prices. Terminal records return the same book without reading
    any market field. No High, Low, Close, Volume or is_closed attribute is used.
    """
    if not isinstance(previous, EntryExecutionBookV2):
        raise EntryExecutionV2Error("execution requires the current execution book")
    entry = previous.for_confirmation(confirmation)
    advanced = _advance_open(entry, opening_bar)
    if advanced is entry:
        return previous
    return EntryExecutionBookV2(
        tuple(advanced if item is entry else item for item in previous.entries)
    )
