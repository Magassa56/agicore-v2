import ast
import math
from pathlib import Path

import pytest

from agicore.trading.controlled_simulation_offline_runner import run_controlled_simulation_offline_runner
from agicore.trading.controlled_simulation_offline_runner_models import (
    ControlledSimulationOfflineRunnerRisk,
    OfflineEquityPoint,
    OfflinePositionState,
    OfflineSignalEvent,
    OfflineSimulationMetrics,
    OfflineStopConditionResult,
    OfflineSyntheticMarketBar,
)
from agicore.trading.controlled_simulation_result_report_post_review import (
    compute_result_report_score,
    detect_result_report_risks,
    evaluate_controlled_simulation_result_report_post_review,
    generate_result_report_recommendations,
    render_controlled_simulation_result_report_markdown,
    review_offline_drawdown_quality,
    review_offline_equity_curve,
    review_offline_expectancy_quality,
    review_offline_pnl_quality,
    review_offline_position_consistency,
    review_offline_profit_factor_quality,
    review_offline_runner_risks,
    review_offline_stop_conditions,
    review_offline_win_rate_quality,
    summarize_offline_simulation_metrics,
    validate_offline_runner_result,
)
from agicore.trading.controlled_simulation_result_report_post_review_models import (
    ControlledSimulationResultReportDecision,
    ControlledSimulationResultReportInput,
    ControlledSimulationResultReportRecommendation,
    ControlledSimulationResultReportRisk,
    ControlledSimulationResultReportState,
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


def _runner_input(**overrides):
    payload = {
        "controlled_simulation_review_precheck": _upstream(
            "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
        ),
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
    return payload


def _runner_result(**overrides):
    result = run_controlled_simulation_offline_runner(_runner_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "controlled_simulation_offline_runner_result": _runner_result(),
        "controlled_simulation_offline_runner_input": _runner_input(),
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
        "paper_runtime_forward_test_plan": _upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION"),
        "official_paper_validation_report": _upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
        "paper_runtime_validation": _upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
        "paper_trading_runtime": _upstream("COMPLETED"),
        "observability_verification": _upstream("READY_FOR_PAPER_RUNTIME_PREP"),
        "rollback_verification": _upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
        "kill_switch_verification": _upstream("READY_FOR_ROLLBACK_VERIFICATION"),
        "human_validated_paper_session": _upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
        "supervised_paper_session": _upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
        "offline_runner_approved": True,
        "require_flat_final_position": True,
        "max_allowed_drawdown_fraction": 0.20,
        "metric_tolerance": 1e-6,
        "report_requested": True,
        "performance_metrics_engine_requested": False,
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
    return ControlledSimulationResultReportInput(**payload)


def test_evaluate_result_report_approves_nominal_runner_result():
    result = evaluate_controlled_simulation_result_report_post_review(_ready_input())

    assert result.state is ControlledSimulationResultReportState.READY_FOR_PERFORMANCE_METRICS_ENGINE
    assert result.decision is ControlledSimulationResultReportDecision.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT
    assert result.risks == ()
    assert result.offline_only is True
    assert result.report_score == 100
    assert result.metric_summary.total_pnl == 10.0
    assert result.metric_summary.max_drawdown == 3.0
    assert result.metric_summary.win_rate == 1.0
    assert math.isinf(result.metric_summary.profit_factor)
    assert result.metric_summary.expectancy == 10.0
    assert result.position_consistency.flat is True


def test_validate_offline_runner_result_refuses_non_approved_runner():
    runner = _runner_result(
        state="RUNNER_INPUT_INVALID",
        decision="REQUIRE_REVIEW_PRECHECK_FIXES",
        risks=(ControlledSimulationOfflineRunnerRisk.REVIEW_PRECHECK_NOT_APPROVED,),
    )
    data = _ready_input(controlled_simulation_offline_runner_result=runner, offline_runner_approved=False)
    result = evaluate_controlled_simulation_result_report_post_review(data)

    assert validate_offline_runner_result(data) is False
    assert ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED in result.risks
    assert result.state is ControlledSimulationResultReportState.REPORT_INPUT_INVALID
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_OFFLINE_RUNNER_FIXES


def test_missing_runner_result_requires_runner_fixes():
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=None)
    )

    assert ControlledSimulationResultReportRisk.OFFLINE_RUNNER_RESULT_MISSING in result.risks
    assert ControlledSimulationResultReportRisk.METRICS_MISSING in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_OFFLINE_RUNNER_FIXES


def test_metrics_missing_blocks_report():
    runner = _runner_result(metrics=None)
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=runner)
    )

    assert ControlledSimulationResultReportRisk.METRICS_MISSING in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_METRIC_FIXES
    assert result.state is ControlledSimulationResultReportState.REPORT_BLOCKED


