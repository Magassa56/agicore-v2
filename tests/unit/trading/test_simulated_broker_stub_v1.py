from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.controlled_offline_runner_minimal_models import ControlledOfflineReadOnlyDecision
from agicore.trading.simulated_broker_stub_v1 import (
    apply_simulated_broker_limits_v1,
    assert_simulated_broker_stub_v1_offline_boundaries,
    build_simulated_broker_account_snapshot_v1,
    build_simulated_broker_position_snapshot_v1,
    build_simulated_broker_stub_v1,
    compute_simulated_broker_available_cash_v1,
    compute_simulated_broker_exposure_v1,
    compute_simulated_broker_margin_usage_v1,
    compute_simulated_broker_stub_v1_metrics,
    detect_simulated_broker_stub_v1_risks,
    generate_simulated_broker_journal_entries_v1,
    generate_simulated_broker_stub_v1_recommendations,
    render_simulated_broker_stub_v1_json_report,
    render_simulated_broker_stub_v1_markdown_report,
    simulate_broker_acceptance_preview_v1,
    simulate_broker_read_only_order_preview_v1,
    simulate_broker_rejection_v1,
    validate_simulated_broker_account_snapshot_v1,
    validate_simulated_broker_position_snapshot_v1,
    validate_simulated_broker_stub_v1_input,
)
from agicore.trading.simulated_broker_stub_v1_models import (
    SimulatedBrokerAccountSnapshotV1,
    SimulatedBrokerLimitsV1,
    SimulatedBrokerPositionSnapshotV1,
    SimulatedBrokerStubV1Decision,
    SimulatedBrokerStubV1Input,
    SimulatedBrokerStubV1Recommendation,
    SimulatedBrokerStubV1Risk,
    SimulatedBrokerStubV1State,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/simulated_broker_stub_v1.py"


def _input(**overrides):
    payload = {
        "broker_id": "sim-broker-v1",
        "account_id": "sim-account",
        "symbol": "SIM",
        "action": "BUY",
        "requested_quantity": 5.0,
        "reference_price": 100.0,
        "initial_cash": 100_000.0,
        "initial_equity": 100_000.0,
        "initial_position_quantity": 2.0,
        "average_price": 95.0,
    }
    payload.update(overrides)
    return SimulatedBrokerStubV1Input(**payload)


def test_nominal():
    result = build_simulated_broker_stub_v1(_input())

    assert result.decision is SimulatedBrokerStubV1Decision.APPROVE_SIMULATED_BROKER_STUB_V1
    assert result.state is SimulatedBrokerStubV1State.READY_FOR_RISK_GUARD_ENFORCEMENT_V1
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.order_preview.order_submitted is False
    assert result.order_preview.real_order is False
    assert result.order_preview.position_mutation is False
    assert result.rejection.rejected is True
    assert result.acceptance_preview.accepted is True
    assert result.metrics.real_order_count == 0
    assert result.metrics.real_account_access_count == 0
    assert result.metrics.position_mutation_count == 0
    assert result.report.markdown
    assert result.report.json


def test_input_missing():
    result = build_simulated_broker_stub_v1(None)

    assert validate_simulated_broker_stub_v1_input(None) is False
    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_INPUT_MISSING in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_INPUT_FIXES
    assert result.state is SimulatedBrokerStubV1State.SIMULATED_BROKER_STUB_V1_INPUT_INVALID


def test_account_snapshot_invalid():
    account = SimulatedBrokerAccountSnapshotV1("sim-account", -1.0, 100_000.0, 100_000.0)
    result = build_simulated_broker_stub_v1(_input(account_snapshot=account))

    assert validate_simulated_broker_account_snapshot_v1(account) is False
    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_ACCOUNT_SNAPSHOT_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_ACCOUNT_SNAPSHOT_FIXES


def test_position_snapshot_invalid():
    position = SimulatedBrokerPositionSnapshotV1("SIM", 2.0, 95.0, -100.0, -200.0)
    result = build_simulated_broker_stub_v1(_input(position_snapshot=position))

    assert validate_simulated_broker_position_snapshot_v1(position) is False
    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_POSITION_SNAPSHOT_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_POSITION_SNAPSHOT_FIXES


def test_broker_limits_invalid():
    result = build_simulated_broker_stub_v1(_input(limits=SimulatedBrokerLimitsV1(max_order_notional=0.0)))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_LIMITS_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_LIMITS_FIXES


def test_exposure_invalid():
    result = build_simulated_broker_stub_v1(_input(force_exposure_invalid=True))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_EXPOSURE_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES


def test_cash_available_invalid():
    result = build_simulated_broker_stub_v1(_input(force_available_cash_invalid=True))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_AVAILABLE_CASH_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES


def test_margin_usage_invalid():
    result = build_simulated_broker_stub_v1(_input(force_margin_usage_invalid=True))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_MARGIN_USAGE_INVALID in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_EXPOSURE_FIXES


def test_order_preview_read_only():
    preview = simulate_broker_read_only_order_preview_v1(_input())

    assert preview.read_only is True
    assert preview.order_submitted is False
    assert preview.real_order is False
    assert preview.position_mutation is False
    assert preview.notional == 500.0


def test_rejection_simulated():
    rejection = simulate_broker_rejection_v1()

    assert rejection.rejected is True
    assert rejection.simulated is True
    assert rejection.real_order_submitted is False


def test_acceptance_preview_simulated():
    data = _input()
    account = build_simulated_broker_account_snapshot_v1(data)
    position = build_simulated_broker_position_snapshot_v1(data)
    preview = simulate_broker_read_only_order_preview_v1(data)
    exposure = compute_simulated_broker_exposure_v1(account, position, preview, data)
    acceptance = simulate_broker_acceptance_preview_v1(account, position, preview, SimulatedBrokerLimitsV1(), exposure)

    assert acceptance.accepted is True
    assert acceptance.status == "SIMULATED_ACCEPTANCE_PREVIEW"
    assert acceptance.real_execution is False
    assert acceptance.estimated_position_after == 7.0


def test_journal_generated():
    result = build_simulated_broker_stub_v1(_input())

    assert result.journal_entries
    assert {entry.event_type for entry in result.journal_entries} >= {"account_snapshot", "read_only_order_preview", "exposure"}


def test_metrics_computed():
    result = build_simulated_broker_stub_v1(_input())

    assert result.metrics.preview_count == 1
    assert result.metrics.rejection_count == 1
    assert result.metrics.acceptance_preview_count == 1
    assert result.metrics.gross_exposure == 700.0
    assert result.metrics.available_cash == 99500.0
    assert result.metrics.margin_usage == 0.007


def test_markdown_report():
    result = build_simulated_broker_stub_v1(_input())
    markdown = render_simulated_broker_stub_v1_markdown_report(result)

    assert "Simulated Broker Stub v1" in markdown
    assert "APPROVE_SIMULATED_BROKER_STUB_V1" in markdown
    assert "no real broker" in markdown


def test_json_report():
    result = build_simulated_broker_stub_v1(_input())
    payload = json.loads(render_simulated_broker_stub_v1_json_report(result))

    assert payload["decision"] == "APPROVE_SIMULATED_BROKER_STUB_V1"
    assert payload["score"] == 100
    assert payload["risks"] == []
    assert payload["order_submitted"] is False
    assert payload["real_order_count"] == 0
    assert payload["offline_only"] is True
    assert payload["simulated_only"] is True


def test_no_data_directory_access_is_used():
    result = build_simulated_broker_stub_v1(_input())
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert result.data_accessed is False
    assert result.metrics.data_access_count == 0
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
    result = build_simulated_broker_stub_v1(_input(order_execution_requested=False))

    assert result.order_preview.order_submitted is False
    assert result.real_order_submitted is False
    assert result.metrics.real_order_count == 0


def test_no_real_account_access():
    result = build_simulated_broker_stub_v1(_input(account_access_requested=False))

    assert result.real_account_accessed is False
    assert result.metrics.real_account_access_count == 0


def test_no_real_position_mutation():
    result = build_simulated_broker_stub_v1(_input(position_mutation_requested=False))

    assert result.position_mutated is False
    assert result.metrics.position_mutation_count == 0


def test_journal_missing():
    result = build_simulated_broker_stub_v1(_input(force_journal_missing=True))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_JOURNAL_MISSING in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_JOURNAL_FIXES


def test_metrics_missing():
    result = build_simulated_broker_stub_v1(_input(force_metrics_missing=True))

    assert SimulatedBrokerStubV1Risk.SIMULATED_BROKER_METRICS_MISSING in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.REQUIRE_SIMULATED_BROKER_METRICS_FIXES


@pytest.mark.parametrize(
    ("overrides", "expected"),
    (
        ({"broker_connection_requested": True}, SimulatedBrokerStubV1Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, SimulatedBrokerStubV1Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        ({"network_requested": True}, SimulatedBrokerStubV1Risk.NETWORK_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, SimulatedBrokerStubV1Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, SimulatedBrokerStubV1Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, SimulatedBrokerStubV1Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, SimulatedBrokerStubV1Risk.DATA_ACCESS_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations(overrides, expected):
    result = build_simulated_broker_stub_v1(_input(**overrides))

    assert expected in result.risks
    assert result.decision is SimulatedBrokerStubV1Decision.BLOCK_SIMULATED_BROKER_STUB_V1


def test_recommendations():
    nominal = build_simulated_broker_stub_v1(_input())
    blocked_recs = generate_simulated_broker_stub_v1_recommendations(
        (SimulatedBrokerStubV1Risk.NETWORK_BOUNDARY_VIOLATION,)
    )

    assert SimulatedBrokerStubV1Recommendation.APPROVE_RISK_GUARD_ENFORCEMENT_V1 in nominal.recommendations
    assert SimulatedBrokerStubV1Recommendation.REMOVE_NETWORK_ACCESS in blocked_recs


def test_required_functions_are_callable_and_deterministic():
    data = _input(
        read_only_decision=ControlledOfflineReadOnlyDecision(
            symbol="SIM",
            action="BUY",
            proposed_position_size=5.0,
            reference_price=100.0,
        )
    )
    account = build_simulated_broker_account_snapshot_v1(data)
    position = build_simulated_broker_position_snapshot_v1(data)
    preview = simulate_broker_read_only_order_preview_v1(data)
    rejection = simulate_broker_rejection_v1()
    exposure = compute_simulated_broker_exposure_v1(account, position, preview, data)
    acceptance = simulate_broker_acceptance_preview_v1(account, position, preview, SimulatedBrokerLimitsV1(), exposure)
    journal = generate_simulated_broker_journal_entries_v1(account, position, preview, rejection, acceptance, exposure, data)
    metrics = compute_simulated_broker_stub_v1_metrics(preview, rejection, acceptance, exposure, data)
    risks = detect_simulated_broker_stub_v1_risks(data, account, position, SimulatedBrokerLimitsV1(), preview, exposure, journal, metrics)

    assert assert_simulated_broker_stub_v1_offline_boundaries(data) is True
    assert account == build_simulated_broker_account_snapshot_v1(data)
    assert position == build_simulated_broker_position_snapshot_v1(data)
    assert preview == simulate_broker_read_only_order_preview_v1(data)
    assert compute_simulated_broker_available_cash_v1(account, preview, data) == 99500.0
    assert compute_simulated_broker_margin_usage_v1(account, exposure.gross_exposure, data) == 0.007
    assert apply_simulated_broker_limits_v1(SimulatedBrokerLimitsV1(), exposure, preview) == ()
    assert acceptance.accepted is True
    assert journal
    assert metrics.real_order_count == 0
    assert risks == ()
