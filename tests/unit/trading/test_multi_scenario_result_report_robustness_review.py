import ast
from dataclasses import replace
from pathlib import Path

import pytest

from agicore.trading.multi_scenario_controlled_simulation import run_multi_scenario_controlled_simulation
from agicore.trading.multi_scenario_controlled_simulation_models import (
    ControlledSimulationScenarioType,
    MultiScenarioControlledSimulationInput,
)
from agicore.trading.multi_scenario_result_report_robustness_review import (
    compute_multi_scenario_result_report_score,
    detect_multi_scenario_result_report_risks,
    evaluate_multi_scenario_result_report_robustness_review,
    generate_multi_scenario_result_report_recommendations,
    render_multi_scenario_result_report_robustness_review_markdown,
    review_drawdown_scenario_behavior,
    review_losing_scenario_behavior,
    review_multi_scenario_drawdown_quality,
    review_multi_scenario_expectancy_quality,
    review_multi_scenario_pnl_quality,
    review_multi_scenario_profit_factor_quality,
    review_multi_scenario_readiness_for_paper_broker_read_only,
    review_multi_scenario_robustness_quality,
    review_multi_scenario_stability_quality,
    review_position_inconsistency_scenario_behavior,
    review_risk_violation_scenario_behavior,
    review_scenario_pass_fail_distribution,
    review_stop_condition_scenario_behavior,
    summarize_multi_scenario_aggregate_metrics,
    validate_multi_scenario_controlled_simulation_result,
)
from agicore.trading.multi_scenario_result_report_robustness_review_models import (
    MultiScenarioResultReportDecision,
    MultiScenarioResultReportInput,
    MultiScenarioResultReportRecommendation,
    MultiScenarioResultReportRisk,
    MultiScenarioResultReportState,
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


def _simulation_input(**overrides):
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
    }
    payload.update(overrides)
    return MultiScenarioControlledSimulationInput(**payload)


