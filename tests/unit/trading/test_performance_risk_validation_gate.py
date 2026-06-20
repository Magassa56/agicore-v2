import ast
import math
from pathlib import Path

import pytest

from agicore.trading.performance_metrics_engine_models import PerformanceMetricSummary
from agicore.trading.performance_risk_validation_gate import (
    compute_performance_risk_validation_score,
    detect_performance_risk_validation_risks,
    evaluate_drawdown_validation,
    evaluate_expectancy_validation,
    evaluate_exposure_validation,
    evaluate_loss_limit_validation,
    evaluate_performance_risk_validation_gate,
    evaluate_pnl_validation,
    evaluate_profit_factor_validation,
    evaluate_return_validation,
    evaluate_risk_per_trade_validation,
    evaluate_rule_violation_validation,
    evaluate_stability_validation,
    evaluate_trade_count_validation,
    evaluate_win_rate_validation,
    generate_performance_risk_validation_recommendations,
    render_performance_risk_validation_gate_markdown,
    validate_performance_metrics_approval,
    validate_risk_metrics_approval,
)
from agicore.trading.performance_risk_validation_gate_models import (
    PerformanceRiskValidationGateDecision,
    PerformanceRiskValidationGateInput,
    PerformanceRiskValidationGateRecommendation,
    PerformanceRiskValidationGateRisk,
    PerformanceRiskValidationGateState,
    PerformanceRiskValidationThresholds,
)
from agicore.trading.risk_metrics_engine_models import RiskMetricSummary


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "risks": tuple(risks), "offline_only": True}
    if decision:
        payload["decision"] = decision
    payload.update(extra)
    return payload


def _performance_summary(**overrides):
    payload = {
        "total_pnl": 10.0,
        "return_fraction": 0.0001,
        "return_percent": 0.01,
        "max_drawdown": 3.0,
        "max_drawdown_fraction": 0.0000299985,
        "win_rate": 1.0,
        "profit_factor": float("inf"),
        "expectancy": 10.0,
        "trade_count": 1,
        "average_win": 10.0,
        "average_loss": 0.0,
        "risk_reward_ratio": float("inf"),
        "stability_score": 100,
        "quality_score": 100,
    }
    payload.update(overrides)
    return PerformanceMetricSummary(**payload)


def _risk_summary(**overrides):
    payload = {
        "max_loss": 0.0,
        "max_drawdown_fraction": 0.0000299985,
        "loss_limit_usage": 0.0,
        "risk_per_trade_fraction": 0.0,
        "exposure_fraction": 0.0010499475,
        "position_risk": 105.0,
        "consecutive_loss_count": 0,
        "loss_stability_score": 100,
        "stop_condition_quality_score": 100,
        "risk_quality_score": 100,
        "max_drawdown_amount": 3.0,
    }
    payload.update(overrides)
    return RiskMetricSummary(**payload)


def _performance_result(summary=None, **overrides):
    payload = {
        "state": "READY_FOR_RISK_METRICS_ENGINE",
        "decision": "APPROVE_PERFORMANCE_METRICS_ENGINE",
        "engine_score": 100,
        "risks": (),
        "metric_summary": _performance_summary() if summary is None else summary,
        "offline_only": True,
    }
    payload.update(overrides)
    return payload


