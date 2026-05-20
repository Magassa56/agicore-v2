"""Offline multi-agent coordination layer for AGIcore Trading."""
from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime

from .adaptive_policy_memory_models import AdaptivePolicyMemory, PolicyMemoryRecommendation
from .context_scoring_models import ContextScoringResult, TradeContextDecision
from .market_regime_models import MarketRegimeAnalysis, SessionCondition
from .meta_strategy_models import MetaStrategyDecision, MetaStrategySelectionResult
from .multi_agent_models import (
    AgentConfidence,
    AgentConsensusStatus,
    AgentCoordinationEvent,
    AgentCoordinationInput,
    AgentCoordinationResult,
    AgentVote,
    TradingAgentRole,
)
from .paper_execution_models import PaperExecutionDecision, PaperExecutionResult
from .reward_models import RewardEvaluationResult, RewardLabel
from .safe_rl_models import SafeRLExperimentResult, SafeRLStatus
from .scenario_replay_models import ReplayArenaResult, ReplayArenaStatus, ReplayScenarioResult
from .semi_auto_decision_models import SemiAutoDecision, SemiAutoDecisionResult


def build_agent_vote(
    role: TradingAgentRole | str,
    coordination_input: AgentCoordinationInput | None = None,
    **kwargs,
) -> AgentCoordinationEvent:
    """Build one deterministic specialized agent vote."""
    resolved_role = role if isinstance(role, TradingAgentRole) else TradingAgentRole(str(role))
    data = _input(coordination_input, **kwargs)
    if resolved_role == TradingAgentRole.MARKET_ANALYST:
        return _market_vote(data)
    if resolved_role == TradingAgentRole.RISK_GUARDIAN:
        return _risk_vote(data)
    if resolved_role == TradingAgentRole.POLICY_SELECTOR:
        return _policy_vote(data)
    if resolved_role == TradingAgentRole.REWARD_ANALYST:
        return _reward_vote(data)
    if resolved_role == TradingAgentRole.SAFE_RL_SUPERVISOR:
        return _safe_rl_vote(data)
    if resolved_role == TradingAgentRole.EXECUTION_SUPERVISOR:
        return _execution_vote(data)
    return _memory_vote(data)


def coordinate_trading_agents(
    coordination_input: AgentCoordinationInput | None = None,
    **kwargs,
) -> AgentCoordinationResult:
    """Coordinate all specialized offline trading agents."""
    data = _input(coordination_input, **kwargs)
    votes = tuple(build_agent_vote(role, data) for role in TradingAgentRole)
    return compute_agent_consensus(votes)


def compute_agent_consensus(
    votes: tuple[AgentCoordinationEvent, ...] | list[AgentCoordinationEvent],
) -> AgentCoordinationResult:
    """Compute weighted consensus from specialized agent votes."""
    vote_tuple = tuple(votes)
    blockers = tuple(event.role for event in vote_tuple if event.vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION})
    risks = tuple(dict.fromkeys(note for event in vote_tuple for note in event.risk_notes))
    disagreements = _disagreements(vote_tuple)
    final_vote = _final_vote(vote_tuple)
    status = _status(final_vote, bool(disagreements))
    score = _consensus_score(vote_tuple, final_vote, disagreements)
    return AgentCoordinationResult(
        final_vote=final_vote,
        consensus_status=status,
        consensus_score=score,
        votes=vote_tuple,
        disagreements=disagreements,
        blocking_agents=blockers,
        risks_detected=risks,
        recommendation=_recommendation(final_vote, blockers, disagreements, risks),
    )


