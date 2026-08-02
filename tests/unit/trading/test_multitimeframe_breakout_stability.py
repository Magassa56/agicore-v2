from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest

from agicore.cli.main import main
from agicore.trading.multitimeframe_breakout_stability import MultiTimeframeStabilityError, create_multitimeframe_breakout_stability_study


def _csv(path, count=600, future_offset=0):
    start = datetime(2026, 8, 1)
    rows = ["timestamp,open,high,low,close,volume"]
    for index in range(count):
        value = 100 + (index % 20) + (future_offset if index >= 600 else 0)
        rows.append(f"{(start + timedelta(minutes=index)).isoformat(sep=' ')},{value},{value + 1},{value - 1},{value},1")
    path.write_text("\n".join(rows), encoding="utf-8")


def test_chronological_stability_bundle_is_canonical_and_deterministic(tmp_path):
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"; _csv(a, 650); _csv(b, 650)
    one = create_multitimeframe_breakout_stability_study([b, a], tmp_path / "one", round_trip_cost_points=1.0, window_bars=300)
    two = create_multitimeframe_breakout_stability_study([a, b], tmp_path / "two", round_trip_cost_points=1.0, window_bars=300)
    results = json.loads((one / "results.json").read_text())
    summary = json.loads((one / "summary.json").read_text())
    assert (one / "results.json").read_text() == (two / "results.json").read_text()
    assert [row["timeframe_minutes"] for row in results[:4]] == [1, 5, 15, 30]
    assert all(results[index]["window_index"] <= results[index + 1]["window_index"] or results[index]["input_filename"] != results[index + 1]["input_filename"] for index in range(len(results) - 1))
    first = [row for row in results if row["input_filename"] == "a.csv" and row["window_index"] == 0][0]
    second = [row for row in results if row["input_filename"] == "a.csv" and row["window_index"] == 1][0]
    assert first["source_end_timestamp"] < second["source_start_timestamp"]
    assert summary["dropped_incomplete_window_bar_count"] == {"a.csv": 50, "b.csv": 50}
    text = json.dumps({"summary": summary, "results": results})
    assert not any(word in text.lower() for word in ("best", "winner", "ranking", "recommended", "selected", "score"))


def test_completed_window_metrics_do_not_depend_on_future_bars(tmp_path):
    baseline_dir, changed_dir = tmp_path / "baseline", tmp_path / "changed"; baseline_dir.mkdir(); changed_dir.mkdir()
    baseline, changed = baseline_dir / "same.csv", changed_dir / "same.csv"; _csv(baseline, 900); _csv(changed, 900, future_offset=500)
    left = create_multitimeframe_breakout_stability_study([baseline], tmp_path / "left", round_trip_cost_points=0.0, window_bars=300)
    right = create_multitimeframe_breakout_stability_study([changed], tmp_path / "right", round_trip_cost_points=0.0, window_bars=300)
    left_rows = json.loads((left / "results.json").read_text()); right_rows = json.loads((right / "results.json").read_text())
    fields = ("source_start_timestamp", "source_end_timestamp", "source_bar_count", "timeframe_minutes", "lookback_bars", "output_bar_count", "dropped_incomplete_bucket_count", "boundary_forced_close_count", "total_trades", "net_total_pnl_points", "net_closed_equity_drawdown_points", "win_rate")
    for timeframe in (1, 5, 15, 30):
        before = next(row for row in left_rows if row["window_index"] == 0 and row["timeframe_minutes"] == timeframe)
        after = next(row for row in right_rows if row["window_index"] == 0 and row["timeframe_minutes"] == timeframe)
        assert {field: before[field] for field in fields} == {field: after[field] for field in fields}


def test_insufficient_windows_and_cli_validation_are_controlled(tmp_path, capsys):
    source = tmp_path / "bars.csv"; _csv(source, 599)
    with pytest.raises(MultiTimeframeStabilityError, match="At least two complete"):
        create_multitimeframe_breakout_stability_study([source], tmp_path / "bundle", window_bars=300)
    assert main(["trading", "study-breakout-stability", str(source), "--output-dir", str(tmp_path / "bad"), "--window-bars", "0"]) == 2
    assert "strictly positive" in capsys.readouterr().err
    _csv(source, 538)
    with pytest.raises(MultiTimeframeStabilityError, match="Window 0 timeframe 30 has insufficient bars"):
        create_multitimeframe_breakout_stability_study([source], tmp_path / "too-short", window_bars=269)


def test_stability_cli_creates_bundle(tmp_path):
    source = tmp_path / "bars.csv"; _csv(source, 600)
    output = tmp_path / "bundle"
    assert main(["trading", "study-breakout-stability", str(source), "--output-dir", str(output), "--window-bars", "300"]) == 0
    assert (output / "results.json").is_file()


def test_boundary_forced_close_is_counted_and_next_window_starts_flat(tmp_path):
    source = tmp_path / "boundary.csv"
    start = datetime(2026, 8, 1); rows = ["timestamp,open,high,low,close,volume"]
    for index in range(600):
        value = 100 if index < 240 or index >= 300 else 102
        rows.append(f"{(start + timedelta(minutes=index)).isoformat(sep=' ')},{value},{value + 1},{value - 1},{value},1")
    source.write_text("\n".join(rows), encoding="utf-8")
    bundle = create_multitimeframe_breakout_stability_study([source], tmp_path / "bundle", round_trip_cost_points=0.5, window_bars=300)
    results = json.loads((bundle / "results.json").read_text())
    summary = json.loads((bundle / "summary.json").read_text())
    first = next(row for row in results if row["window_index"] == 0 and row["timeframe_minutes"] == 1)
    second = next(row for row in results if row["window_index"] == 1 and row["timeframe_minutes"] == 1)
    assert first["total_trades"] == 1
    assert first["boundary_forced_close_count"] == 1
    assert first["gross_total_pnl_points"] - first["net_total_pnl_points"] == 0.5
    assert first["net_total_pnl_points"] == -0.5
    assert second["total_trades"] == 0
    timeframe_rows = [row for row in results if row["timeframe_minutes"] == 1]
    aggregate = summary["by_timeframe"]["1"]
    assert aggregate["total_trades"] == sum(row["total_trades"] for row in timeframe_rows)
    assert aggregate["net_total_pnl_points"] == sum(row["net_total_pnl_points"] for row in timeframe_rows)
