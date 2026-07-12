"""AGIcore Trading v1 offline final manual tag authorization."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_final_manual_tag_authorization_models import (
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationState,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule,
    AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata,
)


Risk = AGIcoreTradingV1OfflineFinalManualTagAuthorizationRisk
Recommendation = AGIcoreTradingV1OfflineFinalManualTagAuthorizationRecommendation
Decision = AGIcoreTradingV1OfflineFinalManualTagAuthorizationDecision
State = AGIcoreTradingV1OfflineFinalManualTagAuthorizationState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

CONDITIONS = (
    "etre sur main",
    "main synchronise avec origin/main",
    "tests/unit verts",
    "git status --short retourne seulement ?? data/",
    "aucun fichier en staging",
    "data/ non staged",
    "tag inexistant localement",
    "tag inexistant sur origin",
    "confirmation humaine explicite de Bama",
)
COMMANDS = (
    "git switch main",
    "git fetch origin",
    "git pull origin main",
    "python -m pytest tests/unit/ -q",
    "git status --short",
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
    'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
    "git push origin agicore-trading-v1-offline",
)
STOP_RULES = (
    "STOP si tests rouges",
    "STOP si main nest pas synchronise",
    "STOP si git status contient autre chose que data/",
    "STOP si data/ est staged",
    "STOP si un fichier est staged",
    "STOP si le tag existe deja localement",
    "STOP si le tag existe deja sur origin",
    "STOP si une commande tente de connecter broker/API/cle",
    "STOP si une formulation presente la release comme trading reel",
    "STOP si une formulation presente la release comme rentable ou comme conseil financier",
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
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput)}
    return AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_final_manual_tag_authorization_input(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.authorization_id
        and review_final_manual_tag_authorization_no_git_tag_created(payload)
        and review_final_manual_tag_authorization_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_final_manual_tag_authorization_boundaries(payload)
    )


def build_final_manual_tag_authorization_context(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Tag Creation Execution Plan Review approuvee", payload.execution_plan_review_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Tag Creation Execution Plan approuve", payload.execution_plan_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Manual Tag Creation Approval approuvee", payload.manual_tag_creation_approval_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Manual Tag Creation Final Checklist approuvee", payload.manual_tag_creation_final_checklist_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Human Tag Go/No-Go approuve", payload.human_tag_go_no_go_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineFinalManualTagAuthorizationPrerequisite(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    return AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext(
        authorization_id=payload.authorization_id,
        tag_metadata=AGIcoreTradingV1OfflineFinalManualTagAuthorizationTagMetadata(
            payload.tag_name, payload.version
        ),
        prerequisites=prerequisites,
        conditions=tuple(
            AGIcoreTradingV1OfflineFinalManualTagAuthorizationCondition(name, payload.conditions_present)
            for name in CONDITIONS
        ),
        commands=tuple(
            AGIcoreTradingV1OfflineFinalManualTagAuthorizationCommand(command, payload.commands_documentation_only)
            for command in COMMANDS
        ),
        stop_rules=tuple(
            AGIcoreTradingV1OfflineFinalManualTagAuthorizationStopRule(rule, payload.stop_rules_present)
            for rule in STOP_RULES
        ),
    )


def review_final_manual_tag_authorization_prerequisites(
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    complete = True if payload is None else payload.prerequisites_complete
    return bool(context and complete and all(item.approved for item in context.prerequisites))


def review_final_manual_tag_authorization_execution_plan_review(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.execution_plan_review_approved)


def review_final_manual_tag_authorization_manual_approval(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.manual_tag_creation_approval_approved)


def review_final_manual_tag_authorization_final_checklist(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.manual_tag_creation_final_checklist_approved)


def review_final_manual_tag_authorization_human_go_no_go(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.human_tag_go_no_go_approved)


def review_final_manual_tag_authorization_tag_name(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_final_manual_tag_authorization_version(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_final_manual_tag_authorization_conditions(
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
) -> bool:
    return bool(context and len(context.conditions) == len(CONDITIONS) and all(item.present for item in context.conditions))


def review_final_manual_tag_authorization_documented_commands_only(
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
) -> bool:
    return bool(context and len(context.commands) == len(COMMANDS) and all(item.documentation_only for item in context.commands))


def review_final_manual_tag_authorization_stop_rules(
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(item.present for item in context.stop_rules))


def review_final_manual_tag_authorization_no_git_tag_created(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_final_manual_tag_authorization_no_git_tag_pushed(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_final_manual_tag_authorization_no_live_trading_claim(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_final_manual_tag_authorization_no_profitability_claim(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_final_manual_tag_authorization_no_financial_advice_claim(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def _boundary_risks(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_final_manual_tag_authorization_boundaries(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_final_manual_tag_authorization_risks(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_final_manual_tag_authorization_prerequisites(context, payload):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE)
    for flag, risk in (
        (payload.execution_plan_review_approved, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        (payload.execution_plan_approved, Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED),
        (payload.manual_tag_creation_approval_approved, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        (payload.manual_tag_creation_final_checklist_approved, Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED),
        (payload.human_tag_go_no_go_approved, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        (payload.tag_creation_instructions_review_approved, Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED),
        (payload.final_tag_review_approved, Risk.FINAL_TAG_REVIEW_NOT_APPROVED),
        (payload.release_package_review_approved, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        (payload.final_readiness_review_approved, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ):
        if not flag:
            risks.append(risk)
    if not review_final_manual_tag_authorization_tag_name(payload):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID)
    if not review_final_manual_tag_authorization_version(payload):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID)
    if not review_final_manual_tag_authorization_conditions(context):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING)
    if not review_final_manual_tag_authorization_documented_commands_only(context):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_final_manual_tag_authorization_stop_rules(context):
        risks.append(Risk.FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING)
    if payload.git_tag_already_created:
        risks.append(Risk.GIT_TAG_ALREADY_CREATED)
    if payload.git_tag_already_pushed:
        risks.append(Risk.GIT_TAG_ALREADY_PUSHED)
    for flag, risk in (
        (payload.live_trading_overclaim, Risk.LIVE_TRADING_READINESS_OVERCLAIM),
        (payload.real_broker_overclaim, Risk.REAL_BROKER_READINESS_OVERCLAIM),
        (payload.real_order_overclaim, Risk.REAL_ORDER_EXECUTION_OVERCLAIM),
        (payload.paper_broker_overclaim, Risk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        (payload.profitability_overclaim, Risk.PROFITABILITY_PROOF_OVERCLAIM),
        (payload.financial_advice_overclaim, Risk.FINANCIAL_ADVICE_OVERCLAIM),
    ):
        if flag:
            risks.append(risk)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def compute_agicore_trading_v1_offline_final_manual_tag_authorization_score(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore:
    payload = _coerce_input(data)
    values = (
        100 if validate_agicore_trading_v1_offline_final_manual_tag_authorization_input(payload) else 0,
        100 if review_final_manual_tag_authorization_prerequisites(context, payload) else 0,
        100 if review_final_manual_tag_authorization_tag_name(payload) else 0,
        100 if review_final_manual_tag_authorization_version(payload) else 0,
        100 if review_final_manual_tag_authorization_conditions(context) else 0,
        100 if review_final_manual_tag_authorization_documented_commands_only(context) else 0,
        100 if review_final_manual_tag_authorization_stop_rules(context) else 0,
        100 if review_final_manual_tag_authorization_no_git_tag_created(payload) and review_final_manual_tag_authorization_no_git_tag_pushed(payload) else 0,
        100 if _no_overclaims(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineFinalManualTagAuthorizationScore(overall, *values)


def generate_agicore_trading_v1_offline_final_manual_tag_authorization_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING: Recommendation.PROVIDE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW,
        Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL,
        Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_DOCUMENTATION_ONLY,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES,
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
    recs = [mapping[risk] for risk in risks if risk in mapping]
    if not recs:
        recs.append(Recommendation.PREPARE_MANUAL_TAG_CREATION_COMMAND_SHEET)
    return _dedupe(recs)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_MISSING in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_FIXES
    prerequisite_risks = {
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITES_INCOMPLETE,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED,
        Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED,
    }
    if any(risk in prerequisite_risks for risk in risks):
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_PREREQUISITE_FIXES
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_TAG_NAME_FIXES
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_INVALID in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_VERSION_FIXES
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_CONDITIONS_MISSING in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_CONDITION_FIXES
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_COMMAND_DOCUMENTATION_FIXES
    if Risk.FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_STOP_RULE_FIXES
    return Decision.REQUIRE_FINAL_MANUAL_TAG_AUTHORIZATION_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET
    return State.AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION_BLOCKED


def render_agicore_trading_v1_offline_final_manual_tag_authorization_markdown(
    context: AGIcoreTradingV1OfflineFinalManualTagAuthorizationContext | None,
) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Final Manual Tag Authorization",
        "",
        "## Statut",
        "",
        "final authorization only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION",
        "",
        "## Conclusion",
        "",
        "- autorisation documentaire finale prete",
        "- Bama peut creer le tag manuellement plus tard uniquement apres derniere verification locale",
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
    lines.extend(f"- {item.name}" for item in (context.prerequisites if context else ()) if item.approved)
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}", "", "## Decision finale humaine/documentaire", "", "- FINAL_AUTHORIZATION_FOR_MANUAL_TAG_CREATION_LATER", "", "## Conditions obligatoires avant creation reelle future", ""))
    lines.extend(f"- {item.name}" for item in (context.conditions if context else ()) if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {item.rule}" for item in (context.stop_rules if context else ()) if item.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet"))
    return "\n".join(lines) + "\n"


def validate_final_manual_tag_authorization_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Final Manual Tag Authorization",
        "final authorization only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION",
        "autorisation documentaire finale prete",
        "Bama peut creer le tag manuellement plus tard uniquement apres derniere verification locale",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "Tag Creation Execution Plan Review approuvee",
        "Tag Creation Execution Plan approuve",
        "Manual Tag Creation Approval approuvee",
        "Manual Tag Creation Final Checklist approuvee",
        "Human Tag Go/No-Go approuve",
        "Tag Creation Instructions Review approuvee",
        "Final Tag Review approuvee",
        "Release Package Review approuvee",
        "Final Readiness Review approuvee",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "FINAL_AUTHORIZATION_FOR_MANUAL_TAG_CREATION_LATER",
        *CONDITIONS,
        *COMMANDS,
        *STOP_RULES,
        "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet",
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


def render_agicore_trading_v1_offline_final_manual_tag_authorization_json_report(
    result: AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult):
        payload = {
            "schema": "agicore_trading_v1_offline_final_manual_tag_authorization",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "git_tag_created": result.git_tag_created,
            "git_tag_pushed": result.git_tag_pushed,
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


def evaluate_agicore_trading_v1_offline_final_manual_tag_authorization(
    data: AGIcoreTradingV1OfflineFinalManualTagAuthorizationInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult:
    payload = _coerce_input(data)
    context = build_final_manual_tag_authorization_context(payload)
    risks = detect_agicore_trading_v1_offline_final_manual_tag_authorization_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_final_manual_tag_authorization_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_manual_tag_authorization_recommendations(risks)
    base = AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        report=None,
        git_tag_created=False,
        git_tag_pushed=False,
    )
    report = AGIcoreTradingV1OfflineFinalManualTagAuthorizationReport(
        markdown=render_agicore_trading_v1_offline_final_manual_tag_authorization_markdown(context),
        json=render_agicore_trading_v1_offline_final_manual_tag_authorization_json_report(base),
    )
    return AGIcoreTradingV1OfflineFinalManualTagAuthorizationResult(**{**base.__dict__, "report": report})
