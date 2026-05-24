"""Offline cognitive consensus engine for AGIcore Trading."""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Optional

from agicore.trading.cognitive_consensus_models import (
    CognitiveConsensusAction,
    CognitiveConsensusEvent,
    CognitiveConsensusInput,
    CognitiveConsensusMode,
    CognitiveConsensusRecommendation,
    CognitiveConsensusResult,
    CognitiveConsensusRisk,
    CognitiveConsensusScore,
    CognitiveConsensusState,
    ConsensusMatrix,
    ConsensusNode,
    ConsensusReasoningChain,
    ConsensusScenario,
    ConsensusVote,
)


def _value(item: Any) -> str:
    if item is None:
        return ""
    if isinstance(item, Enum):
        return str(item.value)
    return str(item)


def _has(item: Any, *needles: str) -> bool:
    text = _value(item).upper()
    return any(needle.upper() in text for needle in needles)


def _get(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default) if obj is not None else default


def _as_tuple(items: Any) -> tuple[Any, ...]:
    if items is None:
        return ()
    if isinstance(items, tuple):
        return items
    if isinstance(items, list):
        return tuple(items)
    return (items,)


def _risks_contain(obj: Any, *needles: str) -> bool:
    return any(_has(risk, *needles) for risk in _as_tuple(_get(obj, "risks", ())))


def _clamp(value: int | float, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(round(value))))


def _average(values: Iterable[int | float]) -> int:
    usable = [float(value) for value in values if value is not None]
    if not usable:
        return 80
    return _clamp(sum(usable) / len(usable))


def _score(obj: Any, *names: str, default: int = 80) -> int:
    for name in names:
        value = _get(obj, name)
        if isinstance(value, (int, float)):
            return _clamp(value)
    return default


def _dedupe(items: Iterable[Any]) -> tuple[Any, ...]:
    seen: set[Any] = set()
    result: list[Any] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return tuple(result)


def _coherence_score(data: CognitiveConsensusInput) -> int:
    coherence = data.cognitive_coherence
    score = _score(coherence, "cognitive_coherence_score", default=80)
    audit = _score(data.self_reflection_audit, "reflection_quality_score", default=score)
    return _average((score, audit))


def _timeline_score(data: CognitiveConsensusInput) -> int:
    forecast = _score(data.scenario_forecast, "forecast_stability_score", default=80)
    timeline = _score(data.multi_timeline_simulation, "overall_survivability_score", default=forecast)
    return _average((forecast, timeline))


def _strategic_score(data: CognitiveConsensusInput) -> int:
    arbitration = _score(data.strategic_arbitration, "confidence_score", default=80)
    orchestrator = _score(data.global_orchestrator, "confidence_score", default=arbitration)
    return _average((arbitration, orchestrator))


def _policy_score(data: CognitiveConsensusInput) -> int:
    policy = _score(data.cognitive_policy, "cognitive_policy_score", "policy_score", default=80)
    governance = _score(data.cognitive_governance, "governance_score", "cognitive_governance_score", default=policy)
    return _average((policy, governance))


def _alignment_score(data: CognitiveConsensusInput) -> int:
    return _average(
        (
            _score(data.cognitive_alignment, "cognitive_alignment_score", default=80),
            _score(data.intent_integrity, "intent_integrity_score", default=80),
            _score(data.cognitive_identity, "cognitive_identity_score", "identity_score", default=80),
        )
    )


def _decision_score(data: CognitiveConsensusInput) -> int:
    return _average(
        (
            _score(data.collective_consensus, "collective_confidence_score", default=80),
            _score(data.global_orchestrator, "confidence_score", default=80),
            _score(data.strategic_arbitration, "confidence_score", default=80),
        )
    )


def _autonomy_score(data: CognitiveConsensusInput) -> int:
    score = 80
    if _has(_get(data.cognitive_governance, "autonomy_level"), "FULL"):
        score += 5
    if _has(_get(data.cognitive_governance, "autonomy_level"), "LOCKED", "OBSERVE", "HUMAN"):
        score -= 30
    if _has(_get(data.cognitive_policy, "mode"), "LOCKED", "SAFE", "RESTRICTED"):
        score -= 25
    if _risks_contain(data.intent_integrity, "AUTONOMY") or _risks_contain(data.cognitive_alignment, "AUTONOMY"):
        score -= 30
    return _clamp(score)


