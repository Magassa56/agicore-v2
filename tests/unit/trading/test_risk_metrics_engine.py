import ast
import math
from pathlib import Path

import pytest

from agicore.trading.controlled_simulation_offline_runner import run_controlled_simulation_offline_runner
from agicore.trading.controlled_simulation_offline_runner_models import (
    OfflineSignalEvent,
    OfflineSyntheticMarketBar,
)
from agicore.trading.controlled_simulation_result_report_post_review import (
    evaluate_controlled_simulation_result_report_post_review,
)
from agicore.trading.performance_metrics_engine import evaluate_performance_metrics_engine
from agicore.trading.performance_metrics_engine_models import (
    PerformanceMetricsEngineInput,
    PerformanceThresholds,
)
from agicore.trading.risk_metrics_engine import (
    compute_consecutive_loss_count,
    compute_exposure_fraction,
    compute_loss_limit_usage,
    compute_loss_stability_score,
    compute_max_drawdown_fraction,
    compute_max_loss,
    compute_position_risk,
    compute_risk_per_trade,
    compute_risk_quality_score,
    compute_stop_condition_quality_score,
    detect_risk_metric_risks,
    detect_risk_metric_violations,
    evaluate_risk_metrics_engine,
    extract_risk_inputs,
    generate_risk_metric_recommendations,
    render_risk_metrics_engine_markdown,
    validate_performance_metrics_result,
)
from agicore.trading.risk_metrics_engine_models import (
    EquityRiskSample,
    PositionRiskSample,
    RiskMetricSummary,
    RiskMetricsEngineDecision,
    RiskMetricsEngineInput,
    RiskMetricsEngineRecommendation,
    RiskMetricsEngineRisk,
    RiskMetricsEngineState,
    RiskThresholds,
    StopConditionRiskSample,
    TradeRiskSample,
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


def _report_result(runner_result=None, **overrides):
    runner_result = _runner_result() if runner_result is None else runner_result
    report = evaluate_controlled_simulation_result_report_post_review(
        {
            "controlled_simulation_offline_runner_result": runner_result,
            "controlled_simulation_offline_runner_input": _runner_input(),
            "controlled_simulation_review_precheck": _upstream(
                "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
                "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
            ),
            "offline_runner_approved": True,
            "require_flat_final_position": True,
            "max_allowed_drawdown_fraction": 0.20,
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
    )
    payload = dict(report.__dict__)
    payload.update(overrides)
    return payload


def _performance_result(runner_result=None, report_result=None, **overrides):
    runner_result = _runner_result() if runner_result is None else runner_result
    report_result = _report_result(runner_result) if report_result is None else report_result
    performance = evaluate_performance_metrics_engine(
        PerformanceMetricsEngineInput(
            controlled_simulation_result_report=report_result,
            controlled_simulation_offline_runner_result=runner_result,
            controlled_simulation_result_report_input=_upstream("READY_FOR_PERFORMANCE_METRICS_ENGINE"),
            controlled_simulation_offline_runner_input=_runner_input(),
            controlled_simulation_review_precheck=_upstream(
                "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
                "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
            ),
            paper_runtime_forward_test_plan=_upstream("READY_FOR_PAPER_BROKER_SANDBOX_SESSION"),
            official_paper_validation_report=_upstream("READY_FOR_SUPERVISED_PAPER_RUNTIME_TRIAL"),
            paper_runtime_validation=_upstream("READY_FOR_OFFICIAL_PAPER_VALIDATION_REPORT"),
            paper_trading_runtime=_upstream("COMPLETED"),
            observability_verification=_upstream("READY_FOR_PAPER_RUNTIME_PREP"),
            rollback_verification=_upstream("READY_FOR_OBSERVABILITY_VERIFICATION"),
            kill_switch_verification=_upstream("READY_FOR_ROLLBACK_VERIFICATION"),
            human_validated_paper_session=_upstream("READY_FOR_SUPERVISED_PAPER_SESSION"),
            supervised_paper_session=_upstream("READY_FOR_PAPER_BROKER_ADAPTER"),
            result_report_approved=True,
            thresholds=PerformanceThresholds(min_trade_count=1, min_expectancy=0.0, min_return_fraction=0.0),
        )
    )
    payload = dict(performance.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    runner = _runner_result()
    report = _report_result(runner)
    performance = _performance_result(runner, report)
    payload = {
        "performance_metrics_result": performance,
        "performance_metrics_input": _upstream("READY_FOR_RISK_METRICS_ENGINE"),
        "performance_thresholds": PerformanceThresholds(min_trade_count=1, min_expectancy=0.0),
        "controlled_simulation_result_report": report,
        "controlled_simulation_offline_runner_result": runner,
        "offline_simulation_metrics": runner["metrics"],
        "offline_equity_curve": runner["equity_curve"],
        "offline_position_state": runner["final_position"],
        "offline_stop_conditions": runner["stop_conditions"],
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
        "thresholds": RiskThresholds(),
        "metric_tolerance": 1e-6,
        "performance_risk_validation_gate_requested": False,
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
    return RiskMetricsEngineInput(**payload)


def test_evaluate_risk_metrics_engine_approves_nominal_performance_result():
    result = evaluate_risk_metrics_engine(_ready_input())

    assert result.state is RiskMetricsEngineState.READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE
    assert result.decision is RiskMetricsEngineDecision.APPROVE_RISK_METRICS_ENGINE
    assert result.risks == ()
    assert result.violations == ()
    assert result.offline_only is True
    assert result.engine_score == 100
    assert result.metric_summary.max_loss == 0.0
    assert result.metric_summary.max_drawdown_fraction == pytest.approx(3.0 / 100_005.0)
    assert result.metric_summary.loss_limit_usage == 0.0
    assert result.metric_summary.risk_per_trade_fraction == 0.0
    assert 0.0 < result.metric_summary.exposure_fraction < 0.01
    assert result.metric_summary.position_risk == 105.0
    assert result.metric_summary.consecutive_loss_count == 0
    assert result.metric_summary.loss_stability_score == 100
    assert result.metric_summary.stop_condition_quality_score == 100
    assert result.metric_summary.risk_quality_score == 100


def test_validate_performance_metrics_result_refuses_non_approved_result():
    performance = _performance_result(state="INPUT_INVALID", decision="REQUIRE_THRESHOLD_FIXES")
    data = _ready_input(performance_metrics_result=performance, performance_metrics_approved=False)
    result = evaluate_risk_metrics_engine(data)

    assert validate_performance_metrics_result(data) is False
    assert RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_PERFORMANCE_METRICS_FIXES


def test_missing_performance_metrics_result_requires_performance_fixes():
    result = evaluate_risk_metrics_engine(
        _ready_input(
            performance_metrics_result=None,
            performance_metric_summary=None,
            controlled_simulation_result_report=None,
            controlled_simulation_offline_runner_result=None,
            offline_simulation_metrics=None,
            offline_equity_curve=None,
            offline_position_state=None,
            offline_stop_conditions=None,
        )
    )

    assert RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED in result.risks
    assert RiskMetricsEngineRisk.RISK_INPUT_MISSING in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_PERFORMANCE_METRICS_FIXES


def test_extract_risk_inputs_uses_performance_and_runner_samples():
    inputs = extract_risk_inputs(_ready_input())

    assert tuple(sample.pnl for sample in inputs["trade_risk_samples"]) == (10.0,)
    assert tuple(sample.equity for sample in inputs["equity_risk_samples"]) == (
        100_000.0,
        100_005.0,
        100_002.0,
        100_010.0,
    )
    assert inputs["initial_equity"] == 100_000.0
    assert inputs["stop_condition_samples"][0].configured is True


def test_compute_risk_metric_functions_are_deterministic():
    trades = (
        TradeRiskSample(10.0, risk_amount=2.0),
        TradeRiskSample(-5.0, risk_amount=5.0),
        TradeRiskSample(-2.0, risk_amount=2.0),
        TradeRiskSample(3.0, risk_amount=1.0),
    )
    equity = (
        EquityRiskSample(0, 100.0),
        EquityRiskSample(1, 90.0),
        EquityRiskSample(2, 120.0),
    )
    positions = (
        PositionRiskSample(0, "SIM", 2.0, 50.0, 100.0),
        PositionRiskSample(1, "SIM", 1.0, 120.0, 120.0),
    )
    stops = (StopConditionRiskSample("loss", True, False),)

    assert compute_max_loss(trades, equity, 100.0) == 10.0
    assert compute_max_drawdown_fraction(equity) == 0.1
    assert compute_loss_limit_usage(10.0, RiskThresholds(max_loss_amount=100.0)) == 0.1
    assert compute_risk_per_trade(trades, 100.0) == 0.05
    assert compute_exposure_fraction(positions) == 1.0
    assert compute_position_risk(positions) == 120.0
    assert compute_consecutive_loss_count(trades) == 2
    assert compute_loss_stability_score(trades) < 100
    assert compute_stop_condition_quality_score(stops) == 100


def test_risk_quality_score_uses_thresholds():
    summary = RiskMetricSummary(
        max_loss=1.0,
        max_drawdown_fraction=0.01,
        loss_limit_usage=0.1,
        risk_per_trade_fraction=0.01,
        exposure_fraction=0.5,
        position_risk=50.0,
        consecutive_loss_count=1,
        loss_stability_score=90,
        stop_condition_quality_score=100,
    )
    thresholds = RiskThresholds(max_loss_amount=10.0, max_position_risk_amount=100.0)

    assert compute_risk_quality_score(summary, thresholds) == 100
    assert compute_risk_quality_score(summary, None) == 0


def test_trade_risk_sample_empty_requires_risk_sample_fixes():
    result = evaluate_risk_metrics_engine(_ready_input(trade_risk_samples=()))

    assert RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_RISK_SAMPLE_FIXES


def test_equity_risk_sample_invalid_requires_equity_sample_fixes():
    result = evaluate_risk_metrics_engine(
        _ready_input(equity_risk_samples=(EquityRiskSample(0, 100.0), EquityRiskSample(0, 90.0)))
    )

    assert RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES


def test_position_risk_sample_invalid_requires_position_sample_fixes():
    result = evaluate_risk_metrics_engine(
        _ready_input(position_risk_samples=(PositionRiskSample(0, "SIM", 1.0, -10.0, 100_000.0),))
    )

    assert RiskMetricsEngineRisk.POSITION_RISK_SAMPLE_INVALID in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_POSITION_SAMPLE_FIXES


def test_stop_condition_sample_invalid_requires_risk_sample_fixes():
    result = evaluate_risk_metrics_engine(_ready_input(stop_condition_samples=(StopConditionRiskSample("loss", False),)))

    assert RiskMetricsEngineRisk.STOP_CONDITION_SAMPLE_INVALID in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_RISK_SAMPLE_FIXES


def test_thresholds_missing_requires_threshold_fixes():
    result = evaluate_risk_metrics_engine(_ready_input(thresholds=None))

    assert RiskMetricsEngineRisk.RISK_THRESHOLD_MISSING in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES


def test_drawdown_breach_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(
            equity_risk_samples=(
                EquityRiskSample(0, 100_000.0),
                EquityRiskSample(1, 70_000.0),
                EquityRiskSample(2, 80_000.0),
            ),
            thresholds=RiskThresholds(max_drawdown_fraction=0.10),
        )
    )

    assert RiskMetricsEngineRisk.DRAWDOWN_LIMIT_BREACHED in result.risks
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_RISK_REVIEW


def test_loss_limit_breach_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(
            trade_risk_samples=(TradeRiskSample(-6_000.0),),
            thresholds=RiskThresholds(max_loss_amount=5_000.0, max_risk_per_trade_fraction=1.0),
        )
    )

    assert RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED in result.risks
    assert result.metric_summary.max_loss == 6_000.0
    assert result.decision is RiskMetricsEngineDecision.REQUIRE_RISK_REVIEW


def test_risk_per_trade_breach_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(trade_risk_samples=(TradeRiskSample(10.0, risk_amount=3_000.0),))
    )

    assert RiskMetricsEngineRisk.RISK_PER_TRADE_TOO_HIGH in result.risks
    assert result.metric_summary.risk_per_trade_fraction == 0.03


def test_exposure_breach_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(position_risk_samples=(PositionRiskSample(0, "SIM", 2.0, 100_000.0, 100_000.0),))
    )

    assert RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH in result.risks
    assert result.metric_summary.exposure_fraction == 2.0


