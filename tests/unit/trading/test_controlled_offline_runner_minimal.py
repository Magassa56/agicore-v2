from __future__ import annotations

import ast
import json
from pathlib import Path

from agicore.trading.controlled_offline_runner_minimal import (
    apply_controlled_offline_risk_guards,
    assert_controlled_offline_runner_no_real_execution_boundaries,
    build_controlled_offline_simulated_account_snapshot,
    build_controlled_offline_simulated_broker_snapshot,
    build_controlled_offline_synthetic_market_scenario,
    compute_controlled_offline_position_size,
    compute_controlled_offline_runner_metrics,
    detect_controlled_offline_runner_risks,
    evaluate_controlled_offline_strategy_signal,
    generate_controlled_offline_runner_recommendations,
    render_controlled_offline_runner_json_report,
    render_controlled_offline_runner_markdown_report,
    run_controlled_offline_runner_minimal,
    simulate_controlled_offline_read_only_decision,
    validate_controlled_offline_runner_minimal_input,
    write_controlled_offline_journal_entries,
)
from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineReadOnlyDecision,
    ControlledOfflineRunnerMinimalDecision,
    ControlledOfflineRunnerMinimalInput,
    ControlledOfflineRunnerMinimalRecommendation,
    ControlledOfflineRunnerMinimalRisk,
    ControlledOfflineRunnerMinimalState,
    ControlledOfflineSimulatedAccountSnapshot,
    ControlledOfflineSimulatedBrokerSnapshot,
    ControlledOfflineStrategySignal,
    ControlledOfflineSyntheticMarketBar,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/controlled_offline_runner_minimal.py"


def _bars():
    return (
        ControlledOfflineSyntheticMarketBar(0, "SIM", 100.0, 101.0, 99.0, 100.0, 1000.0, "T0"),
        ControlledOfflineSyntheticMarketBar(1, "SIM", 100.0, 103.0, 99.0, 102.0, 1000.0, "T1"),
        ControlledOfflineSyntheticMarketBar(2, "SIM", 102.0, 106.0, 101.0, 105.0, 1000.0, "T2"),
    )


def _ready_input(**overrides):
    payload = {
        "scenario_id": "nominal",
        "symbol": "SIM",
        "synthetic_market_bars": _bars(),
        "initial_cash": 100_000.0,
        "max_position_size": 10.0,
        "risk_fraction": 0.01,
    }
    payload.update(overrides)
    return ControlledOfflineRunnerMinimalInput(**payload)


def test_nominal_with_synthetic_scenario():
    result = run_controlled_offline_runner_minimal(_ready_input())

    assert result.state is ControlledOfflineRunnerMinimalState.READY_FOR_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
    assert result.decision is ControlledOfflineRunnerMinimalDecision.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.read_only_decision.order_submitted is False
    assert result.read_only_decision.position_mutated is False
    assert result.metrics.order_count == 0
    assert result.metrics.real_order_count == 0
    assert result.journal_entries
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = run_controlled_offline_runner_minimal(None)

    assert validate_controlled_offline_runner_minimal_input(None) is False
    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_RUNNER_INPUT_MISSING in result.risks
    assert result.state is ControlledOfflineRunnerMinimalState.CONTROLLED_OFFLINE_RUNNER_INPUT_INVALID
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_INPUT_FIXES


def test_market_scenario_empty():
    result = run_controlled_offline_runner_minimal(_ready_input(synthetic_market_bars=()))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_MARKET_SCENARIO_EMPTY in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_MARKET_SCENARIO_FIXES


def test_market_scenario_invalid():
    bad_bar = ControlledOfflineSyntheticMarketBar(0, "SIM", 100.0, 90.0, 99.0, 100.0, 1000.0, "T0")
    result = run_controlled_offline_runner_minimal(_ready_input(synthetic_market_bars=(bad_bar,)))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_MARKET_SCENARIO_INVALID in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_MARKET_SCENARIO_FIXES


def test_account_snapshot_invalid():
    account = ControlledOfflineSimulatedAccountSnapshot("SIM-ACCOUNT", -1.0, 100.0)
    result = run_controlled_offline_runner_minimal(_ready_input(account_snapshot=account))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_INVALID in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_ACCOUNT_SNAPSHOT_FIXES


def test_broker_snapshot_invalid():
    broker = ControlledOfflineSimulatedBrokerSnapshot("REAL", connected=True, simulated=False, read_only=False, orders_supported=True, real_broker=True)
    result = run_controlled_offline_runner_minimal(_ready_input(broker_snapshot=broker))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_BROKER_SNAPSHOT_INVALID in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_BROKER_SNAPSHOT_FIXES


def test_strategy_signal_invalid():
    result = run_controlled_offline_runner_minimal(_ready_input(force_strategy_signal_invalid=True))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_STRATEGY_SIGNAL_INVALID in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_RISK_GUARD_FIXES