def detect_cognitive_consensus_risks(data: CognitiveConsensusInput) -> tuple[CognitiveConsensusRisk, ...]:
    """Detect consensus risks from compatible offline engine outputs."""

    risks: list[CognitiveConsensusRisk] = []

    if (
        _has(_get(data.cognitive_coherence, "state"), "LOGICAL_CONFLICT", "COHERENCE_AT_RISK", "COHERENCE_LOCKED")
        or _risks_contain(data.cognitive_coherence, "LOGICAL_CONTRADICTION", "REASONING_CHAIN_BREAK")
        or _has(_get(data.self_reflection_audit, "state"), "CONTRADICTORY", "AUDIT_REQUIRED", "CRITICAL")
    ):
        risks.append(CognitiveConsensusRisk.REASONING_CONFLICT)

    if (
        _has(_get(data.scenario_forecast, "decision"), "AVOID", "SAFE_MODE", "HUMAN_REVIEW", "REBUILD")
        or _has(_get(data.multi_timeline_simulation, "decision"), "AVOID", "SAFE_MODE", "HUMAN_REVIEW", "REBUILD")
        or _risks_contain(data.multi_timeline_simulation, "DIVERGENCE", "COLLAPSE", "LOW_SURVIVABILITY")
    ):
        risks.append(CognitiveConsensusRisk.TIMELINE_CONFLICT)

    if (
        _has(_get(data.strategic_arbitration, "severity"), "HIGH", "CRITICAL")
        or _has(_get(data.strategic_arbitration, "decision"), "STOP", "EMERGENCY", "ROLLBACK", "SUPERVISION")
        or _has(_get(data.global_orchestrator, "mode"), "EMERGENCY", "SURVIVAL")
    ):
        risks.append(CognitiveConsensusRisk.STRATEGIC_CONFLICT)

    if (
        _has(_get(data.recursive_world_model, "decision"), "REBUILD", "SAFE_MODE", "HUMAN_REVIEW", "FREEZE")
        or _risks_contain(
            data.recursive_world_model,
            "WORLD_MODEL_INCOHERENCE",
            "PLANNING_ACTION_MISMATCH",
            "ORCHESTRATION_DESYNC",
            "SAFETY_MODEL_FAILURE",
        )
    ):
        risks.append(CognitiveConsensusRisk.WORLD_MODEL_CONFLICT)

    if (
        _has(_get(data.cognitive_policy, "mode"), "LOCKED", "SAFE", "RESTRICTED", "AUDIT")
        or _has(_get(data.cognitive_governance, "mode"), "LOCKED", "EMERGENCY", "SAFE", "RESTRICTED")
        or _risks_contain(data.cognitive_policy, "POLICY_CONFLICT", "GOVERNANCE_POLICY_MISMATCH", "SAFETY")
    ):
        risks.append(CognitiveConsensusRisk.POLICY_CONFLICT)

    if (
        _has(_get(data.cognitive_alignment, "state"), "MISALIGNMENT", "LOCKED")
        or _has(_get(data.intent_integrity, "state"), "CONFLICT", "CORRUPTED", "LOCKED")
        or _has(_get(data.cognitive_identity, "state"), "CONFLICTED", "LOCKED", "AT_RISK")
        or _risks_contain(data.cognitive_alignment, "COLLAPSE", "BREAK")
    ):
        risks.append(CognitiveConsensusRisk.ALIGNMENT_CONFLICT)

    if (
        _has(_get(data.collective_consensus, "decision"), "NO_CONSENSUS", "EMERGENCY", "BLOCK")
        or (
            _has(_get(data.strategic_arbitration, "decision"), "STOP", "EMERGENCY")
            and _has(_get(data.global_orchestrator, "decision"), "CONTINUE")
        )
        or (
            _has(_get(data.collective_consensus, "decision"), "APPROVE")
            and _has(_get(data.strategic_arbitration, "decision"), "EMERGENCY", "STOP")
        )
    ):
        risks.append(CognitiveConsensusRisk.DECISION_DEADLOCK)

    if (
        _has(_get(data.collective_consensus, "mode"), "DEGRADED", "COLLAPSE")
        or _score(data.collective_consensus, "collective_confidence_score", default=80) < 60
        or _risks_contain(data.collective_consensus, "FRAGMENTATION", "AUTHORITY_CONFLICT")
    ):
        risks.append(CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION)

    if (
        _risks_contain(data.intent_integrity, "AUTONOMY")
        or _risks_contain(data.cognitive_alignment, "AUTONOMY")
        or _has(_get(data.cognitive_governance, "decision"), "DENY_AUTONOMY", "REDUCE_AUTONOMY")
    ):
        risks.append(CognitiveConsensusRisk.AUTONOMY_CONFLICT)

    critical_flags = sum(
        1
        for condition in (
            _has(_get(data.cognitive_stability, "state"), "CRITICAL", "COLLAPSING"),
            _has(_get(data.cognitive_coherence, "state"), "LOCKED", "SYSTEMIC"),
            _has(_get(data.cognitive_alignment, "state"), "LOCKED", "SYSTEMIC"),
            _has(_get(data.collective_consensus, "mode"), "COLLAPSE"),
            _has(_get(data.strategic_arbitration, "mode"), "EMERGENCY"),
            _has(_get(data.global_orchestrator, "mode"), "EMERGENCY", "SURVIVAL"),
        )
        if condition
    )
    if len(set(risks)) >= 6 or critical_flags >= 3:
        risks.append(CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE)

    return _dedupe(risks)


