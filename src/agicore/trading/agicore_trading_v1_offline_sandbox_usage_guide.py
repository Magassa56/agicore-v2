"""AGIcore Trading v1 offline sandbox usage guide builder."""

from __future__ import annotations

import json
from dataclasses import fields
from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.agicore_trading_v1_offline_sandbox_usage_guide_models import (
    AGIcoreTradingV1OfflineSandboxUsageGuideCommand,
    AGIcoreTradingV1OfflineSandboxUsageGuideContext,
    AGIcoreTradingV1OfflineSandboxUsageGuideDecision,
    AGIcoreTradingV1OfflineSandboxUsageGuideInput,
    AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation,
    AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation,
    AGIcoreTradingV1OfflineSandboxUsageGuideReport,
    AGIcoreTradingV1OfflineSandboxUsageGuideResult,
    AGIcoreTradingV1OfflineSandboxUsageGuideRisk,
    AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule,
    AGIcoreTradingV1OfflineSandboxUsageGuideScore,
    AGIcoreTradingV1OfflineSandboxUsageGuideSection,
    AGIcoreTradingV1OfflineSandboxUsageGuideState,
)


Risk = AGIcoreTradingV1OfflineSandboxUsageGuideRisk
Recommendation = AGIcoreTradingV1OfflineSandboxUsageGuideRecommendation
Decision = AGIcoreTradingV1OfflineSandboxUsageGuideDecision
State = AGIcoreTradingV1OfflineSandboxUsageGuideState

SAFETY_RULES = (
    "pas de trading reel",
    "pas de broker reel",
    "pas d'Alpaca reel",
    "pas d'ordre reel",
    "pas d'acces compte reel",
    "pas de mutation position reelle",
    "pas de lecture data/",
    "pas d'ecriture data/",
    "pas de reseau",
    "pas de cle API",
    "pas de preuve de rentabilite",
    "pas de conseil financier",
)

COMMANDS = (
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "Valide la smoke demo V1 offline.",
    ),
    (
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q",
        "Valide la review de la smoke demo V1 offline.",
    ),
    ("python -m pytest tests/unit/ -q", "Lance la suite unitaire complete."),
)

LIMITATIONS = (
    "strategies simples seulement",
    "donnees synthetiques ou CSV string en memoire seulement",
    "pas de vraie persistance",
    "pas de vraie interface utilisateur",
    "pas de paper broker connecte",
    "pas de donnees reelles automatisees",
    "pas de rentabilite validee",
)

INTERPRETATION_LINES = (
    "APPROVE signifie seulement sandbox/offline OK",
    "score 100 ne prouve pas une rentabilite",
    "risks [] ne signifie pas absence de risque financier reel",
    "broker preview est simule uniquement",
    "read-only decision n'est pas un ordre",
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
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSandboxUsageGuideInput | None:
    if data is None:
        return None
    if isinstance(data, AGIcoreTradingV1OfflineSandboxUsageGuideInput):
        return data
    allowed = {field.name for field in fields(AGIcoreTradingV1OfflineSandboxUsageGuideInput)}
    return AGIcoreTradingV1OfflineSandboxUsageGuideInput(**{key: value for key, value in dict(data).items() if key in allowed})


def validate_agicore_trading_v1_offline_sandbox_usage_guide_input(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> bool:
    payload = _coerce_input(data)
    return bool(payload and payload.guide_id and assert_agicore_trading_v1_offline_sandbox_usage_guide_boundaries(payload))


def build_sandbox_usage_guide_context(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSandboxUsageGuideContext:
    _coerce_input(data)
    return AGIcoreTradingV1OfflineSandboxUsageGuideContext(
        title="AGIcore Trading v1 Offline Sandbox Usage Guide",
        status="offline/sandbox only",
        next_step="AGIcore Trading v1 Offline Local Runbook",
    )


def _safety_rules(data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | None) -> tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...]:
    if data and data.force_safety_language_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule(text) for text in SAFETY_RULES)


def _commands(data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | None) -> tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...]:
    if data and data.force_commands_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineSandboxUsageGuideCommand(command, description) for command, description in COMMANDS)


