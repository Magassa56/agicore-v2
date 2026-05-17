"""Unit tests for offline trader playbooks."""
from __future__ import annotations

from datetime import datetime

import pytest

from agicore.trading.analyze_trades import analyze_trades
from agicore.trading.import_nt8_csv import NormalizedTrade
from agicore.trading.playbook import (
    compare_playbook_to_stats,
    create_trader_profile,
    load_playbook,
    save_playbook,
)
from agicore.trading.playbook_models import RiskRules


def _trade(day: int, hour: int, pnl: float) -> NormalizedTrade:
    when = datetime(2026, 5, day, hour, 0)
    return NormalizedTrade(entry_time=when, exit_time=when, pnl=pnl)


def test_create_trader_profile_normalizes_declared_playbook() -> None:
    profile = create_trader_profile(
        name=" BAMA ",
        style_detected=" scalping tres court terme ",
        entry_conditions=["trend aligned", " ", "pullback into level"],
        exit_conditions=("target reached", "risk invalidated"),
        forbidden_conditions=("revenge trade",),
        risk_rules=RiskRules(max_daily_loss=900.0, forbidden_hours=(19, 20)),
        notes=" Apex evaluation rules ",
    )

    assert profile.name == "BAMA"
    assert profile.style_detected == "scalping tres court terme"
    assert profile.entry_conditions == ("trend aligned", "pullback into level")
    assert profile.exit_conditions == ("target reached", "risk invalidated")
    assert profile.forbidden_conditions == ("revenge trade",)
    assert profile.risk_rules.max_daily_loss == 900.0
    assert profile.risk_rules.forbidden_hours == (19, 20)
    assert profile.notes == "Apex evaluation rules"


def test_create_trader_profile_requires_name_and_style() -> None:
    with pytest.raises(ValueError, match="name"):
        create_trader_profile(name=" ", style_detected="scalping")

    with pytest.raises(ValueError, match="style_detected"):
        create_trader_profile(name="BAMA", style_detected=" ")


def test_playbook_json_round_trip(tmp_path) -> None:
    path = tmp_path / "playbook.json"
    profile = create_trader_profile(
        name="BAMA",
        style_detected="evening scalper",
        entry_conditions=["only A+ setup"],
        exit_conditions=["fixed risk exit"],
        forbidden_conditions=["trade after max loss"],
        risk_rules=RiskRules(
            max_daily_loss=900.0,
            max_trades_per_day=10,
            max_consecutive_losses=3,
            forbidden_hours=(19, 20),
            minimum_win_rate=0.55,
            minimum_average_trade=0.0,
        ),
    )

    save_playbook(profile, path)
    loaded = load_playbook(path)

    assert loaded == profile


def test_compare_playbook_to_stats_detects_respected_rules() -> None:
    stats = analyze_trades(
        [
            _trade(1, 9, 100.0),
            _trade(1, 10, -50.0),
            _trade(2, 11, 125.0),
        ]
    )
    profile = create_trader_profile(
        name="BAMA",
        style_detected="disciplined intraday",
        risk_rules=RiskRules(
            max_daily_loss=300.0,
            max_trades_per_day=3,
            max_consecutive_losses=2,
            forbidden_hours=(19, 20),
            minimum_win_rate=0.50,
            minimum_average_trade=10.0,
        ),
    )

    result = compare_playbook_to_stats(profile, stats)

    assert result.is_compliant is True
    assert result.total_checks == 6
    assert result.passed_checks == 6
    assert result.failed_checks == 0
    assert {check.status for check in result.checks} == {"pass"}


def test_compare_playbook_to_stats_detects_playbook_violations() -> None:
    stats = analyze_trades(
        [
            _trade(1, 19, -400.0),
            _trade(1, 20, -100.0),
            _trade(1, 20, -50.0),
            _trade(1, 20, 25.0),
        ]
    )
    profile = create_trader_profile(
        name="BAMA",
        style_detected="evening scalper",
        risk_rules=RiskRules(
            max_daily_loss=300.0,
            max_trades_per_day=3,
            max_consecutive_losses=2,
            forbidden_hours=(19, 20),
            minimum_win_rate=0.50,
            minimum_average_trade=0.0,
        ),
    )

    result = compare_playbook_to_stats(profile, stats)
    failed_rules = {check.rule for check in result.checks if check.status == "fail"}

    assert result.is_compliant is False
    assert failed_rules == {
        "max_daily_loss",
        "max_trades_per_day",
        "max_consecutive_losses",
        "forbidden_hours",
        "minimum_win_rate",
        "minimum_average_trade",
    }