def compute_cognitive_consensus_score(
    data: CognitiveConsensusInput,
    risks: tuple[CognitiveConsensusRisk, ...] = (),
) -> CognitiveConsensusScore:
    """Compute a deterministic 0..100 score breakdown."""

    reasoning = _coherence_score(data)
    timeline = _timeline_score(data)
    strategic = _strategic_score(data)
    world = _score(data.recursive_world_model, "world_model_coherence_score", default=80)
    policy = _policy_score(data)
    alignment = _alignment_score(data)
    decision = _decision_score(data)
    autonomy = _autonomy_score(data)

    penalties = {
        CognitiveConsensusRisk.REASONING_CONFLICT: ("reasoning", 28),
        CognitiveConsensusRisk.TIMELINE_CONFLICT: ("timeline", 25),
        CognitiveConsensusRisk.STRATEGIC_CONFLICT: ("strategic", 30),
        CognitiveConsensusRisk.WORLD_MODEL_CONFLICT: ("world", 30),
        CognitiveConsensusRisk.POLICY_CONFLICT: ("policy", 30),
        CognitiveConsensusRisk.ALIGNMENT_CONFLICT: ("alignment", 32),
        CognitiveConsensusRisk.DECISION_DEADLOCK: ("decision", 35),
        CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION: ("decision", 25),
        CognitiveConsensusRisk.AUTONOMY_CONFLICT: ("autonomy", 32),
    }
    values = {
        "reasoning": reasoning,
        "timeline": timeline,
        "strategic": strategic,
        "world": world,
        "policy": policy,
        "alignment": alignment,
        "decision": decision,
        "autonomy": autonomy,
    }
    for risk in risks:
        if risk in penalties:
            target, penalty = penalties[risk]
            values[target] = _clamp(values[target] - penalty)

    systemic = _average(values.values())
    if CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks:
        systemic = _clamp(systemic - 35)

    return CognitiveConsensusScore(
        reasoning_consensus_score=values["reasoning"],
        timeline_consensus_score=values["timeline"],
        strategic_consensus_score=values["strategic"],
        world_model_consensus_score=values["world"],
        policy_consensus_score=values["policy"],
        alignment_consensus_score=values["alignment"],
        decision_consensus_score=values["decision"],
        autonomy_consensus_score=values["autonomy"],
        systemic_consensus_score=systemic,
    )


