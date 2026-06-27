from pathlib import Path

import pytest

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation as prep
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationDecision as Decision,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationInput,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRecommendation as Recommendation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk as Risk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationState as State,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate import (
    _ready_input as _safety_gate_ready_input,
)


def _safety_gate():
    return evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate(
        _safety_gate_ready_input()
    )


def _ready_input(**overrides):
    values = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate": _safety_gate(),
        "offline_runner_implementation_safety_gate_approved": True,
    }
    values.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationInput(**values)


def test_nominal_implementation_preparation_is_approved():
    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input()
    )

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert len(result.contracts) == len(prep._SPECS)
    assert result.no_secret_read_guard.no_secret_read is True
    assert result.network_block_guard.network_blocked is True
    assert result.data_access_guard.data_access_blocked is True


def test_safety_gate_approval_validation_rejects_unapproved_or_risky_gate():
    assert prep.validate_offline_runner_implementation_safety_gate_approval(_ready_input()) is True

    gate = _safety_gate()
    risky_gate = gate.__class__(
        **{
            **gate.__dict__,
            "risks": (PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSafetyGateRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,),
        }
    )
    data = _ready_input(
        paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_safety_gate=risky_gate
    )

    assert prep.validate_offline_runner_implementation_safety_gate_approval(data) is False


def test_all_prepare_functions_pass_nominally():
    data = _ready_input()
    for key, (function_name, _cls, _risk, _decision, _recommendation) in prep._SPECS.items():
        assert hasattr(prep, function_name), key
        assert getattr(prep, function_name)(data).prepared is True


@pytest.mark.parametrize(
    ("key", "risk", "decision"),
    [("gate", Risk.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_FIXES)]
    + [(key, risk, decision) for key, (_fn, _cls, risk, decision, _recommendation) in prep._SPECS.items()],
)
def test_each_missing_or_unsafe_component_blocks(key, risk, decision):
    overrides = {"offline_runner_implementation_safety_gate_approved": False}
    if key != "gate":
        overrides = {f"offline_runner_{key}_prepared": False}

    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input(**overrides)
    )

    assert risk in result.risks
    assert result.decision is decision
    assert result.score.overall_score < 100


@pytest.mark.parametrize(
    "overrides",
    [
        {"real_execution_requested": True},
        {"runner_creation_requested": True},
        {"runner_execution_requested": True},
        {"dry_run_requested": True},
        {"dry_run_executed": True},
        {"broker_connection_requested": True},
        {"api_key_read_requested": True},
        {"env_var_read_requested": True},
        {"hardcoded_secret_detected": True},
        {"network_transport_requested": True},
        {"external_api_requested": True},
        {"order_execution_requested": True},
        {"position_mutation_requested": True},
        {"account_access_requested": True},
        {"no_http_transport": False},
        {"no_websocket_transport": False},
        {"no_socket_transport": False},
        {"no_real_broker": False},
        {"no_api_key_read": False},
        {"no_env_var_read": False},
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input(**overrides)
    )

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION


def test_data_access_is_blocked():
    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert Risk.OFFLINE_RUNNER_DATA_ACCESS_GUARD_PREPARATION_UNSAFE in result.risks


def test_premature_preparation_review_is_blocked():
    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_requested=True
        )
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION


def test_mapping_input_and_missing_gate_are_handled():
    nominal = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        dict(_ready_input().__dict__)
    )
    missing = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation({})

    assert nominal.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION
    assert missing.state is State.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_SAFETY_GATE_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = prep.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _ready_input()
    )
    markdown = prep.render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_markdown(result)

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW in result.recommendations
    assert "Implementation Preparation" in markdown
    assert "no executable runner creation" in markdown


def test_score_risks_and_recommendations_helpers():
    data = _ready_input(offline_runner_observability_contract_prepared=False)
    score = prep.compute_offline_runner_implementation_preparation_score(data)
    risks = prep.detect_offline_runner_implementation_preparation_risks(data)
    recommendations = prep.generate_offline_runner_implementation_preparation_recommendations(data, risks)

    assert score.observability_contract_score == 0
    assert Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_MISSING in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation.py"
    ).read_text(encoding="utf-8")
    forbidden = ["requests", "urllib", "import websocket", "import socket", "socket.", "os.environ", "open("]
    for token in forbidden:
        assert token not in source
