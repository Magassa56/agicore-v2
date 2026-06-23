from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation import (
    compute_controlled_execution_preparation_score,
    detect_controlled_execution_preparation_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation,
    generate_controlled_execution_preparation_recommendations,
    prepare_controlled_abort_contract,
    prepare_controlled_account_read_only_contract,
    prepare_controlled_audit_contract,
    prepare_controlled_credentials_reference_contract,
    prepare_controlled_execution_precondition_contract,
    prepare_controlled_execution_runtime_contract,
    prepare_controlled_execution_sequence_contract,
    prepare_controlled_go_no_go_contract,
    prepare_controlled_http_websocket_socket_block_guard,
    prepare_controlled_human_approval_contract,
    prepare_controlled_journal_contract,
    prepare_controlled_market_data_read_only_contract,
    prepare_controlled_network_block_guard,
    prepare_controlled_no_secret_read_guard,
    prepare_controlled_observability_contract,
    prepare_controlled_order_blocking_contract,
    prepare_controlled_position_mutation_block_contract,
    prepare_controlled_stop_conditions_contract,
    prepare_controlled_success_failure_contract,
    render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_markdown,
    validate_controlled_execution_safety_gate_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate import (
    _ready_input as _safety_gate_ready_input,
)


def _safety_gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate(
        _safety_gate_ready_input()
    )
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate": _safety_gate_result(),
        "paper_broker_read_only_connection_dry_run_controlled_execution_plan": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_final_safety_gate": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_final_plan": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_preparation_review": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_preparation": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_safety_gate": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_execution_plan": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_preparation_review": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_preparation": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_safety_gate": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_dry_run_plan": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_preparation_review": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_preparation": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_safety_gate": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_connection_plan": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_safety_review": {"state": "READY", "offline_only": True},
        "paper_broker_read_only_preparation": {"state": "READY", "offline_only": True},
        "controlled_execution_safety_gate_approved": True,
        "controlled_runtime_contract_prepared": True,
        "controlled_sequence_contract_prepared": True,
        "controlled_precondition_contract_prepared": True,
        "controlled_credentials_reference_contract_prepared": True,
        "controlled_credentials_reference_only": True,
        "controlled_no_secret_read_guard_prepared": True,
        "controlled_secret_read_guard_enforced": True,
        "controlled_network_block_guard_prepared": True,
        "controlled_network_blocked": True,
        "controlled_http_websocket_socket_block_guard_prepared": True,
        "controlled_http_transport_blocked": True,
        "controlled_websocket_transport_blocked": True,
        "controlled_socket_transport_blocked": True,
        "controlled_external_api_blocked": True,
        "controlled_account_read_only_contract_prepared": True,
        "controlled_account_active_access_blocked": True,
        "controlled_account_mutations_blocked": True,
        "controlled_market_data_read_only_contract_prepared": True,
        "controlled_market_data_live_subscription_blocked": True,
        "controlled_market_data_network_request_blocked": True,
        "controlled_order_blocking_contract_prepared": True,
        "controlled_order_execution_blocked": True,
        "controlled_cancel_replace_blocked": True,
        "controlled_position_mutation_block_contract_prepared": True,
        "controlled_position_mutation_blocked": True,
        "controlled_observability_contract_prepared": True,
        "controlled_journal_contract_prepared": True,
        "controlled_human_approval_contract_prepared": True,
        "controlled_human_approval_required": True,
        "controlled_stop_conditions_contract_prepared": True,
        "controlled_success_failure_contract_prepared": True,
        "controlled_audit_contract_prepared": True,
        "controlled_go_no_go_contract_prepared": True,
        "controlled_abort_contract_prepared": True,
        "paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_requested": False,
        "offline_mode_enforced": True,
        "sandbox_mode_enforced": True,
        "preparation_only": True,
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
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationInput(**payload)


def test_nominal_controlled_execution_preparation_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION
    assert result.preparation_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.controlled_go_no_go_contract.defined is True
    assert result.controlled_abort_contract.defined is True


def test_prepare_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_controlled_execution_safety_gate_approval(data) is True
    assert prepare_controlled_execution_runtime_contract(data).dry_run_execution_disabled is True
    assert prepare_controlled_execution_sequence_contract(data).connection_not_executed is True
    assert prepare_controlled_execution_precondition_contract(data).safety_gate_required is True
    assert prepare_controlled_credentials_reference_contract(data).no_api_key_read is True
    assert prepare_controlled_no_secret_read_guard(data).guard_enforced is True
    assert prepare_controlled_network_block_guard(data).external_api_blocked is True
    assert prepare_controlled_http_websocket_socket_block_guard(data).socket_blocked is True
    assert prepare_controlled_account_read_only_contract(data).active_account_access_blocked is True
    assert prepare_controlled_market_data_read_only_contract(data).network_request_blocked is True
    assert prepare_controlled_order_blocking_contract(data).order_execution_blocked is True
    assert prepare_controlled_position_mutation_block_contract(data).position_mutation_blocked is True
    assert prepare_controlled_observability_contract(data).offline_events_defined is True
    assert prepare_controlled_journal_contract(data).offline_journal_required is True
    assert prepare_controlled_human_approval_contract(data).human_approval_required is True
    assert prepare_controlled_stop_conditions_contract(data).stop_on_network_request is True
    assert prepare_controlled_success_failure_contract(data).failure_on_secret_network_order_position_or_account is True
    assert prepare_controlled_audit_contract(data).offline_evidence_required is True
    assert prepare_controlled_go_no_go_contract(data).human_go_required is True
    assert prepare_controlled_abort_contract(data).abort_on_network_request is True
    assert compute_controlled_execution_preparation_score(data).overall_score == 100


def test_safety_gate_not_approved_blocks_preparation():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate=_safety_gate_result(
                state="CONTROLLED_EXECUTION_SAFETY_GATE_BLOCKED",
                decision="REQUIRE_CONTROLLED_NETWORK_BLOCK_FIXES",
                risks=("CONTROLLED_NETWORK_NOT_BLOCKED",),
            ),
            controlled_execution_safety_gate_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_EXECUTION_SAFETY_GATE_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"controlled_runtime_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_RUNTIME_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_RUNTIME_CONTRACT_FIXES),
        ({"controlled_sequence_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_SEQUENCE_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_FIXES),
        ({"controlled_precondition_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_PRECONDITION_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_PRECONDITION_CONTRACT_FIXES),
        ({"controlled_credentials_reference_only": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_CREDENTIAL_REFERENCE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_FIXES),
        ({"controlled_secret_read_guard_enforced": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_SECRET_READ_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_FIXES),
        ({"controlled_network_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_NETWORK_BLOCK_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES),
        ({"controlled_websocket_transport_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_FIXES),
        ({"controlled_account_active_access_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_FIXES),
        ({"controlled_market_data_network_request_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_FIXES),
        ({"controlled_order_execution_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_ORDER_BLOCKING_FIXES),
        ({"controlled_position_mutation_blocked": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_FIXES),
        ({"controlled_observability_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_OBSERVABILITY_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_OBSERVABILITY_FIXES),
        ({"controlled_journal_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_JOURNAL_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_JOURNAL_FIXES),
        ({"controlled_human_approval_required": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_FIXES),
        ({"controlled_stop_conditions_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_STOP_CONDITION_FIXES),
        ({"controlled_success_failure_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_SUCCESS_FAILURE_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_FIXES),
        ({"controlled_audit_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_AUDIT_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_AUDIT_FIXES),
        ({"controlled_go_no_go_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_GO_NO_GO_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_GO_NO_GO_FIXES),
        ({"controlled_abort_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_ABORT_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.REQUIRE_CONTROLLED_ABORT_FIXES),
    ],
)
def test_required_contract_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState.CONTROLLED_EXECUTION_PREPARATION_BLOCKED


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
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
        {"no_http_transport": False},
        {"no_websocket_transport": False},
        {"no_socket_transport": False},
    ],
)
def test_real_boundary_violations_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(
        _ready_input(data_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION


def test_premature_preparation_review_is_detected():
    risks = detect_controlled_execution_preparation_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW in risks


def test_recommendations_and_markdown_are_rendered():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(data)
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_markdown(result)

    assert generate_controlled_execution_preparation_recommendations(data) == (
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_SUITE,
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW,
    )
    assert "# Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation" in markdown
    assert "Preparation score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_and_missing_gate_are_supported():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(dict(_ready_input().__dict__))
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(None)

    assert nominal.preparation_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationState.CONTROLLED_EXECUTION_PREPARATION_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationRisk.CONTROLLED_EXECUTION_SAFETY_GATE_NOT_APPROVED in missing.risks


def test_source_has_no_real_io_or_network_imports():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_execution_preparation.py"
    ).read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