def _simulation_result(**overrides):
    result = run_multi_scenario_controlled_simulation(_simulation_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    simulation = overrides.pop("multi_scenario_controlled_simulation_result", _simulation_result())
    payload = {
        "multi_scenario_controlled_simulation_result": simulation,
        "multi_scenario_metric_summary": simulation["metric_summary"] if simulation else None,
        "multi_scenario_aggregate_report": simulation["aggregate_report"] if simulation else None,
        "controlled_simulation_scenario_results": simulation["scenario_results"] if simulation else (),
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
        "multi_scenario_simulation_approved": True,
        "min_robustness_score": 60,
        "min_stability_score": 60,
        "min_total_pnl": 0.0,
        "max_drawdown_fraction": 0.25,
        "min_profit_factor": 1.0,
        "min_expectancy": 0.0,
        "max_failed_scenarios": 0,
        "paper_broker_read_only_preparation_requested": False,
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
    return MultiScenarioResultReportInput(**payload)


def _replace_scenario(results, scenario_type, **updates):
    updated = []
    for result in results:
        if result.scenario_type == scenario_type:
            updated.append(replace(result, **updates))
        else:
            updated.append(result)
    return tuple(updated)


def test_evaluate_multi_scenario_result_report_approves_nominal_result():
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input())

    assert result.state is MultiScenarioResultReportState.READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION
    assert result.decision is MultiScenarioResultReportDecision.APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW
    assert result.risks == ()
    assert result.offline_only is True
    assert result.report_score >= 90
    assert result.aggregate_metric_review.scenario_count == 9
    assert result.aggregate_metric_review.total_pnl == 44.0
    assert result.robustness_review.robustness_score == 93
    assert result.stability_review.stability_score == 88
    assert result.readiness_finding.passed is True


def test_validate_multi_scenario_result_refuses_non_approved_simulation():
    simulation = _simulation_result(state="INPUT_INVALID", decision="REQUIRE_SCENARIO_SUITE_FIXES", risks=("SCENARIO_SUITE_EMPTY",))
    data = _ready_input(multi_scenario_controlled_simulation_result=simulation, multi_scenario_simulation_approved=False)
    result = evaluate_multi_scenario_result_report_robustness_review(data)

    assert validate_multi_scenario_controlled_simulation_result(data) is False
    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_MULTI_SCENARIO_FIXES


def test_missing_result_and_metrics_are_detected():
    result = evaluate_multi_scenario_result_report_robustness_review(
        _ready_input(
            multi_scenario_controlled_simulation_result=None,
            multi_scenario_metric_summary=None,
            multi_scenario_aggregate_report=None,
            controlled_simulation_scenario_results=(),
            multi_scenario_simulation_approved=False,
        )
    )

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_RESULT_MISSING in result.risks
    assert MultiScenarioResultReportRisk.AGGREGATE_METRICS_MISSING in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_MULTI_SCENARIO_FIXES


def test_summary_and_review_functions_are_deterministic():
    data = _ready_input()

    aggregate = summarize_multi_scenario_aggregate_metrics(data)
    assert aggregate.passed is True
    assert aggregate.scenario_count == 9
    assert review_scenario_pass_fail_distribution(data).passed is True
    assert review_multi_scenario_pnl_quality(data).passed is True
    assert review_multi_scenario_drawdown_quality(data).passed is True
    assert review_multi_scenario_profit_factor_quality(data).passed is True
    assert review_multi_scenario_expectancy_quality(data).passed is True
    assert review_multi_scenario_stability_quality(data).passed is True
    assert review_multi_scenario_robustness_quality(data).passed is True
    assert review_losing_scenario_behavior(data).passed is True
    assert review_drawdown_scenario_behavior(data).passed is True
    assert review_risk_violation_scenario_behavior(data).passed is True
    assert review_position_inconsistency_scenario_behavior(data).passed is True
    assert review_stop_condition_scenario_behavior(data).passed is True
    assert review_multi_scenario_readiness_for_paper_broker_read_only(data).passed is True


def test_robustness_weak_requires_robustness_fixes():
    simulation = _simulation_result()
    weak_summary = replace(simulation["metric_summary"], robustness_score=10)
    data = _ready_input(multi_scenario_metric_summary=weak_summary)
    result = evaluate_multi_scenario_result_report_robustness_review(data)

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_ROBUSTNESS_FIXES


def test_stability_weak_requires_stability_fixes():
    simulation = _simulation_result()
    weak_summary = replace(simulation["metric_summary"], stability_score=10)
    data = _ready_input(multi_scenario_metric_summary=weak_summary)
    result = evaluate_multi_scenario_result_report_robustness_review(data)

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_STABILITY_FIXES


def test_losing_scenario_invalid_is_detected():
    simulation = _simulation_result()
    scenarios = _replace_scenario(simulation["scenario_results"], ControlledSimulationScenarioType.LOSING_SCENARIO, pnl=1.0)
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(controlled_simulation_scenario_results=scenarios))

    assert MultiScenarioResultReportRisk.LOSING_SCENARIO_BEHAVIOR_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_drawdown_scenario_invalid_is_detected():
    simulation = _simulation_result()
    scenarios = _replace_scenario(simulation["scenario_results"], ControlledSimulationScenarioType.DRAWDOWN_SCENARIO, max_drawdown_fraction=0.0)
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(controlled_simulation_scenario_results=scenarios))

    assert MultiScenarioResultReportRisk.DRAWDOWN_SCENARIO_BEHAVIOR_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_risk_violation_scenario_invalid_is_detected():
    simulation = _simulation_result()
    scenarios = _replace_scenario(
        simulation["scenario_results"],
        ControlledSimulationScenarioType.RISK_VIOLATION_SCENARIO,
        failures=("risk_violation",),
    )
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(controlled_simulation_scenario_results=scenarios))

    assert MultiScenarioResultReportRisk.RISK_VIOLATION_SCENARIO_BEHAVIOR_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_RISK_REDUCTION


def test_position_inconsistency_scenario_invalid_is_detected():
    simulation = _simulation_result()
    scenarios = _replace_scenario(
        simulation["scenario_results"],
        ControlledSimulationScenarioType.POSITION_INCONSISTENCY_SCENARIO,
        failures=("position_inconsistent",),
    )
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(controlled_simulation_scenario_results=scenarios))

    assert MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_POSITION_CONSISTENCY_FIXES


def test_stop_condition_scenario_invalid_is_detected():
    simulation = _simulation_result()
    scenarios = _replace_scenario(
        simulation["scenario_results"],
        ControlledSimulationScenarioType.STOP_CONDITION_SCENARIO,
        risks=("STOP_CONDITIONS_MISSING",),
    )
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(controlled_simulation_scenario_results=scenarios))

    assert MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_STOP_CONDITION_FIXES


def test_drawdown_quality_invalid_requires_risk_reduction():
    simulation = _simulation_result()
    bad_summary = replace(simulation["metric_summary"], max_drawdown_fraction=0.5)
    result = evaluate_multi_scenario_result_report_robustness_review(
        _ready_input(multi_scenario_metric_summary=bad_summary, max_drawdown_fraction=0.25)
    )

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_DRAWDOWN_REVIEW_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_RISK_REDUCTION


def test_paper_broker_read_only_preparation_premature_blocks_report():
    result = evaluate_multi_scenario_result_report_robustness_review(
        _ready_input(paper_broker_read_only_preparation_requested=True)
    )

    assert MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE in result.risks
    assert result.decision is MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT
    assert result.state is MultiScenarioResultReportState.REPORT_BLOCKED


def test_real_execution_boundary_violation_blocks_report():
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(real_execution_requested=True))

    assert MultiScenarioResultReportRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT
    assert result.offline_only is False


def test_data_access_violation_blocks_report():
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(data_access_requested=True))

    assert MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT


def test_score_and_risk_detection_can_use_supplied_findings():
    data = _ready_input()
    result = evaluate_multi_scenario_result_report_robustness_review(data)
    risks = detect_multi_scenario_result_report_risks(data, result.findings)
    score = compute_multi_scenario_result_report_score(data, result.findings, risks)

    assert risks == ()
    assert score.overall_score >= 90


def test_recommendations_are_risk_driven_and_deduplicated():
    recommendations = generate_multi_scenario_result_report_recommendations(
        (
            MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION,
            MultiScenarioResultReportRisk.DATA_ACCESS_VIOLATION,
            MultiScenarioResultReportRisk.MULTI_SCENARIO_ROBUSTNESS_WEAK,
        ),
        MultiScenarioResultReportDecision.BLOCK_MULTI_SCENARIO_RESULT_REPORT,
    )

    assert recommendations.count(MultiScenarioResultReportRecommendation.REMOVE_DATA_ACCESS) == 1
    assert MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_ROBUSTNESS in recommendations
    assert MultiScenarioResultReportRecommendation.RUN_MULTI_SCENARIO_RESULT_REPORT_SUITE in recommendations


def test_approval_recommendation_follows_approval_decision():
    recommendations = generate_multi_scenario_result_report_recommendations(
        (),
        MultiScenarioResultReportDecision.APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW,
    )

    assert MultiScenarioResultReportRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION in recommendations


def test_markdown_contains_decision_metrics_risks_and_recommendations():
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input())
    markdown = render_multi_scenario_result_report_robustness_review_markdown(result)

    assert "# AGIcore Multi-Scenario Result Report + Robustness Review" in markdown
    assert "Decision: APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW" in markdown
    assert "Scenario count: 9" in markdown
    assert "Robustness score: 93" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION" in markdown


def test_mapping_inputs_are_supported_and_extra_keys_are_ignored():
    payload = dict(_ready_input().__dict__)
    payload["ignored_future_key"] = "ignored"
    result = evaluate_multi_scenario_result_report_robustness_review(payload)

    assert result.state is MultiScenarioResultReportState.READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION


def test_profit_factor_and_expectancy_invalid_are_detected():
    simulation = _simulation_result()
    bad_summary = replace(simulation["metric_summary"], profit_factor=0.5, expectancy=-1.0)
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(multi_scenario_metric_summary=bad_summary))

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_PROFIT_FACTOR_REVIEW_INVALID in result.risks
    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_EXPECTANCY_REVIEW_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_ADDITIONAL_SCENARIOS


def test_pnl_invalid_is_detected():
    simulation = _simulation_result()
    bad_summary = replace(simulation["metric_summary"], total_pnl=-1.0)
    result = evaluate_multi_scenario_result_report_robustness_review(_ready_input(multi_scenario_metric_summary=bad_summary))

    assert MultiScenarioResultReportRisk.MULTI_SCENARIO_PNL_REVIEW_INVALID in result.risks
    assert result.decision is MultiScenarioResultReportDecision.REQUIRE_RISK_REDUCTION


@pytest.mark.parametrize(
    ("risk", "recommendation"),
    [
        (
            MultiScenarioResultReportRisk.MULTI_SCENARIO_SIMULATION_NOT_APPROVED,
            MultiScenarioResultReportRecommendation.APPROVE_MULTI_SCENARIO_SIMULATION_FIRST,
        ),
        (
            MultiScenarioResultReportRisk.MULTI_SCENARIO_STABILITY_WEAK,
            MultiScenarioResultReportRecommendation.IMPROVE_MULTI_SCENARIO_STABILITY,
        ),
        (
            MultiScenarioResultReportRisk.POSITION_INCONSISTENCY_SCENARIO_BEHAVIOR_INVALID,
            MultiScenarioResultReportRecommendation.RECHECK_POSITION_INCONSISTENCY_SCENARIO,
        ),
        (
            MultiScenarioResultReportRisk.STOP_CONDITION_SCENARIO_BEHAVIOR_INVALID,
            MultiScenarioResultReportRecommendation.RECHECK_STOP_CONDITION_SCENARIO,
        ),
        (
            MultiScenarioResultReportRisk.PAPER_BROKER_READ_ONLY_PREPARATION_PREMATURE,
            MultiScenarioResultReportRecommendation.DELAY_PAPER_BROKER_READ_ONLY_PREPARATION,
        ),
    ],
)
def test_recommendation_mapping(risk, recommendation):
    assert recommendation in generate_multi_scenario_result_report_recommendations(
        (risk,),
        MultiScenarioResultReportDecision.REQUIRE_ADDITIONAL_SCENARIOS,
    )


@pytest.mark.parametrize(
    "module_name",
    [
        "multi_scenario_result_report_robustness_review.py",
        "multi_scenario_result_report_robustness_review_models.py",
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