def test_consecutive_loss_limit_breach_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(
            trade_risk_samples=(
                TradeRiskSample(-1.0),
                TradeRiskSample(-1.0),
                TradeRiskSample(-1.0),
                TradeRiskSample(-1.0),
            ),
            thresholds=RiskThresholds(max_loss_amount=100.0, max_risk_per_trade_fraction=1.0),
        )
    )

    assert RiskMetricsEngineRisk.CONSECUTIVE_LOSS_LIMIT_BREACHED in result.risks
    assert RiskMetricsEngineRisk.LOSS_STABILITY_WEAK in result.risks


def test_stop_condition_quality_weak_is_detected():
    result = evaluate_risk_metrics_engine(
        _ready_input(stop_condition_samples=(StopConditionRiskSample("drawdown", True, True, ("drawdown",), ("DRAWDOWN_LIMIT_BREACHED",)),))
    )

    assert RiskMetricsEngineRisk.STOP_CONDITION_QUALITY_WEAK in result.risks
    assert result.metric_summary.stop_condition_quality_score == 50


def test_real_execution_boundary_violation_blocks_engine():
    result = evaluate_risk_metrics_engine(_ready_input(real_execution_requested=True))

    assert RiskMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is RiskMetricsEngineState.RISK_METRICS_BLOCKED
    assert result.decision is RiskMetricsEngineDecision.BLOCK_RISK_METRICS
    assert result.offline_only is False