def _vote_from_score(name: str, source: str, score: int, risk: Optional[CognitiveConsensusRisk]) -> ConsensusVote:
    if risk == CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE or score < 30:
        vote = "BLOCK"
        safe = True
        reason = f"{source} requires consensus lock or blocking."
    elif risk is not None or score < 55:
        vote = "SAFE_MODE"
        safe = True
        reason = f"{source} reports conflict or weak confidence."
    elif score < 70:
        vote = "REVIEW"
        safe = False
        reason = f"{source} supports limited consensus with review."
    else:
        vote = "APPROVE"
        safe = False
        reason = f"{source} supports the current consensus."
    return ConsensusVote(
        node_name=name,
        vote=vote,
        confidence_score=score,
        reason=reason,
        supports_safe_mode=safe,
        risk=risk,
    )


def build_consensus_votes(
    data: CognitiveConsensusInput,
    score: Optional[CognitiveConsensusScore] = None,
    risks: tuple[CognitiveConsensusRisk, ...] = (),
) -> tuple[ConsensusVote, ...]:
    """Build explainable votes from cognitive subsystems."""

    score = score or compute_cognitive_consensus_score(data, risks)
    risk_by_node = {
        "reasoning": CognitiveConsensusRisk.REASONING_CONFLICT if CognitiveConsensusRisk.REASONING_CONFLICT in risks else None,
        "timelines": CognitiveConsensusRisk.TIMELINE_CONFLICT if CognitiveConsensusRisk.TIMELINE_CONFLICT in risks else None,
        "strategy": CognitiveConsensusRisk.STRATEGIC_CONFLICT if CognitiveConsensusRisk.STRATEGIC_CONFLICT in risks else None,
        "world_model": CognitiveConsensusRisk.WORLD_MODEL_CONFLICT if CognitiveConsensusRisk.WORLD_MODEL_CONFLICT in risks else None,
        "policy": CognitiveConsensusRisk.POLICY_CONFLICT if CognitiveConsensusRisk.POLICY_CONFLICT in risks else None,
        "alignment": CognitiveConsensusRisk.ALIGNMENT_CONFLICT if CognitiveConsensusRisk.ALIGNMENT_CONFLICT in risks else None,
        "collective_decision": (
            CognitiveConsensusRisk.DECISION_DEADLOCK
            if CognitiveConsensusRisk.DECISION_DEADLOCK in risks
            else CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION
            if CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION in risks
            else None
        ),
        "autonomy": CognitiveConsensusRisk.AUTONOMY_CONFLICT if CognitiveConsensusRisk.AUTONOMY_CONFLICT in risks else None,
    }
    if CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks:
        risk_by_node["systemic"] = CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE

    votes = (
        _vote_from_score("reasoning", "Cognitive coherence and audit", score.reasoning_consensus_score, risk_by_node["reasoning"]),
        _vote_from_score("timelines", "Forecast and multi-timeline simulation", score.timeline_consensus_score, risk_by_node["timelines"]),
        _vote_from_score("strategy", "Strategic arbitration and orchestration", score.strategic_consensus_score, risk_by_node["strategy"]),
        _vote_from_score("world_model", "Recursive world model", score.world_model_consensus_score, risk_by_node["world_model"]),
        _vote_from_score("policy", "Cognitive policy and governance", score.policy_consensus_score, risk_by_node["policy"]),
        _vote_from_score("alignment", "Alignment, intent and identity", score.alignment_consensus_score, risk_by_node["alignment"]),
        _vote_from_score("collective_decision", "Collective decision layer", score.decision_consensus_score, risk_by_node["collective_decision"]),
        _vote_from_score("autonomy", "Autonomy control", score.autonomy_consensus_score, risk_by_node["autonomy"]),
    )
    if "systemic" in risk_by_node:
        votes += (_vote_from_score("systemic", "Systemic consensus controller", score.systemic_consensus_score, risk_by_node["systemic"]),)
    return votes