def test_metric_summary_extracts_runner_metrics():
    runner = _runner_result()
    summary = summarize_offline_simulation_metrics(runner)

    assert summary.initial_equity == 100_000.0
    assert summary.final_equity == 100_010.0
    assert summary.total_pnl == 10.0
    assert summary.return_fraction == 0.0001


def test_equity_curve_review_detects_invalid_curve():
    runner = _runner_result(equity_curve=())
    summary = summarize_offline_simulation_metrics(runner)
    review = review_offline_equity_curve(runner, summary)

    assert review.passed is False
    assert ControlledSimulationResultReportRisk.EQUITY_CURVE_REVIEW_INVALID in review.risks


def test_pnl_quality_detects_total_pnl_mismatch():
    bad_metrics = OfflineSimulationMetrics(100_000.0, 100_010.0, 11.0, 10.0, 0.0, 3.0, 0.00003, 1, 1, 0, 1.0, float("inf"), 10.0)
    runner = _runner_result(metrics=bad_metrics)
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=runner)
    )

    assert ControlledSimulationResultReportRisk.PNL_REPORT_INVALID in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_METRIC_FIXES


def test_drawdown_quality_detects_mismatch_or_limit_breach():
    runner = _runner_result()
    summary = summarize_offline_simulation_metrics(runner)
    review = review_offline_drawdown_quality(runner, summary, max_allowed_drawdown_fraction=0.000001)

    assert review.passed is False
    assert ControlledSimulationResultReportRisk.DRAWDOWN_REPORT_INVALID in review.risks


def test_win_rate_profit_factor_and_expectancy_reviews_detect_invalid_values():
    win = review_offline_win_rate_quality(
        summarize_offline_simulation_metrics(
            _runner_result(metrics=OfflineSimulationMetrics(100.0, 110.0, 10.0, 10.0, 0.0, 0.0, 0.0, 2, 1, 0, 0.9, 2.0, 5.0))
        )
    )
    pf = review_offline_profit_factor_quality(
        summarize_offline_simulation_metrics(
            _runner_result(metrics=OfflineSimulationMetrics(100.0, 110.0, 10.0, 10.0, 0.0, 0.0, 0.0, 1, 1, 0, 1.0, math.nan, 10.0))
        )
    )
    expectancy = review_offline_expectancy_quality(
        summarize_offline_simulation_metrics(
            _runner_result(metrics=OfflineSimulationMetrics(100.0, 100.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0, 0.0, 0.0, 1.0))
        )
    )

    assert ControlledSimulationResultReportRisk.WIN_RATE_REPORT_INVALID in win.risks
    assert ControlledSimulationResultReportRisk.PROFIT_FACTOR_REPORT_INVALID in pf.risks
    assert ControlledSimulationResultReportRisk.EXPECTANCY_REPORT_INVALID in expectancy.risks


def test_position_consistency_detects_open_or_mismatched_position():
    runner = _runner_result(
        final_position=OfflinePositionState("SIM", 1.0, 100.0, 99_900.0, 0.0, 10.0, 100_010.0)
    )
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=runner)
    )

    assert ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_POSITION_FIXES


def test_stop_conditions_review_detects_triggered_stop():
    runner = _runner_result(
        stop_conditions=OfflineStopConditionResult(
            True,
            (ControlledSimulationOfflineRunnerRisk.LOSS_LIMIT_BREACHED,),
            ("max_loss_amount_breached",),
        )
    )
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=runner)
    )

    assert ControlledSimulationResultReportRisk.STOP_CONDITION_REVIEW_INVALID in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_STOP_CONDITION_FIXES
    assert result.state is ControlledSimulationResultReportState.REPORT_COMPLETED_WITH_WARNINGS


def test_runner_risk_review_detects_runner_warnings():
    runner = _runner_result(risks=(ControlledSimulationOfflineRunnerRisk.UNEXPECTED_OPEN_POSITION,))
    review = review_offline_runner_risks(runner)
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(controlled_simulation_offline_runner_result=runner)
    )

    assert ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE in review.risks
    assert ControlledSimulationResultReportRisk.RISK_REVIEW_INCOMPLETE in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.REQUIRE_RISK_REVIEW_FIXES


def test_real_execution_boundary_violation_blocks_report():
    result = evaluate_controlled_simulation_result_report_post_review(_ready_input(real_execution_requested=True))

    assert ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is ControlledSimulationResultReportState.REPORT_BLOCKED
    assert result.decision is ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT
    assert result.offline_only is False


