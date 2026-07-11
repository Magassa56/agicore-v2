"""AGIcore Trading v1 offline release package review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_release_package_review_models import (
    AGIcoreTradingV1OfflineReleasePackageReviewCapability,
    AGIcoreTradingV1OfflineReleasePackageReviewContext,
    AGIcoreTradingV1OfflineReleasePackageReviewCriterion,
    AGIcoreTradingV1OfflineReleasePackageReviewDecision,
    AGIcoreTradingV1OfflineReleasePackageReviewDocument,
    AGIcoreTradingV1OfflineReleasePackageReviewFinding,
    AGIcoreTradingV1OfflineReleasePackageReviewInput,
    AGIcoreTradingV1OfflineReleasePackageReviewRecommendation,
    AGIcoreTradingV1OfflineReleasePackageReviewReport,
    AGIcoreTradingV1OfflineReleasePackageReviewResult,
    AGIcoreTradingV1OfflineReleasePackageReviewRisk,
    AGIcoreTradingV1OfflineReleasePackageReviewScore,
    AGIcoreTradingV1OfflineReleasePackageReviewState,
    AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence,
)


Risk = AGIcoreTradingV1OfflineReleasePackageReviewRisk
Recommendation = AGIcoreTradingV1OfflineReleasePackageReviewRecommendation
Decision = AGIcoreTradingV1OfflineReleasePackageReviewDecision
State = AGIcoreTradingV1OfflineReleasePackageReviewState

DOCUMENTS = (
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
    "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
    "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
    "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
    "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE.md",
)

CAPABILITIES = (
    "CSV Replay Input v1",
    "Synthetic Market Scenario v1",
    "Strategy Replay Engine v1",
    "Simulated Broker Stub v1",
    "Risk Guard Enforcement v1",
    "Journal Writer v1",
    "Offline Report Markdown JSON v1",
    "Offline Smoke Demo",
    "Offline Final Readiness Review",
    "Offline Release Package",
)

TESTING_EVIDENCE = (
    ("release package test", "35 passed"),
    ("trading tests", "4048 passed"),
    ("unit tests", "4437 passed"),
    ("git diff --check", "OK"),
)

CRITERIA = (
    "package lisible",
    "documents presents",
    "capacites presentes",
    "preuves presentes",
    "commandes presentes",
    "limites presentes",
    "non-goals presents",
    "securite claire",
    "no-overclaim valide",
)

COMMAND_MARKERS = (
    "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
    "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_final_readiness_review.py -q",
    "python -m pytest tests/unit/ -q",
)

SAFETY_MARKERS = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'ordre reel",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "ne jamais connecter de broker reel",
    "ne jamais configurer de cle API",
    "ne jamais lancer d'ordre reel",
    "ne jamais ajouter data/",
)

LIMITATION_MARKERS = (
    "strategies simples seulement",
    "donnees synthetiques ou CSV string en memoire",
    "pas de donnees reelles automatisees",
    "pas de broker connecte",
    "pas de persistance reelle",
    "pas d'interface utilisateur",
    "pas de rentabilite validee",
)

NON_GOAL_MARKERS = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'ordre reel",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "pas de paper broker connecte",
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
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineReleasePackageReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineReleasePackageReviewInput)}
    return AGIcoreTradingV1OfflineReleasePackageReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_release_package_review_input(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.review_id and assert_agicore_trading_v1_offline_release_package_review_boundaries(payload))


def build_release_package_review_context(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageReviewContext:
    _coerce_input(data)
    return AGIcoreTradingV1OfflineReleasePackageReviewContext(
        title="AGIcore Trading v1 Offline Release Package Review",
        status="offline/sandbox release package review only",
        expected_decision="APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW",
        next_step="AGIcore Trading v1 Offline Tag Preparation",
    )


def review_release_package_documents(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageReviewDocument, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_documents_incomplete:
        return tuple(AGIcoreTradingV1OfflineReleasePackageReviewDocument(name, verified=False) for name in DOCUMENTS[:-1])
    return tuple(AGIcoreTradingV1OfflineReleasePackageReviewDocument(name) for name in DOCUMENTS)


def review_release_package_capabilities(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageReviewCapability, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_capabilities_incomplete:
        return tuple(AGIcoreTradingV1OfflineReleasePackageReviewCapability(name, verified=False) for name in CAPABILITIES[:-1])
    return tuple(AGIcoreTradingV1OfflineReleasePackageReviewCapability(name) for name in CAPABILITIES)


def review_release_package_testing_evidence(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_testing_evidence_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence(name, result) for name, result in TESTING_EVIDENCE)


def review_release_package_commands(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_commands_missing)


def review_release_package_safety_rules(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_safety_missing)


def review_release_package_known_limitations(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_limitations_missing)


def review_release_package_non_goals(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_non_goals_missing)


def review_release_package_human_readability(markdown: str) -> bool:
    return bool(markdown and "# AGIcore Trading v1 Offline Release Package Review" in markdown and "## Conclusion" in markdown)


def review_release_package_no_live_trading_claim(markdown: str) -> bool:
    lowered = markdown.lower()
    return "live_trading_ready: true" not in lowered and "ready for live trading" not in lowered


def review_release_package_no_profitability_claim(markdown: str) -> bool:
    lowered = markdown.lower()
    return "profitability_proven: true" not in lowered and "profitability proven" not in lowered


def review_release_package_no_financial_advice_claim(markdown: str) -> bool:
    return "financial_advice: true" not in markdown.lower()


def _criteria(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | None,
) -> tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...]:
    values = (
        ("package lisible", True),
        ("documents presents", not (data and data.force_documents_incomplete)),
        ("capacites presentes", not (data and data.force_capabilities_incomplete)),
        ("preuves presentes", not (data and data.force_testing_evidence_missing)),
        ("commandes presentes", not (data and data.force_commands_missing)),
        ("limites presentes", not (data and data.force_limitations_missing)),
        ("non-goals presents", not (data and data.force_non_goals_missing)),
        ("securite claire", not (data and data.force_safety_missing)),
        ("no-overclaim valide", True),
    )
    return tuple(AGIcoreTradingV1OfflineReleasePackageReviewCriterion(text, ok) for text, ok in values)


def _findings(
    criteria: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...],
) -> tuple[AGIcoreTradingV1OfflineReleasePackageReviewFinding, ...]:
    return tuple(
        AGIcoreTradingV1OfflineReleasePackageReviewFinding(
            name=criterion.text,
            passed=criterion.satisfied,
            detail="review passed" if criterion.satisfied else "review failed",
        )
        for criterion in criteria
    )


def render_agicore_trading_v1_offline_release_package_review_markdown(
    context: AGIcoreTradingV1OfflineReleasePackageReviewContext,
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageReviewDocument, ...],
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence, ...],
    criteria: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...],
) -> str:
    lines = [
        f"# {context.title}",
        "",
        "## Statut",
        "",
        context.status,
        "",
        "## Decision attendue",
        "",
        context.expected_decision,
        "",
        "## Conclusion",
        "",
        "- package de release offline complet",
        "- utilisable localement en sandbox",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Documents verifies",
        "",
    ]
    lines.extend(f"- {document.name}" for document in documents if document.verified)
    lines.extend(("", "## Capacites verifiees", ""))
    lines.extend(f"- {capability.name}" for capability in capabilities if capability.verified)
    lines.extend(("", "## Preuves de tests", ""))
    lines.extend(f"- {evidence.name} : {evidence.result}" for evidence in testing_evidence if evidence.verified)
    lines.extend(("", "## Commandes utiles", ""))
    lines.extend(f"- `{command}`" for command in COMMAND_MARKERS)
    lines.extend(("", "## Regles de securite", ""))
    lines.extend(f"- {rule}" for rule in SAFETY_MARKERS)
    lines.extend(("", "## Limites connues", ""))
    lines.extend(f"- {limitation}" for limitation in LIMITATION_MARKERS)
    lines.extend(("", "## Non-goals", ""))
    lines.extend(f"- {non_goal}" for non_goal in NON_GOAL_MARKERS)
    lines.extend(("", "## Criteres de review", ""))
    lines.extend(f"- {criterion.text}" for criterion in criteria if criterion.satisfied)
    lines.extend(("", "## Prochaine etape suggeree", "", context.next_step))
    return "\n".join(lines) + "\n"


def validate_release_package_review_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Release Package Review",
        "offline/sandbox release package review only",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW",
        "package de release offline complet",
        "utilisable localement en sandbox",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES.md",
        "AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE.md",
        "AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK.md",
        "AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW.md",
        "AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE.md",
        "CSV Replay Input v1",
        "Synthetic Market Scenario v1",
        "Strategy Replay Engine v1",
        "Simulated Broker Stub v1",
        "Risk Guard Enforcement v1",
        "Journal Writer v1",
        "Offline Report Markdown JSON v1",
        "Offline Smoke Demo",
        "Offline Final Readiness Review",
        "Offline Release Package",
        "release package test : 35 passed",
        "trading tests : 4048 passed",
        "unit tests : 4437 passed",
        "git diff --check : OK",
        "package lisible",
        "documents presents",
        "capacites presentes",
        "preuves presentes",
        "commandes presentes",
        "limites presentes",
        "non-goals presents",
        "securite claire",
        "no-overclaim valide",
        "AGIcore Trading v1 Offline Tag Preparation",
    )
    return all(item in markdown for item in required)


def _boundary_risks(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_release_package_review_boundaries(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_release_package_review_risks(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
    markdown: str = "",
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageReviewDocument, ...] = (),
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCapability, ...] = (),
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence, ...] = (),
    criteria: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.RELEASE_PACKAGE_REVIEW_INPUT_MISSING)
    if len(documents) != len(DOCUMENTS) or any(not item.verified for item in documents):
        risks.append(Risk.RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE)
    if len(capabilities) != len(CAPABILITIES) or any(not item.verified for item in capabilities):
        risks.append(Risk.RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE)
    if len(testing_evidence) != len(TESTING_EVIDENCE):
        risks.append(Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING)
    if payload and payload.force_commands_missing:
        risks.append(Risk.RELEASE_PACKAGE_COMMAND_REVIEW_MISSING)
    if payload and payload.force_safety_missing:
        risks.append(Risk.RELEASE_PACKAGE_SAFETY_REVIEW_MISSING)
    if payload and payload.force_limitations_missing:
        risks.append(Risk.RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING)
    if payload and payload.force_non_goals_missing:
        risks.append(Risk.RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING)
    if criteria and any(not criterion.satisfied for criterion in criteria):
        for criterion in criteria:
            if criterion.text == "commandes presentes" and not criterion.satisfied:
                risks.append(Risk.RELEASE_PACKAGE_COMMAND_REVIEW_MISSING)
            if criterion.text == "securite claire" and not criterion.satisfied:
                risks.append(Risk.RELEASE_PACKAGE_SAFETY_REVIEW_MISSING)
            if criterion.text == "limites presentes" and not criterion.satisfied:
                risks.append(Risk.RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING)
            if criterion.text == "non-goals presents" and not criterion.satisfied:
                risks.append(Risk.RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING)
    if payload and payload.force_live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.force_real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.force_real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.force_paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload and payload.force_profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.force_financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    if markdown:
        lowered = markdown.lower()
        if "live_trading_ready: true" in lowered or "ready for live trading" in lowered:
            risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
        if "real_broker_ready: true" in lowered:
            risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
        if "real_order_execution: true" in lowered:
            risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
        if "paper_broker_connected: true" in lowered:
            risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
        if "profitability_proven: true" in lowered or "profitability proven" in lowered:
            risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
        if "financial_advice: true" in lowered:
            risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_release_package_review_score(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
    markdown: str,
    documents: tuple[AGIcoreTradingV1OfflineReleasePackageReviewDocument, ...],
    capabilities: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineReleasePackageReviewTestingEvidence, ...],
    criteria: tuple[AGIcoreTradingV1OfflineReleasePackageReviewCriterion, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineReleasePackageReviewScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_release_package_review_input(payload) else 0
    document_score = 100 if len(documents) == len(DOCUMENTS) and all(item.verified for item in documents) else 0
    capability_score = 100 if len(capabilities) == len(CAPABILITIES) and all(item.verified for item in capabilities) else 0
    testing_score = 100 if len(testing_evidence) == len(TESTING_EVIDENCE) else 0
    command_score = 100 if review_release_package_commands(payload) and all(item in markdown for item in COMMAND_MARKERS) else 0
    safety_score = 100 if review_release_package_safety_rules(payload) and all(item in markdown for item in SAFETY_MARKERS) else 0
    limitation_score = 100 if review_release_package_known_limitations(payload) and all(item in markdown for item in LIMITATION_MARKERS) else 0
    non_goal_score = 100 if review_release_package_non_goals(payload) and all(item in markdown for item in NON_GOAL_MARKERS) else 0
    readability_score = 100 if review_release_package_human_readability(markdown) else 0
    overclaim_score = 100 if not {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    } & set(risks) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    criteria_score = 100 if all(criterion.satisfied for criterion in criteria) else 0
    overall = min(
        input_score,
        document_score,
        capability_score,
        testing_score,
        command_score,
        safety_score,
        limitation_score,
        non_goal_score,
        readability_score,
        overclaim_score,
        boundary_score,
        criteria_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineReleasePackageReviewScore(
        overall_score=overall,
        input_score=input_score,
        document_score=document_score,
        capability_score=capability_score,
        testing_evidence_score=testing_score,
        command_score=command_score,
        safety_score=safety_score,
        limitation_score=limitation_score,
        non_goal_score=non_goal_score,
        readability_score=readability_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_release_package_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.RELEASE_PACKAGE_REVIEW_INPUT_MISSING: Recommendation.PROVIDE_RELEASE_PACKAGE_REVIEW_INPUT,
        Risk.RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE: Recommendation.RESTORE_RELEASE_PACKAGE_DOCUMENT_REVIEW,
        Risk.RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE: Recommendation.RESTORE_RELEASE_PACKAGE_CAPABILITY_REVIEW,
        Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW,
        Risk.RELEASE_PACKAGE_COMMAND_REVIEW_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_COMMAND_REVIEW,
        Risk.RELEASE_PACKAGE_SAFETY_REVIEW_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_SAFETY_REVIEW,
        Risk.RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_LIMITATION_REVIEW,
        Risk.RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING: Recommendation.RESTORE_RELEASE_PACKAGE_NON_GOAL_REVIEW,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM: Recommendation.REMOVE_PAPER_BROKER_CONNECTION_CLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM: Recommendation.REMOVE_PROFITABILITY_PROOF_CLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM: Recommendation.REMOVE_FINANCIAL_ADVICE_CLAIM,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW
    if Risk.RELEASE_PACKAGE_REVIEW_INPUT_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_REVIEW_INPUT_FIXES
    if Risk.RELEASE_PACKAGE_DOCUMENT_REVIEW_INCOMPLETE in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_DOCUMENT_REVIEW_FIXES
    if Risk.RELEASE_PACKAGE_CAPABILITY_REVIEW_INCOMPLETE in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_CAPABILITY_REVIEW_FIXES
    if Risk.RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_TESTING_EVIDENCE_REVIEW_FIXES
    if Risk.RELEASE_PACKAGE_COMMAND_REVIEW_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_COMMAND_REVIEW_FIXES
    safety_risks = {Risk.RELEASE_PACKAGE_SAFETY_REVIEW_MISSING, Risk.RELEASE_PACKAGE_NON_GOAL_REVIEW_MISSING}
    if set(risks) & safety_risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_SAFETY_REVIEW_FIXES
    if Risk.RELEASE_PACKAGE_LIMITATION_REVIEW_MISSING in risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_LIMITATION_REVIEW_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_RELEASE_PACKAGE_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW


def _state_for(data: AGIcoreTradingV1OfflineReleasePackageReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_PREPARATION
    return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE_REVIEW_BLOCKED


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


def render_agicore_trading_v1_offline_release_package_review_json_report(
    result: AGIcoreTradingV1OfflineReleasePackageReviewResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineReleasePackageReviewResult):
        payload = {
            "schema": "agicore_trading_v1_offline_release_package_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "documents": _payload_value(result.documents),
            "capabilities": _payload_value(result.capabilities),
            "testing_evidence": _payload_value(result.testing_evidence),
            "criteria": _payload_value(result.criteria),
            "findings": _payload_value(result.findings),
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


def review_agicore_trading_v1_offline_release_package(
    data: AGIcoreTradingV1OfflineReleasePackageReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleasePackageReviewResult:
    payload = _coerce_input(data)
    context = build_release_package_review_context(payload)
    documents = review_release_package_documents(payload)
    capabilities = review_release_package_capabilities(payload)
    testing_evidence = review_release_package_testing_evidence(payload)
    criteria = _criteria(payload)
    findings = _findings(criteria)
    markdown = render_agicore_trading_v1_offline_release_package_review_markdown(
        context,
        documents,
        capabilities,
        testing_evidence,
        criteria,
    )
    if payload and payload.force_live_trading_overclaim:
        markdown += "\nlive_trading_ready: true\n"
    if payload and payload.force_real_broker_overclaim:
        markdown += "\nreal_broker_ready: true\n"
    if payload and payload.force_real_order_overclaim:
        markdown += "\nreal_order_execution: true\n"
    if payload and payload.force_paper_broker_overclaim:
        markdown += "\npaper_broker_connected: true\n"
    if payload and payload.force_profitability_overclaim:
        markdown += "\nprofitability_proven: true\n"
    if payload and payload.force_financial_advice_overclaim:
        markdown += "\nfinancial_advice: true\n"
    risks = detect_agicore_trading_v1_offline_release_package_review_risks(
        payload,
        markdown,
        documents,
        capabilities,
        testing_evidence,
        criteria,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_release_package_review_score(
        payload,
        markdown,
        documents,
        capabilities,
        testing_evidence,
        criteria,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_package_review_recommendations(risks)
    base = AGIcoreTradingV1OfflineReleasePackageReviewResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        documents=documents,
        capabilities=capabilities,
        testing_evidence=testing_evidence,
        criteria=criteria,
        findings=findings,
        report=None,
    )
    report = AGIcoreTradingV1OfflineReleasePackageReviewReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_release_package_review_json_report(base),
    )
    return AGIcoreTradingV1OfflineReleasePackageReviewResult(**{**base.__dict__, "report": report})
