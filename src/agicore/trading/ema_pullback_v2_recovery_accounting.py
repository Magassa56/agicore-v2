"""Append-only exact marks and the unchanged DEVELOPMENT native reporting contract."""

from __future__ import annotations

from dataclasses import fields
from fractions import Fraction

from . import ema_pullback_v2_development_replay as reference
from .ema_pullback_v2_recovery_evidence import CanonicalEncoderV1


class RecoveryMarksV1:
    """Incremental closed net equity; open marks include only the paid entry fee."""

    def __init__(self):
        self.realized = Fraction()
        self.closed_keys = set()
        self.samples = []
        self.peak = Fraction()
        self.maximum_drawdown = Fraction()

    def append(self, live, bar):
        """Exactly one marked sample for each actual, completed observation."""
        for trade in live.exits.costs.trades:
            key = trade.sized_entry.execution.confirmation.confirmation_bar_index
            if trade.net_realized_pnl_usd is not None and key not in self.closed_keys:
                self.closed_keys.add(key)
                self.realized += trade.net_realized_pnl_usd
        unrealized = Fraction()
        for trade in live.exits.costs.trades:
            if trade.exit is None:
                sign = 1 if trade.direction is reference.assembly.context.RegimeDirection.LONG else -1
                unrealized += (
                    sign * (Fraction(bar.close) - trade.entry.effective_fill_price_after_slippage)
                    * reference.assembly.costs.POINT_VALUE_USD * trade.quantity - trade.entry.fee_usd
                )
        point = reference.screening.MarkedEquityPoint(
            bar.bar_index, bar.timestamp_utc, self.realized, unrealized)
        self.peak = max(self.peak, point.marked_equity_usd)
        self.maximum_drawdown = max(self.maximum_drawdown, self.peak - point.marked_equity_usd)
        self.samples.append(point)


