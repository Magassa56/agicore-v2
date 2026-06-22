from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation import (
    compute_read_only_connection_dry_run_execution_preparation_score,
    detect_read_only_connection_dry_run_execution_preparation_risks,
    evaluate_paper_broker_read_only_connection_dry_run_execution_preparation,
    generate_read_only_connection_dry_run_execution_preparation_recommendations,
    prepare_dry_run_execution_account_read_only_contract,
    prepare_dry_run_execution_audit_contract,
    prepare_dry_run_execution_sequence_contract,
    prepare_dry_run_execution_precondition_contract,
    prepare_dry_run_execution_credentials_reference_contract,
    prepare_dry_run_execution_runtime_contract,
    prepare_dry_run_execution_http_websocket_socket_block_guard,
    prepare_dry_run_execution_human_approval_contract,
    prepare_dry_run_execution_journal_contract,
    prepare_dry_run_execution_market_data_read_only_contract,
    prepare_dry_run_execution_network_block_guard,
    prepare_dry_run_execution_no_secret_read_guard,
    prepare_dry_run_execution_observability_contract,
    prepare_dry_run_execution_order_blocking_contract,
    prepare_dry_run_execution_position_mutation_block_contract,
    prepare_dry_run_execution_stop_conditions_contract,
    prepare_dry_run_execution_success_failure_contract,
    render_paper_broker_read_only_connection_dry_run_execution_preparation_markdown,
    validate_dry_run_execution_safety_gate_approval,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk,
    PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_execution_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_execution_safety_gate import (
    _ready_input as _gate_ready_input,
)


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _safety_gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_safety_gate(_gate_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_dry_run_execution_safety_gate": _safety_gate_result(),
        "paper_broker_read_only_connection_dry_run_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_SAFETY_GATE",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
        ),
        "paper_broker_read_only_connection_preparation_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
        ),
        "paper_broker_read_only_connection_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
        ),
        "paper_broker_read_only_connection_safety_gate": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
        ),
        "paper_broker_read_only_connection_plan": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_SAFETY_GATE",
            "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
        ),
        "paper_broker_read_only_safety_review": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PLAN",
            "APPROVE_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
        ),
        "paper_broker_read_only_preparation": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_SAFETY_REVIEW",
            "APPROVE_PAPER_BROKER_READ_ONLY_PREPARATION",
        ),
        "multi_scenario_result_report": _upstream(
            "READY_FOR_PAPER_BROKER_READ_ONLY_PREPARATION",
            "APPROVE_MULTI_SCENARIO_RESULT_REPORT_ROBUSTNESS_REVIEW",
        ),
        "multi_scenario_controlled_simulation_result": _upstream(
            "READY_FOR_MULTI_SCENARIO_RESULT_REPORT",
            "APPROVE_MULTI_SCENARIO_CONTROLLED_SIMULATION",
        ),
        "performance_risk_validation_gate": _upstream(
            "READY_FOR_MULTI_SCENARIO_CONTROLLED_SIMULATION",
            "APPROVE_PERFORMANCE_RISK_VALIDATION_GATE",
        ),
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
        "dry_run_execution_safety_gate_approved": True,
        "dry_run_execution_runtime_contract_prepared": True,
        "dry_run_execution_sequence_contract_prepared": True,
        "dry_run_execution_precondition_contract_prepared": True,
        "dry_run_execution_credentials_reference_contract_prepared": True,
        "dry_run_execution_credentials_reference_only": True,
        "dry_run_execution_no_secret_read_guard_prepared": True,
        "dry_run_execution_secret_read_guard_enforced": True,
        "dry_run_execution_network_block_guard_prepared": True,
        "dry_run_execution_network_blocked": True,
        "dry_run_execution_http_websocket_socket_block_guard_prepared": True,
        "dry_run_execution_http_transport_blocked": True,
        "dry_run_execution_websocket_transport_blocked": True,
        "dry_run_execution_socket_transport_blocked": True,
        "dry_run_execution_external_api_blocked": True,
        "dry_run_execution_account_read_only_contract_prepared": True,
        "dry_run_execution_account_active_access_blocked": True,
        "dry_run_execution_account_mutations_blocked": True,
        "dry_run_execution_market_data_read_only_contract_prepared": True,
        "dry_run_execution_market_data_live_subscription_blocked": True,
        "dry_run_execution_market_data_network_request_blocked": True,
        "dry_run_execution_order_blocking_contract_prepared": True,
        "dry_run_execution_order_execution_blocked": True,
        "dry_run_execution_cancel_replace_blocked": True,
        "dry_run_execution_position_mutation_block_contract_prepared": True,
        "dry_run_execution_position_mutation_blocked": True,
        "dry_run_execution_observability_contract_prepared": True,
        "dry_run_execution_journal_contract_prepared": True,
        "dry_run_execution_human_approval_contract_prepared": True,
        "dry_run_execution_human_approval_required": True,
        "dry_run_execution_stop_conditions_contract_prepared": True,
        "dry_run_execution_success_failure_contract_prepared": True,
        "dry_run_execution_audit_contract_prepared": True,
        "paper_broker_read_only_connection_dry_run_execution_preparation_review_requested": False,
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
    return PaperBrokerReadOnlyConnectionDryRunExecutionPreparationInput(**payload)