def _limitations(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | None,
) -> tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...]:
    if data and data.force_limitations_missing:
        return ()
    return tuple(AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation(text) for text in LIMITATIONS)


def build_sandbox_usage_guide_safety_section(
    safety_rules: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...],
) -> str:
    lines = ["## Rappel de securite", ""]
    lines.extend(f"- {rule.text}" for rule in safety_rules)
    return "\n".join(lines)


def build_sandbox_usage_guide_prerequisites_section() -> str:
    return "\n".join(
        (
            "## Prerequis locaux",
            "",
            "- etre sur main a jour",
            "- environnement Python local",
            "- dependances deja installees",
            "- ne pas configurer de cle API",
            "- ne pas connecter de broker",
        )
    )


def build_sandbox_usage_guide_commands_section(
    commands: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...],
) -> str:
    lines = ["## Commandes recommandees", ""]
    lines.extend(f"- `{command.command}` : {command.description}" for command in commands)
    return "\n".join(lines)


def build_sandbox_usage_guide_memory_usage_example_section(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> str:
    payload = _coerce_input(data)
    if payload and payload.force_memory_example_missing:
        return ""
    return "\n".join(
        (
            "## Exemple d'usage en memoire",
            "",
            "Utiliser uniquement `PYTHONPATH=src`.",
            "",
            "```python",
            "from agicore.trading.agicore_trading_v1_offline_smoke_demo import (",
            "    run_agicore_trading_v1_offline_smoke_demo,",
            ")",
            "",
            "result = run_agicore_trading_v1_offline_smoke_demo()",
            "print(result.decision)",
            "print(result.state)",
            "print(result.score.overall_score)",
            "print(result.risks)",
            "print(result.recommendations)",
            "```",
        )
    )


def build_sandbox_usage_guide_result_interpretation_section(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> str:
    payload = _coerce_input(data)
    if payload and payload.force_result_interpretation_missing:
        return ""
    lines = ["## Interpretation des resultats", ""]
    lines.extend(f"- {line}" for line in INTERPRETATION_LINES)
    return "\n".join(lines)


def build_sandbox_usage_guide_known_limitations_section(
    limitations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...],
) -> str:
    lines = ["## Limites connues", ""]
    lines.extend(f"- {limitation.text}" for limitation in limitations)
    return "\n".join(lines)


def build_sandbox_usage_guide_workflow_section() -> str:
    return "\n".join(
        (
            "## Workflow recommande",
            "",
            "- lancer les tests",
            "- lancer smoke demo",
            "- lire rapport",
            "- ne rien connecter au reel",
            "- continuer par les prochaines phases",
        )
    )


def build_sandbox_usage_guide_next_steps_section(
    context: AGIcoreTradingV1OfflineSandboxUsageGuideContext,
) -> str:
    return f"## Prochaine etape suggeree\n\n{context.next_step}"


def render_agicore_trading_v1_offline_sandbox_usage_guide_markdown(
    context: AGIcoreTradingV1OfflineSandboxUsageGuideContext,
    safety_rules: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...],
    commands: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...],
    limitations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...],
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None = None,
) -> str:
    sections = [
        f"# {context.title}",
        "## Statut\n\n" + context.status,
        build_sandbox_usage_guide_safety_section(safety_rules),
        build_sandbox_usage_guide_prerequisites_section(),
        build_sandbox_usage_guide_commands_section(commands),
        build_sandbox_usage_guide_memory_usage_example_section(data),
        build_sandbox_usage_guide_result_interpretation_section(data),
        build_sandbox_usage_guide_known_limitations_section(limitations),
        build_sandbox_usage_guide_workflow_section(),
        build_sandbox_usage_guide_next_steps_section(context),
    ]
    return "\n\n".join(section for section in sections if section) + "\n"


