"""Exact offline MNQ accounting for actual V2 entry, stop and EMA20 exit fills.

Base fills, risk decisions and quantities remain immutable. One adverse tick
is embedded in each distinct effective price; only explicit fees are deducted
from effective-price PnL. No market data, signal, order or new exit is created.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from fractions import Fraction
from typing import TYPE_CHECKING

from .ema20_pullback_v2 import _exact_price
from .ema_pullback_entry_execution_v2 import _confirmation_key
from .ema_pullback_exit_policy_v2 import EMA20ExitFillRecordV2
from .ema_pullback_risk_position_sizing_v2 import (
    MAX_CONTRACTS,
    MIN_CONTRACTS,
    POINT_VALUE_USD,
    TICK_SIZE,
    TICK_VALUE_USD,
    RiskPositionSizingBookV2,
    RiskSizedEntryRecordV2,
    RiskSizingDecisionRecordV2,
    RiskSizingDecisionV2,
)
from .ema_pullback_structural_stop_trigger_fill_v2 import (
    StructuralStopExecutionBookV2,
    StructuralStopFillRecordV2,
)
from .regime_context_v2 import RegimeDirection

if TYPE_CHECKING:
    from .ema_pullback_open_position_signal_policy_v2 import OpenPositionSignalPolicyBookV2

FEE_PER_CONTRACT_PER_FILL_USD = Fraction(51, 100)
ADVERSE_SLIPPAGE_TICKS_PER_FILL = 1
ADVERSE_SLIPPAGE_POINTS_PER_FILL = Fraction(1, 4)
SPREAD_MODEL = "ABSORBED_IN_SLIPPAGE"
EXTRA_SPREAD_CHARGE = Fraction(0)
SLIPPAGE_ACCOUNTED_EXACTLY_ONCE = True
NO_POST_CONFIRMATION_RESIZING = True
ROUND_TO_CENTS = ROUND_HALF_UP


class FeesAndSlippageV2Error(ValueError):
    """Refuse invalid accounting inputs or changed canonical fill provenance."""


class FillActionV2(StrEnum):
    """Offline labels; BUY actions pay up and SELL actions receive less."""

    BUY = "BUY"
    BUY_TO_COVER = "BUY_TO_COVER"
    SELL = "SELL"
    SELL_SHORT = "SELL_SHORT"


def _adverse_sign(action: FillActionV2) -> int:
    return 1 if action in (FillActionV2.BUY, FillActionV2.BUY_TO_COVER) else -1


@dataclass(frozen=True)
class FillCostRecordV2:
    """Separate exact prices and one fee for a single actual fill."""

    quantity: int
    action: FillActionV2
    base_fill_price: Fraction
    effective_fill_price_after_slippage: Fraction
    fee_usd: Fraction
    slippage_cost_usd: Fraction
    slippage_ticks: int = ADVERSE_SLIPPAGE_TICKS_PER_FILL

    def __post_init__(self) -> None:
        if (
            type(self.quantity) is not int
            or not MIN_CONTRACTS <= self.quantity <= MAX_CONTRACTS
            or not isinstance(self.action, FillActionV2)
            or not all(
                isinstance(value, Fraction)
                for value in (
                    self.base_fill_price,
                    self.effective_fill_price_after_slippage,
                    self.fee_usd,
                    self.slippage_cost_usd,
                )
            )
            or type(self.slippage_ticks) is not int
            or self.slippage_ticks != ADVERSE_SLIPPAGE_TICKS_PER_FILL
            or self.effective_fill_price_after_slippage
            != self.base_fill_price + _adverse_sign(self.action) * ADVERSE_SLIPPAGE_POINTS_PER_FILL
            or self.fee_usd != self.quantity * FEE_PER_CONTRACT_PER_FILL_USD
            or self.slippage_cost_usd != self.quantity * TICK_VALUE_USD
        ):
            raise FeesAndSlippageV2Error("fill costs must retain the exact frozen baseline")


def calculate_fill_cost_v2(
    *, base_fill_price: object, action: FillActionV2, quantity: int
) -> FillCostRecordV2:
    """Pure cost arithmetic; registration below requires an actual canonical fill.

    Convert finite Decimal/int/Fraction exactly. No rounding, spread debit,
    market lookup, tick-grid repair or post-fill price/quantity filter is added.
    """
    base = _exact_price(base_fill_price)
    if base is None or not isinstance(action, FillActionV2):
        raise FeesAndSlippageV2Error("cost arithmetic requires an exact base price and action")
    if type(quantity) is not int or not MIN_CONTRACTS <= quantity <= MAX_CONTRACTS:
        raise FeesAndSlippageV2Error("cost arithmetic requires the frozen approved quantity")
    return FillCostRecordV2(
        quantity=quantity,
        action=action,
        base_fill_price=base,
        effective_fill_price_after_slippage=base
        + _adverse_sign(action) * ADVERSE_SLIPPAGE_POINTS_PER_FILL,
        fee_usd=quantity * FEE_PER_CONTRACT_PER_FILL_USD,
        slippage_cost_usd=quantity * TICK_VALUE_USD,
    )


@dataclass(frozen=True)
class TradeCostRecordV2:
    """Full source chain with entry costs and at most one actual formal exit."""

    sized_entry: RiskSizedEntryRecordV2
    entry: FillCostRecordV2
    stop_fill: StructuralStopFillRecordV2 | None = None
    exit: FillCostRecordV2 | None = None
    ema_exit_fill: EMA20ExitFillRecordV2 | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.sized_entry, RiskSizedEntryRecordV2) or not isinstance(
            self.entry, FillCostRecordV2
        ):
            raise FeesAndSlippageV2Error("accounting requires the sized entry and its costs")
        execution = self.sized_entry.execution
        if (
            self.entry.quantity != self.quantity
            or self.entry.base_fill_price != execution.execution_price_before_costs
            or self.entry.action.value != execution.execution_action.value
            or self.entry.action
            is not (
                FillActionV2.BUY
                if self.direction is RegimeDirection.LONG
                else FillActionV2.SELL_SHORT
            )
        ):
            raise FeesAndSlippageV2Error("entry accounting cannot change the actual sized fill")
        if self.ema_exit_fill is not None:
            fill = self.ema_exit_fill
            if (
                self.stop_fill is not None
                or not isinstance(fill, EMA20ExitFillRecordV2)
                or not isinstance(self.exit, FillCostRecordV2)
                or fill.initial_stop_at_entry.execution != execution
                or fill.initial_stop_at_entry.initial_stop_record
                != self.sized_entry.risk_decision.initial_stop_record
                or fill.quantity != self.quantity
                or self.exit.quantity != self.quantity
                or self.exit.base_fill_price != fill.base_exit_fill_price
                or self.exit.action.value != fill.protective_action.value
            ):
                raise FeesAndSlippageV2Error(
                    "EMA accounting must retain the actual entry/exit chain"
                )
            return
        if self.stop_fill is None and self.exit is None:
            return
        if not isinstance(self.stop_fill, StructuralStopFillRecordV2) or not isinstance(
            self.exit, FillCostRecordV2
        ):
            raise FeesAndSlippageV2Error("exit costs require an actual formal stop fill")
        stop = self.sized_entry.risk_decision.initial_stop_record
        bound = self.stop_fill.initial_stop_at_entry
        if (
            bound.execution != execution
            or bound.initial_stop_record != stop
            or any(
                getattr(self.stop_fill, name) != getattr(stop, name)
                for name in (
                    "source_regime_event_types",
                    "source_regime_event_bar_index",
                    "source_regime_event_timestamp",
                    "pullback_bar_index",
                    "pullback_timestamp",
                    "ema_reference",
                    "confirmation_bar_index",
                    "confirmation_timestamp",
                    "structural_extreme",
                    "tick_size",
                    "stop_buffer_ticks",
                )
            )
            or (self.stop_fill.entry_bar_index, self.stop_fill.entry_bar_timestamp)
            != (execution.execution_bar_index, execution.execution_bar_timestamp)
            or self.stop_fill.source_regime_event_direction is not self.direction
            or self.stop_fill.entry_price != execution.execution_price_before_costs
            or self.stop_fill.initial_stop_price != stop.initial_stop_price
            or self.stop_fill.stop_state_at_entry is not bound.stop_state
            or self.exit.quantity != self.quantity
            or self.exit.base_fill_price != self.stop_fill.base_stop_fill_price
            or self.exit.action.value != self.stop_fill.protective_action.value
            or self.exit.action
            is not (
                FillActionV2.SELL
                if self.direction is RegimeDirection.LONG
                else FillActionV2.BUY_TO_COVER
            )
        ):
            raise FeesAndSlippageV2Error("stop accounting must retain the entry/stop provenance")

    @property
    def quantity(self) -> int:
        """Always the Risk Engine quantity frozen at Close[q]."""
        return self.sized_entry.quantity

    @property
    def direction(self) -> RegimeDirection:
        """The original trade direction, independent of the costs."""
        return self.sized_entry.risk_decision.direction

    @property
    def exit_type(self) -> str | None:
        """Preserve the actual terminal exit reason, without double realization."""
        if self.ema_exit_fill is not None:
            return self.ema_exit_fill.exit_reason
        return None if self.stop_fill is None else "STRUCTURAL_STOP"

    @property
    def total_fees_usd(self) -> Fraction:
        """Charge entry immediately and an exit only when that fill exists."""
        return self.entry.fee_usd + (Fraction(0) if self.exit is None else self.exit.fee_usd)

    @property
    def diagnostic_total_slippage_cost_usd(self) -> Fraction:
        """Diagnostic only: already embedded in the effective-price PnL."""
        return self.entry.slippage_cost_usd + (
            Fraction(0) if self.exit is None else self.exit.slippage_cost_usd
        )

    @property
    def gross_price_pnl_usd(self) -> Fraction | None:
        """Effective-price PnL, without an invented mark or exit for open positions."""
        if self.exit is None:
            return None
        price_change = (
            self.exit.effective_fill_price_after_slippage
            - self.entry.effective_fill_price_after_slippage
        )
        sign = 1 if self.direction is RegimeDirection.LONG else -1
        return sign * price_change * POINT_VALUE_USD * self.quantity

    @property
    def net_realized_pnl_usd(self) -> Fraction | None:
        """Subtract fees only; never subtract diagnostic slippage or extra spread."""
        gross = self.gross_price_pnl_usd
        return None if gross is None else gross - self.total_fees_usd


@dataclass(frozen=True)
class FeesAndSlippageBookV2:
    """Immutable accounting history for one strategy instance and series."""

    strategy_instance_id: str
    series_id: str
    trades: tuple[TradeCostRecordV2, ...] = ()

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (self.strategy_instance_id, self.series_id)
        ) or not isinstance(self.trades, tuple):
            raise FeesAndSlippageV2Error("accounting book requires immutable history and scope")
        if not all(isinstance(item, TradeCostRecordV2) for item in self.trades) or len(
            {item.sized_entry.risk_decision.opportunity_key for item in self.trades}
        ) != len(self.trades):
            raise FeesAndSlippageV2Error("accounting history cannot duplicate an opportunity")

    def for_decision(self, decision: RiskSizingDecisionRecordV2) -> TradeCostRecordV2:
        """Retrieve accounted source, refusing altered or unknown risk provenance."""
        if not isinstance(decision, RiskSizingDecisionRecordV2):
            raise FeesAndSlippageV2Error("lookup requires a risk decision")
        for record in self.trades:
            if record.sized_entry.risk_decision.opportunity_key == decision.opportunity_key:
                if record.sized_entry.risk_decision != decision:
                    raise FeesAndSlippageV2Error("accounted risk provenance cannot change")
                return record
        raise FeesAndSlippageV2Error("entry must have an actual accounted fill")


def account_entry_fill_v2(
    *,
    previous: FeesAndSlippageBookV2,
    risk_sizing: RiskPositionSizingBookV2,
    decision: RiskSizingDecisionRecordV2,
) -> FeesAndSlippageBookV2:
    """Record costs once for the actual risk-approved fill; non-fills pay nothing."""
    if not isinstance(previous, FeesAndSlippageBookV2) or not isinstance(
        risk_sizing, RiskPositionSizingBookV2
    ):
        raise FeesAndSlippageV2Error("entry accounting requires accounting and risk books")
    if (previous.strategy_instance_id, previous.series_id) != (
        risk_sizing.strategy_instance_id,
        risk_sizing.series_id,
    ):
        raise FeesAndSlippageV2Error("accounting and risk books must have the same scope")
    registered = risk_sizing.for_decision(decision)
    if registered.decision is RiskSizingDecisionV2.REJECT:
        return previous
    sized = next(
        (item for item in risk_sizing.filled_entries if item.risk_decision == registered), None
    )
    if sized is None:
        return previous
    for record in previous.trades:
        if record.sized_entry.risk_decision.opportunity_key == registered.opportunity_key:
            if record.sized_entry != sized:
                raise FeesAndSlippageV2Error("accounted entry provenance cannot change")
            return previous
    costs = calculate_fill_cost_v2(
        base_fill_price=sized.execution.execution_price_before_costs,
        action=FillActionV2(sized.execution.execution_action),
        quantity=registered.approved_quantity,
    )
    return replace(previous, trades=(*previous.trades, TradeCostRecordV2(sized, costs)))


def account_structural_stop_fill_v2(
    *,
    previous: FeesAndSlippageBookV2,
    risk_sizing: RiskPositionSizingBookV2,
    decision: RiskSizingDecisionRecordV2,
    stops: StructuralStopExecutionBookV2 | None,
) -> FeesAndSlippageBookV2:
    """Add one exit cost/PnL only for FILLED_STOP, preserving the PR #293 base fill.

    Entry costs can already exist; repeated accounting or stale unfilled stop
    snapshots cannot double-charge or erase them. No OHLCV/mark price is read.
    """
    current = account_entry_fill_v2(previous=previous, risk_sizing=risk_sizing, decision=decision)
    if stops is None:
        return current
    if not isinstance(stops, StructuralStopExecutionBookV2):
        raise FeesAndSlippageV2Error("exit accounting requires the canonical stop book")
    if not any(item.sized_entry.risk_decision == decision for item in current.trades):
        return current
    record = current.for_decision(decision)
    confirmation = record.sized_entry.execution.confirmation
    if not any(
        _confirmation_key(item.initial_stop_at_entry.initial_stop_record.confirmation)
        == _confirmation_key(confirmation)
        for item in stops.entries
    ):
        return current
    evaluation = stops.for_confirmation(confirmation)
    if not evaluation.stop_triggered:
        return current
    fill = evaluation.fill
    if record.ema_exit_fill is not None:
        raise FeesAndSlippageV2Error("a position already realized by EMA cannot also stop out")
    if record.stop_fill is not None:
        if record.stop_fill != fill:
            raise FeesAndSlippageV2Error("accounted stop provenance cannot change")
        return current
    costs = calculate_fill_cost_v2(
        base_fill_price=fill.base_stop_fill_price,
        action=FillActionV2(fill.protective_action),
        quantity=record.quantity,
    )
    updated = replace(record, stop_fill=fill, exit=costs)
    return replace(
        current, trades=tuple(updated if item is record else item for item in current.trades)
    )


def account_ema20_exit_fill_v2(
    *,
    previous: FeesAndSlippageBookV2,
    risk_sizing: RiskPositionSizingBookV2,
    decision: RiskSizingDecisionRecordV2,
    positions: OpenPositionSignalPolicyBookV2,
) -> FeesAndSlippageBookV2:
    """Account one actual EMA MARKET exit with the unchanged PR #296 cost arithmetic."""
    from .ema_pullback_open_position_signal_policy_v2 import OpenPositionSignalPolicyBookV2

    current = account_entry_fill_v2(previous=previous, risk_sizing=risk_sizing, decision=decision)
    if not isinstance(positions, OpenPositionSignalPolicyBookV2) or (
        positions.strategy_instance_id,
        positions.series_id,
    ) != (current.strategy_instance_id, current.series_id):
        raise FeesAndSlippageV2Error("EMA accounting requires the canonical scoped position book")
    if not any(item.sized_entry.risk_decision == decision for item in current.trades):
        return current
    record = current.for_decision(decision)
    position = next(
        (item for item in positions.positions if item.entry == record.sized_entry.execution), None
    )
    if position is None or not isinstance(position.exit, EMA20ExitFillRecordV2):
        return current
    fill = position.exit
    if record.ema_exit_fill is not None:
        if record.ema_exit_fill != fill:
            raise FeesAndSlippageV2Error("accounted EMA exit provenance cannot change")
        return current
    if record.stop_fill is not None:
        raise FeesAndSlippageV2Error("a stopped position cannot acquire a second EMA exit")
    costs = calculate_fill_cost_v2(
        base_fill_price=fill.base_exit_fill_price,
        action=FillActionV2(fill.protective_action),
        quantity=record.quantity,
    )
    updated = replace(record, ema_exit_fill=fill, exit=costs)
    return replace(
        current, trades=tuple(updated if item is record else item for item in current.trades)
    )


