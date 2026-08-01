from __future__ import annotations
import json
import pytest
from agicore.cli.main import main
from agicore.trading.ohlcv_resampler import OHLCVResamplerError, resample_ohlcv

def _csv(path, count=30, gap=None):
    rows=["timestamp,open,high,low,close,volume"]
    for i in range(count):
        if i != gap: rows.append(f"2026-08-01 00:{i:02d}:00,{10+i},{11+i},{9+i},{10.5+i},1")
    path.write_text("\n".join(rows),encoding="utf-8")

def test_aggregate_complete_buckets_and_manifest(tmp_path):
    source=tmp_path/"input.csv"; _csv(source); output=tmp_path/"five.csv"; resample_ohlcv(source,output,5)
    lines=output.read_text().splitlines(); assert len(lines)==7; assert lines[1].startswith("2026-08-01 00:00:00;10.0;15.0;9.0;14.5;5.0")
    manifest=json.loads((tmp_path/"five.csv.manifest.json").read_text()); assert manifest["output_bar_count"]==6
    assert resample_ohlcv(source,tmp_path/"fifteen.csv",15); assert resample_ohlcv(source,tmp_path/"thirty.csv",30)

def test_incomplete_gap_errors_and_cli(tmp_path,capsys):
    source=tmp_path/"input.csv"; _csv(source,10,2); output=tmp_path/"out.csv"; resample_ohlcv(source,output,5)
    assert json.loads((tmp_path/"out.csv.manifest.json").read_text())["dropped_incomplete_bucket_count"]==1
    with pytest.raises(OHLCVResamplerError): resample_ohlcv(source,output,5)
    assert main(["trading","resample-ohlcv",str(source),"--output",str(tmp_path/"bad.csv"),"--minutes","4"])==2
    assert "5, 15, 30" in capsys.readouterr().err