def _risk_result(summary=None, **overrides):
    payload = {
        "state": "READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE",
        "decision": "APPROVE_RISK_METRICS_ENGINE",
        "engine_score": 100,
        "risks": (),
        "violations": (),
        "metric_summary": _risk_summary() if summary is None else summary,
        "offline_only": True,
    }
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    performance_summary = overrides.pop("performance_metric_summary", _performance_summary())
    risk_summary = overrides.pop("risk_metric_summary", _risk_summary())
    payload = {
        "performance_metrics_result": _performance_result(performance_summary),
        "risk_metrics_result": _risk_result(risk_summary),
        "performance_metric_summary": performance_summary,
        "risk_metric_summary": risk_summary,
        "performance_thresholds": _upstream("READY"),
        "risk_thresholds": _upstream("READY"),
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
        "performance_metrics_approved": True,
        "risk_metrics_approved": True,
        "thresholds": PerformanceRiskValidationThresholds(),
        "metric_tolerance": 1e-6,
        "multi_scenario_controlled_simulation_requested": False,
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
    return PerformanceRiskValidationGateInput(**payload)


def test_evaluate_performance_risk_validation_gate_approves_nominal_inputs():
    result = evaluate_performance_risk_validation_gate(_ready_input())

    assert result.state is PerformanceRiskValidationGateState.READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION
    assert result.decision is PerformanceRiskValidationGateDecision.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE
    assert result.risks == ()
    assert result.offline_only is True
    assert result.gate_score == 100
    assert result.validation_summary.total_pnl == 10.0
    assert result.validation_summary.return_fraction == 0.0001
    assert result.validation_summary.max_drawdown_fraction == pytest.approx(0.0000299985)
    assert math.isinf(result.validation_summary.profit_factor)
    assert result.validation_summary.expectancy == 10.0
    assert result.validation_summary.trade_count == 1
    assert result.validation_summary.win_rate == 1.0
    assert result.validation_summary.risk_per_trade_fraction == 0.0
    assert result.validation_summary.exposure_fraction == 0.0010499475
    assert result.validation_summary.loss_limit_usage == 0.0
    assert result.validation_summary.risk_quality_score == 100


def test_performance_metrics_not_approved_requires_performance_fixes():
    performance = _performance_result(state="INPUT_INVALID", decision="REQUIRE_PERFORMANCE_REVIEW", risks=("PNL_INVALID",))
    data = _ready_input(performance_metrics_result=performance, performance_metrics_approved=False)
    result = evaluate_performance_risk_validation_gate(data)

    assert validate_performance_metrics_approval(data) is False
    assert PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_PERFORMANCE_METRICS_FIXES
    assert result.state is PerformanceRiskValidationGateState.VALIDATION_INPUT_INVALID


def test_risk_metrics_not_approved_requires_risk_fixes():
    risk = _risk_result(state="INPUT_INVALID", decision="REQUIRE_RISK_REVIEW", risks=("EXPOSURE_TOO_HIGH",))
    data = _ready_input(risk_metrics_result=risk, risk_metrics_approved=False)
    result = evaluate_performance_risk_validation_gate(data)

    assert validate_risk_metrics_approval(data) is False
    assert PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_RISK_METRICS_FIXES


def test_missing_inputs_are_detected():
    result = evaluate_performance_risk_validation_gate(
        _ready_input(
            performance_metrics_result=None,
            risk_metrics_result=None,
            performance_metric_summary=None,
            risk_metric_summary=None,
            performance_metrics_approved=False,
            risk_metrics_approved=False,
        )
    )

    assert PerformanceRiskValidationGateRisk.PERFORMANCE_RISK_INPUT_MISSING in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_PERFORMANCE_METRICS_FIXES


def test_individual_validation_functions_are_deterministic():
    performance = _performance_summary()
    risk = _risk_summary()
    thresholds = PerformanceRiskValidationThresholds()

    assert evaluate_pnl_validation(performance, thresholds).passed is True
    assert evaluate_return_validation(performance, thresholds).passed is True
    assert evaluate_drawdown_validation(performance, risk, thresholds).passed is True
    assert evaluate_profit_factor_validation(performance, thresholds).passed is True
    assert evaluate_expectancy_validation(performance, thresholds).passed is True
    assert evaluate_trade_count_validation(performance, thresholds).passed is True
    assert evaluate_win_rate_validation(performance, thresholds).passed is True
    assert evaluate_risk_per_trade_validation(risk, thresholds).passed is True
    assert evaluate_exposure_validation(risk, thresholds).passed is True
    assert evaluate_loss_limit_validation(risk, thresholds).passed is True
    assert evaluate_stability_validation(performance, risk, thresholds).passed is True
    assert evaluate_rule_violation_validation(_risk_result(risk), thresholds).passed is True


def test_trade_count_too_low_requires_more_trades_and_recommends_scenarios():
    performance = _performance_summary(trade_count=1)
    result = evaluate_performance_risk_validation_gate(
        _ready_input(
            performance_metric_summary=performance,
            thresholds=PerformanceRiskValidationThresholds(min_trade_count=2),
        )
    )

    assert PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_MORE_TRADES
    assert PerformanceRiskValidationGateRecommendation.ADD_MORE_TRADES in result.recommendations
    assert PerformanceRiskValidationGateRecommendation.HOLD_MULTI_SCENARIO_CONTROLLED_SIMULATION in result.recommendations


def test_drawdown_too_high_requires_drawdown_reduction():
    performance = _performance_summary(max_drawdown_fraction=0.25)
    risk = _risk_summary(max_drawdown_fraction=0.25)
    result = evaluate_performance_risk_validation_gate(_ready_input(performance_metric_summary=performance, risk_metric_summary=risk))

    assert PerformanceRiskValidationGateRisk.DRAWDOWN_VALIDATION_FAILED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_DRAWDOWN_REDUCTION


def test_risk_per_trade_too_high_requires_risk_reduction():
    risk = _risk_summary(risk_per_trade_fraction=0.03)
    result = evaluate_performance_risk_validation_gate(_ready_input(risk_metric_summary=risk))

    assert PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION


def test_exposure_too_high_requires_risk_reduction():
    risk = _risk_summary(exposure_fraction=2.0)
    result = evaluate_performance_risk_validation_gate(_ready_input(risk_metric_summary=risk))

    assert PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION


def test_loss_limit_usage_too_high_requires_risk_reduction():
    risk = _risk_summary(loss_limit_usage=1.25)
    result = evaluate_performance_risk_validation_gate(_ready_input(risk_metric_summary=risk))

    assert PerformanceRiskValidationGateRisk.LOSS_LIMIT_USAGE_TOO_HIGH in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION


def test_profit_factor_and_expectancy_failures_require_additional_scenarios():
    performance = _performance_summary(profit_factor=0.5, expectancy=-1.0)
    result = evaluate_performance_risk_validation_gate(_ready_input(performance_metric_summary=performance))

    assert PerformanceRiskValidationGateRisk.PROFIT_FACTOR_VALIDATION_FAILED in result.risks
    assert PerformanceRiskValidationGateRisk.EXPECTANCY_VALIDATION_FAILED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_positive_performance_but_unreliable_stability_requires_improvement():
    performance = _performance_summary(total_pnl=10.0, return_fraction=0.01, stability_score=20, quality_score=20)
    risk = _risk_summary(loss_stability_score=20, risk_quality_score=20)
    result = evaluate_performance_risk_validation_gate(_ready_input(performance_metric_summary=performance, risk_metric_summary=risk))

    assert PerformanceRiskValidationGateRisk.STABILITY_VALIDATION_FAILED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_STABILITY_IMPROVEMENT


def test_thresholds_missing_are_detected():
    result = evaluate_performance_risk_validation_gate(_ready_input(thresholds=None))

    assert PerformanceRiskValidationGateRisk.VALIDATION_THRESHOLD_MISSING in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_rule_violation_is_detected_from_risk_metrics_result():
    risk = _risk_result(violations=("drawdown",), risks=("DRAWDOWN_LIMIT_BREACHED",))
    result = evaluate_performance_risk_validation_gate(_ready_input(risk_metrics_result=risk))

    assert PerformanceRiskValidationGateRisk.RULE_VIOLATION_DETECTED in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION


def test_win_rate_warning_requires_additional_scenarios():
    performance = _performance_summary(win_rate=0.2)
    result = evaluate_performance_risk_validation_gate(
        _ready_input(performance_metric_summary=performance, thresholds=PerformanceRiskValidationThresholds(min_win_rate=0.5))
    )

    assert PerformanceRiskValidationGateRisk.WIN_RATE_VALIDATION_WARNING in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_real_execution_boundary_violation_blocks_gate():
    result = evaluate_performance_risk_validation_gate(_ready_input(real_execution_requested=True))

    assert PerformanceRiskValidationGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is PerformanceRiskValidationGateState.VALIDATION_BLOCKED
    assert result.decision is PerformanceRiskValidationGateDecision.BLOCK_PERFORMANCE_RISK_VALIDATION
    assert result.offline_only is False


def test_data_access_violation_blocks_gate():
    result = evaluate_performance_risk_validation_gate(_ready_input(data_access_requested=True))

    assert PerformanceRiskValidationGateRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.BLOCK_PERFORMANCE_RISK_VALIDATION


def test_premature_multi_scenario_request_blocks_gate():
    result = evaluate_performance_risk_validation_gate(_ready_input(multi_scenario_controlled_simulation_requested=True))

    assert PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION in result.risks
    assert result.decision is PerformanceRiskValidationGateDecision.BLOCK_PERFORMANCE_RISK_VALIDATION


def test_score_and_risk_detection_can_use_supplied_findings():
    data = _ready_input()
    result = evaluate_performance_risk_validation_gate(data)
    risks = detect_performance_risk_validation_risks(data, result.findings)
    score = compute_performance_risk_validation_score(data, result.findings, risks)

    assert risks == ()
    assert score.overall_score == 100


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_performance_risk_validation_recommendations(
        (
            PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH,
            PerformanceRiskValidationGateRisk.EXPOSURE_TOO_HIGH,
            PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW,
        ),
        PerformanceRiskValidationGateDecision.REQUIRE_RISK_REDUCTION,
    )

    assert recommendations.count(PerformanceRiskValidationGateRecommendation.REDUCE_EXPOSURE) == 1
    assert PerformanceRiskValidationGateRecommendation.ADD_MORE_TRADES in recommendations
    assert PerformanceRiskValidationGateRecommendation.RUN_PERFORMANCE_RISK_VALIDATION_GATE_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_performance_risk_validation_recommendations(
        (),
        PerformanceRiskValidationGateDecision.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE,
    )

    assert PerformanceRiskValidationGateRecommendation.APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION in recommendations


def test_markdown_contains_decision_score_risks_and_recommendations():
    result = evaluate_performance_risk_validation_gate(_ready_input())
    markdown = render_performance_risk_validation_gate_markdown(result)

    assert "# AGIcore Performance Risk Validation Gate" in markdown
    assert "Decision: APPROVE_PERFORMANCE_RISK_VALIDATION_GATE" in markdown
    assert "Score: 100" in markdown
    assert "Total PnL: 10.0" in markdown
    assert "Risk quality score: 100" in markdown
    assert "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_performance_risk_validation_gate(payload)

    assert result.state is PerformanceRiskValidationGateState.READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PerformanceRiskValidationGateRisk.PERFORMANCE_METRICS_NOT_APPROVED,
            PerformanceRiskValidationGateRecommendation.APPROVE_PERFORMANCE_METRICS_FIRST,
        ),
        (
            PerformanceRiskValidationGateRisk.RISK_METRICS_NOT_APPROVED,
            PerformanceRiskValidationGateRecommendation.APPROVE_RISK_METRICS_FIRST,
        ),
        (
            PerformanceRiskValidationGateRisk.TRADE_COUNT_TOO_LOW,
            PerformanceRiskValidationGateRecommendation.ADD_MORE_TRADES,
        ),
        (
            PerformanceRiskValidationGateRisk.RISK_PER_TRADE_TOO_HIGH,
            PerformanceRiskValidationGateRecommendation.REDUCE_RISK_PER_TRADE,
        ),
        (
            PerformanceRiskValidationGateRisk.PREMATURE_MULTI_SCENARIO_CONTROLLED_SIMULATION,
            PerformanceRiskValidationGateRecommendation.DELAY_MULTI_SCENARIO_CONTROLLED_SIMULATION,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_performance_risk_validation_recommendations(
        (risk,),
        PerformanceRiskValidationGateDecision.REQUIRE_ADDITIONAL_SCENARIOS,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "performance_risk_validation_gate.py",
        "performance_risk_validation_gate_models.py",
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
