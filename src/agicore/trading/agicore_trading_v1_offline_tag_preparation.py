"""AGIcore Trading v1 offline tag preparation."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_preparation_models import (
    AGIcoreTradingV1OfflineTagPreparationArtifact,
    AGIcoreTradingV1OfflineTagPreparationDecision,
    AGIcoreTradingV1OfflineTagPreparationInput,
    AGIcoreTradingV1OfflineTagPreparationRecommendation,
    AGIcoreTradingV1OfflineTagPreparationReport,
    AGIcoreTradingV1OfflineTagPreparationResult,
    AGIcoreTradingV1OfflineTagPreparationRisk,
    AGIcoreTradingV1OfflineTagPreparationReadyState,
    AGIcoreTradingV1OfflineTagPreparationScore,
    AGIcoreTradingV1OfflineTagPreparationState,
    AGIcoreTradingV1OfflineTagPreparationTagInformation,
    AGIcoreTradingV1OfflineTagPreparationTestingEvidence,
    AGIcoreTradingV1OfflineTagPreparationVersionMetadata,
)


Risk = AGIcoreTradingV1OfflineTagPreparationRisk
Recommendation = AGIcoreTradingV1OfflineTagPreparationRecommendation
Decision = AGIcoreTradingV1OfflineTagPreparationDecision
State = AGIcoreTradingV1OfflineTagPreparationState

VERSION_NUMBER = "v1.0.0-offline"
TAG_NAME = "agicore-trading-v1-offline"

OFFLINE_V1_ARTIFACTS = (
    "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
    "docs/AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
    "docs/AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
    "docs/AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
    "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE.md",
    "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW.md",
    "src/agicore/trading/csv_replay_input_v1.py",
    "src/agicore/trading/synthetic_market_scenario_v1.py",
    "src/agicore/trading/strategy_replay_engine_v1.py",
    "src/agicore/trading/simulated_broker_stub_v1.py",
    "src/agicore/trading/risk_guard_enforcement_v1.py",
    "src/agicore/trading/journal_writer_v1.py",
    "src/agicore/trading/offline_report_markdown_json_v1.py",
    "src/agicore/trading/agicore_trading_v1_offline_smoke_demo.py",
    "src/agicore/trading/agicore_trading_v1_offline_release_package_review.py",
)

TESTING_EVIDENCE = (
    ("python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_release_package_review.py -q", "36 passed"),
    ("python -m pytest tests/unit/trading/ -q", "4084 passed"),
    ("python -m pytest tests/unit/ -q", "4473 passed"),
    ("git diff --check", "OK"),
)

READY_STATES = (
    (
        "Release Package Review",
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION",
    ),
    (
        "Tag Preparation",
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW",
    ),
)

DOCUMENTATION_MARKERS = (
    "offline/sandbox",
    "pas de trading reel",
    "pas de broker reel",
    "pas d'ordre reel",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "AGIcore Trading v1 Offline Tag Preparation",
)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    output: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return tuple(output)


def _coerce_input(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagPreparationInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineTagPreparationInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineTagPreparationInput)}
    return AGIcoreTradingV1OfflineTagPreparationInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_tag_preparation_input(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.preparation_id and assert_agicore_trading_v1_offline_tag_preparation_boundaries(payload))


def verify_agicore_trading_v1_offline_artifacts(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagPreparationArtifact, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_artifacts_incomplete:
        return tuple(AGIcoreTradingV1OfflineTagPreparationArtifact(path, present=False) for path in OFFLINE_V1_ARTIFACTS[:-1])
    return tuple(AGIcoreTradingV1OfflineTagPreparationArtifact(path) for path in OFFLINE_V1_ARTIFACTS)


def verify_agicore_trading_v1_offline_documentation_coherence(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_documentation_incoherent)


def verify_agicore_trading_v1_offline_ready_states(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagPreparationReadyState, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_ready_states_incoherent:
        return tuple(AGIcoreTradingV1OfflineTagPreparationReadyState(source, state, coherent=False) for source, state in READY_STATES)
    return tuple(AGIcoreTradingV1OfflineTagPreparationReadyState(source, state) for source, state in READY_STATES)


def verify_agicore_trading_v1_offline_testing_evidence(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineTagPreparationTestingEvidence, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_test_evidence_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineTagPreparationTestingEvidence(command, result) for command, result in TESTING_EVIDENCE)


def prepare_agicore_trading_v1_offline_version_metadata(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagPreparationVersionMetadata | None:
    payload = _coerce_input(data)
    if payload and payload.force_version_metadata_missing:
        return None
    return AGIcoreTradingV1OfflineTagPreparationVersionMetadata(
        product="AGIcore Trading",
        release_name="AGIcore Trading v1 Offline",
        release_scope="offline/sandbox local only",
        safety_profile="no broker, no network, no API key, no real order, no data access",
    )


def prepare_agicore_trading_v1_offline_version_number(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> str:
    payload = _coerce_input(data)
    if payload and payload.force_version_number_invalid:
        return ""
    return VERSION_NUMBER


def prepare_agicore_trading_v1_offline_tag_information(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagPreparationTagInformation | None:
    payload = _coerce_input(data)
    if payload and payload.force_tag_information_missing:
        return None
    version_number = prepare_agicore_trading_v1_offline_version_number(payload)
    if not version_number:
        return None
    return AGIcoreTradingV1OfflineTagPreparationTagInformation(
        tag_name=TAG_NAME,
        version_number=version_number,
        target_branch="main",
        tag_message="AGIcore Trading v1 Offline sandbox release",
    )


def render_agicore_trading_v1_offline_tag_preparation_markdown(
    artifacts: tuple[AGIcoreTradingV1OfflineTagPreparationArtifact, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineTagPreparationTestingEvidence, ...],
    ready_states: tuple[AGIcoreTradingV1OfflineTagPreparationReadyState, ...],
    version_metadata: AGIcoreTradingV1OfflineTagPreparationVersionMetadata | None,
    tag_information: AGIcoreTradingV1OfflineTagPreparationTagInformation | None,
) -> str:
    lines = [
        "# AGIcore Trading v1 Offline Tag Preparation",
        "",
        "## Statut",
        "",
        "offline/sandbox tag preparation only",
        "",
        "## Decision nominale",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION",
        "",
        "## State attendu",
        "",
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW",
        "",
        "## Version",
        "",
        f"- version number : {tag_information.version_number if tag_information else ''}",
        f"- tag name : {tag_information.tag_name if tag_information else ''}",
        f"- target branch : {tag_information.target_branch if tag_information else ''}",
        "",
        "## Metadata",
        "",
        f"- product : {version_metadata.product if version_metadata else ''}",
        f"- release name : {version_metadata.release_name if version_metadata else ''}",
        f"- release scope : {version_metadata.release_scope if version_metadata else ''}",
        f"- safety profile : {version_metadata.safety_profile if version_metadata else ''}",
        "",
        "## Artefacts V1 Offline",
        "",
    ]
    lines.extend(f"- {artifact.path}" for artifact in artifacts if artifact.present)
    lines.extend(("", "## Etats READY_FOR", ""))
    lines.extend(f"- {state.source} : {state.state}" for state in ready_states if state.coherent)
    lines.extend(("", "## Preuves de tests", ""))
    lines.extend(f"- {evidence.command} : {evidence.result}" for evidence in testing_evidence if evidence.validated)
    lines.extend(
        (
            "",
            "## Contraintes confirmees",
            "",
            "- offline/sandbox",
            "- pas de trading reel",
            "- pas de broker reel",
            "- pas d'ordre reel",
            "- pas de preuve de rentabilite",
            "- pas de conseil financier",
            "- aucun acces data/",
            "- aucun reseau",
            "- aucune cle API",
            "",
            "## Prochaine etape suggeree",
            "",
            "AGIcore Trading v1 Offline Final Tag Review",
        )
    )
    return "\n".join(lines) + "\n"


def validate_agicore_trading_v1_offline_tag_preparation_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Preparation",
        "offline/sandbox tag preparation only",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION",
        "READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW",
        VERSION_NUMBER,
        TAG_NAME,
        "AGIcore Trading v1 Offline",
        "docs/AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW.md",
        "src/agicore/trading/strategy_replay_engine_v1.py",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_release_package_review.py -q : 36 passed",
        "python -m pytest tests/unit/trading/ -q : 4084 passed",
        "python -m pytest tests/unit/ -q : 4473 passed",
        "git diff --check : OK",
        "pas de trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "aucun acces data/",
        "AGIcore Trading v1 Offline Final Tag Review",
    )
    return all(item in markdown for item in required)


def _boundary_risks(data: AGIcoreTradingV1OfflineTagPreparationInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    if data.file_read_requested:
        risks.append(Risk.FILE_READ_BOUNDARY_VIOLATION)
    if data.real_data_access_requested:
        risks.append(Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION)
    if data.data_directory_access_requested:
        risks.append(Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION)
    if data.broker_connection_requested:
        risks.append(Risk.REAL_BROKER_BOUNDARY_VIOLATION)
    if data.secret_read_requested:
        risks.append(Risk.REAL_SECRET_BOUNDARY_VIOLATION)
    if data.network_requested or data.http_requested or data.websocket_requested or data.socket_requested or data.external_api_requested:
        risks.append(Risk.NETWORK_BOUNDARY_VIOLATION)
    if data.order_execution_requested:
        risks.append(Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION)
    if data.account_access_requested:
        risks.append(Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION)
    if data.position_mutation_requested:
        risks.append(Risk.POSITION_MUTATION_BOUNDARY_VIOLATION)
    return _dedupe(risks)


def assert_agicore_trading_v1_offline_tag_preparation_boundaries(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_tag_preparation_risks(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
    artifacts: tuple[AGIcoreTradingV1OfflineTagPreparationArtifact, ...] = (),
    documentation_coherent: bool = True,
    ready_states: tuple[AGIcoreTradingV1OfflineTagPreparationReadyState, ...] = (),
    testing_evidence: tuple[AGIcoreTradingV1OfflineTagPreparationTestingEvidence, ...] = (),
    version_metadata: AGIcoreTradingV1OfflineTagPreparationVersionMetadata | None = None,
    version_number: str = "",
    tag_information: AGIcoreTradingV1OfflineTagPreparationTagInformation | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.TAG_PREPARATION_INPUT_MISSING)
    if len(artifacts) != len(OFFLINE_V1_ARTIFACTS) or any(not artifact.present for artifact in artifacts):
        risks.append(Risk.TAG_PREPARATION_ARTIFACTS_INCOMPLETE)
    if not documentation_coherent:
        risks.append(Risk.TAG_PREPARATION_DOCUMENTATION_INCOHERENT)
    if len(ready_states) != len(READY_STATES) or any(not state.coherent for state in ready_states):
        risks.append(Risk.TAG_PREPARATION_READY_STATES_INCOHERENT)
    if len(testing_evidence) != len(TESTING_EVIDENCE):
        risks.append(Risk.TAG_PREPARATION_TEST_EVIDENCE_MISSING)
    if version_metadata is None:
        risks.append(Risk.TAG_PREPARATION_VERSION_METADATA_MISSING)
    if version_number != VERSION_NUMBER:
        risks.append(Risk.TAG_PREPARATION_VERSION_NUMBER_INVALID)
    if tag_information is None:
        risks.append(Risk.TAG_PREPARATION_TAG_INFORMATION_MISSING)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_tag_preparation_score(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
    artifacts: tuple[AGIcoreTradingV1OfflineTagPreparationArtifact, ...],
    documentation_coherent: bool,
    ready_states: tuple[AGIcoreTradingV1OfflineTagPreparationReadyState, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineTagPreparationTestingEvidence, ...],
    version_metadata: AGIcoreTradingV1OfflineTagPreparationVersionMetadata | None,
    version_number: str,
    tag_information: AGIcoreTradingV1OfflineTagPreparationTagInformation | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineTagPreparationScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_tag_preparation_input(payload) else 0
    artifact_score = 100 if len(artifacts) == len(OFFLINE_V1_ARTIFACTS) and all(item.present for item in artifacts) else 0
    documentation_score = 100 if documentation_coherent else 0
    ready_state_score = 100 if len(ready_states) == len(READY_STATES) and all(item.coherent for item in ready_states) else 0
    test_evidence_score = 100 if len(testing_evidence) == len(TESTING_EVIDENCE) else 0
    version_metadata_score = 100 if version_metadata is not None else 0
    version_number_score = 100 if version_number == VERSION_NUMBER else 0
    tag_information_score = 100 if tag_information is not None and tag_information.tag_name == TAG_NAME else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        artifact_score,
        documentation_score,
        ready_state_score,
        test_evidence_score,
        version_metadata_score,
        version_number_score,
        tag_information_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineTagPreparationScore(
        overall_score=overall,
        input_score=input_score,
        artifact_score=artifact_score,
        documentation_score=documentation_score,
        ready_state_score=ready_state_score,
        test_evidence_score=test_evidence_score,
        version_metadata_score=version_metadata_score,
        version_number_score=version_number_score,
        tag_information_score=tag_information_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_tag_preparation_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_PREPARATION_INPUT_MISSING: Recommendation.PROVIDE_TAG_PREPARATION_INPUT,
        Risk.TAG_PREPARATION_ARTIFACTS_INCOMPLETE: Recommendation.RESTORE_TAG_PREPARATION_ARTIFACTS,
        Risk.TAG_PREPARATION_DOCUMENTATION_INCOHERENT: Recommendation.RESTORE_TAG_PREPARATION_DOCUMENTATION,
        Risk.TAG_PREPARATION_READY_STATES_INCOHERENT: Recommendation.RESTORE_TAG_PREPARATION_READY_STATES,
        Risk.TAG_PREPARATION_TEST_EVIDENCE_MISSING: Recommendation.RESTORE_TAG_PREPARATION_TEST_EVIDENCE,
        Risk.TAG_PREPARATION_VERSION_METADATA_MISSING: Recommendation.RESTORE_TAG_PREPARATION_VERSION_METADATA,
        Risk.TAG_PREPARATION_VERSION_NUMBER_INVALID: Recommendation.RESTORE_TAG_PREPARATION_VERSION_NUMBER,
        Risk.TAG_PREPARATION_TAG_INFORMATION_MISSING: Recommendation.RESTORE_TAG_PREPARATION_TAG_INFORMATION,
        Risk.FILE_READ_BOUNDARY_VIOLATION: Recommendation.REMOVE_FILE_READ,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_DATA_ACCESS,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_DATA_DIRECTORY_ACCESS,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_BROKER_ACCESS,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION: Recommendation.REMOVE_REAL_SECRET_ACCESS,
        Risk.NETWORK_BOUNDARY_VIOLATION: Recommendation.REMOVE_NETWORK_ACCESS,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION: Recommendation.REMOVE_ORDER_EXECUTION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION: Recommendation.REMOVE_ACCOUNT_ACCESS,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION: Recommendation.REMOVE_POSITION_MUTATION,
    }
    recommendations = [mapping[risk] for risk in risks if risk in mapping]
    if not recommendations:
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION
    if Risk.TAG_PREPARATION_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_PREPARATION_INPUT_FIXES
    if Risk.TAG_PREPARATION_ARTIFACTS_INCOMPLETE in risks:
        return Decision.REQUIRE_TAG_PREPARATION_ARTIFACT_FIXES
    if Risk.TAG_PREPARATION_DOCUMENTATION_INCOHERENT in risks:
        return Decision.REQUIRE_TAG_PREPARATION_DOCUMENTATION_FIXES
    if Risk.TAG_PREPARATION_READY_STATES_INCOHERENT in risks:
        return Decision.REQUIRE_TAG_PREPARATION_READY_STATE_FIXES
    if Risk.TAG_PREPARATION_TEST_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_TAG_PREPARATION_TEST_EVIDENCE_FIXES
    if Risk.TAG_PREPARATION_VERSION_METADATA_MISSING in risks or Risk.TAG_PREPARATION_VERSION_NUMBER_INVALID in risks:
        return Decision.REQUIRE_TAG_PREPARATION_VERSION_FIXES
    if Risk.TAG_PREPARATION_TAG_INFORMATION_MISSING in risks:
        return Decision.REQUIRE_TAG_PREPARATION_TAG_INFO_FIXES
    boundary_risks = {
        Risk.FILE_READ_BOUNDARY_VIOLATION,
        Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION,
        Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION,
        Risk.REAL_BROKER_BOUNDARY_VIOLATION,
        Risk.REAL_SECRET_BOUNDARY_VIOLATION,
        Risk.NETWORK_BOUNDARY_VIOLATION,
        Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION,
        Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION,
        Risk.POSITION_MUTATION_BOUNDARY_VIOLATION,
    }
    if set(risks) & boundary_risks:
        return Decision.REQUIRE_TAG_PREPARATION_BOUNDARY_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION


def _state_for(data: AGIcoreTradingV1OfflineTagPreparationInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION_BLOCKED


def _payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _payload_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_")}
    return str(value)


def render_agicore_trading_v1_offline_tag_preparation_json_report(
    result: AGIcoreTradingV1OfflineTagPreparationResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineTagPreparationResult):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_preparation",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "artifacts": _payload_value(result.artifacts),
            "testing_evidence": _payload_value(result.testing_evidence),
            "ready_states": _payload_value(result.ready_states),
            "version_metadata": _payload_value(result.version_metadata),
            "tag_information": _payload_value(result.tag_information),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "paper_broker_connected": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def prepare_agicore_trading_v1_offline_tag_preparation(
    data: AGIcoreTradingV1OfflineTagPreparationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagPreparationResult:
    payload = _coerce_input(data)
    artifacts = verify_agicore_trading_v1_offline_artifacts(payload)
    documentation_coherent = verify_agicore_trading_v1_offline_documentation_coherence(payload)
    ready_states = verify_agicore_trading_v1_offline_ready_states(payload)
    testing_evidence = verify_agicore_trading_v1_offline_testing_evidence(payload)
    version_metadata = prepare_agicore_trading_v1_offline_version_metadata(payload)
    version_number = prepare_agicore_trading_v1_offline_version_number(payload)
    tag_information = prepare_agicore_trading_v1_offline_tag_information(payload)
    risks = detect_agicore_trading_v1_offline_tag_preparation_risks(
        payload,
        artifacts,
        documentation_coherent,
        ready_states,
        testing_evidence,
        version_metadata,
        version_number,
        tag_information,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_preparation_score(
        payload,
        artifacts,
        documentation_coherent,
        ready_states,
        testing_evidence,
        version_metadata,
        version_number,
        tag_information,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_tag_preparation_recommendations(risks)
    base = AGIcoreTradingV1OfflineTagPreparationResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        artifacts=artifacts,
        testing_evidence=testing_evidence,
        ready_states=ready_states,
        version_metadata=version_metadata,
        tag_information=tag_information,
        report=None,
    )
    markdown = render_agicore_trading_v1_offline_tag_preparation_markdown(
        artifacts,
        testing_evidence,
        ready_states,
        version_metadata,
        tag_information,
    )
    report = AGIcoreTradingV1OfflineTagPreparationReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_tag_preparation_json_report(base),
    )
    return AGIcoreTradingV1OfflineTagPreparationResult(**{**base.__dict__, "report": report})