def validate_sandbox_usage_guide_markdown(markdown: str) -> bool:
    required = (
        "AGIcore Trading v1 Offline Sandbox Usage Guide",
        "offline/sandbox only",
        "pas de trading reel",
        "pas de broker reel",
        "pas d'Alpaca reel",
        "pas d'ordre reel",
        "pas d'acces compte reel",
        "pas de mutation position reelle",
        "pas de lecture data/",
        "pas d'ecriture data/",
        "pas de reseau",
        "pas de cle API",
        "pas de preuve de rentabilite",
        "pas de conseil financier",
        "etre sur main a jour",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo.py -q",
        "python -m pytest tests/unit/trading/test_agicore_trading_v1_offline_smoke_demo_review.py -q",
        "python -m pytest tests/unit/ -q",
        "PYTHONPATH=src",
        "run_agicore_trading_v1_offline_smoke_demo",
        "APPROVE signifie seulement sandbox/offline OK",
        "score 100 ne prouve pas une rentabilite",
        "broker preview est simule uniquement",
        "read-only decision n'est pas un ordre",
        "strategies simples seulement",
        "pas de paper broker connecte",
        "AGIcore Trading v1 Offline Local Runbook",
    )
    return all(item in markdown for item in required)


def validate_sandbox_usage_guide_safety_language(markdown: str) -> bool:
    return all(item in markdown for item in SAFETY_RULES)


def validate_sandbox_usage_guide_no_overclaims(markdown: str) -> bool:
    forbidden = (
        "live_trading_ready: true",
        "real_broker_ready: true",
        "real_order_execution: true",
        "profitability_proven: true",
        "financial_advice: true",
        "ready for live trading",
        "profitability proven",
    )
    lowered = markdown.lower()
    return all(item not in lowered for item in forbidden)


def _boundary_risks(data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | None) -> tuple[Risk, ...]:
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


def assert_agicore_trading_v1_offline_sandbox_usage_guide_boundaries(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> bool:
    return not _boundary_risks(_coerce_input(data))


def detect_agicore_trading_v1_offline_sandbox_usage_guide_risks(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
    markdown: str = "",
    commands: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...] = (),
    safety_rules: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...] = (),
    limitations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...] = (),
) -> tuple[Risk, ...]:
    payload = _coerce_input(data)
    risks: list[Risk] = []
    if payload is None:
        risks.append(Risk.SANDBOX_USAGE_GUIDE_INPUT_MISSING)
    if len(safety_rules) != len(SAFETY_RULES) or (markdown and not validate_sandbox_usage_guide_safety_language(markdown)):
        risks.append(Risk.SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING)
    if len(commands) != len(COMMANDS):
        risks.append(Risk.SANDBOX_USAGE_GUIDE_COMMANDS_MISSING)
    if not markdown or "run_agicore_trading_v1_offline_smoke_demo" not in markdown:
        risks.append(Risk.SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING)
    if "APPROVE signifie seulement sandbox/offline OK" not in markdown:
        risks.append(Risk.SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING)
    if len(limitations) != len(LIMITATIONS):
        risks.append(Risk.SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING)
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


