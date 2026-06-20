import ast
import math
from pathlib import Path

import pytest

from agicore.trading.controlled_simulation_offline_runner import (
    apply_offline_simulated_fill,
    build_offline_signal_sequence,
    build_offline_simulation_context,
    build_offline_synthetic_market_path,
    compute_offline_expectancy,
    compute_offline_profit_factor,
    compute_offline_simulated_drawdown,
    compute_offline_simulated_pnl,
    compute_offline_win_rate,
    detect_offline_runner_risks,
    detect_offline_stop_conditions,
    execute_offline_simulated_decision,
    execute_offline_simulation_steps,
    generate_offline_runner_recommendations,
    render_controlled_simulation_offline_runner_markdown,
    run_controlled_simulation_offline_runner,
    update_offline_equity_curve,
    update_offline_position_state,
    validate_controlled_simulation_review_precheck,
)
from agicore.trading.controlled_simulation_offline_runner_models import (
    ControlledSimulationOfflineRunnerDecision,
    ControlledSimulationOfflineRunnerInput,
    ControlledSimulationOfflineRunnerRecommendation,
    ControlledSimulationOfflineRunnerRisk,
    ControlledSimulationOfflineRunnerState,
    OfflineEquityPoint,
    OfflinePositionState,
    OfflineSignalEvent,
    OfflineSimulationMetrics,
    OfflineStopConditionResult,
    OfflineSyntheticMarketBar,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _market_path():
    return (
        OfflineSyntheticMarketBar(0, "SIM", 100.0, 101.0, 99.0, 100.0, 1000.0, "T0"),
        OfflineSyntheticMarketBar(1, "SIM", 100.0, 106.0, 99.0, 105.0, 1000.0, "T1"),
        OfflineSyntheticMarketBar(2, "SIM", 105.0, 106.0, 101.0, 102.0, 1000.0, "T2"),
        OfflineSyntheticMarketBar(3, "SIM", 102.0, 111.0, 101.0, 110.0, 1000.0, "T3"),
    )


def _signals():
    return (
        OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "entry"),
        OfflineSignalEvent(3, "SIM", "SELL", 1.0, 1.0, "exit"),
    )


def _ready_input(**overrides):
    payload = {
        "controlled_simulation_review_precheck": _upstream(
            "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
        ),
        "paper_broker_sandbox_dry_run_controlled_simulation_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
        ),
        "paper_broker_sandbox_dry_run_execution_authorization_gate": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_CONTROLLED_SIMULATION_PLAN",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
        ),
        "paper_broker_sandbox_dry_run_execution_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_AUTHORIZATION_GATE",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_pre_execution_check": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_EXECUTION_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
        ),
        "paper_broker_sandbox_dry_run_review": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_PRE_EXECUTION_CHECK",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
        ),
        "paper_broker_sandbox_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_DRY_RUN_REVIEW",
            "APPROVE_PAPER_BROKER_SANDBOX_DRY_RUN_PLAN",
        ),
        "paper_runtime_forward_test_plan": _upstream(
            "READY_FOR_PAPER_BROKER_SANDBOX_SESSION",
            "APPROVE_PAPER_RUNTIME_FORWARD_TEST_PLAN",
        ),
        "supervised_paper_runtime_trial": _upstream("READY_FOR_PAPER_RUNTIME_FORWARD_TEST_PLAN"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "scenario_id": "nominal",
        "symbol": "SIM",
        "initial_equity": 100_000.0,
        "synthetic_market_path": _market_path(),
        "signal_sequence": _signals(),
        "max_steps": 10,
        "max_order_quantity": 2.0,
        "max_position_quantity": 2.0,
        "max_drawdown_fraction": 0.20,
        "max_loss_amount": 5_000.0,
        "commission_per_fill": 0.0,
        "slippage_per_unit": 0.0,
        "require_flat_final_position": True,
        "stop_conditions_required": True,
        "review_precheck_approved": True,
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
        "result_report_requested": False,
    }
    payload.update(overrides)
    return ControlledSimulationOfflineRunnerInput(**payload)