def render_agent_coordination_markdown(result: AgentCoordinationResult) -> str:
    """Render multi-agent coordination as Markdown."""
    lines = [
        "# Multi-Agent Coordination Layer",
        "",
        "## Decision collective",
        "",
        f"- Vote final: {result.final_vote.value}",
        f"- Status: {result.consensus_status.value}",
        f"- Consensus score: {result.consensus_score}/100",
        "",
        "## Votes par agent",
        "",
        "| Agent | Vote | Confidence | Weight | Reasons |",
        "| --- | --- | --- | ---: | --- |",
        *_vote_lines(result.votes),
        "",
        "## Consensus",
        "",
        f"- {result.consensus_status.value}",
        "",
        "## Desaccords",
        "",
        *_bullet_lines(result.disagreements),
        "",
        "## Agents bloquants",
        "",
        *_agent_lines(result.blocking_agents),
        "",
        "## Risques detectes",
        "",
        *_bullet_lines(result.risks_detected),
        "",
        "## Recommandation finale AGIcore",
        "",
        f"- {result.recommendation}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _market_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    market = data.market_regime
    context = data.context_score
    if market is None and context is None:
        return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No market/context input.",), ())
    risks: list[str] = []
    reasons: list[str] = []
    if market is not None:
        reasons.append(f"Market regime {market.primary_regime.value}.")
        if market.dangerous_market or market.session_condition == SessionCondition.DANGEROUS:
            risks.append("Market regime is dangerous.")
            return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.BLOCK, AgentConfidence.HIGH, 3, tuple(reasons), tuple(risks))
        if not market.favorable_for_pullback_strategy:
            risks.append("Market is not favorable for pullback strategy.")
            return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(risks))
    if context is not None:
        reasons.append(f"Context score {context.global_score}/100.")
        if context.decision == TradeContextDecision.NO_TRADE:
            risks.append("Context decision is NO_TRADE.")
            return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.BLOCK, AgentConfidence.HIGH, 3, tuple(reasons), tuple(risks))
        if context.decision in {TradeContextDecision.REDUCE_RISK, TradeContextDecision.HIGH_RISK_CONTEXT}:
            return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(risks))
    return _event(TradingAgentRole.MARKET_ANALYST, AgentVote.APPROVE, AgentConfidence.HIGH, 2, tuple(reasons), tuple(risks))


def _risk_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    risks: list[str] = []
    reasons: list[str] = []
    context = data.context_score
    semi = data.semi_auto_decision
    if context is not None:
        reasons.append(f"Context decision {context.decision.value}.")
        if context.decision == TradeContextDecision.NO_TRADE:
            risks.append("Risk Guardian blocks NO_TRADE context.")
            return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.BLOCK, AgentConfidence.HIGH, 4, tuple(reasons), tuple(risks))
        if context.decision == TradeContextDecision.HIGH_RISK_CONTEXT:
            risks.append("High risk context.")
            return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.REQUIRE_REVIEW, AgentConfidence.HIGH, 3, tuple(reasons), tuple(risks))
    if semi is not None and semi.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.REVIEW_ONLY}:
        risks.extend(semi.blocking_reasons or ("Semi-auto blocks/reviews the trade.",))
        return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.BLOCK, AgentConfidence.HIGH, 4, tuple(reasons), tuple(risks))
    if semi is not None and semi.decision == SemiAutoDecision.STOP_SESSION:
        risks.append("Semi-auto recommends STOP_SESSION.")
        return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.STOP_SESSION, AgentConfidence.HIGH, 5, tuple(reasons), tuple(risks))
    if semi is not None and semi.decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
        return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.HIGH, 3, ("Reduced-risk approval required.",), ())
    return _event(TradingAgentRole.RISK_GUARDIAN, AgentVote.APPROVE, AgentConfidence.MEDIUM, 3, tuple(reasons or ("Risk checks do not block.",)), ())


