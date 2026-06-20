import ast
import math
from pathlib import Path

import pytest

from agicore.trading.controlled_simulation_offline_runner_models import OfflineSignalEvent, OfflineSyntheticMarketBar
from agicore.trading.multi_scenario_controlled_simulation import (
    aggregate_multi_scenario_metrics,
    build_drawdown_scenario,
    build_flat_scenario,
    build_losing_scenario,
    build_multi_scenario_suite,
    build_position_inconsistency_scenario,
    build_risk_violation_scenario,
    build_stop_condition_scenario,
    build_volatile_scenario,
    build_winning_scenario,
    compute_multi_scenario_drawdown,
    compute_multi_scenario_expectancy,
    compute_multi_scenario_pnl,
    compute_multi_scenario_profit_factor,
    compute_multi_scenario_robustness_score,
    compute_multi_scenario_stability_score,
    compute_multi_scenario_win_rate,
    detect_multi_scenario_failures,
    detect_multi_scenario_risks,
    execute_controlled_simulation_scenario,
    generate_multi_scenario_recommendations,
    render_multi_scenario_controlled_simulation_markdown,
    run_multi_scenario_controlled_simulation,
    validate_performance_risk_validation_gate,
)
from agicore.trading.multi_scenario_controlled_simulation_models import (
    ControlledSimulationScenarioDefinition,
    ControlledSimulationScenarioResult,
    ControlledSimulationScenarioType,
    MultiScenarioControlledSimulationDecision,
    MultiScenarioControlledSimulationInput,
    MultiScenarioControlledSimulationRecommendation,
    MultiScenarioControlledSimulationRisk,
    MultiScenarioControlledSimulationState,
    MultiScenarioMetricSummary,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _approved_gate(**overrides):
    payload = {
        "state": "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION",
        "decision": "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE",
        "gate_score": 100,
        "risks": (),
        "offline_only": True,
    }
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "performance_risk_validation_gate": _approved_gate(),
        "performance_metrics_result": _upstream("READY_FOR_RISK_METRICS_ENGINE", "APPROVE_PERFORMANCE_METRICS_ENGINE"),
        "risk_metrics_result": _upstream("READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE", "APPROVE_RISK_METRICS_ENGINE"),
        "controlled_simulation_result_report": _upstream("READY_FOR_PERFORMANCE_METRICS_ENGINE"),
        "controlled_simulation_offline_runner_result": _upstream("READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT"),
        "paper_runtime_forward_test_plan": _upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "performance_risk_validation_approved": True,
        "scenario_suite": None,
        "min_robustness_score": 60,
        "max_drawdown_fraction": 0.25,
        "max_loss_amount": 10_000.0,
        "max_failed_scenarios": 0,
        "multi_scenario_result_report_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_real_order": True,
        "no_real_account_access": True,
        "synthetic_data_only": True,
        "in_memory_only": True,
        "data_access_requested": False,
        "real_execution_requested": False,
    }
    payload.update(overrides)
    return MultiScenarioControlledSimulationInput(**payload)


def _simple_path(closes):
    bars = []
    previous = None
    for step, close in enumerate(closes):
        open_price = close if previous is None else previous
        bars.append(OfflineSyntheticMarketBar(step, "SIM", open_price, max(open_price, close) + 0.5, min(open_price, close) - 0.5, close, 1000.0, f"T{step}"))
        previous = close
    return tuple(bars)


