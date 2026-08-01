"""Deterministic offline causal price-channel breakout replay."""
from __future__ import annotations
import hashlib, json, math
from dataclasses import dataclass
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from .local_bundle import LocalBundleError, deterministic_json, publish_local_bundle, sha256_file
from .market_replay import OHLCVBar, ReplayTrade, load_ohlcv_csv

_WARNINGS = ["strategy is retrospective", "no future result is guaranteed", "parameters are pre-registered and not optimized", "the five existing contracts are development data", "out-of-sample validation is mandatory before any paper trading"]
class BreakoutReplayError(ValueError): pass
@dataclass(frozen=True)
class BreakoutReplayConfig:
    lookback_bars: int = 240
    round_trip_cost_points: float = 1.0
    position_size: int = 1
    execution: str = "next_bar_open"
    def __post_init__(self):
        if self.lookback_bars < 2: raise ValueError("lookback_bars must be at least 2")
        if not math.isfinite(self.round_trip_cost_points) or self.round_trip_cost_points < 0: raise ValueError("round_trip_cost_points must be greater than or equal to 0")

def create_breakout_replay(csv_path: str | Path, output_dir: str | Path, config: BreakoutReplayConfig) -> Path:
    input_path, final_dir = Path(csv_path).resolve(), Path(output_dir).resolve()
    if not input_path.exists(): raise BreakoutReplayError(f"OHLCV CSV file not found: {input_path}")
    if not input_path.is_file(): raise BreakoutReplayError(f"OHLCV CSV path is not a file: {input_path}")
    if final_dir.exists(): raise BreakoutReplayError(f"Output directory already exists: {final_dir}")
    try:
        bars = tuple(load_ohlcv_csv(input_path)); result = replay_breakout(bars, config)
        return publish_local_bundle(final_dir, _files(input_path.name, sha256_file(input_path), result))
    except BreakoutReplayError: raise
    except (LocalBundleError, OSError, ValueError) as exc: raise BreakoutReplayError(str(exc)) from exc

def replay_breakout(bars: tuple[OHLCVBar, ...], config: BreakoutReplayConfig) -> dict[str, object]:
    if len(bars) < config.lookback_bars + 1: raise BreakoutReplayError(f"At least {config.lookback_bars + 1} OHLCV bars are required")
    ordered = tuple(sorted(bars, key=lambda b: b.timestamp)); pos = None; pending = None; trades=[]; decisions=[]
    for i, bar in enumerate(ordered):
        if pending:
            signal, decision = pending
            if pos: trades.append(_close(pos, bar, i, "SIGNAL_REVERSAL", config.round_trip_cost_points))
            pos=(signal, bar.timestamp, bar.open, i); decisions.append({**decision,"action": "ENTER_"+signal if decision["position_before"]=="FLAT" else "REVERSE_TO_"+signal,"execution_bar_index":i,"execution_timestamp":bar.timestamp.isoformat(),"execution_price":bar.open}); pending=None
        if i < config.lookback_bars: continue
        prior=ordered[i-config.lookback_bars:i]; high=max(x.high for x in prior); low=min(x.low for x in prior)
        signal = "LONG" if bar.close > high else "SHORT" if bar.close < low else None
        if not signal or signal == (pos[0] if pos else "FLAT"): continue
        decision={"decision_bar_index":i,"decision_timestamp":bar.timestamp.isoformat(),"prior_window_start_index":i-config.lookback_bars,"prior_window_end_index":i-1,"prior_high":high,"prior_low":low,"close":bar.close,"position_before":pos[0] if pos else "FLAT","signal":signal}
        if i == len(ordered)-1: decisions.append({**decision,"action":"IGNORED_NO_NEXT_BAR","execution_bar_index":None,"execution_timestamp":None,"execution_price":None})
        else: pending=(signal, decision)
    if pos: trades.append(_close(pos, ordered[-1], len(ordered)-1, "END_OF_DATA", config.round_trip_cost_points, ordered[-1].close))
    return {"bars":ordered,"trades":tuple(trades),"decisions":decisions,"config":config}

def _close(pos, bar, index, reason, cost, price=None):
    side, entry_time, entry_price, entry_index=pos
    return ReplayTrade(side,entry_time,entry_price,bar.timestamp,bar.open if price is None else price,entry_index,index,reason,cost)
