"""Offline design layer for the future AGIcore Paper Trading Runtime."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from agicore.trading.paper_trading_runtime_design_models import (
    PaperTradingRuntimeDesignDecision,
    PaperTradingRuntimeDesignInput,
    PaperTradingRuntimeDesignRecommendation,
    PaperTradingRuntimeDesignResult,
    PaperTradingRuntimeDesignRisk,
    PaperTradingRuntimeDesignScore,
    PaperTradingRuntimeDesignSection,
    PaperTradingRuntimeDesignState,
)


def _coerce_input(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignInput:
    if isinstance(data, PaperTradingRuntimeDesignInput):
        return data
    return PaperTradingRuntimeDesignInput(**dict(data))


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, Mapping):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    if isinstance(items, set):
        return tuple(items)
    return (items,)


def _contains(items: Any, *needles: str) -> bool:
    text_items = tuple(_value(item).upper() for item in _as_tuple(items))
    return any(any(needle.upper() in item for item in text_items) for needle in needles)


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _bool_score(value: bool | None, unknown: int = 45) -> int:
    if value is True:
        return 100
    if value is False:
        return 0
    return unknown


def _average(values: Iterable[int | float | None], default: int = 0) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return default
    return _clamp(sum(usable) / len(usable))


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _upstream_items(data: PaperTradingRuntimeDesignInput) -> tuple[Any, ...]:
    return (
        data.paper_runtime_decision_review,
        data.paper_runtime_pre_review,
        data.full_paper_session,
        data.simulated_market_session,
        data.mock_alpaca_session,
        data.mock_connectivity_layer,
        data.alpaca_paper_connectivity_readiness,
        data.broker_paper_sandbox,
        data.paper_trading_end_to_end,
        data.paper_dry_run,
        data.supervised_paper_trial,
        data.observability_verification,
        data.rollback_verification,
        data.kill_switch_verification,
        data.human_validated_paper_session,
        data.supervised_paper_session,
    )


def _upstream_risks(data: PaperTradingRuntimeDesignInput) -> tuple[Any, ...]:
    risks: tuple[Any, ...] = ()
    for item in _upstream_items(data):
        risks += _as_tuple(_get(item, "risks", ()))
        risks += _as_tuple(_get(item, "blockers", ()))
    return risks


def _has_upstream_risk(data: PaperTradingRuntimeDesignInput, *needles: str) -> bool:
    return _contains(_upstream_risks(data), *needles)


def _missing(required: tuple[str, ...], declared: tuple[str, ...]) -> tuple[str, ...]:
    declared_lower = {item.lower() for item in declared}
    return tuple(item for item in required if item.lower() not in declared_lower)


def _section(name: str, score: int, risk: PaperTradingRuntimeDesignRisk, missing: tuple[str, ...], items: tuple[str, ...]) -> PaperTradingRuntimeDesignSection:
    risks = (risk,) if missing or score < 85 else ()
    details = items + tuple(f"missing:{item}" for item in missing)
    return PaperTradingRuntimeDesignSection(name, _clamp(score), not risks and score >= 85, risks, details)


def define_runtime_architecture(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("entrypoint", "state_machine", "session_cycle", "adapter", "safety", "observability", "rollback", "kill_switch", "human_supervision")
    missing = _missing(required, data.architecture_components)
    score = data.architecture_score if data.architecture_score is not None else _clamp(100 - len(missing) * 8 - (0 if data.runtime_entrypoint else 12))
    if data.runtime_entrypoint is None:
        missing += ("runtime_entrypoint",)
    return _section("architecture", score, PaperTradingRuntimeDesignRisk.ARCHITECTURE_UNCLEAR, missing, data.architecture_components)


def define_runtime_state_machine(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("INIT", "AWAIT_HUMAN_APPROVAL", "RUNNING", "PAUSED", "ROLLBACK", "KILL_SWITCHED", "COMPLETED")
    missing = _missing(required, data.runtime_states)
    score = data.state_machine_score if data.state_machine_score is not None else _clamp(100 - len(missing) * 10)
    return _section("state_machine", score, PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE, missing, data.runtime_states)


def define_runtime_session_cycle(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("market_data", "signal", "decision", "safety_gate", "paper_order", "position", "pnl", "journal", "observability")
    missing = _missing(required, data.session_cycle_steps)
    score = data.session_cycle_score if data.session_cycle_score is not None else _clamp(100 - len(missing) * 9)
    return _section("session_cycle", score, PaperTradingRuntimeDesignRisk.SESSION_CYCLE_AMBIGUOUS, missing, data.session_cycle_steps)


def define_runtime_inputs_outputs(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    missing_inputs = _missing(("market_data", "signals", "operator_approval", "risk_limits"), data.input_contracts)
    missing_outputs = _missing(("paper_orders", "positions", "pnl", "journal", "events"), data.output_contracts)
    missing = missing_inputs + missing_outputs
    score = data.inputs_outputs_score if data.inputs_outputs_score is not None else _clamp(100 - len(missing) * 9)
    return _section("inputs_outputs", score, PaperTradingRuntimeDesignRisk.INPUT_OUTPUT_CONTRACT_GAP, missing, data.input_contracts + data.output_contracts)


def define_runtime_safety_boundaries(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("offline_only", "paper_only", "no_real_order", "risk_limits", "safety_gate")
    missing = _missing(required, data.safety_boundaries)
    if _has_upstream_risk(data, "SAFETY"):
        missing += ("upstream_safety_gap",)
    score = data.safety_boundaries_score if data.safety_boundaries_score is not None else _clamp(100 - len(missing) * 12)
    return _section("safety_boundaries", score, PaperTradingRuntimeDesignRisk.SAFETY_BOUNDARY_GAP, missing, data.safety_boundaries)


def define_runtime_observability_hooks(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("logs", "metrics", "traces", "alerts", "audit_events")
    missing = _missing(required, data.observability_hooks)
    if _has_upstream_risk(data, "OBSERVABILITY"):
        missing += ("upstream_observability_gap",)
    score = data.observability_hooks_score if data.observability_hooks_score is not None else _clamp(100 - len(missing) * 11)
    return _section("observability_hooks", score, PaperTradingRuntimeDesignRisk.OBSERVABILITY_HOOK_MISSING, missing, data.observability_hooks)


def define_runtime_rollback_hooks(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("checkpoint", "restore", "state_reconcile", "rollback_event")
    missing = _missing(required, data.rollback_hooks)
    if _has_upstream_risk(data, "ROLLBACK"):
        missing += ("upstream_rollback_gap",)
    score = data.rollback_hooks_score if data.rollback_hooks_score is not None else _clamp(100 - len(missing) * 13)
    return _section("rollback_hooks", score, PaperTradingRuntimeDesignRisk.ROLLBACK_HOOK_MISSING, missing, data.rollback_hooks)


def define_runtime_kill_switch_hooks(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("halt_orders", "halt_session", "lock_state", "emit_alert")
    missing = _missing(required, data.kill_switch_hooks)
    if _has_upstream_risk(data, "KILL_SWITCH"):
        missing += ("upstream_kill_switch_gap",)
    score = data.kill_switch_hooks_score if data.kill_switch_hooks_score is not None else _clamp(100 - len(missing) * 13)
    return _section("kill_switch_hooks", score, PaperTradingRuntimeDesignRisk.KILL_SWITCH_HOOK_MISSING, missing, data.kill_switch_hooks)


def define_runtime_human_supervision_hooks(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("human_approval", "operator_confirmation", "override", "session_authorization")
    missing = _missing(required, data.human_supervision_hooks)
    if _has_upstream_risk(data, "HUMAN", "SUPERVISION"):
        missing += ("upstream_human_supervision_gap",)
    score = data.human_supervision_hooks_score if data.human_supervision_hooks_score is not None else _clamp(100 - len(missing) * 13)
    return _section("human_supervision_hooks", score, PaperTradingRuntimeDesignRisk.HUMAN_SUPERVISION_HOOK_MISSING, missing, data.human_supervision_hooks)


def define_runtime_adapter_contracts(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignSection:
    data = _coerce_input(data)
    required = ("connect", "disconnect", "account", "positions", "submit_order", "order_status", "reject_order")
    missing = _missing(required, data.adapter_contracts)
    score = data.adapter_contracts_score if data.adapter_contracts_score is not None else _clamp(100 - len(missing) * 10)
    return _section("adapter_contracts", score, PaperTradingRuntimeDesignRisk.ADAPTER_CONTRACT_INCOMPLETE, missing, data.adapter_contracts)


def detect_runtime_design_risks(data: PaperTradingRuntimeDesignInput | Mapping[str, Any], *sections: PaperTradingRuntimeDesignSection) -> tuple[PaperTradingRuntimeDesignRisk, ...]:
    data = _coerce_input(data)
    if not sections:
        sections = (
            define_runtime_architecture(data),
            define_runtime_state_machine(data),
            define_runtime_session_cycle(data),
            define_runtime_inputs_outputs(data),
            define_runtime_safety_boundaries(data),
            define_runtime_observability_hooks(data),
            define_runtime_rollback_hooks(data),
            define_runtime_kill_switch_hooks(data),
            define_runtime_human_supervision_hooks(data),
            define_runtime_adapter_contracts(data),
        )
    risks: list[PaperTradingRuntimeDesignRisk] = []
    for section in sections:
        risks.extend(section.risks)
    if (
        data.runtime_scope_locked is not True
        or data.offline_mode_enforced is not True
        or data.no_real_broker is not True
        or data.no_api_key_read is not True
        or data.no_http_transport is not True
        or data.no_websocket_transport is not True
        or data.no_socket_transport is not True
        or data.no_external_api is not True
        or data.no_real_order is not True
        or _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY", "RUNTIME_SCOPE")
    ):
        risks.append(PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT)
    if data.no_runtime_implementation_created is not True:
        risks.append(PaperTradingRuntimeDesignRisk.PREMATURE_IMPLEMENTATION_RISK)
    return _dedupe(risks)


def compute_runtime_design_score(data: PaperTradingRuntimeDesignInput | Mapping[str, Any], risks: tuple[PaperTradingRuntimeDesignRisk, ...] = (), *sections: PaperTradingRuntimeDesignSection) -> PaperTradingRuntimeDesignScore:
    data = _coerce_input(data)
    if not sections:
        sections = (
            define_runtime_architecture(data),
            define_runtime_state_machine(data),
            define_runtime_session_cycle(data),
            define_runtime_inputs_outputs(data),
            define_runtime_safety_boundaries(data),
            define_runtime_observability_hooks(data),
            define_runtime_rollback_hooks(data),
            define_runtime_kill_switch_hooks(data),
            define_runtime_human_supervision_hooks(data),
            define_runtime_adapter_contracts(data),
        )
    base = _average(tuple(section.score for section in sections) + (_bool_score(data.design_review_approved),))
    overall = _clamp(base - min(80, len(set(risks)) * 5))
    for risk, cap in {
        PaperTradingRuntimeDesignRisk.ARCHITECTURE_UNCLEAR: 55,
        PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE: 55,
        PaperTradingRuntimeDesignRisk.SAFETY_BOUNDARY_GAP: 50,
        PaperTradingRuntimeDesignRisk.ROLLBACK_HOOK_MISSING: 55,
        PaperTradingRuntimeDesignRisk.KILL_SWITCH_HOOK_MISSING: 50,
        PaperTradingRuntimeDesignRisk.HUMAN_SUPERVISION_HOOK_MISSING: 55,
        PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT: 40,
        PaperTradingRuntimeDesignRisk.PREMATURE_IMPLEMENTATION_RISK: 35,
    }.items():
        if risk in risks:
            overall = min(overall, cap)
    return PaperTradingRuntimeDesignScore(overall, *(section.score for section in sections))


def _select_decision(score: int, risks: tuple[PaperTradingRuntimeDesignRisk, ...], design_approved: bool | None, implementation_ready: bool | None) -> PaperTradingRuntimeDesignDecision:
    if PaperTradingRuntimeDesignRisk.PREMATURE_IMPLEMENTATION_RISK in risks or PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT in risks or score < 45:
        return PaperTradingRuntimeDesignDecision.BLOCK_RUNTIME_IMPLEMENTATION
    if risks:
        return PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP
    if implementation_ready is True and score >= 94:
        return PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION
    if design_approved is True and score >= 85:
        return PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_DESIGN
    return PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP


def _select_state(decision: PaperTradingRuntimeDesignDecision, risks: tuple[PaperTradingRuntimeDesignRisk, ...], score: int) -> PaperTradingRuntimeDesignState:
    if decision == PaperTradingRuntimeDesignDecision.BLOCK_RUNTIME_IMPLEMENTATION:
        return PaperTradingRuntimeDesignState.NOT_READY
    if decision == PaperTradingRuntimeDesignDecision.REQUIRE_DESIGN_CLEANUP:
        if len(set(risks)) >= 3 or score < 72:
            return PaperTradingRuntimeDesignState.DESIGN_REVIEW_REQUIRED
        return PaperTradingRuntimeDesignState.PARTIALLY_DESIGNED
    if decision == PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION:
        return PaperTradingRuntimeDesignState.READY_FOR_RUNTIME_IMPLEMENTATION
    return PaperTradingRuntimeDesignState.RUNTIME_DESIGN_READY


def generate_runtime_design_recommendations(risks: tuple[PaperTradingRuntimeDesignRisk, ...], decision: PaperTradingRuntimeDesignDecision | None = None) -> tuple[PaperTradingRuntimeDesignRecommendation, ...]:
    recommendations: list[PaperTradingRuntimeDesignRecommendation] = []
    if risks:
        recommendations.append(PaperTradingRuntimeDesignRecommendation.HOLD_RUNTIME_IMPLEMENTATION)
    mapping = {
        PaperTradingRuntimeDesignRisk.ARCHITECTURE_UNCLEAR: PaperTradingRuntimeDesignRecommendation.CLARIFY_RUNTIME_ARCHITECTURE,
        PaperTradingRuntimeDesignRisk.STATE_MACHINE_INCOMPLETE: PaperTradingRuntimeDesignRecommendation.COMPLETE_RUNTIME_STATE_MACHINE,
        PaperTradingRuntimeDesignRisk.SESSION_CYCLE_AMBIGUOUS: PaperTradingRuntimeDesignRecommendation.CLARIFY_SESSION_CYCLE,
        PaperTradingRuntimeDesignRisk.INPUT_OUTPUT_CONTRACT_GAP: PaperTradingRuntimeDesignRecommendation.COMPLETE_INPUT_OUTPUT_CONTRACTS,
        PaperTradingRuntimeDesignRisk.SAFETY_BOUNDARY_GAP: PaperTradingRuntimeDesignRecommendation.COMPLETE_SAFETY_BOUNDARIES,
        PaperTradingRuntimeDesignRisk.OBSERVABILITY_HOOK_MISSING: PaperTradingRuntimeDesignRecommendation.ADD_OBSERVABILITY_HOOKS,
        PaperTradingRuntimeDesignRisk.ROLLBACK_HOOK_MISSING: PaperTradingRuntimeDesignRecommendation.ADD_ROLLBACK_HOOKS,
        PaperTradingRuntimeDesignRisk.KILL_SWITCH_HOOK_MISSING: PaperTradingRuntimeDesignRecommendation.ADD_KILL_SWITCH_HOOKS,
        PaperTradingRuntimeDesignRisk.HUMAN_SUPERVISION_HOOK_MISSING: PaperTradingRuntimeDesignRecommendation.ADD_HUMAN_SUPERVISION_HOOKS,
        PaperTradingRuntimeDesignRisk.ADAPTER_CONTRACT_INCOMPLETE: PaperTradingRuntimeDesignRecommendation.COMPLETE_ADAPTER_CONTRACTS,
        PaperTradingRuntimeDesignRisk.RUNTIME_SCOPE_DRIFT: PaperTradingRuntimeDesignRecommendation.FREEZE_RUNTIME_SCOPE,
        PaperTradingRuntimeDesignRisk.PREMATURE_IMPLEMENTATION_RISK: PaperTradingRuntimeDesignRecommendation.KEEP_IMPLEMENTATION_BLOCKED,
    }
    recommendations.extend(mapping[risk] for risk in risks)
    recommendations.append(PaperTradingRuntimeDesignRecommendation.RUN_RUNTIME_DESIGN_REVIEW_SUITE)
    if decision == PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_DESIGN:
        recommendations.append(PaperTradingRuntimeDesignRecommendation.APPROVE_RUNTIME_DESIGN_AFTER_MANUAL_REVIEW)
    if decision == PaperTradingRuntimeDesignDecision.APPROVE_RUNTIME_IMPLEMENTATION:
        recommendations.append(PaperTradingRuntimeDesignRecommendation.APPROVE_IMPLEMENTATION_AFTER_MANUAL_REVIEW)
    return _dedupe(recommendations)


def evaluate_paper_trading_runtime_design(data: PaperTradingRuntimeDesignInput | Mapping[str, Any]) -> PaperTradingRuntimeDesignResult:
    data = _coerce_input(data)
    sections = (
        define_runtime_architecture(data),
        define_runtime_state_machine(data),
        define_runtime_session_cycle(data),
        define_runtime_inputs_outputs(data),
        define_runtime_safety_boundaries(data),
        define_runtime_observability_hooks(data),
        define_runtime_rollback_hooks(data),
        define_runtime_kill_switch_hooks(data),
        define_runtime_human_supervision_hooks(data),
        define_runtime_adapter_contracts(data),
    )
    risks = detect_runtime_design_risks(data, *sections)
    score = compute_runtime_design_score(data, risks, *sections)
    decision = _select_decision(score.overall_score, risks, data.design_review_approved, data.ready_for_runtime_implementation)
    state = _select_state(decision, risks, score.overall_score)
    recommendations = generate_runtime_design_recommendations(risks, decision)
    offline_only = (
        data.offline_mode_enforced is True
        and data.no_real_broker is True
        and data.no_api_key_read is True
        and data.no_http_transport is True
        and data.no_websocket_transport is True
        and data.no_socket_transport is True
        and data.no_external_api is True
        and data.no_real_order is True
        and data.no_runtime_implementation_created is True
        and not _has_upstream_risk(data, "BROKER", "LIVE_EXECUTION", "API_ACCESS", "NETWORK_LEAK", "EXTERNAL_DEPENDENCY")
    )
    summary = f"{state.value}: decision={decision.value}, score={score.overall_score}, risks={len(risks)}, offline_only={offline_only}"
    return PaperTradingRuntimeDesignResult(state, decision, score.overall_score, score, risks, *sections, recommendations, offline_only, summary)


def render_paper_trading_runtime_design_markdown(result: PaperTradingRuntimeDesignResult) -> str:
    lines = [
        "# AGIcore Paper Trading Runtime Design",
        f"- State: {result.state.value}",
        f"- Decision: {result.decision.value}",
        f"- Score: {result.runtime_design_score}/100",
        f"- Offline only: {result.offline_only}",
        f"- Summary: {result.summary}",
        "",
        "# Runtime Design Sections",
    ]
    sections = (
        result.architecture,
        result.state_machine,
        result.session_cycle,
        result.inputs_outputs,
        result.safety_boundaries,
        result.observability_hooks,
        result.rollback_hooks,
        result.kill_switch_hooks,
        result.human_supervision_hooks,
        result.adapter_contracts,
    )
    for section in sections:
        lines.append(f"- {section.name}: passed={section.passed}, score={section.score}/100, risks={', '.join(risk.value for risk in section.risks) or 'none'}")
        lines.extend(f"  - {item}" for item in section.items)
    lines.append("")
    lines.append("# Runtime Design Risks")
    lines.extend(f"- {risk.value}" for risk in result.risks) if result.risks else lines.append("- none")
    lines.append("")
    lines.append("# Runtime Design Recommendations")
    lines.extend(f"- {recommendation.value}" for recommendation in result.recommendations)
    return "\n".join(lines)


__all__ = [
    "compute_runtime_design_score",
    "define_runtime_adapter_contracts",
    "define_runtime_architecture",
    "define_runtime_human_supervision_hooks",
    "define_runtime_inputs_outputs",
    "define_runtime_kill_switch_hooks",
    "define_runtime_observability_hooks",
    "define_runtime_rollback_hooks",
    "define_runtime_safety_boundaries",
    "define_runtime_session_cycle",
    "define_runtime_state_machine",
    "detect_runtime_design_risks",
    "evaluate_paper_trading_runtime_design",
    "generate_runtime_design_recommendations",
    "render_paper_trading_runtime_design_markdown",
]
