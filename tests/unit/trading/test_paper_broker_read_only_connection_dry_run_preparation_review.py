from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_preparation import (
    evaluate_paper_broker_read_only_connection_dry_run_preparation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_preparation_review import (
    compute_read_only_connection_dry_run_preparation_review_score,
    detect_read_only_connection_dry_run_preparation_review_risks,
    evaluate_paper_broker_read_only_connection_dry_run_preparation_review,
    generate_read_only_connection_dry_run_preparation_review_recommendations,
    render_paper_broker_read_only_connection_dry_run_preparation_review_markdown,
    review_dry_run_account_read_only_contract,
    review_dry_run_adapter_boundary,
    review_dry_run_configuration_schema,
    review_dry_run_credentials_reference_contract,
    review_dry_run_execution_contract,
    review_dry_run_http_websocket_socket_block_guard,
    review_dry_run_human_approval_contract,
    review_dry_run_journal_contract,
    review_dry_run_market_data_read_only_contract,
    review_dry_run_network_block_guard,
    review_dry_run_no_secret_read_guard,
    review_dry_run_observability_contract,
    review_dry_run_order_blocking_contract,
    review_dry_run_position_mutation_block_contract,
    review_dry_run_stop_conditions_contract,
    review_dry_run_success_failure_contract,
    validate_dry_run_preparation_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision,
    PaperBrokerReadOnlyConnectionDryRunPreparationReviewInput,
    PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation,
    PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk,
    PaperBrokerReadOnlyConnectionDryRunPreparationReviewState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_preparation import (
    _ready_input as _preparation_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation(_preparation_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_preparation": _preparation_result(),
        "paper_broker_read_only_connection_dry_run_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE",
        ),
        "paper_broker_read_only_connection_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
        ),
        "paper_broker_read_only_connection_preparation_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
        ),
        "paper_broker_read_only_connection_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION"),
        "paper_broker_read_only_connection_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE"),
        "paper_broker_read_only_safety_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN"),
        "paper_broker_read_only_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW"),
        "multi_scenario_result_report": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION"),
        "multi_scenario_controlled_simulation_result": _upstream("READY_FOR_MULTI_SCENARIO_RESULT_REPORT"),
        "performance_risk_validation_gate": _upstream("READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION"),
        "performance_metrics_result": _upstream("READY_FOR_RISK_METRICS_ENGINE"),
        "risk_metrics_result": _upstream("READY_FOR_PERFORMANCE_RISK_VALIDATION_GATE"),
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
        "dry_run_preparation_approved": True,
        "dry_run_execution_contract_review_verified": True,
        "dry_run_adapter_boundary_review_verified": True,
        "dry_run_configuration_schema_review_verified": True,
        "dry_run_credential_reference_review_verified": True,
        "dry_run_no_secret_read_guard_review_verified": True,
        "dry_run_network_block_guard_review_verified": True,
        "dry_run_http_websocket_socket_block_guard_review_verified": True,
        "dry_run_account_read_only_review_verified": True,
        "dry_run_market_data_read_only_review_verified": True,
        "dry_run_order_blocking_review_verified": True,
        "dry_run_position_mutation_block_review_verified": True,
        "dry_run_observability_review_verified": True,
        "dry_run_journal_review_verified": True,
        "dry_run_human_approval_review_verified": True,
        "dry_run_stop_conditions_review_verified": True,
        "dry_run_success_failure_review_verified": True,
        "paper_broker_read_only_connection_dry_run_execution_plan_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "review_only": True,
        "broker_connection_disabled": True,
        "no_real_broker": True,
        "no_alpaca_real": True,
        "no_api_key_read": True,
        "no_env_var_read": True,
        "no_hardcoded_secrets": True,
        "no_http_transport": True,
        "no_websocket_transport": True,
        "no_socket_transport": True,
        "no_external_api": True,
        "no_external_ml": True,
        "no_external_llm": True,
        "no_live_execution": True,
        "no_real_order": True,
        "no_position_mutation": True,
        "no_real_account_access": True,
        "data_access_requested": False,
        "real_execution_requested": False,
        "broker_connection_requested": False,
        "api_key_read_requested": False,
        "env_var_read_requested": False,
        "hardcoded_secret_detected": False,
        "order_execution_requested": False,
        "position_mutation_requested": False,
        "account_access_requested": False,
        "network_transport_requested": False,
        "external_api_requested": False,
        "dry_run_requested": False,
        "dry_run_executed": False,
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunPreparationReviewInput(**payload)


def test_nominal_dry_run_preparation_review_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW
    assert result.review_score == 100
    assert result.risks == ()
    assert result.dry_run_execution_contract_review.passed is True
    assert result.dry_run_success_failure_contract_review.passed is True
    assert result.offline_only is True