def test_run_multi_scenario_controlled_simulation_approves_default_suite():
    result = run_multi_scenario_controlled_simulation(_ready_input())

    assert result.state is MultiScenarioControlledSimulationState.READY_FOR_MULTI_SCENARIO_RESULT_REPORT
    assert result.decision is MultiScenarioControlledSimulationDecision.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION
    assert result.risks == ()
    assert result.offline_only is True
    assert result.metric_summary.scenario_count == 9
    assert result.metric_summary.failed_scenario_count == 0
    assert result.metric_summary.loss_scenario_count == 1
    assert result.metric_summary.total_pnl > 0
    assert result.metric_summary.robustness_score >= 60
    assert result.simulation_score >= 80
    assert {item.scenario_type for item in result.scenario_suite} >= {
        ControlledSimulationScenarioType.WINNING_SCENARIO,
        ControlledSimulationScenarioType.LOSING_SCENARIO,
        ControlledSimulationScenarioType.FLAT_SCENARIO,
        ControlledSimulationScenarioType.DRAWDOWN_SCENARIO,
        ControlledSimulationScenarioType.VOLATILE_SCENARIO,
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
        ControlledSimulationScenarioType.MIXED_SCENARIO,
    }


def test_validate_performance_risk_validation_gate_refuses_unapproved_gate():
    gate = _approved_gate(state="VALIDATION_INPUT_INVALID", decision="REQUIRE_RISK_REDUCTION", risks=("DRAWDOWN_VALIDATION_FAILED",))
    data = _ready_input(performance_risk_validation_gate=gate, performance_risk_validation_approved=False)
    result = run_multi_scenario_controlled_simulation(data)

    assert validate_performance_risk_validation_gate(data) is False
    assert MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_PERFORMANCE_RISK_VALIDATION_FIXES
    assert result.state is MultiScenarioControlledSimulationState.INPUT_INVALID
    assert result.scenario_results == ()


def test_builders_and_compute_functions_are_deterministic():
    scenarios = (
        build_winning_scenario(),
        build_losing_scenario(),
        build_flat_scenario(),
        build_drawdown_scenario(),
        build_volatile_scenario(),
        build_stop_condition_scenario(),
        build_risk_violation_scenario(),
        build_position_inconsistency_scenario(),
    )
    assert len(scenarios) == 8
    results = (
        ControlledSimulationScenarioResult("a", ControlledSimulationScenarioType.WINNING_SCENARIO, True, pnl=10.0, max_drawdown=1.0, max_drawdown_fraction=0.01, trade_count=1),
        ControlledSimulationScenarioResult("b", ControlledSimulationScenarioType.LOSING_SCENARIO, True, pnl=-5.0, max_drawdown=5.0, max_drawdown_fraction=0.05, trade_count=1),
        ControlledSimulationScenarioResult("c", ControlledSimulationScenarioType.FLAT_SCENARIO, True, pnl=0.0, max_drawdown=0.0, max_drawdown_fraction=0.0, trade_count=0),
    )

    assert compute_multi_scenario_pnl(results) == 5.0
    assert compute_multi_scenario_drawdown(results) == (5.0, 0.05)
    assert compute_multi_scenario_win_rate(results) == 0.5
    assert compute_multi_scenario_profit_factor(results) == 2.0
    assert compute_multi_scenario_expectancy(results) == 2.5
    assert compute_multi_scenario_stability_score(results) > 0
    summary = aggregate_multi_scenario_metrics(results)
    assert compute_multi_scenario_robustness_score(summary) == summary.robustness_score


def test_losing_scenario_executes_as_controlled_loss_without_failure():
    result = execute_controlled_simulation_scenario(build_losing_scenario(), _ready_input())

    assert result.passed is True
    assert result.pnl < 0
    assert result.trade_count == 1
    assert result.failures == ()


def test_missing_scenarios_are_detected():
    suite = (build_winning_scenario(), build_flat_scenario())
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=suite))

    assert MultiScenarioControlledSimulationRisk.LOSING_SCENARIO_MISSING in result.risks
    assert MultiScenarioControlledSimulationRisk.DRAWDOWN_SCENARIO_MISSING in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_SUITE_FIXES


def test_empty_scenario_suite_is_detected():
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=()))

    assert MultiScenarioControlledSimulationRisk.SCENARIO_SUITE_EMPTY in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_SUITE_FIXES


def test_invalid_scenario_definition_is_detected():
    bad = ControlledSimulationScenarioDefinition("bad", ControlledSimulationScenarioType.WINNING_SCENARIO)
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=(bad,)))

    assert MultiScenarioControlledSimulationRisk.SCENARIO_DEFINITION_INVALID in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_SUITE_FIXES


