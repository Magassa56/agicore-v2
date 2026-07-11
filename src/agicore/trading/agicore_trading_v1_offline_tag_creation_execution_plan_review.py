"""AGIcore Trading v1 offline tag creation execution plan review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan_review_models import (
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCommand,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCriterion,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRecommendation,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewReport,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewScore,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewStopRule,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewTagMetadata,
)


Risk = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRisk
Recommendation = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewRecommendation
Decision = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewDecision
State = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

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
LOCAL_CHECKS = (
    "main synchronise",
    "tests unitaires complets",
    "git status propre hors data/",
    "aucun fichier staged",
    "data/ jamais ajoute",
)
REMOTE_CHECKS = ("verification tag local", "verification tag remote")
PLAN_CHECKS = (
    *LOCAL_CHECKS,
    *REMOTE_CHECKS,
    "creation manuelle du tag seulement apres validation",
    "push manuel du tag seulement apres creation locale validee",
)
STOP_RULES = (
    "STOP si tests rouges",
    "STOP si main nest pas synchronise",
    "STOP si git status contient autre chose que data/",
    "STOP si data/ est staged",
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
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput)}
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_tag_creation_execution_plan_review_input(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.review_id
        and review_tag_creation_execution_plan_review_no_git_tag_created(payload)
        and review_tag_creation_execution_plan_review_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_tag_creation_execution_plan_review_boundaries(payload)
    )


def build_tag_creation_execution_plan_review_context(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Tag Creation Execution Plan approuve", payload.execution_plan_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Manual Tag Creation Approval approuvee", payload.manual_tag_creation_approval_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Manual Tag Creation Final Checklist approuvee", payload.manual_tag_creation_final_checklist_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Human Tag Go/No-Go approuve", payload.human_tag_go_no_go_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewPrerequisite(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    criteria = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCriterion(name, payload.steps_present)
        for name in PLAN_CHECKS
    )
    commands = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewCommand(command, payload.commands_documentation_only)
        for command in COMMANDS
    )
    stop_rules = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewStopRule(rule, payload.stop_rules_present)
        for rule in STOP_RULES
    )
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext(
        review_id=payload.review_id,
        tag_metadata=AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewTagMetadata(
            payload.tag_name, payload.version
        ),
        prerequisites=prerequisites,
        criteria=criteria,
        commands=commands,
        stop_rules=stop_rules,
    )


def review_tag_creation_execution_plan_approval(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.execution_plan_approved)


def review_tag_creation_execution_plan_review_prerequisites(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    complete = True if payload is None else payload.prerequisites_complete
    return bool(context and complete and all(item.approved for item in context.prerequisites))


def review_tag_creation_execution_plan_review_tag_name(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_tag_creation_execution_plan_review_version(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_tag_creation_execution_plan_review_steps(context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None) -> bool:
    return bool(context and len(context.criteria) == len(PLAN_CHECKS) and all(item.passed for item in context.criteria))


def review_tag_creation_execution_plan_review_commands_documented_only(context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None) -> bool:
    return bool(context and len(context.commands) == len(COMMANDS) and all(command.documentation_only for command in context.commands))


def review_tag_creation_execution_plan_review_local_checks(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    present = True if payload is None else payload.local_checks_present
    names = {criterion.name for criterion in context.criteria} if context else set()
    return bool(context and present and set(LOCAL_CHECKS).issubset(names))


def review_tag_creation_execution_plan_review_remote_checks(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    present = True if payload is None else payload.remote_checks_present
    names = {criterion.name for criterion in context.criteria} if context else set()
    return bool(context and present and set(REMOTE_CHECKS).issubset(names))


def review_tag_creation_execution_plan_review_stop_rules(context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(rule.present for rule in context.stop_rules))


def review_tag_creation_execution_plan_review_no_git_tag_created(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_tag_creation_execution_plan_review_no_git_tag_pushed(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_tag_creation_execution_plan_review_no_live_trading_claim(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_tag_creation_execution_plan_review_no_profitability_claim(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_tag_creation_execution_plan_review_no_financial_advice_claim(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def _boundary_risks(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_tag_creation_execution_plan_review_boundaries(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_tag_creation_execution_plan_review_risks(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_MISSING,)
    risks: list[Risk] = []
    if not payload.execution_plan_approved:
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED)
    if not review_tag_creation_execution_plan_review_prerequisites(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITES_INCOMPLETE)
    for flag, risk in (
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
    if not review_tag_creation_execution_plan_review_tag_name(payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_INVALID)
    if not review_tag_creation_execution_plan_review_version(payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_INVALID)
    if not review_tag_creation_execution_plan_review_steps(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STEPS_MISSING)
    if not review_tag_creation_execution_plan_review_commands_documented_only(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_tag_creation_execution_plan_review_local_checks(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_LOCAL_CHECKS_MISSING)
    if not review_tag_creation_execution_plan_review_remote_checks(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_REMOTE_CHECKS_MISSING)
    if not review_tag_creation_execution_plan_review_stop_rules(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULES_MISSING)
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


def compute_agicore_trading_v1_offline_tag_creation_execution_plan_review_score(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewScore:
    payload = _coerce_input(data)
    values = (
        100 if validate_agicore_trading_v1_offline_tag_creation_execution_plan_review_input(payload) else 0,
        100 if review_tag_creation_execution_plan_approval(payload) else 0,
        100 if review_tag_creation_execution_plan_review_prerequisites(context, payload) else 0,
        100 if review_tag_creation_execution_plan_review_tag_name(payload) else 0,
        100 if review_tag_creation_execution_plan_review_version(payload) else 0,
        100 if review_tag_creation_execution_plan_review_steps(context) else 0,
        100 if review_tag_creation_execution_plan_review_commands_documented_only(context) else 0,
        100 if review_tag_creation_execution_plan_review_local_checks(context, payload) else 0,
        100 if review_tag_creation_execution_plan_review_remote_checks(context, payload) else 0,
        100 if review_tag_creation_execution_plan_review_stop_rules(context) else 0,
        100 if review_tag_creation_execution_plan_review_no_git_tag_created(payload) and review_tag_creation_execution_plan_review_no_git_tag_pushed(payload) else 0,
        100 if _no_overclaims(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewScore(overall, *values)


def generate_agicore_trading_v1_offline_tag_creation_execution_plan_review_recommendations(risks: Iterable[Risk]) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_MISSING: Recommendation.PROVIDE_TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT,
        Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_APPROVAL,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITES,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL,
        Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_INVALID: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STEPS_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STEPS,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_TAG_CREATION_REVIEW_COMMANDS_DOCUMENTATION_ONLY,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_LOCAL_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_LOCAL_CHECKS,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_REMOTE_CHECKS_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_REMOTE_CHECKS,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULES_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULES,
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
        recs.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION)
    return _dedupe(recs)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW
    if Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_FIXES
    if any(risk in risks for risk in (Risk.TAG_CREATION_EXECUTION_PLAN_NOT_APPROVED, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITES_INCOMPLETE, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED, Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED, Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED, Risk.FINAL_TAG_REVIEW_NOT_APPROVED, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED)):
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_PREREQUISITE_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_TAG_NAME_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_VERSION_FIXES
    if any(risk in risks for risk in (Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STEPS_MISSING, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_LOCAL_CHECKS_MISSING, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_REMOTE_CHECKS_MISSING)):
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STEP_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_COMMAND_DOCUMENTATION_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_STOP_RULE_FIXES
    return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_REVIEW_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_MANUAL_TAG_AUTHORIZATION
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW_BLOCKED


def _build_findings(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | None, context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None) -> tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding, ...]:
    checks = (
        ("execution plan approval", review_tag_creation_execution_plan_approval(data), "plan approuve"),
        ("prerequisites", review_tag_creation_execution_plan_review_prerequisites(context, data), "prerequis verifies"),
        ("tag name", review_tag_creation_execution_plan_review_tag_name(data), EXPECTED_TAG_NAME),
        ("version", review_tag_creation_execution_plan_review_version(data), EXPECTED_VERSION),
        ("steps", review_tag_creation_execution_plan_review_steps(context), "plan verifie"),
        ("commands documentation only", review_tag_creation_execution_plan_review_commands_documented_only(context), "commandes documentees"),
        ("local checks", review_tag_creation_execution_plan_review_local_checks(context, data), "checks locaux"),
        ("remote checks", review_tag_creation_execution_plan_review_remote_checks(context, data), "checks remote"),
        ("stop rules", review_tag_creation_execution_plan_review_stop_rules(context), "regles STOP"),
        ("no git tag created", review_tag_creation_execution_plan_review_no_git_tag_created(data), "aucun tag cree"),
        ("no git tag pushed", review_tag_creation_execution_plan_review_no_git_tag_pushed(data), "aucun tag pousse"),
        ("no live trading claim", review_tag_creation_execution_plan_review_no_live_trading_claim(data), "pas trading reel"),
        ("no profitability claim", review_tag_creation_execution_plan_review_no_profitability_claim(data), "pas rentabilite prouvee"),
        ("no financial advice", review_tag_creation_execution_plan_review_no_financial_advice_claim(data), "pas conseil financier"),
    )
    return tuple(AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding(name, passed, detail) for name, passed, detail in checks)


def render_agicore_trading_v1_offline_tag_creation_execution_plan_review_markdown(context: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewContext | None, findings: tuple[AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewFinding, ...] = ()) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Tag Creation Execution Plan Review",
        "",
        "## Statut",
        "",
        "execution plan review only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW",
        "",
        "## Conclusion",
        "",
        "- plan dexecution relu et valide",
        "- creation reelle du tag reservee a une action manuelle future de Bama",
        "- aucun tag Git cree dans cette phase",
        "- aucun tag Git pousse dans cette phase",
        "- AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "- pas pret pour trading reel",
        "- pas de broker reel",
        "- pas d'ordre reel",
        "- pas de preuve de rentabilite",
        "- pas de conseil financier",
        "",
        "## Prerequis verifies",
        "",
    ]
    lines.extend(f"- {item.name}" for item in (context.prerequisites if context else ()) if item.approved)
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}", "", "## Plan verifie", ""))
    lines.extend(f"- {criterion.name}" for criterion in (context.criteria if context else ()) if criterion.passed)
    lines.extend(("", "## Commandes verifiees comme documentation uniquement", ""))
    lines.extend(f"- {command.command}" for command in (context.commands if context else ()) if command.documentation_only)
    lines.extend(("", "## Regles STOP verifiees", ""))
    lines.extend(f"- {rule.rule}" for rule in (context.stop_rules if context else ()) if rule.present)
    if findings:
        lines.extend(("", "## Findings", ""))
        lines.extend(f"- {finding.name} : {'OK' if finding.passed else 'FAIL'}" for finding in findings)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Final Manual Tag Authorization"))
    return "\n".join(lines) + "\n"


def validate_tag_creation_execution_plan_review_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Creation Execution Plan Review",
        "execution plan review only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW",
        "plan dexecution relu et valide",
        "creation reelle du tag reservee a une action manuelle future de Bama",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
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
        "main synchronise",
        "tests unitaires complets",
        "git status propre hors data/",
        "aucun fichier staged",
        "data/ jamais ajoute",
        "verification tag local",
        "verification tag remote",
        "creation manuelle du tag seulement apres validation",
        "push manuel du tag seulement apres creation locale validee",
        "git switch main",
        "git fetch origin",
        "git pull origin main",
        "python -m pytest tests/unit/ -q",
        "git status --short",
        "git tag --list agicore-trading-v1-offline",
        "git ls-remote --tags origin agicore-trading-v1-offline",
        'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
        "git push origin agicore-trading-v1-offline",
        "STOP si tests rouges",
        "STOP si main nest pas synchronise",
        "STOP si git status contient autre chose que data/",
        "STOP si data/ est staged",
        "STOP si le tag existe deja localement",
        "STOP si le tag existe deja sur origin",
        "STOP si une commande tente de connecter broker/API/cle",
        "STOP si une formulation presente la release comme trading reel",
        "STOP si une formulation presente la release comme rentable ou comme conseil financier",
        "AGIcore Trading v1 Offline Final Manual Tag Authorization",
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


def render_agicore_trading_v1_offline_tag_creation_execution_plan_review_json_report(result: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult | Mapping[str, Any]) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_creation_execution_plan_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "findings": _payload_value(result.findings),
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


def review_agicore_trading_v1_offline_tag_creation_execution_plan(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewInput | Mapping[str, Any] | None) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult:
    payload = _coerce_input(data)
    context = build_tag_creation_execution_plan_review_context(payload)
    risks = detect_agicore_trading_v1_offline_tag_creation_execution_plan_review_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_creation_execution_plan_review_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_execution_plan_review_recommendations(risks)
    findings = _build_findings(payload, context)
    base = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult(
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
    report = AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewReport(
        markdown=render_agicore_trading_v1_offline_tag_creation_execution_plan_review_markdown(context, findings),
        json=render_agicore_trading_v1_offline_tag_creation_execution_plan_review_json_report(base),
    )
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanReviewResult(**{**base.__dict__, "report": report})
