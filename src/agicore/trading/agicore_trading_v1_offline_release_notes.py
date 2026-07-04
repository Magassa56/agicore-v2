"""AGIcore Trading v1 offline release notes builder."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_release_decision import (
    evaluate_agicore_trading_v1_offline_release_decision,
)
from agicore.trading.agicore_trading_v1_offline_release_decision_models import (
    AGIcoreTradingV1OfflineReleaseDecisionDecision,
    AGIcoreTradingV1OfflineReleaseDecisionInput,
    AGIcoreTradingV1OfflineReleaseDecisionResult,
)
from agicore.trading.agicore_trading_v1_offline_release_notes_models import (
    AGIcoreTradingV1OfflineReleaseNotesCapability,
    AGIcoreTradingV1OfflineReleaseNotesContext,
    AGIcoreTradingV1OfflineReleaseNotesDecision,
    AGIcoreTradingV1OfflineReleaseNotesInput,
    AGIcoreTradingV1OfflineReleaseNotesKnownLimitation,
    AGIcoreTradingV1OfflineReleaseNotesNonGoal,
    AGIcoreTradingV1OfflineReleaseNotesRecommendation,
    AGIcoreTradingV1OfflineReleaseNotesReport,
    AGIcoreTradingV1OfflineReleaseNotesResult,
    AGIcoreTradingV1OfflineReleaseNotesRisk,
    AGIcoreTradingV1OfflineReleaseNotesScore,
    AGIcoreTradingV1OfflineReleaseNotesState,
    AGIcoreTradingV1OfflineReleaseNotesTestingEvidence,
    AGIcoreTradingV1OfflineReleaseNotesUsageGuidance,
)


Risk = AGIcoreTradingV1OfflineReleaseNotesRisk
Recommendation = AGIcoreTradingV1OfflineReleaseNotesRecommendation
Decision = AGIcoreTradingV1OfflineReleaseNotesDecision
State = AGIcoreTradingV1OfflineReleaseNotesState

CAPABILITY_NAMES = (
    "CSV Replay Input v1",
    "Synthetic Market Scenario v1",
    "Strategy Replay Engine v1",
    "Simulated Broker Stub v1",
    "Risk Guard Enforcement v1",
    "Journal Writer v1",
    "Offline Report Markdown JSON v1",
    "V1 Candidate",
    "V1 Candidate Review",
    "V1 Offline Release Decision",
)

NON_GOAL_TEXTS = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'Alpaca reel",
    "pas d'ordre reel",
    "pas d'acces compte reel",
    "pas de mutation position reelle",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
    "pas de market data reelle automatisee",
    "pas de lecture data/",
)

LIMITATION_TEXTS = (
    "strategies simples seulement",
    "donnees uniquement synthetiques ou CSV string en memoire",
    "pas encore de vraie persistance de rapports",
    "pas encore de vraie interface utilisateur",
    "pas encore de paper broker connecte",
    "pas encore de validation sur donnees de marche reelles",
    "pas encore de mesure de rentabilite robuste",
)

GUIDANCE_TEXTS = (
    "utiliser uniquement en local/offline",
    "utiliser uniquement en sandbox",
    "ne pas connecter a un broker reel",
    "ne pas utiliser pour prendre des decisions financieres reelles",
)

TESTING_EVIDENCE = (
    ("test release decision", "37 passed"),
    ("trading tests", "3795 passed"),
    ("unit tests", "4184 passed"),
    ("git diff --check", "OK"),
)


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    out: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return tuple(out)


def _coerce_input(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseNotesInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineReleaseNotesInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineReleaseNotesInput)}
    return AGIcoreTradingV1OfflineReleaseNotesInput(**{key: value for key, value in dict(data).items() if key in allowed})


def _release_decision_result(
    data: AGIcoreTradingV1OfflineReleaseNotesInput,
) -> AGIcoreTradingV1OfflineReleaseDecisionResult | None:
    if data.offline_release_decision_result is not None:
        return data.offline_release_decision_result
    if data.offline_release_decision_input is not None:
        return evaluate_agicore_trading_v1_offline_release_decision(data.offline_release_decision_input)
    return None


def validate_agicore_trading_v1_offline_release_notes_input(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and (payload.offline_release_decision_result is not None or payload.offline_release_decision_input is not None))


def build_offline_release_notes_context(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseNotesContext:
    return AGIcoreTradingV1OfflineReleaseNotesContext(
        title="AGIcore Trading v1 Offline Release Notes",
        status="offline/sandbox release only",
        decision="APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION",
        next_step="AGIcore Trading v1 Offline Smoke Demo",
    )


def _capabilities(data: AGIcoreTradingV1OfflineReleaseNotesInput | None) -> tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...]:
    if data and data.force_capabilities_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleaseNotesCapability(name) for name in CAPABILITY_NAMES)


def _non_goals(data: AGIcoreTradingV1OfflineReleaseNotesInput | None) -> tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...]:
    if data and data.force_non_goals_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleaseNotesNonGoal(text) for text in NON_GOAL_TEXTS)


def _testing(data: AGIcoreTradingV1OfflineReleaseNotesInput | None) -> tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...]:
    if data and data.force_testing_evidence_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleaseNotesTestingEvidence(label, result) for label, result in TESTING_EVIDENCE)


def _limitations(data: AGIcoreTradingV1OfflineReleaseNotesInput | None) -> tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...]:
    if data and data.force_limitations_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineReleaseNotesKnownLimitation(text) for text in LIMITATION_TEXTS)


def _guidance() -> tuple[AGIcoreTradingV1OfflineReleaseNotesUsageGuidance, ...]:
    return tuple(AGIcoreTradingV1OfflineReleaseNotesUsageGuidance(text) for text in GUIDANCE_TEXTS)


def build_offline_release_notes_capability_section(
    capabilities: tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...],
) -> str:
    lines = ["## Included Capabilities", ""]
    lines.extend(f"- {capability.name}" for capability in capabilities)
    return "\n".join(lines)


def build_offline_release_notes_non_goals_section(
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...],
) -> str:
    lines = ["## Explicit Non-Goals", ""]
    lines.extend(f"- {non_goal.text}" for non_goal in non_goals)
    return "\n".join(lines)


def build_offline_release_notes_testing_evidence_section(
    evidence: tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...],
) -> str:
    lines = ["## Testing Evidence", ""]
    lines.extend(f"- {item.label} : {item.result}" for item in evidence)
    return "\n".join(lines)


def build_offline_release_notes_known_limitations_section(
    limitations: tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...],
) -> str:
    lines = ["## Known Limitations", ""]
    lines.extend(f"- {limitation.text}" for limitation in limitations)
    return "\n".join(lines)


def build_offline_release_notes_usage_guidance_section(
    guidance: tuple[AGIcoreTradingV1OfflineReleaseNotesUsageGuidance, ...],
) -> str:
    lines = ["## Usage Guidance", ""]
    lines.extend(f"- {item.text}" for item in guidance)
    return "\n".join(lines)


def build_offline_release_notes_next_steps_section(context: AGIcoreTradingV1OfflineReleaseNotesContext) -> str:
    return f"## Next Suggested Step\n\n{context.next_step}"


def render_agicore_trading_v1_offline_release_notes_markdown(
    context: AGIcoreTradingV1OfflineReleaseNotesContext,
    capabilities: tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...],
    evidence: tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...],
    limitations: tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...],
    guidance: tuple[AGIcoreTradingV1OfflineReleaseNotesUsageGuidance, ...],
) -> str:
    sections = [
        f"# {context.title}",
        "## Status\n\n" + context.status,
        "## Decision\n\n" + context.decision,
        build_offline_release_notes_capability_section(capabilities),
        build_offline_release_notes_non_goals_section(non_goals),
        build_offline_release_notes_testing_evidence_section(evidence),
        build_offline_release_notes_known_limitations_section(limitations),
        build_offline_release_notes_usage_guidance_section(guidance),
        build_offline_release_notes_next_steps_section(context),
    ]
    return "\n\n".join(sections) + "\n"


def validate_offline_release_notes_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Release Notes",
        "offline/sandbox release only",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION",
        "CSV Replay Input v1",
        "V1 Offline Release Decision",
        "pas de trading reel",
        "test release decision : 37 passed",
        "unit tests : 4184 passed",
        "strategies simples seulement",
        "utiliser uniquement en local/offline",
        "AGIcore Trading v1 Offline Smoke Demo",
    )
    return all(item in markdown for item in required)


def validate_offline_release_notes_no_overclaims(markdown: str) -> bool:
    forbidden = (
        "live_trading_ready: true",
        "real_broker_ready: true",
        "real_orders_ready: true",
        "profitability_proven: true",
        "financial_advice: true",
        "ready for live trading",
        "profitability proven",
    )
    lower = markdown.lower()
    return all(item not in lower for item in forbidden)


def validate_offline_release_notes_safety_language(markdown: str) -> bool:
    required = (
        "offline/sandbox release only",
        "pas de trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "ne pas connecter a un broker reel",
    )
    return all(item in markdown for item in required)


def _boundary_risks(data: AGIcoreTradingV1OfflineReleaseNotesInput | None) -> tuple[Risk, ...]:
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


def detect_agicore_trading_v1_offline_release_notes_risks(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
    markdown: str = "",
    capabilities: tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...] = (),
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...] = (),
    evidence: tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...] = (),
    limitations: tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.OFFLINE_RELEASE_NOTES_INPUT_MISSING)
    if len(capabilities) != len(CAPABILITY_NAMES):
        risks.append(Risk.OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING)
    if len(non_goals) != len(NON_GOAL_TEXTS):
        risks.append(Risk.OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING)
    if len(evidence) != len(TESTING_EVIDENCE):
        risks.append(Risk.OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING)
    if len(limitations) != len(LIMITATION_TEXTS):
        risks.append(Risk.OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING)
    if markdown and not validate_offline_release_notes_safety_language(markdown):
        risks.append(Risk.OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING)
    if payload and payload.force_safety_language_missing:
        risks.append(Risk.OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING)
    if payload and payload.force_live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload and payload.force_real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload and payload.force_real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload and payload.force_profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload and payload.force_financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_release_notes_score(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
    markdown: str,
    capabilities: tuple[AGIcoreTradingV1OfflineReleaseNotesCapability, ...],
    non_goals: tuple[AGIcoreTradingV1OfflineReleaseNotesNonGoal, ...],
    evidence: tuple[AGIcoreTradingV1OfflineReleaseNotesTestingEvidence, ...],
    limitations: tuple[AGIcoreTradingV1OfflineReleaseNotesKnownLimitation, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineReleaseNotesScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_release_notes_input(payload) else 0
    capability_score = 100 if len(capabilities) == len(CAPABILITY_NAMES) else 0
    non_goal_score = 100 if len(non_goals) == len(NON_GOAL_TEXTS) else 0
    testing_score = 100 if len(evidence) == len(TESTING_EVIDENCE) and all(item.passed for item in evidence) else 0
    limitation_score = 100 if len(limitations) == len(LIMITATION_TEXTS) and all(item.documented for item in limitations) else 0
    safety_score = 100 if validate_offline_release_notes_safety_language(markdown) else 0
    overclaim_score = 100 if validate_offline_release_notes_no_overclaims(markdown) and not {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    } & set(risks) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        capability_score,
        non_goal_score,
        testing_score,
        limitation_score,
        safety_score,
        overclaim_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineReleaseNotesScore(
        overall_score=overall,
        input_score=input_score,
        capability_score=capability_score,
        non_goal_score=non_goal_score,
        testing_score=testing_score,
        limitation_score=limitation_score,
        safety_language_score=safety_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_release_notes_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.OFFLINE_RELEASE_NOTES_INPUT_MISSING: Recommendation.PROVIDE_OFFLINE_RELEASE_NOTES_INPUT,
        Risk.OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING: Recommendation.RESTORE_OFFLINE_RELEASE_NOTES_CAPABILITIES,
        Risk.OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING: Recommendation.RESTORE_OFFLINE_RELEASE_NOTES_NON_GOALS,
        Risk.OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING: Recommendation.RESTORE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE,
        Risk.OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING: Recommendation.RESTORE_OFFLINE_RELEASE_NOTES_LIMITATIONS,
        Risk.OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING: Recommendation.RESTORE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE,
        Risk.LIVE_TRADING_READINESS_OVERCLAIM: Recommendation.REMOVE_LIVE_TRADING_READINESS_CLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM: Recommendation.REMOVE_REAL_BROKER_READINESS_CLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM: Recommendation.REMOVE_REAL_ORDER_EXECUTION_CLAIM,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES
    if Risk.OFFLINE_RELEASE_NOTES_INPUT_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_INPUT_FIXES
    if Risk.OFFLINE_RELEASE_NOTES_CAPABILITIES_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_CAPABILITY_FIXES
    if Risk.OFFLINE_RELEASE_NOTES_NON_GOALS_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_NON_GOAL_FIXES
    if Risk.OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_TESTING_EVIDENCE_FIXES
    if Risk.OFFLINE_RELEASE_NOTES_LIMITATIONS_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_LIMITATION_FIXES
    if Risk.OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_MISSING in risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_SAFETY_LANGUAGE_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_OFFLINE_RELEASE_NOTES_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES


def _state_for(data: AGIcoreTradingV1OfflineReleaseNotesInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_SMOKE_DEMO
    return State.AGICORE_TRADING_V1_OFFLINE_RELEASE_NOTES_BLOCKED


def _payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): _payload_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_payload_value(item) for item in value]
    if isinstance(value, list):
        return [_payload_value(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload_value(item) for key, item in vars(value).items() if not key.startswith("_") and key != "offline_release_decision_result"}
    return str(value)


def render_agicore_trading_v1_offline_release_notes_json_report(
    result: AGIcoreTradingV1OfflineReleaseNotesResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineReleaseNotesResult):
        payload = {
            "schema": "agicore_trading_v1_offline_release_notes",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "capabilities": _payload_value(result.capabilities),
            "non_goals": _payload_value(result.non_goals),
            "testing_evidence": _payload_value(result.testing_evidence),
            "known_limitations": _payload_value(result.known_limitations),
            "usage_guidance": _payload_value(result.usage_guidance),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_orders_ready": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def assert_agicore_trading_v1_offline_release_notes_boundaries(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return not _boundary_risks(payload)


def build_agicore_trading_v1_offline_release_notes(
    data: AGIcoreTradingV1OfflineReleaseNotesInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineReleaseNotesResult:
    payload = _coerce_input(data)
    release_decision = _release_decision_result(payload) if payload else None
    context = build_offline_release_notes_context(payload)
    capabilities = _capabilities(payload)
    non_goals = _non_goals(payload)
    evidence = _testing(payload)
    limitations = _limitations(payload)
    guidance = () if payload and payload.force_safety_language_missing else _guidance()
    markdown = render_agicore_trading_v1_offline_release_notes_markdown(
        context,
        capabilities,
        non_goals,
        evidence,
        limitations,
        guidance,
    )
    if payload and payload.force_live_trading_overclaim:
        markdown += "\nlive_trading_ready: true\n"
    if payload and payload.force_real_broker_overclaim:
        markdown += "\nreal_broker_ready: true\n"
    if payload and payload.force_real_order_overclaim:
        markdown += "\nreal_orders_ready: true\n"
    if payload and payload.force_profitability_overclaim:
        markdown += "\nprofitability_proven: true\n"
    if payload and payload.force_financial_advice_overclaim:
        markdown += "\nfinancial_advice: true\n"
    risks = detect_agicore_trading_v1_offline_release_notes_risks(
        payload,
        markdown,
        capabilities,
        non_goals,
        evidence,
        limitations,
    )
    if release_decision is not None and release_decision.decision is not AGIcoreTradingV1OfflineReleaseDecisionDecision.APPROVE_AGICORE_TRADING_V1_OFFLINE_RELEASE_DECISION:
        risks = _dedupe((*risks, Risk.OFFLINE_RELEASE_NOTES_INPUT_MISSING))
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_release_notes_score(
        payload,
        markdown,
        capabilities,
        non_goals,
        evidence,
        limitations,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_release_notes_recommendations(risks)
    base = AGIcoreTradingV1OfflineReleaseNotesResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        capabilities=capabilities,
        non_goals=non_goals,
        testing_evidence=evidence,
        known_limitations=limitations,
        usage_guidance=guidance,
        report=None,
        offline_release_decision_result=release_decision,
    )
    report = AGIcoreTradingV1OfflineReleaseNotesReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_release_notes_json_report(base),
    )
    return AGIcoreTradingV1OfflineReleaseNotesResult(**{**base.__dict__, "report": report})
