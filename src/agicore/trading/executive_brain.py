"""Offline Executive Decision Brain for AGIcore Trading."""
from __future__ import annotations

from datetime import UTC, datetime

from .autonomous_simulation_models import AutonomousSimulationStatus
from .context_scoring_models import TradeContextDecision
from .executive_brain_models import (
    ExecutiveBrainEvent,
    ExecutiveBrainInput,
    ExecutiveBrainResult,
    ExecutiveDecision,
    ExecutiveIntent,
    ExecutiveMode,
    ExecutiveRiskAppetite,
    ExecutiveState,
)
from .hierarchical_supervisor_models import SupervisorDecision, SupervisorOverride
from .meta_strategy_models import MetaStrategyDecision
from .multi_agent_models import AgentConsensusStatus, AgentVote
from .reward_models import RewardLabel
from .safe_rl_models import SafeRLStatus
from .scenario_replay_models import ReplayArenaStatus


def evaluate_executive_state(
    brain_input: ExecutiveBrainInput | None = None,
    **kwargs,
) -> ExecutiveState:
    """Evaluate the global offline executive state."""
    data = _input(brain_input, **kwargs)
    reasons: list[str] = []
    constraints: list[str] = []

    if _must_pause(data, reasons, constraints):
        return _state(ExecutiveMode.PAUSED, ExecutiveIntent.SESSION_STOP, ExecutiveRiskAppetite.NONE, "Stop session and preserve capital.", constraints, reasons)
    if _must_survive(data, reasons, constraints):
        return _state(ExecutiveMode.SURVIVAL, ExecutiveIntent.CAPITAL_PRESERVATION, ExecutiveRiskAppetite.NONE, "Survive current risk event; no new exposure.", constraints, reasons)
    if _needs_recovery(data, reasons, constraints):
        return _state(ExecutiveMode.RECOVERY, ExecutiveIntent.LEARNING_ONLY, ExecutiveRiskAppetite.VERY_LOW, "Recover discipline and collect offline learning evidence.", constraints, reasons)
    if _is_defensive(data, reasons, constraints):
        return _state(ExecutiveMode.DEFENSIVE, ExecutiveIntent.RISK_REDUCTION, ExecutiveRiskAppetite.LOW, "Reduce risk and require stronger confirmation.", constraints, reasons)
    if _is_opportunity(data, reasons):
        return _state(ExecutiveMode.OPPORTUNITY, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.ELEVATED, "Use controlled opportunity only within offline risk limits.", constraints, reasons)
    reasons.append("Default balanced operating conditions.")
    return _state(ExecutiveMode.NORMAL, ExecutiveIntent.CONTROLLED_GROWTH, ExecutiveRiskAppetite.MODERATE, "Execute normal offline paper decision process.", constraints, reasons)


def decide_executive_action(
    state: ExecutiveState,
    brain_input: ExecutiveBrainInput | None = None,
    **kwargs,
) -> ExecutiveDecision:
    """Build an executable executive action from the state and safety inputs."""
    data = _input(brain_input, **kwargs)
    if state.mode in {ExecutiveMode.PAUSED, ExecutiveMode.SURVIVAL} or state.intent == ExecutiveIntent.SESSION_STOP:
        return ExecutiveDecision(False, False, True, True, "SESSION_STOP", "Block execution and stop the session.")
    if data.supervisor_result is not None and not data.supervisor_result.final_executable:
        return ExecutiveDecision(False, False, True, False, "SUPERVISOR_BLOCK", "Keep execution blocked until supervisor clears risks.")
    if state.mode == ExecutiveMode.RECOVERY:
        return ExecutiveDecision(False, False, True, False, "LEARNING_ONLY", "Run review and learning-only workflows.")
    if state.mode == ExecutiveMode.DEFENSIVE:
        return ExecutiveDecision(True, True, True, False, "REDUCED_RISK_ONLY", "Allow only reduced-risk offline paper simulation.")
    if state.mode == ExecutiveMode.OPPORTUNITY:
        return ExecutiveDecision(True, False, False, False, "CONTROLLED_OPPORTUNITY", "Allow controlled offline paper simulation.")
    return ExecutiveDecision(True, False, False, False, "NORMAL_OPERATION", "Allow normal offline paper decision process.")