def test_run_controlled_simulation_offline_runner_nominal_result():
    result = run_controlled_simulation_offline_runner(_ready_input())

    assert result.state is ControlledSimulationOfflineRunnerState.READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT
    assert result.decision is ControlledSimulationOfflineRunnerDecision.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER
    assert result.risks == ()
    assert result.offline_only is True
    assert result.metrics.initial_equity == 100_000.0
    assert result.metrics.final_equity == 100_010.0
    assert result.metrics.total_pnl == 10.0
    assert result.metrics.max_drawdown == 3.0
    assert result.metrics.trade_count == 1
    assert result.metrics.win_rate == 1.0
    assert math.isinf(result.metrics.profit_factor)
    assert result.metrics.expectancy == 10.0
    assert result.final_position.quantity == 0.0
    assert len(result.equity_curve) == 4
    assert result.equity_curve[-1].equity == 100_010.0


def test_validate_review_precheck_blocks_when_not_approved():
    data = _ready_input(review_precheck_approved=False)
    result = run_controlled_simulation_offline_runner(data)

    assert validate_controlled_simulation_review_precheck(data) is False
    assert ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED in result.risks
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_INPUT_INVALID
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_REVIEW_PRECHECK_FIXES
    assert result.fills == ()


def test_real_execution_boundary_violation_blocks_runner():
    result = run_controlled_simulation_offline_runner(_ready_input(real_execution_requested=True))

    assert ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_BLOCKED
    assert result.decision is ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER
    assert result.offline_only is False


def test_data_access_violation_blocks_runner():
    result = run_controlled_simulation_offline_runner(_ready_input(data_access_requested=True))

    assert ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_BLOCKED
    assert result.decision is ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER


def test_empty_scenario_requires_scenario_fixes():
    result = run_controlled_simulation_offline_runner(_ready_input(synthetic_market_path=(), signal_sequence=()))

    assert ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY in result.risks
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_SCENARIO_FIXES
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_INPUT_INVALID


def test_invalid_market_path_requires_scenario_fixes():
    bad_path = (OfflineSyntheticMarketBar(0, "SIM", 100.0, 90.0, 99.0, 100.0, 1000.0, "T0"),)
    result = run_controlled_simulation_offline_runner(_ready_input(synthetic_market_path=bad_path, signal_sequence=()))

    assert ControlledSimulationOfflineRunnerRisk.SYNTHETIC_MARKET_PATH_INVALID in result.risks
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_SCENARIO_FIXES


def test_invalid_signal_sequence_requires_signal_fixes():
    result = run_controlled_simulation_offline_runner(
        _ready_input(signal_sequence=(OfflineSignalEvent(0, "SIM", "CONNECT", 1.0, 1.0, "bad"),))
    )

    assert ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID in result.risks
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_SIGNAL_FIXES


def test_missing_risk_limits_require_risk_limit_fixes():
    result = run_controlled_simulation_offline_runner(_ready_input(max_loss_amount=None))

    assert ControlledSimulationOfflineRunnerRisk.RISK_LIMITS_MISSING in result.risks
    assert ControlledSimulationOfflineRunnerRisk.STOP_CONDITIONS_MISSING in result.risks
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_RISK_LIMIT_FIXES


def test_drawdown_breach_completes_with_warnings():
    path = (
        OfflineSyntheticMarketBar(0, "SIM", 100.0, 101.0, 99.0, 100.0, 1000.0, "T0"),
        OfflineSyntheticMarketBar(1, "SIM", 100.0, 101.0, 79.0, 80.0, 1000.0, "T1"),
        OfflineSyntheticMarketBar(2, "SIM", 80.0, 111.0, 79.0, 110.0, 1000.0, "T2"),
    )
    result = run_controlled_simulation_offline_runner(
        _ready_input(
            synthetic_market_path=path,
            signal_sequence=(
                OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "entry"),
                OfflineSignalEvent(2, "SIM", "SELL", 1.0, 1.0, "exit"),
            ),
            max_drawdown_fraction=0.0001,
        )
    )

    assert ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED in result.risks
    assert ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION in result.risks
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_COMPLETED_WITH_WARNINGS
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_RISK_LIMIT_FIXES


