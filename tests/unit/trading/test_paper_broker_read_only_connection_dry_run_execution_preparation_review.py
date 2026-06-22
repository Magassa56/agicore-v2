from dataclasses import replace
from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation import (
    evaluate_paper_broker_read_only_connection_dry_run_execution_preparation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation_review import (
    compute_read_only_connection_dry_run_execution_preparation_review_score,
    detect_read_only_connection_dry_run_execution_preparation_review_risks,
    evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review,
    generate_read_only_connection_dry_run_execution_preparation_review_recommendations,
    render_paper_broker_read_only_connection_dry_run_execution_preparation_review_markdown,
    review_dry_run_execution_account_read_only_contract,
    review_dry_run_execution_audit_contract,
    review_dry_run_execution_credentials_reference_contract,
    review_dry_run_execution_human_approval_contract,
    review_dry_run_execution_http_websocket_socket_block_guard,
    review_dry_run_execution_journal_contract,
    review_dry_run_execution_market_data_read_only_contract,
    review_dry_run_execution_network_block_guard,
    review_dry_run_execution_no_secret_read_guard,
    review_dry_run_execution_observability_contract,
    review_dry_run_execution_order_blocking_contract,
    review_dry_run_execution_position_mutation_block_contract,
    review_dry_run_execution_precondition_contract,
    review_dry_run_execution_runtime_contract,
    review_dry_run_execution_sequence_contract,
    review_dry_run_execution_stop_conditions_contract,
    review_dry_run_execution_success_failure_contract,
    validate_dry_run_execution_preparation_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_execution_preparation import (
    _ready_input as _preparation_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(_preparation_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_execution_preparation": _preparation_result(),
        "paper_broker_read_only_connection_dry_run_execution_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE",
        ),
        "paper_broker_read_only_connection_dry_run_execution_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_SAFETY_GATE",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN",
        ),
        "paper_broker_read_only_connection_dry_run_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PLAN"),
        "paper_broker_read_only_connection_dry_run_preparation": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION_REVIEW"),
        "paper_broker_read_only_connection_dry_run_safety_gate": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PREPARATION"),
        "paper_broker_read_only_connection_dry_run_plan": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE"),
        "paper_broker_read_only_connection_preparation_review": _upstream("READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN"),
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
        "dry_run_execution_preparation_approved": True,
        "dry_run_execution_runtime_contract_review_verified": True,
        "dry_run_execution_sequence_contract_review_verified": True,
        "dry_run_execution_precondition_contract_review_verified": True,
        "dry_run_execution_credential_reference_review_verified": True,
        "dry_run_execution_no_secret_read_guard_review_verified": True,
        "dry_run_execution_network_block_guard_review_verified": True,
        "dry_run_execution_http_websocket_socket_block_guard_review_verified": True,
        "dry_run_execution_account_read_only_review_verified": True,
        "dry_run_execution_market_data_read_only_review_verified": True,
        "dry_run_execution_order_blocking_review_verified": True,
        "dry_run_execution_position_mutation_block_review_verified": True,
        "dry_run_execution_observability_review_verified": True,
        "dry_run_execution_journal_review_verified": True,
        "dry_run_execution_human_approval_review_verified": True,
        "dry_run_execution_stop_conditions_review_verified": True,
        "dry_run_execution_success_failure_review_verified": True,
        "dry_run_execution_audit_review_verified": True,
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
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewInput(**payload)


def _with_contract(name, **contract_overrides):
    prep = _preparation_result()
    contract = prep[name]
    prep[name] = replace(contract, **contract_overrides)
    return prep


def test_nominal_execution_preparation_review_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    assert result.review_score == 100
    assert result.risks == ()
    assert result.dry_run_execution_runtime_contract_review.passed is True
    assert result.dry_run_execution_audit_contract_review.passed is True
    assert result.offline_only is True


def test_review_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_execution_preparation_approval(data) is True
    assert review_dry_run_execution_runtime_contract(data).dry_run_execution_disabled is True
    assert review_dry_run_execution_sequence_contract(data).connection_not_executed is True
    assert review_dry_run_execution_precondition_contract(data).fail_closed is True
    assert review_dry_run_execution_credentials_reference_contract(data).no_api_key_read is True
    assert review_dry_run_execution_no_secret_read_guard(data).guard_enforced is True
    assert review_dry_run_execution_network_block_guard(data).external_api_blocked is True
    assert review_dry_run_execution_http_websocket_socket_block_guard(data).socket_blocked is True
    assert review_dry_run_execution_account_read_only_contract(data).active_account_access_blocked is True
    assert review_dry_run_execution_market_data_read_only_contract(data).network_request_blocked is True
    assert review_dry_run_execution_order_blocking_contract(data).order_execution_blocked is True
    assert review_dry_run_execution_position_mutation_block_contract(data).position_mutation_blocked is True
    assert review_dry_run_execution_observability_contract(data).offline_events_defined is True
    assert review_dry_run_execution_journal_contract(data).offline_journal_required is True
    assert review_dry_run_execution_human_approval_contract(data).human_approval_required is True
    assert review_dry_run_execution_stop_conditions_contract(data).stop_on_network_request is True
    assert review_dry_run_execution_success_failure_contract(data).failure_on_secret_network_order_position_or_account is True
    assert review_dry_run_execution_audit_contract(data).offline_evidence_required is True
    assert compute_read_only_connection_dry_run_execution_preparation_review_score(data).overall_score == 100


def test_preparation_not_approved_blocks_review():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_dry_run_execution_preparation=_preparation_result(
                state="DRY_RUN_EXECUTION_PREPARATION_BLOCKED",
                decision="REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_FIXES",
                risks=("DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING",),
            ),
            dry_run_execution_preparation_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_PREPARATION_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"dry_run_execution_runtime_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FIXES),
        ({"dry_run_execution_sequence_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FIXES),
        ({"dry_run_execution_precondition_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FIXES),
        ({"dry_run_execution_credential_reference_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FIXES),
        ({"dry_run_execution_no_secret_read_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        ({"dry_run_execution_network_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"dry_run_execution_http_websocket_socket_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"dry_run_execution_account_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FIXES),
        ({"dry_run_execution_market_data_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FIXES),
        ({"dry_run_execution_order_blocking_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FIXES),
        ({"dry_run_execution_position_mutation_block_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FIXES),
        ({"dry_run_execution_observability_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_REVIEW_FIXES),
        ({"dry_run_execution_journal_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_JOURNAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_REVIEW_FIXES),
        ({"dry_run_execution_human_approval_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FIXES),
        ({"dry_run_execution_stop_conditions_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FIXES),
        ({"dry_run_execution_success_failure_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FIXES),
        ({"dry_run_execution_audit_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_REVIEW_FIXES),
    ],
)
def test_review_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState.DRY_RUN_EXECUTION_PREPARATION_REVIEW_BLOCKED


@pytest.mark.parametrize(
    ("contract_name", "contract_overrides", "risk"),
    [
        ("dry_run_execution_runtime_contract", {"defined": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_REVIEW_FAILED),
        ("dry_run_execution_sequence_contract", {"connection_not_executed": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_REVIEW_FAILED),
        ("dry_run_execution_precondition_contract", {"fail_closed": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PRECONDITION_REVIEW_FAILED),
        ("dry_run_execution_credentials_reference_contract", {"no_api_key_read": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_REVIEW_FAILED),
        ("dry_run_execution_no_secret_read_guard", {"guard_enforced": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_REVIEW_FAILED),
        ("dry_run_execution_network_block_guard", {"network_execution_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_REVIEW_FAILED),
        ("dry_run_execution_http_websocket_socket_block_guard", {"socket_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED),
        ("dry_run_execution_account_read_only_contract", {"active_account_access_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_REVIEW_FAILED),
        ("dry_run_execution_market_data_read_only_contract", {"network_request_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_REVIEW_FAILED),
        ("dry_run_execution_order_blocking_contract", {"order_execution_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_REVIEW_FAILED),
        ("dry_run_execution_position_mutation_block_contract", {"position_mutation_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_REVIEW_FAILED),
        ("dry_run_execution_human_approval_contract", {"human_approval_required": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_REVIEW_FAILED),
        ("dry_run_execution_stop_conditions_contract", {"stop_on_network_request": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_STOP_CONDITION_REVIEW_FAILED),
        ("dry_run_execution_success_failure_contract", {"failure_on_secret_network_order_position_or_account": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_REVIEW_FAILED),
        ("dry_run_execution_audit_contract", {"offline_evidence_required": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED),
    ],
)
def test_invalid_contracts_are_detected(contract_name, contract_overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_preparation=_with_contract(contract_name, **contract_overrides))
    )

    assert risk in result.risks


@pytest.mark.parametrize(
    "overrides",
    [
        {"real_execution_requested": True},
        {"broker_connection_requested": True},
        {"api_key_read_requested": True},
        {"env_var_read_requested": True},
        {"hardcoded_secret_detected": True},
        {"network_transport_requested": True},
        {"external_api_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"no_http_transport": False},
        {"no_websocket_transport": False},
        {"no_socket_transport": False},
    ],
)
def test_real_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW


def test_premature_final_plan_is_detected():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_final_plan_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN in result.risks


def test_recommendations_and_markdown_are_rendered():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_execution_preparation_review_markdown(result)

    assert generate_read_only_connection_dry_run_execution_preparation_review_recommendations(_ready_input()) == (
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW_SUITE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_FINAL_PLAN,
    )
    assert "Paper Broker Read-Only Connection Dry Run Execution Preparation Review" in markdown
    assert "No broker" in markdown
    assert "dry_run_execution_audit_contract" in markdown


def test_mapping_input_and_missing_preparation_input():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation_review(None)

    assert nominal.review_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewState.DRY_RUN_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_PREPARATION_NOT_APPROVED in missing.risks


def test_risk_detection_helper_returns_tuple():
    risks = detect_read_only_connection_dry_run_execution_preparation_review_risks(
        _ready_input(dry_run_execution_audit_review_verified=False)
    )

    assert risks == (PaperBrokerReadOnlyConnectionDryRunExecutionPreparationReviewRisk.DRY_RUN_EXECUTION_AUDIT_REVIEW_FAILED,)


def test_source_has_no_real_io_or_network_imports():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_execution_preparation_review.py").read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
