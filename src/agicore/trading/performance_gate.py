"""Causal, offline gate over the closed trades of the existing EMA replay."""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import MarketReplayConfig, MarketReplayError, MarketReplayResult, ReplayTrade, load_ohlcv_csv, replay_ema_crossover

_WARNINGS = [
    "candidate is retrospective and the gate does not prove future profitability",
    "the five contracts already studied are development data",
    "validation on a never-used contract remains mandatory",
]


class PerformanceGateError(ValueError):
    """Raised when a causal performance-gate bundle cannot be created."""


@dataclass(frozen=True)
class PerformanceGateConfig:
    """Fixed trailing-history gate configuration."""

    gate_window_trades: int = 100

    def __post_init__(self) -> None:
        if self.gate_window_trades < 2:
            raise ValueError("gate_window_trades must be at least 2")


def create_performance_gate(
    csv_path: str | Path, output_dir: str | Path, strategy: MarketReplayConfig, gate: PerformanceGateConfig
) -> Path:
    """Replay explicit OHLCV then atomically publish shadow and candidate results."""
    input_path = Path(csv_path).resolve()
    if not input_path.exists():
        raise PerformanceGateError(f"OHLCV CSV file not found: {input_path}")
    if not input_path.is_file():
        raise PerformanceGateError(f"OHLCV CSV path is not a file: {input_path}")
    final_dir = Path(output_dir).resolve()
    if final_dir.exists():
        raise PerformanceGateError(f"Output directory already exists: {final_dir}")
    try:
        replay = replay_ema_crossover(load_ohlcv_csv(input_path), strategy)
        if gate.gate_window_trades > len(replay.trades):
            raise PerformanceGateError("gate_window_trades must not exceed the number of shadow trades")
        payload = evaluate_performance_gate(replay, strategy, gate)
        return publish_local_bundle(final_dir, _files(input_path.name, sha256_file(input_path), payload))
    except PerformanceGateError:
        raise
    except (MarketReplayError, LocalBundleError, OSError, ValueError) as exc:
        raise PerformanceGateError(str(exc)) from exc


def evaluate_performance_gate(replay: MarketReplayResult, strategy: MarketReplayConfig, gate: PerformanceGateConfig) -> dict[str, object]:
    """Apply the strictly-prior shadow-trade gate without changing shadow trades."""
    shadow = tuple(sorted(replay.trades, key=lambda trade: (trade.entry_timestamp, trade.exit_timestamp)))
    decisions: list[dict[str, object]] = []
    candidate: list[ReplayTrade] = []
    for index, trade in enumerate(shadow, start=1):
        eligible = [(prior_index, prior) for prior_index, prior in enumerate(shadow, start=1) if prior.exit_timestamp < trade.entry_timestamp]
        if len(eligible) < gate.gate_window_trades:
            decision = _decision(index, trade, len(eligible), gate.gate_window_trades, "WARMUP", None, None, None, False, "INSUFFICIENT_HISTORY")
        else:
            window = eligible[-gate.gate_window_trades:]
            trailing = sum(prior.net_pnl_points for _, prior in window)
            on = trailing > 0
            decision = _decision(index, trade, len(eligible), gate.gate_window_trades, "ON" if on else "OFF", window[0][0], window[-1][0], trailing, on, None if on else "TRAILING_NET_PNL_NOT_POSITIVE")
            if on:
                candidate.append(trade)
        decisions.append(decision)
    return {"replay": replay, "shadow": shadow, "candidate": tuple(candidate), "decisions": decisions, "strategy": strategy, "gate": gate}


def _decision(index, trade, count, window, state, first, last, trailing, execute, reason):
    return {"shadow_trade_index": index, "side": trade.side, "entry_timestamp": trade.entry_timestamp.isoformat(), "exit_timestamp": trade.exit_timestamp.isoformat(), "eligible_prior_trade_count": count, "gate_window_trades": window, "gate_state": state, "trailing_first_trade_index": first, "trailing_last_trade_index": last, "trailing_net_pnl_points": trailing, "execute_candidate": execute, "exclusion_reason": reason}


def _metrics(trades: tuple[ReplayTrade, ...] | list[ReplayTrade]) -> dict[str, object]:
    net = [trade.net_pnl_points for trade in trades]
    gross = [trade.gross_pnl_points for trade in trades]
    wins, losses = [p for p in net if p > 0], [p for p in net if p < 0]
    equity = peak = drawdown = 0.0
    for pnl in net:
        equity += pnl; peak = max(peak, equity); drawdown = max(drawdown, peak - equity)
    return {"total_trades": len(trades), "gross_total_pnl_points": sum(gross), "net_total_pnl_points": sum(net), "net_average_trade_points": sum(net) / len(net) if net else 0.0, "winning_trades": len(wins), "losing_trades": len(losses), "breakeven_trades": sum(p == 0 for p in net), "win_rate": len(wins) / len(net) if net else 0.0, "net_profit_factor": sum(wins) / abs(sum(losses)) if losses else None, "net_closed_equity_drawdown_points": drawdown}


def _trade_data(index: int, trade: ReplayTrade) -> dict[str, object]:
    return {"trade_index": index, "side": trade.side, "entry_timestamp": trade.entry_timestamp.isoformat(), "entry_price": trade.entry_price, "exit_timestamp": trade.exit_timestamp.isoformat(), "exit_price": trade.exit_price, "entry_bar_index": trade.entry_bar_index, "exit_bar_index": trade.exit_bar_index, "exit_reason": trade.exit_reason, "gross_pnl_points": trade.gross_pnl_points, "cost_points": trade.cost_points, "net_pnl_points": trade.net_pnl_points}


