"""AGIcore Trading v1 offline manual tag creation approval."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_approval_models import (
    AGIcoreTradingV1OfflineManualTagCreationApprovalCommand,
    AGIcoreTradingV1OfflineManualTagCreationApprovalCondition,
    AGIcoreTradingV1OfflineManualTagCreationApprovalContext,
    AGIcoreTradingV1OfflineManualTagCreationApprovalCriterion,
    AGIcoreTradingV1OfflineManualTagCreationApprovalDecision,
    AGIcoreTradingV1OfflineManualTagCreationApprovalFinding,
    AGIcoreTradingV1OfflineManualTagCreationApprovalInput,
    AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite,
    AGIcoreTradingV1OfflineManualTagCreationApprovalRecommendation,
    AGIcoreTradingV1OfflineManualTagCreationApprovalReport,
    AGIcoreTradingV1OfflineManualTagCreationApprovalResult,
    AGIcoreTradingV1OfflineManualTagCreationApprovalRisk,
    AGIcoreTradingV1OfflineManualTagCreationApprovalScore,
    AGIcoreTradingV1OfflineManualTagCreationApprovalState,
    AGIcoreTradingV1OfflineManualTagCreationApprovalStopRule,
    AGIcoreTradingV1OfflineManualTagCreationApprovalTagMetadata,
)


Risk = AGIcoreTradingV1OfflineManualTagCreationApprovalRisk
Recommendation = AGIcoreTradingV1OfflineManualTagCreationApprovalRecommendation
Decision = AGIcoreTradingV1OfflineManualTagCreationApprovalDecision
State = AGIcoreTradingV1OfflineManualTagCreationApprovalState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"
EXPECTED_APPROVAL = "APPROVED_FOR_MANUAL_TAG_CREATION_LATER"

CONDITIONS = (
    "etre sur main",
    "main synchronise avec origin/main",
    "tests/unit verts",
    "git status --short retourne seulement ?? data/",
    "aucun fichier en staging",
    "aucun tag existant avec le meme nom",
    "confirmation humaine explicite de Bama",
)

DOCUMENTED_COMMANDS = (
    'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
    "git push origin agicore-trading-v1-offline",
)

STOP_RULES = (
    "STOP si tests rouges",
    "STOP si main nest pas synchronise",
    "STOP si git status contient autre chose que data/",
    "STOP si data/ est staged",
    "STOP si un tag du meme nom existe deja",
    "STOP si une commande tente de connecter broker/API/cle",
    "STOP si la release est presentee comme trading reel ou rentable",
)

CRITERIA = (
    "approbation documentaire finale",
    "prerequis approuves",
    "conditions presentes",
    "commandes documentees uniquement",
    "regles STOP presentes",
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
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationApprovalInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineManualTagCreationApprovalInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineManualTagCreationApprovalInput)}
    return AGIcoreTradingV1OfflineManualTagCreationApprovalInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_manual_tag_creation_approval_input(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.approval_id
        and review_manual_tag_creation_approval_no_git_tag_created(payload)
        and review_manual_tag_creation_approval_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_manual_tag_creation_approval_boundaries(payload)
    )


def build_manual_tag_creation_approval_context(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Human Tag Go/No-Go approuve", payload.human_tag_go_no_go_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Manual Tag Creation Final Checklist approuvee",
            payload.manual_tag_creation_final_checklist_approved,
        ),
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineManualTagCreationApprovalPrerequisite(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    conditions = tuple(
        AGIcoreTradingV1OfflineManualTagCreationApprovalCondition(item, payload.conditions_present)
        for item in CONDITIONS
    )
    commands = tuple(
        AGIcoreTradingV1OfflineManualTagCreationApprovalCommand(command, payload.commands_documentation_only)
        for command in DOCUMENTED_COMMANDS
    )
    stop_rules = tuple(
        AGIcoreTradingV1OfflineManualTagCreationApprovalStopRule(rule, payload.stop_rules_present)
        for rule in STOP_RULES
    )
    criteria = tuple(AGIcoreTradingV1OfflineManualTagCreationApprovalCriterion(name, True) for name in CRITERIA)
    return AGIcoreTradingV1OfflineManualTagCreationApprovalContext(
        approval_id=payload.approval_id,
        tag_metadata=AGIcoreTradingV1OfflineManualTagCreationApprovalTagMetadata(
            tag_name=payload.tag_name,
            version=payload.version,
        ),
        approval_decision=payload.approval_decision,
        prerequisites=prerequisites,
        conditions=conditions,
        commands=commands,
        stop_rules=stop_rules,
        criteria=criteria,
    )


def review_manual_tag_creation_approval_prerequisites(
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    prerequisites_complete = True if payload is None else payload.prerequisites_complete
    return bool(context and prerequisites_complete and context.prerequisites and all(item.approved for item in context.prerequisites))


def review_manual_tag_creation_approval_human_go_no_go(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.human_tag_go_no_go_approved)


def review_manual_tag_creation_approval_final_checklist(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.manual_tag_creation_final_checklist_approved)


def review_manual_tag_creation_approval_instructions_review(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_creation_instructions_review_approved)


def review_manual_tag_creation_approval_final_tag_review(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.final_tag_review_approved)


def review_manual_tag_creation_approval_release_package_review(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.release_package_review_approved)


def review_manual_tag_creation_approval_final_readiness_review(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.final_readiness_review_approved)


def review_manual_tag_creation_approval_tag_name(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_manual_tag_creation_approval_version(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_manual_tag_creation_approval_decision(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.approval_decision == EXPECTED_APPROVAL)


def review_manual_tag_creation_approval_required_conditions(
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
) -> bool:
    return bool(context and len(context.conditions) == len(CONDITIONS) and all(item.present for item in context.conditions))


def review_manual_tag_creation_approval_documented_commands_only(
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
) -> bool:
    return bool(context and len(context.commands) == len(DOCUMENTED_COMMANDS) and all(command.documentation_only for command in context.commands))


def review_manual_tag_creation_approval_stop_rules(
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(rule.present for rule in context.stop_rules))


def review_manual_tag_creation_approval_no_git_tag_created(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_manual_tag_creation_approval_no_git_tag_pushed(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_manual_tag_creation_approval_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_manual_tag_creation_approval_no_profitability_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_manual_tag_creation_approval_no_financial_advice_claim(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | None) -> bool:
    return bool(
        data
        and not data.live_trading_overclaim
        and not data.real_broker_overclaim
        and not data.real_order_overclaim
        and not data.paper_broker_overclaim
        and not data.profitability_overclaim
        and not data.financial_advice_overclaim
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_manual_tag_creation_approval_boundaries(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_manual_tag_creation_approval_risks(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.MANUAL_TAG_CREATION_APPROVAL_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_manual_tag_creation_approval_prerequisites(context, payload):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE)
    if not review_manual_tag_creation_approval_human_go_no_go(payload):
        risks.append(Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED)
    if not review_manual_tag_creation_approval_final_checklist(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED)
    if not review_manual_tag_creation_approval_instructions_review(payload):
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED)
    if not review_manual_tag_creation_approval_final_tag_review(payload):
        risks.append(Risk.FINAL_TAG_REVIEW_NOT_APPROVED)
    if not review_manual_tag_creation_approval_release_package_review(payload):
        risks.append(Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED)
    if not review_manual_tag_creation_approval_final_readiness_review(payload):
        risks.append(Risk.FINAL_READINESS_REVIEW_NOT_APPROVED)
    if not review_manual_tag_creation_approval_tag_name(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_INVALID)
    if not review_manual_tag_creation_approval_version(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_VERSION_INVALID)
    if not review_manual_tag_creation_approval_decision(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE)
    if not review_manual_tag_creation_approval_required_conditions(context):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_CONDITIONS_MISSING)
    if not review_manual_tag_creation_approval_documented_commands_only(context):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_manual_tag_creation_approval_stop_rules(context):
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_STOP_RULES_MISSING)
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


def compute_agicore_trading_v1_offline_manual_tag_creation_approval_score(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineManualTagCreationApprovalScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_manual_tag_creation_approval_input(payload) else 0
    prerequisite_score = 100 if review_manual_tag_creation_approval_prerequisites(context, payload) else 0
    tag_name_score = 100 if review_manual_tag_creation_approval_tag_name(payload) else 0
    version_score = 100 if review_manual_tag_creation_approval_version(payload) else 0
    decision_score = 100 if review_manual_tag_creation_approval_decision(payload) else 0
    condition_score = 100 if review_manual_tag_creation_approval_required_conditions(context) else 0
    command_score = 100 if review_manual_tag_creation_approval_documented_commands_only(context) else 0
    stop_rule_score = 100 if review_manual_tag_creation_approval_stop_rules(context) else 0
    no_tag_score = 100 if review_manual_tag_creation_approval_no_git_tag_created(payload) and review_manual_tag_creation_approval_no_git_tag_pushed(payload) else 0
    safety_score = 100 if _no_overclaims(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        prerequisite_score,
        tag_name_score,
        version_score,
        decision_score,
        condition_score,
        command_score,
        stop_rule_score,
        no_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineManualTagCreationApprovalScore(
        overall_score=overall,
        input_score=input_score,
        prerequisite_score=prerequisite_score,
        tag_name_score=tag_name_score,
        version_score=version_score,
        decision_score=decision_score,
        condition_score=condition_score,
        command_score=command_score,
        stop_rule_score=stop_rule_score,
        no_tag_score=no_tag_score,
        safety_score=safety_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_manual_tag_creation_approval_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.MANUAL_TAG_CREATION_APPROVAL_INPUT_MISSING: Recommendation.PROVIDE_MANUAL_TAG_CREATION_APPROVAL_INPUT,
        Risk.MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO_APPROVAL,
        Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST_APPROVAL,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW_APPROVAL,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW_APPROVAL,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW_APPROVAL,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW_APPROVAL,
        Risk.MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_INVALID: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME,
        Risk.MANUAL_TAG_CREATION_APPROVAL_VERSION_INVALID: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL_VERSION,
        Risk.MANUAL_TAG_CREATION_APPROVAL_CONDITIONS_MISSING: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL_CONDITIONS,
        Risk.MANUAL_TAG_CREATION_APPROVAL_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_MANUAL_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY,
        Risk.MANUAL_TAG_CREATION_APPROVAL_STOP_RULES_MISSING: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULES,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL
    if Risk.MANUAL_TAG_CREATION_APPROVAL_INPUT_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_INPUT_FIXES
    if (
        Risk.MANUAL_TAG_CREATION_APPROVAL_PREREQUISITES_INCOMPLETE in risks
        or Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED in risks
        or Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED in risks
        or Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED in risks
        or Risk.FINAL_TAG_REVIEW_NOT_APPROVED in risks
        or Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED in risks
        or Risk.FINAL_READINESS_REVIEW_NOT_APPROVED in risks
    ):
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_PREREQUISITE_FIXES
    if Risk.MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_TAG_NAME_FIXES
    if Risk.MANUAL_TAG_CREATION_APPROVAL_VERSION_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_VERSION_FIXES
    if Risk.MANUAL_TAG_CREATION_APPROVAL_CONDITIONS_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_CONDITION_FIXES
    if Risk.MANUAL_TAG_CREATION_APPROVAL_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_COMMAND_DOCUMENTATION_FIXES
    if Risk.MANUAL_TAG_CREATION_APPROVAL_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_STOP_RULE_FIXES
    return Decision.REQUIRE_MANUAL_TAG_CREATION_APPROVAL_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN
    return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL_BLOCKED


def _build_findings(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | None,
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
) -> tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalFinding, ...]:
    checks = (
        ("prerequisites", review_manual_tag_creation_approval_prerequisites(context, data), "prerequis approuves"),
        ("human go/no-go", review_manual_tag_creation_approval_human_go_no_go(data), "Human Tag Go/No-Go approuve"),
        ("final checklist", review_manual_tag_creation_approval_final_checklist(data), "final checklist approuvee"),
        ("instructions review", review_manual_tag_creation_approval_instructions_review(data), "instructions review approuvee"),
        ("final tag review", review_manual_tag_creation_approval_final_tag_review(data), "final tag review approuvee"),
        ("release package review", review_manual_tag_creation_approval_release_package_review(data), "release package review approuvee"),
        ("final readiness review", review_manual_tag_creation_approval_final_readiness_review(data), "final readiness review approuvee"),
        ("tag name", review_manual_tag_creation_approval_tag_name(data), EXPECTED_TAG_NAME),
        ("version", review_manual_tag_creation_approval_version(data), EXPECTED_VERSION),
        ("approval decision", review_manual_tag_creation_approval_decision(data), EXPECTED_APPROVAL),
        ("required conditions", review_manual_tag_creation_approval_required_conditions(context), "conditions presentes"),
        ("commands documentation only", review_manual_tag_creation_approval_documented_commands_only(context), "commandes non executees"),
        ("stop rules", review_manual_tag_creation_approval_stop_rules(context), "regles STOP presentes"),
        ("no git tag created", review_manual_tag_creation_approval_no_git_tag_created(data), "aucun tag Git cree"),
        ("no git tag pushed", review_manual_tag_creation_approval_no_git_tag_pushed(data), "aucun tag Git pousse"),
        ("no live trading claim", review_manual_tag_creation_approval_no_live_trading_claim(data), "pas pret pour trading reel"),
        ("no profitability claim", review_manual_tag_creation_approval_no_profitability_claim(data), "pas de preuve de rentabilite"),
        ("no financial advice", review_manual_tag_creation_approval_no_financial_advice_claim(data), "pas de conseil financier"),
    )
    return tuple(AGIcoreTradingV1OfflineManualTagCreationApprovalFinding(name, passed, detail) for name, passed, detail in checks)


def render_agicore_trading_v1_offline_manual_tag_creation_approval_markdown(
    context: AGIcoreTradingV1OfflineManualTagCreationApprovalContext | None,
    findings: tuple[AGIcoreTradingV1OfflineManualTagCreationApprovalFinding, ...] = (),
) -> str:
    metadata = context.tag_metadata if context else None
    prerequisites = context.prerequisites if context else ()
    conditions = context.conditions if context else ()
    commands = context.commands if context else ()
    stop_rules = context.stop_rules if context else ()
    lines = [
        "# AGIcore Trading v1 Offline Manual Tag Creation Approval",
        "",
        "## Statut",
        "",
        "approval only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL",
        "",
        "## Conclusion",
        "",
        "- approbation documentaire finale prete",
        "- Bama peut creer le tag manuellement plus tard seulement apres verification locale finale",
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
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}"))
    lines.extend(("", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Decision d'approbation", "", f"- {context.approval_decision if context else ''}"))
    lines.extend(("", "## Conditions obligatoires avant execution reelle future", ""))
    lines.extend(f"- {item.name}" for item in conditions if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {command.command}" for command in commands if command.documentation_only)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {rule.rule}" for rule in stop_rules if rule.present)
    if findings:
        lines.extend(("", "## Findings", ""))
        lines.extend(f"- {finding.name} : {'OK' if finding.passed else 'FAIL'}" for finding in findings)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Tag Creation Execution Plan"))
    return "\n".join(lines) + "\n"


def validate_manual_tag_creation_approval_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Manual Tag Creation Approval",
        "approval only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_APPROVAL",
        "approbation documentaire finale prete",
        "Bama peut creer le tag manuellement plus tard seulement apres verification locale finale",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "Human Tag Go/No-Go approuve",
        "Manual Tag Creation Final Checklist approuvee",
        "Tag Creation Instructions Review approuvee",
        "Final Tag Review approuvee",
        "Release Package Review approuvee",
        "Final Readiness Review approuvee",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        EXPECTED_APPROVAL,
        "etre sur main",
        "main synchronise avec origin/main",
        "tests/unit verts",
        "git status --short retourne seulement ?? data/",
        "aucun fichier en staging",
        "aucun tag existant avec le meme nom",
        "confirmation humaine explicite de Bama",
        'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
        "git push origin agicore-trading-v1-offline",
        "STOP si tests rouges",
        "STOP si main nest pas synchronise",
        "STOP si git status contient autre chose que data/",
        "STOP si data/ est staged",
        "STOP si un tag du meme nom existe deja",
        "STOP si une commande tente de connecter broker/API/cle",
        "STOP si la release est presentee comme trading reel ou rentable",
        "AGIcore Trading v1 Offline Tag Creation Execution Plan",
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


def render_agicore_trading_v1_offline_manual_tag_creation_approval_json_report(
    result: AGIcoreTradingV1OfflineManualTagCreationApprovalResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineManualTagCreationApprovalResult):
        payload = {
            "schema": "agicore_trading_v1_offline_manual_tag_creation_approval",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "findings": _payload_value(result.findings),
            "git_tag_created": result.git_tag_created,
            "git_tag_pushed": result.git_tag_pushed,
            "approval_decision": EXPECTED_APPROVAL,
            "commands_documented_only": True,
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


def evaluate_agicore_trading_v1_offline_manual_tag_creation_approval(
    data: AGIcoreTradingV1OfflineManualTagCreationApprovalInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationApprovalResult:
    payload = _coerce_input(data)
    context = build_manual_tag_creation_approval_context(payload)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_approval_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_approval_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_approval_recommendations(risks)
    findings = _build_findings(payload, context)
    base = AGIcoreTradingV1OfflineManualTagCreationApprovalResult(
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
    report = AGIcoreTradingV1OfflineManualTagCreationApprovalReport(
        markdown=render_agicore_trading_v1_offline_manual_tag_creation_approval_markdown(context, findings),
        json=render_agicore_trading_v1_offline_manual_tag_creation_approval_json_report(base),
    )
    return AGIcoreTradingV1OfflineManualTagCreationApprovalResult(**{**base.__dict__, "report": report})
