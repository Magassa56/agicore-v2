"""AGIcore Trading v1 offline tag creation execution plan."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_creation_execution_plan_models import (
    AGIcoreTradingV1OfflineTagCreationExecutionPlanCommand,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanContext,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanInput,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanReport,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanResult,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanScore,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanState,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanStep,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanStopRule,
    AGIcoreTradingV1OfflineTagCreationExecutionPlanTagMetadata,
)


Risk = AGIcoreTradingV1OfflineTagCreationExecutionPlanRisk
Recommendation = AGIcoreTradingV1OfflineTagCreationExecutionPlanRecommendation
Decision = AGIcoreTradingV1OfflineTagCreationExecutionPlanDecision
State = AGIcoreTradingV1OfflineTagCreationExecutionPlanState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

PLAN_STEPS = (
    "se placer sur main",
    "synchroniser main avec origin/main",
    "lancer les tests unitaires complets",
    "verifier git status --short",
    "verifier quaucun fichier nest staged",
    "verifier que data/ nest pas ajoute",
    "verifier que le tag nexiste pas deja localement",
    "verifier que le tag nexiste pas deja sur origin",
    "creer le tag manuellement seulement si tout est vert",
    "pousser le tag manuellement seulement apres creation locale validee",
)

DOCUMENTED_COMMANDS = (
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

PRE_CHECK_COMMANDS = (
    "git switch main",
    "git fetch origin",
    "git pull origin main",
    "python -m pytest tests/unit/ -q",
    "git status --short",
)

REMOTE_CHECK_COMMANDS = (
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
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
    output: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return tuple(output)


def _coerce_input(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineTagCreationExecutionPlanInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineTagCreationExecutionPlanInput)}
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_tag_creation_execution_plan_input(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.plan_id
        and review_tag_creation_execution_plan_no_git_tag_created(payload)
        and review_tag_creation_execution_plan_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_tag_creation_execution_plan_boundaries(payload)
    )


def build_tag_creation_execution_plan_context(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    prerequisites = (
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Manual Tag Creation Approval approuvee", payload.manual_tag_creation_approval_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Manual Tag Creation Final Checklist approuvee", payload.manual_tag_creation_final_checklist_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Human Tag Go/No-Go approuve", payload.human_tag_go_no_go_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Tag Creation Instructions Review approuvee", payload.tag_creation_instructions_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Final Tag Review approuvee", payload.final_tag_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Release Package Review approuvee", payload.release_package_review_approved
        ),
        AGIcoreTradingV1OfflineTagCreationExecutionPlanPrerequisite(
            "Final Readiness Review approuvee", payload.final_readiness_review_approved
        ),
    )
    steps = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanStep(index + 1, step, payload.steps_present)
        for index, step in enumerate(PLAN_STEPS)
    )
    commands = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanCommand(command, payload.commands_documentation_only)
        for command in DOCUMENTED_COMMANDS
    )
    stop_rules = tuple(
        AGIcoreTradingV1OfflineTagCreationExecutionPlanStopRule(rule, payload.stop_rules_present)
        for rule in STOP_RULES
    )
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanContext(
        plan_id=payload.plan_id,
        tag_metadata=AGIcoreTradingV1OfflineTagCreationExecutionPlanTagMetadata(payload.tag_name, payload.version),
        prerequisites=prerequisites,
        steps=steps,
        commands=commands,
        stop_rules=stop_rules,
    )


def review_tag_creation_execution_plan_prerequisites(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    prerequisites_complete = True if payload is None else payload.prerequisites_complete
    return bool(context and prerequisites_complete and all(item.approved for item in context.prerequisites))


def review_tag_creation_execution_plan_tag_name(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_tag_creation_execution_plan_version(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_tag_creation_execution_plan_steps(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
) -> bool:
    return bool(context and len(context.steps) == len(PLAN_STEPS) and all(step.present for step in context.steps))


def review_tag_creation_execution_plan_commands_documented_only(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
) -> bool:
    return bool(context and len(context.commands) == len(DOCUMENTED_COMMANDS) and all(command.documentation_only for command in context.commands))


def review_tag_creation_execution_plan_pre_checks(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    present = True if payload is None else payload.pre_checks_present
    commands = {command.command for command in context.commands} if context else set()
    return bool(context and present and set(PRE_CHECK_COMMANDS).issubset(commands))


def review_tag_creation_execution_plan_remote_checks(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    present = True if payload is None else payload.remote_checks_present
    commands = {command.command for command in context.commands} if context else set()
    return bool(context and present and set(REMOTE_CHECK_COMMANDS).issubset(commands))


def review_tag_creation_execution_plan_stop_rules(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(rule.present for rule in context.stop_rules))


def review_tag_creation_execution_plan_no_git_tag_created(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_tag_creation_execution_plan_no_git_tag_pushed(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_tag_creation_execution_plan_no_live_trading_claim(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_tag_creation_execution_plan_no_profitability_claim(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_tag_creation_execution_plan_no_financial_advice_claim(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | None) -> bool:
    return bool(
        data
        and not data.live_trading_overclaim
        and not data.real_broker_overclaim
        and not data.real_order_overclaim
        and not data.paper_broker_overclaim
        and not data.profitability_overclaim
        and not data.financial_advice_overclaim
    )


def _boundary_risks(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_tag_creation_execution_plan_boundaries(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_tag_creation_execution_plan_risks(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_tag_creation_execution_plan_prerequisites(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE)
    if not payload.manual_tag_creation_approval_approved:
        risks.append(Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED)
    if not payload.manual_tag_creation_final_checklist_approved:
        risks.append(Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED)
    if not payload.human_tag_go_no_go_approved:
        risks.append(Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED)
    if not payload.tag_creation_instructions_review_approved:
        risks.append(Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED)
    if not payload.final_tag_review_approved:
        risks.append(Risk.FINAL_TAG_REVIEW_NOT_APPROVED)
    if not payload.release_package_review_approved:
        risks.append(Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED)
    if not payload.final_readiness_review_approved:
        risks.append(Risk.FINAL_READINESS_REVIEW_NOT_APPROVED)
    if not review_tag_creation_execution_plan_tag_name(payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID)
    if not review_tag_creation_execution_plan_version(payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID)
    if not review_tag_creation_execution_plan_steps(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING)
    if not review_tag_creation_execution_plan_commands_documented_only(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_tag_creation_execution_plan_pre_checks(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING)
    if not review_tag_creation_execution_plan_remote_checks(context, payload):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING)
    if not review_tag_creation_execution_plan_stop_rules(context):
        risks.append(Risk.TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING)
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


def compute_agicore_trading_v1_offline_tag_creation_execution_plan_score(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_tag_creation_execution_plan_input(payload) else 0
    prerequisite_score = 100 if review_tag_creation_execution_plan_prerequisites(context, payload) else 0
    tag_name_score = 100 if review_tag_creation_execution_plan_tag_name(payload) else 0
    version_score = 100 if review_tag_creation_execution_plan_version(payload) else 0
    step_score = 100 if review_tag_creation_execution_plan_steps(context) else 0
    command_score = 100 if review_tag_creation_execution_plan_commands_documented_only(context) else 0
    pre_check_score = 100 if review_tag_creation_execution_plan_pre_checks(context, payload) else 0
    remote_check_score = 100 if review_tag_creation_execution_plan_remote_checks(context, payload) else 0
    stop_rule_score = 100 if review_tag_creation_execution_plan_stop_rules(context) else 0
    no_tag_score = 100 if review_tag_creation_execution_plan_no_git_tag_created(payload) and review_tag_creation_execution_plan_no_git_tag_pushed(payload) else 0
    safety_score = 100 if _no_overclaims(payload) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        prerequisite_score,
        tag_name_score,
        version_score,
        step_score,
        command_score,
        pre_check_score,
        remote_check_score,
        stop_rule_score,
        no_tag_score,
        safety_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanScore(
        overall, input_score, prerequisite_score, tag_name_score, version_score, step_score,
        command_score, pre_check_score, remote_check_score, stop_rule_score, no_tag_score,
        safety_score, boundary_score,
    )


def generate_agicore_trading_v1_offline_tag_creation_execution_plan_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING: Recommendation.PROVIDE_TAG_CREATION_EXECUTION_PLAN_INPUT,
        Risk.TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITES,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL,
        Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_FINAL_CHECKLIST,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO,
        Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_INSTRUCTIONS_REVIEW,
        Risk.FINAL_TAG_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_TAG_REVIEW,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW,
        Risk.TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME,
        Risk.TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_VERSION,
        Risk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_STEPS,
        Risk.TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_TAG_CREATION_COMMANDS_DOCUMENTATION_ONLY,
        Risk.TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_STOP_RULES,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN
    if Risk.TAG_CREATION_EXECUTION_PLAN_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_INPUT_FIXES
    if (
        Risk.TAG_CREATION_EXECUTION_PLAN_PREREQUISITES_INCOMPLETE in risks
        or Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED in risks
        or Risk.MANUAL_TAG_CREATION_FINAL_CHECKLIST_NOT_APPROVED in risks
        or Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED in risks
        or Risk.TAG_CREATION_INSTRUCTIONS_REVIEW_NOT_APPROVED in risks
        or Risk.FINAL_TAG_REVIEW_NOT_APPROVED in risks
        or Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED in risks
        or Risk.FINAL_READINESS_REVIEW_NOT_APPROVED in risks
    ):
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_PREREQUISITE_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_TAG_NAME_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_VERSION_INVALID in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_VERSION_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_STEPS_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_STEP_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_COMMAND_DOCUMENTATION_FIXES
    if Risk.TAG_CREATION_EXECUTION_PLAN_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_STOP_RULE_FIXES
    return Decision.REQUIRE_TAG_CREATION_EXECUTION_PLAN_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN_BLOCKED


def render_agicore_trading_v1_offline_tag_creation_execution_plan_markdown(
    context: AGIcoreTradingV1OfflineTagCreationExecutionPlanContext | None,
) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Tag Creation Execution Plan",
        "",
        "## Statut",
        "",
        "execution plan only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN",
        "",
        "## Conclusion",
        "",
        "- plan dexecution pret",
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
        "## Prerequis valides",
        "",
    ]
    lines.extend(f"- {item.name}" for item in (context.prerequisites if context else ()) if item.approved)
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}"))
    lines.extend(("", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Plan dexecution futur documente uniquement", ""))
    lines.extend(f"{step.index}. {step.description}" for step in (context.steps if context else ()) if step.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {command.command}" for command in (context.commands if context else ()) if command.documentation_only)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {rule.rule}" for rule in (context.stop_rules if context else ()) if rule.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Tag Creation Execution Plan Review"))
    return "\n".join(lines) + "\n"


def validate_tag_creation_execution_plan_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Creation Execution Plan",
        "execution plan only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_EXECUTION_PLAN",
        "plan dexecution pret",
        "creation reelle du tag reservee a une action manuelle future de Bama",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "Manual Tag Creation Approval approuvee",
        "Manual Tag Creation Final Checklist approuvee",
        "Human Tag Go/No-Go approuve",
        "Tag Creation Instructions Review approuvee",
        "Final Tag Review approuvee",
        "Release Package Review approuvee",
        "Final Readiness Review approuvee",
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        "1. se placer sur main",
        "10. pousser le tag manuellement seulement apres creation locale validee",
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
        "AGIcore Trading v1 Offline Tag Creation Execution Plan Review",
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


def render_agicore_trading_v1_offline_tag_creation_execution_plan_json_report(
    result: AGIcoreTradingV1OfflineTagCreationExecutionPlanResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineTagCreationExecutionPlanResult):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_creation_execution_plan",
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


def build_agicore_trading_v1_offline_tag_creation_execution_plan(
    data: AGIcoreTradingV1OfflineTagCreationExecutionPlanInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineTagCreationExecutionPlanResult:
    payload = _coerce_input(data)
    context = build_tag_creation_execution_plan_context(payload)
    risks = detect_agicore_trading_v1_offline_tag_creation_execution_plan_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_creation_execution_plan_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_execution_plan_recommendations(risks)
    base = AGIcoreTradingV1OfflineTagCreationExecutionPlanResult(
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
    report = AGIcoreTradingV1OfflineTagCreationExecutionPlanReport(
        markdown=render_agicore_trading_v1_offline_tag_creation_execution_plan_markdown(context),
        json=render_agicore_trading_v1_offline_tag_creation_execution_plan_json_report(base),
    )
    return AGIcoreTradingV1OfflineTagCreationExecutionPlanResult(**{**base.__dict__, "report": report})