def test_drawdown_too_high_is_detected():
    result = run_multi_scenario_controlled_simulation(_ready_input(max_drawdown_fraction=0.000001))

    assert MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_RISK_REDUCTION


def test_loss_limit_breach_is_detected():
    losing = ControlledSimulationScenarioDefinition(
        "large_loss",
        ControlledSimulationScenarioType.LOSING_SCENARIO,
        market_path=_simple_path((100.0, 90.0, 80.0, 50.0)),
        signal_sequence=(OfflineSignalEvent(0, "SIM", "BUY", 100.0, 1.0, "loss_entry"), OfflineSignalEvent(3, "SIM", "SELL", 100.0, 1.0, "loss_exit")),
        max_order_quantity=100.0,
        max_position_quantity=100.0,
        max_drawdown_fraction=1.0,
        max_loss_amount=100_000.0,
    )
    suite = tuple(scenario for scenario in build_multi_scenario_suite() if scenario.scenario_type != ControlledSimulationScenarioType.LOSING_SCENARIO) + (losing,)
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=suite, max_loss_amount=100.0))

    assert MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_LOSS_LIMIT_BREACHED in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_RISK_REDUCTION


def test_risk_violation_scenario_failure_is_detected():
    risk_violation = ControlledSimulationScenarioDefinition(
        "risk_violation_fail",
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        market_path=_simple_path((100.0, 101.0, 102.0)),
        signal_sequence=(OfflineSignalEvent(0, "SIM", "BUY", 5.0, 1.0, "too_large"), OfflineSignalEvent(2, "SIM", "SELL", 5.0, 1.0, "exit")),
        max_order_quantity=1.0,
        max_position_quantity=1.0,
    )
    suite = tuple(scenario for scenario in build_multi_scenario_suite() if scenario.scenario_type != ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO) + (risk_violation,)
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=suite, max_failed_scenarios=0))

    assert MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED in result.risks
    assert result.metric_summary.risk_violation_count == 1
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_EXECUTION_FIXES


def test_position_inconsistency_is_detected():
    position = ControlledSimulationScenarioDefinition(
        "position_inconsistent",
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
        market_path=_simple_path((100.0, 103.0, 105.0)),
        signal_sequence=(OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "open"),),
        require_flat_final_position=False,
        allow_open_final_position=False,
    )
    suite = tuple(scenario for scenario in build_multi_scenario_suite() if scenario.scenario_type != ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO) + (position,)
    result = run_multi_scenario_controlled_simulation(_ready_input(scenario_suite=suite))

    assert MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED in result.risks
    assert result.metric_summary.position_inconsistency_count == 1
    assert detect_multi_scenario_failures(result.scenario_results)


def test_robustness_score_weak_is_detected():
    result = run_multi_scenario_controlled_simulation(_ready_input(min_robustness_score=100))

    assert MultiScenarioControlledSimulationRisk.ROBUSTNESS_SCORE_WEAK in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.REQUIRE_ROBUSTNESS_FIXES


def test_real_execution_boundary_violation_blocks_simulation():
    result = run_multi_scenario_controlled_simulation(_ready_input(real_execution_requested=True))

    assert MultiScenarioControlledSimulationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is MultiScenarioControlledSimulationState.MULTI_SCENARIO_BLOCKED
    assert result.decision is MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION
    assert result.offline_only is False


def test_data_access_violation_blocks_simulation():
    result = run_multi_scenario_controlled_simulation(_ready_input(data_access_requested=True))

    assert MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION


def test_premature_result_report_blocks_simulation():
    result = run_multi_scenario_controlled_simulation(_ready_input(multi_scenario_result_report_requested=True))

    assert MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT in result.risks
    assert result.decision is MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION


def test_detect_multi_scenario_risks_can_use_supplied_results():
    data = _ready_input()
    result = run_multi_scenario_controlled_simulation(data)
    risks = detect_multi_scenario_risks(data, result.scenario_suite, result.scenario_results, result.metric_summary)

    assert risks == ()


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_multi_scenario_recommendations(
        (
            MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION,
            MultiScenarioControlledSimulationRisk.DATA_ACCESS_VIOLATION,
            MultiScenarioControlledSimulationRisk.LOSING_SCENARIO_MISSING,
        ),
        MultiScenarioControlledSimulationDecision.BLOCK_MULTI_SCENARIO_CONTROLLED_SIMULATION,
    )

    assert recommendations.count(MultiScenarioControlledSimulationRecommendation.REMOVE_DATA_ACCESS) == 1
    assert MultiScenarioControlledSimulationRecommendation.ADD_LOSING_SCENARIO in recommendations
    assert MultiScenarioControlledSimulationRecommendation.RUN_MULTI_SCENARIO_CONTROLLED_SIMULATION_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_multi_scenario_recommendations(
        (),
        MultiScenarioControlledSimulationDecision.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION,
    )

    assert MultiScenarioControlledSimulationRecommendation.APPROVE_MULTI_SCENARIO_RESULT_REPORT in recommendations


def test_markdown_contains_decision_metrics_scenarios_risks_and_recommendations():
    result = run_multi_scenario_controlled_simulation(_ready_input())
    markdown = render_multi_scenario_controlled_simulation_markdown(result)

    assert "# AGIcore Multi-Scenario Controlled Simulation" in markdown
    assert "Decision: APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION" in markdown
    assert "Scenario count: 9" in markdown
    assert "Robustness score:" in markdown
    assert "APPROVE_MULTI_SCENARIO_RESULT_REPORT" in markdown


def test_mapping_inputs_and_scenarios_are_supported():
    suite = tuple(dict(scenario.__dict__) for scenario in build_multi_scenario_suite())
    payload = dict(_ready_input(scenario_suite=suite).__dict__)
    payload["ignored_future_key"] = "ignored"
    result = run_multi_scenario_controlled_simulation(payload)

    assert result.state is MultiScenarioControlledSimulationState.READY_FOR_MULTI_SCENARIO_RESULT_REPORT


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            MultiScenarioControlledSimulationRisk.PERFORMANCE_RISK_VALIDATION_NOT_APPROVED,
            MultiScenarioControlledSimulationRecommendation.APPROVE_PERFORMANCE_RISK_VALIDATION_FIRST,
        ),
        (
            MultiScenarioControlledSimulationRisk.WINNING_SCENARIO_MISSING,
            MultiScenarioControlledSimulationRecommendation.ADD_WINNING_SCENARIO,
        ),
        (
            MultiScenarioControlledSimulationRisk.SCENARIO_EXECUTION_FAILED,
            MultiScenarioControlledSimulationRecommendation.FIX_SCENARIO_EXECUTION,
        ),
        (
            MultiScenarioControlledSimulationRisk.MULTI_SCENARIO_DRAWDOWN_TOO_HIGH,
            MultiScenarioControlledSimulationRecommendation.REDUCE_MULTI_SCENARIO_DRAWDOWN,
        ),
        (
            MultiScenarioControlledSimulationRisk.PREMATURE_MULTI_SCENARIO_RESULT_REPORT,
            MultiScenarioControlledSimulationRecommendation.DELAY_MULTI_SCENARIO_RESULT_REPORT,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_multi_scenario_recommendations(
        (risk,),
        MultiScenarioControlledSimulationDecision.REQUIRE_SCENARIO_EXECUTION_FIXES,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "multi_scenario_controlled_simulation.py",
        "multi_scenario_controlled_simulation_models.py",
    ],
)
def test_module_keeps_offline_import_boundary(module_name):
    module_path = Path(__file__).parents[3] / "src" / "agicore" / "trading" / module_name
    source = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])

    assert not {"alpaca", "requests", "websocket", "socket", "http"} & imported_roots
    assert "data/" not in source
    assert "open(" not in source