def test_loss_limit_breach_is_reported():
    path = (
        OfflineSyntheticMarketBar(0, "SIM", 100.0, 101.0, 99.0, 100.0, 1000.0, "T0"),
        OfflineSyntheticMarketBar(1, "SIM", 100.0, 101.0, 79.0, 80.0, 1000.0, "T1"),
    )
    result = run_controlled_simulation_offline_runner(
        _ready_input(
            initial_equity=100.0,
            synthetic_market_path=path,
            signal_sequence=(
                OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "entry"),
                OfflineSignalEvent(1, "SIM", "SELL", 1.0, 1.0, "exit"),
            ),
            max_drawdown_fraction=1.0,
            max_loss_amount=10.0,
        )
    )

    assert ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED in result.risks
    assert result.metrics.total_pnl == -20.0
    assert result.decision is ControlledSimulationOfflineRunnerDecision.REQUIRE_RISK_LIMIT_FIXES


def test_unexpected_open_position_is_detected():
    result = run_controlled_simulation_offline_runner(
        _ready_input(signal_sequence=(OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "entry"),))
    )

    assert ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION in result.risks
    assert result.final_position.quantity == 1.0
    assert result.state is ControlledSimulationOfflineRunnerState.RUNNER_COMPLETED_WITH_WARNINGS


def test_builder_functions_create_deterministic_default_context():
    data = _ready_input(synthetic_market_path=None, signal_sequence=None)
    path = build_offline_synthetic_market_path(data)
    signals = build_offline_signal_sequence(data, path)
    context = build_offline_simulation_context(data)

    assert tuple(bar.close for bar in path) == (100.0, 103.0, 101.0, 106.0, 108.0)
    assert tuple(signal.action for signal in signals) == ("BUY", "SELL")
    assert context["market_path"] == path
    assert context["signal_sequence"] == signals


def test_step_execution_decision_fill_position_and_equity_helpers():
    data = _ready_input()
    bar = _market_path()[0]
    position = OfflinePositionState("SIM", 0.0, 0.0, 100_000.0, 0.0, 0.0, 100_000.0)
    signal = OfflineSignalEvent(0, "SIM", "BUY", 1.0, 1.0, "entry")
    decision = execute_offline_simulated_decision(signal, bar, position, data)
    fill = apply_offline_simulated_fill(decision, bar, position)
    updated_position = update_offline_position_state(position, fill, bar)
    equity_curve = update_offline_equity_curve((), updated_position, bar)

    assert decision.accepted is True
    assert fill.status == "FILLED"
    assert updated_position.quantity == 1.0
    assert updated_position.cash == 99_900.0
    assert equity_curve[-1].equity == 100_000.0


def test_execute_offline_simulation_steps_returns_complete_log_bundle():
    context = build_offline_simulation_context(_ready_input())
    execution = execute_offline_simulation_steps(context)

    assert execution["final_position"].quantity == 0.0
    assert execution["equity_curve"][-1].equity == 100_010.0
    assert len(execution["step_logs"]) == 4
    assert execution["fills"][0].status == "FILLED"


def test_metric_functions_are_deterministic():
    curve = (
        OfflineEquityPoint(0, "T0", 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 0.0),
        OfflineEquityPoint(1, "T1", 0.0, 0.0, 90.0, 0.0, 0.0, 10.0, 0.1),
        OfflineEquityPoint(2, "T2", 0.0, 0.0, 120.0, 0.0, 0.0, 0.0, 0.0),
    )

    assert compute_offline_simulated_pnl(curve, 100.0) == 20.0
    assert compute_offline_simulated_drawdown(curve) == 10.0
    assert compute_offline_win_rate((10.0, -5.0, 0.0)) == pytest.approx(1 / 3)
    assert compute_offline_profit_factor((10.0, -5.0)) == 2.0
    assert compute_offline_expectancy((10.0, -5.0)) == 2.5


def test_detect_offline_stop_conditions_reports_limits_and_open_position():
    metrics = OfflineSimulationMetrics(100.0, 80.0, -20.0, -20.0, 0.0, 20.0, 0.2, 1, 0, 1, 0.0, 0.0, -20.0)
    position = OfflinePositionState("SIM", 1.0, 100.0, 0.0, -20.0, 0.0, 80.0)
    stop = detect_offline_stop_conditions(_ready_input(max_drawdown_fraction=0.1, max_loss_amount=10.0), metrics, position)

    assert stop.triggered is True
    assert ControlledSimulationOfflineRunnerRisk.DRAWDOWN_LIMIT_BREACHED in stop.risks
    assert ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED in stop.risks
    assert ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION in stop.risks