def test_nominal_dry_run_preparation_is_approved():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION
    assert result.preparation_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.dry_run_execution_runtime_contract.dry_run_execution_disabled is True
    assert result.dry_run_execution_no_secret_read_guard.guard_enforced is True
    assert result.dry_run_execution_network_block_guard.network_execution_blocked is True
    assert result.dry_run_execution_order_blocking_contract.order_execution_blocked is True
    assert result.dry_run_execution_position_mutation_block_contract.position_mutation_blocked is True
    assert result.dry_run_execution_audit_contract.audit_events_defined is True


def test_preparation_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_dry_run_execution_safety_gate_approval(data) is True
    assert prepare_dry_run_execution_runtime_contract(data).defined is True
    assert prepare_dry_run_execution_sequence_contract(data).connection_not_executed is True
    assert prepare_dry_run_execution_precondition_contract(data).fail_closed is True
    assert prepare_dry_run_execution_credentials_reference_contract(data).reference_only is True
    assert prepare_dry_run_execution_no_secret_read_guard(data).no_api_key_read is True
    assert prepare_dry_run_execution_network_block_guard(data).external_api_blocked is True
    assert prepare_dry_run_execution_http_websocket_socket_block_guard(data).socket_blocked is True
    assert prepare_dry_run_execution_account_read_only_contract(data).active_account_access_blocked is True
    assert prepare_dry_run_execution_market_data_read_only_contract(data).network_request_blocked is True
    assert prepare_dry_run_execution_order_blocking_contract(data).cancel_replace_blocked is True
    assert prepare_dry_run_execution_position_mutation_block_contract(data).position_request_absent is True
    assert prepare_dry_run_execution_observability_contract(data).offline_events_defined is True
    assert prepare_dry_run_execution_journal_contract(data).offline_journal_required is True
    assert prepare_dry_run_execution_human_approval_contract(data).human_approval_required is True
    assert prepare_dry_run_execution_stop_conditions_contract(data).stop_on_network_request is True
    assert prepare_dry_run_execution_success_failure_contract(data).failure_on_secret_network_order_position_or_account is True
    assert prepare_dry_run_execution_audit_contract(data).offline_evidence_required is True
    assert compute_read_only_connection_dry_run_execution_preparation_score(data).overall_score == 100


