"""Tests for deterministic offline historical risk rule simulations."""
from __future__ import annotations

import json
from datetime import datetime

import pytest

from agicore.cli.main import main
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.risk_rule_simulator import (
    BlockReason,
    RiskRuleConfig,
    RiskSimulationError,
    create_risk_rule_simulation,
    simulate_risk_rules,
)


def _trade(day: int, hour: int, pnl: float, minute: int = 0) -> NormalizedTrade:
    when = datetime(2026, 7, day, hour, minute)
    return NormalizedTrade(entry_time=when, exit_time=when, pnl=pnl)


def _csv(path, rows: list[tuple[int, int, float]]) -> None:
    lines = ["Entry time,Exit time,Profit"]
    for day, hour, pnl in rows:
        value = f"({abs(pnl)})" if pnl < 0 else str(pnl)
        lines.append(f"2026-07-{day:02d} {hour:02d}:00:00,2026-07-{day:02d} {hour:02d}:01:00,{value}")
    path.write_text("\n".join(lines), encoding="utf-8")


def test_daily_loss_and_consecutive_stops_keep_triggering_trade() -> None:
    result = simulate_risk_rules(
        [_trade(1, 9, -200), _trade(1, 10, -110), _trade(1, 11, 40), _trade(2, 9, -10)],
        RiskRuleConfig(daily_loss_limit=300, max_consecutive_losses=2, max_trades_per_day=10),
    )

    assert result.protected.total_trades == 3
    assert result.protected.total_pnl == -320
    assert result.blocked[0].reason is BlockReason.DAILY_LOSS_STOP
    assert result.blocked[0].exit_day.isoformat() == "2026-07-01"


def test_all_block_reasons_have_stable_priority_and_day_reset() -> None:
    result = simulate_risk_rules(
        [
            _trade(1, 8, -20),
            _trade(1, 9, -10),
            _trade(2, 8, -1),
            _trade(2, 8, -1),
            _trade(2, 9, -1),
            _trade(3, 9, 10),
        ],
        RiskRuleConfig(
            daily_loss_limit=15,
            max_consecutive_losses=2,
            max_trades_per_day=10,
            forbidden_hours=(9, 9),
        ),
    )

    assert [decision.reason for decision in result.blocked] == [
        BlockReason.DAILY_LOSS_STOP,
        BlockReason.CONSECUTIVE_LOSS_STOP,
        BlockReason.FORBIDDEN_HOUR,
    ]
    assert result.config.forbidden_hours == (9,)

    max_result = simulate_risk_rules(
        [_trade(4, 8, 10), _trade(4, 9, 10)],
        RiskRuleConfig(max_trades_per_day=1, forbidden_hours=(9,)),
    )
    assert max_result.blocked[0].reason is BlockReason.MAX_TRADES_REACHED


def test_bundle_is_private_deterministic_and_rules_change_run_id(tmp_path) -> None:
    csv_path = tmp_path / "trades.csv"
    _csv(csv_path, [(1, 8, 100), (1, 9, -500), (1, 10, 20)])
    first = create_risk_rule_simulation(csv_path, tmp_path / "first", RiskRuleConfig(forbidden_hours=(9,)))
    second = create_risk_rule_simulation(csv_path, tmp_path / "second", RiskRuleConfig(forbidden_hours=(9,)))
    third = create_risk_rule_simulation(csv_path, tmp_path / "third", RiskRuleConfig(forbidden_hours=(10,)))

    first_manifest = json.loads((first / "manifest.json").read_text(encoding="utf-8"))
    third_manifest = json.loads((third / "manifest.json").read_text(encoding="utf-8"))
    summary = json.loads((first / "summary.json").read_text(encoding="utf-8"))
    assert summary["comparison"]["outcome"] == "improved"
    assert summary["comparison"]["blocked_historical_pnl"] == -500
    assert first_manifest["run_id"] != third_manifest["run_id"]
    assert first_manifest["rules_sha256"] != third_manifest["rules_sha256"]
    for name in ("report.md", "summary.json", "manifest.json"):
        content = (first / name).read_text(encoding="utf-8")
        assert content == (second / name).read_text(encoding="utf-8")
        assert str(csv_path.resolve()) not in content
        assert "\\Users\\" not in content


def test_worsened_max_trades_conflict_and_invalid_csv_leave_no_bundle(tmp_path) -> None:
    result = simulate_risk_rules([_trade(1, 8, 100), _trade(1, 10, -200)], RiskRuleConfig(max_trades_per_day=1))
    assert result.protected.total_pnl == 100
    assert result.baseline.total_pnl == -100
    assert result.blocked[0].reason is BlockReason.MAX_TRADES_REACHED
    assert result.protected.total_pnl - result.baseline.total_pnl == 200

    worsened = simulate_risk_rules(
        [_trade(2, 8, -200), _trade(2, 9, 100)], RiskRuleConfig(forbidden_hours=(9,))
    )
    assert worsened.protected.total_pnl < worsened.baseline.total_pnl

    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("Instrument,Qty\nNQ,1\n", encoding="utf-8")
    output = tmp_path / "bundle"
    with pytest.raises(RiskSimulationError, match="Missing required"):
        create_risk_rule_simulation(csv_path, output, RiskRuleConfig())
    assert not output.exists()
    assert not list(tmp_path.glob(".bundle.tmp-*"))


def test_cli_defaults_repeated_hours_and_invalid_values(tmp_path, capsys) -> None:
    csv_path = tmp_path / "trades.csv"
    _csv(csv_path, [(1, 9, 10), (1, 10, -20)])
    output = tmp_path / "bundle"

    assert main(["trading", "simulate-risk", str(csv_path), "--output-dir", str(output), "--forbid-hour", "9", "--forbid-hour", "9"]) == 0
    assert json.loads((output / "summary.json").read_text(encoding="utf-8"))["rules"]["forbidden_hours"] == [9]
    assert main(["trading", "simulate-risk", str(csv_path), "--output-dir", str(tmp_path / "bad"), "--daily-loss-limit", "0"]) == 2
    assert "greater than 0" in capsys.readouterr().err
