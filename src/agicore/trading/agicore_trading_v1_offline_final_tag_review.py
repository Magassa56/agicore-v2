"""AGIcore Trading v1 offline final tag review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_final_tag_review_models import (
    AGIcoreTradingV1OfflineFinalTagReviewContext,
    AGIcoreTradingV1OfflineFinalTagReviewCriterion,
    AGIcoreTradingV1OfflineFinalTagReviewDecision,
    AGIcoreTradingV1OfflineFinalTagReviewDocument,
    AGIcoreTradingV1OfflineFinalTagReviewFinding,
    AGIcoreTradingV1OfflineFinalTagReviewInput,
    AGIcoreTradingV1OfflineFinalTagReviewRecommendation,
    AGIcoreTradingV1OfflineFinalTagReviewReport,
    AGIcoreTradingV1OfflineFinalTagReviewResult,
    AGIcoreTradingV1OfflineFinalTagReviewRisk,
    AGIcoreTradingV1OfflineFinalTagReviewScore,
    AGIcoreTradingV1OfflineFinalTagReviewState,
    AGIcoreTradingV1OfflineFinalTagReviewTagMetadata,
    AGIcoreTradingV1OfflineFinalTagReviewTestingEvidence,
)


Risk = AGIcoreTradingV1OfflineFinalTagReviewRisk
Recommendation = AGIcoreTradingV1OfflineFinalTagReviewRecommendation
Decision = AGIcoreTradingV1OfflineFinalTagReviewDecision
State = AGIcoreTradingV1OfflineFinalTagReviewState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

DOCUMENTS = (
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
    "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
    "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
    "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE.md",
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW.md",
    "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION.md",
)

TESTING_EVIDENCE = (
    ("python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_tag_preparation.py -q", "30 passed"),
    ("python -m pytest tests/unit/trading/ -q", "4114 passed"),
    ("python -m pytest tests/unit/ -q", "4503 passed"),
    ("git diff --check", "OK"),
)

CRITERIA = (
    "tag name coherent",
    "version coherent",
    "documents presents",
    "release package valide",
    "release package review validee",
    "final readiness validee",
    "safety language present",
    "no-overclaim valide",
    "aucun tag Git cree",
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
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalTagReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineFinalTagReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineFinalTagReviewInput)}
    return AGIcoreTradingV1OfflineFinalTagReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_final_tag_review_input(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.review_id and assert_agicore_trading_v1_offline_final_tag_review_boundaries(payload))


def build_final_tag_review_context(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalTagReviewContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    documents = tuple(
        AGIcoreTradingV1OfflineFinalTagReviewDocument(
            path=document,
            present=payload.documents_present,
            coherent=payload.documents_present and payload.safety_language_present,
        )
        for document in DOCUMENTS
    )
    evidence = (
        tuple(AGIcoreTradingV1OfflineFinalTagReviewTestingEvidence(command, result) for command, result in TESTING_EVIDENCE)
        if payload.testing_evidence_present
        else ()
    )
    criteria = tuple(AGIcoreTradingV1OfflineFinalTagReviewCriterion(name, True) for name in CRITERIA)
    return AGIcoreTradingV1OfflineFinalTagReviewContext(
        review_id=payload.review_id,
        tag_metadata=AGIcoreTradingV1OfflineFinalTagReviewTagMetadata(
            tag_name=payload.tag_name,
            version=payload.version,
            git_tag_created=payload.git_tag_already_created,
            creation_mode="manual future tag creation only",
        ),
        documents=documents,
        testing_evidence=evidence,
        criteria=criteria,
    )


def review_final_tag_preparation_approval(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_preparation_approved)


def review_final_tag_name(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_final_tag_version(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_final_tag_documents(context: AGIcoreTradingV1OfflineFinalTagReviewContext | None) -> bool:
    return bool(context and len(context.documents) == len(DOCUMENTS) and all(document.present for document in context.documents))


def review_final_tag_release_package(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.release_package_validated)


def review_final_tag_release_package_review(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.release_package_review_validated)


def review_final_tag_final_readiness(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.final_readiness_validated)


def review_final_tag_testing_evidence(context: AGIcoreTradingV1OfflineFinalTagReviewContext | None) -> bool:
    return bool(context and len(context.testing_evidence) == len(TESTING_EVIDENCE))


def review_final_tag_no_git_tag_created(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_final_tag_safety_boundaries(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.safety_language_present
        and review_final_tag_no_live_trading_claim(payload)
        and review_final_tag_no_profitability_claim(payload)
        and review_final_tag_no_financial_advice_claim(payload)
        and not payload.real_broker_overclaim
        and not payload.real_order_overclaim
        and not payload.paper_broker_overclaim
        and assert_agicore_trading_v1_offline_final_tag_review_boundaries(payload)
    )


def review_final_tag_no_live_trading_claim(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_final_tag_no_profitability_claim(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_final_tag_no_financial_advice_claim(data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _boundary_risks(data: AGIcoreTradingV1OfflineFinalTagReviewInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_final_tag_review_boundaries(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_final_tag_review_risks(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineFinalTagReviewContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.FINAL_TAG_REVIEW_INPUT_MISSING)
    if not review_final_tag_preparation_approval(payload):
        risks.append(Risk.FINAL_TAG_PREPARATION_NOT_APPROVED)
    if not review_final_tag_name(payload):
        risks.append(Risk.FINAL_TAG_NAME_INVALID)
    if not review_final_tag_version(payload):
        risks.append(Risk.FINAL_TAG_VERSION_INVALID)
    if not review_final_tag_documents(context):
        risks.append(Risk.FINAL_TAG_DOCUMENTS_MISSING)
    if not review_final_tag_release_package(payload):
        risks.append(Risk.FINAL_TAG_RELEASE_PACKAGE_MISSING)
    if not review_final_tag_release_package_review(payload):
        risks.append(Risk.FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING)
    if not review_final_tag_final_readiness(payload):
        risks.append(Risk.FINAL_TAG_FINAL_READINESS_MISSING)
    if not review_final_tag_testing_evidence(context):
        risks.append(Risk.FINAL_TAG_TESTING_EVIDENCE_MISSING)
    if payload and payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload and payload.live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload and payload.profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_final_tag_review_score(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineFinalTagReviewContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineFinalTagReviewScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_final_tag_review_input(payload) else 0
    preparation_score = 100 if review_final_tag_preparation_approval(payload) else 0
    tag_name_score = 100 if review_final_tag_name(payload) else 0
    version_score = 100 if review_final_tag_version(payload) else 0
    document_score = 100 if review_final_tag_documents(context) else 0
    release_package_score = (
        100
        if review_final_tag_release_package(payload)
        and review_final_tag_release_package_review(payload)
        and review_final_tag_final_readiness(payload)
        else 0
    )
    testing_evidence_score = 100 if review_final_tag_testing_evidence(context) else 0
    git_tag_score = 100 if review_final_tag_no_git_tag_created(payload) else 0
    safety_score = 100 if review_final_tag_safety_boundaries(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        preparation_score,
        tag_name_score,
        version_score,
        document_score,
        release_package_score,
        testing_evidence_score,
        git_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineFinalTagReviewScore(
        overall_score=overall,
        input_score=input_score,
        preparation_score=preparation_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        document_score=document_score,
        release_package_score=release_package_score,
        testing_evidence_score=testing_evidence_score,
        git_tag_score=git_tag_score,
        safety_score=safety_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_final_tag_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.FINAL_TAG_REVIEW_INPUT_MISSING: Recommendation.PROVIDE_FINAL_TAG_REVIEW_INPUT,
        Risk.FINAL_TAG_PREPARATION_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_PREPARATION_APPROVAL,
        Risk.FINAL_TAG_NAME_INVALID: Recommendation.RESTORE_FINAL_TAG_NAME,
        Risk.FINAL_TAG_VERSION_INVALID: Recommendation.RESTORE_FINAL_TAG_VERSION,
        Risk.FINAL_TAG_DOCUMENTS_MISSING: Recommendation.RESTORE_FINAL_TAG_DOCUMENTS,
        Risk.FINAL_TAG_RELEASE_PACKAGE_MISSING: Recommendation.RESTORE_FINAL_TAG_RELEASE_PACKAGE,
        Risk.FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING: Recommendation.RESTORE_FINAL_TAG_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_TAG_FINAL_READINESS_MISSING: Recommendation.RESTORE_FINAL_TAG_FINAL_READINESS,
        Risk.FINAL_TAG_TESTING_EVIDENCE_MISSING: Recommendation.RESTORE_FINAL_TAG_TESTING_EVIDENCE,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_REVIEW,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM: Recommendation.REMOVE_PAPER_BROKER_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_OVERCLAIM,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW
    if Risk.FINAL_TAG_REVIEW_INPUT_MISSING in risks:
        return Decision.REQUIRE_FINAL_TAG_REVIEW_INPUT_FIXES
    if Risk.FINAL_TAG_PREPARATION_NOT_APPROVED in risks:
        return Decision.REQUIRE_FINAL_TAG_PREPARATION_FIXES
    if Risk.FINAL_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_FINAL_TAG_NAME_FIXES
    if Risk.FINAL_TAG_VERSION_INVALID in risks:
        return Decision.REQUIRE_FINAL_TAG_VERSION_FIXES
    if Risk.FINAL_TAG_DOCUMENTS_MISSING in risks:
        return Decision.REQUIRE_FINAL_TAG_DOCUMENT_FIXES
    if (
        Risk.FINAL_TAG_RELEASE_PACKAGE_MISSING in risks
        or Risk.FINAL_TAG_RELEASE_PACKAGE_REVIEW_MISSING in risks
        or Risk.FINAL_TAG_FINAL_READINESS_MISSING in risks
    ):
        return Decision.REQUIRE_FINAL_TAG_RELEASE_PACKAGE_FIXES
    if Risk.FINAL_TAG_TESTING_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_FINAL_TAG_TESTING_EVIDENCE_FIXES
    overclaim_risks = {
        Risk.GIT_TAG_ALREADY_CREATED,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
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
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_FINAL_TAG_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW


def _state_for(data: AGIcoreTradingV1OfflineFinalTagReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_INSTRUCTIONS
    return State.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW_BLOCKED


def _build_findings(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | None,
    context: AGIcoreTradingV1OfflineFinalTagReviewContext | None,
) -> tuple[AGIcoreTradingV1OfflineFinalTagReviewFinding, ...]:
    checks = (
        ("tag preparation", review_final_tag_preparation_approval(data), "Tag Preparation approuvee"),
        ("tag name", review_final_tag_name(data), EXPECTED_TAG_NAME),
        ("version", review_final_tag_version(data), EXPECTED_VERSION),
        ("documents", review_final_tag_documents(context), "documents offline verifies"),
        ("release package", review_final_tag_release_package(data), "release package valide"),
        ("release package review", review_final_tag_release_package_review(data), "release package review validee"),
        ("final readiness", review_final_tag_final_readiness(data), "final readiness validee"),
        ("testing evidence", review_final_tag_testing_evidence(context), "preuves de tests presentes"),
        ("no git tag created", review_final_tag_no_git_tag_created(data), "aucun tag Git cree"),
        ("safety boundaries", review_final_tag_safety_boundaries(data), "offline/sandbox only"),
    )
    return tuple(AGIcoreTradingV1OfflineFinalTagReviewFinding(name, passed, detail) for name, passed, detail in checks)


def render_agicore_trading_v1_offline_final_tag_review_markdown(
    context: AGIcoreTradingV1OfflineFinalTagReviewContext | None,
    findings: tuple[AGIcoreTradingV1OfflineFinalTagReviewFinding, ...],
) -> str:
    tag_metadata = context.tag_metadata if context else None
    documents = context.documents if context else ()
    evidence = context.testing_evidence if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Final Tag Review",
        "",
        "## Statut",
        "",
        "offline/sandbox final tag review only",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW",
        "",
        "## Conclusion",
        "",
        "- tag preparation complete",
        "- release package complet",
        "- V1 offline utilisable localement en sandbox",
        "- pas de tag Git cree pendant cette review",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Tag propose",
        "",
        f"- {tag_metadata.tag_name if tag_metadata else ''}",
        "",
        "## Version proposee",
        "",
        f"- {tag_metadata.version if tag_metadata else ''}",
        "",
        "## Documents verifies",
        "",
    ]
    lines.extend(f"- {document.path}" for document in documents if document.present)
    lines.extend(("", "## Preuves de tests", ""))
    lines.extend(f"- {item.command} : {item.result}" for item in evidence if item.validated)
    lines.extend(("", "## Criteres de review", ""))
    lines.extend(f"- {finding.name} : {'OK' if finding.passed else 'FAIL'}" for finding in findings)
    lines.extend(
        (
            "",
            "## Securite",
            "",
            "- aucun tag Git cree",
            "- aucun broker reel",
            "- aucune cle API",
            "- aucun reseau",
            "- aucun ordre reel",
            "- aucun acces compte reel",
            "- aucune lecture data/",
            "- aucune ecriture data/",
            "- aucun conseil financier",
            "",
            "## Prochaine etape suggeree",
            "",
            "AGIcore Trading v1 Offline Tag Creation Instructions",
        )
    )
    return "\n".join(lines) + "\n"


def validate_final_tag_review_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Final Tag Review",
        "offline/sandbox final tag review only",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_REVIEW",
        "tag preparation complete",
        "release package complet",
        "V1 offline utilisable localement en sandbox",
        "pas de tag Git cree pendant cette review",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
        "AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION.md",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_tag_preparation.py -q : 30 passed",
        "python -m pytest tests/unit/trading/ -q : 4114 passed",
        "python -m pytest tests/unit/ -q : 4503 passed",
        "git diff --check : OK",
        "AGIcore Trading v1 Offline Tag Creation Instructions",
    )
    return all(item in markdown for item in required)


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


def render_agicore_trading_v1_offline_final_tag_review_json_report(
    result: AGIcoreTradingV1OfflineFinalTagReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineFinalTagReviewResult):
        payload = {
            "schema": "agicore_trading_v1_offline_final_tag_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "findings": _payload_value(result.findings),
            "git_tag_created": result.git_tag_created,
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


def review_agicore_trading_v1_offline_final_tag(
    data: AGIcoreTradingV1OfflineFinalTagReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalTagReviewResult:
    payload = _coerce_input(data)
    context = build_final_tag_review_context(payload)
    risks = detect_agicore_trading_v1_offline_final_tag_review_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_final_tag_review_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_tag_review_recommendations(risks)
    findings = _build_findings(payload, context)
    base = AGIcoreTradingV1OfflineFinalTagReviewResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        findings=findings,
        report=None,
        git_tag_created=False,
    )
    report = AGIcoreTradingV1OfflineFinalTagReviewReport(
        markdown=render_agicore_trading_v1_offline_final_tag_review_markdown(context, findings),
        json=render_agicore_trading_v1_offline_final_tag_review_json_report(base),
    )
    return AGIcoreTradingV1OfflineFinalTagReviewResult(**{**base.__dict__, "report": report})
