from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.cli.main import main
from agicore.trading.breakout_replay import BreakoutReplayConfig,BreakoutReplayError,calculate_breakout_metrics,create_breakout_replay,replay_breakout
from agicore.trading.market_replay import load_ohlcv_csv
from agicore.trading.market_replay import ReplayTrade
def _csv(path):
    vals=[10,10,10,12,13,9,8,14,15]
    rows=["timestamp,open,high,low,close,volume"]+[f"2026-08-01 00:{i:02d}:00,{v},{v+1},{v-1},{v},1" for i,v in enumerate(vals)]; path.write_text("\n".join(rows),encoding="utf-8")
def test_causal_breakout_bundle(tmp_path):
    path=tmp_path/"bars.csv"; _csv(path); one=create_breakout_replay(path,tmp_path/"one",BreakoutReplayConfig(2,0.5)); two=create_breakout_replay(path,tmp_path/"two",BreakoutReplayConfig(2,0.5))
    decisions=json.loads((one/"decisions.json").read_text()); trades=json.loads((one/"trades.json").read_text())
    assert all(d["prior_window_end_index"]==d["decision_bar_index"]-1 for d in decisions)
    assert all(t["cost_points"]==0.5 for t in trades); assert (one/"summary.json").read_text()==(two/"summary.json").read_text()
def test_breakout_cli_errors(tmp_path,capsys):
    path=tmp_path/"bars.csv"; _csv(path)
    assert main(["trading","replay-breakout",str(path),"--output-dir",str(tmp_path/"bad"),"--lookback-bars","1"])==2
    assert "at least 2" in capsys.readouterr().err
    with pytest.raises(BreakoutReplayError): create_breakout_replay(path,tmp_path/"x",BreakoutReplayConfig(99))

def test_public_breakout_metrics_calculates_closed_equity_drawdown():
    stamp=datetime(2026,8,1)
    trades=tuple(ReplayTrade("LONG",stamp+timedelta(minutes=i),100,stamp+timedelta(minutes=i+1),100+pnl,i,i+1,"END_OF_DATA") for i,pnl in enumerate((10,-15,5)))
    metrics=calculate_breakout_metrics(trades)
    assert metrics["net_total_pnl_points"]==0
    assert metrics["net_closed_equity_drawdown_points"]==15

def test_long_only_closes_on_short_signal_without_opening_short_and_preserves_causal_prefix(tmp_path):
    path=tmp_path/"bars.csv"; _csv(path); bars=tuple(load_ohlcv_csv(path))
    result=replay_breakout(bars,BreakoutReplayConfig(2,0.5,side_policy="LONG_ONLY"))
    trades,decisions=result["trades"],result["decisions"]
    assert [trade.side for trade in trades]==["LONG","LONG"]
    assert trades[0].exit_reason=="SIGNAL_REVERSAL" and trades[0].gross_pnl_points-trades[0].net_pnl_points==0.5
    assert trades[-1].exit_reason=="END_OF_DATA" and trades[-1].cost_points==0.5
    assert any(d["action"]=="EXIT_LONG_SIDE_POLICY" and d["policy_block_reason"]=="SHORT_BLOCKED_BY_LONG_ONLY" for d in decisions)
    assert all(d["action"]!="ENTER_SHORT" and d["action"]!="REVERSE_TO_SHORT" for d in decisions)
    extended=bars+(bars[-1].__class__(bars[-1].timestamp+timedelta(minutes=1),16,17,15,16,1),)
    later=replay_breakout(extended,BreakoutReplayConfig(2,0.5,side_policy="LONG_ONLY"))
    assert [d for d in decisions if d["decision_bar_index"]<len(bars)-1]==[d for d in later["decisions"] if d["decision_bar_index"]<len(bars)-1]