def build_consensus_reasoning(data: CognitiveConsensusInput) -> tuple[ConsensusReasoningChain, ...]:
    """Build reasoning chains to compare before consensus."""

    chains: list[ConsensusReasoningChain] = []
    coherence_chains = _as_tuple(_get(data.cognitive_coherence, "reasoning_chains", ()))
    for chain in coherence_chains:
        chains.append(
            ConsensusReasoningChain(
                name=_get(chain, "name", "coherence_chain"),
                steps=tuple(str(step) for step in _as_tuple(_get(chain, "steps", ()))),
                score=_score(chain, "score", default=80),
                agreed=bool(_get(chain, "complete", _get(chain, "agreed", True))),
                conflict=_get(chain, "broken_step", _get(chain, "conflict", None)),
            )
        )

    if not chains:
        chains.append(
            ConsensusReasoningChain(
                name="default_reasoning_chain",
                steps=("collect cognitive state", "compare decisions", "select safest consensus"),
                score=_coherence_score(data),
                agreed=not _has(_get(data.cognitive_coherence, "state"), "CONFLICT", "LOCKED"),
                conflict=None if not _risks_contain(data.cognitive_coherence, "CONTRADICTION") else "coherence risk detected",
            )
        )

    chains.append(
        ConsensusReasoningChain(
            name="strategic_consensus_chain",
            steps=("evaluate arbitration", "compare orchestration", "check collective agreement"),
            score=_strategic_score(data),
            agreed=not _has(_get(data.strategic_arbitration, "decision"), "EMERGENCY", "STOP"),
            conflict="strategic arbitration blocks consensus"
            if _has(_get(data.strategic_arbitration, "decision"), "EMERGENCY", "STOP")
            else None,
        )
    )
    return tuple(chains)


def _build_scenarios(data: CognitiveConsensusInput) -> tuple[ConsensusScenario, ...]:
    scenarios: list[ConsensusScenario] = []
    for scenario in _as_tuple(_get(data.scenario_forecast, "scenarios", ())):
        scenarios.append(
            ConsensusScenario(
                name=_value(_get(scenario, "scenario_type", _get(scenario, "name", "forecast_scenario"))),
                probability_score=_score(scenario, "probability_score", default=50),
                survivability_score=_score(scenario, "stability_score", "survivability_score", default=70),
                preferred=bool(_get(scenario, "preferred", False)),
                conflict=_get(scenario, "risk_note", None),
            )
        )
    for timeline in _as_tuple(_get(data.multi_timeline_simulation, "timeline_states", ())):
        scenarios.append(
            ConsensusScenario(
                name=_value(_get(timeline, "timeline_type", _get(timeline, "name", "timeline_state"))),
                probability_score=50,
                survivability_score=_score(timeline, "survivability_score", default=70),
                preferred=_has(_get(timeline, "outcome"), "STABLE", "IMPROVING", "RECOVERING"),
                conflict=_value(_get(timeline, "outcome")) if _has(_get(timeline, "outcome"), "COLLAPSING", "UNSTABLE") else None,
            )
        )
    if not scenarios:
        scenarios.append(
            ConsensusScenario(
                name="baseline_consensus_scenario",
                probability_score=60,
                survivability_score=_timeline_score(data),
                preferred=True,
            )
        )
    return tuple(scenarios)


def reconcile_conflicts(
    risks: tuple[CognitiveConsensusRisk, ...],
    votes: tuple[ConsensusVote, ...] = (),
) -> tuple[str, ...]:
    """Return deterministic conflict reconciliation notes."""

    resolutions: list[str] = []
    if CognitiveConsensusRisk.REASONING_CONFLICT in risks:
        resolutions.append("Reconcile reasoning chains before expanding decision scope.")
    if CognitiveConsensusRisk.TIMELINE_CONFLICT in risks:
        resolutions.append("Prefer the safest survivable timeline until forecast and simulation agree.")
    if CognitiveConsensusRisk.WORLD_MODEL_CONFLICT in risks:
        resolutions.append("Repair world model alignment before routing actions.")
    if CognitiveConsensusRisk.POLICY_CONFLICT in risks:
        resolutions.append("Enforce restrictive cognitive policy until governance and policy agree.")
    if CognitiveConsensusRisk.ALIGNMENT_CONFLICT in risks:
        resolutions.append("Realign mission, intent and identity before approving consensus.")
    if CognitiveConsensusRisk.DECISION_DEADLOCK in risks:
        resolutions.append("Escalate deadlocked decisions to supervision.")
    if CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks:
        resolutions.append("Lock consensus state and enter safe consensus mode.")
    if not resolutions and votes:
        resolutions.append("Consensus can be preserved with monitoring.")
    return tuple(resolutions)


