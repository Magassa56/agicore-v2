from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from agicore.trading.agicore_trading_v1_offline_tag_preparation import (
    assert_agicore_trading_v1_offline_tag_preparation_boundaries,
    compute_agicore_trading_v1_offline_tag_preparation_score,
    detect_agicore_trading_v1_offline_tag_preparation_risks,
    generate_agicore_trading_v1_offline_tag_preparation_recommendations,
    prepare_agicore_trading_v1_offline_tag_information,
    prepare_agicore_trading_v1_offline_tag_preparation,
    prepare_agicore_trading_v1_offline_version_metadata,
    prepare_agicore_trading_v1_offline_version_number,
    render_agicore_trading_v1_offline_tag_preparation_json_report,
    render_agicore_trading_v1_offline_tag_preparation_markdown,
    validate_agicore_trading_v1_offline_tag_preparation_input,
    validate_agicore_trading_v1_offline_tag_preparation_markdown,
    verify_agicore_trading_v1_offline_artifacts,
    verify_agicore_trading_v1_offline_documentation_coherence,
    verify_agicore_trading_v1_offline_ready_states,
    verify_agicore_trading_v1_offline_testing_evidence,
)
from agicore.trading.agicore_trading_v1_offline_tag_preparation_models import (
    AGIcoreTradingV1OfflineTagPreparationDecision,
    AGIcoreTradingV1OfflineTagPreparationInput,
    AGIcoreTradingV1OfflineTagPreparationRecommendation,
    AGIcoreTradingV1OfflineTagPreparationRisk,
    AGIcoreTradingV1OfflineTagPreparationState,
)


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "src/agicore/trading/agicore_trading_v1_offline_tag_preparation.py"
DOC_PATH = ROOT / "docs/AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION.md"


def _input(**overrides):
    payload = {}
    payload.update(overrides)
    return AGIcoreTradingV1OfflineTagPreparationInput(**payload)


def test_nominal_tag_preparation():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input())

    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION
    assert result.state is AGIcoreTradingV1OfflineTagPreparationState.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW
    assert result.score.overall_score == 100
    assert result.risks == ()
    assert len(result.artifacts) == 15
    assert len(result.testing_evidence) == 4
    assert len(result.ready_states) == 2
    assert result.version_metadata.release_name == "AGIcore Trading v1 Offline"
    assert result.tag_information.tag_name == "agicore-trading-v1-offline"
    assert result.tag_information.version_number == "v1.0.0-offline"
    assert validate_agicore_trading_v1_offline_tag_preparation_markdown(result.report.markdown)


def test_input_manquant():
    result = prepare_agicore_trading_v1_offline_tag_preparation(None)

    assert validate_agicore_trading_v1_offline_tag_preparation_input(None) is False
    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_INPUT_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_INPUT_FIXES
    assert result.state is AGIcoreTradingV1OfflineTagPreparationState.AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_INPUT_INVALID


def test_artifacts_incomplete():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_artifacts_incomplete=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_ARTIFACTS_INCOMPLETE in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_ARTIFACT_FIXES


def test_documentation_incoherent():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_documentation_incoherent=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_DOCUMENTATION_INCOHERENT in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_DOCUMENTATION_FIXES
    assert verify_agicore_trading_v1_offline_documentation_coherence(_input(force_documentation_incoherent=True)) is False


def test_ready_states_incoherent():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_ready_states_incoherent=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_READY_STATES_INCOHERENT in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_READY_STATE_FIXES


def test_test_evidence_missing():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_test_evidence_missing=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_TEST_EVIDENCE_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_TEST_EVIDENCE_FIXES


def test_version_metadata_missing():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_version_metadata_missing=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_VERSION_METADATA_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_VERSION_FIXES
    assert prepare_agicore_trading_v1_offline_version_metadata(_input(force_version_metadata_missing=True)) is None


def test_version_number_invalid():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_version_number_invalid=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_VERSION_NUMBER_INVALID in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_VERSION_FIXES
    assert prepare_agicore_trading_v1_offline_version_number(_input(force_version_number_invalid=True)) == ""


def test_tag_information_missing():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input(force_tag_information_missing=True))

    assert AGIcoreTradingV1OfflineTagPreparationRisk.TAG_PREPARATION_TAG_INFORMATION_MISSING in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_TAG_INFO_FIXES
    assert prepare_agicore_trading_v1_offline_tag_information(_input(force_tag_information_missing=True)) is None


def test_markdown_genere_and_helpers():
    data = _input()
    artifacts = verify_agicore_trading_v1_offline_artifacts(data)
    testing_evidence = verify_agicore_trading_v1_offline_testing_evidence(data)
    ready_states = verify_agicore_trading_v1_offline_ready_states(data)
    metadata = prepare_agicore_trading_v1_offline_version_metadata(data)
    tag_information = prepare_agicore_trading_v1_offline_tag_information(data)
    markdown = render_agicore_trading_v1_offline_tag_preparation_markdown(
        artifacts,
        testing_evidence,
        ready_states,
        metadata,
        tag_information,
    )

    assert "AGIcore Trading v1 Offline Tag Preparation" in markdown
    assert "v1.0.0-offline" in markdown
    assert "agicore-trading-v1-offline" in markdown
    assert "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW" in markdown
    assert validate_agicore_trading_v1_offline_tag_preparation_markdown(markdown)


