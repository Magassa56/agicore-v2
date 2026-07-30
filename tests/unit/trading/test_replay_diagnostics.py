"""Tests for deterministic replay diagnostics."""
from __future__ import annotations

import json

import pytest

from agicore.cli.main import main
from agicore.trading.market_replay import MarketReplayConfig
from agicore.trading.replay_diagnostics import (
    ReplayDiagnosticsConfig,
    ReplayDiagnosticsError,
    _rolling_summary,
    create_replay_diagnostics,
)


def _csv(path) -> None:
    closes = [10, 10, 10, 20, 20, 5, 5, 25, 25, 5, 5, 30, 30, 10, 10, 35, 35]
    rows = ["timestamp,open,high,low,close,volume"]
    for index, close in enumerate(closes):
        rows.append(f"2026-07-{1 + index // 8:02d} {index % 8:02d}:00:00,{close},{close + 2},{close - 1},{close},10")
    path.write_text("\n".join(rows), encoding="utf-8")


def test_diagnostics_breakdowns_reconcile_and_rolling_is_deterministic(tmp_path) -> None:
    path = tmp_path / "bars.csv"
    _csv(path)
    config = MarketReplayConfig(fast_ema=2, slow_ema=3, round_trip_cost_points=0.5)
    first = create_replay_diagnostics(path, tmp_path / "one", config, ReplayDiagnosticsConfig(2))
    second = create_replay_diagnostics(path, tmp_path / "two", config, ReplayDiagnosticsConfig(2))
    summary = json.loads((first / "summary.json").read_text(encoding="utf-8"))
    breakdowns = json.loads((first / "breakdowns.json").read_text(encoding="utf-8"))
    rolling = json.loads((first / "rolling.json").read_text(encoding="utf-8"))
    total = summary["performance"]["net_total_pnl_points"]
    for name in ("by_side", "by_entry_month", "by_entry_iso_week", "by_entry_hour", "by_clock_block", "by_volatility_regime"):
        assert sum(item["net_total_pnl_points"] for item in breakdowns[name].values()) == pytest.approx(total)
    assert len(rolling) == summary["performance"]["total_trades"] - 1
    assert (first / "summary.json").read_text(encoding="utf-8") == (second / "summary.json").read_text(encoding="utf-8")


def test_window_validation_run_id_and_cli(tmp_path, capsys) -> None:
    path = tmp_path / "bars.csv"
    _csv(path)
    config = MarketReplayConfig(fast_ema=2, slow_ema=3)
    first = create_replay_diagnostics(path, tmp_path / "one", config, ReplayDiagnosticsConfig(2))
    changed = create_replay_diagnostics(path, tmp_path / "two", config, ReplayDiagnosticsConfig(3))
    assert json.loads((first / "manifest.json").read_text(encoding="utf-8"))["run_id"] != json.loads((changed / "manifest.json").read_text(encoding="utf-8"))["run_id"]
    assert main(["trading", "diagnose-replay", str(path), "--output-dir", str(tmp_path / "bad"), "--fast-ema", "2", "--slow-ema", "3", "--rolling-window-trades", "1"]) == 2
    assert "at least 2" in capsys.readouterr().err
    with pytest.raises(ReplayDiagnosticsError, match="must not exceed"):
        create_replay_diagnostics(path, tmp_path / "large", config, ReplayDiagnosticsConfig(999))


def test_rolling_profit_factor_extremes_are_finite_or_null() -> None:
    rolling = [
        {"net_total_pnl_points": 1.0, "net_profit_factor": 1.5, "net_closed_equity_drawdown_points": 2.0},
        {"net_total_pnl_points": -1.0, "net_profit_factor": 0.25, "net_closed_equity_drawdown_points": 3.0},
        {"net_total_pnl_points": 0.0, "net_profit_factor": None, "net_closed_equity_drawdown_points": 1.0},
    ]
    summary = _rolling_summary(rolling, 2)
    assert summary["best_window_net_profit_factor"] == 1.5
    assert summary["worst_window_net_profit_factor"] == 0.25
    assert _rolling_summary([
        {"net_total_pnl_points": 0.0, "net_profit_factor": None, "net_closed_equity_drawdown_points": 0.0}
    ], 2)["best_window_net_profit_factor"] is None


def test_report_and_manifest_always_keep_filename_and_volatility_warning(tmp_path) -> None:
    path = tmp_path / "positive.csv"
    _csv(path)
    bundle = create_replay_diagnostics(
        path,
        tmp_path / "bundle",
        MarketReplayConfig(fast_ema=2, slow_ema=3, round_trip_cost_points=0.5),
        ReplayDiagnosticsConfig(2),
    )
    report = (bundle / "report.md").read_text(encoding="utf-8")
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    summary_text = (bundle / "summary.json").read_text(encoding="utf-8")
    warning = "volatility regime thresholds are calculated retrospectively on the complete sample and are not a directly deployable rule"
    assert "File: positive.csv" in report
    assert str(path.resolve()) not in report
    assert warning in report
    assert warning in manifest["warnings"]
    assert "NaN" not in summary_text
    assert "Infinity" not in summary_text
