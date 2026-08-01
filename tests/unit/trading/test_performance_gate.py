from __future__ import annotations
import json
import pytest
from agicore.cli.main import main
from agicore.trading.market_replay import MarketReplayConfig
from agicore.trading.performance_gate import PerformanceGateConfig, PerformanceGateError, create_performance_gate

def _csv(path):
    closes = [10,10,10,20,20,5,5,25,25,5,5,30,30,10,10,35,35]
    rows = ["timestamp,open,high,low,close,volume"] + [f"2026-07-{1+i//8:02d} {i%8:02d}:00:00,{x},{x+2},{x-1},{x},10" for i,x in enumerate(closes)]
    path.write_text("\n".join(rows), encoding="utf-8")

def test_gate_is_causal_subset_and_deterministic(tmp_path):
    path=tmp_path/"bars.csv"; _csv(path); cfg=MarketReplayConfig(2,3,0.5)
    one=create_performance_gate(path,tmp_path/"one",cfg,PerformanceGateConfig(2)); two=create_performance_gate(path,tmp_path/"two",cfg,PerformanceGateConfig(2))
    decisions=json.loads((one/"gate_decisions.json").read_text()); shadow=json.loads((one/"shadow_trades.json").read_text()); candidate=json.loads((one/"candidate_trades.json").read_text())
    assert all(d["gate_state"] == "WARMUP" and not d["execute_candidate"] for d in decisions[:2])
    assert {t["entry_timestamp"] for t in candidate} <= {t["entry_timestamp"] for t in shadow}
    assert all(d["trailing_last_trade_index"] is None or d["trailing_last_trade_index"] < d["shadow_trade_index"] for d in decisions)
    assert (one/"summary.json").read_text() == (two/"summary.json").read_text()

def test_gate_errors_and_cli(tmp_path, capsys):
    path=tmp_path/"bars.csv"; _csv(path)
    with pytest.raises(PerformanceGateError, match="must not exceed"):
        create_performance_gate(path,tmp_path/"x",MarketReplayConfig(2,3),PerformanceGateConfig(999))
    assert main(["trading","replay-performance-gate",str(path),"--output-dir",str(tmp_path/"bad"),"--fast-ema","2","--slow-ema","3","--gate-window-trades","1"]) == 2
    assert "at least 2" in capsys.readouterr().err