def _files(filename: str, input_hash: str, payload: dict[str, object]) -> dict[str, str]:
    shadow, candidate, decisions = payload["shadow"], payload["candidate"], payload["decisions"]
    strategy, gate, replay = payload["strategy"], payload["gate"], payload["replay"]
    assert isinstance(strategy, MarketReplayConfig) and isinstance(gate, PerformanceGateConfig) and isinstance(replay, MarketReplayResult)
    shadow_metrics, candidate_metrics = _metrics(shadow), _metrics(candidate)
    side = {name: _metrics(tuple(trade for trade in candidate if trade.side == name)) for name in ("LONG", "SHORT")}
    states = {state: sum(item["gate_state"] == state for item in decisions) for state in ("WARMUP", "ON", "OFF")}
    strategy_data = {"name": "EMA_CROSSOVER_WITH_CAUSAL_PERFORMANCE_GATE", "fast_ema": strategy.fast_ema, "slow_ema": strategy.slow_ema, "execution": "next_bar_open", "position_size": 1, "round_trip_cost_points": strategy.round_trip_cost_points, "gate_window_trades": gate.gate_window_trades, "gate_rule": "trailing_shadow_net_pnl_strictly_positive", "attribution_rule": "shadow_exit_timestamp_strictly_before_candidate_entry"}
    strategy_hash = _hash({key: strategy_data[key] for key in ("fast_ema", "slow_ema", "execution", "position_size", "round_trip_cost_points")})
    gate_hash = _hash({"gate_window_trades": gate.gate_window_trades, "gate_rule": strategy_data["gate_rule"], "timestamp_rule": strategy_data["attribution_rule"], "warmup": "skip"})
    summary = {"schema_version": "1.0", "strategy": strategy_data, "market_data": {"bar_count": len(replay.bars), "first_timestamp": replay.bars[0].timestamp.isoformat(), "last_timestamp": replay.bars[-1].timestamp.isoformat()}, "shadow_performance": shadow_metrics, "candidate_performance": candidate_metrics, "candidate_by_side": side, "gate_statistics": {"total_shadow_trades": len(shadow), "warmup_trade_count": states["WARMUP"], "gate_on_trade_count": states["ON"], "gate_off_trade_count": states["OFF"], "executed_candidate_trade_count": len(candidate), "skipped_shadow_trade_count": len(shadow) - len(candidate), "execution_rate": len(candidate) / len(shadow) if shadow else 0.0, "gate_on_rate_after_warmup": states["ON"] / (states["ON"] + states["OFF"]) if states["ON"] + states["OFF"] else 0.0, "first_candidate_entry_timestamp": candidate[0].entry_timestamp.isoformat() if candidate else None, "last_candidate_exit_timestamp": candidate[-1].exit_timestamp.isoformat() if candidate else None}, "comparison": {"net_pnl_improvement_points": candidate_metrics["net_total_pnl_points"] - shadow_metrics["net_total_pnl_points"], "drawdown_reduction_points": shadow_metrics["net_closed_equity_drawdown_points"] - candidate_metrics["net_closed_equity_drawdown_points"], "trade_reduction_count": len(shadow) - len(candidate), "trade_reduction_rate": (len(shadow) - len(candidate)) / len(shadow) if shadow else 0.0, "net_profit_factor_change": _delta(candidate_metrics["net_profit_factor"], shadow_metrics["net_profit_factor"]), "net_average_trade_change": candidate_metrics["net_average_trade_points"] - shadow_metrics["net_average_trade_points"]}}
    manifest = {"schema_version": "1.0", "run_id": f"performance-gate-{input_hash[:12]}-{strategy_hash[:8]}-{gate_hash[:8]}", "input_filename": filename, "input_sha256": input_hash, "strategy_sha256": strategy_hash, "gate_sha256": gate_hash, "agicore_version": _version(), "status": "completed", "generated_files": ["candidate_trades.json", "gate_decisions.json", "manifest.json", "report.md", "shadow_trades.json", "summary.json"], "warnings": _WARNINGS}
    return {"report.md": _report(filename, summary), "summary.json": deterministic_json(summary), "shadow_trades.json": deterministic_json([_trade_data(i, t) for i, t in enumerate(shadow, 1)]), "candidate_trades.json": deterministic_json([_trade_data(i, t) for i, t in enumerate(candidate, 1)]), "gate_decisions.json": deterministic_json(decisions), "manifest.json": deterministic_json(manifest)}


def _delta(new, old): return None if new is None or old is None else new - old
def _hash(value): return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
def _version():
    try: return version("agicore")
    except PackageNotFoundError: return "unknown"
def _report(filename, summary):
    s, sh, ca, gs, co = summary["strategy"], summary["shadow_performance"], summary["candidate_performance"], summary["gate_statistics"], summary["comparison"]
    return "\n".join(["# Causal Performance Gate", "", *[f"> Warning: {x}" for x in _WARNINGS], "", f"- File: {filename}", f"- EMA: {s['fast_ema']} / {s['slow_ema']}", f"- Cost: {s['round_trip_cost_points']:.2f}", f"- Gate window: {s['gate_window_trades']}", "- Rule: strictly positive trailing shadow net PnL from trades closed before entry", f"- Shadow net PnL: {sh['net_total_pnl_points']:.2f}", f"- Candidate net PnL: {ca['net_total_pnl_points']:.2f}", f"- Net PnL difference: {co['net_pnl_improvement_points']:.2f}", f"- Drawdown difference: {co['drawdown_reduction_points']:.2f}", f"- WARMUP / ON / OFF: {gs['warmup_trade_count']} / {gs['gate_on_trade_count']} / {gs['gate_off_trade_count']}", f"- Execution rate: {gs['execution_rate']:.2%}", ""])

__all__ = ["PerformanceGateConfig", "PerformanceGateError", "create_performance_gate", "evaluate_performance_gate"]