def test_detect_offline_runner_risks_reports_metric_failures():
    bad_curve = (OfflineEquityPoint(0, "T0", 0.0, 0.0, -1.0, 0.0, 0.0, 0.0, 0.0),)
    bad_metrics = OfflineSimulationMetrics(100.0, math.nan, math.nan, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 0.0)
    stop = OfflineStopConditionResult(True, (ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED,), ("loss",))
    risks = detect_offline_runner_risks(
        _ready_input(),
        _market_path(),
        _signals(),
        bad_curve,
        bad_metrics,
        stop,
    )

    assert ControlledSimulationOfflineRunnerRisk.EQUITY_CURVE_INVALID in risks
    assert ControlledSimulationOfflineRunnerRisk.PNL_COMPUTATION_INVALID in risks
    assert ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED in risks


def test_premature_result_report_blocks_runner():
    result = run_controlled_simulation_offline_runner(_ready_input(result_report_requested=True))

    assert ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT in result.risks
    assert result.decision is ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_offline_runner_recommendations(
        (
            ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION,
            ControlledSimulationOfflineRunnerRisk.DATA_ACCESS_VIOLATION,
            ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED,
        ),
        ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER,
    )

    assert recommendations.count(ControlledSimulationOfflineRunnerRecommendation.REMOVE_DATA_ACCESS) == 1
    assert ControlledSimulationOfflineRunnerRecommendation.REDUCE_LOSS_EXPOSURE in recommendations
    assert ControlledSimulationOfflineRunnerRecommendation.RUN_CONTROLLED_SIMULATION_OFFLINE_RUNNER_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_offline_runner_recommendations(
        (),
        ControlledSimulationOfflineRunnerDecision.APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER,
    )

    assert ControlledSimulationOfflineRunnerRecommendation.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT in recommendations


def test_markdown_contains_decision_metrics_risks_and_logs():
    result = run_controlled_simulation_offline_runner(_ready_input())
    markdown = render_controlled_simulation_offline_runner_markdown(result)

    assert "# AGIcore Controlled Simulation Offline Runner" in markdown
    assert "Decision: APPROVE_CONTROLLED_SIMULATION_OFFLINE_RUNNER" in markdown
    assert "Total PnL: 10.0" in markdown
    assert "Profit factor: inf" in markdown
    assert "step=0" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = run_controlled_simulation_offline_runner(payload)

    assert result.state is ControlledSimulationOfflineRunnerState.READY_FOR_CONTROLLED_SIMULATION_RESULT_REPORT


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED,
            ControlledSimulationOfflineRunnerRecommendation.APPROVE_REVIEW_PRECHECK_FIRST,
        ),
        (
            ControlledSimulationOfflineRunnerRisk.OFFLINE_SCENARIO_EMPTY,
            ControlledSimulationOfflineRunnerRecommendation.PROVIDE_SYNTHETIC_SCENARIO,
        ),
        (
            ControlledSimulationOfflineRunnerRisk.SIGNAL_SEQUENCE_INVALID,
            ControlledSimulationOfflineRunnerRecommendation.FIX_SIGNAL_SEQUENCE,
        ),
        (
            ControlledSimulationOfflineRunnerRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            ControlledSimulationOfflineRunnerRecommendation.RESTORE_OFFLINE_REAL_EXECUTION_BOUNDARIES,
        ),
        (
            ControlledSimulationOfflineRunnerRisk.PREMATURE_RESULT_REPORT,
            ControlledSimulationOfflineRunnerRecommendation.DELAY_CONTROLLED_SIMULATION_RESULT_REPORT,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_offline_runner_recommendations(
        (risk,),
        ControlledSimulationOfflineRunnerDecision.BLOCK_CONTROLLED_SIMULATION_RUNNER,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "controlled_simulation_offline_runner.py",
        "controlled_simulation_offline_runner_models.py",
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
