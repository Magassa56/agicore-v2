"""Offline Autonomous Global Orchestrator Core for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .behavioral_stability_models import BehavioralPressureLevel, BehavioralRecoveryState
from .collective_consensus_models import ConsensusDecision, ConsensusMode, ConsensusRisk, ConsensusState
from .executive_brain_models import ExecutiveMode
from .global_orchestrator_models import (
    CoordinationResult,
    CoordinationState,
    GlobalOrchestratorInput,
    GlobalOrchestratorResult,
    GlobalSystemState,
    OrchestrationGraph,
    OrchestratorCycle,
    OrchestratorDecision,
    OrchestratorEvent,
    OrchestratorMode,
    OrchestratorPriority,
    OrchestratorRecommendation,
    OrchestratorRisk,
    OrchestratorRoute,
    OrchestratorSignal,
    OrchestratorTransition,
    SystemHealthSnapshot,
)
from .hierarchical_supervisor_models import SupervisorDecision
from .intent_alignment_models import IntentAlignmentMode
from .learning_governance_models import LearningGovernanceDecision, LearningGovernanceMode
from .meta_cognition_models import MetaCognitionMode
from .mission_continuity_models import MissionContinuityMode
from .operational_awareness_models import OperationalAwarenessMode, OperationalHealthStatus
from .recovery_resilience_models import RecoveryMode
from .recursive_self_evaluation_models import SelfEvaluationStatus, SystemAutonomyRecommendation
from .strategic_arbitration_models import ArbitrationDecision, ArbitrationMode
from .strategic_planning_models import StrategicPlanStatus
from .system_integrity_models import SystemIntegrityStatus
from .tactical_execution_models import TacticalExecutionQuality


PRIORITY_ORDER: tuple[OrchestratorPriority, ...] = (
    OrchestratorPriority.SURVIVAL,
    OrchestratorPriority.SYSTEM_INTEGRITY,
    OrchestratorPriority.SAFETY,
    OrchestratorPriority.MISSION,
    OrchestratorPriority.CONTINUITY,
    OrchestratorPriority.CONSENSUS,
    OrchestratorPriority.SUPERVISION,
    OrchestratorPriority.STRATEGY,
    OrchestratorPriority.PERFORMANCE,
    OrchestratorPriority.LEARNING,
)


def build_orchestration_graph(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    **kwargs,
) -> OrchestrationGraph:
    """Build an offline global graph of active engines and coordination routes."""
    data = _input(orchestrator_input, **kwargs)
    engines = _active_engines(data)
    isolated = _isolated_engines(data)
    routes: list[OrchestratorRoute] = []
    sequence = (
        ("system_integrity", "recovery_resilience", OrchestratorPriority.SYSTEM_INTEGRITY),
        ("recovery_resilience", "mission_continuity", OrchestratorPriority.SURVIVAL),
        ("mission_continuity", "operational_awareness", OrchestratorPriority.CONTINUITY),
        ("operational_awareness", "intent_alignment", OrchestratorPriority.SAFETY),
        ("intent_alignment", "meta_cognition", OrchestratorPriority.MISSION),
        ("meta_cognition", "collective_consensus", OrchestratorPriority.CONSENSUS),
        ("collective_consensus", "strategic_arbitration", OrchestratorPriority.CONSENSUS),
        ("strategic_arbitration", "supervisor_result", OrchestratorPriority.SUPERVISION),
        ("supervisor_result", "executive_result", OrchestratorPriority.STRATEGY),
        ("executive_result", "learning_governance", OrchestratorPriority.LEARNING),
    )
    for source, target, priority in sequence:
        if source in engines and target in engines:
            enabled = source not in isolated and target not in isolated
            routes.append(OrchestratorRoute(source, target, priority, enabled, "global coordination route"))
    critical_routes = tuple(route for route in routes if route.priority in {OrchestratorPriority.SURVIVAL, OrchestratorPriority.SYSTEM_INTEGRITY, OrchestratorPriority.SAFETY})
    return OrchestrationGraph(
        engines=engines,
        routes=tuple(routes),
        dominant_engine=_dominant_engine(data),
        isolated_engines=isolated,
        critical_routes=critical_routes,
    )


def evaluate_global_system_state(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    **kwargs,
) -> GlobalSystemState:
    """Evaluate global state, dominant priority, signals and risks."""
    data = _input(orchestrator_input, **kwargs)
    graph = build_orchestration_graph(data)
    risks = detect_global_risks(data, graph=graph)
    confidence = compute_orchestration_confidence(data, risks=risks, graph=graph)
    health = _health_snapshot(data, confidence)
    priority = coordinate_engine_priorities(data, risks=risks)
    mode = _mode(priority, risks, data)
    return GlobalSystemState(
        mode=mode,
        dominant_priority=priority,
        health_snapshot=health,
        active_engines=graph.engines,
        degraded_engines=_degraded_engines(data),
        isolated_engines=graph.isolated_engines,
        signals=_signals(data, risks, priority),
        risks=risks,
    )


def detect_global_risks(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    graph: OrchestrationGraph | None = None,
    **kwargs,
) -> tuple[OrchestratorRisk, ...]:
    """Detect global orchestration risks and cross-layer inconsistencies."""
    data = _input(orchestrator_input, **kwargs)
    resolved_graph = graph or build_orchestration_graph(data)
    risks: list[OrchestratorRisk] = []

    if len(_degraded_engines(data)) >= 3:
        risks.append(OrchestratorRisk.GLOBAL_INSTABILITY)
    if len(resolved_graph.engines) >= 6 and len(resolved_graph.routes) == 0:
        risks.append(OrchestratorRisk.ORCHESTRATION_FRAGMENTATION)
    if _safe_mode_required(data) and _execution_allowed(data):
        risks.append(OrchestratorRisk.UNSAFE_COORDINATION)
    if resolve_cross_layer_conflicts(data):
        risks.append(OrchestratorRisk.CROSS_LAYER_CONFLICT)
    if _critical_transition(data):
        risks.append(OrchestratorRisk.CRITICAL_MODE_TRANSITION)
    if data.collective_consensus is not None and (
        data.collective_consensus.mode == ConsensusMode.CONSENSUS_COLLAPSE
        or data.collective_consensus.state == ConsensusState.COLLAPSED
        or ConsensusRisk.CONSENSUS_COLLAPSE_RISK in data.collective_consensus.risks
    ):
        risks.append(OrchestratorRisk.CONSENSUS_BREAKDOWN)
    if _execution_allowed(data) and (_supervision_blocks(data) or _safe_mode_required(data)):
        risks.append(OrchestratorRisk.EXECUTION_DESYNCHRONIZATION)
    if _autonomy_escalation(data):
        risks.append(OrchestratorRisk.AUTONOMY_ESCALATION)
    if _safe_mode_required(data):
        risks.append(OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED)
    if _survival_required(data):
        risks.append(OrchestratorRisk.SURVIVAL_PRIORITY_TRIGGERED)

    return tuple(dict.fromkeys(risks))


def coordinate_engine_priorities(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    risks: tuple[OrchestratorRisk, ...] | None = None,
    **kwargs,
) -> OrchestratorPriority:
    """Select the dominant global priority according to the fixed hierarchy."""
    data = _input(orchestrator_input, **kwargs)
    resolved_risks = risks or detect_global_risks(data)
    active = _active_priorities(data, resolved_risks)
    for priority in PRIORITY_ORDER:
        if priority in active:
            return priority
    return OrchestratorPriority.PERFORMANCE


def resolve_cross_layer_conflicts(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    **kwargs,
) -> tuple[str, ...]:
    """Return explainable cross-layer conflicts."""
    data = _input(orchestrator_input, **kwargs)
    conflicts: list[str] = []
    if data.executive_result is not None and data.executive_result.decision.allow_execution and _supervision_blocks(data):
        conflicts.append("Executive allows execution while supervision blocks or requires review.")
    if data.learning_governance is not None and data.learning_governance.decision == LearningGovernanceDecision.ALLOW_LEARNING and _safe_mode_required(data):
        conflicts.append("Learning is allowed while global safe mode is required.")
    if data.collective_consensus is not None and data.strategic_arbitration is not None:
        if data.collective_consensus.decision == ConsensusDecision.APPROVE_COLLECTIVE_DECISION and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.STOP_EXECUTION, ArbitrationDecision.ENABLE_SAFE_MODE}:
            conflicts.append("Consensus approves while strategic arbitration blocks or enters safe mode.")
    if data.intent_alignment is not None and data.intent_alignment.mode == IntentAlignmentMode.CRITICAL_REALIGNMENT and data.executive_result is not None and data.executive_result.decision.allow_execution:
        conflicts.append("Intent alignment requires realignment while execution is still allowed.")
    return tuple(dict.fromkeys(conflicts))


def compute_orchestration_confidence(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    risks: tuple[OrchestratorRisk, ...] | None = None,
    graph: OrchestrationGraph | None = None,
    **kwargs,
) -> int:
    """Compute global orchestration confidence from 0..100."""
    data = _input(orchestrator_input, **kwargs)
    resolved_graph = graph or build_orchestration_graph(data)
    resolved_risks = risks or detect_global_risks(data, graph=resolved_graph)
    scores = _available_scores(data)
    score = int(round(sum(scores) / len(scores))) if scores else 75
    score -= min(35, len(resolved_risks) * 4)
    score -= min(20, len(resolved_graph.isolated_engines) * 5)
    if OrchestratorRisk.SURVIVAL_PRIORITY_TRIGGERED in resolved_risks:
        score -= 10
    return _clamp(score)


def apply_global_safe_mode(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    risks: tuple[OrchestratorRisk, ...] | None = None,
    **kwargs,
) -> bool:
    """Return True when global safe mode must be active."""
    data = _input(orchestrator_input, **kwargs)
    resolved_risks = risks or detect_global_risks(data)
    return (
        OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED in resolved_risks
        or OrchestratorRisk.UNSAFE_COORDINATION in resolved_risks
        or OrchestratorRisk.CONSENSUS_BREAKDOWN in resolved_risks
        or _safe_mode_required(data)
    )


def schedule_coordination_cycle(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    graph: OrchestrationGraph | None = None,
    state: GlobalSystemState | None = None,
    **kwargs,
) -> OrchestratorCycle:
    """Schedule the next offline coordination cycle."""
    data = _input(orchestrator_input, **kwargs)
    resolved_graph = graph or build_orchestration_graph(data)
    resolved_state = state or evaluate_global_system_state(data)
    safe_mode = apply_global_safe_mode(data, risks=resolved_state.risks)
    actions = _cycle_actions(resolved_state.risks, safe_mode)
    return OrchestratorCycle(
        cycle_id=f"{resolved_state.mode.value.lower()}:{len(resolved_graph.routes)}",
        mode=resolved_state.mode,
        priority=resolved_state.dominant_priority,
        routes=tuple(route for route in resolved_graph.routes if route.enabled),
        actions=actions,
        safe_mode=safe_mode,
        requires_supervision=OrchestratorRisk.CROSS_LAYER_CONFLICT in resolved_state.risks or OrchestratorRisk.UNSAFE_COORDINATION in resolved_state.risks,
    )


def generate_orchestrator_recommendations(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    *,
    risks: tuple[OrchestratorRisk, ...] | None = None,
    mode: OrchestratorMode | None = None,
    **kwargs,
) -> tuple[OrchestratorRecommendation, ...]:
    """Generate ordered global recommendations."""
    data = _input(orchestrator_input, **kwargs)
    resolved_risks = risks or detect_global_risks(data)
    resolved_mode = mode or _mode(coordinate_engine_priorities(data, risks=resolved_risks), resolved_risks, data)
    recommendations: list[OrchestratorRecommendation] = []

    if resolved_mode == OrchestratorMode.SURVIVAL_ORCHESTRATION:
        recommendations.append(OrchestratorRecommendation.ACTIVATE_SURVIVAL_MODE)
        recommendations.append(OrchestratorRecommendation.HALT_HIGH_RISK_ROUTING)
    if resolved_mode in {OrchestratorMode.EMERGENCY_ORCHESTRATION, OrchestratorMode.SAFE_GLOBAL_MODE}:
        recommendations.append(OrchestratorRecommendation.ENTER_GLOBAL_SAFE_MODE)
        recommendations.append(OrchestratorRecommendation.HALT_HIGH_RISK_ROUTING)
    if OrchestratorRisk.AUTONOMY_ESCALATION in resolved_risks or OrchestratorRisk.UNSAFE_COORDINATION in resolved_risks:
        recommendations.append(OrchestratorRecommendation.REDUCE_AUTONOMY)
    if OrchestratorRisk.CROSS_LAYER_CONFLICT in resolved_risks or OrchestratorRisk.CRITICAL_MODE_TRANSITION in resolved_risks:
        recommendations.append(OrchestratorRecommendation.REQUIRE_HUMAN_SUPERVISION)
    if data.learning_governance is not None and data.learning_governance.mode in {LearningGovernanceMode.LEARN, LearningGovernanceMode.EXPLOIT_ONLY} and resolved_risks:
        recommendations.append(OrchestratorRecommendation.FREEZE_LEARNING)
    if OrchestratorRisk.GLOBAL_INSTABILITY in resolved_risks:
        recommendations.append(OrchestratorRecommendation.ENABLE_RECOVERY_COORDINATION)
        recommendations.append(OrchestratorRecommendation.ISOLATE_UNSTABLE_MODULES)
    if OrchestratorRisk.ORCHESTRATION_FRAGMENTATION in resolved_risks:
        recommendations.append(OrchestratorRecommendation.REBALANCE_PRIORITIES)
    if not recommendations:
        recommendations.append(OrchestratorRecommendation.CONTINUE_COORDINATED_OPERATION)
    return tuple(dict.fromkeys(recommendations))


def render_global_orchestrator_markdown(result: GlobalOrchestratorResult) -> str:
    """Render global orchestration result as Markdown."""
    lines = [
        "# Autonomous Global Orchestrator Core",
        "",
        "## Global System State",
        "",
        f"- Mode: {result.system_state.mode.value}",
        f"- Dominant priority: {result.system_state.dominant_priority.value}",
        f"- Confidence: {result.confidence_score}/100",
        "",
        "## Active Engines",
        "",
        *_bullet_lines(result.system_state.active_engines),
        "",
        "## Orchestration Graph",
        "",
        f"- Dominant engine: {result.graph.dominant_engine or 'None'}",
        *_bullet_lines(tuple(f"{route.source} -> {route.target} [{route.priority.value}]" for route in result.graph.routes)),
        "",
        "## Coordination Cycles",
        "",
        f"- Cycle: {result.coordination.cycle.cycle_id}",
        f"- Safe mode: {result.coordination.cycle.safe_mode}",
        f"- Supervision required: {result.coordination.cycle.requires_supervision}",
        "",
        "## Risks",
        "",
        *_bullet_lines(tuple(risk.value for risk in result.system_state.risks)),
        "",
        "## Priorities",
        "",
        *_bullet_lines(tuple(priority.value for priority in PRIORITY_ORDER)),
        "",
        "## Global Decisions",
        "",
        f"- {result.decision.value}",
        f"- {result.final_message}",
        "",
        "## Recommendations",
        "",
        *_bullet_lines(tuple(recommendation.value for recommendation in result.recommendations)),
        "",
        "## AGIcore Orchestrator State",
        "",
        "- Offline only: no broker, no real order, no external API, no external ML, no external LLM, no neural training, no live execution.",
        "",
    ]
    return "\n".join(lines)


def coordinate_global_orchestrator(
    orchestrator_input: GlobalOrchestratorInput | None = None,
    **kwargs,
) -> GlobalOrchestratorResult:
    """Run the full offline global orchestration pipeline."""
    data = _input(orchestrator_input, **kwargs)
    graph = build_orchestration_graph(data)
    state = evaluate_global_system_state(data)
    cycle = schedule_coordination_cycle(data, graph=graph, state=state)
    decision = _decision(state, cycle)
    transitions = _transitions(state)
    recommendations = generate_orchestrator_recommendations(data, risks=state.risks, mode=state.mode)
    coordination_state = CoordinationState(state.mode, state.dominant_priority, state.health_snapshot.orchestration_confidence, state.risks, state.signals)
    coordination = CoordinationResult(
        coordination_state,
        decision,
        transitions,
        cycle,
        recommendations,
        f"Global orchestration selected {decision.value} under {state.dominant_priority.value}.",
    )
    event = OrchestratorEvent(state.mode, decision, coordination.summary, datetime.now(UTC))
    return GlobalOrchestratorResult(
        system_state=state,
        graph=graph,
        coordination=coordination,
        decision=decision,
        confidence_score=state.health_snapshot.orchestration_confidence,
        recommendations=recommendations,
        events=(event,),
        final_message=coordination.summary,
    )


def _active_engines(data: GlobalOrchestratorInput) -> tuple[str, ...]:
    pairs = (
        ("strategic_arbitration", data.strategic_arbitration),
        ("collective_consensus", data.collective_consensus),
        ("intent_alignment", data.intent_alignment),
        ("meta_cognition", data.meta_cognition),
        ("operational_awareness", data.operational_awareness),
        ("mission_continuity", data.mission_continuity),
        ("recovery_resilience", data.recovery_resilience),
        ("system_integrity", data.system_integrity),
        ("learning_governance", data.learning_governance),
        ("self_evaluation", data.self_evaluation),
        ("supervisor_result", data.supervisor_result),
        ("executive_result", data.executive_result),
        ("strategic_result", data.strategic_result),
        ("tactical_execution", data.tactical_execution),
        ("behavioral_stability", data.behavioral_stability),
    )
    return tuple(name for name, value in pairs if value is not None)


def _degraded_engines(data: GlobalOrchestratorInput) -> tuple[str, ...]:
    degraded: list[str] = []
    if data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY:
        degraded.append("system_integrity")
    if data.collective_consensus is not None and data.collective_consensus.mode in {ConsensusMode.DEGRADED_CONSENSUS, ConsensusMode.CONSENSUS_COLLAPSE, ConsensusMode.EMERGENCY_CONSENSUS}:
        degraded.append("collective_consensus")
    if data.intent_alignment is not None and data.intent_alignment.mode not in {IntentAlignmentMode.FULLY_ALIGNED, IntentAlignmentMode.STABLE_ALIGNMENT}:
        degraded.append("intent_alignment")
    if data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.DEGRADED, OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING}:
        degraded.append("operational_awareness")
    if data.meta_cognition is not None and data.meta_cognition.mode in {MetaCognitionMode.CONTRADICTORY, MetaCognitionMode.DEGRADED_REASONING, MetaCognitionMode.RECALIBRATION_REQUIRED}:
        degraded.append("meta_cognition")
    if data.behavioral_stability is not None and data.behavioral_stability.pressure_level in {BehavioralPressureLevel.HIGH, BehavioralPressureLevel.EXTREME}:
        degraded.append("behavioral_stability")
    if data.tactical_execution is not None and data.tactical_execution.quality in {TacticalExecutionQuality.WEAK, TacticalExecutionQuality.DANGEROUS, TacticalExecutionQuality.BLOCKED}:
        degraded.append("tactical_execution")
    return tuple(degraded)


def _isolated_engines(data: GlobalOrchestratorInput) -> tuple[str, ...]:
    isolated: list[str] = []
    if data.system_integrity is not None:
        isolated.extend(data.system_integrity.modules_to_isolate)
    if data.recovery_resilience is not None:
        isolated.extend(data.recovery_resilience.isolated_modules)
    return tuple(dict.fromkeys(isolated))


def _dominant_engine(data: GlobalOrchestratorInput) -> str | None:
    if _survival_required(data):
        return "recovery_resilience"
    if data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE, SystemIntegrityStatus.ROLLBACK_RECOMMENDED}:
        return "system_integrity"
    if data.collective_consensus is not None and data.collective_consensus.mode in {ConsensusMode.EMERGENCY_CONSENSUS, ConsensusMode.SAFETY_FIRST}:
        return "collective_consensus"
    if data.strategic_arbitration is not None:
        return "strategic_arbitration"
    return None


def _health_snapshot(data: GlobalOrchestratorInput, confidence: int) -> SystemHealthSnapshot:
    return SystemHealthSnapshot(
        integrity_score=data.system_integrity.integrity_score if data.system_integrity is not None else 75,
        consensus_score=data.collective_consensus.collective_confidence_score if data.collective_consensus is not None else 75,
        alignment_score=data.intent_alignment.alignment_confidence if data.intent_alignment is not None else 75,
        operational_score=data.operational_awareness.operational_confidence_score if data.operational_awareness is not None else 75,
        continuity_score=data.mission_continuity.continuity_score if data.mission_continuity is not None else 75,
        recovery_score=data.recovery_resilience.resilience_score if data.recovery_resilience is not None else 75,
        cognitive_score=data.meta_cognition.confidence_score if data.meta_cognition is not None else 75,
        behavioral_score=data.behavioral_stability.stability_score if data.behavioral_stability is not None else 75,
        orchestration_confidence=confidence,
    )


def _available_scores(data: GlobalOrchestratorInput) -> tuple[int, ...]:
    scores: list[int] = []
    for value in (
        data.system_integrity.integrity_score if data.system_integrity is not None else None,
        data.collective_consensus.collective_confidence_score if data.collective_consensus is not None else None,
        data.intent_alignment.alignment_confidence if data.intent_alignment is not None else None,
        data.operational_awareness.operational_confidence_score if data.operational_awareness is not None else None,
        data.mission_continuity.continuity_score if data.mission_continuity is not None else None,
        data.recovery_resilience.resilience_score if data.recovery_resilience is not None else None,
        data.meta_cognition.confidence_score if data.meta_cognition is not None else None,
        data.behavioral_stability.stability_score if data.behavioral_stability is not None else None,
    ):
        if value is not None:
            scores.append(value)
    return tuple(scores)


def _active_priorities(data: GlobalOrchestratorInput, risks: tuple[OrchestratorRisk, ...]) -> set[OrchestratorPriority]:
    active: set[OrchestratorPriority] = set()
    if OrchestratorRisk.SURVIVAL_PRIORITY_TRIGGERED in risks or _survival_required(data):
        active.add(OrchestratorPriority.SURVIVAL)
    if data.system_integrity is not None and data.system_integrity.status != SystemIntegrityStatus.HEALTHY:
        active.add(OrchestratorPriority.SYSTEM_INTEGRITY)
    if _safe_mode_required(data):
        active.add(OrchestratorPriority.SAFETY)
    if data.intent_alignment is not None:
        active.add(OrchestratorPriority.MISSION)
    if data.mission_continuity is not None:
        active.add(OrchestratorPriority.CONTINUITY)
    if data.collective_consensus is not None:
        active.add(OrchestratorPriority.CONSENSUS)
    if _supervision_blocks(data):
        active.add(OrchestratorPriority.SUPERVISION)
    if data.strategic_result is not None:
        active.add(OrchestratorPriority.STRATEGY)
    if _execution_allowed(data):
        active.add(OrchestratorPriority.PERFORMANCE)
    if data.learning_governance is not None:
        active.add(OrchestratorPriority.LEARNING)
    return active or {OrchestratorPriority.PERFORMANCE}


def _signals(data: GlobalOrchestratorInput, risks: tuple[OrchestratorRisk, ...], priority: OrchestratorPriority) -> tuple[OrchestratorSignal, ...]:
    signals: list[OrchestratorSignal] = []
    signals.append(OrchestratorSignal.ENGINES_ALIGNED if not risks else OrchestratorSignal.DESYNCHRONIZATION_SIGNAL)
    if _safe_mode_required(data):
        signals.append(OrchestratorSignal.SAFE_MODE_SIGNAL)
    if data.recovery_resilience is not None and data.recovery_resilience.mode != RecoveryMode.NORMAL:
        signals.append(OrchestratorSignal.RECOVERY_SIGNAL)
    if data.learning_governance is not None and data.learning_governance.mode in {LearningGovernanceMode.LEARN, LearningGovernanceMode.EXPLOIT_ONLY}:
        signals.append(OrchestratorSignal.LEARNING_SIGNAL)
    if _supervision_blocks(data):
        signals.append(OrchestratorSignal.SUPERVISION_SIGNAL)
    if priority == OrchestratorPriority.SYSTEM_INTEGRITY:
        signals.append(OrchestratorSignal.INTEGRITY_SIGNAL)
    if data.collective_consensus is not None:
        signals.append(OrchestratorSignal.CONSENSUS_SIGNAL)
    if priority == OrchestratorPriority.SURVIVAL:
        signals.append(OrchestratorSignal.SURVIVAL_SIGNAL)
    return tuple(dict.fromkeys(signals))


def _mode(priority: OrchestratorPriority, risks: tuple[OrchestratorRisk, ...], data: GlobalOrchestratorInput) -> OrchestratorMode:
    if priority == OrchestratorPriority.SURVIVAL:
        return OrchestratorMode.SURVIVAL_ORCHESTRATION
    if OrchestratorRisk.CRITICAL_MODE_TRANSITION in risks:
        return OrchestratorMode.EMERGENCY_ORCHESTRATION
    if OrchestratorRisk.GLOBAL_SAFE_MODE_REQUIRED in risks or OrchestratorRisk.UNSAFE_COORDINATION in risks:
        return OrchestratorMode.SAFE_GLOBAL_MODE
    if data.recovery_resilience is not None and data.recovery_resilience.mode != RecoveryMode.NORMAL:
        return OrchestratorMode.RECOVERY_COORDINATION
    if _supervision_blocks(data):
        return OrchestratorMode.SUPERVISED_GLOBAL_MODE
    if data.learning_governance is not None and data.learning_governance.mode == LearningGovernanceMode.LEARN and not risks:
        return OrchestratorMode.LEARNING_COORDINATION
    if risks:
        return OrchestratorMode.DEGRADED_OPERATION
    if len(_active_engines(data)) >= 3:
        return OrchestratorMode.COORDINATED_OPERATION
    return OrchestratorMode.NORMAL_OPERATION


def _decision(state: GlobalSystemState, cycle: OrchestratorCycle) -> OrchestratorDecision:
    if state.mode == OrchestratorMode.SURVIVAL_ORCHESTRATION:
        return OrchestratorDecision.ACTIVATE_SURVIVAL_MODE
    if state.mode == OrchestratorMode.EMERGENCY_ORCHESTRATION:
        return OrchestratorDecision.EMERGENCY_HALT_ROUTING
    if cycle.safe_mode:
        return OrchestratorDecision.ENTER_SAFE_GLOBAL_MODE
    if state.mode == OrchestratorMode.RECOVERY_COORDINATION:
        return OrchestratorDecision.ENABLE_RECOVERY_COORDINATION
    if state.mode == OrchestratorMode.LEARNING_COORDINATION:
        return OrchestratorDecision.ENABLE_LEARNING_COORDINATION
    if state.mode == OrchestratorMode.SUPERVISED_GLOBAL_MODE or cycle.requires_supervision:
        return OrchestratorDecision.REQUIRE_HUMAN_SUPERVISION
    if state.isolated_engines:
        return OrchestratorDecision.ISOLATE_UNSTABLE_MODULES
    if OrchestratorRisk.AUTONOMY_ESCALATION in state.risks:
        return OrchestratorDecision.FREEZE_LEARNING
    return OrchestratorDecision.CONTINUE_COORDINATED_OPERATION


def _transitions(state: GlobalSystemState) -> tuple[OrchestratorTransition, ...]:
    if state.mode == OrchestratorMode.NORMAL_OPERATION:
        return ()
    return (
        OrchestratorTransition(
            OrchestratorMode.NORMAL_OPERATION,
            state.mode,
            f"Dominant priority {state.dominant_priority.value} selected from global signals.",
            state.dominant_priority,
        ),
    )


def _cycle_actions(risks: tuple[OrchestratorRisk, ...], safe_mode: bool) -> tuple[str, ...]:
    actions: list[str] = []
    if safe_mode:
        actions.append("route_only_safety_critical_engines")
    if OrchestratorRisk.GLOBAL_INSTABILITY in risks:
        actions.append("coordinate_recovery")
    if OrchestratorRisk.CROSS_LAYER_CONFLICT in risks:
        actions.append("pause_conflicting_routes")
    if OrchestratorRisk.CONSENSUS_BREAKDOWN in risks:
        actions.append("rebuild_consensus")
    if not actions:
        actions.append("continue_coordination")
    return tuple(actions)


def _safe_mode_required(data: GlobalOrchestratorInput) -> bool:
    return (
        (data.strategic_arbitration is not None and data.strategic_arbitration.mode in {ArbitrationMode.EMERGENCY_LOCKDOWN, ArbitrationMode.SURVIVAL_MODE} or (data.strategic_arbitration is not None and data.strategic_arbitration.decision in {ArbitrationDecision.EMERGENCY_LOCKDOWN, ArbitrationDecision.ENABLE_SAFE_MODE, ArbitrationDecision.STOP_EXECUTION}))
        or (data.collective_consensus is not None and data.collective_consensus.decision in {ConsensusDecision.EMERGENCY_HALT, ConsensusDecision.ENTER_SAFE_MODE, ConsensusDecision.BLOCK_COLLECTIVE_ACTION})
        or (data.intent_alignment is not None and data.intent_alignment.mode in {IntentAlignmentMode.CRITICAL_REALIGNMENT, IntentAlignmentMode.MISALIGNED})
        or (data.system_integrity is not None and data.system_integrity.status in {SystemIntegrityStatus.COMPROMISED, SystemIntegrityStatus.PROTECTION_MODE, SystemIntegrityStatus.ROLLBACK_RECOMMENDED})
        or (data.operational_awareness is not None and data.operational_awareness.health_status in {OperationalHealthStatus.CRITICAL, OperationalHealthStatus.COLLAPSING})
    )


def _survival_required(data: GlobalOrchestratorInput) -> bool:
    return (
        (data.recovery_resilience is not None and data.recovery_resilience.mode == RecoveryMode.SURVIVAL_MODE)
        or (data.mission_continuity is not None and data.mission_continuity.mode == MissionContinuityMode.SURVIVAL_CONTINUITY)
        or (data.executive_result is not None and data.executive_result.state.mode == ExecutiveMode.SURVIVAL)
    )


def _supervision_blocks(data: GlobalOrchestratorInput) -> bool:
    return data.supervisor_result is not None and (
        not data.supervisor_result.final_executable
        or data.supervisor_result.decision in {SupervisorDecision.REQUIRE_HUMAN_REVIEW, SupervisorDecision.OVERRIDE_TO_BLOCK, SupervisorDecision.OVERRIDE_TO_STOP_SESSION, SupervisorDecision.EMERGENCY_HALT}
    )


def _execution_allowed(data: GlobalOrchestratorInput) -> bool:
    return data.executive_result is not None and data.executive_result.decision.allow_execution


def _autonomy_escalation(data: GlobalOrchestratorInput) -> bool:
    return data.self_evaluation is not None and data.self_evaluation.autonomy_recommendation == SystemAutonomyRecommendation.MAINTAIN_AUTONOMY and _safe_mode_required(data)


def _critical_transition(data: GlobalOrchestratorInput) -> bool:
    critical_count = 0
    if data.strategic_arbitration is not None and data.strategic_arbitration.mode == ArbitrationMode.EMERGENCY_LOCKDOWN:
        critical_count += 1
    if data.collective_consensus is not None and data.collective_consensus.mode == ConsensusMode.EMERGENCY_CONSENSUS:
        critical_count += 1
    if data.system_integrity is not None and data.system_integrity.status == SystemIntegrityStatus.COMPROMISED:
        critical_count += 1
    if data.operational_awareness is not None and data.operational_awareness.mode == OperationalAwarenessMode.CRITICAL:
        critical_count += 1
    if data.self_evaluation is not None and data.self_evaluation.status == SelfEvaluationStatus.CONTRADICTORY:
        critical_count += 1
    if data.behavioral_stability is not None and data.behavioral_stability.recovery_state == BehavioralRecoveryState.CRITICAL:
        critical_count += 1
    return critical_count >= 3


def _input(orchestrator_input: GlobalOrchestratorInput | None = None, **kwargs: Any) -> GlobalOrchestratorInput:
    if orchestrator_input is not None:
        return orchestrator_input
    return GlobalOrchestratorInput(**kwargs)


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "apply_global_safe_mode",
    "build_orchestration_graph",
    "compute_orchestration_confidence",
    "coordinate_engine_priorities",
    "coordinate_global_orchestrator",
    "detect_global_risks",
    "evaluate_global_system_state",
    "generate_orchestrator_recommendations",
    "render_global_orchestrator_markdown",
    "resolve_cross_layer_conflicts",
    "schedule_coordination_cycle",
]