@pytest.mark.parametrize("side_policy",("BOTH","LONG_ONLY","SHORT_ONLY"))
def test_future_extension_preserves_determined_breakout_history_for_all_side_policies(tmp_path,side_policy):
    path=tmp_path/"bars.csv"; _csv(path); prefix=tuple(load_ohlcv_csv(path)); boundary=len(prefix)-1
    future=tuple(prefix[-1].__class__(prefix[-1].timestamp+timedelta(minutes=index),value,value+1,value-1,value,1) for index,value in enumerate((16,7,6,20),1))
    config=BreakoutReplayConfig(2,0.5,side_policy=side_policy)
    baseline,later=replay_breakout(prefix,config),replay_breakout(prefix+future,config)
    baseline_decisions=[d for d in baseline["decisions"] if d["decision_bar_index"]<boundary]
    later_decisions=[d for d in later["decisions"] if d["decision_bar_index"]<boundary]
    baseline_trades=[t for t in baseline["trades"] if t.exit_bar_index<=boundary and not (t.exit_reason=="END_OF_DATA" and t.exit_bar_index==boundary)]
    later_trades=[t for t in later["trades"] if t.exit_bar_index<=boundary and not (t.exit_reason=="END_OF_DATA" and t.exit_bar_index==boundary)]
    assert baseline_decisions and later_decisions and baseline_trades and later_trades
    assert baseline_decisions==later_decisions and baseline_trades==later_trades
    comparable_executions=[d for d in baseline_decisions+later_decisions if d["execution_bar_index"] is not None]
    assert comparable_executions and all(d["execution_bar_index"]==d["decision_bar_index"]+1 for d in comparable_executions)
    actions={d["action"] for d in baseline_decisions}
    if side_policy=="BOTH": assert any(action.startswith(("ENTER_","REVERSE_TO_")) for action in actions)
    if side_policy=="LONG_ONLY": assert "ENTER_LONG" in actions and "EXIT_LONG_SIDE_POLICY" in actions
    if side_policy=="SHORT_ONLY": assert "ENTER_SHORT" in actions and "EXIT_SHORT_SIDE_POLICY" in actions
    forbidden={"LONG_ONLY":("ENTER_SHORT","REVERSE_TO_SHORT"),"SHORT_ONLY":("ENTER_LONG","REVERSE_TO_LONG")}.get(side_policy,())
    assert all(d["action"] not in forbidden for d in later["decisions"])

def test_short_only_blocks_long_signal_and_finishes_short_at_end_of_data(tmp_path):
    path=tmp_path/"short.csv"
    values=[10,10,10,12,13,8,7,11,12,6,5]
    rows=["timestamp,open,high,low,close,volume"]+[f"2026-08-01 00:{i:02d}:00,{v},{v+1},{v-1},{v},1" for i,v in enumerate(values)]
    path.write_text("\n".join(rows),encoding="utf-8")
    result=replay_breakout(tuple(load_ohlcv_csv(path)),BreakoutReplayConfig(2,0.5,side_policy="SHORT_ONLY"))
    trades,decisions=result["trades"],result["decisions"]
    assert [trade.side for trade in trades]==["SHORT","SHORT"]
    assert trades[-1].exit_reason=="END_OF_DATA" and all(trade.cost_points==0.5 for trade in trades)
    assert any(d["action"]=="BLOCKED_BY_SIDE_POLICY" and d["policy_block_reason"]=="LONG_BLOCKED_BY_SHORT_ONLY" for d in decisions)
    assert any(d["action"]=="EXIT_SHORT_SIDE_POLICY" for d in decisions)
    assert all(d["action"]!="ENTER_LONG" and d["action"]!="REVERSE_TO_LONG" for d in decisions)

def test_default_side_policy_is_both_and_invalid_policy_is_rejected(tmp_path):
    path=tmp_path/"bars.csv"; _csv(path); bars=tuple(load_ohlcv_csv(path))
    assert BreakoutReplayConfig(2,0.5).side_policy=="BOTH"
    default=replay_breakout(bars,BreakoutReplayConfig(2,0.5)); explicit=replay_breakout(bars,BreakoutReplayConfig(2,0.5,side_policy="BOTH"))
    assert default["trades"]==explicit["trades"] and default["decisions"]==explicit["decisions"]
    with pytest.raises(ValueError,match="side_policy"):
        BreakoutReplayConfig(2,0.5,side_policy="INVALID")

def test_breakout_artifacts_publish_side_policy_and_change_run_id(tmp_path):
    path=tmp_path/"bars.csv"; _csv(path)
    both=create_breakout_replay(path,tmp_path/"both",BreakoutReplayConfig(2,0.5))
    long_only=create_breakout_replay(path,tmp_path/"long-only",BreakoutReplayConfig(2,0.5,side_policy="LONG_ONLY"))
    expected_files={"decisions.json","manifest.json","report.md","summary.json","trades.json"}
    artifacts=[]
    for bundle,policy in ((both,"BOTH"),(long_only,"LONG_ONLY")):
        summary=json.loads((bundle/"summary.json").read_text()); manifest=json.loads((bundle/"manifest.json").read_text())
        assert summary["schema_version"]==manifest["schema_version"]=="1.2"
        assert summary["strategy"]["side_policy"]==manifest["strategy"]["side_policy"]==policy
        assert f"- Side policy: {policy}" in (bundle/"report.md").read_text()
        assert set(manifest["generated_files"])==expected_files and all((bundle/name).is_file() for name in expected_files)
        artifacts.append(manifest)
    assert artifacts[0]["run_id"]!=artifacts[1]["run_id"]
