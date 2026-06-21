from pathlib import Path

import pytest

from agicore.trading.paper_broker_read_only_connection_preparation import (
    evaluate_paper_broker_read_only_connection_preparation,
)
from agicore.trading.paper_broker_read_only_connection_preparation_review import (
    compute_read_only_connection_preparation_review_score,
    detect_read_only_connection_preparation_review_risks,
    evaluate_paper_broker_read_only_connection_preparation_review,
    generate_read_only_connection_preparation_review_recommendations,
    render_paper_broker_read_only_connection_preparation_review_markdown,
    review_account_read_only_contract,
    review_broker_adapter_boundary,
    review_connection_configuration_schema,
    review_connection_human_approval_contract,
    review_connection_journal_contract,
    review_connection_observability_contract,
    review_connection_stop_conditions_contract,
    review_credentials_reference_contract,
    review_http_websocket_socket_block_guard,
    review_market_data_read_only_contract,
    review_network_execution_block_guard,
    review_no_secret_read_guard,
    review_order_blocking_contract,
    review_position_mutation_block_contract,
    review_read_only_connection_contract,
    validate_connection_preparation_approval,
)
from agicore.trading.paper_broker_read_only_connection_preparation_review_models import (
    PaperBrokerReadOnlyConnectionPreparationReviewDecision,
    PaperBrokerReadOnlyConnectionPreparationReviewInput,
    PaperBrokerReadOnlyConnectionPreparationReviewRecommendation,
    PaperBrokerReadOnlyConnectionPreparationReviewRisk,
    PaperBrokerReadOnlyConnectionPreparationReviewState,
)
from tests.unit.trading.test_paper_broker_read_only_connection_preparation import _ready_input as _preparation_ready_input


def _upstream(state="READY", decision=None, risks=(), **extra):
    payload = {"state": state, "decision": decision or state, "risks": tuple(risks), "offline_only": True}
    payload.update(extra)
    return payload


def _preparation_result(**overrides):
    result = evaluate_paper_broker_read_only_connection_preparation(_preparation_ready_input())
    payload = dict(result.__dict__)
    payload.update(overrides)
    return payload


def _ready_input(**overrides):
    payload = {
        "paper_broker_read_only_connection_preparation": _preparation_result(),
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
        "connection_preparation_approved": True,
        "connection_contract_review_verified": True,
        "broker_adapter_boundary_review_verified": True,
        "configuration_schema_review_verified": True,
        "credential_reference_review_verified": True,
        "no_secret_read_guard_review_verified": True,
        "network_block_guard_review_verified": True,
        "http_websocket_socket_block_guard_review_verified": True,
        "account_read_only_contract_review_verified": True,
        "market_data_read_only_contract_review_verified": True,
        "order_blocking_contract_review_verified": True,
        "position_mutation_block_review_verified": True,
        "observability_contract_review_verified": True,
        "journal_contract_review_verified": True,
        "human_approval_contract_review_verified": True,
        "stop_conditions_contract_review_verified": True,
        "paper_broker_read_only_connection_dry_run_plan_requested": False,
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
    }
    payload.update(overrides)
    return PaperBrokerReadOnlyConnectionPreparationReviewInput(**payload)


def _bad_contract(**overrides):
    payload = {"defined": False, "score": 0, "risks": ("bad",)}
    payload.update(overrides)
    return payload


def _prep_with(**contract_overrides):
    return _preparation_result(**contract_overrides)


def test_nominal_preparation_review_is_approved():
    result = evaluate_paper_broker_read_only_connection_preparation_review(_ready_input())

    assert result.state is PaperBrokerReadOnlyConnectionPreparationReviewState.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW
    assert result.review_score == 100
    assert result.risks == ()
    assert result.offline_only is True
    assert result.no_secret_read_guard_review.guard_enforced is True
    assert result.network_execution_block_guard_review.network_execution_blocked is True
    assert result.order_blocking_contract_review.order_execution_blocked is True
    assert result.position_mutation_block_contract_review.position_mutation_blocked is True


