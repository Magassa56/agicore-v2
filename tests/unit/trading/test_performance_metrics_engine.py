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
from agicore.trading.controlled_simulation_result_report_post_review_models import (
    OfflineSimulationMetricSummary,
)
from agicore.trading.performance_metrics_engine import (
    compute_average_loss,
    compute_average_win,
    compute_expectancy,
    compute_max_drawdown,
    compute_performance_quality_score,
    compute_performance_stability_score,
    compute_profit_factor,
    compute_return_fraction,
    compute_risk_reward_ratio,
    compute_total_pnl,
    compute_trade_count,
    compute_win_rate,
    detect_performance_metric_risks,
    evaluate_performance_metrics_engine,
    extract_performance_inputs,
    generate_performance_metric_recommendations,
    render_performance_metrics_engine_markdown,
    validate_controlled_simulation_result_report,
)
from agicore.trading.performance_metrics_engine_models import (
    EquityPerformanceSample,
    PerformanceMetricSummary,
    PerformanceMetricsEngineDecision,
    PerformanceMetricsEngineInput,
    PerformanceMetricsEngineRecommendation,
    PerformanceMetricsEngineRisk,
    PerformanceMetricsEngineState,
    PerformanceThresholds,
    TradePerformanceSample,
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


def _ready_input(**overrides):
    runner = _runner_result()
    payload = {
        "controlled_simulation_result_report": _report_result(runner),
        "controlled_simulation_offline_runner_result": runner,
        "controlled_simulation_result_report_input": _upstream("READY_FOR_PERFORMANCE_METRICS_ENGINE"),
        "controlled_simulation_offline_runner_input": _runner_input(),
        "controlled_simulation_review_precheck": _upstream(
            "READY_FOR_CONTROLLED_SIMULATION_OFFLINE_RUNNER",
            "APPROVE_CONTROLLED_SIMULATION_REVIEW_PRECHECK",
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
        "result_report_approved": True,
        "thresholds": PerformanceThresholds(min_trade_count=1, min_expectancy=0.0, min_return_fraction=0.0),
        "metric_tolerance": 1e-6,
        "risk_metrics_engine_requested": False,
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
    return PerformanceMetricsEngineInput(**payload)


def test_evaluate_performance_metrics_engine_approves_nominal_report():
    result = evaluate_performance_metrics_engine(_ready_input())

    assert result.state is PerformanceMetricsEngineState.READY_FOR_RISK_METRICS_ENGINE
    assert result.decision is PerformanceMetricsEngineDecision.APPROVE_PERFORMANCE_METRICS_ENGINE
    assert result.risks == ()
    assert result.offline_only is True
    assert result.engine_score == 100
    assert result.metric_summary.total_pnl == 10.0
    assert result.metric_summary.return_fraction == 0.0001
    assert result.metric_summary.return_percent == 0.01
    assert result.metric_summary.max_drawdown == 3.0
    assert result.metric_summary.win_rate == 1.0
    assert math.isinf(result.metric_summary.profit_factor)
    assert result.metric_summary.expectancy == 10.0
    assert result.metric_summary.trade_count == 1
    assert result.metric_summary.average_win == 10.0
    assert result.metric_summary.average_loss == 0.0
    assert math.isinf(result.metric_summary.risk_reward_ratio)


def test_validate_result_report_refuses_non_approved_report():
    report = _report_result(state="REPORT_INPUT_INVALID", decision="REQUIRE_METRIC_FIXES", risks=("PNL_REPORT_INVALID",))
    data = _ready_input(controlled_simulation_result_report=report, result_report_approved=False)
    result = evaluate_performance_metrics_engine(data)

    assert validate_controlled_simulation_result_report(data) is False
    assert PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_RESULT_REPORT_FIXES
    assert result.state is PerformanceMetricsEngineState.INPUT_INVALID


def test_missing_result_report_requires_report_fixes():
    result = evaluate_performance_metrics_engine(_ready_input(controlled_simulation_result_report=None))

    assert PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED in result.risks
    assert PerformanceMetricsEngineRisk.PERFORMANCE_INPUT_MISSING in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_RESULT_REPORT_FIXES


def test_extract_performance_inputs_uses_runner_samples():
    inputs = extract_performance_inputs(_ready_input())

    assert tuple(sample.pnl for sample in inputs["trade_samples"]) == (10.0,)
    assert tuple(sample.equity for sample in inputs["equity_samples"]) == (100_000.0, 100_005.0, 100_002.0, 100_010.0)
    assert inputs["thresholds"].min_trade_count == 1


def test_compute_metric_functions_are_deterministic():
    trades = (TradePerformanceSample(10.0), TradePerformanceSample(-5.0), TradePerformanceSample(0.0))
    equity = (
        EquityPerformanceSample(0, 100.0),
        EquityPerformanceSample(1, 90.0),
        EquityPerformanceSample(2, 120.0),
    )

    assert compute_total_pnl(trade_samples=trades) == 5.0
    assert compute_return_fraction(20.0, equity_samples=equity) == 0.2
    assert compute_max_drawdown(equity_samples=equity) == (10.0, 0.1)
    assert compute_win_rate(trades) == pytest.approx(1 / 3)
    assert compute_profit_factor(trades) == 2.0
    assert compute_expectancy(trades) == pytest.approx(5.0 / 3)
    assert compute_trade_count(trades) == 3
    assert compute_average_win(trades) == 10.0
    assert compute_average_loss(trades) == -5.0
    assert compute_risk_reward_ratio(10.0, -5.0) == 2.0
    assert compute_performance_stability_score(equity) < 100


def test_quality_score_uses_thresholds():
    summary = PerformanceMetricSummary(10.0, 0.1, 10.0, 1.0, 0.01, 1.0, 2.0, 10.0, 2, 10.0, -5.0, 2.0, 95, 0)
    thresholds = PerformanceThresholds(min_trade_count=2, min_win_rate=0.5, min_profit_factor=1.0, min_expectancy=0.0)

    assert compute_performance_quality_score(summary, thresholds) == 100
    assert compute_performance_quality_score(summary, None) == 0


def test_trade_sample_empty_requires_trade_sample_fixes():
    result = evaluate_performance_metrics_engine(_ready_input(trade_samples=()))

    assert PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_TRADE_SAMPLE_FIXES


def test_equity_sample_invalid_requires_equity_sample_fixes():
    result = evaluate_performance_metrics_engine(
        _ready_input(equity_samples=(EquityPerformanceSample(0, 100.0), EquityPerformanceSample(0, 90.0)))
    )

    assert PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_EQUITY_SAMPLE_FIXES


def test_thresholds_missing_requires_threshold_fixes():
    result = evaluate_performance_metrics_engine(_ready_input(thresholds=None))

    assert PerformanceMetricsEngineRisk.PERFORMANCE_THRESHOLD_MISSING in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_THRESHOLD_FIXES


def test_pnl_mismatch_requires_performance_review():
    result = evaluate_performance_metrics_engine(_ready_input(trade_samples=(TradePerformanceSample(11.0),)))

    assert PerformanceMetricsEngineRisk.PNL_INVALID in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW
    assert result.state is PerformanceMetricsEngineState.METRICS_COMPLETED_WITH_WARNINGS


def test_return_invalid_is_detected():
    report = _report_result(
        metric_summary=OfflineSimulationMetricSummary(100_000.0, 100_010.0, 10.0, 10.0, 0.0, 3.0, 0.00003, 1, 1, 0, 1.0, float("inf"), 10.0, -2.0)
    )
    result = evaluate_performance_metrics_engine(_ready_input(controlled_simulation_result_report=report))

    assert PerformanceMetricsEngineRisk.RETURN_INVALID in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW


def test_drawdown_mismatch_is_detected():
    result = evaluate_performance_metrics_engine(
        _ready_input(
            equity_samples=(
                EquityPerformanceSample(0, 100_000.0),
                EquityPerformanceSample(1, 99_900.0),
                EquityPerformanceSample(2, 100_010.0),
            )
        )
    )

    assert PerformanceMetricsEngineRisk.DRAWDOWN_INVALID in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW


def test_win_rate_profit_factor_and_expectancy_mismatch_are_detected():
    result = evaluate_performance_metrics_engine(
        _ready_input(trade_samples=(TradePerformanceSample(10.0), TradePerformanceSample(-5.0)))
    )

    assert PerformanceMetricsEngineRisk.WIN_RATE_INVALID in result.risks
    assert PerformanceMetricsEngineRisk.PROFIT_FACTOR_INVALID in result.risks
    assert PerformanceMetricsEngineRisk.EXPECTANCY_INVALID in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW


def test_trade_count_too_low_is_detected():
    result = evaluate_performance_metrics_engine(_ready_input(thresholds=PerformanceThresholds(min_trade_count=2)))

    assert PerformanceMetricsEngineRisk.TRADE_COUNT_TOO_LOW in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW


def test_risk_reward_invalid_is_detected():
    report = _report_result(
        metric_summary=OfflineSimulationMetricSummary(100_000.0, 100_000.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1, 0, 0, 0.0, 0.0, 0.0, 0.0)
    )
    result = evaluate_performance_metrics_engine(
        _ready_input(
            controlled_simulation_result_report=report,
            trade_samples=(TradePerformanceSample(0.0),),
            thresholds=PerformanceThresholds(min_risk_reward_ratio=1.0),
        )
    )

    assert PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK in result.risks
    assert result.metric_summary.risk_reward_ratio == 0.0


def test_performance_stability_weak_is_detected():
    result = evaluate_performance_metrics_engine(
        _ready_input(thresholds=PerformanceThresholds(max_drawdown_fraction=0.0))
    )

    assert PerformanceMetricsEngineRisk.PERFORMANCE_STABILITY_WEAK in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.REQUIRE_PERFORMANCE_REVIEW


def test_real_execution_boundary_violation_blocks_engine():
    result = evaluate_performance_metrics_engine(_ready_input(real_execution_requested=True))

    assert PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.state is PerformanceMetricsEngineState.METRICS_BLOCKED
    assert result.decision is PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS
    assert result.offline_only is False


def test_data_access_violation_blocks_engine():
    result = evaluate_performance_metrics_engine(_ready_input(data_access_requested=True))

    assert PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS


def test_premature_risk_metrics_engine_blocks_engine():
    result = evaluate_performance_metrics_engine(_ready_input(risk_metrics_engine_requested=True))

    assert PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE in result.risks
    assert result.decision is PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS


def test_detect_performance_metric_risks_can_use_supplied_inputs_and_summary():
    data = _ready_input()
    inputs = extract_performance_inputs(data)
    result = evaluate_performance_metrics_engine(data)
    risks = detect_performance_metric_risks(data, result.metric_summary, inputs)

    assert risks == ()


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_performance_metric_recommendations(
        (
            PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION,
            PerformanceMetricsEngineRisk.DATA_ACCESS_VIOLATION,
            PerformanceMetricsEngineRisk.PNL_INVALID,
        ),
        PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS,
    )

    assert recommendations.count(PerformanceMetricsEngineRecommendation.REMOVE_DATA_ACCESS) == 1
    assert PerformanceMetricsEngineRecommendation.RECHECK_PNL in recommendations
    assert PerformanceMetricsEngineRecommendation.RUN_PERFORMANCE_METRICS_ENGINE_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_performance_metric_recommendations(
        (),
        PerformanceMetricsEngineDecision.APPROVE_PERFORMANCE_METRICS_ENGINE,
    )

    assert PerformanceMetricsEngineRecommendation.APPROVE_RISK_METRICS_ENGINE in recommendations


def test_markdown_contains_decision_metrics_risks_and_recommendations():
    result = evaluate_performance_metrics_engine(_ready_input())
    markdown = render_performance_metrics_engine_markdown(result)

    assert "# AGIcore Performance Metrics Engine" in markdown
    assert "Decision: APPROVE_PERFORMANCE_METRICS_ENGINE" in markdown
    assert "Total PnL: 10.0" in markdown
    assert "Risk/reward ratio: inf" in markdown
    assert "APPROVE_RISK_METRICS_ENGINE" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_performance_metrics_engine(payload)

    assert result.state is PerformanceMetricsEngineState.READY_FOR_RISK_METRICS_ENGINE


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            PerformanceMetricsEngineRisk.RESULT_REPORT_NOT_APPROVED,
            PerformanceMetricsEngineRecommendation.APPROVE_RESULT_REPORT_FIRST,
        ),
        (
            PerformanceMetricsEngineRisk.TRADE_SAMPLE_EMPTY,
            PerformanceMetricsEngineRecommendation.PROVIDE_TRADE_SAMPLES,
        ),
        (
            PerformanceMetricsEngineRisk.EQUITY_SAMPLE_INVALID,
            PerformanceMetricsEngineRecommendation.REBUILD_EQUITY_SAMPLES,
        ),
        (
            PerformanceMetricsEngineRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,
            PerformanceMetricsEngineRecommendation.RESTORE_REAL_EXECUTION_BOUNDARIES,
        ),
        (
            PerformanceMetricsEngineRisk.PREMATURE_RISK_METRICS_ENGINE,
            PerformanceMetricsEngineRecommendation.DELAY_RISK_METRICS_ENGINE,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_performance_metric_recommendations(
        (risk,),
        PerformanceMetricsEngineDecision.BLOCK_PERFORMANCE_METRICS,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "performance_metrics_engine.py",
        "performance_metrics_engine_models.py",
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
