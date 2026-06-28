from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.risk_guard_enforcement_v1 import (
    aggregate_risk_guard_evaluations_v1,
    assert_risk_guard_enforcement_v1_offline_boundaries,
    build_risk_guard_context_v1,
    build_risk_guard_limits_v1,
    compute_risk_guard_enforcement_v1_score,
    detect_risk_guard_enforcement_v1_risks,
    enforce_account_snapshot_guard_v1,
    enforce_available_cash_guard_v1,
    enforce_daily_loss_guard_v1,
    enforce_margin_usage_guard_v1,
    enforce_max_drawdown_guard_v1,
    enforce_max_notional_exposure_guard_v1,
    enforce_max_position_size_guard_v1,
    enforce_no_real_execution_guard_v1,
    enforce_position_snapshot_guard_v1,
    enforce_read_only_order_preview_guard_v1,
    enforce_risk_guard_v1,
    enforce_symbol_allowlist_guard_v1,
    enforce_synthetic_market_scenario_guard_v1,
    generate_risk_guard_enforcement_v1_recommendations,
    render_risk_guard_enforcement_v1_json_report,
    render_risk_guard_enforcement_v1_markdown_report,
    validate_risk_guard_enforcement_v1_input,
)
from agicore.trading.risk_guard_enforcement_v1_models import (
    RiskGuardEnforcementV1Decision,
    RiskGuardEnforcementV1Input,
    RiskGuardEnforcementV1Recommendation,
    RiskGuardEnforcementV1Risk,
    RiskGuardEnforcementV1State,
    RiskGuardLimitsV1,
)
from agicore.trading.simulated_broker_stub_v1_models import (
    SimulatedBrokerAccountSnapshotV1,
    SimulatedBrokerPositionSnapshotV1,
    SimulatedBrokerReadOnlyOrderPreviewV1,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/risk_guard_enforcement_v1.py"


def _input(**overrides):
    payload = {
        "symbol": "SIM",
        "requested_quantity": 5.0,
        "reference_price": 100.0,
        "available_cash": 99_500.0,
        "margin_usage": 0.01,
        "daily_loss": 0.0,
        "drawdown": 0.0,
    }
    payload.update(overrides)
    return RiskGuardEnforcementV1Input(**payload)


def test_nominal_all_guards_ok():
    result = enforce_risk_guard_v1(_input())

    assert result.decision is RiskGuardEnforcementV1Decision.APPROVE_RISK_GUARD_ENFORCEMENT_V1
    assert result.state is RiskGuardEnforcementV1State.READY_FOR_JOURNAL_WRITER_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.summary.all_passed is True
    assert result.summary.evaluation_count == 12
    assert result.summary.violation_count == 0
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = enforce_risk_guard_v1(None)

    assert validate_risk_guard_enforcement_v1_input(None) is False
    assert RiskGuardEnforcementV1Risk.RISK_GUARD_INPUT_MISSING in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_INPUT_FIXES
    assert result.state is RiskGuardEnforcementV1State.RISK_GUARD_ENFORCEMENT_V1_INPUT_INVALID


def test_limits_invalid():
    result = enforce_risk_guard_v1(_input(limits=RiskGuardLimitsV1(max_position_size=-1.0)))

    assert RiskGuardEnforcementV1Risk.RISK_GUARD_LIMITS_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_LIMITS_FIXES


def test_context_invalid():
    result = enforce_risk_guard_v1(_input(force_context_invalid=True))

    assert RiskGuardEnforcementV1Risk.RISK_GUARD_CONTEXT_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES


def test_max_position_size_exceeded():
    result = enforce_risk_guard_v1(_input(requested_quantity=11.0))

    assert RiskGuardEnforcementV1Risk.MAX_POSITION_SIZE_EXCEEDED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_MAX_POSITION_SIZE_FIXES


def test_max_notional_exposure_exceeded():
    result = enforce_risk_guard_v1(_input(limits=RiskGuardLimitsV1(max_notional_exposure=400.0)))

    assert RiskGuardEnforcementV1Risk.MAX_NOTIONAL_EXPOSURE_EXCEEDED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_MAX_NOTIONAL_EXPOSURE_FIXES


def test_cash_insufficient():
    result = enforce_risk_guard_v1(_input(available_cash=100.0))

    assert RiskGuardEnforcementV1Risk.AVAILABLE_CASH_INSUFFICIENT in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_AVAILABLE_CASH_FIXES


def test_margin_usage_exceeded():
    result = enforce_risk_guard_v1(_input(margin_usage=0.8))

    assert RiskGuardEnforcementV1Risk.MARGIN_USAGE_EXCEEDED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_MARGIN_USAGE_FIXES


def test_daily_loss_exceeded():
    result = enforce_risk_guard_v1(_input(daily_loss=1001.0))

    assert RiskGuardEnforcementV1Risk.DAILY_LOSS_LIMIT_EXCEEDED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_DAILY_LOSS_FIXES


def test_drawdown_exceeded():
    result = enforce_risk_guard_v1(_input(drawdown=0.2))

    assert RiskGuardEnforcementV1Risk.MAX_DRAWDOWN_EXCEEDED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_DRAWDOWN_FIXES


def test_symbol_not_allowed():
    result = enforce_risk_guard_v1(_input(symbol="OTHER"))

    assert RiskGuardEnforcementV1Risk.SYMBOL_NOT_ALLOWED in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_SYMBOL_ALLOWLIST_FIXES


def test_order_preview_non_read_only():
    preview = SimulatedBrokerReadOnlyOrderPreviewV1("SIM", "BUY", 5.0, 100.0, 500.0, read_only=False)
    result = enforce_risk_guard_v1(_input(order_preview=preview))

    assert RiskGuardEnforcementV1Risk.READ_ONLY_ORDER_PREVIEW_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_READ_ONLY_ORDER_PREVIEW_FIXES


def test_account_snapshot_invalid():
    account = SimulatedBrokerAccountSnapshotV1("SIM-ACCOUNT", -1.0, 100_000.0, 100_000.0)
    result = enforce_risk_guard_v1(_input(account_snapshot=account))

    assert RiskGuardEnforcementV1Risk.ACCOUNT_SNAPSHOT_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES


def test_position_snapshot_invalid():
    position = SimulatedBrokerPositionSnapshotV1("OTHER", 5.0, 100.0, 100.0, 500.0)
    result = enforce_risk_guard_v1(_input(position_snapshot=position))

    assert RiskGuardEnforcementV1Risk.POSITION_SNAPSHOT_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES


def test_synthetic_market_scenario_invalid():
    result = enforce_risk_guard_v1(_input(synthetic_market_scenario="invalid"))

    assert RiskGuardEnforcementV1Risk.SYNTHETIC_MARKET_SCENARIO_INVALID in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.REQUIRE_RISK_GUARD_CONTEXT_FIXES


def test_aggregation_of_evaluations():
    context = build_risk_guard_context_v1(_input(requested_quantity=11.0, available_cash=100.0))
    limits = build_risk_guard_limits_v1(_input())
    evaluations = (
        enforce_max_position_size_guard_v1(context, limits),
        enforce_available_cash_guard_v1(context, limits),
        enforce_symbol_allowlist_guard_v1(context, limits),
    )
    summary = aggregate_risk_guard_evaluations_v1(evaluations)

    assert summary.evaluation_count == 3
    assert summary.passed_count == 1
    assert summary.violation_count == 2
    assert summary.blocking_violation_count == 2
    assert summary.all_passed is False


def test_score_calculated():
    result = enforce_risk_guard_v1(_input())
    score = compute_risk_guard_enforcement_v1_score(result.context and _input(), result.limits, result.context, result.summary, result.risks)

    assert score.overall_score == 100
    assert score.guard_score == 100
    assert score.boundary_score == 100


def test_recommendations_generated():
    nominal = enforce_risk_guard_v1(_input())
    recs = generate_risk_guard_enforcement_v1_recommendations(
        (RiskGuardEnforcementV1Risk.MAX_POSITION_SIZE_EXCEEDED,)
    )

    assert RiskGuardEnforcementV1Recommendation.APPROVE_JOURNAL_WRITER_V1 in nominal.recommendations
    assert RiskGuardEnforcementV1Recommendation.REDUCE_POSITION_SIZE in recs


def test_markdown_report():
    result = enforce_risk_guard_v1(_input())
    markdown = render_risk_guard_enforcement_v1_markdown_report(result)

    assert "Risk Guard Enforcement v1" in markdown
    assert "APPROVE_RISK_GUARD_ENFORCEMENT_V1" in markdown
    assert "no broker" in markdown


def test_json_report():
    result = enforce_risk_guard_v1(_input())
    payload = json.loads(render_risk_guard_enforcement_v1_json_report(result))

    assert payload["decision"] == "APPROVE_RISK_GUARD_ENFORCEMENT_V1"
    assert payload["score"] == 100
    assert payload["risks"] == []
    assert payload["evaluation_count"] == 12
    assert payload["offline_only"] is True
    assert payload["simulated_only"] is True


def test_no_data_directory_access_is_used():
    result = enforce_risk_guard_v1(_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.data_accessed is False
    assert "data/" not in source
    assert "open(" not in source
    assert "read_text" not in source


def test_no_network_socket_http_websocket_access_is_used():
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

    assert imported_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})
    assert imported_from_modules.isdisjoint({"requests", "httpx", "urllib", "socket", "websocket"})


