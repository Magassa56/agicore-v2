"""AGIcore Trading v1 offline human tag go/no-go decision."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_human_tag_go_no_go_models import (
    AGIcoreTradingV1OfflineHumanTagGoNoGoContext,
    AGIcoreTradingV1OfflineHumanTagGoNoGoCriterion,
    AGIcoreTradingV1OfflineHumanTagGoNoGoDecision,
    AGIcoreTradingV1OfflineHumanTagGoNoGoFinding,
    AGIcoreTradingV1OfflineHumanTagGoNoGoGuardrail,
    AGIcoreTradingV1OfflineHumanTagGoNoGoInput,
    AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite,
    AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation,
    AGIcoreTradingV1OfflineHumanTagGoNoGoReport,
    AGIcoreTradingV1OfflineHumanTagGoNoGoResult,
    AGIcoreTradingV1OfflineHumanTagGoNoGoRisk,
    AGIcoreTradingV1OfflineHumanTagGoNoGoScore,
    AGIcoreTradingV1OfflineHumanTagGoNoGoState,
    AGIcoreTradingV1OfflineHumanTagGoNoGoTagMetadata,
)


Risk = AGIcoreTradingV1OfflineHumanTagGoNoGoRisk
Recommendation = AGIcoreTradingV1OfflineHumanTagGoNoGoRecommendation
Decision = AGIcoreTradingV1OfflineHumanTagGoNoGoDecision
State = AGIcoreTradingV1OfflineHumanTagGoNoGoState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"
EXPECTED_HUMAN_DECISION = "GO_FOR_MANUAL_TAG_CREATION_LATER"

GUARDRAILS = (
    "ne pas creer le tag si tests rouges",
    "ne pas creer le tag si main nest pas synchronise",
    "ne pas creer le tag si git status contient autre chose que data/",
    "ne jamais ajouter data/",
    "ne jamais faire git add .",
    "ne jamais connecter broker/API/cle",
    "ne jamais presenter la V1 comme trading reel",
)

CRITERIA = (
    "prerequis approuves",
    "tag name coherent",
    "version coherente",
    "decision humaine GO documentaire",
    "garde-fous presents",
    "aucun tag Git cree",
    "aucun tag Git pousse",
    "no-overclaim valide",
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
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineHumanTagGoNoGoInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineHumanTagGoNoGoInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineHumanTagGoNoGoInput)}
    return AGIcoreTradingV1OfflineHumanTagGoNoGoInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_human_tag_go_no_go_input(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.decision_id
        and review_human_tag_no_git_tag_created(payload)
        and review_human_tag_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_human_tag_go_no_go_boundaries(payload)
    )


def build_human_tag_go_no_go_context(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite(
            "Tag Creation Instructions approuvees", payload.tag_creation_instructions_approved
        ),
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite("Release Package approuve", payload.release_package_approved),
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineHumanTagGoNoGoPrerequisite(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    guardrails = tuple(
        AGIcoreTradingV1OfflineHumanTagGoNoGoGuardrail(name, payload.guardrails_present) for name in GUARDRAILS
    )
    criteria = tuple(AGIcoreTradingV1OfflineHumanTagGoNoGoCriterion(name, True) for name in CRITERIA)
    return AGIcoreTradingV1OfflineHumanTagGoNoGoContext(
        decision_id=payload.decision_id,
        tag_metadata=AGIcoreTradingV1OfflineHumanTagGoNoGoTagMetadata(
            tag_name=payload.tag_name,
            version=payload.version,
            human_decision=payload.human_go_decision,
        ),
        prerequisites=prerequisites,
        guardrails=guardrails,
        criteria=criteria,
    )


def review_human_tag_prerequisites(
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None,
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    prerequisites_complete = True if payload is None else payload.prerequisites_complete
    return bool(context and prerequisites_complete and context.prerequisites and all(item.approved for item in context.prerequisites))


def review_human_tag_final_tag_review(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.final_tag_review_approved)


def review_human_tag_creation_instructions_review(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_creation_instructions_review_approved)


def review_human_tag_release_package_review(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.release_package_review_approved)


def review_human_tag_final_readiness_review(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.final_readiness_review_approved)


def review_human_tag_name(data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_human_tag_version(data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_human_tag_go_decision(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.human_go_decision == EXPECTED_HUMAN_DECISION)


def review_human_tag_guardrails(context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None) -> bool:
    return bool(context and len(context.guardrails) == len(GUARDRAILS) and all(guardrail.present for guardrail in context.guardrails))


def review_human_tag_no_git_tag_created(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_human_tag_no_git_tag_pushed(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_human_tag_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_human_tag_no_profitability_claim(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_human_tag_no_financial_advice_claim(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | None) -> bool:
    return bool(
        data
        and not data.live_trading_overclaim
        and not data.real_broker_overclaim
        and not data.real_order_overclaim
        and not data.paper_broker_overclaim
        and not data.profitability_overclaim
        and not data.financial_advice_overclaim
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_human_tag_go_no_go_boundaries(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_human_tag_go_no_go_risks(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.HUMAN_TAG_GO_NO_GO_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_human_tag_prerequisites(context, payload):
        risks.append(Risk.HUMAN_TAG_PREREQUISITES_INCOMPLETE)
    if not review_human_tag_final_tag_review(payload):
        risks.append(Risk.FINAL_TAG_REVIEW_NOT_APPROVED)
    if not review_human_tag_creation_instructions_review(payload):
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED)
    if not review_human_tag_release_package_review(payload):
        risks.append(Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED)
    if not review_human_tag_final_readiness_review(payload):
        risks.append(Risk.FINAL_READINESS_REVIEW_NOT_APPROVED)
    if not review_human_tag_name(payload):
        risks.append(Risk.HUMAN_TAG_NAME_INVALID)
    if not review_human_tag_version(payload):
        risks.append(Risk.HUMAN_TAG_VERSION_INVALID)
    if not review_human_tag_go_decision(payload):
        risks.append(Risk.HUMAN_TAG_PREREQUISITES_INCOMPLETE)
    if not review_human_tag_guardrails(context):
        risks.append(Risk.HUMAN_TAG_GUARDRAILS_MISSING)
    if payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload.git_tag_already_pushed:
        risks.append(Risk.GIT_TAG_ALREADY_PUSHED)
    if payload.live_trading_overclaim:
        risks.append(Risk.LIVE_TRADING_READINESS_OVERCLAIM)
    if payload.real_broker_overclaim:
        risks.append(Risk.REAL_BROKER_READINESS_OVERCLAIM)
    if payload.real_order_overclaim:
        risks.append(Risk.REAL_ORDER_EXECUTION_OVERCLAIM)
    if payload.paper_broker_overclaim:
        risks.append(Risk.PAPER_BROKER_CONNECTION_OVERCLAIM)
    if payload.profitability_overclaim:
        risks.append(Risk.PROFITABILITY_PROOF_OVERCLAIM)
    if payload.financial_advice_overclaim:
        risks.append(Risk.FINANCIAL_ADVICE_OVERCLAIM)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_human_tag_go_no_go_score(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineHumanTagGoNoGoScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_human_tag_go_no_go_input(payload) else 0
    prerequisite_score = 100 if review_human_tag_prerequisites(context, payload) else 0
    tag_name_score = 100 if review_human_tag_name(payload) else 0
    version_score = 100 if review_human_tag_version(payload) else 0
    go_decision_score = 100 if review_human_tag_go_decision(payload) else 0
    guardrail_score = 100 if review_human_tag_guardrails(context) else 0
    no_tag_score = 100 if review_human_tag_no_git_tag_created(payload) and review_human_tag_no_git_tag_pushed(payload) else 0
    safety_score = 100 if _no_overclaims(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        prerequisite_score,
        tag_name_score,
        version_score,
        go_decision_score,
        guardrail_score,
        no_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineHumanTagGoNoGoScore(
        overall_score=overall,
        input_score=input_score,
        prerequisite_score=prerequisite_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        go_decision_score=go_decision_score,
        guardrail_score=guardrail_score,
        no_tag_score=no_tag_score,
        safety_score=safety_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_human_tag_go_no_go_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.HUMAN_TAG_GO_NO_GO_INPUT_MISSING: Recommendation.PROVIDE_HUMAN_TAG_GO_NO_GO_INPUT,
        Risk.HUMAN_TAG_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_HUMAN_TAG_PREREQUISITES,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW_APPROVAL,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW_APPROVAL,
        Risk.HUMAN_TAG_NAME_INVALID: Recommendation.RESTORE_HUMAN_TAG_NAME,
        Risk.HUMAN_TAG_VERSION_INVALID: Recommendation.RESTORE_HUMAN_TAG_VERSION,
        Risk.HUMAN_TAG_GUARDRAILS_MISSING: Recommendation.RESTORE_HUMAN_TAG_GUARDRAILS,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE,
        Risk.GIT_TAG_ALREADY_PUSHED: Recommendation.DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO
    if Risk.HUMAN_TAG_GO_NO_GO_INPUT_MISSING in risks:
        return Decision.REQUIRE_HUMAN_TAG_INPUT_FIXES
    if (
        Risk.HUMAN_TAG_PREREQUISITES_INCOMPLETE in risks
        or Risk.FINAL_TAG_REVIEW_NOT_APPROVED in risks
        or Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED in risks
        or Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED in risks
        or Risk.FINAL_READINESS_REVIEW_NOT_APPROVED in risks
    ):
        return Decision.REQUIRE_HUMAN_TAG_PREREQUISITE_FIXES
    if Risk.HUMAN_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_HUMAN_TAG_NAME_FIXES
    if Risk.HUMAN_TAG_VERSION_INVALID in risks:
        return Decision.REQUIRE_HUMAN_TAG_VERSION_FIXES
    if Risk.HUMAN_TAG_GUARDRAILS_MISSING in risks:
        return Decision.REQUIRE_HUMAN_TAG_GUARDRAIL_FIXES
    return Decision.REQUIRE_HUMAN_TAG_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_FINAL_CHECKLIST
    return State.AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO_BLOCKED


def _build_findings(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | None,
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None,
) -> tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoFinding, ...]:
    checks = (
        ("prerequisites", review_human_tag_prerequisites(context, data), "toutes les etapes precedentes sont approuvees"),
        ("final tag review", review_human_tag_final_tag_review(data), "Final Tag Review approuvee"),
        ("tag creation instructions review", review_human_tag_creation_instructions_review(data), "instructions review approuvee"),
        ("release package review", review_human_tag_release_package_review(data), "release package review approuvee"),
        ("final readiness review", review_human_tag_final_readiness_review(data), "final readiness review approuvee"),
        ("tag name", review_human_tag_name(data), EXPECTED_TAG_NAME),
        ("version", review_human_tag_version(data), EXPECTED_VERSION),
        ("human go decision", review_human_tag_go_decision(data), EXPECTED_HUMAN_DECISION),
        ("guardrails", review_human_tag_guardrails(context), "garde-fous humains presents"),
        ("no git tag created", review_human_tag_no_git_tag_created(data), "aucun tag Git cree"),
        ("no git tag pushed", review_human_tag_no_git_tag_pushed(data), "aucun tag Git pousse"),
        ("no live trading claim", review_human_tag_no_live_trading_claim(data), "pas pret pour trading reel"),
        ("no profitability claim", review_human_tag_no_profitability_claim(data), "pas de preuve de rentabilite"),
        ("no financial advice", review_human_tag_no_financial_advice_claim(data), "pas de conseil financier"),
    )
    return tuple(AGIcoreTradingV1OfflineHumanTagGoNoGoFinding(name, passed, detail) for name, passed, detail in checks)


def render_agicore_trading_v1_offline_human_tag_go_no_go_markdown(
    context: AGIcoreTradingV1OfflineHumanTagGoNoGoContext | None,
    findings: tuple[AGIcoreTradingV1OfflineHumanTagGoNoGoFinding, ...],
) -> str:
    metadata = context.tag_metadata if context else None
    prerequisites = context.prerequisites if context else ()
    guardrails = context.guardrails if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Human Tag Go/No-Go",
        "",
        "## Statut",
        "",
        "human decision only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO",
        "",
        "## Conclusion",
        "",
        "- GO documentaire pour creation manuelle future du tag",
        "- aucun tag Git cree dans cette phase",
        "- aucun tag Git pousse dans cette phase",
        "- AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Prerequis valides",
        "",
    ]
    lines.extend(f"- {item.name}" for item in prerequisites if item.approved)
    lines.extend(
        (
            "",
            "## Tag propose",
            "",
            f"- {metadata.tag_name if metadata else ''}",
            "",
            "## Version proposee",
            "",
            f"- {metadata.version if metadata else ''}",
            "",
            "## Decision humaine",
            "",
            f"- {metadata.human_decision if metadata else ''}",
            "",
            "## Garde-fous",
            "",
        )
    )
    lines.extend(f"- {guardrail.name}" for guardrail in guardrails if guardrail.present)
    lines.extend(("", "## Findings", ""))
    lines.extend(f"- {finding.name} : {'OK' if finding.passed else 'FAIL'}" for finding in findings)
    lines.extend(
        (
            "",
            "## Prochaine etape suggeree",
            "",
            "AGIcore Trading v1 Offline Manual Tag Creation Final Checklist",
        )
    )
    return "\n".join(lines) + "\n"


def validate_human_tag_go_no_go_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Human Tag Go/No-Go",
        "human decision only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_HUMAN_TAG_GO_NO_GO",
        "GO documentaire pour creation manuelle future du tag",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "Final Tag Review approuvee",
        "Tag Creation Instructions approuvees",
        "Tag Creation Instructions Review approuvee",
        "Release Package approuve",
        "Release Package Review approuvee",
        "Final Readiness Review approuvee",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        EXPECTED_HUMAN_DECISION,
        "ne pas creer le tag si tests rouges",
        "ne pas creer le tag si main nest pas synchronise",
        "ne pas creer le tag si git status contient autre chose que data/",
        "ne jamais ajouter data/",
        "ne jamais faire git add .",
        "ne jamais connecter broker/API/cle",
        "ne jamais presenter la V1 comme trading reel",
        "AGIcore Trading v1 Offline Manual Tag Creation Final Checklist",
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


def render_agicore_trading_v1_offline_human_tag_go_no_go_json_report(
    result: AGIcoreTradingV1OfflineHumanTagGoNoGoResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineHumanTagGoNoGoResult):
        payload = {
            "schema": "agicore_trading_v1_offline_human_tag_go_no_go",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "findings": _payload_value(result.findings),
            "git_tag_created": result.git_tag_created,
            "git_tag_pushed": result.git_tag_pushed,
            "human_decision": EXPECTED_HUMAN_DECISION,
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


def evaluate_agicore_trading_v1_offline_human_tag_go_no_go(
    data: AGIcoreTradingV1OfflineHumanTagGoNoGoInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineHumanTagGoNoGoResult:
    payload = _coerce_input(data)
    context = build_human_tag_go_no_go_context(payload)
    risks = detect_agicore_trading_v1_offline_human_tag_go_no_go_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_human_tag_go_no_go_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_human_tag_go_no_go_recommendations(risks)
    findings = _build_findings(payload, context)
    base = AGIcoreTradingV1OfflineHumanTagGoNoGoResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        findings=findings,
        report=None,
        git_tag_created=False,
        git_tag_pushed=False,
    )
    report = AGIcoreTradingV1OfflineHumanTagGoNoGoReport(
        markdown=render_agicore_trading_v1_offline_human_tag_go_no_go_markdown(context, findings),
        json=render_agicore_trading_v1_offline_human_tag_go_no_go_json_report(base),
    )
    return AGIcoreTradingV1OfflineHumanTagGoNoGoResult(**{**base.__dict__, "report": report})