def _build_nodes(votes: tuple[ConsensusVote, ...]) -> tuple[ConsensusNode, ...]:
    return tuple(
        ConsensusNode(
            name=vote.node_name,
            source=vote.reason,
            confidence_score=vote.confidence_score,
            position=vote.vote,
            risk=vote.risk,
        )
        for vote in votes
    )


def build_consensus_matrix(
    data: CognitiveConsensusInput,
    score: Optional[CognitiveConsensusScore] = None,
    risks: tuple[CognitiveConsensusRisk, ...] = (),
) -> ConsensusMatrix:
    """Build the explainable consensus matrix."""

    score = score or compute_cognitive_consensus_score(data, risks)
    votes = build_consensus_votes(data, score, risks)
    nodes = _build_nodes(votes)
    chains = build_consensus_reasoning(data)
    scenarios = _build_scenarios(data)
    resolutions = reconcile_conflicts(risks, votes)
    conflict_count = len([vote for vote in votes if vote.vote in {"SAFE_MODE", "BLOCK"}])
    approve_count = len([vote for vote in votes if vote.vote == "APPROVE"])
    winning_position = "APPROVE"
    if any(vote.vote == "BLOCK" for vote in votes):
        winning_position = "BLOCK"
    elif any(vote.vote == "SAFE_MODE" for vote in votes):
        winning_position = "SAFE_MODE"
    elif approve_count < len(votes) / 2:
        winning_position = "REVIEW"
    agreement_score = _clamp(100 - (conflict_count * 12) - len(risks) * 4)
    global_score = _average((score.systemic_consensus_score, agreement_score))
    return ConsensusMatrix(
        nodes=nodes,
        votes=votes,
        reasoning_chains=chains,
        scenarios=scenarios,
        global_score=global_score,
        agreement_score=agreement_score,
        conflict_count=conflict_count,
        winning_position=winning_position,
        conflict_resolutions=resolutions,
        locked=CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks,
        autonomy_reduced=any(
            risk in risks
            for risk in (
                CognitiveConsensusRisk.AUTONOMY_CONFLICT,
                CognitiveConsensusRisk.DECISION_DEADLOCK,
                CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE,
            )
        ),
    )


def generate_cognitive_consensus_recommendations(
    risks: tuple[CognitiveConsensusRisk, ...],
) -> tuple[CognitiveConsensusRecommendation, ...]:
    recommendations: list[CognitiveConsensusRecommendation] = [
        CognitiveConsensusRecommendation.CONTINUE_CONSENSUS_MONITORING,
        CognitiveConsensusRecommendation.UPDATE_CONSENSUS_STATE,
    ]
    if CognitiveConsensusRisk.REASONING_CONFLICT in risks:
        recommendations.append(CognitiveConsensusRecommendation.EXTEND_REASONING_DEBATE)
    if CognitiveConsensusRisk.TIMELINE_CONFLICT in risks:
        recommendations.append(CognitiveConsensusRecommendation.RECHECK_TIMELINE_ALIGNMENT)
    if CognitiveConsensusRisk.WORLD_MODEL_CONFLICT in risks:
        recommendations.append(CognitiveConsensusRecommendation.REPAIR_WORLD_MODEL_ALIGNMENT)
    if any(
        risk in risks
        for risk in (
            CognitiveConsensusRisk.STRATEGIC_CONFLICT,
            CognitiveConsensusRisk.POLICY_CONFLICT,
            CognitiveConsensusRisk.ALIGNMENT_CONFLICT,
            CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION,
        )
    ):
        recommendations.append(CognitiveConsensusRecommendation.REBUILD_CONFLICTED_CONSENSUS)
        recommendations.append(CognitiveConsensusRecommendation.REDUCE_DECISION_SCOPE)
    if any(
        risk in risks
        for risk in (
            CognitiveConsensusRisk.DECISION_DEADLOCK,
            CognitiveConsensusRisk.AUTONOMY_CONFLICT,
            CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE,
        )
    ):
        recommendations.append(CognitiveConsensusRecommendation.ENABLE_SAFE_CONSENSUS)
        recommendations.append(CognitiveConsensusRecommendation.REQUIRE_MANUAL_VALIDATION)
    if risks:
        recommendations.append(CognitiveConsensusRecommendation.PRESERVE_CONSENSUS_SNAPSHOT)
    return _dedupe(recommendations)


