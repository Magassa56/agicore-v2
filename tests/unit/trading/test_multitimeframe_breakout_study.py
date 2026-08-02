from __future__ import annotations
import json
from datetime import datetime, timedelta
import pytest
from agicore.trading.multitimeframe_breakout_study import TIMEFRAMES, MultiTimeframeStudyError, create_multitimeframe_breakout_study

def _csv(path, offset=0):
    start=datetime(2026,8,1,0,0); rows=["timestamp,open,high,low,close,volume"]
    for i in range(270):
        value=100+offset+(i%20)
        rows.append(f"{(start+timedelta(minutes=i)).isoformat(sep=' ')},{value},{value+1},{value-1},{value},1")
    path.write_text("\n".join(rows),encoding="utf-8")

def test_study_has_all_pre_registered_timeframes_and_is_deterministic(tmp_path):
    a,b=tmp_path/"a.csv",tmp_path/"b.csv"; _csv(a); _csv(b,10)
    one=create_multitimeframe_breakout_study([b,a],tmp_path/"one",1.0); two=create_multitimeframe_breakout_study([a,b],tmp_path/"two",1.0)
    results=json.loads((one/"results.json").read_text()); summary=json.loads((one/"summary.json").read_text())
    assert TIMEFRAMES=={1:240,5:48,15:16,30:8}; assert {x["timeframe_minutes"] for x in results}==set(TIMEFRAMES)
    assert "best_timeframe" not in summary and "winner" not in summary
    assert (one/"results.json").read_text()==(two/"results.json").read_text()

def test_study_rejects_duplicate_basename_and_negative_cost(tmp_path):
    a=tmp_path/"a.csv"; _csv(a)
    with pytest.raises(MultiTimeframeStudyError): create_multitimeframe_breakout_study([a],tmp_path/"x",-1)
    with pytest.raises(MultiTimeframeStudyError): create_multitimeframe_breakout_study([],tmp_path/"y",1)