def test_review_functions_pass_nominal_input():
    data = _ready_input()

    assert validate_connection_preparation_approval(data) is True
    assert review_read_only_connection_contract(data).passed is True
    assert review_broker_adapter_boundary(data).passed is True
    assert review_connection_configuration_schema(data).passed is True
    assert review_credentials_reference_contract(data).passed is True
    assert review_no_secret_read_guard(data).passed is True
    assert review_network_execution_block_guard(data).passed is True
    assert review_http_websocket_socket_block_guard(data).passed is True
    assert review_account_read_only_contract(data).passed is True
    assert review_market_data_read_only_contract(data).passed is True
    assert review_order_blocking_contract(data).passed is True
    assert review_position_mutation_block_contract(data).passed is True
    assert review_connection_observability_contract(data).passed is True
    assert review_connection_journal_contract(data).passed is True
    assert review_connection_human_approval_contract(data).passed is True
    assert review_connection_stop_conditions_contract(data).passed is True
    assert compute_read_only_connection_preparation_review_score(data).overall_score == 100


def test_non_approved_preparation_blocks_review():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_preparation=_preparation_result(
                state="CONNECTION_PREPARATION_BLOCKED",
                decision="REQUIRE_NETWORK_BLOCK_GUARD_FIXES",
                risks=("NETWORK_EXECUTION_BLOCK_GUARD_MISSING",),
            ),
            connection_preparation_approved=False,
        )
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_PREPARATION_NOT_APPROVED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONNECTION_PREPARATION_FIXES


