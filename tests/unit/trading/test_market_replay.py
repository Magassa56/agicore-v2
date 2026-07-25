"""Tests for deterministic local OHLCV market replay."""
from __future__ import annotations

import json

import pytest

from agicore.cli.main import main
from agicore.trading.market_replay import (
    MarketReplayConfig,
    MarketReplayError,
    calculate_ema,
    create_market_replay,
    load_ohlcv_csv,
    replay_ema_crossover,
)


def _csv(path, closes, *, delimiter=",", bom=False, reverse=False) -> None:
    rows = []
    for index, close in enumerate(closes):
        rows.append(f"2026-07-01 09:{index:02d}:00{delimiter}{close}{delimiter}{close + 1}{delimiter}{close - 1}{delimiter}{close}{delimiter}10")
    if reverse:
        rows.reverse()
    path.write_text("timestamp{}open{}high{}low{}close{}volume\n{}".format(delimiter, delimiter, delimiter, delimiter, delimiter, "\n".join(rows)), encoding="utf-8-sig" if bom else "utf-8")


def test_parse_bom_delimiter_sort_and_validation(tmp_path) -> None:
    path = tmp_path / "bars.csv"
    _csv(path, [10, 11, 12], delimiter=";", bom=True, reverse=True)
    bars = load_ohlcv_csv(path)
    assert [bar.close for bar in bars] == [10.0, 11.0, 12.0]
    path.write_text("timestamp,open,high,low,close,volume\n2026-07-01 09:00:00,1,0.5,0.5,1,0\n", encoding="utf-8")
    with pytest.raises(MarketReplayError, match="Inconsistent"):
        load_ohlcv_csv(path)


def test_ema_and_next_bar_execution_without_future_data(tmp_path) -> None:
    path = tmp_path / "bars.csv"
    _csv(path, [10, 10, 10, 20, 20, 20])
    bars = load_ohlcv_csv(path)
    assert calculate_ema([10, 20, 20], 2) == pytest.approx([10, 16.6666666667, 18.8888888889])
    result = replay_ema_crossover(bars, MarketReplayConfig(fast_ema=2, slow_ema=3))
    assert result.trades[0].side == "LONG"
    assert result.trades[0].entry_bar_index == 4
    assert result.trades[0].entry_price == bars[4].open
    assert result.trades[0].exit_reason == "END_OF_DATA"


def test_long_short_reversals_pnl_and_closed_drawdown(tmp_path) -> None:
    path = tmp_path / "bars.csv"
    _csv(path, [10, 10, 10, 20, 20, 5, 5, 25, 25])
    result = replay_ema_crossover(load_ohlcv_csv(path), MarketReplayConfig(fast_ema=2, slow_ema=3))
    assert {trade.side for trade in result.trades} == {"LONG", "SHORT"}
    bundle = create_market_replay(path, tmp_path / "bundle", MarketReplayConfig(fast_ema=2, slow_ema=3))
    summary = json.loads((bundle / "summary.json").read_text(encoding="utf-8"))
    ledger = json.loads((bundle / "trades.json").read_text(encoding="utf-8"))
    assert summary["performance"]["total_trades"] == len(ledger)
    assert all(item["exit_reason"] in {"SIGNAL_REVERSAL", "END_OF_DATA"} for item in ledger)
    assert "max_closed_equity_drawdown_points" in summary["performance"]


def test_bundle_determinism_privacy_conflict_and_cli(tmp_path, capsys) -> None:
    path = tmp_path / "bars.csv"
    _csv(path, [10] * 49 + [20, 20])
    first = create_market_replay(path, tmp_path / "one", MarketReplayConfig())
    second = create_market_replay(path, tmp_path / "two", MarketReplayConfig())
    changed = create_market_replay(path, tmp_path / "three", MarketReplayConfig(fast_ema=18, slow_ema=50))
    manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_id"] != json.loads((changed / "manifest.json").read_text(encoding="utf-8"))["run_id"]
    for name in ("report.md", "summary.json", "trades.json", "manifest.json"):
        content = (first / name).read_text(encoding="utf-8")
        assert content == (second / name).read_text(encoding="utf-8")
        assert str(path.resolve()) not in content
    with pytest.raises(MarketReplayError, match="already exists"):
        create_market_replay(path, first, MarketReplayConfig())
    cli_dir = tmp_path / "cli"
    assert main(["trading", "replay-market", str(path), "--output-dir", str(cli_dir)]) == 0
    assert main(["trading", "replay-market", str(path), "--output-dir", str(tmp_path / "bad"), "--fast-ema", "50", "--slow-ema", "50"]) == 2
    assert "less than" in capsys.readouterr().err


def test_insufficient_and_duplicate_data_leave_no_bundle(tmp_path) -> None:
    path = tmp_path / "small.csv"
    _csv(path, [10, 11, 12])
    with pytest.raises(MarketReplayError, match="At least"):
        create_market_replay(path, tmp_path / "bundle", MarketReplayConfig(fast_ema=2, slow_ema=3))
    assert not (tmp_path / "bundle").exists()
    path.write_text("timestamp,open,high,low,close,volume\n2026-07-01 09:00:00,1,2,0.5,1,0\n2026-07-01 09:00:00,1,2,0.5,1,0\n", encoding="utf-8")
    with pytest.raises(MarketReplayError, match="duplicate"):
        load_ohlcv_csv(path)
