"""AGIcore Trading v1 offline final tag creation human confirmation."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_final_tag_creation_human_confirmation_models import (
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCommand as Command,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationCondition as Condition,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationContext as Context,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationDecision as Decision,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationInput as ConfirmationInput,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationPrerequisite as Prerequisite,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRecommendation as Recommendation,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationReport as Report,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationResult as Result,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationRisk as Risk,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationScore as Score,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationState as State,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationStopRule as StopRule,
    AGIcoreTradingV1OfflineFinalTagCreationHumanConfirmationTagMetadata as TagMetadata,
)

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"
HUMAN_CONFIRMATION = "HUMAN_CONFIRMATION_READY_FOR_MANUAL_TAG_CREATION_LATER"
PREREQUISITES = (
    "Manual Tag Creation Command Sheet Review approuvee",
    "Manual Tag Creation Command Sheet approuvee",
    "Final Manual Tag Authorization approuvee",
    "Tag Creation Execution Plan Review approuvee",
    "Manual Tag Creation Approval approuvee",
    "Human Tag Go/No-Go approuve",
    "Release Package Review approuvee",
    "Final Readiness Review approuvee",
)
CONDITIONS = (
    "Bama relit la fiche de commandes",
    "Bama confirme explicitement la creation du tag",
    "etre sur main",
    "main synchronise avec origin/main",
    "tests/unit verts",
    "git status --short retourne seulement ?? data/",
    "git diff --cached --name-only ne retourne rien",
    "tag inexistant localement",
    "tag inexistant sur origin",
    "data/ non staged",
)
COMMANDS = (
    "git switch main",
    "git fetch origin",
    "git pull origin main",
    "python -m pytest tests/unit/ -q",
    "git status --short",
    "git diff --cached --name-only",
    "git tag --list agicore-trading-v1-offline",
    "git ls-remote --tags origin agicore-trading-v1-offline",
    'git tag -a agicore-trading-v1-offline -m "AGIcore Trading v1 Offline - sandbox release"',
    "git push origin agicore-trading-v1-offline",
)
STOP_RULES = (
    "STOP si Bama na pas confirme explicitement",
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
    output: list[Any] = []
    for item in items:
        if item not in output:
            output.append(item)
    return tuple(output)


def _coerce(data: ConfirmationInput | Mapping[str, Any] | None) -> ConfirmationInput | None:
    if data is None or isinstance(data, ConfirmationInput):
        return data
    allowed = {field.name for field in fields(ConfirmationInput)}
    return ConfirmationInput(**{key: value for key, value in dict(data).items() if key in allowed})


def build_final_tag_creation_human_confirmation_context(data: ConfirmationInput | Mapping[str, Any] | None) -> Context | None:
    payload = _coerce(data)
    if payload is None:
        return None
    approvals = (
        payload.command_sheet_review_approved,
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
        confirmation_id=payload.confirmation_id,
        tag_metadata=TagMetadata(payload.tag_name, payload.version),
        prerequisites=tuple(Prerequisite(name, approved) for name, approved in zip(PREREQUISITES, approvals, strict=True)),
        human_confirmation=HUMAN_CONFIRMATION,
        conditions=tuple(Condition(item, payload.conditions_present) for item in CONDITIONS),
        commands=tuple(Command(item, payload.commands_documentation_only) for item in COMMANDS),
        stop_rules=tuple(StopRule(item, payload.stop_rules_present) for item in STOP_RULES),
    )


def review_final_tag_creation_human_confirmation_prerequisites(context: Context | None, data: ConfirmationInput | Mapping[str, Any] | None = None) -> bool:
    payload = _coerce(data) if data is not None else None
    flags_ok = True
    if payload is not None:
        flags_ok = (
            payload.prerequisites_complete
            and payload.command_sheet_review_approved
            and payload.command_sheet_approved
            and payload.final_manual_tag_authorization_approved
            and payload.execution_plan_review_approved
            and payload.manual_tag_creation_approval_approved
            and payload.human_tag_go_no_go_approved
            and payload.release_package_review_approved
            and payload.final_readiness_review_approved
        )
    return bool(context and flags_ok and len(context.prerequisites) == len(PREREQUISITES) and all(item.approved for item in context.prerequisites))


def review_final_tag_creation_human_confirmation_command_sheet_review(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.command_sheet_review_approved)


def review_final_tag_creation_human_confirmation_final_authorization(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.final_manual_tag_authorization_approved)


def review_final_tag_creation_human_confirmation_tag_name(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_final_tag_creation_human_confirmation_version(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_final_tag_creation_human_confirmation_conditions(context: Context | None) -> bool:
    return bool(context and len(context.conditions) == len(CONDITIONS) and all(item.present for item in context.conditions))


def review_final_tag_creation_human_confirmation_documented_commands_only(context: Context | None) -> bool:
    return bool(context and len(context.commands) == len(COMMANDS) and all(item.documentation_only for item in context.commands))


def review_final_tag_creation_human_confirmation_stop_rules(context: Context | None) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(item.present for item in context.stop_rules))


def review_final_tag_creation_human_confirmation_no_git_tag_created(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_created)


def review_final_tag_creation_human_confirmation_no_git_tag_pushed(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_final_tag_creation_human_confirmation_no_live_trading_claim(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_final_tag_creation_human_confirmation_no_profitability_claim(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.profitability_overclaim)


def review_final_tag_creation_human_confirmation_no_financial_advice_claim(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _boundary_risks(data: ConfirmationInput | None) -> tuple[Risk, ...]:
    if data is None:
        return ()
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
    return _dedupe(risk for flag, risk in checks if flag)


def assert_agicore_trading_v1_offline_final_tag_creation_human_confirmation_boundaries(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    return not _boundary_risks(_coerce(data))


def validate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_input(data: ConfirmationInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.confirmation_id and review_final_tag_creation_human_confirmation_no_git_tag_created(payload) and review_final_tag_creation_human_confirmation_no_git_tag_pushed(payload) and assert_agicore_trading_v1_offline_final_tag_creation_human_confirmation_boundaries(payload))


def detect_agicore_trading_v1_offline_final_tag_creation_human_confirmation_risks(data: ConfirmationInput | Mapping[str, Any] | None, context: Context | None = None) -> tuple[Risk, ...]:
    payload = _coerce(data)
    if payload is None:
        return (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING,)
    checks = (
        (not review_final_tag_creation_human_confirmation_prerequisites(context, payload), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE),
        (not payload.command_sheet_review_approved, Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED),
        (not payload.final_manual_tag_authorization_approved, Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        (not payload.execution_plan_review_approved, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        (not payload.manual_tag_creation_approval_approved, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        (not payload.human_tag_go_no_go_approved, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        (not payload.release_package_review_approved, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        (not payload.final_readiness_review_approved, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED),
        (not review_final_tag_creation_human_confirmation_tag_name(payload), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID),
        (not review_final_tag_creation_human_confirmation_version(payload), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID),
        (not review_final_tag_creation_human_confirmation_conditions(context), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING),
        (not review_final_tag_creation_human_confirmation_documented_commands_only(context), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY),
        (not review_final_tag_creation_human_confirmation_stop_rules(context), Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING),
        (payload.git_tag_already_created, Risk.GIT_TAG_ALREADY_CREATED),
        (payload.git_tag_already_pushed, Risk.GIT_TAG_ALREADY_PUSHED),
        (payload.live_trading_overclaim, Risk.LIVE_TRADING_READINESS_OVERCLAIM),
        (payload.real_broker_overclaim, Risk.REAL_BROKER_READINESS_OVERCLAIM),
        (payload.real_order_overclaim, Risk.REAL_ORDER_EXECUTION_OVERCLAIM),
        (payload.paper_broker_overclaim, Risk.PAPER_BROKER_CONNECTION_OVERCLAIM),
        (payload.profitability_overclaim, Risk.PROFITABILITY_PROOF_OVERCLAIM),
        (payload.financial_advice_overclaim, Risk.FINANCIAL_ADVICE_OVERCLAIM),
    )
    risks = [risk for flag, risk in checks if flag]
    risks.extend(_boundary_risks(payload))
    return _dedupe(risks)


def _safe(data: ConfirmationInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def compute_agicore_trading_v1_offline_final_tag_creation_human_confirmation_score(data: ConfirmationInput | Mapping[str, Any] | None, context: Context | None, risks: tuple[Risk, ...]) -> Score:
    payload = _coerce(data)
    values = (
        100 if validate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_input(payload) else 0,
        100 if review_final_tag_creation_human_confirmation_prerequisites(context, payload) else 0,
        100 if review_final_tag_creation_human_confirmation_tag_name(payload) else 0,
        100 if review_final_tag_creation_human_confirmation_version(payload) else 0,
        100 if review_final_tag_creation_human_confirmation_conditions(context) else 0,
        100 if review_final_tag_creation_human_confirmation_documented_commands_only(context) else 0,
        100 if review_final_tag_creation_human_confirmation_stop_rules(context) else 0,
        100 if review_final_tag_creation_human_confirmation_no_git_tag_created(payload) and review_final_tag_creation_human_confirmation_no_git_tag_pushed(payload) else 0,
        100 if _safe(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return Score(overall, *values)


def generate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_recommendations(risks: Iterable[Risk]) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING: Recommendation.PROVIDE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_NAME,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID: Recommendation.RESTORE_VERSION,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING: Recommendation.RESTORE_CONDITIONS,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_COMMANDS_DOCUMENTATION_ONLY,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING: Recommendation.RESTORE_STOP_RULES,
        Risk.GIT_TAG_ALREADY_CREATED: Recommendation.DO_NOT_CREATE_GIT_TAG_IN_THIS_PHASE,
        Risk.GIT_TAG_ALREADY_PUSHED: Recommendation.DO_NOT_PUSH_GIT_TAG_IN_THIS_PHASE,
    }
    output: list[Recommendation] = []
    for risk in risks:
        if risk in mapping:
            output.append(mapping[risk])
        elif "OVERCLAIM" in risk.value:
            output.append(Recommendation.REMOVE_OVERCLAIM)
        elif "BOUNDARY_VIOLATION" in risk.value:
            output.append(Recommendation.REMOVE_BOUNDARY_VIOLATION)
    return _dedupe(output or [Recommendation.PREPARE_TAG_CREATION_FINAL_PREFLIGHT])


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION
    if Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_MISSING in risks:
        return Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_FIXES
    prerequisite = {
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITES_INCOMPLETE,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED,
    }
    if any(risk in prerequisite for risk in risks):
        return Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_PREREQUISITE_FIXES
    ordered = (
        (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_INVALID, Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_TAG_NAME_FIXES),
        (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_INVALID, Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_VERSION_FIXES),
        (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITIONS_MISSING, Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_CONDITION_FIXES),
        (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMANDS_NOT_DOCUMENTATION_ONLY, Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_COMMAND_DOCUMENTATION_FIXES),
        (Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULES_MISSING, Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_STOP_RULE_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.REQUIRE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NO_OVERCLAIM_FIXES


def _state_for(data: ConfirmationInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT
    return State.AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION_BLOCKED


def render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_markdown(context: Context | None) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Final Tag Creation Human Confirmation",
        "",
        "## Statut",
        "",
        "human confirmation only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION",
        "",
        "## Conclusion",
        "",
        "- confirmation humaine finale prete",
        "- Bama pourra creer le tag manuellement plus tard uniquement apres derniere verification locale",
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
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Confirmation humaine", "", f"- {context.human_confirmation if context else ''}", "", "## Conditions avant toute creation reelle future", ""))
    lines.extend(f"- {item.condition}" for item in (context.conditions if context else ()) if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {item.rule}" for item in (context.stop_rules if context else ()) if item.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Tag Creation Final Preflight"))
    return "\n".join(lines) + "\n"


def validate_final_tag_creation_human_confirmation_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Final Tag Creation Human Confirmation",
        "human confirmation only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_FINAL_TAG_CREATION_HUMAN_CONFIRMATION",
        "confirmation humaine finale prete",
        "Bama pourra creer le tag manuellement plus tard uniquement apres derniere verification locale",
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
        HUMAN_CONFIRMATION,
        *CONDITIONS,
        *COMMANDS,
        *STOP_RULES,
        "AGIcore Trading v1 Offline Tag Creation Final Preflight",
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


def render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_json_report(result: Result | Mapping[str, Any]) -> str:
    if isinstance(result, Result):
        payload = {
            "schema": "agicore_trading_v1_offline_final_tag_creation_human_confirmation",
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
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def evaluate_agicore_trading_v1_offline_final_tag_creation_human_confirmation(data: ConfirmationInput | Mapping[str, Any] | None) -> Result:
    payload = _coerce(data)
    context = build_final_tag_creation_human_confirmation_context(payload)
    risks = detect_agicore_trading_v1_offline_final_tag_creation_human_confirmation_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_final_tag_creation_human_confirmation_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_final_tag_creation_human_confirmation_recommendations(risks)
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
        markdown=render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_markdown(context),
        json=render_agicore_trading_v1_offline_final_tag_creation_human_confirmation_json_report(base),
    )
    return Result(**{**base.__dict__, "report": report})
