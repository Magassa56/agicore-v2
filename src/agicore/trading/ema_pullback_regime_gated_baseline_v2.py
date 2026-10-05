"""Synthetic-only deterministic assembly of the frozen V2 gates.

The caller supplies observations at their availability boundary. Open reads
only opening metadata/price; completed OHLC supplies the later stop observation
before the Close decision. No data loader, broker, strategy formula or tunable
business parameter belongs here. All market predicates remain in their gates.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, fields, is_dataclass, replace
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from pathlib import Path

from . import directional_impulse_v2 as impulse
from . import ema20_pullback_v2 as pullback
from . import ema_pullback_entry_confirmation_v2 as confirmation
from . import ema_pullback_entry_execution_v2 as execution
from . import ema_pullback_exit_policy_v2 as exits
from . import ema_pullback_fees_and_slippage_v2 as costs
from . import ema_pullback_initial_stop_v2 as initial_stop
from . import ema_pullback_open_position_signal_policy_v2 as position
from . import ema_pullback_pending_opportunity_policy_v2 as pending
from . import ema_pullback_risk_position_sizing_v2 as risk
from . import ema_pullback_structural_stop_trigger_fill_v2 as stop
from . import regime_context_v2 as context
from . import reversal_transition_v2 as reversal

STRATEGY_ID = "EMA_PULLBACK_V2_REGIME_GATED_BASELINE"
FORMALIZATION_VERSION = 1
MODE = "OFFLINE_DETERMINISTIC"
INPUT_DOMAIN = "SYNTHETIC_ONLY"
REAL_DATA_ACCESS = "FORBIDDEN"
OOS_ACCESS = "FORBIDDEN"
REPLAY = "FORBIDDEN"
BROKER_ACCESS = "FORBIDDEN"
PAPER_TRADING = "FORBIDDEN"
PARAMETER_OPTIMIZATION = "FORBIDDEN"

_COMPONENTS = (
    impulse,
    reversal,
    context,
    pullback,
    confirmation,
    risk,
    initial_stop,
    execution,
    stop,
    position,
    costs,
    exits,
    pending,
)


class BaselineAssemblyV2Error(ValueError):
    """Reject a corrupt phase/provenance without silently releasing ownership."""


def _canonical_value(value):
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Fraction):
        return {"numerator": value.numerator, "denominator": value.denominator}
    if isinstance(value, Decimal):
        return {"decimal": str(value)}
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, timedelta):
        return {"microseconds": (value.days * 86400 + value.seconds) * 1000000 + value.microseconds}
    if isinstance(value, bytes):
        return value.decode("utf-8")
    if is_dataclass(value):
        return {field.name: _canonical_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {key: _canonical_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_canonical_value(item) for item in value]
    if value is None or type(value) in (bool, int, str):
        return value
    raise BaselineAssemblyV2Error(f"noncanonical value: {type(value).__name__}")


def _canonical_bytes(value) -> bytes:
    return (
        json.dumps(
            _canonical_value(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        + "\n"
    ).encode("utf-8")


@dataclass(frozen=True)
class StrategyManifestV2:
    """Immutable canonical bytes; approval belongs to exact-head CI/merge evidence."""

    canonical_utf8: bytes

    def __post_init__(self) -> None:
        if (
            type(self.canonical_utf8) is not bytes
            or _canonical_bytes(json.loads(self.canonical_utf8)) != self.canonical_utf8
        ):
            raise BaselineAssemblyV2Error("manifest must be canonical UTF-8 JSON with a final LF")

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.canonical_utf8).hexdigest()


def build_strategy_manifest_v2() -> StrategyManifestV2:
    """Snapshot source code/constants only, never read market data or audit datasets."""
    components = []
    for module in _COMPONENTS:
        constants = {
            name: getattr(module, name)
            for name in getattr(module, "__all__", vars(module))
            if name.isupper() and not name.startswith("_") and name != "TYPE_CHECKING"
        }
        source = Path(module.__file__)
        components.append(
            {
                "name": source.name,
                "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                "constants": constants,
            }
        )
    return StrategyManifestV2(
        _canonical_bytes(
            {
                "strategy_id": STRATEGY_ID,
                "formalization_version": FORMALIZATION_VERSION,
                "mode": MODE,
                "input_domain": INPUT_DOMAIN,
                "instrument": risk.INSTRUMENT,
                "timeframe": "1 minute",
                "manifest_role": "CANONICAL_PRE_REPLAY_STRATEGY",
                "components": components,
                "assembly_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "prohibitions": {
                    name: globals()[name]
                    for name in (
                        "REAL_DATA_ACCESS",
                        "OOS_ACCESS",
                        "REPLAY",
                        "BROKER_ACCESS",
                        "PAPER_TRADING",
                        "PARAMETER_OPTIMIZATION",
                    )
                },
                "semantics": {
                    "entry": execution.ORDER_SEMANTICS,
                    "entry_point": execution.EXECUTION_POINT,
                    "stop": stop.STOP_ORDER_SEMANTICS,
                    "risk": risk.RISK_BUDGET_KIND,
                    "costs": "EFFECTIVE_FILL_PRICE_SLIPPAGE_ONCE_PLUS_PER_FILL_FEES",
                    "exit": (exits.EXIT_1, exits.EXIT_2),
                    "opening_exit_priority": "STRUCTURAL_STOP_BEFORE_PENDING_EMA20_EXIT",
                    "pending_opportunity_policy": pending.PENDING_OPPORTUNITY_LOCK,
                    "close_admission_order": "PENDING_RESOLUTION_BEFORE_NEW_REGIME_ADMISSION",
                },
                **{
                    name: getattr(exits, name)
                    for name in (
                        "TAKE_PROFIT",
                        "BREAKEVEN",
                        "TRAILING_STOP",
                        "TIME_EXIT",
                        "SESSION_EXIT",
                    )
                },
            }
        )
    )


@dataclass(frozen=True)
class RawRegimeDecisionV2:
    """Actual frozen evaluations, including the current unconfirmed rejection."""

    impulse: impulse.DirectionalImpulseEvaluation
    reversal: reversal.ReversalTransitionEventEvaluation | None
    current_rejection: reversal.ReversalTransitionEventEvaluation


@dataclass(frozen=True)
class FinalPositionRecordV2:
    """Native provenance plus delegated exact accounting, including unrealized trades."""

    position: position.PositionRecordV2
    accounting: costs.TradeCostRecordV2
    approved_quantity: int
    gross_price_pnl_usd: Fraction | None
    total_fees_usd: Fraction
    net_realized_pnl_usd: Fraction | None

    def __post_init__(self) -> None:
        if (
            not isinstance(self.position, position.PositionRecordV2)
            or not isinstance(self.accounting, costs.TradeCostRecordV2)
            or self.position.entry != self.accounting.sized_entry.execution
            or self.position.exit != (self.accounting.stop_fill or self.accounting.ema_exit_fill)
            or (
                self.approved_quantity,
                self.gross_price_pnl_usd,
                self.total_fees_usd,
                self.net_realized_pnl_usd,
            )
            != (
                self.accounting.quantity,
                self.accounting.gross_price_pnl_usd,
                self.accounting.total_fees_usd,
                self.accounting.net_realized_pnl_usd,
            )
        ):
            raise BaselineAssemblyV2Error(
                "final accounting must retain the actual native fill chain"
            )


@dataclass(frozen=True)
class RegimeGatedBaselineBookV2:
    """Caller-owned immutable state; each series has its own independent book."""

    policy: pending.PendingOpportunityPolicyBookV2
    exits: exits.ExitPolicyBookV2
    manifest: StrategyManifestV2
    closed_bars: tuple[impulse.DirectionalImpulseBarV2, ...] = ()
    raw_decisions: tuple[RawRegimeDecisionV2, ...] = ()
    latest_open: execution.EntryExecutionOpenV2 | None = None
    end_of_data: bool = False

    def __post_init__(self) -> None:
        if (
            not isinstance(self.policy, pending.PendingOpportunityPolicyBookV2)
            or not isinstance(self.exits, exits.ExitPolicyBookV2)
            or not isinstance(self.manifest, StrategyManifestV2)
            or self.policy.positions != self.exits.positions
            or self.policy.risks != self.exits.risk_sizing
            or type(self.closed_bars) is not tuple
            or type(self.raw_decisions) is not tuple
            or len(self.closed_bars) != len(self.raw_decisions)
            or type(self.end_of_data) is not bool
            or self.end_of_data != self.policy.end_of_data
            or self.end_of_data != self.exits.end_of_data
            or len(self.policy.positions.positions) != len(self.exits.costs.trades)
            or any(
                not any(
                    trade.sized_entry.execution == pos.entry for trade in self.exits.costs.trades
                )
                for pos in self.policy.positions.positions
            )
        ):
            raise BaselineAssemblyV2Error("assembly must retain synchronized canonical gate books")

    @property
    def final_positions(self) -> tuple[FinalPositionRecordV2, ...]:
        records = []
        for pos in self.policy.positions.positions:
            trade = next(
                item for item in self.exits.costs.trades if item.sized_entry.execution == pos.entry
            )
            records.append(
                FinalPositionRecordV2(
                    pos,
                    trade,
                    trade.quantity,
                    trade.gross_price_pnl_usd,
                    trade.total_fees_usd,
                    trade.net_realized_pnl_usd,
                )
            )
        return tuple(records)


def begin_regime_gated_baseline_v2(
    *, strategy_instance_id: str, series_id: str
) -> RegimeGatedBaselineBookV2:
    policy = pending.begin_pending_opportunity_policy_v2(
        strategy_instance_id=strategy_instance_id, series_id=series_id
    )
    return RegimeGatedBaselineBookV2(
        policy,
        exits.begin_exit_policy_v2(positions=policy.positions, risk_sizing=policy.risks),
        build_strategy_manifest_v2(),
    )


def _price_views(raw):
    return {
        index: pullback.EMA20PullbackBarV2(
            index, bar.timestamp_utc, bar.open, bar.high, bar.low, bar.close, bar.is_closed
        )
        for index, bar in raw.items()
    }


def _raw_regime_decision(raw, index, *, end_of_data=False):
    rejection_bars = {
        i: reversal.RejectionBarV2(i, b.timestamp_utc, b.close, b.is_closed, b.open, b.high, b.low)
        for i, b in raw.items()
    }
    return RawRegimeDecisionV2(
        impulse.evaluate_directional_impulse_event_v2(
            impulse_candidate_bar_index=index, bars_by_index=raw
        ),
        None
        if index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS not in raw
        else reversal.evaluate_reversal_transition_event_v2(
            rejection_candidate_bar_index=index - reversal.CONFIRMATION_WINDOW_CLOSED_BARS,
            closed_bar_index=index,
            bars_by_index=rejection_bars,
        ),
        reversal.evaluate_reversal_transition_event_v2(
            rejection_candidate_bar_index=index,
            closed_bar_index=index,
            bars_by_index=rejection_bars,
            end_of_data=end_of_data,
        ),
    )


def process_baseline_open_v2(
    *, previous: RegimeGatedBaselineBookV2, opening_bar: execution.EntryExecutionOpenInputV2
) -> RegimeGatedBaselineBookV2:
    """Entry/bind/breach, then existing-position stop gap before pending EMA exit."""
    if previous.end_of_data:
        return previous
    index = getattr(opening_bar, "bar_index", None)
    if previous.latest_open is not None and index == previous.latest_open.bar_index:
        return previous
    timestamp = getattr(opening_bar, "timestamp_utc", None)
    position._require_clock(index, timestamp)
    if previous.latest_open is not None and (
        not previous.closed_bars
        or previous.closed_bars[-1].bar_index != previous.latest_open.bar_index
        or index <= previous.latest_open.bar_index
        or timestamp <= previous.latest_open.timestamp_utc
    ):
        raise BaselineAssemblyV2Error("each new Open must follow the previous completed Close")
    opening = execution.EntryExecutionOpenV2(index, timestamp, getattr(opening_bar, "open", None))
    policy = pending.execute_pending_opportunity_open_v2(
        previous=previous.policy, opening_bar=opening
    )
    accounting = previous.exits.costs
    for sized in policy.risks.filled_entries[len(previous.exits.risk_sizing.filled_entries) :]:
        accounting = costs.account_entry_fill_v2(
            previous=accounting, risk_sizing=policy.risks, decision=sized.risk_decision
        )
        activation = policy.stop_activations.for_confirmation(sized.execution.confirmation)
        if activation.stop_triggered:
            accounting = costs.account_structural_stop_fill_v2(
                previous=accounting,
                risk_sizing=policy.risks,
                decision=sized.risk_decision,
                stops=policy.stop_activations,
            )
    exit_book = replace(
        previous.exits, positions=policy.positions, risk_sizing=policy.risks, costs=accounting
    )
    exit_book = exits.process_exit_policy_open_v2(previous=exit_book, observation=opening)
    policy = pending.adopt_pending_position_resolution_v2(
        previous=policy, positions=exit_book.positions
    )
    return replace(previous, policy=policy, exits=exit_book, latest_open=opening)


def process_baseline_close_v2(
    *, previous: RegimeGatedBaselineBookV2, closed_bar: impulse.DirectionalImpulseBarV2
) -> RegimeGatedBaselineBookV2:
    """Intrabar stop -> final position -> EMA exit -> pending resolution -> raw/admission.

    Completed OHLC reveals the adverse extreme no later than Close. Its frozen
    exit gate resolves the intrabar stop before reading Close/EMA for a signal;
    this assembly never invents the unavailable exact intrabar trigger time.
    """
    if previous.end_of_data:
        return previous
    index = getattr(closed_bar, "bar_index", None)
    if previous.closed_bars and index == previous.closed_bars[-1].bar_index:
        return previous
    opening = previous.latest_open
    if (
        not isinstance(closed_bar, impulse.DirectionalImpulseBarV2)
        or closed_bar.is_closed is not True
        or opening is None
        or (index, closed_bar.timestamp_utc) != (opening.bar_index, opening.timestamp_utc)
        or closed_bar.open != opening.open
    ):
        raise BaselineAssemblyV2Error("the completed bar must retain its own earlier Open")
    raw = {bar.bar_index: bar for bar in (*previous.closed_bars, closed_bar)}
    prices = _price_views(raw)
    exit_book = exits.process_exit_policy_close_v2(
        previous=previous.exits,
        closed_bar_index=index,
        closed_bar_timestamp=closed_bar.timestamp_utc,
        source_bar_closed=True,
        bars_by_index=prices,
        stop_observation=closed_bar,
    )
    policy = pending.adopt_pending_position_resolution_v2(
        previous=previous.policy, positions=exit_book.positions
    )
    telemetry = []

    def evaluate_raw():
        decision = _raw_regime_decision(raw, index)
        telemetry.append(decision)
        return (
            decision.impulse.event,
            None
            if decision.reversal is None or decision.reversal.event is None
            else decision.reversal.event.as_regime_event(),
        )

    policy = pending.advance_pending_opportunity_close_v2(
        previous=policy,
        closed_bar_index=index,
        closed_bar_timestamp=closed_bar.timestamp_utc,
        source_bar_closed=True,
        bars_by_index=prices,
        regime_events_at_close=evaluate_raw,
    )
    exit_book = replace(exit_book, positions=policy.positions, risk_sizing=policy.risks)
    return replace(
        previous,
        policy=policy,
        exits=exit_book,
        closed_bars=(*previous.closed_bars, closed_bar),
        raw_decisions=(*previous.raw_decisions, telemetry[0]),
    )


def finish_regime_gated_baseline_v2(
    *, previous: RegimeGatedBaselineBookV2
) -> RegimeGatedBaselineBookV2:
    """Seal actual end of input; no final-bar fill, liquidation or synthetic observation."""
    if previous.end_of_data:
        return previous
    if previous.latest_open is not None and (
        not previous.closed_bars
        or previous.closed_bars[-1].bar_index != previous.latest_open.bar_index
    ):
        raise BaselineAssemblyV2Error(
            "end of closed-bar input cannot silently skip an opened observation"
        )
    exit_book = exits.finish_exit_policy_v2(previous=previous.exits)
    policy = pending.adopt_pending_position_resolution_v2(
        previous=previous.policy, positions=exit_book.positions
    )
    if policy.positions.lifetime is not None:
        policy = replace(
            policy,
            positions=replace(
                policy.positions,
                lifetime=context.finish_regime_context_v2(policy.positions.lifetime),
            ),
        )
    policy = pending.finish_pending_opportunity_policy_v2(previous=policy)
    exit_book = replace(exit_book, positions=policy.positions, risk_sizing=policy.risks)
    raw_decisions = previous.raw_decisions
    if previous.closed_bars:
        raw = {b.bar_index: b for b in previous.closed_bars}
        last = _raw_regime_decision(raw, previous.closed_bars[-1].bar_index, end_of_data=True)
        raw_decisions = (*raw_decisions[:-1], last)
    return replace(
        previous, policy=policy, exits=exit_book, raw_decisions=raw_decisions, end_of_data=True
    )


def deterministic_baseline_snapshot_v2(book: RegimeGatedBaselineBookV2) -> bytes:
    """Canonical full histories, quantities, fills, terminal states, PnL and hash."""
    return _canonical_bytes(
        {
            "book": book,
            "final_positions": book.final_positions,
            "end_state": book.exits.end_state,
            "manifest_sha256": book.manifest.sha256,
        }
    )


def evaluate_synthetic_scenario_v2(
    *,
    strategy_instance_id: str,
    series_id: str,
    closed_bars: Iterable[impulse.DirectionalImpulseBarV2],
) -> RegimeGatedBaselineBookV2:
    """Only synthetic caller-supplied observations; no file/dataset/replay integration."""
    book = begin_regime_gated_baseline_v2(
        strategy_instance_id=strategy_instance_id, series_id=series_id
    )
    for bar in closed_bars:
        book = process_baseline_open_v2(previous=book, opening_bar=bar)
        book = process_baseline_close_v2(previous=book, closed_bar=bar)
    return finish_regime_gated_baseline_v2(previous=book)


__all__ = [
    "BROKER_ACCESS",
    "FORMALIZATION_VERSION",
    "INPUT_DOMAIN",
    "MODE",
    "OOS_ACCESS",
    "PAPER_TRADING",
    "PARAMETER_OPTIMIZATION",
    "REAL_DATA_ACCESS",
    "REPLAY",
    "STRATEGY_ID",
    "BaselineAssemblyV2Error",
    "FinalPositionRecordV2",
    "RawRegimeDecisionV2",
    "RegimeGatedBaselineBookV2",
    "StrategyManifestV2",
    "begin_regime_gated_baseline_v2",
    "build_strategy_manifest_v2",
    "deterministic_baseline_snapshot_v2",
    "evaluate_synthetic_scenario_v2",
    "finish_regime_gated_baseline_v2",
    "process_baseline_close_v2",
    "process_baseline_open_v2",
]