def _policy_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    meta = data.meta_strategy
    if meta is None:
        return _event(TradingAgentRole.POLICY_SELECTOR, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No meta strategy result.",), ())
    reasons = (meta.recommendation,)
    risks = meta.risk_notes
    if meta.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES:
        return _event(TradingAgentRole.POLICY_SELECTOR, AgentVote.BLOCK, AgentConfidence.HIGH, 3, reasons, risks)
    if meta.decision in {MetaStrategyDecision.REQUIRE_REVIEW, MetaStrategyDecision.NO_STRATEGY}:
        return _event(TradingAgentRole.POLICY_SELECTOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, reasons, risks)
    if meta.decision in {MetaStrategyDecision.SELECT_REDUCED_RISK_POLICY, MetaStrategyDecision.FALLBACK_TO_CONSERVATIVE}:
        return _event(TradingAgentRole.POLICY_SELECTOR, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.MEDIUM, 2, reasons, risks)
    return _event(TradingAgentRole.POLICY_SELECTOR, AgentVote.APPROVE, AgentConfidence.HIGH, 2, reasons, risks)


def _reward_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    reward = data.reward_evaluation
    if reward is None:
        return _event(TradingAgentRole.REWARD_ANALYST, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No reward evaluation.",), ())
    reasons = (f"Reward {reward.normalized_reward}/100: {reward.reward_label.value}.",)
    risks = reward.improvement_actions
    if reward.reward_label == RewardLabel.DANGEROUS_DECISION or reward.normalized_reward < 30:
        return _event(TradingAgentRole.REWARD_ANALYST, AgentVote.BLOCK, AgentConfidence.HIGH, 3, reasons, risks)
    if reward.reward_label == RewardLabel.BAD_DECISION or reward.normalized_reward < 50:
        return _event(TradingAgentRole.REWARD_ANALYST, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, reasons, risks)
    if reward.reward_label == RewardLabel.ACCEPTABLE:
        return _event(TradingAgentRole.REWARD_ANALYST, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.MEDIUM, 2, reasons, risks)
    return _event(TradingAgentRole.REWARD_ANALYST, AgentVote.APPROVE, AgentConfidence.HIGH, 2, reasons, ())


def _safe_rl_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    safe = data.safe_rl_result
    if safe is None:
        return _event(TradingAgentRole.SAFE_RL_SUPERVISOR, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No Safe RL result.",), ())
    reasons = (safe.safety_summary,)
    risks = safe.risks_detected
    if safe.status == SafeRLStatus.BLOCKED:
        return _event(TradingAgentRole.SAFE_RL_SUPERVISOR, AgentVote.BLOCK, AgentConfidence.HIGH, 5, reasons, risks)
    if safe.status == SafeRLStatus.REVIEW_REQUIRED:
        return _event(TradingAgentRole.SAFE_RL_SUPERVISOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.HIGH, 4, reasons, risks)
    if safe.status == SafeRLStatus.WARNING:
        return _event(TradingAgentRole.SAFE_RL_SUPERVISOR, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.MEDIUM, 3, reasons, risks)
    return _event(TradingAgentRole.SAFE_RL_SUPERVISOR, AgentVote.APPROVE, AgentConfidence.HIGH, 3, reasons, ())


def _execution_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    semi = data.semi_auto_decision
    paper = data.paper_execution
    if semi is not None and semi.decision == SemiAutoDecision.STOP_SESSION:
        return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.STOP_SESSION, AgentConfidence.HIGH, 4, (semi.trader_message,), semi.detected_risks)
    if semi is not None and semi.decision in {SemiAutoDecision.BLOCK_TRADE, SemiAutoDecision.REVIEW_ONLY}:
        return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.BLOCK, AgentConfidence.HIGH, 4, (semi.trader_message,), semi.blocking_reasons or semi.detected_risks)
    if paper is not None:
        if paper.decision == PaperExecutionDecision.PRECHECK_REJECTED or not paper.accepted:
            return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.BLOCK, AgentConfidence.HIGH, 4, paper.precheck_reasons, ("Paper loop rejected execution.",))
        if paper.decision == PaperExecutionDecision.PAPER_ORDER_FILLED:
            return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.APPROVE, AgentConfidence.HIGH, 2, ("Paper loop accepted simulated execution.",), ())
    if semi is not None and semi.decision == SemiAutoDecision.APPROVE_REDUCED_RISK:
        return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.APPROVE_REDUCED_RISK, AgentConfidence.MEDIUM, 2, ("Semi-auto reduced-risk action.",), semi.detected_risks)
    if semi is not None and semi.decision == SemiAutoDecision.REQUIRE_CONFIRMATION:
        return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, semi.manual_confirmation_conditions, semi.detected_risks)
    return _event(TradingAgentRole.EXECUTION_SUPERVISOR, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No execution evidence.",), ())


def _memory_vote(data: AgentCoordinationInput) -> AgentCoordinationEvent:
    memory = data.policy_memory
    arena = data.arena_result
    scenario = data.scenario_result
    risks: list[str] = []
    reasons: list[str] = []
    if memory is not None:
        reasons.append(f"Memory tracks {len(memory.entries)} policies.")
        disabled = list(memory.disabled_policies)
        disabled.extend(name for name, entry in memory.entries.items() if entry.recommendation == PolicyMemoryRecommendation.DISABLE_POLICY)
        if disabled:
            risks.append(f"Disabled policies: {', '.join(sorted(set(disabled)))}.")
        if memory.entries:
            avg_conf = sum(entry.confidence_score for entry in memory.entries.values()) / len(memory.entries)
            if avg_conf < 45:
                risks.append("Policy memory confidence is weak.")
                return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(risks))
    if arena is not None:
        reasons.append(f"Arena robustness {arena.robustness_score}/100.")
        risks.extend(arena.risks_detected)
        if arena.status == ReplayArenaStatus.BLOCKED_BY_SAFETY or arena.robustness_score < 40:
            return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.BLOCK, AgentConfidence.HIGH, 3, tuple(reasons), tuple(risks))
        if arena.robustness_score < 65:
            return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(risks))
    if scenario is not None:
        reasons.append(f"Scenario score {scenario.scenario_score}/100.")
        risks.extend(scenario.risks_detected)
        if scenario.scenario_score < 45:
            return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.REQUIRE_REVIEW, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(risks))
    if not reasons:
        return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.NO_OPINION, AgentConfidence.LOW, 1, ("No memory or replay evidence.",), ())
    return _event(TradingAgentRole.MEMORY_CURATOR, AgentVote.APPROVE, AgentConfidence.MEDIUM, 2, tuple(reasons), tuple(dict.fromkeys(risks)))