def test_data_access_violation_blocks_engine():
    result = evaluate_risk_metrics_engine(_ready_input(data_access_requested=True))

    assert RiskMetricsEngineRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is RiskMetricsEngineDecision.BLOCK_RISK_METRICS


def test_premature_performance_risk_validation_gate_blocks_engine():
    result = evaluate_risk_metrics_engine(_ready_input(performance_risk_validation_gate_requested=True))

    assert RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE in result.risks
    assert result.decision is RiskMetricsEngineDecision.BLOCK_RISK_METRICS


def test_detect_risk_metric_violations_returns_failed_threshold_checks_only():
    summary = RiskMetricSummary(max_loss=20.0, max_drawdown_fraction=0.30, risk_quality_score=50)
    thresholds = RiskThresholds(max_loss_amount=10.0, max_drawdown_fraction=0.20)
    violations = detect_risk_metric_violations(summary, thresholds)

    assert RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED in tuple(risk for finding in violations for risk in finding.risks)
    assert RiskMetricsEngineRisk.DRAWDOWN_LIMIT_BREACHED in tuple(risk for finding in violations for risk in finding.risks)


def test_detect_risk_metric_risks_can_use_supplied_inputs_and_summary():
    data = _ready_input()
    inputs = extract_risk_inputs(data)
    result = evaluate_risk_metrics_engine(data)
    risks = detect_risk_metric_risks(data, result.metric_summary, inputs)

    assert risks == ()


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_risk_metric_recommendations(
        (
            RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH,
            RiskMetricsEngineRisk.EXPOSURE_TOO_HIGH,
            RiskMetricsEngineRisk.LOSS_LIMIT_BREACHED,
        ),
        RiskMetricsEngineDecision.REQUIRE_RISK_REVIEW,
    )

    assert recommendations.count(RiskMetricsEngineRecommendation.REDUCE_EXPOSURE) == 1
    assert RiskMetricsEngineRecommendation.REDUCE_LOSS_LIMIT_USAGE in recommendations
    assert RiskMetricsEngineRecommendation.RUN_RISK_METRICS_ENGINE_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_risk_metric_recommendations(
        (),
        RiskMetricsEngineDecision.APPROVE_RISK_METRICS_ENGINE,
    )

    assert RiskMetricsEngineRecommendation.APPROVE_PERFORMANCE_RISK_VALIDATION_GATE in recommendations


