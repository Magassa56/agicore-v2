"""Offline hierarchical supervisor system for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Iterable

from .context_scoring_models import TradeContextDecision
from .hierarchical_supervisor_models import (
    AgentReliabilityScore,
    SupervisorDecision,
    SupervisorEvent,
    SupervisorInput,
    SupervisorOverride,
    SupervisorResult,
    SupervisorRole,
)
from .multi_agent_models import (
    AgentConfidence,
    AgentConsensusStatus,
    AgentCoordinationEvent,
    AgentCoordinationResult,
    AgentVote,
    TradingAgentRole,
)
from .paper_execution_models import PaperExecutionDecision
from .reward_models import RewardLabel
from .safe_rl_models import SafeRLStatus
from .scenario_replay_models import ReplayArenaStatus
from .semi_auto_decision_models import SemiAutoDecision


def evaluate_supervisor_decision(
    supervisor_input: SupervisorInput | None = None,
    **kwargs,
) -> SupervisorResult:
    """Evaluate the final offline supervisor decision above agent consensus."""
    data = _input(supervisor_input, **kwargs)
    reliability = compute_agent_reliability(
        data.coordination_result.votes if data.coordination_result is not None else (),
        coordination_result=data.coordination_result,
        prior_reliability=data.prior_reliability,
    )
    overrides = _required_overrides(data, reliability)
    decision = _decision_from_overrides(data, overrides)
    events = _events_for_decision(decision, overrides)
    trusted = tuple(score.role for score in reliability if score.trusted)
    watch = tuple(score.role for score in reliability if not score.trusted)
    conflicts = _conflicts(data, reliability)
    risks = _critical_risks(data, overrides, reliability)
    return SupervisorResult(
        decision=decision,
        final_executable=_final_executable(decision),
        applied_overrides=overrides,
        reliability_scores=reliability,
        trusted_agents=trusted,
        agents_to_watch=watch,
        conflicts_detected=conflicts,
        critical_risks=risks,
        events=events,
        recommendation=_recommendation(decision, overrides, conflicts, risks),
    )


def compute_agent_reliability(
    votes: Iterable[AgentCoordinationEvent],
    *,
    coordination_result: AgentCoordinationResult | None = None,
    prior_reliability: tuple[AgentReliabilityScore, ...] = (),
) -> tuple[AgentReliabilityScore, ...]:
    """Compute deterministic reliability scores from current/prior votes."""
    current_votes = tuple(votes)
    prior_by_role = {score.role: score for score in prior_reliability}
    final_vote = coordination_result.final_vote if coordination_result is not None else None
    scores: list[AgentReliabilityScore] = []
    for role in TradingAgentRole:
        role_votes = tuple(event for event in current_votes if event.role == role)
        prior = prior_by_role.get(role)
        votes_count = len(role_votes) + (prior.votes_count if prior is not None else 0)
        coherent = sum(1 for event in role_votes if final_vote is None or event.vote == final_vote)
        coherent += prior.coherent_votes if prior is not None else 0
        blocking = sum(1 for event in role_votes if event.vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION})
        blocking += prior.blocking_votes if prior is not None else 0
        risk_notes = sum(len(event.risk_notes) for event in role_votes)
        risk_notes += prior.risk_notes_count if prior is not None else 0
        confidence_bonus = sum(_confidence_bonus(event.confidence) for event in role_votes)
        base = 55 + confidence_bonus
        if votes_count:
            base += (coherent / votes_count) * 25
        base -= min(25, risk_notes * 4)
        if role in {TradingAgentRole.RISK_GUARDIAN, TradingAgentRole.SAFE_RL_SUPERVISOR} and blocking:
            base += 8
        if prior is not None:
            base = (base + prior.reliability_score) / 2
        score = _clamp(base)
        reasons = _reliability_reasons(role_votes, score, risk_notes, blocking)
        scores.append(
            AgentReliabilityScore(
                role=role,
                reliability_score=score,
                votes_count=votes_count,
                coherent_votes=coherent,
                blocking_votes=blocking,
                risk_notes_count=risk_notes,
                trusted=score >= 60,
                reasons=reasons,
            )
        )
    return tuple(scores)


def apply_supervisor_override(
    decision: SupervisorDecision,
    overrides: tuple[SupervisorOverride, ...] | list[SupervisorOverride],
) -> SupervisorDecision:
    """Apply hierarchical safety overrides to a proposed supervisor decision."""
    override_tuple = tuple(overrides)
    if SupervisorOverride.EMERGENCY_HALT in override_tuple:
        return SupervisorDecision.EMERGENCY_HALT
    if SupervisorOverride.STOP_SESSION in override_tuple:
        return SupervisorDecision.OVERRIDE_TO_STOP_SESSION
    if any(
        override in override_tuple
        for override in (
            SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS,
            SupervisorOverride.BLOCK_SAFE_RL,
            SupervisorOverride.BLOCK_RISK_AGENT,
            SupervisorOverride.BLOCK_EXECUTION_REJECTED,
        )
    ):
        return SupervisorDecision.OVERRIDE_TO_BLOCK
    if SupervisorOverride.REQUIRE_REVIEW_LOW_CONFIDENCE in override_tuple:
        return SupervisorDecision.REQUIRE_HUMAN_REVIEW
    if SupervisorOverride.REDUCE_RISK_CONFLICT in override_tuple:
        return SupervisorDecision.APPROVE_WITH_REDUCED_RISK
    return decision


def render_supervisor_markdown(result: SupervisorResult) -> str:
    """Render the hierarchical supervisor result as Markdown."""
    lines = [
        "# Hierarchical Supervisor System",
        "",
        "## Decision superviseur",
        "",
        f"- Decision: {result.decision.value}",
        "",
        "## Overrides appliques",
        "",
        *_override_lines(result.applied_overrides),
        "",
        "## Agents fiables / agents a surveiller",
        "",
        f"- Trusted: {_join_agents(result.trusted_agents)}",
        f"- Watch: {_join_agents(result.agents_to_watch)}",
        "",
        "## Conflits detectes",
        "",
        *_bullet_lines(result.conflicts_detected),
        "",
        "## Risques critiques",
        "",
        *_bullet_lines(result.critical_risks),
        "",
        "## Decision finale executable",
        "",
        f"- Executable: {result.final_executable}",
        "",
        "## Recommandation AGIcore",
        "",
        f"- {result.recommendation}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _required_overrides(
    data: SupervisorInput,
    reliability: tuple[AgentReliabilityScore, ...],
) -> tuple[SupervisorOverride, ...]:
    overrides: list[SupervisorOverride] = []
    coordination = data.coordination_result
    if coordination is not None:
        if coordination.final_vote == AgentVote.STOP_SESSION:
            overrides.append(SupervisorOverride.STOP_SESSION)
        if coordination.consensus_status in {AgentConsensusStatus.CONSENSUS_BLOCK, AgentConsensusStatus.CONSENSUS_STOP_SESSION}:
            overrides.append(SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS)
        hard_blockers = {TradingAgentRole.RISK_GUARDIAN, TradingAgentRole.SAFE_RL_SUPERVISOR}
        if any(role in hard_blockers for role in coordination.blocking_agents):
            overrides.append(SupervisorOverride.BLOCK_RISK_AGENT)
        if coordination.disagreements and coordination.consensus_score < 70:
            overrides.append(SupervisorOverride.REDUCE_RISK_CONFLICT)
        if coordination.consensus_score < 45:
            overrides.append(SupervisorOverride.REQUIRE_REVIEW_LOW_CONFIDENCE)
    if data.safe_rl_result is not None and data.safe_rl_result.status == SafeRLStatus.BLOCKED:
        overrides.append(SupervisorOverride.BLOCK_SAFE_RL)
    if data.context_score is not None and data.context_score.decision == TradeContextDecision.NO_TRADE:
        overrides.append(SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS)
    if data.semi_auto_decision is not None and data.semi_auto_decision.decision == SemiAutoDecision.STOP_SESSION:
        overrides.append(SupervisorOverride.STOP_SESSION)
    if data.paper_execution is not None:
        if data.paper_execution.decision == PaperExecutionDecision.PRECHECK_REJECTED or not data.paper_execution.accepted:
            overrides.append(SupervisorOverride.BLOCK_EXECUTION_REJECTED)
    if data.reward_evaluation is not None and data.reward_evaluation.reward_label == RewardLabel.DANGEROUS_DECISION:
        overrides.append(SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS)
    if data.arena_result is not None and data.arena_result.status == ReplayArenaStatus.BLOCKED_BY_SAFETY:
        overrides.append(SupervisorOverride.EMERGENCY_HALT)
    weak_trusted_agents = [score for score in reliability if score.votes_count > 0 and score.reliability_score < 45]
    if weak_trusted_agents:
        overrides.append(SupervisorOverride.REQUIRE_REVIEW_LOW_CONFIDENCE)
    return tuple(dict.fromkeys(overrides or [SupervisorOverride.NONE]))


def _decision_from_overrides(data: SupervisorInput, overrides: tuple[SupervisorOverride, ...]) -> SupervisorDecision:
    if overrides != (SupervisorOverride.NONE,):
        return apply_supervisor_override(SupervisorDecision.APPROVE_SYSTEM_DECISION, overrides)
    coordination = data.coordination_result
    if coordination is None:
        return SupervisorDecision.NO_ACTION
    if coordination.final_vote == AgentVote.APPROVE_REDUCED_RISK:
        return SupervisorDecision.APPROVE_WITH_REDUCED_RISK
    if coordination.final_vote == AgentVote.REQUIRE_REVIEW:
        return SupervisorDecision.REQUIRE_HUMAN_REVIEW
    if coordination.final_vote == AgentVote.APPROVE:
        return SupervisorDecision.APPROVE_SYSTEM_DECISION
    if coordination.final_vote == AgentVote.NO_OPINION:
        return SupervisorDecision.NO_ACTION
    return SupervisorDecision.OVERRIDE_TO_BLOCK


def _events_for_decision(
    decision: SupervisorDecision,
    overrides: tuple[SupervisorOverride, ...],
) -> tuple[SupervisorEvent, ...]:
    now = datetime.now(UTC)
    roles = _roles_for_decision(decision, overrides)
    return tuple(
        SupervisorEvent(
            role=role,
            decision=decision,
            override=overrides[0] if overrides else SupervisorOverride.NONE,
            message=_event_message(role, decision, overrides),
            timestamp=now,
        )
        for role in roles
    )


def _roles_for_decision(
    decision: SupervisorDecision,
    overrides: tuple[SupervisorOverride, ...],
) -> tuple[SupervisorRole, ...]:
    roles = [SupervisorRole.CHIEF_SUPERVISOR]
    if any(override in overrides for override in (SupervisorOverride.BLOCK_SAFE_RL, SupervisorOverride.BLOCK_RISK_AGENT, SupervisorOverride.BLOCK_DANGEROUS_CONSENSUS)):
        roles.append(SupervisorRole.RISK_SUPREME_CONTROLLER)
    if SupervisorOverride.EMERGENCY_HALT in overrides or decision == SupervisorDecision.EMERGENCY_HALT:
        roles.append(SupervisorRole.EMERGENCY_HALT_SUPERVISOR)
    if SupervisorOverride.REDUCE_RISK_CONFLICT in overrides:
        roles.append(SupervisorRole.CONFLICT_RESOLUTION_ENGINE)
    if SupervisorOverride.REQUIRE_REVIEW_LOW_CONFIDENCE in overrides:
        roles.append(SupervisorRole.AGENT_TRUST_MONITOR)
    if decision in {SupervisorDecision.APPROVE_SYSTEM_DECISION, SupervisorDecision.APPROVE_WITH_REDUCED_RISK, SupervisorDecision.OVERRIDE_TO_BLOCK}:
        roles.append(SupervisorRole.EXECUTION_FINAL_APPROVER)
    return tuple(dict.fromkeys(roles))


def _conflicts(
    data: SupervisorInput,
    reliability: tuple[AgentReliabilityScore, ...],
) -> tuple[str, ...]:
    conflicts: list[str] = []
    if data.coordination_result is not None:
        conflicts.extend(data.coordination_result.disagreements)
        if data.coordination_result.final_vote == AgentVote.APPROVE and data.safe_rl_result is not None and data.safe_rl_result.status == SafeRLStatus.BLOCKED:
            conflicts.append("Consensus approves while Safe RL is BLOCKED.")
    weak = [score.role.value for score in reliability if score.votes_count > 0 and score.reliability_score < 45]
    if weak:
        conflicts.append(f"Low agent reliability detected: {', '.join(weak)}.")
    return tuple(dict.fromkeys(conflicts))


def _critical_risks(
    data: SupervisorInput,
    overrides: tuple[SupervisorOverride, ...],
    reliability: tuple[AgentReliabilityScore, ...],
) -> tuple[str, ...]:
    risks: list[str] = []
    if data.coordination_result is not None:
        risks.extend(data.coordination_result.risks_detected)
    if data.safe_rl_result is not None:
        risks.extend(data.safe_rl_result.risks_detected)
    if data.semi_auto_decision is not None:
        risks.extend(data.semi_auto_decision.detected_risks)
        risks.extend(data.semi_auto_decision.blocking_reasons)
    if data.paper_execution is not None and not data.paper_execution.accepted:
        risks.extend(data.paper_execution.precheck_reasons)
    if data.reward_evaluation is not None and data.reward_evaluation.normalized_reward < 50:
        risks.extend(data.reward_evaluation.improvement_actions)
    if data.arena_result is not None:
        risks.extend(data.arena_result.risks_detected)
    if any(override != SupervisorOverride.NONE for override in overrides):
        risks.append("Supervisor override is active.")
    watch = [score.role.value for score in reliability if not score.trusted and score.votes_count > 0]
    if watch:
        risks.append(f"Agents to watch: {', '.join(watch)}.")
    return tuple(dict.fromkeys(risks))


def _final_executable(decision: SupervisorDecision) -> bool:
    return decision in {SupervisorDecision.APPROVE_SYSTEM_DECISION, SupervisorDecision.APPROVE_WITH_REDUCED_RISK}


def _recommendation(
    decision: SupervisorDecision,
    overrides: tuple[SupervisorOverride, ...],
    conflicts: tuple[str, ...],
    risks: tuple[str, ...],
) -> str:
    if decision == SupervisorDecision.EMERGENCY_HALT:
        return "Emergency halt: stop the session and keep all execution offline/review-only."
    if decision == SupervisorDecision.OVERRIDE_TO_STOP_SESSION:
        return "Override to STOP_SESSION: stop trading activity and require review."
    if decision == SupervisorDecision.OVERRIDE_TO_BLOCK:
        return "Override to BLOCK: prevent execution until blocking risks are cleared."
    if decision == SupervisorDecision.REQUIRE_HUMAN_REVIEW:
        return "Human review is required before any further offline paper action."
    if decision == SupervisorDecision.APPROVE_WITH_REDUCED_RISK:
        return "Approve only reduced-risk offline paper simulation with strict controls."
    if decision == SupervisorDecision.APPROVE_SYSTEM_DECISION and not conflicts and not risks:
        return "Approve the coordinated system decision for offline paper simulation only."
    if decision == SupervisorDecision.APPROVE_SYSTEM_DECISION:
        return "Approval is conditional; review non-critical risks before proceeding offline."
    return "No supervisor action; keep the system in observation mode."


def _reliability_reasons(
    votes: tuple[AgentCoordinationEvent, ...],
    score: int,
    risk_notes: int,
    blocking: int,
) -> tuple[str, ...]:
    reasons: list[str] = [f"Reliability score {score}/100."]
    if not votes:
        reasons.append("No current vote evidence.")
    if risk_notes:
        reasons.append(f"{risk_notes} risk note(s) attached.")
    if blocking:
        reasons.append(f"{blocking} blocking vote(s) observed.")
    return tuple(reasons)


def _event_message(
    role: SupervisorRole,
    decision: SupervisorDecision,
    overrides: tuple[SupervisorOverride, ...],
) -> str:
    override_text = ", ".join(override.value for override in overrides) if overrides else SupervisorOverride.NONE.value
    return f"{role.value} emitted {decision.value} with overrides: {override_text}."


def _confidence_bonus(confidence: AgentConfidence) -> int:
    return {AgentConfidence.LOW: 0, AgentConfidence.MEDIUM: 4, AgentConfidence.HIGH: 8}[confidence]


def _override_lines(overrides: tuple[SupervisorOverride, ...]) -> list[str]:
    if not overrides:
        return ["- NONE"]
    return [f"- {override.value}" for override in overrides]


def _join_agents(agents: tuple[TradingAgentRole, ...]) -> str:
    return ", ".join(agent.value for agent in agents) if agents else "None"


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(supervisor_input: SupervisorInput | None = None, **kwargs) -> SupervisorInput:
    if supervisor_input is not None:
        return supervisor_input
    return SupervisorInput(**kwargs)


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "apply_supervisor_override",
    "compute_agent_reliability",
    "evaluate_supervisor_decision",
    "render_supervisor_markdown",
]
