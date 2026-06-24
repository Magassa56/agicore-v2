from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review import (
    compute_controlled_execution_preparation_review_score,
    detect_controlled_execution_preparation_review_risks,
    evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review,
    generate_controlled_execution_preparation_review_recommendations,
    render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_markdown,
    review_controlled_abort_contract,
    review_controlled_account_read_only_contract,
    review_controlled_audit_contract,
    review_controlled_credentials_reference_contract,
    review_controlled_execution_precondition_contract,
    review_controlled_execution_runtime_contract,
    review_controlled_execution_sequence_contract,
    review_controlled_go_no_go_contract,
    review_controlled_http_websocket_socket_block_guard,
    review_controlled_human_approval_contract,
    review_controlled_journal_contract,
    review_controlled_market_data_read_only_contract,
    review_controlled_network_block_guard,
    review_controlled_no_secret_read_guard,
    review_controlled_observability_contract,
    review_controlled_order_blocking_contract,
    review_controlled_position_mutation_block_contract,
    review_controlled_stop_conditions_contract,
    review_controlled_success_failure_contract,
    validate_controlled_execution_preparation_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk,
    PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_execution_preparation import (
    _ready_input as _preparation_ready_input,
)


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation(
        _preparation_ready_input()
    )
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_controlled_execution_preparation": _preparation_result(),
        "paper_broker_read_only_connection_dry_run_controlled_execution_safety_gate": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_controlled_execution_plan": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_final_safety_gate": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_final_plan": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_preparation_review": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_preparation": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_safety_gate": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_execution_plan": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_preparation_review": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_preparation": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_safety_gate": _upstream("READY"),
        "paper_broker_read_only_connection_dry_run_plan": _upstream("READY"),
        "paper_broker_read_only_connection_preparation_review": _upstream("READY"),
        "paper_broker_read_only_connection_preparation": _upstream("READY"),
        "paper_broker_read_only_connection_safety_gate": _upstream("READY"),
        "paper_broker_read_only_connection_plan": _upstream("READY"),
        "paper_broker_read_only_safety_review": _upstream("READY"),
        "paper_broker_read_only_preparation": _upstream("READY"),
        "controlled_execution_preparation_approved": True,
        "controlled_runtime_contract_review_verified": True,
        "controlled_sequence_contract_review_verified": True,
        "controlled_precondition_contract_review_verified": True,
        "controlled_credential_reference_review_verified": True,
        "controlled_no_secret_read_guard_review_verified": True,
        "controlled_network_block_guard_review_verified": True,
        "controlled_http_websocket_socket_block_guard_review_verified": True,
        "controlled_account_read_only_review_verified": True,
        "controlled_market_data_read_only_review_verified": True,
        "controlled_order_blocking_review_verified": True,
        "controlled_position_mutation_block_review_verified": True,
        "controlled_observability_review_verified": True,
        "controlled_journal_review_verified": True,
        "controlled_human_approval_review_verified": True,
        "controlled_stop_conditions_review_verified": True,
        "controlled_success_failure_review_verified": True,
        "controlled_audit_review_verified": True,
        "controlled_go_no_go_review_verified": True,
        "controlled_abort_review_verified": True,
        "paper_broker_read_only_connection_dry_run_controlled_execution_final_plan_requested": False,
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
    return PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewInput(**payload)


def test_nominal_controlled_execution_preparation_review_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW
    assert result.review_score == 100
    assert result.risks == ()
    assert result.controlled_go_no_go_review.passed is True
    assert result.controlled_abort_review.passed is True
    assert result.offline_only is True


def test_review_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_controlled_execution_preparation_approval(data) is True
    assert review_controlled_execution_runtime_contract(data).dry_run_execution_disabled is True
    assert review_controlled_execution_sequence_contract(data).connection_not_executed is True
    assert review_controlled_execution_precondition_contract(data).fail_closed is True
    assert review_controlled_credentials_reference_contract(data).no_api_key_read is True
    assert review_controlled_no_secret_read_guard(data).guard_enforced is True
    assert review_controlled_network_block_guard(data).external_api_blocked is True
    assert review_controlled_http_websocket_socket_block_guard(data).socket_blocked is True
    assert review_controlled_account_read_only_contract(data).active_account_access_blocked is True
    assert review_controlled_market_data_read_only_contract(data).network_request_blocked is True
    assert review_controlled_order_blocking_contract(data).order_execution_blocked is True
    assert review_controlled_position_mutation_block_contract(data).position_mutation_blocked is True
    assert review_controlled_observability_contract(data).offline_events_defined is True
    assert review_controlled_journal_contract(data).offline_journal_required is True
    assert review_controlled_human_approval_contract(data).human_approval_required is True
    assert review_controlled_stop_conditions_contract(data).stop_on_network_request is True
    assert review_controlled_success_failure_contract(data).failure_on_secret_network_order_position_or_account is True
    assert review_controlled_audit_contract(data).offline_evidence_required is True
    assert review_controlled_go_no_go_contract(data).human_go_required is True
    assert review_controlled_abort_contract(data).abort_on_network_request is True
    assert compute_controlled_execution_preparation_review_score(data).overall_score == 100


def test_preparation_not_approved_blocks_review():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_execution_preparation=_preparation_result(
                state="CONTROLLED_EXECUTION_PREPARATION_BLOCKED",
                decision="REQUIRE_CONTROLLED_RUNTIME_CONTRACT_FIXES",
                risks=("CONTROLLED_RUNTIME_CONTRACT_MISSING",),
            ),
            controlled_execution_preparation_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_EXECUTION_PREPARATION_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"controlled_runtime_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_RUNTIME_CONTRACT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_RUNTIME_CONTRACT_REVIEW_FIXES),
        ({"controlled_sequence_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_SEQUENCE_CONTRACT_REVIEW_FIXES),
        ({"controlled_precondition_contract_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_PRECONDITION_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_PRECONDITION_REVIEW_FIXES),
        ({"controlled_credential_reference_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_CREDENTIAL_REFERENCE_REVIEW_FIXES),
        ({"controlled_no_secret_read_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_SECRET_READ_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_NO_SECRET_READ_GUARD_REVIEW_FIXES),
        ({"controlled_network_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"controlled_http_websocket_socket_block_guard_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_NETWORK_BLOCK_GUARD_REVIEW_FIXES),
        ({"controlled_account_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_ACCOUNT_READ_ONLY_REVIEW_FIXES),
        ({"controlled_market_data_read_only_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_MARKET_DATA_READ_ONLY_REVIEW_FIXES),
        ({"controlled_order_blocking_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_ORDER_BLOCKING_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_ORDER_BLOCKING_REVIEW_FIXES),
        ({"controlled_position_mutation_block_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_POSITION_MUTATION_BLOCK_REVIEW_FIXES),
        ({"controlled_observability_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_OBSERVABILITY_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_OBSERVABILITY_REVIEW_FIXES),
        ({"controlled_journal_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_JOURNAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_JOURNAL_REVIEW_FIXES),
        ({"controlled_human_approval_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_HUMAN_APPROVAL_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_HUMAN_APPROVAL_REVIEW_FIXES),
        ({"controlled_stop_conditions_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_STOP_CONDITION_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_STOP_CONDITION_REVIEW_FIXES),
        ({"controlled_success_failure_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_SUCCESS_FAILURE_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_SUCCESS_FAILURE_REVIEW_FIXES),
        ({"controlled_audit_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_AUDIT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_AUDIT_REVIEW_FIXES),
        ({"controlled_go_no_go_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_GO_NO_GO_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_GO_NO_GO_REVIEW_FIXES),
        ({"controlled_abort_review_verified": False}, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_ABORT_REVIEW_FAILED, PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.REQUIRE_CONTROLLED_ABORT_REVIEW_FIXES),
    ],
)
def test_review_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState.CONTROLLED_EXECUTION_PREPARATION_REVIEW_BLOCKED


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
def test_real_boundaries_are_blocked(overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(_ready_input(**overrides))

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW


def test_data_access_is_blocked():
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(
        _ready_input(data_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewDecision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW


def test_premature_final_plan_is_detected():
    risks = detect_controlled_execution_preparation_review_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_controlled_execution_final_plan_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN in risks


def test_recommendations_and_markdown_are_rendered():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(data)
    markdown = render_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review_markdown(result)

    assert generate_controlled_execution_preparation_review_recommendations(data) == (
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_PREPARATION_REVIEW_SUITE,
        PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_EXECUTION_FINAL_PLAN,
    )
    assert "# Paper Broker Read-Only Connection Dry Run Controlled Execution Preparation Review" in markdown
    assert "Review score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_and_missing_preparation_are_supported():
    nominal = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(
        dict(_ready_input().__dict__)
    )
    missing = evaluate_paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review(None)

    assert nominal.review_score == 100
    assert missing.state is PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewState.CONTROLLED_EXECUTION_PREPARATION_REVIEW_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunControlledExecutionPreparationReviewRisk.CONTROLLED_EXECUTION_PREPARATION_NOT_APPROVED in missing.risks


def test_source_has_no_real_io_or_network_imports():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_execution_preparation_review.py"
    ).read_text()

    forbidden = ("import os", "import socket", "import requests", "from requests", "urllib", "http.client", "open(", "os.environ")
    for token in forbidden:
        assert token not in source
