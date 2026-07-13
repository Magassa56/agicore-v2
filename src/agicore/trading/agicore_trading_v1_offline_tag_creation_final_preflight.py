"""AGIcore Trading v1 offline tag creation final preflight."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_tag_creation_final_preflight_models import (
    AGIcoreTradingV1OfflineTagCreationFinalPreflightCheck as Check,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightCommand as Command,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightContext as Context,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightDecision as Decision,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightExpectedResult as ExpectedResult,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightInput as PreflightInput,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightPrerequisite as Prerequisite,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightRecommendation as Recommendation,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightReport as Report,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightResult as Result,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightRisk as Risk,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightScore as Score,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightState as State,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightStopRule as StopRule,
    AGIcoreTradingV1OfflineTagCreationFinalPreflightTagMetadata as TagMetadata,
)

EXPECTED_TAG_NAME = "agicore-trading-v1-offline"
EXPECTED_VERSION = "v1.0.0-offline"
PREREQUISITES = (
    "Final Tag Creation Human Confirmation approuvee",
    "Manual Tag Creation Command Sheet Review approuvee",
    "Final Manual Tag Authorization approuvee",
    "Tag Creation Execution Plan Review approuvee",
    "Manual Tag Creation Approval approuvee",
    "Human Tag Go/No-Go approuve",
    "Release Package Review approuvee",
    "Final Readiness Review approuvee",
)
REQUIRED_CHECKS = (
    "Bama confirme explicitement lintention de creer le tag",
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
    "confirmation humaine explicite presente",
    "tests unitaires verts",
    "git status --short retourne seulement ?? data/",
    "git diff --check OK",
    "git diff --cached --name-only ne retourne rien",
    "git tag --list agicore-trading-v1-offline ne retourne rien",
    "git ls-remote --tags origin agicore-trading-v1-offline ne retourne rien",
    "data/ nest pas staged",
)
COMMANDS = (
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
    "STOP si git diff --check echoue",
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


def _coerce(data: PreflightInput | Mapping[str, Any] | None) -> PreflightInput | None:
    if data is None or isinstance(data, PreflightInput):
        return data
    allowed = {field.name for field in fields(PreflightInput)}
    return PreflightInput(**{key: value for key, value in dict(data).items() if key in allowed})


def build_tag_creation_final_preflight_context(data: PreflightInput | Mapping[str, Any] | None) -> Context | None:
    payload = _coerce(data)
    if payload is None:
        return None
    approvals = (
        payload.final_tag_creation_human_confirmation_approved,
        payload.command_sheet_review_approved,
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
        preflight_id=payload.preflight_id,
        tag_metadata=TagMetadata(payload.tag_name, payload.version),
        prerequisites=tuple(Prerequisite(name, approved) for name, approved in zip(PREREQUISITES, approvals, strict=True)),
        human_confirmation_present=payload.human_confirmation_present,
        required_checks=tuple(Check(item, payload.required_checks_present) for item in REQUIRED_CHECKS),
        expected_results=tuple(ExpectedResult(item, payload.expected_results_present) for item in EXPECTED_RESULTS),
        commands=tuple(Command(item, payload.commands_documentation_only) for item in COMMANDS),
        stop_rules=tuple(StopRule(item, payload.stop_rules_present) for item in STOP_RULES),
    )


def review_tag_creation_final_preflight_prerequisites(context: Context | None, data: PreflightInput | Mapping[str, Any] | None = None) -> bool:
    payload = _coerce(data) if data is not None else None
    flags_ok = True
    if payload is not None:
        flags_ok = (
            payload.prerequisites_complete
            and payload.final_tag_creation_human_confirmation_approved
            and payload.command_sheet_review_approved
            and payload.final_manual_tag_authorization_approved
            and payload.execution_plan_review_approved
            and payload.manual_tag_creation_approval_approved
            and payload.human_tag_go_no_go_approved
            and payload.release_package_review_approved
            and payload.final_readiness_review_approved
        )
    return bool(context and flags_ok and len(context.prerequisites) == len(PREREQUISITES) and all(item.approved for item in context.prerequisites))


def review_tag_creation_final_preflight_human_confirmation(context: Context | None) -> bool:
    return bool(context and context.human_confirmation_present)


def review_tag_creation_final_preflight_tag_name(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.tag_name == EXPECTED_TAG_NAME)


def review_tag_creation_final_preflight_version(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.version == EXPECTED_VERSION)


def review_tag_creation_final_preflight_required_checks(context: Context | None) -> bool:
    return bool(context and len(context.required_checks) == len(REQUIRED_CHECKS) and all(item.present for item in context.required_checks))


def review_tag_creation_final_preflight_expected_results(context: Context | None) -> bool:
    return bool(context and len(context.expected_results) == len(EXPECTED_RESULTS) and all(item.present for item in context.expected_results))


def review_tag_creation_final_preflight_documented_commands_only(context: Context | None) -> bool:
    return bool(context and len(context.commands) == len(COMMANDS) and all(item.documentation_only for item in context.commands))


def review_tag_creation_final_preflight_stop_rules(context: Context | None) -> bool:
    return bool(context and len(context.stop_rules) == len(STOP_RULES) and all(item.present for item in context.stop_rules))


def review_tag_creation_final_preflight_no_git_tag_created(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_created)


def review_tag_creation_final_preflight_no_git_tag_pushed(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.git_tag_already_pushed)


def review_tag_creation_final_preflight_no_live_trading_claim(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.live_trading_overclaim)


def review_tag_creation_final_preflight_no_profitability_claim(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.profitability_overclaim)


def review_tag_creation_final_preflight_no_financial_advice_claim(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and not payload.financial_advice_overclaim)


def _boundary_risks(data: PreflightInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_tag_creation_final_preflight_boundaries(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    return not _boundary_risks(_coerce(data))


def validate_agicore_trading_v1_offline_tag_creation_final_preflight_input(data: PreflightInput | Mapping[str, Any] | None) -> bool:
    payload = _coerce(data)
    return bool(payload and payload.preflight_id and review_tag_creation_final_preflight_no_git_tag_created(payload) and review_tag_creation_final_preflight_no_git_tag_pushed(payload) and assert_agicore_trading_v1_offline_tag_creation_final_preflight_boundaries(payload))


def detect_agicore_trading_v1_offline_tag_creation_final_preflight_risks(data: PreflightInput | Mapping[str, Any] | None, context: Context | None = None) -> tuple[Risk, ...]:
    payload = _coerce(data)
    if payload is None:
        return (Risk.TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING,)
    checks = (
        (not review_tag_creation_final_preflight_prerequisites(context, payload), Risk.TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE),
        (not payload.final_tag_creation_human_confirmation_approved, Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NOT_APPROVED),
        (not payload.command_sheet_review_approved, Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED),
        (not payload.final_manual_tag_authorization_approved, Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED),
        (not payload.execution_plan_review_approved, Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED),
        (not payload.manual_tag_creation_approval_approved, Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED),
        (not payload.human_tag_go_no_go_approved, Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED),
        (not payload.release_package_review_approved, Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED),
        (not payload.final_readiness_review_approved, Risk.FINAL_READINESS_REVIEW_NOT_APPROVED),
        (not review_tag_creation_final_preflight_human_confirmation(context), Risk.TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING),
        (not review_tag_creation_final_preflight_tag_name(payload), Risk.TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID),
        (not review_tag_creation_final_preflight_version(payload), Risk.TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID),
        (not review_tag_creation_final_preflight_required_checks(context), Risk.TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING),
        (not review_tag_creation_final_preflight_expected_results(context), Risk.TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING),
        (not review_tag_creation_final_preflight_documented_commands_only(context), Risk.TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY),
        (not review_tag_creation_final_preflight_stop_rules(context), Risk.TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING),
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


def _safe(data: PreflightInput | None) -> bool:
    return bool(data and not data.live_trading_overclaim and not data.real_broker_overclaim and not data.real_order_overclaim and not data.paper_broker_overclaim and not data.profitability_overclaim and not data.financial_advice_overclaim)


def compute_agicore_trading_v1_offline_tag_creation_final_preflight_score(data: PreflightInput | Mapping[str, Any] | None, context: Context | None, risks: tuple[Risk, ...]) -> Score:
    payload = _coerce(data)
    values = (
        100 if validate_agicore_trading_v1_offline_tag_creation_final_preflight_input(payload) else 0,
        100 if review_tag_creation_final_preflight_prerequisites(context, payload) else 0,
        100 if review_tag_creation_final_preflight_human_confirmation(context) else 0,
        100 if review_tag_creation_final_preflight_tag_name(payload) else 0,
        100 if review_tag_creation_final_preflight_version(payload) else 0,
        100 if review_tag_creation_final_preflight_required_checks(context) else 0,
        100 if review_tag_creation_final_preflight_expected_results(context) else 0,
        100 if review_tag_creation_final_preflight_documented_commands_only(context) else 0,
        100 if review_tag_creation_final_preflight_stop_rules(context) else 0,
        100 if review_tag_creation_final_preflight_no_git_tag_created(payload) and review_tag_creation_final_preflight_no_git_tag_pushed(payload) else 0,
        100 if _safe(payload) else 0,
        100 if not _boundary_risks(payload) else 0,
    )
    overall = min(values)
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return Score(overall, *values)


def generate_agicore_trading_v1_offline_tag_creation_final_preflight_recommendations(risks: Iterable[Risk]) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING: Recommendation.PROVIDE_FINAL_PREFLIGHT_INPUT,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE: Recommendation.RESTORE_PREREQUISITES,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING: Recommendation.RESTORE_HUMAN_CONFIRMATION,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID: Recommendation.RESTORE_TAG_NAME,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID: Recommendation.RESTORE_VERSION,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING: Recommendation.RESTORE_REQUIRED_CHECKS,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING: Recommendation.RESTORE_EXPECTED_RESULTS,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY: Recommendation.KEEP_COMMANDS_DOCUMENTATION_ONLY,
        Risk.TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING: Recommendation.RESTORE_STOP_RULES,
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
    return _dedupe(output or [Recommendation.PREPARE_FINAL_PREFLIGHT_REVIEW])


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT
    if Risk.TAG_CREATION_FINAL_PREFLIGHT_INPUT_MISSING in risks:
        return Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_FIXES
    prerequisite = {
        Risk.TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITES_INCOMPLETE,
        Risk.FINAL_TAG_CREATION_HUMAN_CONFIRMATION_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_COMMAND_SHEET_REVIEW_NOT_APPROVED,
        Risk.FINAL_MANUAL_TAG_AUTHORIZATION_NOT_APPROVED,
        Risk.TAG_CREATION_EXECUTION_PLAN_REVIEW_NOT_APPROVED,
        Risk.MANUAL_TAG_CREATION_APPROVAL_NOT_APPROVED,
        Risk.HUMAN_TAG_GO_NO_GO_NOT_APPROVED,
        Risk.RELEASE_PACKAGE_REVIEW_NOT_APPROVED,
        Risk.FINAL_READINESS_REVIEW_NOT_APPROVED,
    }
    if any(risk in prerequisite for risk in risks):
        return Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_PREREQUISITE_FIXES
    ordered = (
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_MISSING, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_HUMAN_CONFIRMATION_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_INVALID, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_TAG_NAME_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_VERSION_INVALID, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_VERSION_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_CHECKS_MISSING, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_CHECK_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULTS_MISSING, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_EXPECTED_RESULT_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_COMMANDS_NOT_DOCUMENTATION_ONLY, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_COMMAND_DOCUMENTATION_FIXES),
        (Risk.TAG_CREATION_FINAL_PREFLIGHT_STOP_RULES_MISSING, Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_STOP_RULE_FIXES),
    )
    for risk, decision in ordered:
        if risk in risks:
            return decision
    return Decision.REQUIRE_TAG_CREATION_FINAL_PREFLIGHT_NO_OVERCLAIM_FIXES


def _state_for(data: PreflightInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_REVIEW
    return State.AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT_BLOCKED


def render_agicore_trading_v1_offline_tag_creation_final_preflight_markdown(context: Context | None) -> str:
    metadata = context.tag_metadata if context else None
    lines = [
        "# AGIcore Trading v1 Offline Tag Creation Final Preflight",
        "",
        "## Statut",
        "",
        "final preflight only, no Git tag created",
        "",
        "## Decision attendue",
        "",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT",
        "",
        "## Conclusion",
        "",
        "- preflight final pret",
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
    lines.extend(("", "## Tag propose", "", f"- {metadata.tag_name if metadata else ''}", "", "## Version proposee", "", f"- {metadata.version if metadata else ''}"))
    lines.extend(("", "## Preflight obligatoire avant creation reelle future", ""))
    lines.extend(f"{index}. {item.check}" for index, item in enumerate((context.required_checks if context else ()), start=1) if item.present)
    lines.extend(("", "## Resultats attendus", ""))
    lines.extend(f"- {item.result}" for item in (context.expected_results if context else ()) if item.present)
    lines.extend(("", "## Commandes futures documentees uniquement", ""))
    lines.extend(f"- {item.command}" for item in (context.commands if context else ()) if item.documentation_only)
    lines.extend(("", "## Procedure STOP", ""))
    lines.extend(f"- {item.rule}" for item in (context.stop_rules if context else ()) if item.present)
    lines.extend(("", "## Prochaine etape suggeree", "", "AGIcore Trading v1 Offline Tag Creation Final Preflight Review"))
    return "\n".join(lines) + "\n"


def validate_tag_creation_final_preflight_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Tag Creation Final Preflight",
        "final preflight only, no Git tag created",
        "APPROVE_AGICORE_TRADING_V1_OFFLINE_TAG_CREATION_FINAL_PREFLIGHT",
        "preflight final pret",
        "creation reelle du tag reservee a une action manuelle future de Bama",
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
        *REQUIRED_CHECKS,
        *EXPECTED_RESULTS,
        *COMMANDS,
        *STOP_RULES,
        "AGIcore Trading v1 Offline Tag Creation Final Preflight Review",
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


def render_agicore_trading_v1_offline_tag_creation_final_preflight_json_report(result: Result | Mapping[str, Any]) -> str:
    if isinstance(result, Result):
        payload = {
            "schema": "agicore_trading_v1_offline_tag_creation_final_preflight",
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


def evaluate_agicore_trading_v1_offline_tag_creation_final_preflight(data: PreflightInput | Mapping[str, Any] | None) -> Result:
    payload = _coerce(data)
    context = build_tag_creation_final_preflight_context(payload)
    risks = detect_agicore_trading_v1_offline_tag_creation_final_preflight_risks(payload, context)
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_tag_creation_final_preflight_score(payload, context, risks)
    recommendations = generate_agicore_trading_v1_offline_tag_creation_final_preflight_recommendations(risks)
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
        markdown=render_agicore_trading_v1_offline_tag_creation_final_preflight_markdown(context),
        json=render_agicore_trading_v1_offline_tag_creation_final_preflight_json_report(base),
    )
    return Result(**{**base.__dict__, "report": report})