def test_review_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_preparation_approval(data) is True
    assert review_dry_run_execution_contract(data).passed is True
    assert review_dry_run_adapter_boundary(data).network_transport_blocked is True
    assert review_dry_run_configuration_schema(data).env_var_read_blocked is True
    assert review_dry_run_credentials_reference_contract(data).reference_only is True
    assert review_dry_run_no_secret_read_guard(data).no_api_key_read is True
    assert review_dry_run_network_block_guard(data).external_api_blocked is True
    assert review_dry_run_http_websocket_socket_block_guard(data).socket_blocked is True
    assert review_dry_run_account_read_only_contract(data).active_account_access_blocked is True
    assert review_dry_run_market_data_read_only_contract(data).network_request_blocked is True
    assert review_dry_run_order_blocking_contract(data).order_execution_blocked is True
    assert review_dry_run_position_mutation_block_contract(data).position_mutation_blocked is True
    assert review_dry_run_observability_contract(data).offline_events_defined is True
    assert review_dry_run_journal_contract(data).offline_journal_required is True
    assert review_dry_run_human_approval_contract(data).human_approval_required is True
    assert review_dry_run_stop_conditions_contract(data).stop_on_network_request is True
    assert review_dry_run_success_failure_contract(data).failure_on_secret_network_order_position_or_account is True
    assert compute_read_only_connection_dry_run_preparation_review_score(data).overall_score == 100


def test_preparation_not_approved_blocks_review():
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_dry_run_preparation=_preparation_result(
                state="DRY_RUN_PREPARATION_BLOCKED",
                decision="REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            dry_run_preparation_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_PREPARATION_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"dry_run_execution_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_EXECUTION_CONTRACT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_CONTRACT_REVIEW_FIXES),
        ({"dry_run_adapter_boundary_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FIXES),
        ({"dry_run_configuration_schema_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_CONFIGURATION_SCHEMA_REVIEW_FIXES),
        ({"dry_run_credential_reference_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_CREDENTIAL_REFERENCE_REVIEW_FIXES),
        ({"dry_run_no_secret_read_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_SECRET_READ_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        ({"dry_run_network_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"dry_run_http_websocket_socket_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"dry_run_account_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_ACCOUNT_READ_ONLY_REVIEW_FIXES),
        ({"dry_run_market_data_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_MARKET_DATA_READ_ONLY_REVIEW_FIXES),
        ({"dry_run_order_blocking_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_ORDER_BLOCKING_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_ORDER_BLOCKING_REVIEW_FIXES),
        ({"dry_run_position_mutation_block_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_POSITION_MUTATION_BLOCK_REVIEW_FIXES),
        ({"dry_run_observability_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_OBSERVABILITY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_OBSERVABILITY_REVIEW_FIXES),
        ({"dry_run_journal_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_JOURNAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_JOURNAL_REVIEW_FIXES),
        ({"dry_run_human_approval_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_HUMAN_APPROVAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_HUMAN_APPROVAL_REVIEW_FIXES),
        ({"dry_run_stop_conditions_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_STOP_CONDITIONS_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_STOP_CONDITION_REVIEW_FIXES),
        ({"dry_run_success_failure_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_SUCCESS_FAILURE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_SUCCESS_FAILURE_REVIEW_FIXES),
    ],
)
def test_review_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunPreparationReviewState.DRY_RUN_PREPARATION_REVIEW_BLOCKED


@pytest.mark.parametrize(
    ("overrides", "risk"),
    [
        ({"real_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"env_var_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"hardcoded_secret_detected": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"network_transport_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"dry_run_executed": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DATA_ACCESS_VIOLATION),
    ],
)
def test_boundary_violations_are_detected(overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunPreparationReviewDecision.REQUIRE_DRY_RUN_ADAPTER_BOUNDARY_REVIEW_FIXES


def test_premature_execution_plan_is_detected():
    risks = detect_read_only_connection_dry_run_preparation_review_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_plan_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN in risks


def test_recommendations_map_risks_to_actions():
    recommendations = generate_read_only_connection_dry_run_preparation_review_recommendations(
        _ready_input(dry_run_network_block_guard_review_verified=False)
    )

    assert PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN in recommendations
    assert PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation.FIX_DRY_RUN_NETWORK_BLOCK_GUARD_REVIEW in recommendations


def test_nominal_recommendations_approve_execution_plan():
    recommendations = generate_read_only_connection_dry_run_preparation_review_recommendations(_ready_input())

    assert recommendations == (
        PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW_SUITE,
        PaperBrokerReadOnlyConnectionDryRunPreparationReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN,
    )


def test_markdown_render_includes_decision_score_and_boundaries():
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_preparation_review_markdown(result)

    assert "# Paper Broker Read-Only Connection Dry Run Preparation Review" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW" in markdown
    assert "Review score: 100" in markdown
    assert "No HTTP, websocket, socket, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_is_supported():
    data = dict(_ready_input().__dict__)
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(data)

    assert result.review_score == 100
    assert result.risks == ()


def test_input_without_preparation_is_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_preparation_review(
        _ready_input(paper_broker_read_only_connection_dry_run_preparation=None)
    )

    assert result.state is PaperBrokerReadOnlyConnectionDryRunPreparationReviewState.DRY_RUN_PREPARATION_REVIEW_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunPreparationReviewRisk.DRY_RUN_PREPARATION_NOT_APPROVED in result.risks


def test_source_does_not_open_runtime_transports_or_data_access():
    source_path = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_preparation_review.py")
    source = source_path.read_text(encoding="utf-8")

    assert "import requests" not in source
    assert "import socket" not in source
    assert "websocket" in source
    assert "os.environ" not in source
    assert "Path('data" not in source
    assert 'Path("data' not in source
