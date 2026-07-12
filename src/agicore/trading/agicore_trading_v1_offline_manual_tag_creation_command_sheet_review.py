"""AGIcore Trading v1 offline manual tag creation command sheet review."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_models import (
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewCommand as Command,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewContext as Context,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewDecision as Decision,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewExpectedResult as ExpectedResult,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewInput as ReviewInput,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewPrerequisite as Prerequisite,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRecommendation as Recommendation,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewReport as Report,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewResult as Result,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewRisk as Risk,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewScore as Score,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewState as State,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewStopRule as StopRule,
    AGIcoreTradingV1OfflineManualTagCreationCommandSheetReviewTagMetadata as TagMetadata,
)

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"
PREREQUISITES = (
    "Manual Tag Creation Command Sheet approuvee",
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
EXPECTED_RESULTS = (
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
    out: list[Any] = []
    for item in items:
        if item not in out:
            out.append(item)
    return tuple(out)


def _coerce(data: ReviewInput | Mapping[str, Any] | None) -> ReviewInput | None:
    if data is None or isinstance(data, ReviewInput):
        return data
    allowed = {field.name for field in fields(ReviewInput)}
    return ReviewInput(**{key: value for key, value in dict(data).items() if key in allowed})


def build_manual_tag_creation_command_sheet_review_context(data: ReviewInput | Mapping[str, Any] | None) -> Context | None:
    payload = _coerce(data)
    if payload is None:
        return None
    approvals = (
        payload.command_sheet_approved,
        payload.final_manual_tag_authorization_approved,
        payload.execution_plan_review_approved,
        payload.manual_tag_creation_approval_approved,
        payload.human_tag_go_no_go_approved,
        payload.release_package_review_approved,
        payload.final_readiness_review_approved,
    )
    if not payload.prerequisites_complete:
        approvals = tuple(False for _ in approvals)
    return Context(
        review_id=payload.review_id,
        tag_metadata=TagMetadata(payload.tag_name, payload.version),
        prerequisites=tuple(Prerequisite(name, ok) for name, ok in zip(PREREQUISITES, approvals, strict=True)),
        pre_tag_commands=tuple(Command(cmd, "pre_tag", payload.pre_tag_commands_present, payload.documented_commands_only) for cmd in PRE_TAG_COMMANDS),
        expected_results=tuple(ExpectedResult(item, payload.expected_results_present) for item in EXPECTED_RESULTS),
        tag_creation_commands=tuple(Command(cmd, "tag_creation", True, payload.tag_creation_command_documentation_only) for cmd in TAG_CREATION_COMMANDS),
        tag_push_commands=tuple(Command(cmd, "tag_push", True, payload.tag_push_command_documentation_only) for cmd in TAG_PUSH_COMMANDS),
        post_tag_commands=tuple(Command(cmd, "post_tag", payload.post_tag_commands_present, payload.documented_commands_only) for cmd in POST_TAG_COMMANDS),
        stop_rules=tuple(StopRule(rule, payload.stop_rules_present) for rule in STOP_RULES),
    )


def review_manual_tag_creation_command_sheet_approval(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.command_sheet_approved)


def review_manual_tag_creation_command_sheet_review_prerequisites(
    context: Context | None, data: ReviewInput | Mapping[str, Any] | None = None
) -> bool:
    payload = _coerce(data) if data is not None else None
    flags_ok = True
    if payload is not None:
        flags_ok = (
            payload.prerequisites_complete
            and payload.command_sheet_approved
            and payload.final_manual_tag_authorization_approved
            and payload.execution_plan_review_approved
            and payload.manual_tag_creation_approval_approved
            and payload.human_tag_go_no_go_approved
            and payload.release_package_review_approved
            and payload.final_readiness_review_approved
        )
    return bool(context and flags_ok and len(context.prerequisites) == len(PREREQUISITES) and all(item.approved for item in context.prerequisites))


def review_manual_tag_creation_command_sheet_review_tag_name(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_manual_tag_creation_command_sheet_review_version(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_manual_tag_creation_command_sheet_review_pre_tag_commands(context: Context | None) -> bool:
    return bool(context and len(context.pre_tag_commands) == len(PRE_TAG_COMMANDS) and all(item.present for item in context.pre_tag_commands))


def review_manual_tag_creation_command_sheet_review_expected_results(context: Context | None) -> bool:
    return bool(context and len(context.expected_results) == len(EXPECTED_RESULTS) and all(item.present for item in context.expected_results))


def review_manual_tag_creation_command_sheet_review_tag_creation_command(context: Context | None) -> bool:
    return bool(context and len(context.tag_creation_commands) == len(TAG_CREATION_COMMANDS) and all(item.documentation_only for item in context.tag_creation_commands))


def review_manual_tag_creation_command_sheet_review_tag_push_command(context: Context | None) -> bool:
    return bool(context and len(context.tag_push_commands) == len(TAG_PUSH_COMMANDS) and all(item.documentation_only for item in context.tag_push_commands))


def review_manual_tag_creation_command_sheet_review_post_tag_commands(context: Context | None) -> bool:
    return bool(context and len(context.post_tag_commands) == len(POST_TAG_COMMANDS) and all(item.present for item in context.post_tag_commands))


def review_manual_tag_creation_command_sheet_review_stop_rules(context: Context | None) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(item.present for item in context.stop_rules))


def review_manual_tag_creation_command_sheet_review_documented_commands_only(context: Context | None) -> bool:
    if context is None:
        return False
    commands = (*context.pre_tag_commands, *context.tag_creation_commands, *context.tag_push_commands, *context.post_tag_commands)
    return bool(commands and all(item.documentation_only for item in commands))


def review_manual_tag_creation_command_sheet_review_no_git_tag_created(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_created)


def review_manual_tag_creation_command_sheet_review_no_git_tag_pushed(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_manual_tag_creation_command_sheet_review_no_live_trading_claim(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_manual_tag_creation_command_sheet_review_no_profitability_claim(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.profitability_overclaim)


def review_manual_tag_creation_command_sheet_review_no_financial_advice_claim(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _boundary_risks(data: ReviewInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
    risks: list[Risk] = []
    checks = (
        (data.file_read_requested, Risk.FILE_READ_BOUNDARY_VIOLATION),
        (data.real_data_access_requested, Risk.REAL_DATA_ACCESS_BOUNDARY_VIOLATION),
        (data.data_directory_access_requested, Risk.DATA_DIRECTORY_ACCESS_BOUNDARY_VIOLATION),
        (data.broker_connection_requested, Risk.REAL_BROKER_BOUNDARY_VIOLATION),
        (data.secret_read_requested, Risk.REAL_SECRET_BOUNDARY_VIOLATION),
        (data.network_requested or data.http_requested or data.websocket_requested or data.socket_requested or data.external_api_requested, Risk.NETWORK_BOUNDARY_VIOLATION),
        (data.order_execution_requested, Risk.ORDER_EXECUTION_BOUNDARY_VIOLATION),
        (data.account_access_requested, Risk.ACCOUNT_ACCESS_BOUNDARY_VIOLATION),
        (data.position_mutation_requested, Risk.POSITION_MUTATION_BOUNDARY_VIOLATION),
    )
    for flag, risk in checks:
        if flag:
            risks.append(risk)
    return _dedupe(risks)


def assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_boundaries(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    return not _boundary_risks(_coerce(data))


def validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_input(data: ReviewInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(
        payload
        and payload.review_id
        and review_manual_tag_creation_command_sheet_review_no_git_tag_created(payload)
        and review_manual_tag_creation_command_sheet_review_no_git_tag_pushed(payload)
        and assert_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_boundaries(payload)
    )


def detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_risks(
    data: ReviewInput | Mapping[str, Any] | None, context: Context | None = None
) -> tuple[Risk, ...]:
    payload = _coerce(data)
    if payload is None:
        return (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING,)
    risks: list[Risk] = []
    flag_risks = (
        (not payload.command_sheet_approved, Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED),
        (not review_manual_tag_creation_command_sheet_review_prerequisites(context, payload), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE),
        (not payload.final_manual_tag_authorization_approved, Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        (not payload.execution_plan_review_approved, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        (not payload.manual_tag_creation_approval_approved, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        (not payload.human_tag_go_no_go_approved, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        (not payload.release_package_review_approved, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        (not payload.final_readiness_review_approved, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED),
        (not review_manual_tag_creation_command_sheet_review_tag_name(payload), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID),
        (not review_manual_tag_creation_command_sheet_review_version(payload), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID),
        (not review_manual_tag_creation_command_sheet_review_pre_tag_commands(context), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING),
        (not review_manual_tag_creation_command_sheet_review_expected_results(context), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING),
        (not review_manual_tag_creation_command_sheet_review_tag_creation_command(context) or not review_manual_tag_creation_command_sheet_review_tag_push_command(context) or not review_manual_tag_creation_command_sheet_review_documented_commands_only(context), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY),
        (not review_manual_tag_creation_command_sheet_review_stop_rules(context), Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING),
        (payload.git_tag_already_created, Risk.GIT_TAG_ALREADY_CREATED),
        (payload.git_tag_already_pushed, Risk.GIT_TAG_ALREADY_PUSHED),
        (payload.live_trading_overclaim, Risk.LIVE_TRADING_READINESS_OVERCLAIM),
        (payload.real_broker_overclaim, Risk.REAL_BROKER_READINESS_OVERCLAIM),
        (payload.real_order_overclaim, Risk.REAL_ORDER_EXECUTION_OVERCLAIM),
        (payload.paper_broker_overclaim, Risk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        (payload.profitability_overclaim, Risk.PROFITABILITY_PROOF_OVERCLAIM),
        (payload.financial_advice_overclaim, Risk.FINANCIAL_ADVICE_OVERCLAIM),
    )
    risks.extend(risk for flag, risk in flag_risks if flag)
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def _safe(data: ReviewInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_score(
    data: ReviewInput | Mapping[str, Any] | None, context: Context | None, risks: tuple[Risk, ...]
) -> Score:
    payload = _coerce(data)
    values = (
        100 if validate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_input(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_review_prerequisites(context, payload) else 0,
        100 if review_manual_tag_creation_command_sheet_review_tag_name(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_review_version(payload) else 0,
        100 if review_manual_tag_creation_command_sheet_review_pre_tag_commands(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_expected_results(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_tag_creation_command(context) and review_manual_tag_creation_command_sheet_review_tag_push_command(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_post_tag_commands(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_stop_rules(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_documented_commands_only(context) else 0,
        100 if review_manual_tag_creation_command_sheet_review_no_git_tag_created(payload) and review_manual_tag_creation_command_sheet_review_no_git_tag_pushed(payload) else 0,
        100 if _safe(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return Score(overall, *values)


def generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING: Recommendation.PROVIDE_COMMAND_SHEET_REVIEW_INPUT,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED: Recommendation.RESTORE_COMMAND_SHEET_APPROVAL,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_COMMAND_SHEET_REVIEW_PREREQUISITES,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED: Recommendation.RESTORE_FINAL_MANUAL_TAG_AUTHORIZATION,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED: Recommendation.RESTORE_TAG_CREATION_EXECUTION_PLAN_REVIEW,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED: Recommendation.RESTORE_MANUAL_TAG_CREATION_APPROVAL,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED: Recommendation.RESTORE_HUMAN_TAG_GO_NO_GO,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED: Recommendation.RESTORE_RELEASE_PACKAGE_REVIEW,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED: Recommendation.RESTORE_FINAL_READINESS_REVIEW,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID: Recommendation.RESTORE_COMMAND_SHEET_REVIEW_TAG_NAME,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID: Recommendation.RESTORE_COMMAND_SHEET_REVIEW_VERSION,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING: Recommendation.RESTORE_PRE_TAG_COMMAND_REVIEW,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING: Recommendation.RESTORE_EXPECTED_RESULT_REVIEW,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_TAG_COMMANDS_DOCUMENTATION_ONLY,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING: Recommendation.RESTORE_STOP_RULE_REVIEW,
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
    return _dedupe(recommendations or [Recommendation.PREPARE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION])


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW
    if Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_MISSING in risks:
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_FIXES
    prerequisite = {
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITES_INCOMPLETE,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED,
    }
    if any(risk in prerequisite for risk in risks):
        return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PREREQUISITE_FIXES
    ordered = (
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_INVALID, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_NAME_FIXES),
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_INVALID, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_VERSION_FIXES),
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMANDS_MISSING, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_PRE_TAG_COMMAND_FIXES),
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULTS_MISSING, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_EXPECTED_RESULT_FIXES),
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMANDS_NOT_DOCUMENTATION_ONLY, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_TAG_COMMAND_FIXES),
        (Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULES_MISSING, Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_STOP_RULE_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.REQUIRE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NO_OVERCLAIM_FIXES


def _state_for(data: ReviewInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION
    return State.AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_BLOCKED


def render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_markdown(context: Context | None) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Manual Tag Creation Command Sheet Review",
        "",
        "## Statut",
        "",
        "command sheet review only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW",
        "",
        "## Conclusion",
        "",
        "- fiche de commandes relue et validee",
        "- commandes utilisables manuellement plus tard uniquement par Bama",
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
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Commandes avant tag verifiees", ""))
    lines.extend(f"- {item.command}" for item in (context.pre_tag_commands if context else ()) if item.present)
    lines.extend(("", "## Resultats attendus verifies", ""))
    lines.extend(f"- {item.result}" for item in (context.expected_results if context else ()) if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.tag_creation_commands if context else ()) if item.documentation_only)
    lines.extend(f"- {item.command}" for item in (context.tag_push_commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Commandes post-tag verifiees comme documentation uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.post_tag_commands if context else ()) if item.present)
    lines.extend(("", "## Regles STOP verifiees", ""))
    lines.extend(f"- {item.rule}" for item in (context.stop_rules if context else ()) if item.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Final Tag Creation Human Confirmation"))
    return "\n".join(lines) + "\n"


def validate_manual_tag_creation_command_sheet_review_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Manual Tag Creation Command Sheet Review",
        "command sheet review only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW",
        "fiche de commandes relue et validee",
        "commandes utilisables manuellement plus tard uniquement par Bama",
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
        *EXPECTED_RESULTS,
        *TAG_CREATION_COMMANDS,
        *TAG_PUSH_COMMANDS,
        *POST_TAG_COMMANDS,
        *STOP_RULES,
        "AGIcore Trading v1 Offline Final Tag Creation Human Confirmation",
    )
    return all(item in markdown for item in required)


def _payload(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Mapping):
        return {str(key): _payload(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_payload(item) for item in value]
    if hasattr(value, "__dict__"):
        return {key: _payload(item) for key, item in vars(value).items() if not key.startswith("_")}
    return str(value)


def render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_json_report(result: Result | Mapping[str, Any]) -> str:
    if isinstance(result, Result):
        data = {
            "schema": "agicore_trading_v1_offline_manual_tag_creation_command_sheet_review",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload(result.context),
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
        data = dict(result)
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def review_agicore_trading_v1_offline_manual_tag_creation_command_sheet(data: ReviewInput | Mapping[str, Any] | None) -> Result:
    payload = _coerce(data)
    context = build_manual_tag_creation_command_sheet_review_context(payload)
    risks = detect_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_recommendations(risks)
    base = Result(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        report=None,
        git_tag_created=False,
        git_tag_pushed=False,
        real_order_submitted=False,
        real_account_accessed=False,
        position_mutated=False,
    )
    report = Report(
        markdown=render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_markdown(context),
        json=render_agicore_trading_v1_offline_manual_tag_creation_command_sheet_review_json_report(base),
    )
    return Result(**{**base.__dict__, "report": report})