def test_safety_gate_not_approved_blocks_preparation():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(
        _ready_input(
            paper_broker_read_only_connection_dry_run_execution_safety_gate=_safety_gate_result(
                state="DRY_RUN_SAFETY_BLOCKED",
                decision="REQUIRE_BOUNDARY_SAFETY_FIXES",
                risks=("REAL_EXECUTION_BOUNDARY_VIOLATION",),
            ),
            dry_run_execution_safety_gate_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SAFETY_GATE_FIXES


@pytest.mark.parametrize(
    ("overrides", "risk", "decision"),
    [
        ({"dry_run_execution_runtime_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_RUNTIME_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_RUNTIME_CONTRACT_FIXES),
        ({"dry_run_execution_sequence_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_FIXES),
        ({"dry_run_execution_precondition_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_PRECONDITION_CONTRACT_FIXES),
        ({"dry_run_execution_credentials_reference_only": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_CREDENTIAL_REFERENCE_FIXES),
        ({"dry_run_execution_secret_read_guard_enforced": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SECRET_READ_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_NO_SECRET_READ_GUARD_FIXES),
        ({"dry_run_execution_network_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_FIXES),
        ({"dry_run_execution_websocket_transport_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD_FIXES),
        ({"dry_run_execution_account_active_access_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_ACCOUNT_READ_ONLY_FIXES),
        ({"dry_run_execution_market_data_network_request_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_MARKET_DATA_READ_ONLY_FIXES),
        ({"dry_run_execution_order_execution_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_ORDER_BLOCKING_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_ORDER_BLOCKING_FIXES),
        ({"dry_run_execution_position_mutation_blocked": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_UNSAFE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_POSITION_MUTATION_BLOCK_FIXES),
        ({"dry_run_execution_observability_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_OBSERVABILITY_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_OBSERVABILITY_FIXES),
        ({"dry_run_execution_journal_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_JOURNAL_INCOMPLETE, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_JOURNAL_FIXES),
        ({"dry_run_execution_human_approval_required": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_HUMAN_APPROVAL_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_HUMAN_APPROVAL_FIXES),
        ({"dry_run_execution_stop_conditions_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_STOP_CONDITIONS_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_STOP_CONDITION_FIXES),
        ({"dry_run_execution_success_failure_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SUCCESS_FAILURE_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SUCCESS_FAILURE_FIXES),
        ({"dry_run_execution_audit_contract_prepared": False}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_AUDIT_CONTRACT_MISSING, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_AUDIT_FIXES),
    ],
)
def test_required_contract_gaps_are_enforced(overrides, risk, decision):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is decision
    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.DRY_RUN_EXECUTION_PREPARATION_BLOCKED


@pytest.mark.parametrize(
    ("overrides", "risk"),
    [
        ({"real_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"broker_connection_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"api_key_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"env_var_read_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"hardcoded_secret_detected": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"network_transport_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"order_execution_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"position_mutation_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"account_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"dry_run_executed": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION),
        ({"data_access_requested": True}, PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DATA_ACCESS_VIOLATION),
    ],
)
def test_boundary_violations_are_detected(overrides, risk):
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(_ready_input(**overrides))

    assert risk in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationDecision.REQUIRE_DRY_RUN_EXECUTION_SEQUENCE_CONTRACT_FIXES


def test_premature_preparation_review_is_detected():
    risks = detect_read_only_connection_dry_run_execution_preparation_risks(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_preparation_review_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW in risks


def test_recommendations_map_risks_to_actions():
    recommendations = generate_read_only_connection_dry_run_execution_preparation_recommendations(
        _ready_input(dry_run_execution_network_blocked=False)
    )

    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.HOLD_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW in recommendations
    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.INSTALL_DRY_RUN_EXECUTION_NETWORK_BLOCK_GUARD in recommendations


def test_nominal_recommendations_approve_next_review():
    recommendations = generate_read_only_connection_dry_run_execution_preparation_recommendations(_ready_input())

    assert recommendations == (
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_SUITE,
        PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION_REVIEW,
    )


def test_markdown_render_includes_decision_score_and_boundaries():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(_ready_input())
    markdown = render_paper_broker_read_only_connection_dry_run_execution_preparation_markdown(result)

    assert "# Paper Broker Read-Only Connection Dry Run Execution Preparation" in markdown
    assert "APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_EXECUTION_PREPARATION" in markdown
    assert "Preparation score: 100" in markdown
    assert "No HTTP, websocket, socket, network transport, or external API" in markdown
    assert "No data/ access" in markdown


def test_mapping_input_is_supported():
    data = dict(_ready_input().__dict__)
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(data)

    assert result.preparation_score == 100
    assert result.risks == ()


def test_input_without_safety_gate_is_invalid():
    result = evaluate_paper_broker_read_only_connection_dry_run_execution_preparation(
        _ready_input(paper_broker_read_only_connection_dry_run_execution_safety_gate=None)
    )

    assert result.state is PaperBrokerReadOnlyConnectionDryRunExecutionPreparationState.DRY_RUN_EXECUTION_PREPARATION_INPUT_INVALID
    assert PaperBrokerReadOnlyConnectionDryRunExecutionPreparationRisk.DRY_RUN_EXECUTION_SAFETY_GATE_NOT_APPROVED in result.risks


def test_source_does_not_open_runtime_transports_or_data_access():
    source_path = Path("src/agicore/trading/paper_broker_read_only_connection_dry_run_execution_preparation.py")
    source = source_path.read_text(encoding="utf-8")

    assert "import requests" not in source
    assert "import socket" not in source
    assert "websocket" in source
    assert "os.environ" not in source
    assert "Path('data" not in source
    assert "Path(\"data" not in source