def test_risk_guard_failed():
    result = run_controlled_offline_runner_minimal(_ready_input(force_risk_guard_failed=True))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_RISK_GUARD_FAILED in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_RISK_GUARD_FIXES


def test_journal_missing():
    result = run_controlled_offline_runner_minimal(_ready_input(force_journal_missing=True))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_JOURNAL_MISSING in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_JOURNAL_FIXES


def test_metrics_missing():
    result = run_controlled_offline_runner_minimal(_ready_input(force_metrics_missing=True))

    assert ControlledOfflineRunnerMinimalRisk.CONTROLLED_OFFLINE_METRICS_MISSING in result.risks
    assert result.decision is ControlledOfflineRunnerMinimalDecision.REQUIRE_CONTROLLED_OFFLINE_METRICS_FIXES


def test_markdown_report():
    result = run_controlled_offline_runner_minimal(_ready_input())
    markdown = render_controlled_offline_runner_markdown_report(result)

    assert "Controlled Offline Runner Minimal Report" in markdown
    assert "APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL" in markdown
    assert "no broker" in markdown


def test_json_report():
    result = run_controlled_offline_runner_minimal(_ready_input())
    payload = json.loads(render_controlled_offline_runner_json_report(result))

    assert payload["decision"] == "APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL"
    assert payload["score"] == 100
    assert payload["risks"] == []
    assert payload["real_order_count"] == 0
    assert payload["offline_only"] is True


def test_no_data_access_is_used():
    result = run_controlled_offline_runner_minimal(_ready_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.data_accessed is False
    assert result.metrics.data_access_count == 0
    assert "data/" not in source
    assert "open(" not in source
    assert "read_text" not in source


def test_no_network_socket_http_websocket_is_used():
    result = run_controlled_offline_runner_minimal(_ready_input())
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_from_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }

    assert result.offline_only is True
    assert imported_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})
    assert imported_from_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})


def test_no_real_key_or_env_var_is_read():
    result = run_controlled_offline_runner_minimal(_ready_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.offline_only is True
    assert "environ" not in source
    assert "getenv" not in source
    assert "dotenv" not in source
    assert "API_KEY" not in source


def test_no_real_order_is_produced():
    result = run_controlled_offline_runner_minimal(_ready_input(order_execution_requested=False))

    assert isinstance(result.read_only_decision, ControlledOfflineReadOnlyDecision)
    assert result.read_only_decision.order_submitted is False
    assert result.real_order_submitted is False
    assert result.metrics.order_count == 0
    assert result.metrics.real_order_count == 0


def test_boundary_violations_are_blocked():
    cases = (
        ("broker", {"broker_connection_requested": True}, ControlledOfflineRunnerMinimalRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret", {"api_key_read_requested": True}, ControlledOfflineRunnerMinimalRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network", {"network_requested": True}, ControlledOfflineRunnerMinimalRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order", {"order_execution_requested": True}, ControlledOfflineRunnerMinimalRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account", {"account_access_requested": True}, ControlledOfflineRunnerMinimalRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("data", {"data_access_requested": True}, ControlledOfflineRunnerMinimalRisk.DATA_ACCESS_BOUNDARY_VIOLATION),
    )
    for _name, overrides, expected in cases:
        result = run_controlled_offline_runner_minimal(_ready_input(**overrides))
        assert expected in result.risks
        assert result.decision is ControlledOfflineRunnerMinimalDecision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL


def test_required_functions_are_callable_and_deterministic():
    data = _ready_input()
    scenario = build_controlled_offline_synthetic_market_scenario(data)
    account = build_controlled_offline_simulated_account_snapshot(data)
    broker = build_controlled_offline_simulated_broker_snapshot(data)
    signal = evaluate_controlled_offline_strategy_signal(scenario, data)
    size = compute_controlled_offline_position_size(account, signal, scenario, data)
    guard = apply_controlled_offline_risk_guards(data, account, broker, signal, size)
    decision = simulate_controlled_offline_read_only_decision(scenario, signal, guard)
    journal = write_controlled_offline_journal_entries(scenario, account, broker, signal, guard, decision, data)
    metrics = compute_controlled_offline_runner_metrics(scenario, decision, data)
    risks = detect_controlled_offline_runner_risks(data, scenario, account, broker, signal, guard, journal, metrics)
    recs = generate_controlled_offline_runner_recommendations(data, risks)

    assert assert_controlled_offline_runner_no_real_execution_boundaries(data) is True
    assert scenario == build_controlled_offline_synthetic_market_scenario(data)
    assert signal == ControlledOfflineStrategySignal("SIM", "BUY", 0.75, "synthetic upward drift")
    assert size == 9.5238095238
    assert guard.passed is True
    assert decision.read_only is True
    assert journal
    assert metrics.price_change == 5.0
    assert risks == ()
    assert ControlledOfflineRunnerMinimalRecommendation.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW in recs
