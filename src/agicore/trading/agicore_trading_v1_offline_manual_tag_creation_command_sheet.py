"""AGIcore Trading v1 offline manual tag creation command sheet."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_command_sheet_models import (
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetCommand,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetDecision,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetExpectedResult,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetRecommendation,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReport,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetRisk,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetScore,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetState,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetStopRule,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetTagMetadata,
)


Risk = AGIcoreTradingV1OfflineManualTagCreationCommandSheetRisk
Recommendation = AGIcoreTradingV1OfflineManualTagCreationCommandSheetRecommendation
Decision = AGIcoreTradingV1OfflineManualTagCreationCommandSheetDecision
State = AGIcoreTradingV1OfflineManualTagCreationCommandSheetState

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"

PREREQUISITES = (
    "Final Manual Tag Authorization approuvee",
    "Tag Creation Execution Plan Review approuvee",
    "Manual Tag Creation Approval approuvee",
    "Human Tag Go/No-Go approuve",
    "Release Package Review approuvee",
    "Final Readiness Review approuvee",
)
PRE_TAG_COMMANDS = (
    "git switch main",
    "git fetch origin",
    "git pull origin main",
    "python -m pytest tests/unit/ -q",
    "git status --short",
    "git diff --check",
    "git diff --cached --name-only",
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
)
EXPECTED_PRE_TAG_RESULTS = (
    "tests verts",
    "git status --short retourne seulement ?? data/",
    "git diff --cached --name-only ne retourne rien",
    "git tag --list agicore-trading-v1-offline ne retourne rien",
    "git ls-remote --tags origin agicore-trading-v1-offline ne retourne rien",
)
TAG_CREATION_COMMANDS = (
    'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
)
TAG_PUSH_COMMANDS = ("git push origin agicore-trading-v1-offline",)
POST_TAG_COMMANDS = (
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
    "git status --short",
)
STOP_RULES = (
    "STOP si tests rouges",
    "STOP si main nest pas synchronise",
    "STOP si git status contient autre chose que data/",
    "STOP si data/ est staged",
    "STOP si git diff --cached --name-only retourne quelque chose",
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
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput)}
    return AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput(
        **{key: value for key, value in dict(data).items() if key in allowed}
    )


def validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_input(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(
        payload
        and payload.sheet_id
        and review_manual_tag_creation_command_sheet_no_git_tag_created(payload)
        and review_manual_tag_creation_command_sheet_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_boundaries(payload)
    )


def build_manual_tag_creation_command_sheet_context(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None:
    payload = _coerce_input(data)
    if payload is None:
        return None
    return AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext(
        sheet_id=payload.sheet_id,
        tag_metadata=AGIcoreTradingV1OfflineManualTagCreationCommandSheetTagMetadata(
            payload.tag_name, payload.version
        ),
        prerequisites=PREREQUISITES if payload.prerequisites_complete else (),
        pre_tag_commands=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetCommand(
                command, "pre_tag", payload.pre_tag_commands_present, payload.documented_commands_only
            )
            for command in PRE_TAG_COMMANDS
        ),
        expected_pre_tag_results=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetExpectedResult(
                result, payload.expected_results_present
            )
            for result in EXPECTED_PRE_TAG_RESULTS
        ),
        tag_creation_commands=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetCommand(
                command, "tag_creation", True, payload.tag_creation_command_documentation_only
            )
            for command in TAG_CREATION_COMMANDS
        ),
        tag_push_commands=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetCommand(
                command, "tag_push", True, payload.tag_push_command_documentation_only
            )
            for command in TAG_PUSH_COMMANDS
        ),
        post_tag_commands=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetCommand(
                command, "post_tag", payload.post_tag_commands_present, payload.documented_commands_only
            )
            for command in POST_TAG_COMMANDS
        ),
        stop_rules=tuple(
            AGIcoreTradingV1OfflineManualTagCreationCommandSheetStopRule(rule, payload.stop_rules_present)
            for rule in STOP_RULES
        ),
    )


def review_manual_tag_creation_command_sheet_prerequisites(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None = None,
) -> bool:
    payload = _coerce_input(data) if data is not None else None
    flags_ok = True
    if payload is not None:
        flags_ok = (
            payload.prerequisites_complete
            and payload.final_manual_tag_authorization_approved
            and payload.execution_plan_review_approved
            and payload.manual_tag_creation_approval_approved
            and payload.human_tag_go_no_go_approved
            and payload.release_package_review_approved
            and payload.final_readiness_review_approved
        )
    return bool(context and flags_ok and set(PREREQUISITES).issubset(set(context.prerequisites)))


def review_manual_tag_creation_command_sheet_tag_name(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_manual_tag_creation_command_sheet_version(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_manual_tag_creation_command_sheet_pre_tag_commands(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.pre_tag_commands) == len(PRE_TAG_COMMANDS) and all(item.present for item in context.pre_tag_commands))


def review_manual_tag_creation_command_sheet_expected_pre_tag_results(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.expected_pre_tag_results) == len(EXPECTED_PRE_TAG_RESULTS) and all(item.present for item in context.expected_pre_tag_results))


def review_manual_tag_creation_command_sheet_tag_creation_command(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.tag_creation_commands) == len(TAG_CREATION_COMMANDS) and all(item.documentation_only for item in context.tag_creation_commands))


def review_manual_tag_creation_command_sheet_tag_push_command(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.tag_push_commands) == len(TAG_PUSH_COMMANDS) and all(item.documentation_only for item in context.tag_push_commands))


def review_manual_tag_creation_command_sheet_post_tag_commands(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.post_tag_commands) == len(POST_TAG_COMMANDS) and all(item.present for item in context.post_tag_commands))


def review_manual_tag_creation_command_sheet_stop_rules(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(item.present for item in context.stop_rules))


def review_manual_tag_creation_command_sheet_documented_commands_only(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> bool:
    if context is None:
        return False
    commands = (*context.pre_tag_commands, *context.tag_creation_commands, *context.tag_push_commands, *context.post_tag_commands)
    return bool(commands and all(item.documentation_only for item in commands))


def review_manual_tag_creation_command_sheet_no_git_tag_created(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_created)


def review_manual_tag_creation_command_sheet_no_git_tag_pushed(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_manual_tag_creation_command_sheet_no_live_trading_claim(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_manual_tag_creation_command_sheet_no_profitability_claim(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.profitability_overclaim)


def review_manual_tag_creation_command_sheet_no_financial_advice_claim(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce_input(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _no_overclaims(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def _boundary_risks(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_boundaries(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_risks(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None = None,
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    if payload is None:
        return (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_INPUT_MISSING,)
    risks: list[Risk] = []
    if not review_manual_tag_creation_command_sheet_prerequisites(context, payload):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PREREQUISITES_INCOMPLETE)
    for flag, risk in (
        (payload.final_manual_tag_authorization_approved, Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        (payload.execution_plan_review_approved, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        (payload.manual_tag_creation_approval_approved, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        (payload.human_tag_go_no_go_approved, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        (payload.release_package_review_approved, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        (payload.final_readiness_review_approved, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED),
    ):
        if not flag:
            risks.append(risk)
    if not review_manual_tag_creation_command_sheet_tag_name(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_NAME_INVALID)
    if not review_manual_tag_creation_command_sheet_version(payload):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_VERSION_INVALID)
    if not review_manual_tag_creation_command_sheet_pre_tag_commands(context):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PRE_TAG_COMMANDS_MISSING)
    if not review_manual_tag_creation_command_sheet_expected_pre_tag_results(context):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_EXPECTED_RESULTS_MISSING)
    if not review_manual_tag_creation_command_sheet_tag_creation_command(context) or not review_manual_tag_creation_command_sheet_tag_push_command(context) or not review_manual_tag_creation_command_sheet_documented_commands_only(context):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY)
    if not review_manual_tag_creation_command_sheet_stop_rules(context):
        risks.append(Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_STOP_RULES_MISSING)
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


def compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_score(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineManualTagCreationCommandSheetScore:
    payload = _coerce_input(data)
    values = (
        100 if validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_input(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_prerequisites(context, payload) else 0,
        100 if review_manual_tag_creation_command_sheet_tag_name(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_version(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_pre_tag_commands(context) else 0,
        100 if review_manual_tag_creation_command_sheet_expected_pre_tag_results(context) else 0,
        100 if review_manual_tag_creation_command_sheet_tag_creation_command(context) and review_manual_tag_creation_command_sheet_tag_push_command(context) else 0,
        100 if review_manual_tag_creation_command_sheet_post_tag_commands(context) else 0,
        100 if review_manual_tag_creation_command_sheet_stop_rules(context) else 0,
        100 if review_manual_tag_creation_command_sheet_documented_commands_only(context) else 0,
        100 if review_manual_tag_creation_command_sheet_no_git_tag_created(payload) and review_manual_tag_creation_command_sheet_no_git_tag_pushed(payload) else 0,
        100 if _no_overclaims(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineManualTagCreationCommandSheetScore(overall, *values)


def generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_INPUT_MISSING: Recommendation.PROVIDE_COMMAND_SHEET_INPUT,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_COMMAND_SHEET_PREREQUISITES,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_NAME_INVALID: Recommendation.RESTORE_COMMAND_SHEET_TAG_NAME,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_VERSION_INVALID: Recommendation.RESTORE_COMMAND_SHEET_VERSION,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PRE_TAG_COMMANDS_MISSING: Recommendation.RESTORE_PRE_TAG_COMMANDS,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_EXPECTED_RESULTS_MISSING: Recommendation.RESTORE_EXPECTED_PRE_TAG_RESULTS,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_STOP_RULES_MISSING: Recommendation.RESTORE_STOP_RULES,
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
        recs.append(Recommendation.PREPARE_COMMAND_SHEET_REVIEW)
    return _dedupe(recs)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_INPUT_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_INPUT_FIXES
    prerequisite_risks = {
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PREREQUISITES_INCOMPLETE,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED,
    }
    if any(risk in prerequisite_risks for risk in risks):
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_PREREQUISITE_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_NAME_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_NAME_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_VERSION_INVALID in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_VERSION_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_PRE_TAG_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_PRE_TAG_COMMAND_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_EXPECTED_RESULTS_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_EXPECTED_RESULT_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_TAG_COMMAND_FIXES
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_STOP_RULES_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_STOP_RULE_FIXES
    return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_NO_OVERCLAIM_FIXES


def _state_for(data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_BLOCKED


def render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_markdown(
    context: AGIcoreTradingV1OfflineManualTagCreationCommandSheetContext | None,
) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Manual Tag Creation Command Sheet",
        "",
        "## Statut",
        "",
        "command sheet only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET",
        "",
        "## Conclusion",
        "",
        "- fiche de commandes prete",
        "- commandes a executer manuellement plus tard uniquement par Bama",
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
    lines.extend(f"- {item}" for item in (context.prerequisites if context else ()))
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}", "", "## Bloc 1 : verification avant creation du tag", ""))
    lines.extend(f"- {item.command}" for item in (context.pre_tag_commands if context else ()) if item.present)
    lines.extend(("", "## Resultat attendu avant tag", ""))
    lines.extend(f"- {item.result}" for item in (context.expected_pre_tag_results if context else ()) if item.present)
    lines.extend(("", "## Bloc 2 : creation future manuelle du tag, documentee uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.tag_creation_commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Bloc 3 : push futur manuel du tag, documente uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.tag_push_commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Bloc 4 : verification apres push du tag, documentee uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.post_tag_commands if context else ()) if item.present)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {item.rule}" for item in (context.stop_rules if context else ()) if item.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet Review"))
    return "\n".join(lines) + "\n"


def validate_manual_tag_creation_command_sheet_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet",
        "command sheet only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET",
        "fiche de commandes prete",
        "commandes a executer manuellement plus tard uniquement par Bama",
        "aucun tag Git cree dans cette phase",
        "aucun tag Git pousse dans cette phase",
        "AGIcore Trading v1 Offline reste sandbox/offline uniquement",
        "pas pret pour trading reel",
        "pas de broker reel",
        "pas d'ordre reel",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        *PREREQUISITES,
        EXPECTED_TAG_NAME,
        EXPECTED_VERSION,
        *PRE_TAG_COMMANDS,
        *EXPECTED_PRE_TAG_RESULTS,
        *TAG_CREATION_COMMANDS,
        *TAG_PUSH_COMMANDS,
        *POST_TAG_COMMANDS,
        *STOP_RULES,
        "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet Review",
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


def render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_json_report(
    result: AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult):
        payload = {
            "schema": "agicore_trading_v1_offline_manual_tag_creation_command_sheet",
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


def build_agicore_trading_v1_offline_manual_tag_creation_command_sheet(
    data: AGIcoreTradingV1OfflineManualTagCreationCommandSheetInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult:
    payload = _coerce_input(data)
    context = build_manual_tag_creation_command_sheet_context(payload)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_recommendations(risks)
    base = AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult(
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
    report = AGIcoreTradingV1OfflineManualTagCreationCommandSheetReport(
        markdown=render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_markdown(context),
        json=render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_json_report(base),
    )
    return AGIcoreTradingV1OfflineManualTagCreationCommandSheetResult(**{**base.__dict__, "report": report})
