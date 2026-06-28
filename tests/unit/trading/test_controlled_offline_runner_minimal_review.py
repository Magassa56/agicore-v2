from __future__ import annotations

from dataclasses import replace

import pytest

import agicore.trading.controlled_offline_runner_minimal_review as review
from agicore.trading.controlled_offline_runner_minimal import run_controlled_offline_runner_minimal
from agicore.trading.controlled_offline_runner_minimal_models import (
    ControlledOfflineReadOnlyDecision,
    ControlledOfflineRiskGuardResult,
    ControlledOfflineRunnerMetrics,
    ControlledOfflineRunnerMinimalInput,
    ControlledOfflineRunnerReport,
    ControlledOfflineSimulatedAccountSnapshot,
    ControlledOfflineSimulatedBrokerSnapshot,
    ControlledOfflineStrategySignal,
    ControlledOfflineSyntheticMarketBar,
    ControlledOfflineSyntheticMarketScenario,
)
from agicore.trading.controlled_offline_runner_minimal_review_models import (
    ControlledOfflineRunnerMinimalReviewDecision as Decision,
    ControlledOfflineRunnerMinimalReviewInput,
    ControlledOfflineRunnerMinimalReviewRecommendation as Recommendation,
    ControlledOfflineRunnerMinimalReviewRisk as Risk,
    ControlledOfflineRunnerMinimalReviewState as State,
)


def _bars():
    return (
        ControlledOfflineSyntheticMarketBar(0, "SIM", 100.0, 101.0, 99.0, 100.0, 1000.0, "T0"),
        ControlledOfflineSyntheticMarketBar(1, "SIM", 100.0, 103.0, 99.0, 102.0, 1000.0, "T1"),
        ControlledOfflineSyntheticMarketBar(2, "SIM", 102.0, 106.0, 101.0, 105.0, 1000.0, "T2"),
    )


def _minimal_input(**overrides):
    payload = {"scenario_id": "nominal", "symbol": "SIM", "synthetic_market_bars": _bars()}
    payload.update(overrides)
    return ControlledOfflineRunnerMinimalInput(**payload)


def _minimal_result(**input_overrides):
    return run_controlled_offline_runner_minimal(_minimal_input(**input_overrides))


def _review_input(result=None, minimal_input=None, **overrides):
    payload = {
        "minimal_result": result if result is not None else _minimal_result(),
        "minimal_input": minimal_input if minimal_input is not None else _minimal_input(),
        "controlled_offline_runner_minimal_approved": True,
    }
    payload.update(overrides)
    return ControlledOfflineRunnerMinimalReviewInput(**payload)


def test_nominal_review():
    result = review.review_controlled_offline_runner_minimal(_review_input())

    assert result.decision is Decision.APPROVE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW
    assert result.state is State.READY_FOR_SYNTHETIC_MARKET_SCENARIO_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert Recommendation.APPROVE_SYNTHETIC_MARKET_SCENARIO_V1 in result.recommendations


def test_minimal_result_not_approved():
    result = review.review_controlled_offline_runner_minimal(
        _review_input(run_controlled_offline_runner_minimal(None), None, controlled_offline_runner_minimal_approved=False)
    )

    assert Risk.CONTROLLED_OFFLINE_RUNNER_MINIMAL_NOT_APPROVED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_MINIMAL_FIXES
    assert result.state is State.CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_INPUT_INVALID


def test_non_determinism_detected(monkeypatch):
    calls = {"count": 0}
    base = _minimal_result()

    def drifting_runner(_data):
        calls["count"] += 1
        report = ControlledOfflineRunnerReport(markdown=base.report.markdown, json=f"{base.report.json}:{calls['count']}")
        return replace(base, report=report)

    monkeypatch.setattr(review, "run_controlled_offline_runner_minimal", drifting_runner)
    result = review.review_controlled_offline_runner_minimal(_review_input(base, _minimal_input()))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_NOT_DETERMINISTIC in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_DETERMINISM_FIXES


def test_market_scenario_review_failed():
    bad = replace(_minimal_result(), scenario=ControlledOfflineSyntheticMarketScenario("bad", "SIM", ()))
    result = review.review_controlled_offline_runner_minimal(_review_input(bad))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_MARKET_SCENARIO_FIXES


def test_account_snapshot_review_failed():
    bad = replace(_minimal_result(), account_snapshot=ControlledOfflineSimulatedAccountSnapshot("A", -1.0, 100.0))
    result = review.review_controlled_offline_runner_minimal(_review_input(bad))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_ACCOUNT_SNAPSHOT_FIXES