def _actions_for_risks(risks: tuple[CognitiveConsensusRisk, ...]) -> tuple[CognitiveConsensusAction, ...]:
    actions: list[CognitiveConsensusAction] = [CognitiveConsensusAction.PRESERVE_CONSENSUS_STATE]
    if CognitiveConsensusRisk.REASONING_CONFLICT in risks:
        actions.append(CognitiveConsensusAction.RECONCILE_REASONING)
    if CognitiveConsensusRisk.TIMELINE_CONFLICT in risks:
        actions.append(CognitiveConsensusAction.RECONCILE_TIMELINES)
    if CognitiveConsensusRisk.WORLD_MODEL_CONFLICT in risks:
        actions.append(CognitiveConsensusAction.RECONCILE_WORLD_MODEL)
    if any(
        risk in risks
        for risk in (
            CognitiveConsensusRisk.STRATEGIC_CONFLICT,
            CognitiveConsensusRisk.POLICY_CONFLICT,
            CognitiveConsensusRisk.ALIGNMENT_CONFLICT,
            CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION,
        )
    ):
        actions.append(CognitiveConsensusAction.REBUILD_CONSENSUS)
    if any(
        risk in risks
        for risk in (
            CognitiveConsensusRisk.AUTONOMY_CONFLICT,
            CognitiveConsensusRisk.DECISION_DEADLOCK,
            CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE,
        )
    ):
        actions.append(CognitiveConsensusAction.REDUCE_AUTONOMY)
        actions.append(CognitiveConsensusAction.REQUIRE_SUPERVISION)
    if CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks:
        actions.append(CognitiveConsensusAction.FORCE_SAFE_MODE)
        actions.append(CognitiveConsensusAction.LOCK_CONSENSUS_STATE)
        actions.append(CognitiveConsensusAction.ESCALATE_TO_HUMAN)
    return _dedupe(actions)


def _state_and_mode(
    score: int,
    risks: tuple[CognitiveConsensusRisk, ...],
    matrix: ConsensusMatrix,
) -> tuple[CognitiveConsensusState, CognitiveConsensusMode]:
    if CognitiveConsensusRisk.SYSTEMIC_CONSENSUS_COLLAPSE in risks or matrix.locked:
        return CognitiveConsensusState.CONSENSUS_LOCKED, CognitiveConsensusMode.LOCKED_CONSENSUS_MODE
    if len(risks) >= 7 or score < 30:
        return CognitiveConsensusState.SYSTEMIC_CONFLICT, CognitiveConsensusMode.HUMAN_SUPERVISION_MODE
    if len(risks) >= 5 or score < 45:
        return CognitiveConsensusState.HIGH_CONFLICT_STATE, CognitiveConsensusMode.CONFLICT_RESOLUTION_MODE
    if CognitiveConsensusRisk.CONSENSUS_FRAGMENTATION in risks:
        return CognitiveConsensusState.CONSENSUS_FRAGMENTED, CognitiveConsensusMode.SAFE_CONSENSUS_MODE
    if CognitiveConsensusRisk.STRATEGIC_CONFLICT in risks:
        return CognitiveConsensusState.STRATEGIC_DISAGREEMENT, CognitiveConsensusMode.STRATEGIC_ARBITRATION
    if risks:
        return CognitiveConsensusState.PARTIAL_CONSENSUS, CognitiveConsensusMode.CONSENSUS_VALIDATION
    if score < 75:
        return CognitiveConsensusState.CONSENSUS_MONITORING, CognitiveConsensusMode.NORMAL_CONSENSUS
    return CognitiveConsensusState.CONSENSUS_REACHED, CognitiveConsensusMode.NORMAL_CONSENSUS


