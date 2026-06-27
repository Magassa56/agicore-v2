from pathlib import Path

import pytest

from agicore.trading import paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review as review
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation import (
    evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewDecision as Decision,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRecommendation as Recommendation,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewRisk as Risk,
)
from agicore.trading.paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_models import (
    PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewState as State,
)
from tests.unit.trading.test_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation import (
    _ready_input as _preparation_ready_input,
)


def _preparation():
    return evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation(
        _preparation_ready_input()
    )


def _ready_input(**overrides):
    values = {
        "paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation": _preparation(),
        "offline_runner_implementation_preparation_approved": True,
    }
    values.update(overrides)
    return PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationReviewInput(**values)


def test_nominal_implementation_preparation_review_is_approved():
    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        _ready_input()
    )

    assert result.state is State.READY_FOR_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN
    assert result.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert result.runner_created is False
    assert result.runner_executed is False
    assert result.dry_run_executed is False
    assert len(result.findings) == len(review._SPECS)
    assert result.no_secret_read_guard.no_secret_read is True
    assert result.network_block_guard.network_blocked is True
    assert result.data_access_guard.data_access_blocked is True


def test_preparation_approval_validation_rejects_unapproved_or_risky_preparation():
    assert review.validate_offline_runner_implementation_preparation_approval(_ready_input()) is True

    preparation = _preparation()
    risky_preparation = preparation.__class__(
        **{
            **preparation.__dict__,
            "risks": (PaperBrokerReadOnlyConnectionDryRunControlledOfflineRunnerImplementationPreparationRisk.REAL_EXECUTION_BOUNDARY_VIOLATION,),
        }
    )
    data = _ready_input(
        paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation=risky_preparation
    )

    assert review.validate_offline_runner_implementation_preparation_approval(data) is False


def test_all_review_functions_pass_nominally():
    data = _ready_input()
    for key, (function_name, _cls, _risk, _decision, _recommendation) in review._SPECS.items():
        assert hasattr(review, function_name), key
        assert getattr(review, function_name)(data).reviewed is True


@pytest.mark.parametrize(
    ("key", "risk", "decision"),
    [
        ("preparation", Risk.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED, Decision.REQUIRE_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_FIXES)
    ]
    + [(key, risk, decision) for key, (_fn, _cls, risk, decision, _recommendation) in review._SPECS.items()],
)
def test_each_failed_review_component_blocks(key, risk, decision):
    overrides = {"offline_runner_implementation_preparation_approved": False}
    if key != "preparation":
        overrides = {f"offline_runner_{key}_reviewed": False}

    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
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
    ],
)
def test_real_execution_boundaries_are_blocked(overrides):
    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        _ready_input(**overrides)
    )

    assert Risk.REAL_EXECUTION_BOUNDARY_VIOLATION in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW


def test_data_access_is_blocked():
    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        _ready_input(data_access_requested=True)
    )

    assert Risk.DATA_ACCESS_VIOLATION in result.risks
    assert Risk.OFFLINE_RUNNER_DATA_ACCESS_GUARD_REVIEW_FAILED in result.risks


def test_premature_final_plan_is_blocked():
    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        _ready_input(
            paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_final_plan_requested=True
        )
    )

    assert Risk.PREMATURE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN in result.risks
    assert result.decision is Decision.BLOCK_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW


def test_mapping_input_and_missing_preparation_are_handled():
    nominal = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        dict(_ready_input().__dict__)
    )
    missing = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review({})

    assert nominal.decision is Decision.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW
    assert missing.state is State.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_INPUT_INVALID
    assert Risk.OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_NOT_APPROVED in missing.risks


def test_recommendations_and_markdown_nominal():
    result = review.evaluate_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review(
        _ready_input()
    )
    markdown = review.render_paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review_markdown(
        result
    )

    assert Recommendation.RUN_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_PREPARATION_REVIEW_SUITE in result.recommendations
    assert Recommendation.APPROVE_PAPER_BROKER_READ_ONLY_CONNECTION_DRY_RUN_CONTROLLED_OFFLINE_RUNNER_IMPLEMENTATION_FINAL_PLAN in result.recommendations
    assert "Implementation Preparation Review" in markdown
    assert "no executable runner creation" in markdown


def test_score_risks_and_recommendations_helpers():
    data = _ready_input(offline_runner_observability_contract_reviewed=False)
    score = review.compute_offline_runner_implementation_preparation_review_score(data)
    risks = review.detect_offline_runner_implementation_preparation_review_risks(data)
    recommendations = review.generate_offline_runner_implementation_preparation_review_recommendations(data, risks)

    assert score.observability_contract_score == 0
    assert Risk.OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED in risks
    assert Recommendation.FIX_OFFLINE_RUNNER_OBSERVABILITY_PREPARATION_REVIEW_FAILED in recommendations


def test_module_has_no_forbidden_runtime_imports_or_data_access():
    source = Path(
        "src/agicore/trading/paper_broker_read_only_connection_dry_run_controlled_offline_runner_implementation_preparation_review.py"
    ).read_text(encoding="utf-8")
    forbidden = ["requests", "urllib", "import websocket", "import socket", "socket.", "os.environ", "open("]
    for token in forbidden:
        assert token not in source