def report_usd_cents_v2(value: Fraction) -> Decimal:
    """Round HALF_UP only at the reporting boundary, retaining exact internal PnL.

    Integer arithmetic avoids precision-dependent Decimal division/quantization
    even for repeating rationals, very large values and tiny negative values.
    """
    if not isinstance(value, Fraction):
        raise FeesAndSlippageV2Error("monetary reporting requires the exact internal Fraction")
    magnitude = abs(value) * 100
    cents = (2 * magnitude.numerator + magnitude.denominator) // (2 * magnitude.denominator)
    sign = "-" if value < 0 else ""
    return Decimal(f"{sign}{cents // 100}.{cents % 100:02d}")


__all__ = [
    "ADVERSE_SLIPPAGE_POINTS_PER_FILL",
    "ADVERSE_SLIPPAGE_TICKS_PER_FILL",
    "EXTRA_SPREAD_CHARGE",
    "FEE_PER_CONTRACT_PER_FILL_USD",
    "NO_POST_CONFIRMATION_RESIZING",
    "POINT_VALUE_USD",
    "ROUND_TO_CENTS",
    "SLIPPAGE_ACCOUNTED_EXACTLY_ONCE",
    "SPREAD_MODEL",
    "TICK_SIZE",
    "TICK_VALUE_USD",
    "FeesAndSlippageBookV2",
    "FeesAndSlippageV2Error",
    "FillActionV2",
    "FillCostRecordV2",
    "TradeCostRecordV2",
    "account_ema20_exit_fill_v2",
    "account_entry_fill_v2",
    "account_structural_stop_fill_v2",
    "calculate_fill_cost_v2",
    "report_usd_cents_v2",
]