def _final_vote(votes: tuple[AgentCoordinationEvent, ...]) -> AgentVote:
    if any(event.vote == AgentVote.STOP_SESSION for event in votes):
        return AgentVote.STOP_SESSION
    if any(event.vote == AgentVote.BLOCK and event.role in {TradingAgentRole.RISK_GUARDIAN, TradingAgentRole.SAFE_RL_SUPERVISOR, TradingAgentRole.EXECUTION_SUPERVISOR} for event in votes):
        return AgentVote.BLOCK
    scores: dict[AgentVote, int] = defaultdict(int)
    for event in votes:
        if event.vote == AgentVote.NO_OPINION:
            continue
        scores[event.vote] += event.weight * _confidence_weight(event.confidence)
    if not scores:
        return AgentVote.NO_OPINION
    return max(scores.items(), key=lambda item: (item[1], _vote_priority(item[0])))[0]


def _status(vote: AgentVote, has_disagreement: bool) -> AgentConsensusStatus:
    if vote == AgentVote.STOP_SESSION:
        return AgentConsensusStatus.CONSENSUS_STOP_SESSION
    if vote == AgentVote.BLOCK:
        return AgentConsensusStatus.CONSENSUS_BLOCK
    if vote == AgentVote.REQUIRE_REVIEW:
        return AgentConsensusStatus.CONSENSUS_REVIEW
    if vote == AgentVote.APPROVE_REDUCED_RISK:
        return AgentConsensusStatus.CONSENSUS_REDUCED_RISK
    if vote == AgentVote.APPROVE and not has_disagreement:
        return AgentConsensusStatus.CONSENSUS_APPROVE
    if vote == AgentVote.APPROVE:
        return AgentConsensusStatus.CONSENSUS_REDUCED_RISK
    return AgentConsensusStatus.NO_CONSENSUS


def _consensus_score(votes: tuple[AgentCoordinationEvent, ...], final_vote: AgentVote, disagreements: tuple[str, ...]) -> int:
    decisive = [event for event in votes if event.vote != AgentVote.NO_OPINION]
    if not decisive:
        return 0
    total = sum(event.weight * _confidence_weight(event.confidence) for event in decisive)
    aligned = sum(event.weight * _confidence_weight(event.confidence) for event in decisive if event.vote == final_vote)
    score = (aligned / total) * 100 if total else 0
    score -= min(25, len(disagreements) * 8)
    return _clamp(score)