def test_data_access_violation_blocks_report():
    result = evaluate_controlled_simulation_result_report_post_review(_ready_input(data_access_requested=True))

    assert ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT


def test_premature_performance_metrics_engine_blocks_report():
    result = evaluate_controlled_simulation_result_report_post_review(
        _ready_input(performance_metrics_engine_requested=True)
    )

    assert ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE in result.risks
    assert result.decision is ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT


def test_detect_result_report_risks_can_collect_supplied_reviews():
    runner = _runner_result()
    summary = summarize_offline_simulation_metrics(runner)
    equity_review = review_offline_equity_curve(runner, summary)
    pnl_review = review_offline_pnl_quality(runner, summary)
    drawdown_review = review_offline_drawdown_quality(runner, summary)
    risks = detect_result_report_risks(
        _ready_input(),
        summary,
        equity_review,
        pnl_review,
        drawdown_review,
        review_offline_win_rate_quality(summary),
        review_offline_profit_factor_quality(summary),
        review_offline_expectancy_quality(summary),
        review_offline_position_consistency(runner),
        review_offline_stop_conditions(runner),
        review_offline_runner_risks(runner),
    )

    assert risks == ()


def test_compute_result_report_score_caps_for_metric_risk():
    data = _ready_input()
    runner = data.controlled_simulation_offline_runner_result
    summary = summarize_offline_simulation_metrics(runner)
    score = compute_result_report_score(
        data,
        (ControlledSimulationResultReportRisk.PNL_REPORT_INVALID,),
        summary,
        review_offline_equity_curve(runner, summary),
        review_offline_pnl_quality(runner, summary),
        review_offline_drawdown_quality(runner, summary),
        review_offline_win_rate_quality(summary),
        review_offline_profit_factor_quality(summary),
        review_offline_expectancy_quality(summary),
        review_offline_position_consistency(runner),
        review_offline_stop_conditions(runner),
        review_offline_runner_risks(runner),
    )

    assert score.overall_score <= 55


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_result_report_recommendations(
        (
            ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION,
            ControlledSimulationResultReportRisk.DATA_ACCESS_VIOLATION,
            ControlledSimulationResultReportRisk.PNL_REPORT_INVALID,
        ),
        ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT,
    )

    assert recommendations.count(ControlledSimulationResultReportRecommendation.REMOVE_DATA_ACCESS) == 1
    assert ControlledSimulationResultReportRecommendation.RECHECK_PNL_REPORT in recommendations
    assert ControlledSimulationResultReportRecommendation.RUN_RESULT_REPORT_POST_REVIEW_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_result_report_recommendations(
        (),
        ControlledSimulationResultReportDecision.APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT,
    )

    assert ControlledSimulationResultReportRecommendation.APPROVE_PERFORMANCE_METRICS_ENGINE in recommendations


def test_markdown_contains_decision_metrics_risks_and_recommendations():
    result = evaluate_controlled_simulation_result_report_post_review(_ready_input())
    markdown = render_controlled_simulation_result_report_markdown(result)

    assert "# AGIcore Controlled Simulation Result Report + Post-Run Review" in markdown
    assert "Decision: APPROVE_CONTROLLED_SIMULATION_RESULT_REPORT" in markdown
    assert "Total PnL: 10.0" in markdown
    assert "Profit factor: inf" in markdown
    assert "APPROVE_PERFORMANCE_METRICS_ENGINE" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_controlled_simulation_result_report_post_review(payload)

    assert result.state is ControlledSimulationResultReportState.READY_FOR_PERFORMANCE_METRICS_ENGINE


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            ControlledSimulationResultReportRisk.OFFLINE_RUNNER_NOT_APPROVED,
            ControlledSimulationResultReportRecommendation.APPROVE_OFFLINE_RUNNER_FIRST,
        ),
        (
            ControlledSimulationResultReportRisk.PNL_REPORT_INVALID,
            ControlledSimulationResultReportRecommendation.RECHECK_PNL_REPORT,
        ),
        (
            ControlledSimulationResultReportRisk.POSITION_CONSISTENCY_INVALID,
            ControlledSimulationResultReportRecommendation.RECONCILE_FINAL_POSITION,
        ),
        (
            ControlledSimulationResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            ControlledSimulationResultReportRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        ),
        (
            ControlledSimulationResultReportRisk.PREMATURE_PERFORMANCE_METRICS_ENGINE,
            ControlledSimulationResultReportRecommendation.DELAY_PERFORMANCE_METRICS_ENGINE,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_result_report_recommendations(
        (risk,),
        ControlledSimulationResultReportDecision.BLOCK_RESULT_REPORT,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "controlled_simulation_result_report_post_review.py",
        "controlled_simulation_result_report_post_review_models.py",
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