def compute_agicore_trading_v1_offline_sandbox_usage_guide_score(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
    markdown: str,
    commands: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideCommand, ...],
    safety_rules: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideSafetyRule, ...],
    limitations: tuple[AGIcoreTradingV1OfflineSandboxUsageGuideKnownLimitation, ...],
    risks: tuple[Risk, ...],
) -> AGIcoreTradingV1OfflineSandboxUsageGuideScore:
    payload = _coerce_input(data)
    input_score = 100 if validate_agicore_trading_v1_offline_sandbox_usage_guide_input(payload) else 0
    safety_score = 100 if len(safety_rules) == len(SAFETY_RULES) and validate_sandbox_usage_guide_safety_language(markdown) else 0
    command_score = 100 if len(commands) == len(COMMANDS) else 0
    memory_score = 100 if "run_agicore_trading_v1_offline_smoke_demo" in markdown and "PYTHONPATH=src" in markdown else 0
    interpretation_score = 100 if all(item in markdown for item in INTERPRETATION_LINES) else 0
    limitation_score = 100 if len(limitations) == len(LIMITATIONS) else 0
    overclaim_score = 100 if validate_sandbox_usage_guide_no_overclaims(markdown) and not {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    } & set(risks) else 0
    boundary_score = 100 if not _boundary_risks(payload) else 0
    overall = min(
        input_score,
        safety_score,
        command_score,
        memory_score,
        interpretation_score,
        limitation_score,
        overclaim_score,
        boundary_score,
    )
    if risks:
        overall = min(overall, max(0, 100 - len(risks) * 10))
    return AGIcoreTradingV1OfflineSandboxUsageGuideScore(
        overall_score=overall,
        input_score=input_score,
        safety_score=safety_score,
        command_score=command_score,
        memory_example_score=memory_score,
        interpretation_score=interpretation_score,
        limitation_score=limitation_score,
        overclaim_score=overclaim_score,
        boundary_score=boundary_score,
    )