def test_broker_snapshot_review_failed():
    broker = ControlledOfflineSimulatedBrokerSnapshot("B", connected=True, simulated=False, read_only=False, orders_supported=True, real_broker=True)
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), broker_snapshot=broker)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_BROKER_SNAPSHOT_FIXES


def test_strategy_signal_review_failed():
    signal = ControlledOfflineStrategySignal("SIM", "EXECUTE", 1.5, "bad", observation_only=False)
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), strategy_signal=signal)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_STRATEGY_SIGNAL_FIXES


def test_risk_guard_review_failed():
    guard = ControlledOfflineRiskGuardResult(False, 10.0, 1.0, (), ("bad",))
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), risk_guard=guard)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_RISK_GUARD_FIXES


def test_read_only_decision_review_failed():
    decision = ControlledOfflineReadOnlyDecision("SIM", "BUY", 1.0, 100.0, order_submitted=True, position_mutated=True, read_only=False)
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), read_only_decision=decision)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_READ_ONLY_DECISION_FIXES


def test_journal_review_failed():
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), journal_entries=())))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_JOURNAL_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_JOURNAL_FIXES


def test_metrics_review_failed():
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), metrics=None)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_METRICS_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_METRICS_FIXES


def test_report_review_failed():
    bad_report = ControlledOfflineRunnerReport(markdown="", json="{}")
    result = review.review_controlled_offline_runner_minimal(_review_input(replace(_minimal_result(), report=bad_report)))

    assert Risk.CONTROLLED_OFFLINE_RUNNER_REPORT_REVIEW_FAILED in result.risks
    assert result.decision is Decision.REQUIRE_CONTROLLED_OFFLINE_RUNNER_REPORT_FIXES


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"broker_connection_requested": True}, Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ({"network_requested": True}, Risk.NETWORK_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, Risk.DATA_ACCESS_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(overrides, expected):
    minimal_input = _minimal_input(**overrides)
    result = review.review_controlled_offline_runner_minimal(
        _review_input(run_controlled_offline_runner_minimal(minimal_input), minimal_input)
    )

    assert expected in result.risks
    assert result.decision is Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW


def test_premature_synthetic_market_scenario_v1_blocks():
    result = review.review_controlled_offline_runner_minimal(
        _review_input(synthetic_market_scenario_v1_requested=True)
    )

    assert Risk.PREMATURE_SYNTHETIC_MARKET_SCENARIO_V1 in result.risks
    assert Recommendation.DELAY_SYNTHETIC_MARKET_SCENARIO_V1 in result.recommendations
    assert result.decision is Decision.BLOCK_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW


def test_recommendations_and_markdown():
    result = review.review_controlled_offline_runner_minimal(_review_input())
    markdown = review.render_controlled_offline_runner_minimal_review_markdown(result)

    assert Recommendation.RUN_CONTROLLED_OFFLINE_RUNNER_MINIMAL_REVIEW_TEST_SUITE in result.recommendations
    assert "Controlled Offline Runner Minimal Review" in markdown
    assert "READY_FOR_SYNTHETIC_MARKET_SCENARIO_V1" in markdown
    assert "no broker" in markdown


def test_required_functions_are_callable():
    data = _review_input()
    result = data.minimal_result

    assert review.validate_controlled_offline_runner_minimal_result_for_review(data) is True
    assert review.review_controlled_offline_runner_determinism(data).passed is True
    assert review.review_controlled_offline_runner_market_scenario(result).passed is True
    assert review.review_controlled_offline_runner_account_snapshot(result).passed is True
    assert review.review_controlled_offline_runner_broker_snapshot(result).passed is True
    assert review.review_controlled_offline_runner_strategy_signal(result).passed is True
    assert review.review_controlled_offline_runner_risk_guards(result).passed is True
    assert review.review_controlled_offline_runner_read_only_decision(result).passed is True
    assert review.review_controlled_offline_runner_journal(result).passed is True
    assert review.review_controlled_offline_runner_metrics(result).passed is True
    assert review.review_controlled_offline_runner_markdown_report(result).passed is True
    assert review.review_controlled_offline_runner_json_report(result).passed is True
    assert review.review_controlled_offline_runner_no_real_execution_boundaries(data).passed is True
    assert review.compute_controlled_offline_runner_minimal_review_score(data).overall_score == 100
    assert review.detect_controlled_offline_runner_minimal_review_risks(data) == ()