def test_markdown_docs_valide():
    markdown = DOC_PATH.read_text(encoding="utf-8")

    assert validate_agicore_trading_v1_offline_tag_preparation_markdown(markdown)
    assert "AGIcore Trading v1 Offline Final Tag Review" in markdown


def test_json_report():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input())
    payload = json.loads(render_agicore_trading_v1_offline_tag_preparation_json_report(result))

    assert payload["schema"] == "agicore_trading_v1_offline_tag_preparation"
    assert payload["decision"] == "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION"
    assert payload["state"] == "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW"
    assert payload["score"] == 100
    assert payload["tag_information"]["tag_name"] == "agicore-trading-v1-offline"
    assert payload["real_broker_ready"] is False
    assert payload["real_order_execution"] is False


def test_score_risks_and_recommendations_directly():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input())
    version_number = prepare_agicore_trading_v1_offline_version_number(_input())
    risks = detect_agicore_trading_v1_offline_tag_preparation_risks(
        _input(),
        result.artifacts,
        True,
        result.ready_states,
        result.testing_evidence,
        result.version_metadata,
        version_number,
        result.tag_information,
    )
    score = compute_agicore_trading_v1_offline_tag_preparation_score(
        _input(),
        result.artifacts,
        True,
        result.ready_states,
        result.testing_evidence,
        result.version_metadata,
        version_number,
        result.tag_information,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_tag_preparation_recommendations(risks)

    assert risks == ()
    assert score.overall_score == 100
    assert recommendations == (
        AGIcoreTradingV1OfflineTagPreparationRecommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW,
    )


@pytest.mark.parametrize(
    ("field", "risk"),
    (
        ("file_read_requested", AGIcoreTradingV1OfflineTagPreparationRisk.FILE_READ_BOUNDARY_VIOLATION),
        ("real_data_access_requested", AGIcoreTradingV1OfflineTagPreparationRisk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        ("data_directory_access_requested", AGIcoreTradingV1OfflineTagPreparationRisk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        ("broker_connection_requested", AGIcoreTradingV1OfflineTagPreparationRisk.REAL_BROKER_BOUNDARY_VIOLATION),
        ("secret_read_requested", AGIcoreTradingV1OfflineTagPreparationRisk.REAL_SECRET_BOUNDARY_VIOLATION),
        ("network_requested", AGIcoreTradingV1OfflineTagPreparationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("http_requested", AGIcoreTradingV1OfflineTagPreparationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("websocket_requested", AGIcoreTradingV1OfflineTagPreparationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("socket_requested", AGIcoreTradingV1OfflineTagPreparationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("external_api_requested", AGIcoreTradingV1OfflineTagPreparationRisk.NETWORK_BOUNDARY_VIOLATION),
        ("order_execution_requested", AGIcoreTradingV1OfflineTagPreparationRisk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        ("account_access_requested", AGIcoreTradingV1OfflineTagPreparationRisk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        ("position_mutation_requested", AGIcoreTradingV1OfflineTagPreparationRisk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    ),
)
def test_boundary_violations_are_blocked(field, risk):
    data = _input(**{field: True})
    result = prepare_agicore_trading_v1_offline_tag_preparation(data)

    assert risk in result.risks
    assert result.decision is AGIcoreTradingV1OfflineTagPreparationDecision.REQUIRE_TAG_PREPARATION_BOUNDARY_FIXES
    assert assert_agicore_trading_v1_offline_tag_preparation_boundaries(data) is False


def test_no_file_read_or_write_calls_in_module_source():
    source = MODULE_PATH.read_text(encoding="utf-8")

    assert "open(" not in source
    assert ".write(" not in source
    assert "write_text" not in source
    assert "read_text" not in source
    assert "Path(" not in source


def test_no_network_socket_http_websocket_imports_or_calls():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    forbidden_imports = {"requests", "httpx", "urllib", "socket", "websocket"}
    forbidden_calls = {"request", "urlopen", "connect", "send", "create_connection"}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert not {alias.name.split(".")[0] for alias in node.names} & forbidden_imports
        if isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden_imports
        if isinstance(node, ast.Call):
            func_name = getattr(node.func, "attr", getattr(node.func, "id", ""))
            assert func_name not in forbidden_calls


def test_no_real_secret_environment_read():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name != "os" for alias in node.names)
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv"}
        if isinstance(node, ast.Call):
            assert getattr(node.func, "attr", "") != "getenv"


def test_no_order_account_or_position_side_effects_are_reported():
    result = prepare_agicore_trading_v1_offline_tag_preparation(_input())

    assert result.file_read is False
    assert result.data_accessed is False
    assert result.real_order_submitted is False
    assert result.real_account_accessed is False
    assert result.position_mutated is False