def _metrics(trades):
    net=[t.net_pnl_points for t in trades]; gross=[t.gross_pnl_points for t in trades]; wins=[x for x in net if x>0]; losses=[x for x in net if x<0]; eq=peak=dd=0.0
    for x in net: eq+=x; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"total_trades":len(trades),"winning_trades":len(wins),"losing_trades":len(losses),"breakeven_trades":sum(x==0 for x in net),"win_rate":len(wins)/len(net) if net else 0.0,"gross_total_pnl_points":sum(gross),"net_total_pnl_points":sum(net),"gross_average_trade_points":sum(gross)/len(gross) if gross else 0.0,"net_average_trade_points":sum(net)/len(net) if net else 0.0,"gross_profit_factor":sum(x for x in gross if x>0)/abs(sum(x for x in gross if x<0)) if any(x<0 for x in gross) else None,"net_profit_factor":sum(wins)/abs(sum(losses)) if losses else None,"net_closed_equity_drawdown_points":dd,"largest_net_gain_points":max(net,default=0.0),"largest_net_loss_points":min(net,default=0.0)}
def _trade(i,t): return {"trade_index":i,"side":t.side,"entry_timestamp":t.entry_timestamp.isoformat(),"entry_price":t.entry_price,"exit_timestamp":t.exit_timestamp.isoformat(),"exit_price":t.exit_price,"entry_bar_index":t.entry_bar_index,"exit_bar_index":t.exit_bar_index,"exit_reason":t.exit_reason,"gross_pnl_points":t.gross_pnl_points,"cost_points":t.cost_points,"net_pnl_points":t.net_pnl_points}
def _files(filename, input_hash, result):
    bars,trades,decisions,cfg=result["bars"],result["trades"],result["decisions"],result["config"]; perf=_metrics(trades); by={s:_metrics(tuple(t for t in trades if t.side==s)) for s in ("LONG","SHORT")}
    strategy={"name":"CAUSAL_PRICE_CHANNEL_BREAKOUT","lookback_bars":cfg.lookback_bars,"execution":"next_bar_open","position_size":1,"round_trip_cost_points":cfg.round_trip_cost_points,"pyramiding":False,"channel_rule":"prior_completed_bars_only","exit_rule":"opposite_breakout_or_end_of_data"}; sh=hashlib.sha256(json.dumps(strategy,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    stats={"long_breakout_count":sum(d["signal"]=="LONG" for d in decisions),"short_breakout_count":sum(d["signal"]=="SHORT" for d in decisions),"long_entry_count":sum(t.side=="LONG" for t in trades),"short_entry_count":sum(t.side=="SHORT" for t in trades),"reversal_count":sum(d["action"].startswith("REVERSE") for d in decisions),"ignored_last_bar_signal_count":sum(d["action"]=="IGNORED_NO_NEXT_BAR" for d in decisions),"end_of_data_close_count":sum(t.exit_reason=="END_OF_DATA" for t in trades)}
    summary={"schema_version":"1.0","strategy":strategy,"market_data":{"bar_count":len(bars),"first_timestamp":bars[0].timestamp.isoformat(),"last_timestamp":bars[-1].timestamp.isoformat()},"performance":perf,"by_side":by,"signal_statistics":stats}; manifest={"schema_version":"1.0","run_id":f"breakout-{input_hash[:12]}-{sh[:8]}","input_filename":filename,"input_sha256":input_hash,"strategy_sha256":sh,"agicore_version":_version(),"status":"completed","generated_files":["decisions.json","manifest.json","report.md","summary.json","trades.json"],"warnings":_WARNINGS}
    report="\n".join(["# Causal Breakout Replay","",*[f"> Warning: {w}" for w in _WARNINGS],"",f"- File: {filename}",f"- Period: {summary['market_data']['first_timestamp']} to {summary['market_data']['last_timestamp']}",f"- Bars: {len(bars)}",f"- Lookback: {cfg.lookback_bars}",f"- Cost: {cfg.round_trip_cost_points:.2f}","- Channel: prior completed bars only","- Execution: next-bar-open",f"- Trades: {perf['total_trades']}",f"- Gross PnL: {perf['gross_total_pnl_points']:.2f}",f"- Net PnL: {perf['net_total_pnl_points']:.2f}",f"- Net PF: {perf['net_profit_factor']}",f"- Net drawdown: {perf['net_closed_equity_drawdown_points']:.2f}",f"- LONG net: {by['LONG']['net_total_pnl_points']:.2f}",f"- SHORT net: {by['SHORT']['net_total_pnl_points']:.2f}",f"- Breakouts: {stats['long_breakout_count']+stats['short_breakout_count']}",f"- Reversals: {stats['reversal_count']}",""])
    return {"report.md":report,"summary.json":deterministic_json(summary),"trades.json":deterministic_json([_trade(i,t) for i,t in enumerate(trades,1)]),"decisions.json":deterministic_json(decisions),"manifest.json":deterministic_json(manifest)}
def _version():
    try:return version("agicore")
    except PackageNotFoundError:return "unknown"
__all__=["BreakoutReplayConfig","BreakoutReplayError","create_breakout_replay","replay_breakout"]
