from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_preparation import (
    compute_read_only_connection_preparation_score,
    detect_read_only_connection_preparation_risks,
    evaluate_paper_broker_read_only_connection_preparation,
    generate_read_only_connection_preparation_recommendations,
    prepare_account_read_only_contract,
    prepare_broker_adapter_boundary,
    prepare_connection_configuration_schema,
    prepare_connection_human_approval_contract,
    prepare_connection_journal_contract,
    prepare_connection_observability_contract,
    prepare_connection_stop_conditions_contract,
    prepare_credentials_reference_contract,
    prepare_http_websocket_socket_block_guard,
    prepare_market_data_read_only_contract,
    prepare_network_execution_block_guard,
    prepare_no_secret_read_guard,
    prepare_order_blocking_contract,
    prepare_position_mutation_block_contract,
    prepare_read_only_connection_contract,
    render_paper_broker_read_only_connection_preparation_markdown,
    validate_connection_safety_gate_approval,
)
from agicore.trading.paper_broker_read_only_connection_preparation_models import (
    PaperBrokerReadOnlyConnectionPreparationDecision,
    PaperBrokerReadOnlyConnectionPreparationInput,
    PaperBrokerReadOnlyConnectionPreparationRecommendation,
    PaperBrokerReadOnlyConnectionPreparationRisk,
    PaperBrokerReadOnlyConnectionPreparationState,
)
from agicore.trading.paper_broker_read_only_connection_safety_gate import (
    evaluate_paper_broker_read_only_connection_safety_gate,
)
from tests.unit.trading.test_paper_broker_read_only_connection_safety_gate import _ready_input as _safety_gate_ready_input


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _safety_gate_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_safety_gate(_safety_gate_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_safety_gate": _safety_gate_result(),
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
        "connection_safety_gate_approved": True,
        "read_only_connection_contract_prepared": True,
        "broker_adapter_boundary_prepared": True,
        "connection_configuration_schema_prepared": True,
        "credentials_reference_contract_prepared": True,
        "credentials_reference_only": True,
        "no_secret_read_guard_prepared": True,
        "secret_read_guard_enforced": True,
        "network_execution_block_guard_prepared": True,
        "network_execution_blocked": True,
        "http_websocket_socket_block_guard_prepared": True,
        "http_transport_blocked": True,
        "websocket_transport_blocked": True,
        "socket_transport_blocked": True,
        "account_read_only_contract_prepared": True,
        "account_active_access_blocked": True,
        "account_mutations_blocked": True,
        "market_data_read_only_contract_prepared": True,
        "market_data_live_subscription_blocked": True,
        "market_data_network_request_blocked": True,
        "order_blocking_contract_prepared": True,
        "order_execution_blocked": True,
        "cancel_replace_blocked": True,
        "position_mutation_block_contract_prepared": True,
        "position_mutation_blocked": True,
        "observability_contract_prepared": True,
        "journal_contract_prepared": True,
        "human_approval_contract_prepared": True,
        "human_approval_required": True,
        "stop_conditions_contract_prepared": True,
        "paper_broker_read_only_connection_preparation_review_requested": False,
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
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionPreparationInput(**payload)


def test_nominal_connection_preparation_is_approved():
    result = evaluate_paper_broker_read_only_connection_preparation(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionPreparationState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION
    assert result.preparation_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.read_only_connection_contract.no_connection_execution is True
    assert result.credentials_reference_contract.secret_source == "none_in_this_phase"
    assert result.network_execution_block_guard.network_execution_blocked is True
    assert result.order_blocking_contract.order_execution_blocked is True
    assert result.position_mutation_block_contract.position_mutation_blocked is True


def test_prepare_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_connection_safety_gate_approval(data) is True
    assert prepare_read_only_connection_contract(data).defined is True
    assert prepare_broker_adapter_boundary(data).adapter_instantiation_blocked is True
    assert prepare_connection_configuration_schema(data).env_var_read_blocked is True
    assert prepare_credentials_reference_contract(data).reference_only is True
    assert prepare_no_secret_read_guard(data).guard_enforced is True
    assert prepare_network_execution_block_guard(data).network_execution_blocked is True
    assert prepare_http_websocket_socket_block_guard(data).http_blocked is True
    assert prepare_account_read_only_contract(data).active_account_access_blocked is True
    assert prepare_market_data_read_only_contract(data).live_subscription_blocked is True
    assert prepare_order_blocking_contract(data).cancel_replace_blocked is True
    assert prepare_position_mutation_block_contract(data).close_modify_blocked is True
    assert prepare_connection_observability_contract(data).defined is True
    assert prepare_connection_journal_contract(data).no_secret_material_logged is True
    assert prepare_connection_human_approval_contract(data).human_approval_required is True
    assert prepare_connection_stop_conditions_contract(data).stop_on_network_request is True
    assert compute_read_only_connection_preparation_score(data).overall_score == 100


def test_non_approved_safety_gate_blocks_preparation():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(
            paper_broker_read_only_connection_safety_gate=_safety_gate_result(
                state="CONNECTION_SAFETY_BLOCKED",
                decision="REQUIRE_NETWORK_BLOCK_FIXES",
                risks=("NETWORK_EXECUTION_NOT_BLOCKED",),
            ),
            connection_safety_gate_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_SAFETY_GATE_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONNECTION_SAFETY_GATE_FIXES


@pytest.mark.parametrize(
    ("field", "risk", "decision"),
    [
        (
            "read_only_connection_contract_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.READ_ONLY_CONNECTION_CONTRACT_MISSING,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONNECTION_CONTRACT_FIXES,
        ),
        (
            "broker_adapter_boundary_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.BROKER_ADAPTER_BOUNDARY_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES,
        ),
        (
            "connection_configuration_schema_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.CONNECTION_CONFIGURATION_SCHEMA_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CONFIGURATION_SCHEMA_FIXES,
        ),
        (
            "credentials_reference_contract_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.CREDENTIAL_REFERENCE_CONTRACT_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_CREDENTIAL_REFERENCE_CONTRACT_FIXES,
        ),
        (
            "account_read_only_contract_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.ACCOUNT_READ_ONLY_CONTRACT_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_FIXES,
        ),
        (
            "market_data_read_only_contract_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_FIXES,
        ),
        (
            "human_approval_contract_prepared",
            PaperBrokerReadOnlyConnectionPreparationRisk.HUMAN_APPROVAL_CONTRACT_MISSING,
            PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_HUMAN_APPROVAL_CONTRACT_FIXES,
        ),
    ],
)
def test_required_contracts_are_enforced(field, risk, decision):
    result = evaluate_paper_broker_read_only_connection_preparation(_ready_input(**{field: False}))

    assert risk in result.risks
    assert result.decision is decision


def test_secret_guard_missing_or_secret_read_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(no_secret_read_guard_prepared=False, api_key_read_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_NO_SECRET_READ_GUARD_FIXES


def test_hardcoded_secret_or_env_read_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(no_hardcoded_secrets=False, hardcoded_secret_detected=True, env_var_read_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.SECRET_READ_GUARD_MISSING in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationRecommendation.INSTALL_NO_SECRET_READ_GUARD in result.recommendations


def test_network_guard_missing_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(network_execution_block_guard_prepared=False, network_transport_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.NETWORK_EXECUTION_BLOCK_GUARD_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_NETWORK_BLOCK_GUARD_FIXES


def test_http_websocket_socket_guard_missing_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(
            http_websocket_socket_block_guard_prepared=False,
            no_http_transport=False,
            no_websocket_transport=False,
            no_socket_transport=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_MISSING in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_NETWORK_BLOCK_GUARD_FIXES


def test_order_execution_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(order_execution_blocked=False, order_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.ORDER_BLOCKING_CONTRACT_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_ORDER_BLOCKING_CONTRACT_FIXES


def test_position_mutation_not_blocked_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(position_mutation_blocked=False, position_mutation_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.POSITION_MUTATION_BLOCK_CONTRACT_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_POSITION_MUTATION_BLOCK_FIXES


def test_account_read_only_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(account_active_access_blocked=False, account_access_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.ACCOUNT_READ_ONLY_CONTRACT_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_FIXES


def test_market_data_read_only_unsafe_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(market_data_live_subscription_blocked=False)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.MARKET_DATA_READ_ONLY_CONTRACT_UNSAFE in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_FIXES


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(no_real_broker=False, broker_connection_requested=True, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionPreparationRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_FIXES


def test_stop_conditions_missing_blocks_preparation_review():
    result = evaluate_paper_broker_read_only_connection_preparation(
        _ready_input(stop_conditions_contract_prepared=False, paper_broker_read_only_connection_preparation_review_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationRisk.STOP_CONDITION_CONTRACT_MISSING in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationRecommendation.DEFINE_CONNECTION_STOP_CONDITIONS in result.recommendations


def test_recommendations_and_markdown_for_nominal_case():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_preparation(data)
    markdown = render_paper_broker_read_only_connection_preparation_markdown(result)

    assert generate_read_only_connection_preparation_recommendations(data) == (
        PaperBrokerReadOnlyConnectionPreparationRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_SUITE,
        PaperBrokerReadOnlyConnectionPreparationRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW,
    )
    assert "Paper Broker Read-Only Connection Preparation" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlyConnectionPreparationDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["order_execution_requested"] = True

    risks = detect_read_only_connection_preparation_risks(data)

    assert PaperBrokerReadOnlyConnectionPreparationRisk.ORDER_BLOCKING_CONTRACT_UNSAFE in risks


def test_module_does_not_import_network_secret_or_environment_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_preparation.py").read_text(encoding="utf-8")

    forbidden_imports = (
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import httpx",
        "import aiohttp",
        "import websockets",
        "import socket",
        "import os",
    )
    assert all(pattern not in source for pattern in forbidden_imports)