def update_executive_state(
    previous_state: ExecutiveState | None = None,
    brain_input: ExecutiveBrainInput | None = None,
    **kwargs,
) -> ExecutiveBrainResult:
    """Evaluate state, decide action, and emit an auditable executive result."""
    data = _input(brain_input, **kwargs)
    if previous_state is not None and data.previous_state is None:
        data = ExecutiveBrainInput(
            supervisor_result=data.supervisor_result,
            agent_coordination=data.agent_coordination,
            context_score=data.context_score,
            safe_rl_result=data.safe_rl_result,
            reward_evaluation=data.reward_evaluation,
            replay_arena=data.replay_arena,
            policy_memory=data.policy_memory,
            meta_strategy=data.meta_strategy,
            autonomous_simulation=data.autonomous_simulation,
            previous_state=previous_state,
        )
    state = evaluate_executive_state(data)
    decision = decide_executive_action(state, data)
    event = ExecutiveBrainEvent(
        mode=state.mode,
        intent=state.intent,
        message=f"Executive mode {state.mode.value}; decision {decision.decision_label}.",
        timestamp=datetime.now(UTC),
    )
    return ExecutiveBrainResult(
        state=state,
        decision=decision,
        events=(event,),
        recommendation=_recommendation(state, decision),
    )


def render_executive_brain_markdown(result: ExecutiveBrainResult) -> str:
    """Render an Executive Decision Brain result as Markdown."""
    lines = [
        "# Executive Decision Brain",
        "",
        "## Mode executif",
        "",
        f"- {result.state.mode.value}",
        "",
        "## Intention strategique",
        "",
        f"- {result.state.intent.value}",
        "",
        "## Appetit au risque",
        "",
        f"- {result.state.risk_appetite.value}",
        "",
        "## Decision executive",
        "",
        f"- Label: {result.decision.decision_label}",
        f"- Allow execution: {result.decision.allow_execution}",
        f"- Reduced risk only: {result.decision.allow_reduced_risk_only}",
        f"- Human review: {result.decision.require_human_review}",
        f"- Stop session: {result.decision.stop_session}",
        "",
        "## Raisons",
        "",
        *_bullet_lines(result.state.reasons),
        "",
        "## Contraintes actives",
        "",
        *_bullet_lines(result.state.active_constraints),
        "",
        "## Objectif de session",
        "",
        f"- {result.state.session_objective}",
        "",
        "## Recommandation AGIcore",
        "",
        f"- {result.recommendation}",
        "",
        "- Offline only: no broker, no real order, no external ML, no neural training.",
        "",
    ]
    return "\n".join(lines)


def _must_pause(data: ExecutiveBrainInput, reasons: list[str], constraints: list[str]) -> bool:
    supervisor = data.supervisor_result
    if supervisor is not None and supervisor.decision in {
        SupervisorDecision.OVERRIDE_TO_BLOCK,
        SupervisorDecision.OVERRIDE_TO_STOP_SESSION,
        SupervisorDecision.EMERGENCY_HALT,
    }:
        reasons.append(f"Supervisor decision blocks execution: {supervisor.decision.value}.")
        constraints.extend(override.value for override in supervisor.applied_overrides)
        return True
    if data.context_score is not None and data.context_score.decision == TradeContextDecision.NO_TRADE:
        reasons.append("Context scoring is NO_TRADE.")
        constraints.append("NO_TRADE_CONTEXT")
        return True
    if data.meta_strategy is not None and data.meta_strategy.decision == MetaStrategyDecision.BLOCK_ALL_POLICIES:
        reasons.append("Meta strategy blocks all policies.")
        constraints.append("META_STRATEGY_BLOCK")
        return True
    return False


def _must_survive(data: ExecutiveBrainInput, reasons: list[str], constraints: list[str]) -> bool:
    supervisor = data.supervisor_result
    if supervisor is not None and supervisor.decision == SupervisorDecision.EMERGENCY_HALT:
        reasons.append("Supervisor emitted emergency halt.")
        constraints.append("EMERGENCY_HALT")
        return True
    if data.safe_rl_result is not None and data.safe_rl_result.status == SafeRLStatus.BLOCKED:
        reasons.append("Safe RL status is BLOCKED.")
        constraints.append("SAFE_RL_BLOCKED")
        return True
    if data.autonomous_simulation is not None and data.autonomous_simulation.status in {
        AutonomousSimulationStatus.STOPPED_DAILY_LOSS_LIMIT,
        AutonomousSimulationStatus.STOPPED_SESSION,
        AutonomousSimulationStatus.STOPPED_SAFE_RL_BLOCKED,
    }:
        reasons.append(f"Autonomous simulation stopped: {data.autonomous_simulation.status.value}.")
        constraints.append("SIMULATION_STOP")
        return True
    return False


