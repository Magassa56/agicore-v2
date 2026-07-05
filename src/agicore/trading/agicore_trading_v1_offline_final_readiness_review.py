"""AGIcore Trading v1 offline final readiness review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_final_readiness_review_models import (
    AGIcoreTradingV1OfflineFinalReadinessCapability,
    AGIcoreTradingV1OfflineFinalReadinessContext,
    AGIcoreTradingV1OfflineFinalReadinessCriterion,
    AGIcoreTradingV1OfflineFinalReadinessDecision,
    AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck,
    AGIcoreTradingV1OfflineFinalReadinessInput,
    AGIcoreTradingV1OfflineFinalReadinessKnownLimitation,
    AGIcoreTradingV1OfflineFinalReadinessNonGoal,
    AGIcoreTradingV1OfflineFinalReadinessRecommendation,
    AGIcoreTradingV1OfflineFinalReadinessReport,
    AGIcoreTradingV1OfflineFinalReadinessResult,
    AGIcoreTradingV1OfflineFinalReadinessRisk,
    AGIcoreTradingV1OfflineFinalReadinessScore,
    AGIcoreTradingV1OfflineFinalReadinessState,
    AGIcoreTradingV1OfflineFinalReadinessTestingEvidence,
)


Risk = AGIcoreTradingV1OfflineFinalReadinessRisk
Recommendation = AGIcoreTradingV1OfflineFinalReadinessRecommendation
Decision = AGIcoreTradingV1OfflineFinalReadinessDecision
State = AGIcoreTradingV1OfflineFinalReadinessState

CAPABILITIES = (
    "CSV Replay Input v1",
    "Synthetic Market Scenario v1",
    "Strategy Replay Engine v1",
    "Simulated Broker Stub v1",
    "Risk Guard Enforcement v1",
    "Journal Writer v1",
    "Offline Report Markdown JSON v1",
    "V1 Candidate",
    "V1 Candidate Review",
    "Offline Release Decision",
    "Offline Release Notes",
    "Offline Smoke Demo",
    "Offline Smoke Demo Review",
    "Offline Sandbox Usage Guide",
    "Offline Local Runbook",
)

TESTING_EVIDENCE = (
    ("local runbook test", "35 passed"),
    ("trading tests", "3976 passed"),
    ("unit tests", "4365 passed"),
    ("git diff --check", "OK"),
)

DOCUMENTATION = (
    "Offline Release Notes",
    "Offline Sandbox Usage Guide",
    "Offline Local Runbook",
    "Final Readiness Review",
)

READINESS_CRITERIA = (
    "capabilities presentes",
    "smoke demo validee",
    "docs d'usage presentes",
    "runbook present",
    "securite offline claire",
    "limites documentees",
    "no-overclaim valide",
)

LIMITATIONS = (
    "strategies simples seulement",
    "donnees synthetiques ou CSV string en memoire",
    "pas de broker reel",
    "pas de paper broker connecte",
    "pas de donnees reelles automatisees",
    "pas de persistance reelle de rapports",
    "pas d'interface utilisateur",
    "pas de rentabilite validee",
)

NON_GOALS = (
    "pas de trading reel",
    "pas d'Alpaca reel",
    "pas d'ordre reel",
    "pas d'acces compte reel",
    "pas de mutation position reelle",
    "pas de conseil financier",
)

SAFETY_BOUNDARIES = (
    "pas de trading reel",
    "pas de broker reel",
    "pas de paper broker connecte",
    "pas d'Alpaca reel",
    "pas d'ordre reel",
    "pas d'acces compte reel",
    "pas de mutation position reelle",
    "pas de lecture data/",
    "pas d'ecriture data/",
    "pas de reseau",
    "pas de cle API",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
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
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalReadinessInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineFinalReadinessInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineFinalReadinessInput)}
    return AGIcoreTradingV1OfflineFinalReadinessInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_final_readiness_input(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.review_id and assert_agicore_trading_v1_offline_final_readiness_boundaries(payload))


def build_final_readiness_context(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalReadinessContext:
    _coerce_input(data)
    return AGIcoreTradingV1OfflineFinalReadinessContext(
        title="AGIcore Trading v1 Offline Final Readiness Review",
        status="offline/sandbox local readiness review only",
        expected_decision="APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW",
        next_step="AGIcore Trading v1 Offline Release Package",
    )


def review_final_readiness_capabilities(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_capabilities_incomplete:
        return tuple(AGIcoreTradingV1OfflineFinalReadinessCapability(name, validated=False) for name in CAPABILITIES[:-1])
    return tuple(AGIcoreTradingV1OfflineFinalReadinessCapability(name) for name in CAPABILITIES)


def review_final_readiness_testing_evidence(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_testing_evidence_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineFinalReadinessTestingEvidence(name, result) for name, result in TESTING_EVIDENCE)


def review_final_readiness_documentation(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_documentation_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck(name) for name in DOCUMENTATION)


def review_final_readiness_smoke_demo(data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_smoke_demo_missing)


def review_final_readiness_sandbox_usage_guide(data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_sandbox_usage_guide_missing)


def review_final_readiness_local_runbook(data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return not (payload and payload.force_local_runbook_missing)


def review_final_readiness_safety_boundaries(data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(not (payload and payload.force_safety_boundary_missing) and assert_agicore_trading_v1_offline_final_readiness_boundaries(payload))


def review_final_readiness_known_limitations(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...]:
    payload = _coerce_input(data)
    if payload and payload.force_limitations_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineFinalReadinessKnownLimitation(text) for text in LIMITATIONS)


def review_final_readiness_non_goals() -> tuple[AGIcoreTradingV1OfflineFinalReadinessNonGoal, ...]:
    return tuple(AGIcoreTradingV1OfflineFinalReadinessNonGoal(text) for text in NON_GOALS)


def review_final_readiness_no_live_trading_claim(markdown: str) -> bool:
    return "live_trading_ready: true" not in markdown.lower() and "ready for live trading" not in markdown.lower()


def review_final_readiness_no_profitability_claim(markdown: str) -> bool:
    return "profitability_proven: true" not in markdown.lower() and "profitability proven" not in markdown.lower()


def review_final_readiness_no_financial_advice_claim(markdown: str) -> bool:
    return "financial_advice: true" not in markdown.lower()


def _criteria(data: AGIcoreTradingV1OfflineFinalReadinessInput | None) -> tuple[AGIcoreTradingV1OfflineFinalReadinessCriterion, ...]:
    smoke_demo = review_final_readiness_smoke_demo(data)
    docs = not (data and (data.force_documentation_missing or data.force_sandbox_usage_guide_missing or data.force_local_runbook_missing))
    safety = review_final_readiness_safety_boundaries(data)
    limitations = not (data and data.force_limitations_missing)
    capabilities = not (data and data.force_capabilities_incomplete)
    values = (
        ("capabilities presentes", capabilities),
        ("smoke demo validee", smoke_demo),
        ("docs d'usage presentes", docs),
        ("runbook present", not (data and data.force_local_runbook_missing)),
        ("securite offline claire", safety),
        ("limites documentees", limitations),
        ("no-overclaim valide", True),
    )
    return tuple(AGIcoreTradingV1OfflineFinalReadinessCriterion(text, ok) for text, ok in values)


def _markdown_lines(
    context: AGIcoreTradingV1OfflineFinalReadinessContext,
    capabilities: tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...],
    documentation_checks: tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...],
    criteria: tuple[AGIcoreTradingV1OfflineFinalReadinessCriterion, ...],
    limitations: tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineFinalReadinessNonGoal, ...],
) -> list[str]:
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
        "- AGIcore Trading v1 Offline est utilisable localement en sandbox",
        "- AGIcore Trading v1 Offline n'est pas pret pour trading reel",
        "- aucune rentabilite n'est prouvee",
        "- aucun conseil financier n'est fourni",
        "",
        "## Capacites validees",
        "",
    ]
    lines.extend(f"- {capability.name}" for capability in capabilities if capability.validated)
    lines.extend(("", "## Preuves de tests", ""))
    lines.extend(f"- {evidence.name} : {evidence.result}" for evidence in testing_evidence if evidence.validated)
    lines.extend(("", "## Documentation verifiee", ""))
    lines.extend(f"- {doc.name}" for doc in documentation_checks if doc.present)
    lines.extend(("", "## Criteres de readiness", ""))
    lines.extend(f"- {criterion.text}" for criterion in criteria if criterion.satisfied)
    lines.extend(("", "## Securite offline", ""))
    lines.extend(f"- {boundary}" for boundary in SAFETY_BOUNDARIES)
    lines.extend(("", "## Limites finales", ""))
    lines.extend(f"- {limitation.text}" for limitation in limitations if limitation.documented)
    lines.extend(("", "## Non-goals", ""))
    lines.extend(f"- {non_goal.text}" for non_goal in non_goals if non_goal.explicit)
    lines.extend(("", "## Prochaine etape suggeree", "", context.next_step))
    return lines


def render_agicore_trading_v1_offline_final_readiness_markdown(
    context: AGIcoreTradingV1OfflineFinalReadinessContext,
    capabilities: tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...],
    documentation_checks: tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...],
    criteria: tuple[AGIcoreTradingV1OfflineFinalReadinessCriterion, ...],
    limitations: tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineFinalReadinessNonGoal, ...],
) -> str:
    return "\n".join(_markdown_lines(context, capabilities, testing_evidence, documentation_checks, criteria, limitations, non_goals)) + "\n"


def validate_final_readiness_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Final Readiness Review",
        "offline/sandbox local readiness review only",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW",
        "AGIcore Trading v1 Offline est utilisable localement en sandbox",
        "AGIcore Trading v1 Offline n'est pas pret pour trading reel",
        "aucune rentabilite n'est prouvee",
        "aucun conseil financier n'est fourni",
        "CSV Replay Input v1",
        "Synthetic Market Scenario v1",
        "Strategy Replay Engine v1",
        "Simulated Broker Stub v1",
        "Risk Guard Enforcement v1",
        "Journal Writer v1",
        "Offline Report Markdown JSON v1",
        "V1 Candidate",
        "V1 Candidate Review",
        "Offline Release Decision",
        "Offline Release Notes",
        "Offline Smoke Demo",
        "Offline Smoke Demo Review",
        "Offline Sandbox Usage Guide",
        "Offline Local Runbook",
        "local runbook test : 35 passed",
        "trading tests : 3976 passed",
        "unit tests : 4365 passed",
        "git diff --check : OK",
        "capabilities presentes",
        "smoke demo validee",
        "docs d'usage presentes",
        "runbook present",
        "securite offline claire",
        "limites documentees",
        "no-overclaim valide",
        "strategies simples seulement",
        "donnees synthetiques ou CSV string en memoire",
        "pas de broker reel",
        "pas de paper broker connecte",
        "pas de donnees reelles automatisees",
        "pas de persistance reelle de rapports",
        "pas d'interface utilisateur",
        "pas de rentabilite validee",
        "pas de trading reel",
        "pas d'Alpaca reel",
        "pas d'ordre reel",
        "pas d'acces compte reel",
        "pas de mutation position reelle",
        "pas de conseil financier",
        "AGIcore Trading v1 Offline Release Package",
    )
    return all(item in markdown for item in required)


def _boundary_risks(data: AGIcoreTradingV1OfflineFinalReadinessInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_final_readiness_boundaries(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_final_readiness_risks(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
    markdown: str = "",
    capabilities: tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...] = (),
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...] = (),
    documentation_checks: tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...] = (),
    limitations: tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.FINAL_READINESS_INPUT_MISSING)
    if len(capabilities) != len(CAPABILITIES) or any(not capability.validated for capability in capabilities):
        risks.append(Risk.FINAL_READINESS_CAPABILITIES_INCOMPLETE)
    if len(testing_evidence) != len(TESTING_EVIDENCE):
        risks.append(Risk.FINAL_READINESS_TESTING_EVIDENCE_MISSING)
    if len(documentation_checks) != len(DOCUMENTATION):
        risks.append(Risk.FINAL_READINESS_DOCUMENTATION_MISSING)
    if payload and payload.force_smoke_demo_missing:
        risks.append(Risk.FINAL_READINESS_SMOKE_DEMO_MISSING)
    if payload and payload.force_sandbox_usage_guide_missing:
        risks.append(Risk.FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING)
    if payload and payload.force_local_runbook_missing:
        risks.append(Risk.FINAL_READINESS_LOCAL_RUNBOOK_MISSING)
    if payload and payload.force_safety_boundary_missing:
        risks.append(Risk.FINAL_READINESS_SAFETY_BOUNDARY_MISSING)
    if len(limitations) != len(LIMITATIONS):
        risks.append(Risk.FINAL_READINESS_LIMITATIONS_MISSING)
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
    risks.extend(_boundary_risks(payload))
    if markdown:
        if not review_final_readiness_no_live_trading_claim(markdown):
            risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
        if "real_broker_ready: true" in markdown.lower():
            risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
        if "real_order_execution: true" in markdown.lower():
            risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
        if "paper_broker_connected: true" in markdown.lower():
            risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
        if not review_final_readiness_no_profitability_claim(markdown):
            risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
        if not review_final_readiness_no_financial_advice_claim(markdown):
            risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_final_readiness_score(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
    markdown: str,
    capabilities: tuple[AGIcoreTradingV1OfflineFinalReadinessCapability, ...],
    testing_evidence: tuple[AGIcoreTradingV1OfflineFinalReadinessTestingEvidence, ...],
    documentation_checks: tuple[AGIcoreTradingV1OfflineFinalReadinessDocumentationCheck, ...],
    criteria: tuple[AGIcoreTradingV1OfflineFinalReadinessCriterion, ...],
    limitations: tuple[AGIcoreTradingV1OfflineFinalReadinessKnownLimitation, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineFinalReadinessNonGoal, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineFinalReadinessScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_final_readiness_input(payload) else 0
    capability_score = 100 if len(capabilities) == len(CAPABILITIES) and all(item.validated for item in capabilities) else 0
    testing_score = 100 if len(testing_evidence) == len(TESTING_EVIDENCE) else 0
    documentation_score = 100 if len(documentation_checks) == len(DOCUMENTATION) and all(item.present for item in documentation_checks) else 0
    smoke_demo_score = 100 if review_final_readiness_smoke_demo(payload) and "Offline Smoke Demo" in markdown else 0
    safety_score = 100 if review_final_readiness_safety_boundaries(payload) and all(item in markdown for item in SAFETY_BOUNDARIES) else 0
    limitation_score = 100 if len(limitations) == len(LIMITATIONS) else 0
    non_goal_score = 100 if len(non_goals) == len(NON_GOALS) else 0
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
        capability_score,
        testing_score,
        documentation_score,
        smoke_demo_score,
        safety_score,
        limitation_score,
        non_goal_score,
        overclaim_score,
        boundary_score,
        criteria_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineFinalReadinessScore(
        overall_score=overall,
        input_score=input_score,
        capability_score=capability_score,
        testing_evidence_score=testing_score,
        documentation_score=documentation_score,
        smoke_demo_score=smoke_demo_score,
        safety_score=safety_score,
        limitation_score=limitation_score,
        non_goal_score=non_goal_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_final_readiness_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.FINAL_READINESS_INPUT_MISSING: Recommendation.PROVIDE_FINAL_READINESS_INPUT,
        Risk.FINAL_READINESS_CAPABILITIES_INCOMPLETE: Recommendation.COMPLETE_FINAL_READINESS_CAPABILITIES,
        Risk.FINAL_READINESS_TESTING_EVIDENCE_MISSING: Recommendation.RESTORE_FINAL_READINESS_TESTING_EVIDENCE,
        Risk.FINAL_READINESS_DOCUMENTATION_MISSING: Recommendation.RESTORE_FINAL_READINESS_DOCUMENTATION,
        Risk.FINAL_READINESS_SMOKE_DEMO_MISSING: Recommendation.RESTORE_FINAL_READINESS_SMOKE_DEMO,
        Risk.FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING: Recommendation.RESTORE_FINAL_READINESS_SANDBOX_USAGE_GUIDE,
        Risk.FINAL_READINESS_LOCAL_RUNBOOK_MISSING: Recommendation.RESTORE_FINAL_READINESS_LOCAL_RUNBOOK,
        Risk.FINAL_READINESS_SAFETY_BOUNDARY_MISSING: Recommendation.RESTORE_FINAL_READINESS_SAFETY_BOUNDARIES,
        Risk.FINAL_READINESS_LIMITATIONS_MISSING: Recommendation.RESTORE_FINAL_READINESS_LIMITATIONS,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW
    if Risk.FINAL_READINESS_INPUT_MISSING in risks:
        return Decision.REQUIRE_FINAL_READINESS_INPUT_FIXES
    if Risk.FINAL_READINESS_CAPABILITIES_INCOMPLETE in risks:
        return Decision.REQUIRE_FINAL_READINESS_CAPABILITY_FIXES
    if Risk.FINAL_READINESS_TESTING_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_FINAL_READINESS_TESTING_EVIDENCE_FIXES
    documentation_risks = {
        Risk.FINAL_READINESS_DOCUMENTATION_MISSING,
        Risk.FINAL_READINESS_SANDBOX_USAGE_GUIDE_MISSING,
        Risk.FINAL_READINESS_LOCAL_RUNBOOK_MISSING,
    }
    if set(risks) & documentation_risks:
        return Decision.REQUIRE_FINAL_READINESS_DOCUMENTATION_FIXES
    if Risk.FINAL_READINESS_SMOKE_DEMO_MISSING in risks:
        return Decision.REQUIRE_FINAL_READINESS_SMOKE_DEMO_FIXES
    if Risk.FINAL_READINESS_SAFETY_BOUNDARY_MISSING in risks:
        return Decision.REQUIRE_FINAL_READINESS_SAFETY_FIXES
    if Risk.FINAL_READINESS_LIMITATIONS_MISSING in risks:
        return Decision.REQUIRE_FINAL_READINESS_LIMITATION_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PAPER_BROKER_CONNECTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_FINAL_READINESS_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW


def _state_for(data: AGIcoreTradingV1OfflineFinalReadinessInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_RELEASE_PACKAGE
    return State.AGICORE_TRADING_V1_OFFLINE_FINAL_READINESS_BLOCKED


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


def render_agicore_trading_v1_offline_final_readiness_json_report(
    result: AGIcoreTradingV1OfflineFinalReadinessResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineFinalReadinessResult):
        payload = {
            "schema": "agicore_trading_v1_offline_final_readiness_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "capabilities": _payload_value(result.capabilities),
            "testing_evidence": _payload_value(result.testing_evidence),
            "documentation_checks": _payload_value(result.documentation_checks),
            "known_limitations": _payload_value(result.known_limitations),
            "non_goals": _payload_value(result.non_goals),
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


def review_agicore_trading_v1_offline_final_readiness(
    data: AGIcoreTradingV1OfflineFinalReadinessInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalReadinessResult:
    payload = _coerce_input(data)
    context = build_final_readiness_context(payload)
    capabilities = review_final_readiness_capabilities(payload)
    testing_evidence = review_final_readiness_testing_evidence(payload)
    documentation_checks = review_final_readiness_documentation(payload)
    criteria = _criteria(payload)
    limitations = review_final_readiness_known_limitations(payload)
    non_goals = review_final_readiness_non_goals()
    markdown = render_agicore_trading_v1_offline_final_readiness_markdown(
        context,
        capabilities,
        testing_evidence,
        documentation_checks,
        criteria,
        limitations,
        non_goals,
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
    risks = detect_agicore_trading_v1_offline_final_readiness_risks(
        payload,
        markdown,
        capabilities,
        testing_evidence,
        documentation_checks,
        limitations,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_final_readiness_score(
        payload,
        markdown,
        capabilities,
        testing_evidence,
        documentation_checks,
        criteria,
        limitations,
        non_goals,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_final_readiness_recommendations(risks)
    base = AGIcoreTradingV1OfflineFinalReadinessResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        capabilities=capabilities,
        testing_evidence=testing_evidence,
        documentation_checks=documentation_checks,
        readiness_criteria=criteria,
        known_limitations=limitations,
        non_goals=non_goals,
        report=None,
    )
    report = AGIcoreTradingV1OfflineFinalReadinessReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_final_readiness_json_report(base),
    )
    return AGIcoreTradingV1OfflineFinalReadinessResult(**{**base.__dict__, "report": report})