def build_native_result_v1(engine, bars, marks, identity, bindings):
    """Produce every frozen result field; delegate screening and native provenance."""
    r, a = reference, reference.assembly
    book = engine.snapshot()
    lifecycle = r._lifecycle(book, "SYNTHETIC_ONLY")
    records = [r._trade_record(p, lifecycle) for p in book.final_positions]
    closed = [v for v in records if v["net_realized_pnl_usd"] is not None]
    opened = [v for v in records if v["net_realized_pnl_usd"] is None]
    times = tuple(b.timestamp_utc for b in bars)
    screen = r.screening.evaluate_screening(
        bindings.protocol, run_identity=identity, dataset_role=r.DATASET_ROLE,
        closed_trades=tuple(r.screening.ClosedTrade(
            i, v["entry_timestamp"], v["exit_timestamp"], v["net_realized_pnl_usd"])
            for i, v in enumerate(closed, 1)),
        marked_equity=tuple(marks.samples), closed_bar_timestamps=times,
        open_trades_at_end=len(opened),
    )
    r._require(screen.maximum_marked_equity_drawdown_usd == marks.maximum_drawdown,
               "incremental marked drawdown mismatch")
    costs = r._aggregate_costs(closed)
    actual = book.exits.costs.trades
    metrics = {
        **{f.name: getattr(screen.metrics, f.name) for f in fields(screen.metrics)},
        **{k: v for k, v in costs.items() if k != "diagnostic_slippage_cost_usd"},
        "directional_impulses": sum(e.event_type is a.context.RegimeEventType.DIRECTIONAL_IMPULSE_EVENT
                                    for e in lifecycle["events"]),
        "reversal_transitions": sum(e.event_type is a.context.RegimeEventType.REVERSAL_TRANSITION_EVENT
                                    for e in lifecycle["events"]),
        "admitted_contexts": len(lifecycle["contexts"]),
        "ambiguous_contexts": sum(d.composition.status is a.context.RegimeContextStatus.AMBIGUOUS
                                  for d in book.policy.signal_decisions),
        "expired_contexts": sum(c.state.value.startswith("EXPIRED_") for c in lifecycle["contexts"]),
        "qualified_ema20_pullbacks": len(lifecycle["pullbacks"]),
        "suppressed_pending_opportunities": sum(s.suppression_reason == "PENDING_OPPORTUNITY_ALREADY_ACTIVE"
                                                for s in lifecycle["suppressions"]),
        "suppressed_position_open_events": sum(s.suppression_reason == "POSITION_ALREADY_OPEN"
                                              for s in lifecycle["suppressions"]),
        "confirmations": len(lifecycle["confirmations"]),
        "risk_approvals": sum(d.decision is a.risk.RiskSizingDecisionV2.APPROVE
                              for d in lifecycle["risk_decisions"]),
        "risk_rejections": sum(d.decision is a.risk.RiskSizingDecisionV2.REJECT
                               for d in lifecycle["risk_decisions"]),
        "quantity_1_count": sum(t.quantity == 1 for t in actual),
        "quantity_2_count": sum(t.quantity == 2 for t in actual),
        "entry_fills": len(lifecycle["entries"]), "open_trades_at_end": len(opened),
        "long_entry_fills": sum(t.direction is a.context.RegimeDirection.LONG for t in actual),
        "short_entry_fills": sum(t.direction is a.context.RegimeDirection.SHORT for t in actual),
        "total_fees_usd": sum((t.total_fees_usd for t in actual), Fraction()),
        "closed_trade_fees_usd": costs["total_fees_usd"],
        "open_entry_fees_usd": sum((v["entry_fee_usd"] for v in opened), Fraction()),
        "diagnostic_total_slippage_cost_usd": sum(
            (t.diagnostic_total_slippage_cost_usd for t in actual), Fraction()),
        "maximum_marked_equity_drawdown_usd": screen.maximum_marked_equity_drawdown_usd,
        "unrealized_pnl_at_end_usd": marks.samples[-1].unrealized_pnl_usd,
        "marked_equity_at_end_usd": marks.samples[-1].marked_equity_usd,
    }
    span = times[-1] - times[0]
    duration = (span.days * 86400 + span.seconds) * 1_000_000 + span.microseconds
    groups = [[], [], []]
    for trade in closed:
        delta = trade["exit_timestamp"] - times[0]
        offset = (delta.days * 86400 + delta.seconds) * 1_000_000 + delta.microseconds
        groups[min(2, offset * 3 // duration)].append(trade)
    segments = []
    for segment, group in zip(screen.segments, groups, strict=True):
        segment_costs = r._aggregate_costs(group)
        segment_costs["diagnostic_total_slippage_cost_usd"] = segment_costs.pop(
            "diagnostic_slippage_cost_usd")
        segments.append({
            **{f.name: getattr(segment.metrics, f.name) for f in fields(segment.metrics)},
            **segment_costs, "label": segment.label, "profitable": segment.profitable,
            "start_offset_microseconds": segment.start_offset_microseconds,
            "end_offset_microseconds": segment.end_offset_microseconds,
        })
    result = r._native({
        "strategy_id": a.STRATEGY_ID, "formalization_version": a.FORMALIZATION_VERSION,
        "dataset_role": r.DATASET_ROLE, "dataset_id": book.policy.positions.series_id,
        "run_identity": identity, "run_id_sha256": identity.sha256,
        "dataset_lineage_manifest_sha256": r.DATASET_LINEAGE_MANIFEST_SHA256,
        "dataset_first_timestamp_utc": times[0], "dataset_last_timestamp_utc": times[-1],
        "metrics": metrics, "segments": segments, "closed_trade_records": closed,
        "open_trade_records": opened,
        "marked_equity_samples": [{
            **{f.name: getattr(p, f.name) for f in fields(p)},
            "marked_equity_usd": p.marked_equity_usd,
        } for p in marks.samples],
        "immutable_lifecycle_records": lifecycle,
        "diagnostic_trades_per_trading_day_session": r._diagnostics(bars, closed, opened, bindings),
        "verdict": screen.verdict, "failed_criteria": screen.failed_criteria,
        "next_gate": screen.next_gate, "oos_accessed": False, "parameter_changes": False,
        "production_proof": False,
    })
    result["output_sha256"] = CanonicalEncoderV1().sha256(result)
    return result
