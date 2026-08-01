from __future__ import annotations
import json
import pytest
from agicore.cli.main import main
from agicore.trading.breakout_replay import BreakoutReplayConfig,BreakoutReplayError,create_breakout_replay
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