def evaluate_cognitive_consensus(data: CognitiveConsensusInput) -> CognitiveConsensusResult:
    """Evaluate cognitive consensus across reasoning, timelines and safety engines."""

    risks = detect_cognitive_consensus_risks(data)
    score_breakdown = compute_cognitive_consensus_score(data, risks)
    matrix = build_consensus_matrix(data, score_breakdown, risks)
    score = _clamp(matrix.global_score)
    state, mode = _state_and_mode(score, risks, matrix)
    actions = _actions_for_risks(risks)
    recommendations = generate_cognitive_consensus_recommendations(risks)
    events = (
        CognitiveConsensusEvent(
            name="COGNITIVE_CONSENSUS_EVALUATED",
            detail=f"Consensus score {score} with {len(risks)} risk(s).",
            severity="WARNING" if risks else "INFO",
        ),
    )
    summary = (
        "Cognitive consensus locked due to systemic conflict."
        if state == CognitiveConsensusState.CONSENSUS_LOCKED
        else "Cognitive consensus requires conflict resolution."
        if risks
        else "Cognitive consensus reached and remains offline-only."
    )
    return CognitiveConsensusResult(
        state=state,
        mode=mode,
        cognitive_consensus_score=score,
        score_breakdown=score_breakdown,
        nodes=matrix.nodes,
        votes=matrix.votes,
        reasoning_chains=matrix.reasoning_chains,
        scenarios=matrix.scenarios,
        matrix=matrix,
        risks=risks,
        actions=actions,
        recommendations=recommendations,
        events=events,
        summary=summary,
    )


def render_cognitive_consensus_markdown(result: CognitiveConsensusResult) -> str:
    """Render a concise Markdown report for the cognitive consensus engine."""

    votes = "\n".join(
        f"- {vote.node_name}: {vote.vote} ({vote.confidence_score}/100) - {vote.reason}"
        for vote in result.votes
    ) or "- Aucun vote."
    reasoning = "\n".join(
        f"- {chain.name}: {chain.score}/100, agreed={chain.agreed}, conflict={chain.conflict or 'none'}"
        for chain in result.reasoning_chains
    ) or "- Aucun reasoning chain."
    matrix = "\n".join(
        (
            f"- global_score: {result.matrix.global_score}",
            f"- agreement_score: {result.matrix.agreement_score}",
            f"- winning_position: {result.matrix.winning_position}",
            f"- conflict_count: {result.matrix.conflict_count}",
            f"- autonomy_reduced: {result.matrix.autonomy_reduced}",
            f"- locked: {result.matrix.locked}",
        )
    )
    risks = "\n".join(f"- {risk.value}" for risk in result.risks) or "- Aucun risque critique."
    actions = "\n".join(f"- {action.value}" for action in result.actions) or "- Aucune action."
    recommendations = "\n".join(f"- {rec.value}" for rec in result.recommendations) or "- Aucune recommandation."
    resolutions = "\n".join(f"- {item}" for item in result.matrix.conflict_resolutions) or "- Aucun conflit a reconcilier."

    return "\n".join(
        (
            "# Cognitive Consensus State",
            f"- State: {result.state.value}",
            f"- Mode: {result.mode.value}",
            "",
            "# Consensus Score",
            f"- Score: {result.cognitive_consensus_score}/100",
            f"- Systemic: {result.score_breakdown.systemic_consensus_score}/100",
            "",
            "# Consensus Votes",
            votes,
            "",
            "# Reasoning Debate",
            reasoning,
            "",
            "# Consensus Matrix",
            matrix,
            "",
            "# Consensus Risks",
            risks,
            "",
            "# Actions",
            actions,
            "",
            "# Recommendations",
            recommendations,
            "",
            "# AGIcore Cognitive Consensus Outlook",
            f"- Summary: {result.summary}",
            resolutions,
            "- Offline only: no broker, no external API, no live execution.",
        )
    )