def test_no_real_key_or_env_var_is_read():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "environ" not in source
    assert "getenv" not in source
    assert "dotenv" not in source
    assert "API_KEY" not in source


def test_no_real_order_is_produced():
    result = enforce_risk_guard_v1(_input(order_execution_requested=False))

    assert result.real_order_submitted is False
    assert all(getattr(item.context.order_preview, "order_submitted", False) is False for item in (result,))


def test_no_real_account_access():
    result = enforce_risk_guard_v1(_input(account_access_requested=False))

    assert result.real_account_accessed is False


def test_no_real_position_mutation():
    result = enforce_risk_guard_v1(_input(position_mutation_requested=False))

    assert result.position_mutated is False


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"broker_connection_requested": True}, RiskGuardEnforcementV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, RiskGuardEnforcementV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ({"network_requested": True}, RiskGuardEnforcementV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, RiskGuardEnforcementV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, RiskGuardEnforcementV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, RiskGuardEnforcementV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, RiskGuardEnforcementV1Risk.DATA_ACCESS_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(overrides, expected):
    result = enforce_risk_guard_v1(_input(**overrides))

    assert expected in result.risks
    assert result.decision is RiskGuardEnforcementV1Decision.BLOCK_RISK_GUARD_ENFORCEMENT_V1


def test_required_functions_are_callable_and_deterministic():
    data = _input()
    limits = build_risk_guard_limits_v1(data)
    context = build_risk_guard_context_v1(data)
    evaluations = (
        enforce_max_position_size_guard_v1(context, limits),
        enforce_max_notional_exposure_guard_v1(context, limits),
        enforce_available_cash_guard_v1(context, limits),
        enforce_margin_usage_guard_v1(context, limits),
        enforce_max_drawdown_guard_v1(context, limits),
        enforce_daily_loss_guard_v1(context, limits),
        enforce_symbol_allowlist_guard_v1(context, limits),
        enforce_read_only_order_preview_guard_v1(context),
        enforce_no_real_execution_guard_v1(data),
        enforce_account_snapshot_guard_v1(context),
        enforce_position_snapshot_guard_v1(context),
        enforce_synthetic_market_scenario_guard_v1(context),
    )
    summary = aggregate_risk_guard_evaluations_v1(evaluations)
    risks = detect_risk_guard_enforcement_v1_risks(data, limits, context, evaluations)

    assert validate_risk_guard_enforcement_v1_input(data) is True
    assert assert_risk_guard_enforcement_v1_offline_boundaries(data) is True
    assert limits == build_risk_guard_limits_v1(data)
    assert context == build_risk_guard_context_v1(data)
    assert all(item.passed for item in evaluations)
    assert summary.all_passed is True
    assert risks == ()