def generate_agicore_trading_v1_offline_sandbox_usage_guide_recommendations(
    risks: Iterable[Risk],
) -> tuple[Recommendation, ...]:
    mapping = {
        Risk.SANDBOX_USAGE_GUIDE_INPUT_MISSING: Recommendation.PROVIDE_SANDBOX_USAGE_GUIDE_INPUT,
        Risk.SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING: Recommendation.RESTORE_SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE,
        Risk.SANDBOX_USAGE_GUIDE_COMMANDS_MISSING: Recommendation.RESTORE_SANDBOX_USAGE_GUIDE_COMMANDS,
        Risk.SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING: Recommendation.RESTORE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE,
        Risk.SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING: Recommendation.RESTORE_SANDBOX_USAGE_GUIDE_INTERPRETATION,
        Risk.SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING: Recommendation.RESTORE_SANDBOX_USAGE_GUIDE_LIMITATIONS,
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
        recommendations.append(Recommendation.PREPARE_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK)
    return _dedupe(recommendations)


def _decision_for(risks: tuple[Risk, ...]) -> Decision:
    if not risks:
        return Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE
    if Risk.SANDBOX_USAGE_GUIDE_INPUT_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_INPUT_FIXES
    if Risk.SANDBOX_USAGE_GUIDE_SAFETY_LANGUAGE_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_SAFETY_FIXES
    if Risk.SANDBOX_USAGE_GUIDE_COMMANDS_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_COMMAND_FIXES
    if Risk.SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_MEMORY_EXAMPLE_FIXES
    if Risk.SANDBOX_USAGE_GUIDE_RESULT_INTERPRETATION_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_INTERPRETATION_FIXES
    if Risk.SANDBOX_USAGE_GUIDE_LIMITATIONS_MISSING in risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_LIMITATION_FIXES
    overclaim_risks = {
        Risk.LIVE_TRADING_READINESS_OVERCLAIM,
        Risk.REAL_BROKER_READINESS_OVERCLAIM,
        Risk.REAL_ORDER_EXECUTION_OVERCLAIM,
        Risk.PROFITABILITY_PROOF_OVERCLAIM,
        Risk.FINANCIAL_ADVICE_OVERCLAIM,
    }
    if set(risks) & overclaim_risks:
        return Decision.REQUIRE_SANDBOX_USAGE_GUIDE_NO_OVERCLAIM_FIXES
    return Decision.BLOCK_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE


def _state_for(data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | None, decision: Decision) -> State:
    if data is None:
        return State.AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_INPUT_INVALID
    if decision is Decision.APPROVE_AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE:
        return State.READY_FOR_AGICORE_TRADING_V1_OFFLINE_LOCAL_RUNBOOK
    return State.AGICORE_TRADING_V1_OFFLINE_SANDBOX_USAGE_GUIDE_BLOCKED


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


def render_agicore_trading_v1_offline_sandbox_usage_guide_json_report(
    result: AGIcoreTradingV1OfflineSandboxUsageGuideResult | Mapping[str, Any],
) -> str:
    if isinstance(result, AGIcoreTradingV1OfflineSandboxUsageGuideResult):
        payload = {
            "schema": "agicore_trading_v1_offline_sandbox_usage_guide",
            "decision": result.decision.value,
            "state": result.state.value,
            "score": result.score.overall_score,
            "risks": [risk.value for risk in result.risks],
            "recommendations": [recommendation.value for recommendation in result.recommendations],
            "context": _payload_value(result.context),
            "commands": _payload_value(result.commands),
            "safety_rules": _payload_value(result.safety_rules),
            "known_limitations": _payload_value(result.known_limitations),
            "live_trading_ready": False,
            "real_broker_ready": False,
            "real_order_execution": False,
            "profitability_proven": False,
            "financial_advice": False,
        }
    else:
        payload = dict(result)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def build_agicore_trading_v1_offline_sandbox_usage_guide(
    data: AGIcoreTradingV1OfflineSandboxUsageGuideInput | Mapping[str, Any] | None,
) -> AGIcoreTradingV1OfflineSandboxUsageGuideResult:
    payload = _coerce_input(data)
    context = build_sandbox_usage_guide_context(payload)
    safety_rules = _safety_rules(payload)
    commands = _commands(payload)
    limitations = _limitations(payload)
    markdown = render_agicore_trading_v1_offline_sandbox_usage_guide_markdown(
        context,
        safety_rules,
        commands,
        limitations,
        payload,
    )
    if payload and payload.force_live_trading_overclaim:
        markdown += "\nlive_trading_ready: true\n"
    if payload and payload.force_real_broker_overclaim:
        markdown += "\nreal_broker_ready: true\n"
    if payload and payload.force_real_order_overclaim:
        markdown += "\nreal_order_execution: true\n"
    if payload and payload.force_profitability_overclaim:
        markdown += "\nprofitability_proven: true\n"
    if payload and payload.force_financial_advice_overclaim:
        markdown += "\nfinancial_advice: true\n"
    risks = detect_agicore_trading_v1_offline_sandbox_usage_guide_risks(
        payload,
        markdown,
        commands,
        safety_rules,
        limitations,
    )
    decision = _decision_for(risks)
    state = _state_for(payload, decision)
    score = compute_agicore_trading_v1_offline_sandbox_usage_guide_score(
        payload,
        markdown,
        commands,
        safety_rules,
        limitations,
        risks,
    )
    recommendations = generate_agicore_trading_v1_offline_sandbox_usage_guide_recommendations(risks)
    sections = (
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("SAFETY", build_sandbox_usage_guide_safety_section(safety_rules)),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("PREREQUISITES", build_sandbox_usage_guide_prerequisites_section()),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("COMMANDS", build_sandbox_usage_guide_commands_section(commands)),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("MEMORY_USAGE", build_sandbox_usage_guide_memory_usage_example_section(payload)),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("INTERPRETATION", build_sandbox_usage_guide_result_interpretation_section(payload)),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("LIMITATIONS", build_sandbox_usage_guide_known_limitations_section(limitations)),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("WORKFLOW", build_sandbox_usage_guide_workflow_section()),
        AGIcoreTradingV1OfflineSandboxUsageGuideSection("NEXT_STEPS", build_sandbox_usage_guide_next_steps_section(context)),
    )
    base = AGIcoreTradingV1OfflineSandboxUsageGuideResult(
        state=state,
        decision=decision,
        score=score,
        risks=risks,
        recommendations=recommendations,
        context=context,
        sections=sections,
        commands=commands,
        safety_rules=safety_rules,
        known_limitations=limitations,
        report=None,
    )
    report = AGIcoreTradingV1OfflineSandboxUsageGuideReport(
        markdown=markdown,
        json=render_agicore_trading_v1_offline_sandbox_usage_guide_json_report(base),
    )
    return AGIcoreTradingV1OfflineSandboxUsageGuideResult(**{**base.__dict__, "report": report})