def test_markdown_contains_decision_metrics_violations_risks_and_recommendations():
    result = evaluate_risk_metrics_engine(_ready_input())
    markdown = render_risk_metrics_engine_markdown(result)

    assert "# AGIcore Risk Metrics Engine" in markdown
    assert "Decision: APPROVE_RISK_METRICS_ENGINE" in markdown
    assert "Max loss: 0.0" in markdown
    assert "Risk quality score: 100" in markdown
    assert "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_risk_metrics_engine(payload)

    assert result.state is RiskMetricsEngineState.READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            RiskMetricsEngineRisk.PERFORMANCE_METRICS_NOT_APPROVED,
            RiskMetricsEngineRecommendation.APPROVE_PERFORMANCE_METRICS_FIRST,
        ),
        (
            RiskMetricsEngineRisk.TRADE_RISK_SAMPLE_EMPTY,
            RiskMetricsEngineRecommendation.PROVIDE_TRADE_RISK_SAMPLES,
        ),
        (
            RiskMetricsEngineRisk.EQUITY_RISK_SAMPLE_INVALID,
            RiskMetricsEngineRecommendation.REBUILD_EQUITY_RISK_SAMPLES,
        ),
        (
            RiskMetricsEngineRisk.RISK_PER_TRADE_TOO_HIGH,
            RiskMetricsEngineRecommendation.REDUCE_RISK_PER_TRADE,
        ),
        (
            RiskMetricsEngineRisk.PREMATURE_PERFORMANCE_RISK_VALIDATION_GATE,
            RiskMetricsEngineRecommendation.DELAY_PERFORMANCE_RISK_VALIDATION_GATE,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_risk_metric_recommendations(
        (risk,),
        RiskMetricsEngineDecision.REQUIRE_RISK_REVIEW,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "risk_metrics_engine.py",
        "risk_metrics_engine_models.py",
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
