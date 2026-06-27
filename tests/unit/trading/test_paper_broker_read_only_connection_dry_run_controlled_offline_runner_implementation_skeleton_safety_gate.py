from pathlib import Path

import pytest

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate as safety_gate
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateDecision as Decision,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRecommendation as Recommendation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateRisk as Risk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan import (
    _ready_input as _skeleton_plan_ready_input,
)


def _skeleton_plan():
    return evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan(
        _skeleton_plan_ready_input()
    )


def _ready_input(**overrides):
    values = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan": _skeleton_plan(),
        "offline_runner_implementation_skeleton_plan_approved": True,
    }
    values.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonSafetyGateInput(**values)


def test_nominal_skeleton_safety_gate_is_approved():
    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        _ready_input()
    )

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert len(result.boundaries) == len(safety_gate._SPECS)
    assert result.no_secret_read_boundary.no_secret_read is True
    assert result.network_block_boundary.network_blocked is True
    assert result.http_websocket_socket_block_boundary.socket_blocked is True
    assert result.data_access_boundary.data_access_blocked is True
    assert result.runtime_stub_boundary.stub_only is True
    assert result.readiness_criteria_boundary.safe is True


def test_skeleton_plan_approval_validation_rejects_unapproved_or_risky_plan():
    assert safety_gate.validate_offline_runner_implementation_skeleton_plan_approval(_ready_input()) is True

    plan = _skeleton_plan()
    risky_plan = plan.__class__(
        **{
            **plan.__dict__,
            "risks": (PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationSkeletonPlanRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,),
        }
    )
    data = _ready_input(
        paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_plan=risky_plan
    )

    assert safety_gate.validate_offline_runner_implementation_skeleton_plan_approval(data) is False


def test_all_boundary_functions_pass_nominally():
    data = _ready_input()
    for key, (function_name, _cls, _risk, _decision, _recommendation) in safety_gate._SPECS.items():
        assert hasattr(safety_gate, function_name), key
        assert getattr(safety_gate, function_name)(data).safe is True


@pytest.mark.parametrize(
    ("key", "risk", "decision"),
    [
        (
            "plan",
            Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED,
            Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_FIXES,
        )
    ]
    + [(key, risk, decision) for key, (_fn, _cls, risk, decision, _recommendation) in safety_gate._SPECS.items()],
)
def test_each_failed_boundary_blocks(key, risk, decision):
    overrides = {"offline_runner_implementation_skeleton_plan_approved": False}
    if key != "plan":
        overrides = {f"offline_runner_{key}_safe": False}

    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
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
        {"no_external_ml": False},
        {"no_external_llm": False},
        {"no_live_execution": False},
        {"stubs_only": False},
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        _ready_input(**overrides)
    )

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert (
        result.decision
        is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    )


def test_data_access_is_blocked():
    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert Risk.OFFLINE_RUNNER_SKELETON_SAFETY_DATA_ACCESS_BOUNDARY_FAILED in result.risks


def test_premature_skeleton_preparation_is_blocked():
    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_preparation_requested=True
        )
    )

    assert (
        Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION
        in result.risks
    )
    assert (
        result.decision
        is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    )


def test_mapping_input_and_missing_plan_are_handled():
    nominal = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        dict(_ready_input().__dict__)
    )
    missing = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate({})

    assert (
        nominal.decision
        is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE
    )
    assert missing.state is State.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PLAN_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = safety_gate.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate(
        _ready_input()
    )
    markdown = safety_gate.render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate_markdown(
        result
    )

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_SAFETY_GATE_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_SKELETON_PREPARATION in result.recommendations
    assert "Implementation Skeleton Safety Gate" in markdown
    assert "stub contracts only" in markdown


def test_score_risks_and_recommendations_helpers():
    data = _ready_input(offline_runner_observability_stub_boundary_safe=False)
    score = safety_gate.compute_offline_runner_skeleton_safety_gate_score(data)
    risks = safety_gate.detect_offline_runner_skeleton_safety_gate_risks(data)
    recommendations = safety_gate.generate_offline_runner_skeleton_safety_gate_recommendations(data, risks)

    assert score.observability_stub_boundary_score == 0
    assert Risk.OFFLINE_RUNNER_SKELETON_SAFETY_OBSERVABILITY_STUB_BOUNDARY_FAILED in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_SKELETON_SAFETY_OBSERVABILITY_STUB_BOUNDARY_FAILED in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_skeleton_safety_gate.py"
    ).read_text(encoding="utf-8")
    forbidden = ["requests", "urllib", "import websocket", "import socket", "socket.", "os.environ", "open("]
    for token in forbidden:
        assert token not in source