def _needs_recovery(data: ExecutiveBrainInput, reasons: list[str], constraints: list[str]) -> bool:
    reward = data.reward_evaluation
    if reward is not None and (reward.total_reward < 0 or reward.reward_label in {RewardLabel.BAD_DECISION, RewardLabel.DANGEROUS_DECISION}):
        reasons.append(f"Reward indicates recovery need: {reward.reward_label.value}.")
        constraints.append("NEGATIVE_REWARD")
        return True
    if data.replay_arena is not None and data.replay_arena.robustness_score < 50:
        reasons.append("Replay arena robustness is weak.")
        constraints.append("WEAK_REPLAY_ROBUSTNESS")
        return True
    if data.previous_state is not None and data.previous_state.mode == ExecutiveMode.SURVIVAL:
        reasons.append("Previous state was SURVIVAL; transition through RECOVERY.")
        constraints.append("POST_SURVIVAL_RECOVERY")
        return True
    return False


def _is_defensive(data: ExecutiveBrainInput, reasons: list[str], constraints: list[str]) -> bool:
    if data.context_score is not None and data.context_score.decision in {TradeContextDecision.HIGH_RISK_CONTEXT, TradeContextDecision.REDUCE_RISK}:
        reasons.append(f"Context decision requires caution: {data.context_score.decision.value}.")
        constraints.append("CONTEXT_CAUTION")
        return True
    if data.safe_rl_result is not None and data.safe_rl_result.status in {SafeRLStatus.WARNING, SafeRLStatus.REVIEW_REQUIRED}:
        reasons.append(f"Safe RL requires caution: {data.safe_rl_result.status.value}.")
        constraints.append("SAFE_RL_CAUTION")
        return True
    if data.agent_coordination is not None and (data.agent_coordination.disagreements or data.agent_coordination.consensus_score < 65):
        reasons.append("Agent coordination has conflict or weak consensus.")
        constraints.append("AGENT_CONFLICT")
        return True
    if data.supervisor_result is not None and data.supervisor_result.decision in {
        SupervisorDecision.APPROVE_WITH_REDUCED_RISK,
        SupervisorDecision.REQUIRE_HUMAN_REVIEW,
    }:
        reasons.append(f"Supervisor requires caution: {data.supervisor_result.decision.value}.")
        constraints.append("SUPERVISOR_CAUTION")
        return True
    return False


def _is_opportunity(data: ExecutiveBrainInput, reasons: list[str]) -> bool:
    if data.context_score is None or data.reward_evaluation is None:
        return False
    reliable_policy = _policy_reliable(data)
    supervisor_ok = data.supervisor_result is None or data.supervisor_result.final_executable
    safe_ok = data.safe_rl_result is None or data.safe_rl_result.status == SafeRLStatus.SAFE
    if (
        data.context_score.global_score >= 80
        and data.reward_evaluation.normalized_reward >= 70
        and reliable_policy
        and supervisor_ok
        and safe_ok
    ):
        reasons.append("Strong context, positive reward, reliable policy memory and controlled risk.")
        return True
    return False


def _policy_reliable(data: ExecutiveBrainInput) -> bool:
    if data.policy_memory is None or not data.policy_memory.entries:
        return True
    return any(entry.confidence_score >= 70 and entry.dangerous_decision_rate <= 0.1 for entry in data.policy_memory.entries.values())


def _state(
    mode: ExecutiveMode,
    intent: ExecutiveIntent,
    risk: ExecutiveRiskAppetite,
    objective: str,
    constraints: list[str],
    reasons: list[str],
) -> ExecutiveState:
    return ExecutiveState(
        mode=mode,
        intent=intent,
        risk_appetite=risk,
        session_objective=objective,
        active_constraints=tuple(dict.fromkeys(constraints)),
        reasons=tuple(dict.fromkeys(reasons)),
    )


def _recommendation(state: ExecutiveState, decision: ExecutiveDecision) -> str:
    if decision.stop_session:
        return "Stop the session and preserve capital. Keep all workflows offline."
    if state.mode == ExecutiveMode.RECOVERY:
        return "Run learning/review only until risk and reward quality recover."
    if decision.allow_reduced_risk_only:
        return "Proceed only with reduced-risk offline paper simulation after review."
    if state.mode == ExecutiveMode.OPPORTUNITY:
        return "Proceed with controlled offline opportunity handling; keep risk limits strict."
    if decision.allow_execution:
        return "Proceed with normal offline paper decision process."
    return "Hold in observation mode."


def _bullet_lines(values: tuple[str, ...]) -> list[str]:
    if not values:
        return ["- None"]
    return [f"- {value}" for value in values]


def _input(brain_input: ExecutiveBrainInput | None = None, **kwargs) -> ExecutiveBrainInput:
    if brain_input is not None:
        return brain_input
    return ExecutiveBrainInput(**kwargs)


__all__ = [
    "decide_executive_action",
    "evaluate_executive_state",
    "render_executive_brain_markdown",
    "update_executive_state",
]