@pytest.mark.parametrize(
    ("field", "contract_payload", "risk", "decision"),
    [
        (
            "read_only_connection_contract",
            _bad_contract(read_only_only=False, no_connection_execution=False, preparation_only=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.READ_ONLY_CONNECTION_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONNECTION_CONTRACT_REVIEW_FIXES,
        ),
        (
            "broker_adapter_boundary",
            _bad_contract(no_real_broker=False, no_alpaca_real=False, adapter_instantiation_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES,
        ),
        (
            "connection_configuration_schema",
            _bad_contract(schema_only=False, env_var_read_blocked=False, api_key_value_absent=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CONFIGURATION_SCHEMA_REVIEW_FIXES,
        ),
        (
            "credentials_reference_contract",
            _bad_contract(reference_only=False, no_secret_values=False, no_api_key_read=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.CREDENTIAL_REFERENCE_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_CREDENTIAL_REFERENCE_REVIEW_FIXES,
        ),
        (
            "no_secret_read_guard",
            _bad_contract(guard_enforced=False, no_api_key_read=False, no_env_var_read=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.SECRET_READ_GUARD_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_NO_SECRET_READ_GUARD_REVIEW_FIXES,
        ),
        (
            "network_execution_block_guard",
            _bad_contract(network_execution_blocked=False, external_api_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.NETWORK_EXECUTION_BLOCK_GUARD_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
        ),
        (
            "http_websocket_socket_block_guard",
            _bad_contract(http_blocked=False, websocket_blocked=False, socket_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.HTTP_WEBSOCKET_SOCKET_BLOCK_GUARD_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_NETWORK_BLOCK_GUARD_REVIEW_FIXES,
        ),
        (
            "account_read_only_contract",
            _bad_contract(active_account_access_blocked=False, account_mutations_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_ACCOUNT_READ_ONLY_CONTRACT_REVIEW_FIXES,
        ),
        (
            "market_data_read_only_contract",
            _bad_contract(read_only_market_data_only=False, live_subscription_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_MARKET_DATA_READ_ONLY_CONTRACT_REVIEW_FIXES,
        ),
        (
            "order_blocking_contract",
            _bad_contract(order_execution_blocked=False, real_order_blocked=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.ORDER_BLOCKING_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_ORDER_BLOCKING_CONTRACT_REVIEW_FIXES,
        ),
        (
            "position_mutation_block_contract",
            _bad_contract(position_mutation_blocked=False, position_request_absent=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.POSITION_MUTATION_BLOCK_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_POSITION_MUTATION_BLOCK_REVIEW_FIXES,
        ),
        (
            "human_approval_contract",
            _bad_contract(human_approval_required=False, approval_before_review=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.HUMAN_APPROVAL_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_HUMAN_APPROVAL_CONTRACT_REVIEW_FIXES,
        ),
        (
            "stop_conditions_contract",
            _bad_contract(stop_on_secret_read=False, stop_on_network_request=False),
            PaperBrokerReadOnlyConnectionPreparationReviewRisk.STOP_CONDITION_CONTRACT_REVIEW_FAILED,
            PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_STOP_CONDITION_CONTRACT_REVIEW_FIXES,
        ),
    ],
)
def test_invalid_contracts_are_rejected(field, contract_payload, risk, decision):
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(paper_broker_read_only_connection_preparation=_prep_with(**{field: contract_payload}))
    )

    assert risk in result.risks
    assert result.decision is decision


def test_observability_contract_invalid_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_preparation=_prep_with(
                observability_contract=_bad_contract(offline_events_defined=False, sensitive_values_redacted=False)
            )
        )
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.OBSERVABILITY_CONTRACT_REVIEW_FAILED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_OBSERVABILITY_CONTRACT_REVIEW_FIXES


def test_journal_contract_invalid_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_preparation=_prep_with(
                journal_contract=_bad_contract(offline_journal_required=False, no_secret_material_logged=False)
            )
        )
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.JOURNAL_CONTRACT_REVIEW_FAILED in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_JOURNAL_CONTRACT_REVIEW_FIXES


def test_secret_and_env_read_are_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(api_key_read_requested=True, env_var_read_requested=True, hardcoded_secret_detected=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.CONNECTION_CONFIGURATION_SCHEMA_REVIEW_FAILED in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.SECRET_READ_GUARD_REVIEW_FAILED in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.FIX_NO_SECRET_READ_GUARD in result.recommendations


def test_real_execution_boundary_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(no_real_broker=False, broker_connection_requested=True, real_execution_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED in result.risks
    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES


def test_data_access_violation_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(_ready_input(data_access_requested=True))

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.DATA_ACCESS_VIOLATION in result.risks
    assert result.decision is PaperBrokerReadOnlyConnectionPreparationReviewDecision.REQUIRE_BROKER_ADAPTER_BOUNDARY_REVIEW_FIXES


def test_premature_dry_run_plan_is_rejected():
    result = evaluate_paper_broker_read_only_connection_preparation_review(
        _ready_input(paper_broker_read_only_connection_dry_run_plan_requested=True)
    )

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN in result.risks
    assert (
        PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.DELAY_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN
        in result.recommendations
    )


def test_recommendations_and_markdown_for_nominal_case():
    data = _ready_input()
    result = evaluate_paper_broker_read_only_connection_preparation_review(data)
    markdown = render_paper_broker_read_only_connection_preparation_review_markdown(result)

    assert generate_read_only_connection_preparation_review_recommendations(data) == (
        PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW_SUITE,
        PaperBrokerReadOnlyConnectionPreparationReviewRecommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_PLAN,
    )
    assert "Paper Broker Read-Only Connection Preparation Review" in markdown
    assert "No API key or environment variable read" in markdown
    assert PaperBrokerReadOnlyConnectionPreparationReviewDecision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_PREPARATION_REVIEW.value in markdown


def test_mapping_input_ignores_unknown_fields_and_detects_risks():
    data = dict(_ready_input().__dict__)
    data["unknown"] = "ignored"
    data["network_transport_requested"] = True

    risks = detect_read_only_connection_preparation_review_risks(data)

    assert PaperBrokerReadOnlyConnectionPreparationReviewRisk.BROKER_ADAPTER_BOUNDARY_REVIEW_FAILED in risks


def test_module_does_not_import_network_secret_or_environment_clients():
    source = Path("src/agicore/trading/paper_broker_read_only_connection_preparation_review.py").read_text(encoding="utf-8")

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