def _disagreements(votes: tuple[AgentCoordinationEvent, ...]) -> tuple[str, ...]:
    active = [event for event in votes if event.vote != AgentVote.NO_OPINION]
    if not active:
        return ()
    vote_set = {event.vote for event in active}
    if len(vote_set) <= 1:
        return ()
    blockers = [event.role.value for event in active if event.vote in {AgentVote.BLOCK, AgentVote.STOP_SESSION}]
    approvers = [event.role.value for event in active if event.vote == AgentVote.APPROVE]
    items: list[str] = []
    if blockers and approvers:
        items.append(f"Blocking agents disagree with approvers: blockers={', '.join(blockers)}; approvers={', '.join(approvers)}.")
    if AgentVote.REQUIRE_REVIEW in vote_set and AgentVote.APPROVE in vote_set:
        items.append("Some agents require review while others approve.")
    if AgentVote.APPROVE_REDUCED_RISK in vote_set and AgentVote.APPROVE in vote_set:
        items.append("Reduced-risk votes conflict with full approval votes.")
    return tuple(items)


def _recommendation(
    final_vote: AgentVote,
    blockers: tuple[TradingAgentRole, ...],
    disagreements: tuple[str, ...],
    risks: tuple[str, ...],
) -> str:
    if final_vote == AgentVote.STOP_SESSION:
        return "Stop the session and keep the system offline/review-only."
    if final_vote == AgentVote.BLOCK:
        agents = ", ".join(role.value for role in blockers) or "coordination layer"
        return f"Block the trade because {agents} raised a hard safety concern."
    if final_vote == AgentVote.REQUIRE_REVIEW:
        return "Require manual review before any further offline paper action."
    if final_vote == AgentVote.APPROVE_REDUCED_RISK:
        return "Allow only reduced-risk offline paper simulation after confirming risk controls."
    if final_vote == AgentVote.APPROVE and not disagreements and not risks:
        return "Collective decision approves offline paper simulation only."
    if final_vote == AgentVote.APPROVE:
        return "Approval is conditional; review disagreements and risks first."
    return "No collective decision; keep the system in review-only mode."


def _event(
    role: TradingAgentRole,
    vote: AgentVote,
    confidence: AgentConfidence,
    weight: int,
    reasons: tuple[str, ...],
    risk_notes: tuple[str, ...],
) -> AgentCoordinationEvent:
    return AgentCoordinationEvent(
        role=role,
        vote=vote,
        confidence=confidence,
        weight=weight,
        reasons=tuple(dict.fromkeys(reasons)),
        risk_notes=tuple(dict.fromkeys(risk_notes)),
        timestamp=datetime.now(UTC),
    )


def _input(coordination_input: AgentCoordinationInput | None = None, **kwargs) -> AgentCoordinationInput:
    if coordination_input is not None:
        return coordination_input
    return AgentCoordinationInput(**kwargs)


def _confidence_weight(confidence: AgentConfidence) -> int:
    return {AgentConfidence.LOW: 1, AgentConfidence.MEDIUM: 2, AgentConfidence.HIGH: 3}[confidence]


def _vote_priority(vote: AgentVote) -> int:
    order = {
        AgentVote.STOP_SESSION: 5,
        AgentVote.BLOCK: 4,
        AgentVote.REQUIRE_REVIEW: 3,
        AgentVote.APPROVE_REDUCED_RISK: 2,
        AgentVote.APPROVE: 1,
        AgentVote.NO_OPINION: 0,
    }
    return order[vote]


def _vote_lines(votes: tuple[AgentCoordinationEvent, ...]) -> list[str]:
    if not votes:
        return ["| None | NO_OPINION | LOW | 0 | None |"]
    return [
        (
            f"| {event.role.value} | {event.vote.value} | {event.confidence.value} | "
            f"{event.weight} | {'; '.join(event.reasons) or 'None'} |"
        )
        for event in votes
    ]


def _agent_lines(agents: tuple[TradingAgentRole, ...]) -> list[str]:
    if not agents:
        return ["- None"]
    return [f"- {agent.value}" for agent in agents]


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _clamp(value: int | float) -> int:
    return max(0, min(100, int(round(value))))


__all__ = [
    "build_agent_vote",
    "compute_agent_consensus",
    "coordinate_trading_agents",
    "render_agent_coordination_markdown",
]
